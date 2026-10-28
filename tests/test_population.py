import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box

from etl import population


def _naselja():
    return gpd.GeoDataFrame({
        "id": ["001", "002", "003"], "jls": ["Tisno", "Tisno", "Unešić"],
        "stanovnici_2021": [1000.0, 100.0, 50.0],
        "poligon": [box(0, 0, 10, 10), box(10, 0, 20, 10), box(100, 100, 110, 110)],
    }, geometry=[Point(5, 5), Point(15, 5), Point(105, 105)], crs="EPSG:3765")


def test_udio_po_turistickim_objektima_i_po_stanovnicima():
    tur = gpd.GeoDataFrame(geometry=[Point(1, 1)] * 6 + [Point(11, 1)] * 2 + [Point(101, 101)], crs="EPSG:3765")
    u = population.udjeli_naselja(_naselja(), tur).set_index("id")
    assert u.loc["001", "udio"] == 0.75 and u.loc["002", "udio"] == 0.25
    assert u.loc["001", "udio_metoda"] == "osm_turisticki_objekti"
    # Unešić ima < 5 objekata → udio stanovnika (jedino naselje → 1)
    assert u.loc["003", "udio"] == 1.0 and u.loc["003", "udio_metoda"] == "udio_stanovnika"


def test_ljetna_populacija_scenariji_rastu():
    n = _naselja()
    udjeli = pd.DataFrame({"id": ["001", "002", "003"], "udio": [0.75, 0.25, 1.0], "udio_metoda": ["x"] * 3})
    tur = pd.DataFrame({"jls": ["Tisno", "Unešić"], "postelje_stalne": [1000.0, 0.0]})
    sta = pd.DataFrame({"jls": ["Tisno", "Unešić"], "stanovi_odmor": [100.0, 0.0]})
    p = population.ljetna_populacija(n, udjeli, tur, sta).set_index("id")
    # opt: 1000 + 1000·0,70·0,75 + 100·2·0,75 = 1675
    assert p.loc["001", "p_ljeto_opt"] == 1675
    assert p.loc["001", "p_ljeto_opt"] < p.loc["001", "p_ljeto_sred"] < p.loc["001", "p_ljeto_pes"]
    assert p.loc["003", "p_ljeto_pes"] == 50
