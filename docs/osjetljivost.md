# Analiza osjetljivosti prioriteta

Generirano naredbom `python -m etl.osjetljivost` iz `web/public/data/settlements.geojson`.

Osnovni scenarij (T središnji, H = 0,6·g + 0,4·p): 1 naselja u razredu A.

Top-10 u osnovnom scenariju: Grebaštica (A), Dazlina (B), Jezera (B), Tisno (B), Murter (B), Betina (B), Raslina (B), Dubrava kod Tisna (B), Gradina (B), Drinovci (B).

| Varijanta | Naselja u A | Isti u top-10 | Novi u top-10 |
|---|---|---|---|
| T opt (manje ljudi, veći protok) | 0 | 9/10 | Nos Kalik |
| T pes (više ljudi, manji protok) | 1 | 7/10 | Bilice, Stivašnica, Ražanj |
| H = 0,5·g + 0,5·p | 1 | 9/10 | Zečevo Rogozničko |
| H = 0,7·g + 0,3·p | 1 | 10/10 | – |
| H = 1,0·g (bez povijesti požara) | 3 | 5/10 | Radljevac, Kornati, Zlarin, Kaprije, Žirje |

Tumačenje: što je više naselja „isto u top-10“, to je lista manje ovisna o pretpostavkama. Naselja koja ostaju na vrhu u svim varijantama su najpouzdaniji kandidati za plan evakuacije.
