"""D7: kandidat za „drugu cestu“ — najkraći put iz područja iza uskog grla do
sigurne mreže kad se usko grlo ukloni, uz dopušteno korištenje putova `track`.

Graf = {vozive ceste bez bridova reza} ∪ {putovi track} (kombinirani OSM graf).
Bridove reza uklanjamo GEOMETRIJSKI (sredina brida unutar 2 m od geometrije reza),
jer kombinirani graf ima drugačije pojednostavljene bridove od glavnog grafa.

Rezultat je samo KANDIDAT: „prohodnost provjeriti na terenu“. Rang = ljudi iza / km.
"""
from __future__ import annotations

import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

from etl.config import CRS_ANALIZA
from etl.graph_egress import geometrija_brida

TOLERANCIJA_M = 2.0
PONOR = "__ponor__"


def bridovi_gdf(C: nx.Graph) -> gpd.GeoDataFrame:
    """Bridovi kombiniranog grafa sa sredinom (EPSG:3765) za prostorno traženje."""
    uv, geom = [], []
    for u, v in C.edges:
        uv.append((u, v))
        geom.append(geometrija_brida(C, u, v))
    gdf = gpd.GeoDataFrame({"uv": uv}, geometry=geom, crs="EPSG:4326").to_crs(CRS_ANALIZA)
    gdf["sredina"] = gdf.geometry.interpolate(0.5, normalized=True)
    return gdf


def druga_cesta(C: nx.Graph, C_bridovi: gpd.GeoDataFrame, sigurni_C: set, izvori_C: set,
                rez_geom_3765: MultiLineString) -> dict | None:
    """Najkraći put (po duljini) od izvora do sigurnih čvorova bez bridova reza."""
    if not izvori_C:
        return None
    sred = gpd.GeoSeries(C_bridovi["sredina"], crs=CRS_ANALIZA)
    idx = sred.sindex.query(rez_geom_3765.buffer(TOLERANCIJA_M), predicate="intersects")
    ukloni = [C_bridovi.uv.iloc[i] for i in idx]
    H = C.copy()
    H.remove_edges_from(ukloni)
    H.add_node(PONOR)
    H.add_edges_from(((s, PONOR) for s in sigurni_C if s in H), length=0.0)
    try:
        duljina, put = nx.multi_source_dijkstra(H, izvori_C & set(H.nodes), target=PONOR, weight="length")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
    put = put[:-1]
    if len(put) < 2:
        return None
    track_m = 0.0
    dijelovi = []
    for a, b in zip(put, put[1:]):
        d = H[a][b]
        if d.get("highway") == "track":
            track_m += d.get("length", 0) or 0
        g = geometrija_brida(H, a, b)
        # Orijentiraj dio prema smjeru puta (radi lijepe linije na karti).
        if (g.coords[0][0] - H.nodes[a]["x"]) ** 2 + (g.coords[0][1] - H.nodes[a]["y"]) ** 2 > \
                (g.coords[-1][0] - H.nodes[a]["x"]) ** 2 + (g.coords[-1][1] - H.nodes[a]["y"]) ** 2:
            g = LineString(list(g.coords)[::-1])
        dijelovi.append(g)
    linija = linemerge(dijelovi)
    return {"duljina_km": round(duljina / 1000, 2), "udio_track": round(track_m / duljina, 3) if duljina else 0.0,
            "geometrija": linija}
