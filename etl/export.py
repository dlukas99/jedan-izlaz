"""Izvoz za web: settlements.geojson, bottlenecks.geojson, second_roads.geojson,
burned.geojson, meta.json, kpi.json i generirani docs/izvori.md.

Shema je opisana u CLAUDE.md §5.2 (v1); dodatna polja su zapisana u dnevniku (§9).
Koordinate su EPSG:4326 na 5 decimala (D1, RFC 7946).
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

from shapely.geometry import mapping

from etl import config, izvori
from etl.config import DOCS_DIR, KOORD_DECIMALE, ODRICANJE, WEB_DATA_DIR

REDOSLIJED_PRIORITETA = {"A": 0, "B": 1, "C": 2, "-": 3}


def _zaokruzi(o):
    """Rekurzivno zaokruži koordinate na KOORD_DECIMALE."""
    if isinstance(o, (list, tuple)):
        return [_zaokruzi(x) for x in o]
    if isinstance(o, float):
        return round(o, KOORD_DECIMALE)
    return o


def _cisto(v):
    """NaN/numpy → JSON-prijateljske vrijednosti."""
    if isinstance(v, dict):
        return {k: _cisto(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_cisto(x) for x in v]
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def feature(geom, props: dict) -> dict:
    g = mapping(geom)
    return {"type": "Feature", "geometry": {"type": g["type"], "coordinates": _zaokruzi(g["coordinates"])},
            "properties": _cisto(props)}


def zapisi_geojson(ime: str, znacajke: list[dict], dir_: Path = WEB_DATA_DIR):
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / ime).write_text(json.dumps({"type": "FeatureCollection", "features": znacajke},
                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def scenariji() -> dict:
    """Sve konstante koje ulaze u izračun (za meta.json i stranicu „Izvori i metoda“)."""
    return {
        "popunjenost_stalnih_postelja": config.POPUNJENOST,
        "osoba_po_stanu_za_odmor": config.OSOBA_PO_STANU_ODMOR,
        "osoba_po_vozilu": config.OSOBA_PO_VOZILU,
        "kapacitet_trake_voz_h": config.KAPACITET_TRAKE_VOZ_H,
        "faktor_klase_ceste": config.FAKTOR_KLASE_CESTE,
        "maks_izlaza": config.MAKS_IZLAZA,
        "pufer_km": config.PUFER_KM,
        "h_tezine": {"gorivo": config.H_TEZINA_GORIVO, "pozari": config.H_TEZINA_POZARI},
        "h_radijusi_m": {"gorivo": config.RADIJUS_GORIVO_M, "pozari": config.RADIJUS_POZARI_M},
        "f_klase": config.F_KLASE,
        "t_pragovi_h": {"A": config.T_PRAG_A_H, "B": config.T_PRAG_B_H, "norma": config.T_NORMA_H},
        "fwi_razredi": config.FWI_RAZREDI,
        "povijesni_dan": config.POVIJESNI_DAN,
    }


def meta(nacin: str, dodatno: dict | None = None) -> dict:
    return {
        "generirano": dt.datetime.now().isoformat(timespec="seconds"),
        "nacin": nacin,
        "scenariji": scenariji(),
        "izvori": izvori.svi(),
        "odricanje": ODRICANJE,
        **(dodatno or {}),
    }


def kpi(naselja_props: list[dict], datum: str) -> dict:
    po_klasi: dict[str, int] = {}
    ljudi = {"E0": {"opt": 0, "sred": 0, "pes": 0}, "E1": {"opt": 0, "sred": 0, "pes": 0}}
    for p in naselja_props:
        po_klasi[p["klasa_izlaza"]] = po_klasi.get(p["klasa_izlaza"], 0) + 1
        if p["klasa_izlaza"] in ljudi:
            for s in ("opt", "sred", "pes"):
                ljudi[p["klasa_izlaza"]][s] += int(p["p_ljeto"][s] or 0)
    po_prioritetu: dict[str, int] = {}
    for p in naselja_props:
        po_prioritetu[p["prioritet"]] = po_prioritetu.get(p["prioritet"], 0) + 1
    top = sorted(naselja_props, key=lambda p: (REDOSLIJED_PRIORITETA[p["prioritet"]], -(p["iz"] or 0)))[:10]
    return {
        "datum": datum,
        "broj_naselja": len(naselja_props),
        "naselja_po_klasi": dict(sorted(po_klasi.items())),
        "naselja_po_prioritetu": dict(sorted(po_prioritetu.items())),
        "ljudi_ljeti_u_naseljima_E0": ljudi["E0"],
        "ljudi_ljeti_u_naseljima_E1": ljudi["E1"],
        "top10": [{"id": p["id"], "naziv": p["naziv"], "jls": p["jls"], "prioritet": p["prioritet"],
                   "klasa_izlaza": p["klasa_izlaza"], "iz": p["iz"]} for p in top],
    }


def izvori_md(m: dict, put: Path = DOCS_DIR / "izvori.md"):
    """docs/izvori.md generiran iz meta.json — popis svih skupova za predaju."""
    L = ["# Izvori podataka", "",
         f"Generirano iz `web/public/data/meta.json` ({m['generirano']}, način: `{m['nacin']}`). Ne uređivati ručno.", "",
         "| # | Skup podataka | Izdavač | Poveznica | Licenca | Dohvaćeno | Izmijenjeno (metapodaci) |",
         "|---|---|---|---|---|---|---|"]
    for i, z in enumerate(m["izvori"], 1):
        url = z.get("url_paketa") or z.get("url") or ""
        poveznica = f"[poveznica]({url})" if url else "–"
        L.append(f"| {i} | {z['naziv']} | {z['izdavac']} | {poveznica} | {z['licenca']} | "
                 f"{(z.get('dohvaceno') or '–')[:10]} | {(z.get('metadata_modified') or '–')[:10]} |")
    L += ["", "## Obavezni navodi", ""]
    for z in m["izvori"]:
        L.append(f"- {z['navod']}")
    L += ["", "Izvedeni podaci s geometrijom iz OpenStreetMapa licencirani su pod ODbL 1.0.",
          "Podaci s portala data.gov.hr dohvaćaju se preko CKAN API-ja (`package_show`).", "",
          f"> {ODRICANJE}", ""]
    put.parent.mkdir(parents=True, exist_ok=True)
    put.write_text("\n".join(L), encoding="utf-8")
