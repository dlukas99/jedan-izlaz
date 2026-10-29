"""D11: model podložnosti požaru (opožareno da/ne) na mreži 250 m za 7 obalnih županija.

Zašto 7 županija: jedna županija ima premalo opožarenih ćelija za pouzdan model.

Značajke (sve iz otvorenih izvora, bez DEM-a jer licenca Copernicus GLO-30 još nije provjerena — N):
- udjeli WorldCover 2021 klasa u ćeliji (drveće, grmlje, travnjaci, poljoprivreda, izgrađeno, golo tlo);
- udaljenost do ceste (OSM), do naselja (OSM place) i do vode (WorldCover klasa 80, more i jezera);
- koordinate NISU značajke (model bi naučio „gdje je gorjelo“, a ne „zašto“).
Cilj: ćelija presijeca EFFIS opožarenu površinu (2000.–danas).

Evaluacija: prostorna blok-CV (blokovi 10 km, GroupKFold) — susjedne ćelije su
korelirane, pa bi obična CV precijenila točnost. Metrike: ROC-AUC, PR-AUC, Brier.
Model zamjenjuje `p` u D8 SAMO ako je AUC ≥ 0,70 i bolji od logističke regresije.
Rezultat se uvijek upisuje u docs/evaluacija.md.

python -m etl.ml_susceptibility
"""
from __future__ import annotations

import datetime as dt
import json

import geopandas as gpd
import numpy as np
import rasterio
from rasterio import features
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from etl import load_dgu, load_effis, load_osm
from etl.config import CRS_ANALIZA, DOCS_DIR, INTERIM_DIR, WORLDCOVER_URL
from etl.hazard import GDAL_ENV

OBALNE = ["Istarska", "Primorsko-goranska", "Ličko-senjska", "Zadarska", "Šibensko-kninska",
          "Splitsko-dalmatinska", "Dubrovačko-neretvanska"]  # izvor: NUTS HR03 Jadranska Hrvatska
CELIJA_M = 250        # izvor: D11
BLOK_M = 10_000       # izvor: D11 (prostorna blok-CV)
PRAG_AUC = 0.70       # izvor: D11
KLASE = {10: "drvece", 20: "grmlje", 30: "travnjaci", 40: "poljoprivreda", 50: "izgradeno", 60: "golo"}
WC_PREGLED = 2        # WorldCover COG pregled razine 2 (faktor 8 → ~80 m), da ne vučemo pune tileove
SUSC_TIF = INTERIM_DIR / "podloznost_250m.tif"
REZ_JSON = INTERIM_DIR / "ml_rezultat.json"


def _mreza(kopno: gpd.GeoDataFrame):
    x0, y0, x1, y1 = kopno.total_bounds
    sirina = int(np.ceil((x1 - x0) / CELIJA_M))
    visina = int(np.ceil((y1 - y0) / CELIJA_M))
    return from_origin(x0, y1, CELIJA_M, CELIJA_M), (visina, sirina)


def _rasteriziraj(geoms, transform, oblik, all_touched=False) -> np.ndarray:
    geoms = [g for g in geoms if g is not None and not g.is_empty]
    if not geoms:
        return np.zeros(oblik, dtype=np.uint8)
    return features.rasterize(((g, 1) for g in geoms), out_shape=oblik, transform=transform,
                              fill=0, dtype="uint8", all_touched=all_touched)


def _udaljenost(maska_cilja: np.ndarray) -> np.ndarray:
    """Udaljenost (m) svake ćelije do najbliže ćelije cilja."""
    return ndimage.distance_transform_edt(maska_cilja == 0) * CELIJA_M


