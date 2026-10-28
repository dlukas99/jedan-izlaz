"""D9: prioritet naselja u razredima A / B / C / – (decimalni indeks služi samo za sortiranje).

A: (E0 ili E1) i H visok i (E0 ili T_sred ≥ 1 h)
B: (E0 ili E1) i (H srednji ili T_sred > 3 h); ili E2-5 i H visok i T_sred > 3 h
C: ostali E0–E5
–: E6+

iz = 100 · H_stat · f(E) · g(T), f(E0)=1, f(E1)=0,9, f(E2-5)=0,4, f(E6+)=0,
g = min(1, T_sred / 3 h), za E0 g = 1.  (PRETPOSTAVKA, analiza osjetljivosti u docs/metodologija.md)
"""
from __future__ import annotations

from etl.config import F_KLASE, T_NORMA_H, T_PRAG_A_H, T_PRAG_B_H


def razred(klasa: str, h_razred: str | None, t_sred: float | None) -> str:
    if klasa == "E6+":
        return "-"
    t = t_sred if t_sred is not None else 0.0
    jedan = klasa in ("E0", "E1")
    if jedan and h_razred == "visok" and (klasa == "E0" or t >= T_PRAG_A_H):
        return "A"
    if jedan and (h_razred == "srednji" or t > T_PRAG_B_H):
        return "B"
    if klasa == "E2-5" and h_razred == "visok" and t > T_PRAG_B_H:
        return "B"
    return "C"


def indeks(klasa: str, h_stat: float | None, t_sred: float | None) -> float:
    if klasa == "E0":
        g = 1.0
    else:
        g = min(1.0, (t_sred or 0.0) / T_NORMA_H)
    return round(100 * (h_stat or 0.0) * F_KLASE[klasa] * g, 1)


def tercili(vrijednosti: list[float]) -> tuple[float, float]:
    """Granice tercila (33. i 67. percentil) — razredi H su relativni unutar pilota."""
    s = sorted(v for v in vrijednosti if v is not None)
    if not s:
        return (0.0, 0.0)
    q = lambda p: s[min(len(s) - 1, int(round(p * (len(s) - 1))))]
    return q(1 / 3), q(2 / 3)


def h_razred(h: float | None, granice: tuple[float, float]) -> str | None:
    if h is None:
        return None
    if h <= granice[0]:
        return "nizak"
    if h <= granice[1]:
        return "srednji"
    return "visok"
