from etl import evac_time


def test_kapacitet_i_vrijeme():
    kap = evac_time.kapacitet_reza([{"highway": "primary", "paralelno": 1}])
    assert kap == {"opt": 1300, "sred": 1000, "pes": 600}
    t = evac_time.vrijeme_h({"opt": 5000, "sred": 6000, "pes": 7000}, kap)
    # sred: 6000 / 2,5 = 2400 vozila / 1000 voz/h = 2,4 h
    assert t["sred"] == 2.4
    assert t["opt"] < t["sred"] < t["pes"]
    assert evac_time.tekst_raspona(t) == "1,3–5,8 h (središnje 2,4 h)"


def test_faktor_klase_i_razumnost():
    assert evac_time.faktor_klase("residential") == 0.6
    assert evac_time.faktor_klase("primary_link") == 1.0
    assert evac_time.kapacitet_reza([{"highway": "residential", "paralelno": 2}])["sred"] == 1200
    assert not evac_time.razumno({"sred": 0.01})
    assert evac_time.razumno({"sred": 2.0})
