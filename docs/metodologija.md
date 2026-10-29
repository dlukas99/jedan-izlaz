# Metodologija

JEDAN IZLAZ za svako naselje računa koliko ima **neovisnih cestovnih izlaza** do sigurne mreže, gdje je
**usko grlo**, **koliko ljudi ljeti** stoji iza njega, **koliko bi trajala evakuacija cestom** (raspon) i
kolika je **opasnost od požara** oko naselja. Iz toga nastaje prioritetna lista za planove evakuacije.

> Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.

Sve konstante su u [`etl/config.py`](../etl/config.py), svaka s oznakom `# izvor:` ili `# PRETPOSTAVKA:`.
Popis izvora s licencama: [izvori.md](izvori.md). Kvaliteta podataka: [kvaliteta_podataka.md](kvaliteta_podataka.md).

## 1. Naselja (DZS ↔ DGU)

- **Stanovništvo**: DZS Popis 2021., „Stanovništvo prema starosti i spolu po naseljima“ (resurs se razrješava
  preko data.gov.hr CKAN API-ja). Zbroj naselja kontrolira se prema retku županije (ŠKŽ: 96.381).
- **Matični broj i poligon naselja**: DGU Upravne jedinice (INSPIRE AU, ATOM, ~600 MB GML).
  DZS nema matični broj, pa se spaja par (JLS, naziv) uz normalizaciju (CLAUDE.md §3.3) i rapidfuzz ≥ 88
  unutar iste JLS. **Rezultat za ŠKŽ: 199/199 naselja spojeno točno**, ručni ispravci nisu bili potrebni.
- **Točka naselja**: poligoni naselja u RH pokrivaju cijeli teritorij (šume, polja), pa „središte“ naselja
  uzimamo iz **DGU Registra geografskih imena** (tip „naselje“; 194/199), zatim OSM `place` (4), a tek onda
  reprezentativnu točku poligona (1).

## 2. Cestovni graf (D2) i sigurna mreža (D3)

- OpenStreetMap (Geofabrik izvadak za Hrvatsku, pyosmium → OSMnx), za poligon županije + 15 km.
  Vozive ceste: `motorway … tertiary` (+ `_link`), `unclassified, residential, living_street, service`
  bez `access=private|no`. Trajekti nisu bridovi. `retain_all=True` (inače nestaju otočne mreže).
- Graf je **neusmjeren** (mjerimo povezanost, ne smjer vožnje); paralelni bridovi broje se u `paralelno`.
- **Sigurni čvorovi**: izvan poligona županije proširenog za 1 km (`SIGURNO_PUFER_M`) i svi čvorovi na
  autocesti. Pufer je potreban jer je DGU poligon kopneni: rive i molovi strše u more i bez pufera bi
  postali „sigurna mreža“ na samom otoku (Murter bi bio E2-5, Žirje E1).
- **Ograničenje**: „sigurno“ znači *izvan županije ili na autocesti*, a ne *izvan dosega požara*.
- **Provjera pokrivenosti**: javne ceste Hrvatskih cesta (INSPIRE WFS, RoadLink) — OSM glavni graf pokriva
  99,5 % od 1.188 km javnih cesta u ŠKŽ (tolerancija 30 m).

## 3. Broj izlaznih pravaca (D4) — jezgra metode

1. **Jezgra naselja**: cestovni čvorovi u krugu oko točke naselja (radijus prema OSM tipu mjesta:
   town 2,5 km, village 700 m, hamlet 300 m; bez tipa procjena po broju stanovnika), unutar poligona
   naselja. Zadržavaju se samo čvorovi u **2-bridno-povezanoj komponenti s najviše čvorova**, pa slijepe
   ulice i prilazi kućama ne mijenjaju status.
2. **v1 — mostovi grafa** (`networkx.bridges` uz super-ponor spojen sa sigurnim čvorovima):
   E0 = nema puta, E1 = svaki put prelazi most grafa, E2+ = inače.
3. **v2 — maksimalni tok = broj bridno-disjunktnih putova** (Mengerov teorem): super-izvor → jezgra,
   sigurni čvorovi → super-ponor, kapacitet brida = broj paralelnih bridova; tok se računa do 6
   (Edmonds–Karp s BFS-om, vlastita implementacija s više izvora i ponora, testirana prema
   `networkx.maximum_flow_value`).
   Razredi: **E0, E1, E2-5, E6+** — prag ≈ 6 izlaza prema Fong i sur., *PNAS* 2026 (doi:10.1073/pnas.2535081123).
