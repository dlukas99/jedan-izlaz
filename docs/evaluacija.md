# Evaluacija modela podložnosti požaru (D11)

Generirano 2026-10-29 naredbom `python -m etl.ml_susceptibility`.

## Postavke

- Područje: 7 obalnih županija (Istarska, Primorsko-goranska, Ličko-senjska, Zadarska, Šibensko-kninska, Splitsko-dalmatinska, Dubrovačko-neretvanska), mreža 250 m, 395.128 kopnenih ćelija.
- Cilj: ćelija presijeca EFFIS opožarenu površinu (MODIS/VIIRS, ~≥ 30 ha, 2000.–danas): 33.325 ćelija (8,4 %).
- Značajke: drvece, grmlje, travnjaci, poljoprivreda, izgradeno, golo, udalj_cesta_m, udalj_naselje_m, udalj_voda_m (udaljenosti logaritmirane). Bez nagiba/ekspozicije: licenca DEM-a nije provjerena.
- Evaluacija: prostorna blok-CV, blokovi 10 km, 5 preklopa (GroupKFold), 432 blokova.

## Rezultati (out-of-fold)

| Model | ROC-AUC | PR-AUC | Brier |
|---|---|---|---|
| Logistička regresija (baseline) | 0.747 | 0.273 | 0.0699 |
| Gradient boosting (HistGradientBoosting) | 0.776 | 0.312 | 0.0678 |

Udio pozitivnih (PR-AUC slučajnog modela): 0.084.

## Kalibracija (gradient boosting, po decilima predviđanja)

| Predviđeno | Stvarno |
|---|---|
| 0.006 | 0.013 |
| 0.014 | 0.024 |
| 0.021 | 0.027 |
| 0.029 | 0.035 |
| 0.038 | 0.041 |
| 0.050 | 0.056 |
| 0.068 | 0.075 |
| 0.097 | 0.100 |
| 0.153 | 0.153 |
| 0.363 | 0.319 |

## Odluka

Model je **prihvaćen** (ROC-AUC 0.776 ≥ 0.7 i bolji od baselinea): u D8 komponenta `p` (povijest požara) zamijenjena je prosječnom podložnošću modela u krugu 5 km, normiranom unutar pilota.

## Ograničenja

- EFFIS bilježi samo veće požare (~≥ 30 ha); manji požari nisu u cilju.
- Opožarene površine ovise i o gašenju i dostupnosti, ne samo o podložnosti terena.
- WorldCover je iz 2021.; nakon požara pokrov se mijenja (moguće obrnuto curenje informacije).
- Model je prostorni (gdje je teren podložan), a ne dnevna prognoza izbijanja požara.