def _worldcover_udjeli(transform, oblik) -> dict[str, np.ndarray]:
    """Udio svake WorldCover klase u ćeliji 250 m (prosjek indikatora, pregled ~80 m)."""
    klase = {**KLASE, 80: "voda"}  # voda nije značajka, služi za udaljenost do obale
    udjeli = {ime: np.zeros(oblik, dtype=np.float32) for ime in klase.values()}
    with rasterio.Env(**GDAL_ENV):
        for tile in ("N42E012", "N42E015", "N42E018", "N45E012", "N45E015"):
            print(f"[D11]   WorldCover {tile}", flush=True)
            with rasterio.open("/vsicurl/" + WORLDCOVER_URL.format(tile=tile), OVERVIEW_LEVEL=WC_PREGLED) as ds:
                a = ds.read(1)
                for kod, ime in klase.items():
                    izlaz = np.full(oblik, np.nan, dtype=np.float32)
                    reproject((a == kod).astype(np.float32), izlaz, src_transform=ds.transform, src_crs=ds.crs,
                              dst_transform=transform, dst_crs=CRS_ANALIZA, resampling=Resampling.average,
                              src_nodata=None, dst_nodata=np.nan)
                    m = ~np.isnan(izlaz)
                    udjeli[ime][m] = izlaz[m]
    return udjeli


def pripremi():
    au = load_dgu.ucitaj_au()
    zup = au[(au.razina == "zupanija") & au.naziv.str.startswith(tuple(OBALNE))]
    kopno = gpd.GeoDataFrame(geometry=[zup.union_all()], crs=CRS_ANALIZA)
    transform, oblik = _mreza(kopno)
    print(f"[D11] mreža {oblik[0]}×{oblik[1]} ćelija od {CELIJA_M} m", flush=True)
    m_kopno = _rasteriziraj(kopno.geometry, transform, oblik).astype(bool)

    bbox_wgs = tuple(round(float(x), 2) for x in kopno.to_crs(4326).total_bounds)
    poligon_wgs = kopno.to_crs(4326).geometry.iloc[0].envelope
    print("[D11] EFFIS opožarene površine", flush=True)
    pozari = load_effis.opozarene_povrsine(bbox_wgs)
    y = _rasteriziraj(pozari.geometry, transform, oblik, all_touched=True)

    print("[D11] OSM ceste i naselja", flush=True)
    ceste = _osm_ceste(poligon_wgs)
    mjesta = load_osm.dohvati_objekte(poligon_wgs, {"place": ["city", "town", "village", "hamlet"]}, "place_jadran")

    print("[D11] WorldCover udjeli", flush=True)
    X = _worldcover_udjeli(transform, oblik)
    voda = X.pop("voda")
    X["udalj_cesta_m"] = _udaljenost(_rasteriziraj(ceste, transform, oblik, all_touched=True))
    X["udalj_naselje_m"] = _udaljenost(_rasteriziraj(mjesta.geometry, transform, oblik, all_touched=True))
    # Voda (more i jezera) iz WorldCovera; kopnena granica s BiH/Slovenijom tako ne glumi „obalu“.
    X["udalj_voda_m"] = _udaljenost((voda > 0.5).astype(np.uint8))
    return X, y, m_kopno, transform, oblik


def _osm_ceste(poligon_wgs) -> gpd.GeoSeries:
    """Vozive ceste iz Geofabrik PBF-a kao linije (bez grafa — trebaju nam samo udaljenosti)."""
    import osmium
    from shapely.geometry import LineString

    from etl.config import HIGHWAY_GLAVNI
    put = INTERIM_DIR / "osm_ceste_jadran.gpkg"
    if put.exists():
        return gpd.read_file(put).geometry
    x0, y0, x1, y1 = poligon_wgs.bounds
    linije = []
    for w in osmium.FileProcessor(str(load_osm.pbf())).with_locations().with_filter(osmium.filter.KeyFilter("highway")):
        if not w.is_way() or w.tags.get("highway") not in HIGHWAY_GLAVNI or w.tags.get("highway") == "service":
            continue
        t = [(n.lon, n.lat) for n in w.nodes if n.location.valid()]
        if len(t) >= 2 and any(x0 <= a <= x1 and y0 <= b <= y1 for a, b in t):
            linije.append(LineString(t))
    g = gpd.GeoSeries(linije, crs=4326).to_crs(CRS_ANALIZA)
    gpd.GeoDataFrame(geometry=g).to_file(put, driver="GPKG")
    return g


