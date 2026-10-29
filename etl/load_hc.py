"""Hrvatske ceste: brojenje prometa (PLDP, validacija D6) i WFS mreže javnih cesta (validacija OSM-a).

Brojenje: CKAN paket „brojenje-prometa-…-2025“ → ZIP s ugniježđenim
„csv 2025.zip“ → „Promet na cestama Republike Hrvatske 2025.csv“ (cp1250, ';'):
Oznaka ceste; Brojačko mjesto/Oznaka; Brojačko mjesto/Ime; PGDP; PLDP; …
(npr. 121;5304;Murter;2940;5835). Brojila nemaju koordinate, pa ih s uskim
grlom povezujemo po broju ceste (D121 → 121) i imenu naselja iza reza, uz
ručno nadjačavanje u data/manual/brojila_hc.csv.

WFS: RoadLink ima samo geometriju (EPSG:3765) bez oznake ceste, pa ga koristimo
za provjeru: koliki udio duljine javnih cesta HC-a u županiji pokriva OSM graf.
"""
from __future__ import annotations

import csv
import io
import re
import zipfile

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

from etl import ckan, http, izvori
from etl.config import HC_WFS, MANUAL_DIR, RAW_DIR
from etl.match_settlements import norm

PAKET_BROJENJE = "brojenje-prometa-na-cestama-republike-hrvatske-godine-{godina}"


def _datoteke_zipa(z: zipfile.ZipFile):
    for ime in z.namelist():
        b = z.read(ime)
        if ime.lower().endswith(".zip"):
            yield from _datoteke_zipa(zipfile.ZipFile(io.BytesIO(b)))
        else:
            yield ime, b


def ucitaj_pldp(godina: int = 2025) -> pd.DataFrame:
    """Tablica brojila: cesta, brojilo, naziv, pgdp, pldp, godina."""
    paket = ckan.package_show(PAKET_BROJENJE.format(godina=godina))
    res = paket["resources"][0]
    put = http.preuzmi(res["url"], RAW_DIR / "hc_brojenje" / f"brojenje_{godina}.zip", timeout=300)
    opis = ckan.opis_izvora(paket, res)
    izvori.zabiljezi(f"hc_brojenje_{godina}", url=opis["url"], url_paketa=opis["url_paketa"],
                     metadata_modified=opis["metadata_modified"], dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    for ime, b in _datoteke_zipa(zipfile.ZipFile(put)):
        if ime.lower().startswith("promet na cestama") and ime.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(b), sep=";", encoding="cp1250", dtype=str)
            break
    else:
        raise FileNotFoundError("U ZIP-u HC-a nema datoteke 'Promet na cestama … .csv'")
    c = {k: next(col for col in df.columns if k.lower() in col.lower())
         for k in ("Oznaka ceste", "Brojačko mjesto/Oznaka", "Brojačko mjesto/Ime", "PGDP", "PLDP")}
    broj = lambda s: pd.to_numeric(s.str.replace(".", "", regex=False).str.strip(), errors="coerce")
    return pd.DataFrame({
        "cesta": df[c["Oznaka ceste"]].str.strip(),
        "brojilo": df[c["Brojačko mjesto/Oznaka"]].str.strip(),
        "naziv": df[c["Brojačko mjesto/Ime"]].str.strip(),
        "pgdp": broj(df[c["PGDP"]]),
        "pldp": broj(df[c["PLDP"]]),
        "godina": godina,
    })


def _rucna_brojila() -> dict:
    """usko grlo (oznaka ceste + naselje) → brojilo, iz data/manual/brojila_hc.csv."""
    put = MANUAL_DIR / "brojila_hc.csv"
    if not put.exists():
        return {}
    with open(put, encoding="utf-8", newline="") as f:
        redovi = list(csv.reader(f))[2:]
    return {(r[1].strip(), norm(r[2])): r[0].strip() for r in redovi if len(r) >= 3}


def pldp_za_usko_grlo(pldp: pd.DataFrame, cesta_ref: str | None, nazivi_iza: list[str]) -> dict | None:
    """PLDP brojila na istoj cesti čije ime odgovara naselju iza reza (ili ručno pridruženo)."""
    if not cesta_ref or pldp is None or pldp.empty:
        return None
    m = re.search(r"(\d+)", str(cesta_ref))
    if not m:
        return None
    broj = m.group(1)
    rucna = _rucna_brojila()
    kand = pldp[pldp.cesta == broj]
    for naziv in nazivi_iza:
        b = rucna.get((broj, norm(naziv)))
        if b:
            kand_b = pldp[pldp.brojilo == b]
            if len(kand_b):
                r = kand_b.iloc[0]
                return {"godina": int(r.godina), "vrijednost": int(r.pldp), "brojilo": r.brojilo, "naziv": r.naziv}
    for naziv in nazivi_iza:
        pogodak = kand[kand.naziv.map(norm).str.contains(norm(naziv), regex=False)]
        if len(pogodak) and pd.notna(pogodak.iloc[0].pldp):
            r = pogodak.iloc[0]
            return {"godina": int(r.godina), "vrijednost": int(r.pldp), "brojilo": r.brojilo, "naziv": r.naziv}
    return None


def hc_roadlinks(bbox_wgs84: tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    """RoadLink geometrije iz HC WFS-a (GML 3.2, EPSG:3765), stranicama po 5000."""
    x0, y0, x1, y1 = bbox_wgs84
    linije, start = [], 0
    # Poslužitelj vraća najviše 50 objekata po zahtjevu (provjereno 29.10.2026.), pa straničimo
    # do numberMatched.
    while True:
        params = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                  "typeNames": "hc_inspire_tn-ro:RoadLink", "count": 1000, "startIndex": start,
                  "bbox": f"{y0},{x0},{y1},{x1},urn:ogc:def:crs:EPSG::4326"}
        put = http.preuzmi(HC_WFS, RAW_DIR / "hc_wfs" / f"roadlink_{x0}_{y0}_{x1}_{y1}_{start}.xml",
                           params=params, timeout=300)
        tekst = put.read_text(encoding="utf-8")
        nove = re.findall(r"<gml:posList[^>]*>([^<]+)</gml:posList>", tekst)
        for pl in nove:
            v = [float(x) for x in pl.split()]
            # EPSG:3765 (HTRS96/TM) ima redoslijed osi (E, N) — x, y.
            if len(v) >= 4:
                linije.append(LineString(list(zip(v[0::2], v[1::2]))))
        vraceno = int(re.search(r'numberReturned="(\d+)"', tekst).group(1))
        ukupno = int(re.search(r'numberMatched="(\d+)"', tekst).group(1))
        start += vraceno
        if vraceno == 0 or start >= ukupno:
            break
    izvori.zabiljezi("hc_wfs", url=HC_WFS)
    return gpd.GeoDataFrame(geometry=linije, crs="EPSG:3765")


def pokrivenost_osm(hc: gpd.GeoDataFrame, osm_bridovi: gpd.GeoDataFrame, poligon, tolerancija_m: float = 30) -> dict:
    """Udio duljine HC javnih cesta (unutar poligona) koji je unutar 30 m od OSM grafa."""
    hc = hc.clip(poligon)
    ukupno = hc.length.sum()
    pufer = osm_bridovi.buffer(tolerancija_m).union_all()
    pokriveno = hc.intersection(pufer).length.sum()
    return {"hc_km": round(ukupno / 1000, 1), "pokriveno_km": round(pokriveno / 1000, 1),
            "udio": round(pokriveno / ukupno, 4) if ukupno else None, "tolerancija_m": tolerancija_m}
