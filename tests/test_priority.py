from etl import priority


def test_razredi():
    assert priority.razred("E0", "visok", None) == "A"
    assert priority.razred("E1", "visok", 1.5) == "A"
    assert priority.razred("E1", "visok", 0.5) == "C"
    assert priority.razred("E1", "srednji", 0.2) == "B"
    assert priority.razred("E1", "nizak", 3.5) == "B"
    assert priority.razred("E2-5", "visok", 4.0) == "B"
    assert priority.razred("E2-5", "visok", 1.0) == "C"
    assert priority.razred("E6+", "visok", 10) == "-"


def test_indeks_i_tercili():
    assert priority.indeks("E0", 0.5, None) == 50.0
    assert priority.indeks("E1", 1.0, 1.5) == 45.0
    assert priority.indeks("E6+", 1.0, 5) == 0.0
    gr = priority.tercili([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    assert priority.h_razred(0.1, gr) == "nizak"
    assert priority.h_razred(0.6, gr) == "visok"