def evaluiraj(X: dict, y: np.ndarray, maska: np.ndarray, oblik):
    imena = list(X)
    redovi, stupci = np.nonzero(maska)
    M = np.column_stack([X[k][redovi, stupci] for k in imena]).astype(np.float32)
    M[:, imena.index("udalj_cesta_m")] = np.log1p(M[:, imena.index("udalj_cesta_m")])
    M[:, imena.index("udalj_naselje_m")] = np.log1p(M[:, imena.index("udalj_naselje_m")])
    M[:, imena.index("udalj_voda_m")] = np.log1p(M[:, imena.index("udalj_voda_m")])
    M = np.nan_to_num(M)
    t = y[redovi, stupci].astype(int)
    blok = (redovi // (BLOK_M // CELIJA_M)) * 10_000 + (stupci // (BLOK_M // CELIJA_M))
    modeli = {
        "logisticka_regresija": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "gradient_boosting": lambda: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06,
                                                                    max_leaf_nodes=31, random_state=0),
    }
    rez = {}
    for ime, tvornica in modeli.items():
        oof = np.zeros(len(t), dtype=np.float64)
        for tr, te in GroupKFold(n_splits=5).split(M, t, blok):
            m = tvornica().fit(M[tr], t[tr])
            oof[te] = m.predict_proba(M[te])[:, 1]
        rez[ime] = {"roc_auc": round(float(roc_auc_score(t, oof)), 4),
                    "pr_auc": round(float(average_precision_score(t, oof)), 4),
                    "brier": round(float(brier_score_loss(t, oof)), 4)}
        # Kalibracija po decilima predviđanja (za evaluacija.md).
        kv = np.quantile(oof, np.linspace(0, 1, 11))
        rez[ime]["kalibracija"] = [
            {"predvideno": round(float(oof[(oof >= a) & (oof <= b)].mean()), 4),
             "stvarno": round(float(t[(oof >= a) & (oof <= b)].mean()), 4)}
            for a, b in zip(kv[:-1], kv[1:]) if ((oof >= a) & (oof <= b)).any()]
        print(f"[D11] {ime}: {rez[ime]['roc_auc']=} {rez[ime]['pr_auc']=}", flush=True)
    najbolji = rez["gradient_boosting"]
    prihvacen = najbolji["roc_auc"] >= PRAG_AUC and najbolji["roc_auc"] > rez["logisticka_regresija"]["roc_auc"]
    # Konačni model na svim podacima → raster podložnosti.
    konacni = modeli["gradient_boosting"]().fit(M, t)
    susc = np.full(oblik, np.nan, dtype=np.float32)
    susc[redovi, stupci] = konacni.predict_proba(M)[:, 1]
    return rez, prihvacen, susc, {"celija": len(t), "opozareno": int(t.sum()), "blokova": int(len(np.unique(blok))),
                                  "znacajke": imena}


def podloznost_u_krugu(tocke_3765: gpd.GeoSeries, radijus_m: float) -> list[float | None]:
    """Prosječna podložnost modela u krugu oko svake točke (za D8, ako je model prihvaćen)."""
    from rasterio.mask import mask as rmask
    rez = []
    with rasterio.open(SUSC_TIF) as ds:
        for p in tocke_3765:
            try:
                a, _ = rmask(ds, [p.buffer(radijus_m)], crop=True, nodata=np.nan, filled=True)
                v = np.nanmean(a) if np.isfinite(a).any() else np.nan
            except ValueError:
                v = np.nan
            rez.append(None if not np.isfinite(v) else round(float(v), 4))
    return rez


def prihvacen() -> bool:
    if not (REZ_JSON.exists() and SUSC_TIF.exists()):
        return False
    return bool(json.loads(REZ_JSON.read_text(encoding="utf-8")).get("prihvacen"))


