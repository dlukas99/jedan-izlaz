"""Validacija na stvarnim slučajevima iz izvezenih podataka (preskače se ako ih nema ili su mock).

Murter mora biti E1 (jedini cestovni izlaz preko Tisna, pokretni most), a Zlarin,
Prvić Luka, Prvić Šepurine i Krapanj E0 (otoci bez cestovne veze).
"""
import json

import pytest

from etl.config import WEB_DATA_DIR

PUT = WEB_DATA_DIR / "settlements.geojson"


@pytest.fixture(scope="module")
def naselja():
    if not PUT.exists():
        pytest.skip("nema web/public/data/settlements.geojson")
    meta = json.loads((WEB_DATA_DIR / "meta.json").read_text(encoding="utf-8"))
    if meta.get("nacin") == "mock":
        pytest.skip("mock podaci")
    d = json.loads(PUT.read_text(encoding="utf-8"))
    return {(f["properties"]["jls"], f["properties"]["naziv"]): f["properties"] for f in d["features"]}


def test_murter_e1_iza_pokretnog_mosta(naselja):
    m = naselja[("Murter-Kornati", "Murter")]
    assert m["klasa_izlaza"] == "E1"
    assert m["pokretni_most"] is True
    assert m["usko_grlo_id"] is not None


@pytest.mark.parametrize("jls,naziv", [("Šibenik", "Zlarin"), ("Vodice", "Prvić Luka"),
                                       ("Vodice", "Prvić Šepurine"), ("Šibenik", "Krapanj")])
def test_otoci_bez_ceste_e0(naselja, jls, naziv):
    n = naselja[(jls, naziv)]
    assert n["klasa_izlaza"] == "E0"
    assert n["t_evak_h"] is None
    assert n["trajektna_linija"]


def test_sva_naselja_spojena(naselja):
    assert len(naselja) == 199  # DZS Popis 2021.: 199 naselja u ŠKŽ


def test_rasponi_uredeni(naselja):
    for n in naselja.values():
        p = n["p_ljeto"]
        assert p["opt"] <= p["sred"] <= p["pes"]
        if n["t_evak_h"]:
            t = n["t_evak_h"]
            assert t["opt"] <= t["sred"] <= t["pes"]
