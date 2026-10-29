"""D3–D4: sigurna mreža, jezgra naselja i broj izlaznih pravaca (minimalni rez).

Kako radi (detaljnije u docs/metodologija.md):

1. Sigurni čvorovi (D3): čvorovi izvan poligona županije i čvorovi na autocesti.
2. Jezgra naselja: cestovni čvorovi u krugu oko službene točke naselja (RGI),
   unutar poligona naselja (DGU). Od njih uzimamo samo one u 2-bridno-povezanoj
   komponenti s najviše čvorova — tako slijepe ulice i prilazi kućama ne
   mijenjaju status naselja.
3. v1 (mostovi grafa): grafu dodamo super-ponor spojen sa svim sigurnim čvorovima.
   Ako jezgra nije povezana s ponorom → E0; ako ih dijeli most grafa → E1; inače E2+.
4. v2 (maksimalni tok = broj bridno-disjunktnih putova, Mengerov teorem):
   super-izvor → jezgra, sigurni čvorovi → super-ponor, kapacitet brida =
   broj paralelnih bridova. Tok računamo do 6 (prag iz Fong i sur., PNAS 2026).
   Ako je tok < 6, minimalni rez je USKO GRLO. Biramo rez najbliži ponoru
   (sigurnoj mreži), jer on obuhvaća najviše ljudi „iza“ — npr. cijeli otok
   Murter iza mosta u Tisnu, a ne samo jednu ulicu u Murteru.

Tok računamo vlastitom BFS implementacijom Edmonds–Karpa s više izvora i ponora
(bez umjetnih čvorova). Test test_graph_egress.py je uspoređuje s
networkx.maximum_flow_value.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import geopandas as gpd
import networkx as nx
import numpy as np
from shapely.geometry import LineString, MultiLineString

from etl.config import MAKS_IZLAZA, MAKS_UDALJENOST_CESTE_M, SIGURNO_PUFER_M


# --------------------------------------------------------------- D3 -------
def sigurni_cvorovi(G: nx.Graph, cvorovi: gpd.GeoDataFrame, poligon_zupanije,
                    pufer_m: float = SIGURNO_PUFER_M) -> set:
    """Čvorovi izvan županije (+ pufer, zbog riva izvan kopnenog poligona) i čvorovi na autocesti."""
    unutra = cvorovi.geometry.within(poligon_zupanije.buffer(pufer_m)).values
    sigurni = set(cvorovi.cvor.values[~unutra])
    for u, v, d in G.edges(data=True):
        if d.get("highway") == "motorway":
            sigurni.add(u)
            sigurni.add(v)
    return sigurni


# --------------------------------------------------------------- jezgra ---
def komponente_bez_mostova(G: nx.Graph) -> dict:
    """Oznaka 2-bridno-povezane komponente za svaki čvor (G bez mostova grafa)."""
    H = G.copy()
    H.remove_edges_from(nx.bridges(G))
    oznaka = {}
    for i, komp in enumerate(nx.connected_components(H)):
        for n in komp:
            oznaka[n] = i
    return oznaka


def jezgra(kandidati: list, udaljenosti: list[float], komp: dict) -> set:
    """Iz kandidata zadrži one u 2-bridno-povezanoj komponenti s najviše kandidata.

    Kad nijedna komponenta nema više od jednog kandidata (selo „na grani“),
    uzimamo čvor najbliži točki naselja.
    """
    if not kandidati:
        return set()
    broj: dict[int, int] = {}
    for n in kandidati:
        broj[komp[n]] = broj.get(komp[n], 0) + 1
    najvise = max(broj.values())
    if najvise == 1:
        return {kandidati[int(np.argmin(udaljenosti))]}
    # Kod izjednačenja: komponenta koja sadrži najbliži kandidat.
    poredak = sorted(zip(udaljenosti, kandidati))
    pobjednik = next(komp[n] for _, n in poredak if broj[komp[n]] == najvise)
    return {n for n in kandidati if komp[n] == pobjednik}


def jezgre_naselja(naselja: gpd.GeoDataFrame, cvorovi: gpd.GeoDataFrame, komp: dict) -> dict:
    """Za svako naselje skup čvorova jezgre.

    naselja: EPSG:3765, stupci id, tocka (Point), poligon (Polygon ili None), radijus_m.
    """
    sindex = cvorovi.sindex
    xy = np.column_stack([cvorovi.geometry.x.values, cvorovi.geometry.y.values])
    ids = cvorovi.cvor.values
    rez = {}
    for r in naselja.itertuples():
        t = r.tocka
        idx = sindex.query(t.buffer(r.radijus_m), predicate="intersects")
        if r.poligon is not None and len(idx):
            unutra = cvorovi.geometry.iloc[idx].within(r.poligon).values
            idx = idx[unutra]
        if len(idx) == 0:
            # Nema čvora u krugu: najbliži čvor do 1 km (CLAUDE.md §3.3), inače naselje nema cestu.
            j, d = sindex.nearest(t, return_distance=True, max_distance=MAKS_UDALJENOST_CESTE_M)
            idx = j[1] if len(j[1]) else np.array([], dtype=int)
        kandidati = list(ids[idx])
        udaljenosti = list(np.hypot(xy[idx, 0] - t.x, xy[idx, 1] - t.y)) if len(idx) else []
        rez[r.id] = jezgra(kandidati, udaljenosti, komp)
    return rez


# --------------------------------------------------------------- v1 -------
def klase_v1(G: nx.Graph, jezgre: dict, sigurni: set) -> dict:
    """E0 / E1 / E2+ preko mostova grafa s dodanim super-ponorom."""
    PONOR = ("__ponor__",)
    H = G.copy()
    H.add_edges_from((PONOR, s) for s in sigurni)
    povezanost = {}
    for i, komp in enumerate(nx.connected_components(H)):
        for n in komp:
            povezanost[n] = i
    komp2 = komponente_bez_mostova(H)
    rez = {}
    for nid, jz in jezgre.items():
        if not jz or all(povezanost[n] != povezanost[PONOR] for n in jz):
            rez[nid] = "E0"
        elif any(komp2[n] == komp2[PONOR] for n in jz):
            rez[nid] = "E2+"
        else:
            rez[nid] = "E1"
    return rez


# --------------------------------------------------------------- v2 -------
def _kapacitet(G: nx.Graph, u, v) -> int:
    return int(G[u][v].get("paralelno", 1) or 1)


def max_tok(G: nx.Graph, izvori: set, ponori: set, cutoff: int = MAKS_IZLAZA) -> tuple[int, dict]:
    """Edmonds–Karp za neusmjeren graf s cjelobrojnim kapacitetima, više izvora i ponora.

    Vraća (vrijednost toka do cutoff, tok) gdje je tok[(u, v)] = -tok[(v, u)].
    Ako izvor jest ponor, tok je „beskonačan“ → vraćamo cutoff.
    """
    if izvori & ponori:
        return cutoff, {}
    tok: dict = {}
    vrijednost = 0
    while vrijednost < cutoff:
        prethodni = {n: None for n in izvori}
        red = deque(izvori)
        kraj = None
        while red and kraj is None:
            u = red.popleft()
            for v in G.adj[u]:
                if v in prethodni:
                    continue
                if _kapacitet(G, u, v) - tok.get((u, v), 0) > 0:
                    prethodni[v] = u
                    if v in ponori:
                        kraj = v
                        break
                    red.append(v)
        if kraj is None:
            break
        put = []
        v = kraj
        while prethodni[v] is not None:
            put.append((prethodni[v], v))
            v = prethodni[v]
        usko = min(_kapacitet(G, a, b) - tok.get((a, b), 0) for a, b in put)
        potisak = min(usko, cutoff - vrijednost)
        for a, b in put:
            tok[(a, b)] = tok.get((a, b), 0) + potisak
            tok[(b, a)] = -tok[(a, b)]
        vrijednost += potisak
    return vrijednost, tok


def rez_najblizi_ponoru(G: nx.Graph, izvori: set, ponori: set, tok: dict) -> tuple[list, set]:
    """Minimalni rez najbliži ponoru i područje „iza“ njega.

    Čvorovi koji u rezidualnom grafu mogu doći do ponora čine stranu ponora.
    Bridovi s ostatka grafa na tu stranu čine rez (zasićeni su). Područje iza
    reza je komponenta izvora u grafu bez bridova reza — tako ne „pokupimo“
    nepovezane otoke koji također ne dosežu ponor.
    """
    do_ponora = set(ponori)
    red = deque(ponori)
    while red:
        v = red.popleft()
        for u in G.adj[v]:
            if u not in do_ponora and _kapacitet(G, u, v) - tok.get((u, v), 0) > 0:
                do_ponora.add(u)
                red.append(u)
    # Područje iza: BFS od izvora koji ne prelazi na stranu ponora.
    iza = set(izvori)
    red = deque(izvori)
    rez = []
    while red:
        u = red.popleft()
        for v in G.adj[u]:
            if v in do_ponora:
                rez.append((u, v))
            elif v not in iza:
                iza.add(v)
                red.append(v)
    return sorted(set(tuple(sorted((u, v), key=str)) for u, v in rez), key=str), iza


def putovi_toka(izvori: set, ponori: set, tok: dict) -> list[list]:
    """Rastavi tok na bridno-disjunktne putove (izvor → ponor) — to su IZLAZNI PRAVCI za kartu.

    Zašto iz toka, a ne npr. k najkraćih putova: tok već jamči da putovi nemaju
    zajednički brid, pa ih je na karti točno onoliko koliko piše „broj izlaza“.
    Ako rastavljanje naiđe na kružni tok, petlju izrežemo (ne mijenja izlaz).
    """
    izlaz: dict = {}
    for (u, v), f in tok.items():
        if f > 0:
            izlaz.setdefault(u, {})[v] = f
    putovi = []
    for s in izvori:
        while izlaz.get(s):
            put, u = [s], s
            while u not in ponori:
                susjedi = izlaz.get(u)
                if not susjedi:
                    break  # ne bi se smjelo dogoditi (očuvanje toka); put odbacujemo
                v = next(iter(susjedi))
                susjedi[v] -= 1
                if susjedi[v] == 0:
                    del susjedi[v]
                if v in put:
                    put = put[:put.index(v) + 1]
                else:
                    put.append(v)
                u = v
            if u in ponori:
                putovi.append(put)
    return putovi


def klasa(e: int) -> str:
    if e == 0:
        return "E0"
    if e == 1:
        return "E1"
    if e >= MAKS_IZLAZA:
        return "E6+"
    return "E2-5"


@dataclass
class UskoGrlo:
    bridovi: list
    naselja_iza: set = field(default_factory=set)
    cvorovi_iza: set = field(default_factory=set)


def izlazi_svih(G: nx.Graph, jezgre: dict, sigurni: set) -> tuple[dict, dict]:
    """D4 v2 za sva naselja.

    Vraća (po_naselju, uska_grla):
      po_naselju[id] = {izlazi_e, klasa_izlaza, usko_grlo (ključ ili None), cvorovi_iza (set), putovi}
      uska_grla[ključ] = UskoGrlo — ključ je tuple bridova reza (isti rez dijeli više naselja).
    """
    po_naselju, uska = {}, {}
    for nid, jz in jezgre.items():
        if not jz:
            po_naselju[nid] = {"izlazi_e": 0, "klasa_izlaza": "E0", "usko_grlo": None, "cvorovi_iza": set(),
                               "putovi": []}
            continue
        e, tok = max_tok(G, set(jz), sigurni)
        zapis = {"izlazi_e": int(e), "klasa_izlaza": klasa(e), "usko_grlo": None, "cvorovi_iza": set(),
                 "putovi": putovi_toka(set(jz), sigurni, tok)}
        if e < MAKS_IZLAZA:
            bridovi, iza = rez_najblizi_ponoru(G, set(jz), sigurni, tok)
            zapis["cvorovi_iza"] = iza
            if bridovi:
                kljuc = tuple(bridovi)
                ug = uska.setdefault(kljuc, UskoGrlo(bridovi=bridovi))
                ug.cvorovi_iza |= iza
                zapis["usko_grlo"] = kljuc
        po_naselju[nid] = zapis
    return po_naselju, uska


def naselja_u_podrucju(jezgre: dict, cvorovi_iza: set) -> list:
    """Naselja čija je jezgra (većinom) u zadanom skupu čvorova."""
    return [nid for nid, jz in jezgre.items() if jz and sum(n in cvorovi_iza for n in jz) * 2 > len(jz)]


def geometrija_brida(G: nx.Graph, u, v) -> LineString:
    g = G[u][v].get("geometry")
    if g is not None:
        return g
    return LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])])


def geometrija_puta(G: nx.Graph, put: list) -> LineString:
    """Niz čvorova → jedna linija; geometriju svakog brida okrećemo u smjeru puta."""
    koord = []
    for u, v in zip(put, put[1:]):
        c = list(geometrija_brida(G, u, v).coords)
        pu = (G.nodes[u]["x"], G.nodes[u]["y"])
        if np.hypot(c[0][0] - pu[0], c[0][1] - pu[1]) > np.hypot(c[-1][0] - pu[0], c[-1][1] - pu[1]):
            c.reverse()
        koord.extend(c if not koord else c[1:])
    return LineString(koord)


def oznaka_ceste(ref) -> str | None:
    """OSM `ref` → službena oznaka javne ceste.

    U hrvatskom OSM-u državne i autoceste imaju slovo (D8, A1), a županijske i
    lokalne samo broj. Po sustavu razvrstavanja javnih cesta županijske imaju
    4 znamenke (Ž6090), lokalne 5 (L65014). Ostalo (npr. „650650“) nije valjana
    oznaka javne ceste pa je ne prikazujemo.
    """
    if not ref:
        return None
    ref = str(ref).split(";")[0].strip().replace(" ", "")
    if ref[:1] in ("A", "D") and ref[1:].isdigit():
        return ref
    if ref.isdigit() and len(ref) == 4:
        return f"Ž{ref}"
    if ref.isdigit() and len(ref) == 5:
        return f"L{ref}"
    return None


def opis_puta(G: nx.Graph, put: list, sigurni_autocesta: set) -> dict:
    """Duljina (km), redom oznake cesta (D121 → D8 …) i kamo put izlazi (autocesta / izvan županije)."""
    duljina, ceste = 0.0, []
    for u, v in zip(put, put[1:]):
        d = G[u][v]
        duljina += float(d.get("length") or 0)
        ref = oznaka_ceste(d.get("ref"))
        if ref and (not ceste or ceste[-1] != ref):
            ceste.append(ref)
    return {"km": round(duljina / 1000, 1), "ceste": ceste[:6],
            "kraj": "autocesta" if put[-1] in sigurni_autocesta else "izvan županije"}


def cvorovi_autoceste(G: nx.Graph) -> set:
    return {n for u, v, d in G.edges(data=True) if d.get("highway") == "motorway" for n in (u, v)}


def geometrija_reza(G: nx.Graph, bridovi: list) -> MultiLineString:
    return MultiLineString([geometrija_brida(G, u, v) for u, v in bridovi])


def pokretni_mostovi_iza(G: nx.Graph, sigurni: set) -> set:
    """Čvorovi s kojih SVAKI put do sigurne mreže prelazi pokretni most (D10).

    Za svaki pokretni most koji je most grafa uklonimo ga i uzmemo stranu bez sigurnih čvorova.
    """
    rez = set()
    mostovi = set(nx.bridges(G))
    for u, v, d in G.edges(data=True):
        if not d.get("pokretni_most") or ((u, v) not in mostovi and (v, u) not in mostovi):
            continue
        H = G.copy()
        H.remove_edge(u, v)
        for strana in (nx.node_connected_component(H, u), nx.node_connected_component(H, v)):
            if not (strana & sigurni):
                rez |= strana
    return rez
