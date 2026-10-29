"""Analiza osjetljivosti prioriteta (D9) na pretpostavke: scenarij opt/pes i težine H.

Ponovno računa razred i indeks iz izvezenog settlements.geojson i uspoređuje top-10.
Rezultat: docs/osjetljivost.md (uključeno u docs/metodologija.md poveznicom).

python -m etl.osjetljivost
"""
from __future__ import annotations

import json

from etl import priority
from etl.config import DOCS_DIR, WEB_DATA_DIR

RED = {"A": 0, "B": 1, "C": 2, "-": 3}


def _top(naselja: list[dict], scenarij: str = "sred", w_g: float = 0.6) -> list[tuple]:
    """Top-10 (id, naziv, razred) za scenarij vremena i težinu goriva w_g (težina požara = 1 − w_g)."""
    hs = []
    for n in naselja:
        if n["h_gorivo"] is None:
            hs.append(None)
            continue
        hs.append(w_g * n["h_gorivo"] + (1 - w_g) * n.get("_p_norm", 0.0))
    granice = priority.tercili(hs)
    redovi = []
    for n, h in zip(naselja, hs):
        t = n["t_evak_h"][scenarij] if n["t_evak_h"] else None
        hr = priority.h_razred(h, granice)
        r = priority.razred(n["klasa_izlaza"], hr, t)
        redovi.append((RED[r], -priority.indeks(n["klasa_izlaza"], h, t), n["id"], n["naziv"], r))
    redovi.sort()
    return [(x[2], x[3], x[4]) for x in redovi[:10]], sum(1 for x in redovi if x[4] == "A")


def main():
    d = json.loads((WEB_DATA_DIR / "settlements.geojson").read_text(encoding="utf-8"))
    naselja = [f["properties"] for f in d["features"]]
    # p_norm iz H: h = 0,6 g + 0,4 p  →  p = (h − 0,6 g) / 0,4 (rekonstrukcija bez ponovnog dohvata EFFIS-a
    # ili modela; „bez povijesti požara“ znači i bez D11 podložnosti)
    for n in naselja:
        if n["h_stat"] is not None and n["h_gorivo"] is not None:
            n["_p_norm"] = max(0.0, (n["h_stat"] - 0.6 * n["h_gorivo"]) / 0.4)
    osnova, a0 = _top(naselja)
    varijante = {
        "T opt (manje ljudi, veći protok)": _top(naselja, "opt"),
        "T pes (više ljudi, manji protok)": _top(naselja, "pes"),
        "H = 0,5·g + 0,5·p": _top(naselja, "sred", 0.5),
        "H = 0,7·g + 0,3·p": _top(naselja, "sred", 0.7),
        "H = 1,0·g (bez povijesti požara)": _top(naselja, "sred", 1.0),
    }
    skup0 = {x[0] for x in osnova}
    L = ["# Analiza osjetljivosti prioriteta", "",
         "Generirano naredbom `python -m etl.osjetljivost` iz `web/public/data/settlements.geojson`.", "",
         f"Osnovni scenarij (T središnji, H = 0,6·g + 0,4·p): {a0} naselja u razredu A.", "",
         "Top-10 u osnovnom scenariju: " + ", ".join(f"{x[1]} ({x[2]})" for x in osnova) + ".", "",
         "| Varijanta | Naselja u A | Isti u top-10 | Novi u top-10 |", "|---|---|---|---|"]
    for ime, (top, a) in varijante.items():
        skup = {x[0] for x in top}
        novi = [x[1] for x in top if x[0] not in skup0]
        L.append(f"| {ime} | {a} | {len(skup & skup0)}/10 | {', '.join(novi) or '–'} |")
    L += ["", "Tumačenje: što je više naselja „isto u top-10“, to je lista manje ovisna o pretpostavkama. "
          "Naselja koja ostaju na vrhu u svim varijantama su najpouzdaniji kandidati za plan evakuacije.", ""]
    (DOCS_DIR / "osjetljivost.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
