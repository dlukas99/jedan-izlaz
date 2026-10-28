# JEDAN IZLAZ

**Koliko cestovnih izlaza ima vaše naselje kad gori?** Javna web karta za planiranje evakuacije obalnih naselja: broj izlaznih cestovnih pravaca do sigurne mreže, usko grlo i broj ljudi ljeti iza njega, vrijeme evakuacije kao raspon scenarija te opasnost od požara (statička i dnevna EFFIS FWI).

Pilot: Šibensko-kninska županija. Projekt za *Datathon Portala otvorenih podataka 2026.* (izazov B – Okoliš i održivi prostor).

> Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.

## Pokretanje u 3 naredbe

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r etl/requirements.txt
python -m etl.pipeline --county SKZ --mode live
cd web; npm install; npm run dev
```

Testovi: `pytest -q`. Provjera izvora: `python -m etl.probe` (piše `docs/probe_report.md`).

## Izvori podataka

Popis svih skupova s izdavačem, poveznicom, licencom i datumom dohvata generira se u [docs/izvori.md](docs/izvori.md).

## Licence

- Kod: **EUPL-1.2** (vidi [LICENSE](LICENSE)).
- Izvedeni podaci s geometrijom iz OpenStreetMapa: **ODbL 1.0** („© OpenStreetMap contributors“).
- Sadrži podatke Državne geodetske uprave.

## Korišteni AI alati

U razvoju je korišten **Claude Code** (Anthropic) kao pomoćnik za pisanje koda i dokumentacije. Samo rješenje ne koristi nikakve zatvorene AI API-je.
