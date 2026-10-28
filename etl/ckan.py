"""Razrješavanje resursa preko data.gov.hr CKAN API-ja.

Zašto: kriterij „Upotreba otvorenih podataka“ boduje izravnu upotrebu API-ja,
pa URL resursa ne hardkodiramo nego ga svaki put tražimo preko package_show.
Uz to dobivamo metadata_modified i last_modified za meta.json.
"""
from __future__ import annotations

import re
import unicodedata

from etl import http
from etl.config import CKAN_API


def _poziv(akcija: str, **params) -> dict:
    r = http.get(CKAN_API + akcija, params=params)
    r.raise_for_status()
    odgovor = r.json()
    if not odgovor.get("success"):
        raise RuntimeError(f"CKAN {akcija} nije uspio: {odgovor.get('error')}")
    return odgovor["result"]


def package_show(paket_id: str) -> dict:
    return _poziv("package_show", id=paket_id)


def package_search(upit: str, rows: int = 20) -> list[dict]:
    return _poziv("package_search", q=upit, rows=rows)["results"]


def _norm(tekst: str) -> str:
    """Mala slova bez dijakritika — samo za usporedbu naziva resursa."""
    t = unicodedata.normalize("NFKD", tekst or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t.lower()).strip()


def nadji_resurs(paket: dict, *, naziv_sadrzi: str | None = None, url_sadrzi: str | None = None,
                 resurs_id: str | None = None) -> dict:
    """Odaberi resurs iz paketa po id-u, dijelu naziva ili dijelu URL-a."""
    for res in paket.get("resources", []):
        if resurs_id and res.get("id") == resurs_id:
            return res
        if naziv_sadrzi and _norm(naziv_sadrzi) in _norm(res.get("name", "")):
            return res
        if url_sadrzi and url_sadrzi.lower() in (res.get("url") or "").lower():
            return res
    raise KeyError(f"Resurs nije pronađen u paketu {paket.get('name')}: "
                   f"{naziv_sadrzi or url_sadrzi or resurs_id}")


def opis_izvora(paket: dict, resurs: dict) -> dict:
    """Sažetak za meta.json: tko je izdavač, licenca i kada je mijenjano."""
    org = paket.get("organization") or {}
    return {
        "paket": paket.get("name"),
        "naziv": paket.get("title"),
        "izdavac": org.get("title"),
        "licenca": paket.get("license_title") or paket.get("license_id"),
        "url_paketa": f"https://data.gov.hr/ckan/dataset/{paket.get('name')}",
        "url": resurs.get("url"),
        "resurs": resurs.get("name"),
        "metadata_modified": paket.get("metadata_modified"),
        "last_modified": resurs.get("last_modified") or resurs.get("metadata_modified"),
    }
