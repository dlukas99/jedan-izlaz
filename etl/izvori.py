"""Registar izvora: tko je izdavač, licenca, navod i kada je izvor dohvaćen.

Zašto: pravila natječaja traže popis svih skupova podataka s izdavačem i
poveznicom, a NN 67/17 traži navođenje izvora. Statični opis izvora je ovdje,
a dinamični dio (URL resursa, datum dohvata, metadata_modified) upisuju
loaderi pri svakom dohvatu u data/interim/izvori_dohvat.json.
"""
from __future__ import annotations

import datetime as dt
import json

from etl.config import INTERIM_DIR

OPIS = {
    "dzs_popis_naselja": {
        "naziv": "Popis stanovništva 2021. – stanovništvo prema starosti i spolu po naseljima",
        "izdavac": "Državni zavod za statistiku (DZS)", "licenca": "Otvorena dozvola",
        "navod": "Izvor: DZS, Popis stanovništva, kućanstava i stanova 2021.",
    },
    "dzs_stanovi": {
        "naziv": "Popis 2021. – stambene jedinice po gradovima i općinama (stanovi za odmor)",
        "izdavac": "Državni zavod za statistiku (DZS)", "licenca": "Otvorena dozvola",
        "navod": "Izvor: DZS, Popis stanovništva, kućanstava i stanova 2021.",
    },
    "dzs_turizam_2025": {
        "naziv": "Turizam u 2025. (Statistička izvješća 1747/2026), tablica 2.11 – postelje, dolasci i noćenja po gradovima i općinama",
        "izdavac": "Državni zavod za statistiku (DZS)", "licenca": "Otvorena dozvola",
        "navod": "Izvor: DZS, Turizam u 2025.",
    },
    "dzs_popunjenost_2025_08": {
        "naziv": "Dolasci i noćenja turista u kolovozu 2025. (priopćenje) – bruto popunjenost stalnih postelja",
        "izdavac": "Državni zavod za statistiku (DZS)", "licenca": "Otvorena dozvola",
        "navod": "Izvor: DZS, priopćenje za kolovoz 2025.", "url": "https://podaci.dzs.hr/2025/hr/97111",
    },
    "hc_brojenje_2025": {
        "naziv": "Brojenje prometa na cestama Republike Hrvatske godine 2025. (PGDP/PLDP)",
        "izdavac": "Hrvatske ceste d.o.o.", "licenca": "Otvorena dozvola",
        "navod": "Izvor: Hrvatske ceste, Brojenje prometa na cestama RH 2025.",
    },
    "hc_wfs": {
        "naziv": "Mreža javnih cesta RH – WFS INSPIRE (RoadLink)",
        "izdavac": "Hrvatske ceste d.o.o.", "licenca": "Nema uvjeta za pristup i korištenje (NIPP)",
        "navod": "Izvor: Hrvatske ceste, INSPIRE TN-RO WFS", "url": "https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs",
    },
    "dgu_au": {
        "naziv": "Upravne jedinice – INSPIRE (županije, gradovi i općine, naselja)",
        "izdavac": "Državna geodetska uprava (DGU)", "licenca": "Otvorena dozvola (NN 56/2023)",
        "navod": "Sadrži podatke Državne geodetske uprave (Upravne jedinice, INSPIRE)",
    },
    "dgu_rgi": {
        "naziv": "Registar geografskih imena – WFS (imenovana mjesta tipa „naselje“)",
        "izdavac": "Državna geodetska uprava (DGU)", "licenca": "Otvorena dozvola (NN 56/2023)",
        "navod": "Sadrži podatke Državne geodetske uprave (Registar geografskih imena)",
    },
    "effis_fwi": {
        "naziv": "EFFIS – indeks opasnosti od požara (Fire Weather Index, sloj mf010.fwi), WMS",
        "izdavac": "European Forest Fire Information System (EFFIS), Copernicus EMS / JRC", "licenca": "CC BY 4.0",
        "navod": "EFFIS – European Forest Fire Information System, Copernicus EMS / JRC",
        "url": "https://maps.effis.emergency.copernicus.eu/effis",
    },
    "effis_ba": {
        "naziv": "EFFIS – opožarene površine (modis.ba.poly), WFS",
        "izdavac": "European Forest Fire Information System (EFFIS), Copernicus EMS / JRC", "licenca": "CC BY 4.0",
        "navod": "EFFIS – European Forest Fire Information System, Copernicus EMS / JRC",
        "url": "https://maps.effis.emergency.copernicus.eu/effis",
    },
    "worldcover": {
        "naziv": "ESA WorldCover 10 m 2021 v200",
        "izdavac": "European Space Agency (ESA)", "licenca": "CC BY 4.0",
        "navod": "© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021)",
    },
    "osm": {
        "naziv": "OpenStreetMap – cestovna mreža, mjesta, turistički objekti",
        "izdavac": "OpenStreetMap contributors", "licenca": "ODbL 1.0",
        "navod": "© OpenStreetMap contributors", "url": "https://www.openstreetmap.org/copyright",
    },
    "jadrolinija": {
        "naziv": "Jadrolinija – državne brodske linije (ručno upisane linije u data/manual/trajekti.csv)",
        "izdavac": "Jadrolinija", "licenca": "javno objavljeni red plovidbe (činjenični podatak)",
        "navod": "Izvor: Jadrolinija, red plovidbe", "url": "https://www.jadrolinija.hr/",
    },
    "tz_tisno_most": {
        "naziv": "Raspored dizanja pokretnog mosta u Tisnom",
        "izdavac": "Turistička zajednica općine Tisno", "licenca": "javno objavljena informacija",
        "navod": "Izvor: TZ Tisno",
        "url": "https://www.tz-tisno.hr/hr/planiranje-putovanja/korisne-informacije/raspored-dizanja-mosta/",
    },
}

_PUT = INTERIM_DIR / "izvori_dohvat.json"


def zabiljezi(kljuc: str, **polja) -> None:
    """Upiši dinamične podatke o dohvatu (url, dohvaceno, metadata_modified …)."""
    _PUT.parent.mkdir(parents=True, exist_ok=True)
    stanje = json.loads(_PUT.read_text(encoding="utf-8")) if _PUT.exists() else {}
    zapis = stanje.get(kljuc, {})
    zapis.update({k: v for k, v in polja.items() if v is not None})
    zapis.setdefault("dohvaceno", dt.datetime.now().isoformat(timespec="seconds"))
    stanje[kljuc] = zapis
    _PUT.write_text(json.dumps(stanje, ensure_ascii=False, indent=2), encoding="utf-8")


def svi() -> list[dict]:
    """Spoji statični opis i zadnji dohvat — oblik zapisa iz sheme meta.json."""
    stanje = json.loads(_PUT.read_text(encoding="utf-8")) if _PUT.exists() else {}
    rez = []
    for kljuc, opis in OPIS.items():
        d = stanje.get(kljuc, {})
        rez.append({
            "kljuc": kljuc, "naziv": opis["naziv"], "izdavac": opis["izdavac"],
            "url": d.get("url") or opis.get("url"), "licenca": opis["licenca"], "navod": opis["navod"],
            "dohvaceno": d.get("dohvaceno"), "metadata_modified": d.get("metadata_modified"),
            **({"url_paketa": d["url_paketa"]} if d.get("url_paketa") else {}),
        })
    return rez
