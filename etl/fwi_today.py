"""Noćni job: EFFIS FWI za točke naselja → web/public/data/fwi_today.json (i povijesni dan).

Pokreće ga GitHub Actions (nightly_fwi.yml) svaku noć, bez ostatka pipelinea:
točke naselja čita iz već izvezenog settlements.geojson.

python -m etl.fwi_today [--datum YYYY-MM-DD] [--povijesni]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json

from etl import load_effis
from etl.config import EFFIS_FWI_SLOJ, POVIJESNI_DAN, WEB_DATA_DIR


def izracunaj(datum: str, naselja_geojson: dict) -> dict:
    tocke = [(f["properties"]["id"], *f["geometry"]["coordinates"]) for f in naselja_geojson["features"]]
    lon = [t[1] for t in tocke]
    lat = [t[2] for t in tocke]
    bbox = (round(min(lon) - 0.1, 2), round(min(lat) - 0.1, 2), round(max(lon) + 0.1, 2), round(max(lat) + 0.1, 2))
    put = load_effis.fwi_raster(datum, bbox, osvjezi=True)
    vrijednosti = load_effis.fwi_u_tockama(put, [(t[1], t[2]) for t in tocke])
    return {
        "datum": datum,
        "sloj": EFFIS_FWI_SLOJ,
        "izvor": "EFFIS – European Forest Fire Information System, Copernicus EMS / JRC (CC BY 4.0)",
        "dohvaceno": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "vrijednosti": {t[0]: v for t, v in zip(tocke, vrijednosti)},
        "razredi": {t[0]: load_effis.razred_fwi(v) for t, v in zip(tocke, vrijednosti)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datum", default=dt.date.today().isoformat())
    ap.add_argument("--povijesni", action="store_true", help=f"izračunaj i povijesni dan {POVIJESNI_DAN}")
    args = ap.parse_args()
    naselja = json.loads((WEB_DATA_DIR / "settlements.geojson").read_text(encoding="utf-8"))
    rez = izracunaj(args.datum, naselja)
    (WEB_DATA_DIR / "fwi_today.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"FWI {args.datum}: {sum(v is not None for v in rez['vrijednosti'].values())} naselja")
    if args.povijesni:
        rez = izracunaj(POVIJESNI_DAN, naselja)
        (WEB_DATA_DIR / f"fwi_{POVIJESNI_DAN}.json").write_text(json.dumps(rez, ensure_ascii=False, indent=1),
                                                                 encoding="utf-8")
        print(f"FWI {POVIJESNI_DAN}: gotovo")


if __name__ == "__main__":
    main()