def main():
    X, y, maska, transform, oblik = pripremi()
    rez, prihvacen, susc, info = evaluiraj(X, y, maska, oblik)
    with rasterio.open(SUSC_TIF, "w", driver="GTiff", height=oblik[0], width=oblik[1], count=1, dtype="float32",
                       crs=CRS_ANALIZA, transform=transform, nodata=np.nan, compress="deflate") as ds:
        ds.write(susc, 1)
    zapis = {"datum": dt.date.today().isoformat(), "prihvacen": bool(prihvacen), "prag_auc": PRAG_AUC,
             "modeli": rez, **info}
    REZ_JSON.write_text(json.dumps(zapis, ensure_ascii=False, indent=1), encoding="utf-8")
    pisi_evaluaciju(zapis)
    print(f"[D11] prihvaćen za D8: {prihvacen}")


def pisi_evaluaciju(z: dict):
    lr, gb = z["modeli"]["logisticka_regresija"], z["modeli"]["gradient_boosting"]
    tis = lambda n: f"{n:,}".replace(",", ".")  # hrvatski razdjelnik tisućica
    postotak = f"{100 * z['opozareno'] / z['celija']:.1f}".replace(".", ",")
    L = ["# Evaluacija modela podložnosti požaru (D11)", "",
         f"Generirano {z['datum']} naredbom `python -m etl.ml_susceptibility`.", "",
         "## Postavke", "",
         f"- Područje: 7 obalnih županija ({', '.join(OBALNE)}), mreža {CELIJA_M} m, {tis(z['celija'])} kopnenih ćelija.",
         f"- Cilj: ćelija presijeca EFFIS opožarenu površinu (MODIS/VIIRS, ~≥ 30 ha, 2000.–danas): "
         f"{tis(z['opozareno'])} ćelija ({postotak} %).",
         f"- Značajke: {', '.join(z['znacajke'])} (udaljenosti logaritmirane). Bez nagiba/ekspozicije: licenca DEM-a nije provjerena.",
         f"- Evaluacija: prostorna blok-CV, blokovi {BLOK_M // 1000} km, 5 preklopa (GroupKFold), {z['blokova']} blokova.", "",
         "## Rezultati (out-of-fold)", "",
         "| Model | ROC-AUC | PR-AUC | Brier |", "|---|---|---|---|",
         f"| Logistička regresija (baseline) | {lr['roc_auc']:.3f} | {lr['pr_auc']:.3f} | {lr['brier']:.4f} |",
         f"| Gradient boosting (HistGradientBoosting) | {gb['roc_auc']:.3f} | {gb['pr_auc']:.3f} | {gb['brier']:.4f} |",
         "", f"Udio pozitivnih (PR-AUC slučajnog modela): {z['opozareno'] / z['celija']:.3f}.", "",
         "## Kalibracija (gradient boosting, po decilima predviđanja)", "",
         "| Predviđeno | Stvarno |", "|---|---|"]
    L += [f"| {k['predvideno']:.3f} | {k['stvarno']:.3f} |" for k in gb["kalibracija"]]
    L += ["", "## Odluka", "",
          (f"Model je **prihvaćen** (ROC-AUC {gb['roc_auc']:.3f} ≥ {PRAG_AUC} i bolji od baselinea): u D8 komponenta `p` "
           "(povijest požara) zamijenjena je prosječnom podložnošću modela u krugu 5 km, normiranom unutar pilota."
           if z["prihvacen"] else
           f"Model **nije prihvaćen** (uvjet: ROC-AUC ≥ {PRAG_AUC} i bolji od baselinea). D8 i dalje koristi "
           "izmjerenu povijest požara (EFFIS) kao `p`."),
          "", "## Ograničenja", "",
          "- EFFIS bilježi samo veće požare (~≥ 30 ha); manji požari nisu u cilju.",
          "- Opožarene površine ovise i o gašenju i dostupnosti, ne samo o podložnosti terena.",
          "- WorldCover je iz 2021.; nakon požara pokrov se mijenja (moguće obrnuto curenje informacije).",
          "- Model je prostorni (gdje je teren podložan), a ne dnevna prognoza izbijanja požara.", ""]
    (DOCS_DIR / "evaluacija.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
