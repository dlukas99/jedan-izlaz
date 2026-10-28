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

from etl import izvori
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


def filter_track() -> str:
    return f'["highway"~"^({"|".join(HIGHWAY_TRACK)})$"]'


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


def dohvati_grafove(poligon_wgs84, kljuc: str, osvjezi: bool = False) -> tuple[nx.Graph, nx.Graph]:
    """Glavni graf i graf putova za poligon (EPSG:4326). Vraća neusmjerene Graph objekte."""
    _postavi_osmnx()
    put = INTERIM_DIR / f"graf_{kljuc}.pkl"
    if put.exists() and not osvjezi:
        with open(put, "rb") as f:
            return pickle.load(f)
    G = ox.graph_from_polygon(poligon_wgs84, custom_filter=filter_glavni(), simplify=True,
                              retain_all=True, truncate_by_edge=True)
    T = ox.graph_from_polygon(poligon_wgs84, custom_filter=filter_track(), simplify=True,
                              retain_all=True, truncate_by_edge=True)
    rez = (_u_graph(G), _u_graph(T))
    put.parent.mkdir(parents=True, exist_ok=True)
    with open(put, "wb") as f:
        pickle.dump(rez, f, protocol=pickle.HIGHEST_PROTOCOL)
    izvori.zabiljezi("osm", url="https://overpass-api.de/api/interpreter (OSMnx graph_from_polygon)")
    return rez


def dohvati_objekte(poligon_wgs84, oznake: dict, ime: str, osvjezi: bool = False) -> gpd.GeoDataFrame:
    """OSM objekti (točke/poligoni → reprezentativna točka) u EPSG:3765."""
    _postavi_osmnx()
    put = INTERIM_DIR / f"osm_{ime}.gpkg"
    if put.exists() and not osvjezi:
        return gpd.read_file(put)
    gdf = ox.features_from_polygon(poligon_wgs84, tags=oznake).reset_index()
    stupci = [c for c in ("element", "id", "name", "place", "tourism", "population") if c in gdf.columns]
    gdf = gdf[stupci + ["geometry"]].copy()
    gdf["geometry"] = gdf.geometry.representative_point()
    gdf = gdf.to_crs(CRS_ANALIZA)
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
