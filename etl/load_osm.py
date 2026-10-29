"""OpenStreetMap: cestovni graf (D2), graf putova `track` (D7), turistički objekti (D5).

Zašto OSM: jedini otvoreni izvor koji ima i nerazvrstane ceste i šumske putove.
Javne ceste HC-a (WFS) koristimo samo za provjeru pokrivenosti (load_hc.py).

Graf se dohvaća preko Overpass API-ja (OSMnx) za poligon županije + 15 km
i sprema u data/interim/ (pickle), jer dohvat traje nekoliko minuta.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd

from etl import http, izvori
from etl.config import (ACCESS_ISKLJUCI, CRS_ANALIZA, HIGHWAY_GLAVNI, HIGHWAY_TRACK, INTERIM_DIR, RAW_DIR,
                        TOURISM_OZNAKE)

# Atributi koje OSMnx inače odbacuje, a trebaju nam (most, pristup, oznaka ceste, broj traka).
DODATNE_OZNAKE = ["bridge", "access", "ref", "name", "lanes", "tunnel", "service", "motor_vehicle"]


def _postavi_osmnx():
    ox.settings.useful_tags_way = sorted(set(ox.settings.useful_tags_way) | set(DODATNE_OZNAKE))
    ox.settings.cache_folder = str(RAW_DIR / "osm" / "cache")
    ox.settings.use_cache = True
    ox.settings.log_console = False
    ox.settings.requests_timeout = 600
    # Overpass: OSMnx sam čeka slobodan slot; User-Agent postavljamo kao i za ostale izvore.
    ox.settings.http_user_agent = "JedanIzlaz/0.1 (studentski projekt, Datathon 2026)"


def filter_glavni() -> str:
    hw = "|".join(HIGHWAY_GLAVNI)
    acc = "|".join(ACCESS_ISKLJUCI)
    return f'["highway"~"^({hw})$"]["access"!~"^({acc})$"]["motor_vehicle"!~"^({acc})$"]'


def filter_kombinirani() -> str:
    """Ceste + putovi `track` u JEDNOM grafu (D7).

    Zašto ne zaseban graf putova: OSMnx pri pojednostavljenju briše čvorove
    stupnja 2, pa bi se izgubila mjesta gdje se put spaja s cestom. U zajedničkom
    grafu ta raskrižja ostaju.
    """
    hw = "|".join(HIGHWAY_GLAVNI + HIGHWAY_TRACK)
    acc = "|".join(ACCESS_ISKLJUCI)
    return f'["highway"~"^({hw})$"]["access"!~"^({acc})$"]["motor_vehicle"!~"^({acc})$"]'


def _u_graph(G: nx.MultiDiGraph) -> nx.Graph:
    """MultiDiGraph → neusmjereni Graph; broj paralelnih bridova pamtimo u 'paralelno' (D2).

    Paralelni brid (npr. dvije odvojene kolničke trake između istih čvorova)
    znači da veza nije jedno usko grlo, pa mu je u D4 v2 kapacitet = paralelno.
    """
    M = ox.convert.to_undirected(G)
    H = nx.Graph()
    H.graph.update(M.graph)
    H.add_nodes_from(M.nodes(data=True))
    for u, v, d in M.edges(data=True):
        if u == v:
            continue  # petlje ne pridonose povezanosti
        if H.has_edge(u, v):
            H[u][v]["paralelno"] += 1
            # Zadrži atribute „jače“ ceste (most ostaje most ako je ijedan od njih most).
            if d.get("bridge") and not H[u][v].get("bridge"):
                H[u][v]["bridge"] = d.get("bridge")
        else:
            H.add_edge(u, v, **{k: d.get(k) for k in ("osmid", "highway", "ref", "name", "bridge", "length",
                                                       "lanes", "tunnel", "geometry")}, paralelno=1)
    for _, _, d in H.edges(data=True):
        hw = d.get("highway")
        d["highway"] = hw[0] if isinstance(hw, list) else hw
        br = d.get("bridge")
        br = br if isinstance(br, list) else [br]
        d["pokretni_most"] = "movable" in br
        d["most"] = any(b not in (None, "no") for b in br)
        ref = d.get("ref")
        d["ref"] = ref[0] if isinstance(ref, list) else ref
        nm = d.get("name")
        d["name"] = nm[0] if isinstance(nm, list) else nm
    return H


GEOFABRIK_URL = "https://download.geofabrik.de/europe/croatia-latest.osm.pbf"  # izvor: Geofabrik (ODbL)


def pbf() -> Path:
    """Geofabrik izvadak za Hrvatsku (~200 MB, dnevno osvježavan)."""
    put = http.preuzmi(GEOFABRIK_URL, RAW_DIR / "osm" / "croatia-latest.osm.pbf", timeout=1800)
    izvori.zabiljezi("osm", url=GEOFABRIK_URL, dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    return put


def _prihvati_cestu(tags, highway_dozvoljeni: set) -> bool:
    hw = tags.get("highway")
    if hw not in highway_dozvoljeni:
        return False
    return tags.get("access") not in ACCESS_ISKLJUCI and tags.get("motor_vehicle") not in ACCESS_ISKLJUCI


def _izdvoji_xml(pbf_put: Path, poligon_wgs84, highway_dozvoljeni: set, odrediste: Path) -> Path:
    """Dva prolaza osmiumom: (1) ceste s barem jednim čvorom u omotnici poligona,
    (2) zapiši te putove i njihove čvorove u OSM XML (za ox.graph_from_xml)."""
    import osmium

    x0, y0, x1, y1 = poligon_wgs84.bounds
    putovi, cvorovi = set(), set()
    for w in osmium.FileProcessor(str(pbf_put)).with_locations().with_filter(osmium.filter.KeyFilter("highway")):
        if not w.is_way() or not _prihvati_cestu(w.tags, highway_dozvoljeni):
            continue
        if any(n.location.valid() and x0 <= n.lon <= x1 and y0 <= n.lat <= y1 for n in w.nodes):
            putovi.add(w.id)
            cvorovi.update(n.ref for n in w.nodes)
    odrediste.parent.mkdir(parents=True, exist_ok=True)
    if odrediste.exists():
        odrediste.unlink()
    with osmium.SimpleWriter(str(odrediste)) as pisac:
        for o in osmium.FileProcessor(str(pbf_put), osmium.osm.NODE | osmium.osm.WAY):
            if (o.is_node() and o.id in cvorovi) or (o.is_way() and o.id in putovi):
                pisac.add(o)
    return odrediste


def dohvati_graf(poligon_wgs84, kljuc: str, vrsta: str = "glavni", osvjezi: bool = False) -> nx.Graph:
    """Neusmjereni graf za poligon (EPSG:4326) iz Geofabrik PBF-a.

    vrsta: "glavni" (vozive ceste, D2–D6) ili "kombinirani" (ceste + track, D7).
    retain_all=True je obavezan: bez njega OSMnx odbacuje nepovezane otočne
    mreže (Zlarin, Žirje) i E0 se ne bi mogao otkriti.

    Zašto PBF, a ne Overpass: 28.10.2026. javni Overpass je vraćao 502 („at capacity“),
    a PBF daje isti rezultat ponovljivo i bez opterećenja tuđeg servisa (plan B iz CLAUDE.md).
    """
    _postavi_osmnx()
    put = INTERIM_DIR / f"graf_{kljuc}_{vrsta}.pkl"
    if put.exists() and not osvjezi:
        with open(put, "rb") as f:
            return pickle.load(f)
    dozvoljeni = set(HIGHWAY_GLAVNI) | (set(HIGHWAY_TRACK) if vrsta == "kombinirani" else set())
    xml = _izdvoji_xml(pbf(), poligon_wgs84, dozvoljeni, INTERIM_DIR / f"osm_{kljuc}_{vrsta}.osm")
    Gd = ox.graph_from_xml(xml, bidirectional=False, simplify=False, retain_all=True)
    # Isto kao graph_from_polygon(..., truncate_by_edge=True): zadrži bridove koji diraju poligon.
    Gd = ox.truncate.truncate_graph_polygon(Gd, poligon_wgs84, truncate_by_edge=True)
    Gd = ox.simplification.simplify_graph(Gd)
    G = _u_graph(Gd)
    put.parent.mkdir(parents=True, exist_ok=True)
    with open(put, "wb") as f:
        pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
    return G


def dohvati_objekte(poligon_wgs84, oznake: dict, ime: str, osvjezi: bool = False) -> gpd.GeoDataFrame:
    """OSM čvorovi i putovi s danim oznakama → točka (čvor ili središte puta), EPSG:3765.

    Relacije (npr. multipoligon kampa) preskačemo — rijetke su i ne mijenjaju udjele bitno.
    """
    import osmium

    put = INTERIM_DIR / f"osm_{ime}.gpkg"
    if put.exists() and not osvjezi:
        return gpd.read_file(put)
    kljuc, vrijednosti = next(iter(oznake.items()))
    vrijednosti = set(vrijednosti)
    x0, y0, x1, y1 = poligon_wgs84.bounds
    redovi = []
    for o in osmium.FileProcessor(str(pbf())).with_locations().with_filter(osmium.filter.KeyFilter(kljuc)):
        if o.tags.get(kljuc) not in vrijednosti:
            continue
        if o.is_node():
            lon, lat = o.lon, o.lat
        elif o.is_way():
            tocke = [(n.lon, n.lat) for n in o.nodes if n.location.valid()]
            if not tocke:
                continue
            lon, lat = sum(t[0] for t in tocke) / len(tocke), sum(t[1] for t in tocke) / len(tocke)
        else:
            continue
        if x0 <= lon <= x1 and y0 <= lat <= y1:
            redovi.append({"osm_id": f"{o.type_str()}{o.id}", "name": o.tags.get("name"), kljuc: o.tags.get(kljuc),
                           "lon": lon, "lat": lat})
    df = pd.DataFrame(redovi, columns=["osm_id", "name", kljuc, "lon", "lat"])
    gdf = gpd.GeoDataFrame(df.drop(columns=["lon", "lat"]), geometry=gpd.points_from_xy(df.lon, df.lat),
                           crs="EPSG:4326")
    gdf = gdf[gdf.within(poligon_wgs84)].to_crs(CRS_ANALIZA)
    gdf.to_file(put, driver="GPKG")
    return gdf


def turisticki_objekti(poligon_wgs84, osvjezi: bool = False) -> gpd.GeoDataFrame:
    return dohvati_objekte(poligon_wgs84, {"tourism": TOURISM_OZNAKE}, "tourism", osvjezi)


def mjesta(poligon_wgs84, osvjezi: bool = False) -> gpd.GeoDataFrame:
    return dohvati_objekte(poligon_wgs84, {"place": ["city", "town", "village", "hamlet", "suburb",
                                                     "isolated_dwelling", "locality", "neighbourhood"]},
                           "place", osvjezi)


def cvorovi_gdf(G: nx.Graph) -> gpd.GeoDataFrame:
    """Čvorovi grafa kao GeoDataFrame u EPSG:3765 (za prostorne upite)."""
    ids = list(G.nodes)
    gdf = gpd.GeoDataFrame({"cvor": ids},
                           geometry=gpd.points_from_xy([G.nodes[n]["x"] for n in ids],
                                                       [G.nodes[n]["y"] for n in ids]), crs="EPSG:4326")
    return gdf.to_crs(CRS_ANALIZA)
