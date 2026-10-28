"""D5: ljetna populacija naselja u tri scenarija (opt / sred / pes).

P = stanovnici_2021
  + postelje_JLS × popunjenost × udio_naselja
  + stanovi_za_odmor_JLS × osoba_po_stanu × udio_naselja

- postelje_JLS: STALNE postelje 2025. (DZS, Turizam u 2025., tab. 2.11). Pomoćne
  postelje ne brojimo, jer se DZS-ova popunjenost odnosi na stalne postelje.
- udio_naselja: udio OSM turističkih objekata JLS-a koji leže u poligonu naselja;
  ako JLS ima manje od 5 objekata, udio stanovnika. Metoda se zapisuje u udio_metoda.
- „Pesimistično“ znači VIŠE ljudi (teži slučaj za evakuaciju).
"""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

from etl.config import MIN_TURIST_OBJEKATA_JLS, OSOBA_PO_STANU_ODMOR, POPUNJENOST, SCENARIJI
from etl.match_settlements import norm


def udjeli_naselja(naselja: gpd.GeoDataFrame, turizam: gpd.GeoDataFrame) -> pd.DataFrame:
    """Udio JLS-ovog turizma koji pripada svakom naselju (+ metoda)."""
    pol = gpd.GeoDataFrame(naselja[["id", "jls"]], geometry=naselja["poligon"], crs=naselja.crs)
    if len(turizam):
        spoj = gpd.sjoin(turizam[["geometry"]], pol, predicate="within", how="inner")
        broj = spoj.groupby("id").size()
    else:
        broj = pd.Series(dtype=float)
    df = naselja[["id", "jls", "stanovnici_2021"]].copy()
    df["turist_objekata"] = df.id.map(broj).fillna(0)
    rez = []
    for jls, g in df.groupby("jls"):
        ukupno = g.turist_objekata.sum()
        if ukupno >= MIN_TURIST_OBJEKATA_JLS:
            u = g.turist_objekata / ukupno
            metoda = "osm_turisticki_objekti"
        else:
            st = g.stanovnici_2021.sum()
            u = g.stanovnici_2021 / st if st > 0 else 1.0 / len(g)
            metoda = "udio_stanovnika"
        rez.append(pd.DataFrame({"id": g.id, "udio": u, "udio_metoda": metoda,
                                 "turist_objekata": g.turist_objekata}))
    return pd.concat(rez, ignore_index=True)


def ljetna_populacija(naselja: pd.DataFrame, udjeli: pd.DataFrame, turizam_jls: pd.DataFrame,
                      stanovi_jls: pd.DataFrame) -> pd.DataFrame:
    """Vrati id, postelje_jls, stanovi_odmor_jls, udio, udio_metoda i p_ljeto_{opt,sred,pes}."""
    tur = turizam_jls.assign(k=turizam_jls.jls.map(norm)).set_index("k")
    sta = stanovi_jls.assign(k=stanovi_jls.jls.map(norm)).set_index("k")
    df = naselja[["id", "jls", "stanovnici_2021"]].merge(udjeli[["id", "udio", "udio_metoda"]], on="id")
    k = df.jls.map(norm)
    df["postelje_jls"] = k.map(tur["postelje_stalne"]).fillna(0)
    df["stanovi_odmor_jls"] = k.map(sta["stanovi_odmor"]).fillna(0)
    for s in SCENARIJI:
        df[f"p_ljeto_{s}"] = (df.stanovnici_2021
                              + df.postelje_jls * POPUNJENOST[s] * df.udio
                              + df.stanovi_odmor_jls * OSOBA_PO_STANU_ODMOR[s] * df.udio).round()
    return df
