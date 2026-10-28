"""Provjera svih izvora prije pisanja parsera (pravilo 3 iz CLAUDE.md §8).

Za svaki izvor spremamo sirovi odgovor u data/raw/<izvor>_probe/ i redak u
docs/probe_report.md (izvor, URL, HTTP kod, veličina, nalaz, OK/GREŠKA).
Ne pretpostavljamo nazive stupaca — ispisujemo ono što stvarno dođe.

Pokretanje: python -m etl.probe [--samo ime1,ime2]
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import traceback
import zipfile
from pathlib import Path

from etl import ckan, http
from etl.config import (DOCS_DIR, EFFIS_BA_SLOJ, EFFIS_FWI_SLOJ, EFFIS_WMS, HAC_WFS, HC_WFS,
                        POVIJESNI_DAN, RAW_DIR, WORLDCOVER_URL)

DANAS = dt.date.today().isoformat()
MURTER = (15.59, 43.82)  # lon, lat — približno središte naselja Murter (provjereno u OSM probi)
TISNO_BBOX = (15.62, 43.79, 15.66, 43.81)  # lon/lat oko mosta u Tisnom
SKZ_BBOX = (15.40, 43.40, 16.60, 44.30)  # gruba omotnica ŠKŽ (lon/lat), samo za probe

redovi: list[dict] = []
detalji: list[str] = []


def _dir(izvor: str) -> Path:
    d = RAW_DIR / f"{izvor}_probe"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _spremi(izvor: str, ime: str, sadrzaj: bytes | str) -> Path:
    p = _dir(izvor) / ime
    if isinstance(sadrzaj, str):
        p.write_text(sadrzaj, encoding="utf-8")
    else:
        p.write_bytes(sadrzaj)
    return p


def _red(izvor, url, http_kod, velicina, nalaz, ok=True):
    redovi.append({"izvor": izvor, "url": url, "http": http_kod, "velicina": velicina,
                   "nalaz": nalaz, "status": "OK" if ok else "GREŠKA"})
    print(f"[{'OK' if ok else 'GREŠKA'}] {izvor}: {nalaz[:160]}")


def _detalj(naslov: str, tekst: str):
    detalji.append(f"### {naslov}\n\n```\n{tekst.strip()[:6000]}\n```\n")


def _get(izvor: str, ime: str, url: str, params: dict | None = None, timeout: float = 120):
    r = http.get(url, params=params, timeout=timeout)
    _spremi(izvor, ime, r.content)
    return r


# ---------------------------------------------------------------- CKAN ----
CKAN_PAKETI = {
    "dzs_popis": "statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021",
    "dzs_stanovi": "statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021-stambene-jedinice",
    "dzs_gradovi": "statistika-u-nizu-gradovi-u-statistici",
    "dzs_turizam_niz": "statistika-u-nizu-turizam",
    "hc_brojenje_2025": "brojenje-prometa-na-cestama-republike-hrvatske-godine-2025",
    "hc_brojenje_2024": "brojenje-prometa-na-cestama-republike-hrvatske-godine-2024",
    "dgu_au": "upravne-jedinice-inspire",
    "dgu_rgi": "registar-geografskih-imena",
    "dgu_rgi_inspire": "registar-geografskih-imena-inspire",
    "hc_wms": "mrea-javnih-cesta-rh-wms",
}


def probe_ckan():
    for kljuc, pid in CKAN_PAKETI.items():
        url = f"https://data.gov.hr/ckan/api/3/action/package_show?id={pid}"
        try:
            p = ckan.package_show(pid)
            _spremi("ckan", f"{kljuc}.json", json.dumps(p, ensure_ascii=False, indent=2))
            res = "; ".join(f"{r.get('name') or '?'} [{r.get('format')}]" for r in p["resources"])
            _red("CKAN " + kljuc, url, 200, len(p["resources"]),
                 f"izdavač={(p.get('organization') or {}).get('title')}; licenca={p.get('license_title')}; "
                 f"metadata_modified={p.get('metadata_modified')}; resursi: {res}")
        except Exception as e:
            _red("CKAN " + kljuc, url, "-", "-", f"{type(e).__name__}: {e}", ok=False)


# ---------------------------------------------------------------- HC ZIP --
def probe_hc_brojenje():
    p = ckan.package_show(CKAN_PAKETI["hc_brojenje_2025"])
    res = p["resources"][0]
    url = res["url"]
    zip_put = http.preuzmi(url, _dir("hc_brojenje") / "brojenje_2025.zip", timeout=300)
    # ZIP sadrži ugniježđene ZIP-ove („csv 2025.zip“, „xls 2025.zip“), pa ih raspakiramo rekurzivno.
    def _raspakiraj(z: zipfile.ZipFile, prefiks: str = ""):
        for ime in z.namelist():
            if ime.endswith("/"):
                continue
            b = z.read(ime)
            if ime.lower().endswith(".zip"):
                yield from _raspakiraj(zipfile.ZipFile(io.BytesIO(b)), prefiks + ime + "/")
            else:
                yield prefiks + ime, b

    datoteke = [(i, b) for i, b in _raspakiraj(zipfile.ZipFile(zip_put)) if not i.lower().endswith(".xls")]
    nalazi = [f"ZIP: {len(datoteke)} datoteka (bez .xls duplikata): {[i for i, _ in datoteke]}"]
    tekst_detalj = []
    for ime, sadrzaj in datoteke:
        dno = ime.lower()
        if dno.endswith((".csv", ".txt")):
            for enc in ("utf-8-sig", "cp1250", "latin-1"):
                try:
                    t = sadrzaj.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            linije = t.splitlines()
            tekst_detalj.append(f"--- {ime} ({enc}, {len(linije)} redaka)\n" + "\n".join(linije[:8]))
            for l in linije:
                if "murter" in l.lower():
                    tekst_detalj.append(f"    MURTER: {l}")
            nalazi.append(f"{ime}: PLDP u zaglavlju={'PLDP' in t[:3000].upper()}, Murter={'murter' in t.lower()}")
        elif dno.endswith((".xlsx", ".xls")):
            import pandas as pd
            try:
                listovi = pd.read_excel(io.BytesIO(sadrzaj), sheet_name=None, header=None, nrows=12)
                for lst, df in listovi.items():
                    tekst_detalj.append(f"--- {ime} / list {lst}\n{df.to_string(max_cols=20)[:2500]}")
                svi = pd.read_excel(io.BytesIO(sadrzaj), sheet_name=None, header=None)
                for lst, df in svi.items():
                    s = df.astype(str)
                    maska = s.apply(lambda c: c.str.contains("Murter", case=False, na=False)).any(axis=1)
                    for _, red in df[maska].iterrows():
                        tekst_detalj.append(f"    MURTER ({lst}): {list(red.values)}")
                    pldp = s.apply(lambda c: c.str.contains("PLDP", case=False, na=False)).any().any()
                    nalazi.append(f"{ime}/{lst}: {df.shape}, PLDP={pldp}, Murter={int(maska.sum())} redaka")
            except Exception as e:
                nalazi.append(f"{ime}: ne mogu čitati ({e})")
        else:
            nalazi.append(f"{ime}: {len(sadrzaj)} B (preskočeno)")
    _detalj("HC brojenje 2025 – sadržaj ZIP-a", "\n".join(tekst_detalj))
    _red("HC brojenje 2025 (ZIP)", url, 200, zip_put.stat().st_size, " | ".join(nalazi))


# ---------------------------------------------------------------- DZS -----
def _xlsx_pregled(izvor: str, paket_kljuc: str, resurs_naziv: str | None, url_sadrzi: str | None,
                  trazi: list[str]):
    import pandas as pd
    p = ckan.package_show(CKAN_PAKETI[paket_kljuc])
    res = ckan.nadji_resurs(p, naziv_sadrzi=resurs_naziv, url_sadrzi=url_sadrzi)
    url = res["url"]
    put = http.preuzmi(url, _dir(izvor) / Path(url).name, timeout=300)
    listovi = pd.read_excel(put, sheet_name=None, header=None)
    nalazi, det = [], []
    for lst, df in listovi.items():
        nalazi.append(f"list '{lst}' {df.shape}")
        det.append(f"--- list '{lst}' {df.shape}\n{df.head(15).to_string(max_cols=25, max_colwidth=40)}")
        s = df.astype(str)
        for pojam in trazi:
            maska = s.apply(lambda c: c.str.contains(pojam, case=False, na=False, regex=False)).any(axis=1)
            idx = list(df.index[maska][:5])
            if idx:
                det.append(f"    '{pojam}' u redcima {idx}:")
                for i in idx[:3]:
                    det.append("      " + " | ".join(str(v) for v in df.loc[i].values[:20]))
                nalazi.append(f"'{pojam}' u '{lst}' (redak {idx[0]}, ukupno {int(maska.sum())})")
    _detalj(f"{izvor} – {Path(url).name}", "\n".join(det))
    _red(izvor, url, 200, put.stat().st_size, "; ".join(nalazi))


def probe_dzs():
    _xlsx_pregled("dzs_naselja", "dzs_popis", "Stanovništvo po naseljima", None,
                  ["Šibensko-kninska", "Murter", "Zlarin", "Prvić", "Krapanj", "65"])
    _xlsx_pregled("dzs_jls", "dzs_popis", "Stanovništvo po gradovima i općinama", None,
                  ["Šibensko-kninska", "Tisno"])
    _xlsx_pregled("dzs_stanovi", "dzs_stanovi", "po gradovima i općinama", None,
                  ["odmor", "rekreacij", "Tisno", "Šibensko-kninska"])
    _xlsx_pregled("dzs_gradovi", "dzs_gradovi", None, "gradovi-u-statistici",
                  ["Tisno", "postelj", "noćenj", "dolas", "turist"])


def probe_dzs_turizam():
    # Poveznica izravno vraća PDF publikacije (nema XLSX-a), pa tablicu 2.11 čitamo pdfplumberom.
    url = "https://podaci.dzs.hr/2026/en/122435"
    r = _get("dzs_turizam", "turizam_2025.pdf", url, timeout=300)
    nalaz = f"Content-Type={r.headers.get('Content-Type')}; PDF={r.content[:4] == b'%PDF'}"
    if r.content[:4] == b"%PDF":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            str_211 = [i + 1 for i, p in enumerate(pdf.pages) if "2.11." in (p.extract_text() or "")[:200]]
            tekst = next((p.extract_text() for p in pdf.pages if "Šibensko-kninska županija" in (p.extract_text() or "")
                          and "2.11." in (p.extract_text() or "")[:200]), "")
        k = tekst.find("Šibensko-kninska županija")
        _detalj("DZS Turizam 2025, tablica 2.11 (ŠKŽ)", tekst[k:k + 1500])
        nalaz += f"; stranica={len(str_211) and str_211}; tablica 2.11 ŠKŽ pronađena={k >= 0}"
    _red("DZS Turizam u 2025. (PDF)", url, r.status_code, len(r.content), nalaz, ok=r.ok)


# ---------------------------------------------------------------- WFS -----
def _sazetak_capabilities(xml: str) -> str:
    tipovi = re.findall(r"<(?:wfs:)?Name>([^<]+)</(?:wfs:)?Name>", xml)
    crs = sorted(set(re.findall(r"(?:Default|Other)(?:CRS|SRS)>([^<]+)<", xml)))
    formati = sorted(set(re.findall(r"<(?:ows:)?Value>([^<]*(?:json|gml|shape)[^<]*)</(?:ows:)?Value>", xml, re.I)))
    return f"tipovi={tipovi[:30]}; CRS={crs[:8]}; formati={formati[:10]}"


def probe_hc_wfs():
    r = _get("hc_wfs", "capabilities.xml", HC_WFS, {"service": "WFS", "request": "GetCapabilities"})
    _red("HC WFS GetCapabilities", r.url, r.status_code, len(r.content), _sazetak_capabilities(r.text), ok=r.ok)
    _detalj("HC WFS capabilities (početak)", r.text[:4000])
    tip = next((t for t in re.findall(r"<(?:wfs:)?Name>([^<]+)</(?:wfs:)?Name>", r.text) if "RoadLink" in t
                and "Sequence" not in t), "tn-ro:RoadLink")
    r2 = _get("hc_wfs", "describe_roadlink.xml", HC_WFS,
              {"service": "WFS", "version": "2.0.0", "request": "DescribeFeatureType", "typeNames": tip})
    elementi = re.findall(r'element name="([^"]+)"', r2.text)
    _red("HC WFS DescribeFeatureType " + tip, r2.url, r2.status_code, len(r2.content),
         f"elementi: {elementi[:40]}", ok=r2.ok)
    x0, y0, x1, y1 = TISNO_BBOX
    r3 = _get("hc_wfs", "getfeature_tisno.xml", HC_WFS,
              {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeNames": tip, "count": 5,
               "bbox": f"{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::4326"})
    # Prefiks prostora imena sadrži crticu (hc_inspire_tn-ro), pa \w nije dovoljan.
    n = len(re.findall(r"<(?:[\w.-]+:)?RoadLink\s", r3.text))
    _red("HC WFS GetFeature (Tisno, count=5)", r3.url, r3.status_code, len(r3.content),
         f"RoadLink elemenata: {n}; početak: {r3.text[:300]!r}", ok=r3.ok and n > 0)
    _detalj("HC WFS GetFeature Tisno", r3.text[:5000])
    # Ceste (Road) nose oznaku ceste — provjeri i njih.
    r4 = _get("hc_wfs", "getfeature_road_tisno.xml", HC_WFS,
              {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
               "typeNames": tip.replace("RoadLink", "Road"), "count": 3,
               "bbox": f"{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::4326"})
    _detalj("HC WFS GetFeature Road Tisno", r4.text[:4000])
    _red("HC WFS GetFeature Road (Tisno)", r4.url, r4.status_code, len(r4.content),
         f"početak: {r4.text[:200]!r}", ok=r4.ok)


def probe_hac_wfs():
    r = _get("hac_wfs", "capabilities.xml", HAC_WFS,
             {"service": "WFS", "request": "GetCapabilities", "version": "2.0.0"})
    _red("HAC WFS GetCapabilities", r.url, r.status_code, len(r.content), _sazetak_capabilities(r.text), ok=r.ok)


def probe_dgu_rgi():
    url = "https://rgi.dgu.hr/geoserver/wfshr/wfs"
    r = _get("dgu_rgi", "capabilities.xml", url, {"service": "WFS", "request": "GetCapabilities", "version": "2.0.0"})
    _red("DGU RGI WFS GetCapabilities", r.url, r.status_code, len(r.content), _sazetak_capabilities(r.text), ok=r.ok)
    tipovi = re.findall(r"<(?:wfs:)?Name>([^<]+)</(?:wfs:)?Name>", r.text)
    x0, y0, x1, y1 = (15.55, 43.76, 15.70, 43.86)
    for tip in tipovi[:6]:
        try:
            rr = _get("dgu_rgi", f"getfeature_{tip.replace(':', '_')}.json", url,
                      {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeNames": tip,
                       "count": 5, "outputFormat": "application/json",
                       "bbox": f"{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::4326"})
            try:
                js = rr.json()
                prop = js["features"][0]["properties"] if js.get("features") else {}
                nalaz = f"{len(js.get('features', []))} objekata; svojstva: {prop}"
            except Exception:
                nalaz = f"nije JSON: {rr.text[:200]!r}"
            _red(f"DGU RGI GetFeature {tip}", rr.url, rr.status_code, len(rr.content), nalaz, ok=rr.ok)
        except Exception as e:
            _red(f"DGU RGI GetFeature {tip}", url, "-", "-", str(e), ok=False)


def probe_dgu_au():
    url = "https://geoportal.dgu.hr/services/atom/au/xml"
    r = _get("dgu_au", "atom.xml", url)
    linkovi = re.findall(r'href="([^"]+)"', r.text)
    _detalj("DGU AU ATOM", r.text[:5000])
    _red("DGU Upravne jedinice ATOM", url, r.status_code, len(r.content),
         f"poveznica: {len(linkovi)}; {[l for l in linkovi if 'zip' in l.lower() or 'gml' in l.lower() or 'atom' in l.lower()][:10]}",
         ok=r.ok)


# ---------------------------------------------------------------- EFFIS ---
def probe_effis():
    r = _get("effis", "wms_capabilities.xml", EFFIS_WMS,
             {"service": "WMS", "request": "GetCapabilities", "version": "1.3.0"}, timeout=180)
    slojevi = re.findall(r"<Name>([^<]+)</Name>", r.text)
    ecm = [s for s in slojevi if s.startswith(("ecmwf", "mf0"))]
    # TIME dimenzija za FWI sloj
    blok = r.text[r.text.find(f"<Name>{EFFIS_FWI_SLOJ}</Name>"):][:4000]
    dim = re.search(r"<Dimension[^>]*name=\"time\"[^>]*>([^<]*)<", blok)
    _red("EFFIS WMS GetCapabilities", r.url, r.status_code, len(r.content),
         f"slojeva: {len(slojevi)}; ecmwf*: {ecm[:30]}; TIME({EFFIS_FWI_SLOJ}): {dim.group(1)[:200] if dim else 'nema'}",
         ok=r.ok)
    _detalj("EFFIS FWI sloj u capabilities", blok[:3000])
    lon, lat = MURTER
    d = 0.5
    # mf010.fwi nije queryable; queryable je mf010.query, ali za Murter vraća prazan Feature.
    for dan in (DANAS, POVIJESNI_DAN):
        for fmt in ("text/plain",):
            params = {"service": "WMS", "version": "1.1.1", "request": "GetFeatureInfo",
                      "layers": "mf010.query", "query_layers": "mf010.query", "srs": "EPSG:4326",
                      "bbox": f"{lon-d},{lat-d},{lon+d},{lat+d}", "width": 101, "height": 101,
                      "x": 50, "y": 50, "info_format": fmt, "time": dan, "styles": ""}
            try:
                rr = _get("effis", f"gfi_{dan}_{fmt.replace('/', '_')}.txt", EFFIS_WMS, params)
                _red(f"EFFIS GetFeatureInfo FWI {dan} ({fmt})", rr.url, rr.status_code, len(rr.content),
                     rr.text[:400].replace("\n", " ⏎ "), ok=rr.ok)
            except Exception as e:
                _red(f"EFFIS GetFeatureInfo FWI {dan} ({fmt})", EFFIS_WMS, "-", "-", str(e), ok=False)
    x0, y0, x1, y1 = SKZ_BBOX
    for fmt in ("image/tiff", "image/geotiff"):
        params = {"service": "WMS", "version": "1.1.1", "request": "GetMap", "layers": EFFIS_FWI_SLOJ,
                  "srs": "EPSG:4326", "bbox": f"{x0},{y0},{x1},{y1}", "width": 120, "height": 90,
                  "format": fmt, "time": POVIJESNI_DAN, "styles": ""}
        rr = _get("effis", f"getmap_{fmt.replace('/', '_')}.tif", EFFIS_WMS, params)
        nalaz = f"Content-Type={rr.headers.get('Content-Type')}"
        try:
            import rasterio
            with rasterio.MemoryFile(rr.content) as mf, mf.open() as ds:
                a = ds.read()
                nalaz += f"; pojasevi={ds.count}, dtype={ds.dtypes[0]}, min={a.min()}, max={a.max()}, crs={ds.crs}"
        except Exception as e:
            nalaz += f"; nije raster: {rr.text[:150]!r}" if "xml" in (rr.headers.get("Content-Type") or "") else f"; {e}"
        _red(f"EFFIS GetMap {fmt}", rr.url, rr.status_code, len(rr.content), nalaz, ok=rr.ok)
    rr = _get("effis", "legend_fwi.png", EFFIS_WMS,
              {"service": "WMS", "version": "1.1.1", "request": "GetLegendGraphic", "layer": EFFIS_FWI_SLOJ,
               "format": "image/png"})
    _red("EFFIS GetLegendGraphic FWI", rr.url, rr.status_code, len(rr.content),
         f"Content-Type={rr.headers.get('Content-Type')} (razrede pročitati sa slike)", ok=rr.ok)


def probe_effis_ba():
    x0, y0, x1, y1 = SKZ_BBOX
    # bbox BEZ oznake CRS-a: s ",EPSG:4326" MapServer očekuje lat,lon i vraća prazno.
    for fmt in ("geojson", None):
        params = {"service": "WFS", "version": "1.1.0", "request": "GetFeature", "typename": EFFIS_BA_SLOJ,
                  "bbox": f"{x0},{y0},{x1},{y1}", "maxfeatures": 2000}
        if fmt:
            params["outputformat"] = fmt
        try:
            rr = _get("effis_ba", f"ba_skz_{fmt or 'gml'}.dat", EFFIS_WMS, params, timeout=300)
            n = len(re.findall(r'"type":\s*"Feature"', rr.text)) or len(re.findall(r"<gml:featureMember|<ms:modis", rr.text))
            _red(f"EFFIS BA WFS bbox ŠKŽ ({fmt or 'GML'})", rr.url, rr.status_code, len(rr.content),
                 f"objekata≈{n}; početak: {rr.text[:300]!r}", ok=rr.ok and n > 0)
            if rr.ok and n > 0:
                break
        except Exception as e:
            _red(f"EFFIS BA WFS ({fmt})", EFFIS_WMS, "-", "-", str(e), ok=False)


# ---------------------------------------------------------------- ostalo --
def probe_worldcover():
    for tile in ("N42E015", "N42E012", "N45E015"):
        url = WORLDCOVER_URL.format(tile=tile)
        r = http.head(url)
        _red(f"WorldCover HEAD {tile}", url, r.status_code, r.headers.get("Content-Length"),
             f"Content-Type={r.headers.get('Content-Type')}, Last-Modified={r.headers.get('Last-Modified')}",
             ok=r.ok)


def probe_gisco():
    url = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326_LEVL_3.geojson"
    r = _get("gisco", "nuts3_2021.geojson", url, timeout=300)
    try:
        js = r.json()
        hr = [(f["properties"].get("NUTS_ID"), f["properties"].get("NAME_LATN"))
              for f in js["features"] if f["properties"].get("CNTR_CODE") == "HR"]
        _red("GISCO NUTS3 2021", url, r.status_code, len(r.content), f"HR regije: {hr}", ok=True)
    except Exception as e:
        _red("GISCO NUTS3 2021", url, r.status_code, len(r.content), str(e), ok=False)


def probe_osm():
    import networkx as nx
    import osmnx as ox
    ox.settings.useful_tags_way = list(set(ox.settings.useful_tags_way + ["bridge", "access", "ref", "name"]))
    ox.settings.cache_folder = str(_dir("osm") / "cache")
    filt = ('["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service"]'
            '["access"!~"private|no"]')
    # Otok Murter + Tisno + dio kopna (do D8 i dalje), da kopno ima „sigurnu“ stranu.
    bbox = (15.50, 43.74, 15.80, 43.88)  # (left, bottom, right, top) — osmnx 2.x redoslijed
    G = ox.graph_from_bbox(bbox, custom_filter=filt, simplify=True, retain_all=True, truncate_by_edge=True)
    U = nx.Graph(ox.convert.to_undirected(G))
    mostovi = set(nx.bridges(U))
    kand = []
    for u, v, d in U.edges(data=True):
        if d.get("bridge") and str(d.get("name", "")).strip() and d.get("highway") not in ("service",):
            kand.append((u, v, d))
    tisno = [(u, v, d) for u, v, d in U.edges(data=True)
             if d.get("bridge") and 15.63 < (U.nodes[u]["x"] + U.nodes[v]["x"]) / 2 < 15.65
             and 43.79 < (U.nodes[u]["y"] + U.nodes[v]["y"]) / 2 < 43.81]
    opis = []
    for u, v, d in tisno:
        jest_most = (u, v) in mostovi or (v, u) in mostovi
        opis.append(f"most osm={d.get('osmid')} ime={d.get('name')} ref={d.get('ref')} highway={d.get('highway')} "
                    f"bridge={d.get('bridge')} → most grafa={jest_most}")
    # Je li Murter (naselje) odvojen od kopna mostom grafa?
    murter_cvor = ox.distance.nearest_nodes(G, *MURTER)
    kopno_cvor = ox.distance.nearest_nodes(G, 15.75, 43.80)
    H = U.copy()
    H.remove_edges_from(mostovi)
    povezani_bez_mostova = nx.has_path(H, murter_cvor, kopno_cvor)
    _detalj("OSM Tisno mostovi", "\n".join(opis) or "nema bridge bridova kod Tisna")
    _red("OSM (OSMnx) Murter–Tisno", "Overpass API via OSMnx", 200, f"{U.number_of_nodes()} čvorova",
         f"bridova={U.number_of_edges()}, mostova grafa={len(mostovi)}; Tisno: {' || '.join(opis)}; "
         f"Murter↔kopno bez mostova grafa povezani={povezani_bez_mostova} (False → Murter je E1)",
         ok=bool(tisno))


PROBE = {
    "ckan": probe_ckan, "hc_brojenje": probe_hc_brojenje, "dzs": probe_dzs, "dzs_turizam": probe_dzs_turizam,
    "hc_wfs": probe_hc_wfs, "hac_wfs": probe_hac_wfs, "dgu_rgi": probe_dgu_rgi, "dgu_au": probe_dgu_au,
    "effis": probe_effis, "effis_ba": probe_effis_ba, "worldcover": probe_worldcover, "gisco": probe_gisco,
    "osm": probe_osm,
}


def pisi_izvjestaj():
    DOCS_DIR.mkdir(exist_ok=True)
    linije = [
        "# Izvješće probe izvora",
        "",
        f"Generirano: {dt.datetime.now().isoformat(timespec='seconds')} naredbom `python -m etl.probe`.",
        "Sirovi odgovori su u `data/raw/<izvor>_probe/` (nisu u gitu).",
        "",
        "| Izvor | URL | HTTP | Veličina | Nalaz | Status |",
        "|---|---|---|---|---|---|",
    ]
    for r in redovi:
        nalaz = str(r["nalaz"]).replace("|", "\\|").replace("\n", " ")[:900]
        url = str(r["url"])[:200].replace("|", "%7C")
        linije.append(f"| {r['izvor']} | {url} | {r['http']} | {r['velicina']} | {nalaz} | {r['status']} |")
    linije += ["", "## Detalji", ""] + detalji
    (DOCS_DIR / "probe_report.md").write_text("\n".join(linije), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samo", help="zarezom odvojena imena proba: " + ",".join(PROBE))
    args = ap.parse_args()
    imena = args.samo.split(",") if args.samo else list(PROBE)
    for ime in imena:
        try:
            PROBE[ime]()
        except Exception as e:
            _red(ime, "-", "-", "-", f"{type(e).__name__}: {e}", ok=False)
            traceback.print_exc()
    pisi_izvjestaj()
    print(f"\nIzvješće: {DOCS_DIR / 'probe_report.md'}")


if __name__ == "__main__":
    main()