4. **Usko grlo** = minimalni rez **najbliži sigurnoj mreži** (čvorovi koji u rezidualnom grafu dosežu ponor čine
   njegovu stranu). Taj rez obuhvaća najviše ljudi „iza“ — npr. cijeli otok Murter s Betinom, Jezerima i
   Tisnom iza jedine kopnene dionice D121, a ne samo jednu ulicu. „Iza reza“ su naselja čija je jezgra u
   komponenti izvora u grafu bez bridova reza.
5. v1 i v2 se slažu za **199/199** naselja (provjera u svakom pokretanju).
6. **Izlazni pravci na karti**: tok se rastavi na bridno-disjunktne putove od jezgre do sigurne mreže
   (`graph_egress.putovi_toka`) — na karti ih je točno onoliko koliko piše „broj izlaza“. Uz svaki pravac
   izvozimo duljinu, redoslijed oznaka javnih cesta i kraj (autocesta ili izlaz iz županije) u
   `routes.geojson`. To je **ilustracija** neovisnih pravaca za planiranje, ne preporučeni put bijega:
   tok bira bilo koje disjunktne putove (najkraće po broju dionica), a ne najbrže ni najsigurnije.
   Oznake cesta: OSM `ref` od 4 znamenke = županijska (Ž), 5 znamenki = lokalna (L); ostalo se ne prikazuje.
7. **Pokretni most (D10)**: OSM `bridge=movable` (most D121 u Tisnu). Naselja s kojih svaki put prelazi
   pokretni most dobivaju napomenu s rasporedom dizanja (TZ Tisno); raspored ne ulazi u formulu.

**Validacija**: Murter, Betina, Jezera i Tisno su E1; Zlarin, Prvić Luka, Prvić Šepurine, Krapanj, Kaprije i
Žirje su E0 ([tests/test_cases_real.py](../tests/test_cases_real.py)). Radljevac, Dazlina i Kornati nemaju
vozivu cestu unutar 1 km, ali imaju šumske/poljske putove — označeni su `samo_putovi` (E0, ne „samo morem“).

## 4. Ljetna populacija (D5)

```
P = stanovnici_2021
  + stalne_postelje_JLS (DZS Turizam 2025., tab. 2.11) × popunjenost × udio_naselja
  + stanovi_za_odmor_JLS (DZS Popis 2021.)             × osoba_po_stanu × udio_naselja
```

| | opt | sred | pes | izvor |
|---|---|---|---|---|
| popunjenost stalnih postelja | 0,70 | 0,80 | 0,95 | DZS, kolovoz 2025.: odmarališta 70,8 %, kampovi 81,7 %, hoteli 97,3 % |
| osoba po stanu za odmor | 2 | 3 | 4 | **pretpostavka** |

- Tablica 2.11 postoji samo u PDF-u; čita se pdfplumberom grupiranjem riječi po x-koordinati
  (razmak je razdjelnik tisućica). Zbroj ŠKŽ (80.914 stalnih postelja) odgovara retku županije.
- **udio_naselja** = udio OSM turističkih objekata JLS-a (hotel, apartment, guest_house, hostel, camp_site,
  chalet, motel) u poligonu naselja; ako JLS ima < 5 objekata, udio stanovnika (`udio_metoda`).
- Pomoćne postelje, nautički turizam i dnevni posjetitelji **nisu uključeni** (podcjenjuje vršno opterećenje).

## 5. Vrijeme evakuacije (D6)

```
T = (P_iza_reza / osoba_po_vozilu) / Σ kapacitet_bridova_reza
kapacitet brida = protok jedne trake × faktor klase ceste × paralelno
```

| | opt | sred | pes |
|---|---|---|---|
| osoba po vozilu | 3,0 | 2,5 | 2,0 |
| protok jedne trake (voz/h) | 1.300 | 1.000 | 600 |

Izvori protoka: Rohaert, Kuligowski i sur., *Transportation Research Part D* 116 (2023) 103610 (≈ 1.275 voz/h
po traci tijekom evakuacije od požara Kincade 2019.); kalifornijski evakuacijski planovi (1.000 voz/h);
zagušenje ≈ 500 voz/h. Faktor klase: `trunk…tertiary` = 1,0, niže klase 0,6 (**pretpostavka**).
Računa se jedna traka u izlaznom smjeru, bez kontrasmjera. Prikaz je uvijek raspon opt–pes uz središnju vrijednost.

**Validacija**: na uskom grlu prikazuje se izmjereni prosječni ljetni dnevni promet (PLDP) s brojila Hrvatskih
cesta (npr. brojilo 5304 „Murter“ na D121: PLDP 2025. = 5.835 vozila/dan). Brojila nemaju koordinate, pa se
pridružuju po broju ceste i imenu naselja iza reza (ručno nadjačavanje: `data/manual/brojila_hc.csv`).

