"""Izmišljeni podaci po shemi 5.2 — da web može raditi bez pipelinea.

meta.json ima "nacin": "mock", a UI tada prikazuje crvenu traku „MOCK“.
Mock se NIKAD ne smije pojaviti u videu ni u predaji.
"""
from __future__ import annotations

import json

from shapely.geometry import LineString, Point

from etl import export
from etl.config import WEB_DATA_DIR

NASELJA = [  # (id, naziv, jls, lon, lat, klasa, e)
    ("m001", "Mockovo", "Mock-Kornati", 15.59, 43.82, "E1", 1),
    ("m002", "Otočić", "Mockšibenik", 15.86, 43.69, "E0", 0),
    ("m003", "Dvoput", "Mockšibenik", 15.95, 43.70, "E2-5", 2),
    ("m004", "Gradić", "Mockšibenik", 15.90, 43.73, "E6+", 6),
]


def zapisi():
    feats = []
    for i, (nid, naziv, jls, lon, lat, kl, e) in enumerate(NASELJA):
        t = {"opt": 0.5 + i, "sred": 1.0 + i, "pes": 2.0 + i} if kl in ("E1", "E2-5") else None
        feats.append(export.feature(Point(lon, lat), {
            "id": nid, "naziv": naziv, "jls": jls, "zupanija": "MOCK", "stanovnici_2021": 1000 * (i + 1),
            "stanovnici_65plus": 200, "postelje_jls": 5000, "stanovi_odmor_jls": 500,
            "p_ljeto": {"opt": 3000, "sred": 3500, "pes": 4000}, "udio_naselja": 0.5, "udio_metoda": "mock",
            "izlazi_e": e, "klasa_izlaza": kl, "usko_grlo_id": "UG-MOCK-001" if kl == "E1" else None,
            "ljudi_iza_reza": {"opt": 3000, "sred": 3500, "pes": 4000} if kl != "E6+" else None,
            "t_evak_h": t, "pokretni_most": kl == "E1", "trajektna_linija": "Mock linija 000" if kl == "E0" else None,
            "h_stat": 0.2 * (i + 1), "h_gorivo": 0.5, "h_pozari_udio": 0.1, "h_razred": ["visok", "srednji", "nizak", "visok"][i],
            "prioritet": ["A", "B", "C", "-"][i], "iz": 80 - 20 * i, "druga_cesta_km": 4.2 if kl == "E1" else None,
            "druga_cesta_udio_track": 0.6 if kl == "E1" else None, "tocka_izvor": "mock",
            "napomene": ["MOCK podaci — nisu stvarni."], "izvori": ["osm"],
        }))
    export.zapisi_geojson("settlements.geojson", feats)
    export.zapisi_geojson("bottlenecks.geojson", [export.feature(LineString([(15.63, 43.80), (15.65, 43.80)]), {
        "id": "UG-MOCK-001", "cesta_ref": "D000", "naziv": "Mock most", "pokretni_most": True, "most": True,
        "broj_izlaza": 1, "kapacitet_voz_h": {"opt": 1300, "sred": 1000, "pes": 600},
        "ljudi_iza": {"opt": 3000, "sred": 3500, "pes": 4000}, "t_evak_h": {"opt": 0.5, "sred": 1.0, "pes": 2.0},
        "naselja_iza": ["m001"], "naselja_iza_nazivi": ["Mockovo"], "pldp": None, "druga_cesta_km": 4.2})])
    export.zapisi_geojson("second_roads.geojson", [])
    m = export.meta("mock")
    (WEB_DATA_DIR / "meta.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    k = export.kpi([f["properties"] for f in feats], "mock")
    (WEB_DATA_DIR / "kpi.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Mock podaci zapisani u", WEB_DATA_DIR)
