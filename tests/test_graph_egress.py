"""Sintetički testovi za D4 (bez mreže): most → E1, dva mosta → E2-5, trajekt → E0,
slijepa ulica ne mijenja status, rez najbliži sigurnoj mreži."""
import networkx as nx
import pytest

from etl import graph_egress as ge


def _graf(bridovi):
    G = nx.Graph()
    for u, v in bridovi:
        G.add_edge(u, v, paralelno=1)
    return G


def _kopno(G, prefiks="k", n=8):
    """Gusta „kopnena“ mreža (rešetka) čiji su rubni čvorovi sigurni."""
    for i in range(n):
        for j in range(n):
            if i + 1 < n:
                G.add_edge(f"{prefiks}{i},{j}", f"{prefiks}{i+1},{j}", paralelno=1)
            if j + 1 < n:
                G.add_edge(f"{prefiks}{i},{j}", f"{prefiks}{i},{j+1}", paralelno=1)
    return {f"{prefiks}{i},{j}" for i in range(n) for j in range(n) if i in (0, n - 1) or j in (0, n - 1)}


def _otok(G, prefiks, spoj_na=None):
    """Otok s petljom (2-bridno-povezan) i slijepom ulicom."""
    G.add_edges_from([(f"{prefiks}a", f"{prefiks}b"), (f"{prefiks}b", f"{prefiks}c"),
                      (f"{prefiks}c", f"{prefiks}a"), (f"{prefiks}c", f"{prefiks}slijepa")], paralelno=1)
    return {f"{prefiks}a", f"{prefiks}b", f"{prefiks}c"}


def test_jedan_most_daje_e1_i_rez_je_most():
    G = nx.Graph()
    sigurni = _kopno(G)
    jz = _otok(G, "o")
    G.add_edge("oa", "k3,3", paralelno=1, pokretni_most=True)  # most
    e, tok = ge.max_tok(G, jz, sigurni)
    assert e == 1 and ge.klasa(e) == "E1"
    rez, iza = ge.rez_najblizi_ponoru(G, jz, sigurni, tok)
    assert rez == [tuple(sorted(("oa", "k3,3"), key=str))]
    assert "oslijepa" in iza and "k3,3" not in iza
    assert ge.klase_v1(G, {"o": jz}, sigurni)["o"] == "E1"
    assert {"oa", "ob", "oc", "oslijepa"} <= ge.pokretni_mostovi_iza(G, sigurni)


def test_dva_mosta_daju_e2():
    G = nx.Graph()
    sigurni = _kopno(G)
    jz = _otok(G, "o")
    G.add_edge("oa", "k3,3", paralelno=1)
    G.add_edge("ob", "k5,5", paralelno=1)
    e, _ = ge.max_tok(G, jz, sigurni)
    assert e == 2 and ge.klasa(e) == "E2-5"
    assert ge.klase_v1(G, {"o": jz}, sigurni)["o"] == "E2+"


def test_paralelni_brid_nije_most():
    G = nx.Graph()
    sigurni = _kopno(G)
    jz = _otok(G, "o")
    G.add_edge("oa", "k3,3", paralelno=2)  # dvije odvojene kolničke trake
    e, _ = ge.max_tok(G, jz, sigurni)
    assert e == 2


def test_otok_bez_ceste_je_e0():
    G = nx.Graph()
    sigurni = _kopno(G)
    jz = _otok(G, "z")  # trajekt nije brid grafa → nema veze s kopnom
    e, tok = ge.max_tok(G, jz, sigurni)
    assert e == 0 and ge.klasa(e) == "E0"
    rez, iza = ge.rez_najblizi_ponoru(G, jz, sigurni, tok)
    assert rez == [] and iza == {"za", "zb", "zc", "zslijepa"}
    assert ge.klase_v1(G, {"z": jz}, sigurni)["z"] == "E0"


def test_slijepa_ulica_ne_mijenja_status():
    """Jezgra se bira iz 2-bridno-povezane komponente; slijepa ulica ne smije postati „naselje“."""
    G = nx.Graph()
    sigurni = _kopno(G)
    _otok(G, "o")
    G.add_edge("oa", "k3,3", paralelno=1)
    G.add_edge("k4,4", "k4,4kuca", paralelno=1)  # prilaz kući na kopnu
    komp = ge.komponente_bez_mostova(G)
    jz = ge.jezgra(["k3,4", "k4,4", "k4,4kuca"], [10.0, 5.0, 1.0], komp)
    assert jz == {"k3,4", "k4,4"}
    e, _ = ge.max_tok(G, jz, sigurni)
    assert e >= 2


def test_rez_najblizi_ponoru_obuhvaca_cijeli_otok():
    """Lanac: selo — cesta (most grafa) — otok — most — kopno. Usko grlo je most prema kopnu."""
    G = nx.Graph()
    sigurni = _kopno(G)
    _otok(G, "o")
    G.add_edge("oa", "k3,3", paralelno=1)
    G.add_edge("oc", "selo1", paralelno=1)
    G.add_edge("selo1", "selo2", paralelno=1)
    G.add_edge("selo2", "selo3", paralelno=1)
    G.add_edge("selo3", "selo1", paralelno=1)
    jz = {"selo1", "selo2", "selo3"}
    e, tok = ge.max_tok(G, jz, sigurni)
    assert e == 1
    rez, iza = ge.rez_najblizi_ponoru(G, jz, sigurni, tok)
    assert rez == [tuple(sorted(("oa", "k3,3"), key=str))]
    assert {"oa", "ob", "oc", "selo1"} <= iza


def test_e6_kad_je_jezgra_u_gustoj_mrezi():
    G = nx.Graph()
    sigurni = _kopno(G, n=12)
    jz = {"k5,5", "k5,6", "k6,5", "k6,6"}
    e, _ = ge.max_tok(G, jz, sigurni)
    assert e == 6 and ge.klasa(e) == "E6+"


@pytest.mark.parametrize("seed", range(5))
def test_max_tok_jednak_networkx(seed):
    """Vlastiti Edmonds–Karp mora dati isto što i networkx (uz super-izvor i super-ponor)."""
    G = nx.gnm_random_graph(60, 110, seed=seed)
    for u, v in G.edges:
        G[u][v]["paralelno"] = 1 + (u + v) % 2
    izvori, ponori = {0, 1, 2}, {57, 58, 59}
    e, _ = ge.max_tok(G, izvori, ponori, cutoff=10**6)
    D = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        D.add_edge(u, v, capacity=d["paralelno"])
        D.add_edge(v, u, capacity=d["paralelno"])
    for s in izvori:
        D.add_edge("S", s)
    for t in ponori:
        D.add_edge(t, "T")
    assert e == nx.maximum_flow_value(D, "S", "T")