**Kontrola razumnosti**: T_sred < 5 min ili > 24 h zapisuje se u kvaliteta_podataka.md. Kratka vremena
za vrlo mala sela (< 300 ljudi) su očekivana i navode se zbirno.

## 6. Druga cesta (D7)

Za svako usko grlo s jednim bridom: najkraći put (po duljini) od područja iza reza do sigurne mreže u grafu
{vozive ceste bez reza} ∪ {putovi `highway=track`} (zajednički OSM graf, jer bi zasebno pojednostavljen
graf putova izgubio spojeve s cestama). Rez se uklanja geometrijski (sredina brida unutar 2 m).
Izvoz: duljina, udio puta po `track`, rang = ljudi iza / km. Oznaka: **„kandidat – prohodnost provjeriti na terenu“**.

## 7. Opasnost od požara (D8)

- **Statička**: `H = 0,6·g + 0,4·p` (težine su **pretpostavka**).
  - `g` = udio WorldCover 2021 klasa 10/20/30 (drveće, grmlje, travnjaci) u krugu 2 km, **na kopnenim pikselima**
    (more, klasa 80, se ne broji — inače bi obalna naselja izgledala sigurnije samo zato što je pola kruga more).
    WorldCover se čita izravno iz COG-a na AWS-u, samo prozori oko naselja.
  - `p` = udio kruga od 5 km koji je izgorio barem jednom (unija EFFIS opožarenih površina), min–max normiran.
  - Razredi **nizak / srednji / visok** su tercili unutar pilota — **relativno unutar županije**.
- **Dnevna**: EFFIS Fire Weather Index (sloj `mf010.fwi`; stari `ecmwf007.fwi` više ne postoji). WMS GetMap s
  `format=image/tiff` vraća float32 vrijednosti, koje uzorkujemo u točkama naselja; razredi su iz EFFIS
  legende (GetLegendGraphic): nizak < 11,2; umjeren 11,2–21,3; visok 21,3–38; vrlo visok 38–50;
  ekstreman 50–70; vrlo ekstreman > 70. Na karti se FWI prikazuje i uživo kao WMS sloj.
- **Povijesni dan 13. 8. 2026.** (požar kod Lokve Rogoznice): 174 od 199 naselja ŠKŽ bilo je u razredu
  „ekstreman“ ili „vrlo ekstreman“.
- **Model podložnosti (D11)**: gradient boosting na mreži 250 m za 7 obalnih županija, cilj = EFFIS opožarene
  površine 2000.–danas; prostorna blok-CV (10 km): ROC-AUC 0,776 prema 0,747 za logističku regresiju. Model je
  prošao prag (AUC ≥ 0,70 i bolji od baselinea), pa **u D8 zamjenjuje `p`** prosječnom podložnošću u krugu
  5 km (normiranom). Izmjerena povijest požara i dalje se prikazuje na kartici. Detalji: [evaluacija.md](evaluacija.md).

## 8. Prioritet (D9)

- **A**: (E0 ili E1) i H visok i (E0 ili T_sred ≥ 1 h)
- **B**: (E0 ili E1) i (H srednji ili T_sred > 3 h); ili E2-5 i H visok i T_sred > 3 h
- **C**: ostali E0–E5; **–**: E6+
- Unutar razreda sortira se indeks `iz = 100 · H · f(E) · g(T)`, `f(E0)=1, f(E1)=0,9, f(E2-5)=0,4, f(E6+)=0`,
  `g = min(1, T_sred / 3 h)`, za E0 `g = 1` (**pretpostavka**; služi samo za redoslijed).

**Analiza osjetljivosti**: [osjetljivost.md](osjetljivost.md) — koliko se top-10 mijenja između opt i pes
scenarija i uz druge težine H.

## 9. Ograničenja

- „Sigurno“ = izvan županije ili na autocesti, ne „izvan dosega požara“; požar može zatvoriti i cestu izvan reza.
- OSM može imati pogrešne oznake pristupa ili nedostajuće ceste; HC WFS potvrđuje pokrivenost javnih cesta (99,5 %),
  ali ne i nerazvrstanih.
- Model protoka je statičan (bez dinamike prometa, kontrasmjera, zatvaranja cesta i evakuacije morem).
- Ljetna populacija je procjena po JLS-u raspodijeljena na naselja; stvarni broj gostiju (eVisitor) nije javan.
- Razredi opasnosti su relativni unutar županije; FWI je prognostički indeks na grubljoj mreži (~ 8 km).
- Jadrolinijine linije u `data/manual/trajekti.csv` treba provjeriti prije objave (oznaka N).
