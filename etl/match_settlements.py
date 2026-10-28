"""Spajanje naselja: DZS (stanovništvo) ↔ DGU (matični broj, poligon) ↔ točka naselja.

Pravila iz CLAUDE.md §3.3:
- DZS nema matični broj naselja, pa spajamo par (JLS, naselje) uz normalizaciju
  (mala slova, bez „Grad“/„Općina“ i zagrada, „Sv.“ → „sveti“, crtice → razmak;
  dijakritike uklanjamo SAMO za usporedbu).
- Neizrazito spajanje rapidfuzz token_sort_ratio ≥ 88, samo unutar iste JLS.
- Ostatak ide u data/manual/ispravci_naselja.csv; nespojena DZS naselja se
  zapisuju u data/interim/dzs_bez_tocke.csv (mora biti prazna ili objašnjena).

Točka naselja: službena točka imena iz DGU RGI (tip „naselje“) unutar poligona
naselja; ako je nema, OSM place=* istog imena; inače reprezentativna točka poligona.
"""
from __future__ import annotations

import csv
import re
import unicodedata

import geopandas as gpd
import pandas as pd
from rapidfuzz import fuzz

from etl.config import INTERIM_DIR, MANUAL_DIR, RADIJUS_PLACE_M, RADIJUS_ZADANO_M

PRAG_FUZZY = 88  # izvor: CLAUDE.md §3.3


def norm(tekst: str) -> str:
    t = (tekst or "").lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"\b(grad|općina|opcina)\b", " ", t)
    t = re.sub(r"\bsv\.\s*", "sveti ", t)
    t = t.replace("-", " ").replace("–", " ")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).strip()


def _rucni_ispravci() -> dict:
    """(jls, naselje_dzs) → matični broj DGU iz ručnog CSV-a (prvi redak je izvor)."""
    put = MANUAL_DIR / "ispravci_naselja.csv"
    if not put.exists():
        return {}
    with open(put, encoding="utf-8", newline="") as f:
        redovi = list(csv.reader(f))
    rez = {}
    for r in redovi[2:]:  # 1. redak: izvor, 2. redak: zaglavlje
        if len(r) >= 3 and r[2].strip():
            rez[(norm(r[0]), norm(r[1]))] = r[2].strip()
    return rez


def spoji_dzs_dgu(dzs: pd.DataFrame, dgu: gpd.GeoDataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Vrati (spojeno, nespojeno). spojeno ima stupce DZS-a + sifra (matični broj), nacin_spajanja."""
    dgu = dgu.copy()
    dgu["k_jls"] = dgu.jls.map(norm)
    dgu["k_nas"] = dgu.naziv.map(norm)
    rucni = _rucni_ispravci()
    rez, nespojeno = [], []
    for r in dzs.itertuples(index=False):
        kj, kn = norm(r.jls), norm(r.naselje)
        kand = dgu[dgu.k_jls == kj]
        if (kj, kn) in rucni:
            pogodak, nacin = rucni[(kj, kn)], "rucno"
        else:
            tocno = kand[kand.k_nas == kn]
            if len(tocno) == 1:
                pogodak, nacin = tocno.iloc[0].sifra, "tocno"
            else:
                ocjene = [(fuzz.token_sort_ratio(kn, x), s) for x, s in zip(kand.k_nas, kand.sifra)]
                ocjene.sort(reverse=True)
                if ocjene and ocjene[0][0] >= PRAG_FUZZY and (len(ocjene) == 1 or ocjene[1][0] < ocjene[0][0]):
                    pogodak, nacin = ocjene[0][1], f"fuzzy {ocjene[0][0]:.0f}"
                else:
                    pogodak, nacin = None, None
        if pogodak is None:
            nespojeno.append(r._asdict())
        else:
            rez.append({**r._asdict(), "sifra": str(pogodak), "nacin_spajanja": nacin})
    return pd.DataFrame(rez), pd.DataFrame(nespojeno)


def _radijus(place: str | None, stanovnici: float) -> int:
    if place in RADIJUS_PLACE_M:
        return RADIJUS_PLACE_M[place]
    # PRETPOSTAVKA: bez OSM tipa mjesta procjenjujemo tip po broju stanovnika.
    if stanovnici >= 10000:
        return RADIJUS_PLACE_M["city"]
    if stanovnici >= 1500:
        return RADIJUS_PLACE_M["town"]
    if stanovnici >= 100:
        return RADIJUS_PLACE_M["village"]
    return RADIJUS_PLACE_M.get("hamlet", RADIJUS_ZADANO_M)


def tocke_naselja(spojeno: pd.DataFrame, dgu: gpd.GeoDataFrame, rgi: gpd.GeoDataFrame,
                  osm_mjesta: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Za svako spojeno naselje: točka, poligon, radijus jezgre i izvor točke."""
    poligoni = dgu.set_index("sifra").geometry
    rgi = rgi.assign(k=rgi.geografskoime.map(norm))
    osm = osm_mjesta.assign(k=osm_mjesta["name"].fillna("").map(norm)) if len(osm_mjesta) else osm_mjesta
    redovi = []
    for r in spojeno.itertuples(index=False):
        pol = poligoni.get(r.sifra)
        k = norm(r.naselje)
        tocka, izvor, place = None, None, None
        if pol is not None:
            kand = rgi[(rgi.k == k) & rgi.geometry.within(pol)]
            if len(kand):
                # Prednost tipu „naselje“ ispred „dio naselja“ / „zaselak“.
                kand = kand.assign(p=(kand.vrstaobiljezja != "naselje").astype(int)).sort_values("p")
                tocka, izvor = kand.geometry.iloc[0], "dgu_rgi"
            if len(osm):
                ko = osm[(osm.k == k) & osm.geometry.within(pol)]
                if len(ko):
                    place = ko.iloc[0]["place"]
                    if tocka is None:
                        tocka, izvor = ko.geometry.iloc[0], "osm_place"
            if tocka is None:
                tocka, izvor = pol.representative_point(), "dgu_poligon"
        redovi.append({**r._asdict(), "tocka": tocka, "poligon": pol, "tocka_izvor": izvor, "osm_place": place,
                       "radijus_m": _radijus(place, r.stanovnici_2021)})
    gdf = gpd.GeoDataFrame(redovi, geometry="tocka", crs=dgu.crs)
    return gdf


def spoji(dzs: pd.DataFrame, dgu_naselja: gpd.GeoDataFrame, rgi: gpd.GeoDataFrame,
          osm_mjesta: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    spojeno, nespojeno = spoji_dzs_dgu(dzs, dgu_naselja)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    nespojeno.to_csv(INTERIM_DIR / "dzs_bez_tocke.csv", index=False, encoding="utf-8")
    udio = len(spojeno) / max(1, len(dzs))
    print(f"[spajanje] DZS→DGU: {len(spojeno)}/{len(dzs)} ({udio:.1%}); nespojeno: {len(nespojeno)}")
    gdf = tocke_naselja(spojeno, dgu_naselja, rgi, osm_mjesta)
    gdf = gdf.rename(columns={"sifra": "id", "naselje": "naziv"})
    gdf["id"] = gdf["id"].astype(str)
    return gdf
