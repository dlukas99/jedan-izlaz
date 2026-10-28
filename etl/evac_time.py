"""D6: vrijeme evakuacije cestom kroz usko grlo, kao raspon scenarija.

T = (P_iza_reza / osoba_po_vozilu) / Σ kapacitet_bridova_reza

- Kapacitet brida = protok jedne trake u izlaznom smjeru × faktor klase ceste
  × broj paralelnih bridova (bez kontrasmjera).
- opt: manje ljudi, više osoba po vozilu, veći protok → najkraće vrijeme;
  pes: obrnuto. Prikazujemo „opt–pes (središnje sred)“, nikad jednu brojku.
- Kontrola razumnosti: središnji T < 5 min ili > 24 h zapisujemo za ručnu provjeru.
"""
from __future__ import annotations

from etl.config import (FAKTOR_KLASE_CESTE, KAPACITET_TRAKE_VOZ_H, OSOBA_PO_VOZILU, SCENARIJI,
                        T_MAX_RAZUMNO_H, T_MIN_RAZUMNO_H)


def faktor_klase(highway: str | None) -> float:
    if not highway:
        return FAKTOR_KLASE_CESTE["unclassified"]
    return FAKTOR_KLASE_CESTE.get(str(highway).replace("_link", ""), FAKTOR_KLASE_CESTE["unclassified"])


def kapacitet_reza(bridovi_atributi: list[dict]) -> dict:
    """Σ kapaciteta bridova reza (voz/h) po scenariju."""
    return {s: round(sum(KAPACITET_TRAKE_VOZ_H[s] * faktor_klase(d.get("highway")) * int(d.get("paralelno", 1) or 1)
                         for d in bridovi_atributi), 1) for s in SCENARIJI}


def vrijeme_h(ljudi: dict, kapacitet: dict) -> dict:
    """Vrijeme evakuacije u satima po scenariju (ljudi i kapacitet su dict po scenariju)."""
    return {s: round((ljudi[s] / OSOBA_PO_VOZILU[s]) / kapacitet[s], 2) if kapacitet[s] > 0 else None
            for s in SCENARIJI}


def razumno(t: dict) -> bool:
    sred = t.get("sred")
    return sred is None or T_MIN_RAZUMNO_H <= sred <= T_MAX_RAZUMNO_H


def tekst_raspona(t: dict | None) -> str:
    """„1,2–4,8 h (središnje 2,4 h)“ — hrvatski decimalni zarez."""
    if not t or t.get("sred") is None:
        return "–"
    f = lambda x: f"{x:.1f}".replace(".", ",")
    return f"{f(t['opt'])}–{f(t['pes'])} h (središnje {f(t['sred'])} h)"
