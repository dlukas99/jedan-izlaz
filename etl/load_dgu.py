"""DGU Upravne jedinice (INSPIRE AU, ATOM) i Registar geografskih imena (WFS).

Kako radi:
1. ATOM feed (iz CKAN paketa „upravne-jedinice-inspire“) daje ZIP s jednim
   GML-om (~600 MB, EPSG:3035) za cijelu RH: država, županije, JLS, naselja,
   statistički i popisni krugovi.
2. GML čitamo streamingom (iterparse) i zadržavamo samo razine 2–4
   (županija, JLS, naselje). Svako naselje ima matični broj (nationalCode)
   i nadređenu JLS (upperLevelUnit) — to je ključ za spajanje s DZS-om.
3. Rezultat spremamo u data/interim/dgu_au.gpkg da se GML ne parsira svaki put.

RGI: poligoni naselja u RH pokrivaju CIJELI teritorij (i šume i more uz obalu),
pa za „središte“ naselja koristimo službenu točku imena iz RGI-ja (tip „naselje“).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon, Point, Polygon

from etl import ckan, http, izvori
from etl.config import CRS_ANALIZA, INTERIM_DIR, RAW_DIR

AU = "{http://inspire.ec.europa.eu/schemas/au/4.0}"
GN = "{http://inspire.ec.europa.eu/schemas/gn/4.0}"
GML ="{http://www.opengis.net/gml/3.2}"
XLINK = "{http://www.w3.org/1999/xlink}"
ATOM_FEED = "https://geoportal.dgu.hr/services/atom/au/xml"  # izvor: CKAN upravne-jedinice-inspire → ATOM
RGI_WFS = "https://rgi.dgu.hr/geoserver/wfshr/wfs"            # izvor: CKAN registar-geografskih-imena
RAZINE = {"2ndOrder": "zupanija", "3rdOrder": "jls", "4thOrder": "naselje"}
AU_CACHE = INTERIM_DIR / "dgu_au.gpkg"


def _zip_url() -> str:
    """Iz ATOM feeda pročitaj poveznicu na ZIP (ne hardkodiramo je)."""
    r = http.get(ATOM_FEED)
    r.raise_for_status()
    m = re.search(r'href="([^"]+\.zip)"', r.text)
    if not m:
        raise RuntimeError("U ATOM feedu DGU-a nema poveznice na ZIP.")
    return m.group(1)


def _prsten(el) -> list[tuple[float, float]]:
    vrijednosti = [float(v) for v in el.find(f".//{GML}posList").text.split()]
    return list(zip(vrijednosti[0::2], vrijednosti[1::2]))


def _geometrija(el):
    """GML MultiSurface → shapely. Koordinate su u EPSG:3035 (os: x, y)."""
    poligoni = []
    for pol in el.iter(f"{GML}Polygon"):
        ext = pol.find(f"{GML}exterior")
        unutra = [_prsten(i) for i in pol.findall(f"{GML}interior")]
        poligoni.append(Polygon(_prsten(ext), unutra))
    if not poligoni:
        return None
    return poligoni[0] if len(poligoni) == 1 else MultiPolygon(poligoni)


def parsiraj_gml(gml: Path) -> gpd.GeoDataFrame:
    redovi = []
    for _, el in ET.iterparse(gml, events=("end",)):
        if el.tag != f"{AU}AdministrativeUnit":
            continue
        lvl = el.find(f"{AU}nationalLevel")
        razina = RAZINE.get((lvl.get(f"{XLINK}href", "") if lvl is not None else "").rsplit("/", 1)[-1])
        if razina:
            # Ime je u au:name/gn:GeographicalName/gn:spelling/gn:SpellingOfName/gn:text
            ime_el = el.find(f"{AU}name")
            tekst = list(ime_el.iter(f"{GN}text")) if ime_el is not None else []
            gore = el.find(f"{AU}upperLevelUnit")
            redovi.append({
                "gml_id": el.get(f"{GML}id"),
                "razina": razina,
                "sifra": (el.findtext(f"{AU}nationalCode") or "").strip(),
                "naziv": tekst[0].text.strip() if tekst else None,
                "nadredena_id": (gore.get(f"{XLINK}href", "").lstrip("#") if gore is not None else None),
                "nadredena_naziv": gore.get(f"{XLINK}title") if gore is not None else None,
                "geometry": _geometrija(el.find(f"{AU}geometry")),
            })
        el.clear()
    gdf = gpd.GeoDataFrame(redovi, geometry="geometry", crs="EPSG:3035").to_crs(CRS_ANALIZA)
    return gdf


def ucitaj_au(osvjezi: bool = False) -> gpd.GeoDataFrame:
    """Sve županije, JLS i naselja RH (EPSG:3765), s matičnim brojevima kao tekst."""
    if AU_CACHE.exists() and not osvjezi:
        return gpd.read_file(AU_CACHE)
    paket = ckan.package_show("upravne-jedinice-inspire")
    url = _zip_url()
    zip_put = http.preuzmi(url, RAW_DIR / "dgu_au" / "INSPIRE_AU.zip", timeout=1800)
    gml = RAW_DIR / "dgu_au" / "AdministrativeUnit.gml"
    if not gml.exists():
        with zipfile.ZipFile(zip_put) as z:
            z.extract("AdministrativeUnit.gml", gml.parent)
    gdf = parsiraj_gml(gml)
    AU_CACHE.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(AU_CACHE, driver="GPKG")
    izvori.zabiljezi("dgu_au", url=url, url_paketa="https://data.gov.hr/ckan/dataset/upravne-jedinice-inspire",
                     metadata_modified=paket.get("metadata_modified"),
                     dohvaceno=http.dohvati_meta(zip_put).get("dohvaceno"))
    return gdf


def zupanija(au: gpd.GeoDataFrame, naziv_dzs: str) -> gpd.GeoDataFrame:
    """Poligon županije po nazivu (DZS piše „Šibensko-kninska“, DGU „Šibensko-kninska županija“)."""
    z = au[(au.razina == "zupanija") & au.naziv.str.startswith(naziv_dzs)]
    if len(z) != 1:
        raise KeyError(f"Županija '{naziv_dzs}' nije jednoznačna u DGU AU: {list(z.naziv)}")
    return z


def jls_i_naselja(au: gpd.GeoDataFrame, zup: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    zid = zup.iloc[0].gml_id
    jls = au[(au.razina == "jls") & (au.nadredena_id == zid)].copy()
    nas = au[(au.razina == "naselje") & au.nadredena_id.isin(jls.gml_id)].copy()
    nas = nas.merge(jls[["gml_id", "naziv", "sifra"]].rename(
        columns={"gml_id": "nadredena_id", "naziv": "jls", "sifra": "jls_sifra"}), on="nadredena_id")
    return jls, nas


def ucitaj_rgi_naselja(bbox_wgs84: tuple[float, float, float, float], osvjezi: bool = False) -> gpd.GeoDataFrame:
    """Službene točke imena tipa „naselje“ (i dijelovi naselja) iz Registra geografskih imena."""
    put = RAW_DIR / "dgu_rgi" / "naselja_{:.2f}_{:.2f}_{:.2f}_{:.2f}.geojson".format(*bbox_wgs84)
    if not put.exists() or osvjezi:
        x0, y0, x1, y1 = bbox_wgs84
        params = {
            "service": "WFS", "version": "2.0.0", "request": "GetFeature",
            "typeNames": "wfshr:nippimenovanomjesto", "outputFormat": "application/json",
            # CQL_FILTER je GeoServer proširenje; filtriramo na poslužitelju da ne vučemo cijeli registar.
            "CQL_FILTER": f"vrstaobiljezja IN ('naselje','zaselak','dio naselja') AND "
                          f"BBOX(geom,{x0},{y0},{x1},{y1},'EPSG:4326')",
        }
        http.preuzmi(RGI_WFS, put, params=params, osvjezi=True, timeout=300)
        paket = ckan.package_show("registar-geografskih-imena")
        izvori.zabiljezi("dgu_rgi", url=RGI_WFS, metadata_modified=paket.get("metadata_modified"),
                         url_paketa="https://data.gov.hr/ckan/dataset/registar-geografskih-imena")
    gdf = gpd.read_file(put)
    if gdf.crs is None or gdf.crs.to_epsg() != 3765:
        gdf = gdf.set_crs(CRS_ANALIZA, allow_override=True)  # RGI vraća EPSG:3765 bez oznake u GeoJSON-u
    return gdf[["identifikator", "vrstaobiljezja", "geografskoime", "geometry"]]
