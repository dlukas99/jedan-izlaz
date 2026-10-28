# JEDAN IZLAZ — kontekst projekta (pročitaj prije svakog rada)

> Ova datoteka je „mozak“ projekta i izvor istine za Claude Code.
> Repozitorij: `github.com/dlukas99/jedan-izlaz` (javni; ispravi naziv ako je drukčiji).
> Nakon svakog većeg koraka AŽURIRAJ odjeljke 6 (kvačice), 9 (dnevnik), 10 (otvorena pitanja) i 11 (sljedeći korak).
> Pravila i Javni poziv natječaja imaju prednost pred ovom datotekom.

---

## 1. Što radimo i za koga

Natjecanje je **Datathon Portala otvorenih podataka 2026.** (organizator: Ministarstvo pravosuđa, uprave i digitalne transformacije – MPUDT).
Prijavljujemo **izazov B) Okoliš i održivi prostor**, temu „izloženost poplavama, **požarima** i drugim klimatskim rizicima“.

**JEDAN IZLAZ** je javna web karta. Za svako obalno naselje pokazuje:
1. **koliko izlaznih cestovnih pravaca** ima do sigurne mreže (0 = samo morem, 1 = jedan izlaz … ≥ 6);
2. **gdje je usko grlo** (most, nasip, jedina cesta) i **koliko ljudi ljeti** stoji iza njega;
3. **koliko bi trajala evakuacija cestom**, kao raspon scenarija, nikad kao jedna brojka;
4. **opasnost od požara** oko naselja: statička (gorivo + povijest požara) i dnevna (EFFIS FWI).

Iz toga nastaju **prioritetna lista naselja** kojima treba plan evakuacije (uključujući morem) i **kandidati za „drugu cestu“**.

**Pilot:** Šibensko-kninska županija (ŠKŽ). Proširenje na Splitsko-dalmatinsku i Zadarsku slijedi tek nakon GO odluke 4.11.

**Dokaz problema (PROVJERENO):**
- **Požar kod Lokve Rogoznice (SDŽ), 13.–15.8.2026.** HVZ, ažuriranje 15.8.2026. u 10:00 (https://hvz.gov.hr/vijesti/pozar-kod-lokve-rogoznice-6124/6124):
  - „evakuirano je oko 2500 ljudi“;
  - ozlijeđene su 43 osobe i 3 vatrogasca;
  - „jedna osoba je smrtno stradala“;
  - na požarištu je bilo 253 vatrogasca s 83 vozila, 4 Canadaira CL-415 i 4 Air Tractora;
  - izgorjelo je oko 1.000 ha;
  - prihvatni centri bili su u Omišu, Dugom Ratu, Makarskoj i Splitu, a cesta je bila zatvorena.
- **Fong i sur., PNAS, 1.6.2026., doi:10.1073/pnas.2535081123** (sažetak UCSB-a: https://news.ucsb.edu/2026/022617/six-roads-safety-new-study-finds-critical-threshold-wildfire-survival):
  - analizirano je 342 smrtna slučaja u požarima u SAD-u (2008.–2024.);
  - smrtnost strmo pada s brojem izlaznih cesta do otprilike **6 izlaza**;
  - 17,7 milijuna ljudi živi ispod tog praga;
  - primjeri: Lahaina 2023. (102 poginula, 4 izlaza), Berry Creek 2020. (13 poginulih, 2 izlaza).
  → Naša metrika „broj izlaznih pravaca“ (D4) izravno slijedi tu metodu.

**Persone:**
- **P1 Stožer civilne zaštite obalne JLS:** „Koja naša naselja trebaju plan evakuacije morem i gdje je usko grlo?“
- **P2 Županijski vatrogasni operativni centar (ŽVOC):** „Gdje je danas visok FWI, a iza jednog mosta je 5.000 ljudi?“
- **P3 Izrađivač procjene rizika od velikih nesreća** (nacrt ŠKŽ 2025., Grad Šibenik 2025., Općina Rogoznica 2025., Grad Vodice 2022.): treba podlogu s brojkama i izvorima.
- **P4 (daljnji razvoj) turistička zajednica i gost:** „Ovo mjesto ima jedan izlaz: što učiniti u požaru.“

**Što NIJE:** sustav uzbunjivanja ni prognoza „gdje će izgorjeti“. Na svakom ekranu stoji:
„Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite.“

---

## 2. Rokovi i pravila natječaja

**Prijava tima: do 30.10.2026. u 24:00** (interni cilj je 18:00).
- Prijavljuje se izazov **B**, s nazivom tima i kontaktom mentora.
- Pravila kažu da svaki član ispunjava online obrazac, a objave FESB-a i EFST-a da prijavu podnosi mentor kao voditelj tima. Zato obrazac ispunjavaju **svi članovi i mentor**, a pošalji i upit (odjeljak 10).
- Obrazac uključuje privolu za javnu objavu videa.

**Predaja: do 9.11.2026. u 24:00** (interni cilj je 18:00), samo e-mailom na **open.data@mpudt.hr**. Šalje voditelj tima, ostali su u kopiji. Predaja sadrži:
1. izvorni kod ili poveznicu na javni GitHub repozitorij (objava pod licencom otvorenog koda se boduje);
2. tehničku i projektnu dokumentaciju: arhitekturu i **popis svih skupova podataka s izdavačem i poveznicom**;
3. demo: poveznicu na radni prototip i snimke zaslona;
4. **video do 3:00** koji prikazuje rješenje u primjeni: problem, korisnici, izvori podataka, funkcionalnosti, arhitektura, korisnička vrijednost i daljnji razvoj. **Bez videa nema ocjene.**

**Ostala pravila:**
- Poveznice moraju raditi barem do objave rezultata (17.11.2026.). Naš cilj je do konferencije u Zagrebu, 23.11.2026.
- **Podaci:** obavezni su otvoreni podaci javnog sektora, a prednost ima **data.gov.hr**. Drugi javni izvori dopušteni su ako licenca to dopušta. Izvor se uvijek navodi (NN 67/17).
- **Softver:** rješenje se razvija softverom otvorenog koda. AI alati su dopušteni ako se navedu. **U samom rješenju nema zatvorenih AI API-ja.**

**Bodovanje (najviše 60):**

| Kriterij | Raspon |
|---|---|
| Upotreba otvorenih podataka (izravno putem API-ja ili preuzeto) | 1–5 |
| Povezivanje javno dostupnih podataka (nova vrijednost) | 1–5 |
| Relevantnost za izazov | 1–5 |
| Utjecaj i korist za zajednicu | 1–5 |
| Inovativnost i primjena tehnologija | 1–5 |
| **Izvedivost** (radni prototip, dovršenost) | **1–10** |
| Tehnička arhitektura i integracijski potencijal | 1–5 |
| **Dojam rješenja (UI/UX)** | **1–10** |
| **Prezentacija (video)** | **1–10** |

Kod izjednačenja odlučuje Izvedivost, pa Upotreba otvorenih podataka. Nagrada se ne mora dodijeliti rješenju ispod 50 bodova.

**Posljedice za nas:**
- Izvedivost, UI/UX i video nose **30 od 60 bodova**. Radni prototip i video idu ispred novih značajki, a nakon 6.11. samo poliramo.
- „Upotreba“: podatke s data.gov.hr dohvaćamo **preko CKAN API-ja** (bez hardkodiranih URL-ova resursa). EFFIS se dohvaća **uživo** (WMS/WFS), a HC WFS uživo ako radi. Svaki dohvat upisuje datum u `meta.json`.
- „Povezivanje“: uz svaku brojku na kartici piše iz kojih je izvora nastala.
- „Inovativnost“: oslanja se na algoritme grafa (broj izlaza preko minimalnog reza, prema PNAS 2026.), spajanje 6+ izvora i model podložnosti požaru (D11), ali samo ako model prođe evaluaciju.
- „Arhitektura“:
  - standardi: GeoJSON, OGC WMS/WFS, OpenAPI, DCAT-AP;
  - u dokumentaciji pišemo tehničke, organizacijske i pravne preduvjete.

---

## 3. Podaci

**Legenda:**
- **P** = PROVJERENO (stranica ili metapodaci otvoreni 28.10.2026.).
- **N** = NEPROVJERENO. Prvo ga provjeri `etl/probe.py`, koji spremi sirovi odgovor u `data/raw/<izvor>_probe/`. Tek onda se piše parser. Nakon provjere promijeni N u P i dodaj datum.

### 3.1 data.gov.hr (CKAN API)

API: `https://data.gov.hr/ckan/api/3/action/` s akcijama `package_search?q=…` i `package_show?id=…` (P).
Resurse uvijek razrješavaj preko `package_show`. Pritom spremi `metadata_modified`, `last_modified` i URL resursa u `meta.json`.

| Skup | Izdavač | CKAN / resurs | Licenca | Uloga | Status |
|---|---|---|---|---|---|
| Popis 2021. – stanovništvo (Statistika u nizu) | DZS | skup `statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021` (N, potvrdi slug); resurs „Stanovništvo po naseljima“: `https://podaci.dzs.hr/media/rqybclnx/popis_2021-stanovnistvo_po_naseljima.xlsx` | Otvorena dozvola | **jezgra:** stalno stanovništvo po naselju (+ dob ako postoji) | P (resurs, licenca); N (listovi, stupci, šifre naselja, dobne skupine) |
| Popis 2021. – po gradovima i općinama | DZS | `https://podaci.dzs.hr/media/td3jvrbu/popis_2021-stanovnistvo_po_gradovima_opcinama.xlsx` | Otvorena dozvola | kontrola zbroja | P |
| Popis 2021. – stambene jedinice po gradovima i općinama | DZS | `https://podaci.dzs.hr/media/ryynjuzk/popis-2021-stambene-jedinice-po-gradovima-i-opcinama.xlsx` | Otvorena dozvola | stanovi za odmor (vikendaši), D5 | P (postojanje); N (stupac „za odmor i rekreaciju“) |
| Gradovi i općine u statistici | DZS | `https://podaci.dzs.hr/media/bz5hplcj/gradovi-u-statistici.xlsx` | Otvorena dozvola | plan B za turizam po JLS-u | P (postojanje); N (godina podataka) |
| Brojenje prometa na cestama RH | Hrvatske ceste | ZIP po godini: 2022 `6691c054-924f-4be4-9a64-cedef7240284`, 2023 `881dd770-41df-4d01-a974-8486f7dbb569`, 2024 `c9fc32e6-fb70-4687-b3a7-477209de3803`, 2025 `77fe88a7-5566-48b1-9062-b6061aec3c5c` (objavljen 15.9.2026.) | Otvorena dozvola | **validacija:** PLDP (prosječni ljetni dnevni promet) na uskim grlima | P (skupovi); N (sadržaj ZIP-a) |
| Mreža javnih cesta RH – WMS | HC (harvestano od DGU-a) | `mrea-javnih-cesta-rh-wms` | polje prazno; „nema ograničenja javnom pristupu“ | podloga u dokumentaciji | P (metapodaci) |
| Upravne jedinice – ATOM INSPIRE | DGU | pronađi s `package_search?q=upravne jedinice` | NN 56/2023 | granice JLS-a i naselja | N |

**Format PLDP-a:** HC-ovo izvješće za 2018. (https://hrvatske-ceste.hr/uploads/documents/attachment_file/file/1544/PLDP2018.pdf) sadrži retke „cesta 121 | brojilo 5304 | Murter | PLDP 2018 = 5.193“ i „102 | 2919 | NP Krčki most | 22.364“ (P). Isti oblik očekujemo i u ZIP-ovima za 2022.–2025. (N).

### 3.2 Ostali javni izvori

- **HC – Mreža javnih cesta RH – WFS INSPIRE**
  - NIPP: https://registri.nipp.hr/izvori/1656. Uvjet: „Nema uvjeta za pristup i korištenje“. U NIPP-u od 10.11.2023. (P).
  - `https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs?service=wfs&request=GetCapabilities`
  - Feature typeovi: Road, RoadLink, RoadLinkSequence, RoadNode (P).
  - **N:** imena s namespaceom, atributi (kategorija, oznaka ceste), CRS (vjerojatno EPSG:3765), pokriva li lokalne ceste (ŽUC-ovi upravljaju i njima, pa vjerojatno da) i radi li bez registracije.
  - Uloga: provjera kategorije i oznake ceste (D121…) te sigurne mreže.
- **HAC – autoceste WFS:** `https://geoportal.hac.hr/inspire/tn-ro/wfs?service=WFS&request=GetCapabilities&version=2.0.0` (N).
- **EFFIS (JRC / Copernicus EMS)**
  - Licenca: **CC BY 4.0** (P: https://forest-fire.emergency.copernicus.eu/about-effis/data-license). Navod: „EFFIS – European Forest Fire Information System, Copernicus EMS / JRC“.
  - **WMS (živi API):** `https://maps.effis.emergency.copernicus.eu/effis`, sloj `ecmwf007.fwi`. Parametar `TIME=YYYY-MM-DD` je obavezan, a slojevi su queryable (GetFeatureInfo). Upute: https://forest-fire.emergency.copernicus.eu/downloads-instructions (P).
  - Dodatni slojevi prema GetCapabilities: `ecmwf007.isi`, `.bui`, `.danger_index`, `.ranking` (N).
  - N: razlučivost (~8 km), horizont prognoze, format GetFeatureInfo, vraća li GetMap `image/tiff` vrijednosti ili RGB. **Razrede FWI uzmi iz EFFIS legende (GetLegendGraphic), ne napamet.**
  - **Opožarene površine (WFS → SHAPEZIP, cijela Europa, ~200 MB):** `https://maps.effis.emergency.copernicus.eu/effis?service=WFS&request=getfeature&typename=ms%3Amodis.ba.poly&version=1.1.0&outputformat=SHAPEZIP` (N). Prvo probaj s BBOX-om. Sadrži požare od oko 30–50 ha naviše, od 2000. (N). Atributi (datum, površina, država) su N.
  - **Karta goriva (fuel map):** `https://forest-fire.emergency.copernicus.eu/effis/applications/data-and-services/FuelMap_LAEA.zip` (N).
- **ESA WorldCover 2021 v200** (10 m, CC BY 4.0), za gorivo:
  - klase 10 = drveće, 20 = grmlje, 30 = travnjaci;
  - tile za ŠKŽ je `N42E015`: `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E015_Map.tif` (N, provjeri HEAD-om);
  - navod: „© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021)“.
- **DZS – Turizam u 2025.** (Statistička izvješća 1747/2026; https://podaci.dzs.hr/2026/en/122435)
  - Tablica **2.11**: postelje, dolasci i noćenja po gradovima i općinama, 2025. (P, potvrđeno u sadržaju).
  - Tablica **2.5**: po mjesecima (P).
  - N: postoji li XLSX ili samo PDF. Ako je samo PDF, tablicu izvuci `pdfplumberom` ili ručno u `data/manual/dzs_turizam_2025_t2_11.csv`, s izvorom u prvom retku.
- **DZS – priopćenje za kolovoz 2025.** (https://podaci.dzs.hr/2025/hr/97111, P): bruto popunjenost stalnih postelja je **hoteli 97,3 %, odmarališta i slični objekti 70,8 %, kampovi 81,7 %**.
- **DGU**
  - Pravilnik NN 56/2023 (https://narodne-novine.nn.hr/clanci/sluzbeni/2023_05_56_970.html, P): ponovna uporaba je bez naknade, komercijalna i nekomercijalna. Obavezna je napomena **„Sadrži podatke Državne geodetske uprave“**, uz naziv proizvoda i datum.
  - Upravne jedinice ATOM: `geoportal.dgu.hr/services/atom/au/xml` (~219 MB GML). N: postoji li razina naselja i matični broj naselja.
  - DOF WMS kao podloga karte (N).
- **Eurostat GISCO**
  - Census Grid 2021: mreža 1 km s ukupnim stanovništvom, spolom i dobi (<15 / 15–64 / 65+), verzija od 30.5.2026., na stranici „Population grids“ (N: točan URL i licenca). Uloga: ranjivost (65+) i validacija.
  - NUTS3 `HR034` (Šibensko-kninska, N) i LAU 2021 kao plan B za granice županije i JLS-ova.
- **JRC ENACT-POP 2011** (https://human-settlement.emergency.copernicus.eu/ENACT_POP.php): mjesečne noćne i dnevne populacijske mreže iz 2011. Služi samo za validaciju omjera kolovoz/siječanj (licenca N).
- **DHMZ indeks opasnosti od šumskog požara** (https://meteo.hr/podaci.php?section=podaci_agro&param=pozarind&el=karta): tablica po postajama (FFMC, ISI, BUI, FWI, razred) u sezoni. Stranica je P, strojni format i uvjeti korištenja su N. Uloga: validacija EFFIS-a („Moglo bi“).
- **Jadrolinija** (https://www.jadrolinija.hr/en/travels):
  - linije 505 Šibenik–Zlarin–Prvić Šepurine–Vodice i 532 Šibenik–Zlarin–Obonjan–Kaprije–Žirje (N, provjeri prije videa);
  - službeni GTFS ne postoji, pa se koristi ručni `data/manual/trajekti.csv`.
- **OpenStreetMap** (ODbL 1.0, „© OpenStreetMap contributors“)
  - To je **jedini otvoreni izvor koji sadrži nerazvrstane ceste i šumske puteve**, pa je **jezgra grafa**.
  - Dohvat: OSMnx (Overpass) za poligon ŠKŽ + 15 km. Plan B: Geofabrik `croatia-latest.osm.pbf` + pyosmium.
  - Izvedeni podaci s OSM geometrijom licenciraju se pod ODbL (share-alike).
- **Procjene rizika od velikih nesreća** (kontekst, citati i persona P3):
  - Grad Šibenik 2025.: https://www.sibenik.hr/upload/dokumenti/2025/Procjena%20rizika%20od%20velikih%20nesre%C4%87a%20za%20Grad%20%C5%A0ibenik%202025.pdf
  - Općina Rogoznica: https://rogoznica.hr/wp-content/uploads/2025/11/PRVN-Rogoznica-.pdf
  - Grad Vodice: https://www.grad-vodice.hr/assets/files/civilna-zastita/procjena-rizika-od-velikih-nesreca-grad-vodice.pdf
  - nacrt procjene ŠKŽ 2025. (savjetovanje na sibensko-kninska-zupanija.hr)
- **Srodni rad:** MIRIP (vatra.fesb.hr), mikrolokacijski indeks rizika od požara za Splitsko-dalmatinsku (N, citiraj oprezno). Tvrdnju o novosti formuliraj oprezno: „nismo pronašli kartu naselja s jednim izlazom za RH“.
- **NE koristiti:**
  - DUZS „Evidencija vatrogasnih intervencija“ (izdavač neaktivan, bez licence);
  - GTFS (nije relevantan);
  - **promet-info.hr ne struži**, jer robots.txt zabranjuje.

### 3.3 Ključevi za spajanje

- **Naselja DZS ↔ DGU/OSM:**
  - Ako DZS i DGU imaju **matični broj naselja**, to je ključ (N).
  - Inače se spaja par (JLS, naselje) uz normalizaciju: mala slova; ukloni „Grad“, „Općina“ i zagrade; „Sv.“ → „sveti“; crtice → razmak. Dijakritike uklanjaj **samo za usporedbu**.
  - Neizrazito spajanje: `rapidfuzz.fuzz.token_sort_ratio ≥ 88`, **samo unutar iste JLS**. Ostatak ide u `data/manual/ispravci_naselja.csv`.
  - Obrnuta provjera zapisuje DZS naselja bez točke u `data/interim/dzs_bez_tocke.csv`. Ta datoteka mora biti prazna ili objašnjena.
- **Šifre se uvijek čuvaju kao tekst** (zbog vodećih nula). Šifra ŠKŽ je vjerojatno 15 (N).
- **Naselje ↔ graf:**
  - čvorovi unutar poligona naselja;
  - bez poligona: OSM točka `place=*` i radijus (town 2,5 km, village 700 m, hamlet / isolated_dwelling 300 m), najviše 1 km do najbliže ceste.
- **Turizam:** podaci su po JLS-u (naziv ili šifra), a na naselja se raspodjeljuju prema D5.
- **PLDP:** brojilo HC-a (broj, cesta, naziv) ručno se povezuje s uskim grlom u `data/manual/brojila_hc.csv` (brojilo, cesta, lon, lat, izvor).

---

## 4. Metodološke odluke (mijenjaju se samo uz zapis u odjeljak 9)

- **D1 Opseg i CRS:** pilot je ŠKŽ. Analiza se radi u HTRS96/TM (**EPSG:3765**), a web izlaz je u **EPSG:4326**, s koordinatama na 5 decimala.

- **D2 Graf ceste:**
  - **Glavni graf** su vozive OSM ceste: `motorway, trunk, primary, secondary, tertiary` (+ `_link`), `unclassified, residential, living_street`, te `service` bez `access=private|no`.
  - `highway=track` ide u **zaseban graf**, koji se koristi samo za D7.
  - Trajekti (`route=ferry`) nisu bridovi grafa.
  - OSMnx: `graph_from_polygon(..., custom_filter=..., simplify=True, retain_all=True, truncate_by_edge=True)`. **`retain_all=True` je obavezan**, inače se izgube otočne mreže (Zlarin) i E0 se ne može otkriti.
  - Graf je **neusmjeren**, jer mjerimo povezanost, ne smjer vožnje. MultiGraph se pretvara u Graph, pri čemu broj paralelnih bridova pamtiš u atributu `paralelno`. Brid s `paralelno ≥ 2` nije most, a u D4 v2 mu je kapacitet jednak broju paralelnih bridova.
  - OSM oznaka `bridge=movable` daje atribut `pokretni_most=True` (za Tisno provjeri oznaku u OSM-u).

- **D3 Sigurna mreža:** graf se gradi za poligon ŠKŽ + 15 km.
  - Sigurni čvorovi su čvorovi **izvan poligona ŠKŽ** i čvorovi na **autocesti** (A1).
  - Ograničenje, koje se dokumentira: „sigurno“ znači „izvan županije ili na autocesti“, a ne „izvan dosega požara“.

- **D4 Broj izlaznih pravaca (jezgra metode):**
  - **Jezgra naselja** je komponenta ili skup čvorova s najviše čvorova tog naselja. Slijepe ulice i prilazi kućama ne mijenjaju status naselja.
  - **v1 (Mora):** `nx.bridges` i 2-bridno-povezane komponente daju klase:
    - `E0`: nema cestovnog puta do sigurnih čvorova (izlaz samo morem);
    - `E1`: put postoji, ali svi putovi idu preko mosta grafa;
    - `E2+`: postoji više bridno-disjunktnih putova.
  - **v2 (Mora do 2.11., ako v1 radi):** `e = min(6, broj bridno-disjunktnih putova)` od jezgre naselja do sigurnih čvorova.
    - Graf toka: super-izvor spojen s čvorovima jezgre (velik kapacitet), sigurni čvorovi spojeni sa super-ponorom, bridovi imaju kapacitet 1 (odnosno `paralelno`).
    - `edmonds_karp` ili `shortest_augmenting_path` s `cutoff=6` (provjeri parametar u dokumentaciji networkx-a). Kad tok dosegne 6, naselje je `E6+` i rez se ne računa.
    - Inače se računa `nx.minimum_cut`: **usko grlo** su bridovi minimalnog reza, a „iza reza“ su sva naselja na strani izvora.
    - Razredi: `E0`, `E1`, `E2-5`, `E6+` (prag od otprilike 6 izlaza prema Fong i sur., PNAS 2026.).
  - Očekivano je da će mnogi mali zaseoci biti E1, i to je točno. Prioritet određuje broj ljudi iza reza, a ne sama klasa.

- **D5 Ljetna populacija (3 scenarija):**
  ```
  P = stanovnici_2021
    + postelje_JLS        × popunjenost  × udio_naselja
    + stanovi_za_odmor_JLS × osoba_po_stanu × udio_naselja
  ```
  - **Popunjenost:** opt 0,70 / sred 0,80 / pes 0,95 (DZS, kolovoz 2025.: odmarališta 70,8 %, kampovi 81,7 %, hoteli 97,3 %). „Pesimistično“ znači više ljudi.
  - **osoba_po_stanu** za stanove za odmor: 2 / 3 / 4. Ovo je **PRETPOSTAVKA** i ulazi u analizu osjetljivosti. Komponenta se koristi samo ako probe potvrdi stupac.
  - **udio_naselja:** prema broju OSM objekata `tourism=hotel|apartment|guest_house|hostel|camp_site|chalet` u naselju. Ako ih u JLS-u ima manje od 5, koristi se udio stanovnika. U izlaz se uvijek zapisuje `udio_metoda`.
  - **Ograničenje:** nautički turizam i dnevni posjetitelji nisu uključeni.

- **D6 Vrijeme evakuacije (raspon, ne točka):**
  ```
  T = (P_iza_reza / osoba_po_vozilu) / Σ kapacitet_bridova_reza
  ```
  - opt: 3,0 osobe/vozilu i 1.300 voz/h po traci; sred: 2,5 i 1.000; pes: 2,0 i 600.
  - Izvori konstanti (citate provjeri prije dokumentacije):
    - Rohaert, Kuligowski i sur., *Transportation Research Part D* 116 (2023) 103610: tijekom evakuacije od požara Kincade 2019. izmjereno je oko 1.275 voz/h po traci;
    - evakuacijski planovi u Kaliforniji računaju s 1.000 voz/h;
    - zagušenje može spustiti protok na oko 500 voz/h po traci.
  - Računa se jedna traka u izlaznom smjeru, bez kontrasmjera.
  - Faktor klase ceste: `trunk/primary/secondary/tertiary` = 1,0; `unclassified/residential/service` = 0,6 (**PRETPOSTAVKA**, analiza osjetljivosti).
  - Prikaz: „1,2–4,8 h (središnje 2,4 h)“. T se računa za E1 i E2-5. Za E0 se prikazuje „izlaz morem“ i trajektna linija.
  - **Kontrola razumnosti:** ako je središnji T kraći od 5 minuta ili dulji od 24 sata, zapiši slučaj u `docs/kvaliteta_podataka.md` i provjeri ga ručno.
  - **Validacija:** PLDP s HC-ova brojila na uskom grlu (npr. 5304 Murter) prikazuje se na kartici kao „izmjereni ljetni promet“.

- **D7 Druga cesta:** za svako usko grlo E1 traži se najkraći put od jezgre do sigurne mreže u grafu {glavni graf bez bridova reza} ∪ {graf putova `track`}.
  - Izvoz: duljina u km i udio puta po `track`.
  - Rang = `P_iza_reza / duljina_km`.
  - Oznaka: „kandidat – prohodnost provjeriti na terenu“.

- **D8 Opasnost od požara:**
  - **Statička:** `H_stat = 0,6·g + 0,4·p`.
    - `g` je udio WorldCover klasa 10, 20 i 30 u krugu od 2 km oko jezgre naselja.
    - `p` je udio površine opožarene u EFFIS-u (2000.–danas) u krugu od 5 km, min–max normaliziran unutar pilota.
    - Težine 0,6 i 0,4 su **PRETPOSTAVKA** i ulaze u analizu osjetljivosti.
  - **Razredi H** su tercili unutar pilota (nizak, srednji, visok), uvijek uz napomenu „relativno unutar županije“.
  - **Dnevna:** EFFIS FWI za centroid naselja, kao zaseban sloj, prikazan u razredima iz EFFIS legende.
  - **Povijesni dan** `TIME=2026-08-13` je dan požara kod Lokve Rogoznice. U studenom je FWI svugdje nizak, pa bez povijesnog dana demo ne bi ništa pokazao.

- **D9 Prioritet (razredi, ne decimalni indeks):**
  - **A:** (E0 ili E1) i H visok i (E0 ili T_sred ≥ 1 h).
  - **B:** (E0 ili E1) i (H srednji ili T_sred > 3 h); ili E2-5 i H visok i T_sred > 3 h.
  - **C:** ostali E0–E5.
  - **–:** E6+.
  - Numerički `iz` (0–100) služi **samo za sortiranje** unutar razreda: `iz = 100 · H_stat · f(E) · g(T)`, uz `f(E0)=1, f(E1)=0,9, f(E2-5)=0,4, f(E6+)=0` i `g = min(1, T_sred/3 h)` (za E0 je `g = 1`). Ovo je **PRETPOSTAVKA**.
  - Analiza osjetljivosti ide u `docs/metodologija.md`: koliko se top-10 mijenja između opt i pes scenarija.

- **D10 Pokretni most Tisno:**
  - TZ Tisno (https://www.tz-tisno.hr/hr/planiranje-putovanja/korisne-informacije/raspored-dizanja-mosta/, P, ali stranica nema godinu):
    - ljeto (1.6.–15.9.): svaki dan 18:00–18:20;
    - zima (16.9.–31.5.): ponedjeljkom i petkom 09:00–09:20.
  - Istraživanje navodi i dodatno ljetno podizanje u 9:00 prema objavi Općine Tisno od 29.5.2026. To je N, provjeri na tisno.hr.
  - Prvotna tvrdnja „dvaput po 30 minuta“ je netočna.
  - Raspored se prikazuje kao napomena na kartici, a ne ulazi u formulu.

- **D11 ML, model podložnosti požaru („Trebalo bi“, paralelna grana):**
  - **Cilj:** opožareno da/ne (EFFIS, 2000.–2025.) na mreži od 250 m za **svih 7 obalnih županija**, jer jedna županija ima premalo događaja.
  - **Značajke:**
    - udjeli WorldCover klasa;
    - nagib i ekspozicija (DEM iz DGU-a ili Copernicus GLO-30, licenca N);
    - udaljenost do ceste i naselja (OSM);
    - udaljenost do obale.
  - **Modeli:** logistička regresija (baseline) i gradient boosting (HistGradientBoosting ili LightGBM).
  - **Evaluacija:** prostorna blok-CV s blokovima od 10 km, ROC-AUC, PR-AUC i kalibracija.
  - Model zamjenjuje `p` u D8 **samo ako** je AUC ≥ 0,70 i bolji od baselinea. U svakom slučaju rezultat iskreno upisujemo u `docs/evaluacija.md`.

- **D12 Privatnost:** nema osobnih podataka. Koriste se samo javni podaci o cestama te agregati stanovništva i turizma.

---

## 5. Arhitektura

```
IZVORI                                  PIPELINE (Python, etl/)                      IZLAZ                          KORISNICI
data.gov.hr CKAN API (DZS, HC) ──┐      probe → load_* → match_settlements           web/public/data/*.geojson      karta (GitHub Pages):
EFFIS WMS/WFS (uživo) ───────────┼────► → graph_egress → population → evac_time ───► meta.json, kpi.json,      ───► stožeri CZ, ŽVOC,
HC / HAC WFS (INSPIRE TN) ───────┤      → second_road → hazard → priority             fwi_today.json                 izrađivači procjena
DGU ATOM, OSM, WorldCover ───────┘      → (ml_susceptibility) → export                docs/izvori.md (generirano)    rizika
                                        GitHub Actions: tests · noćni FWI · deploy Pages
```

- **Bez PostGIS-a i bez poslužitelja.** Web čita samo statične datoteke iz `web/public/data/`.
- **Python 3.12:** pandas, geopandas, pyogrio, shapely, pyproj, osmnx, networkx, rasterio, numpy, requests, owslib, openpyxl, pdfplumber, rapidfuzz, pytest; za D11 još scikit-learn i lightgbm. Na Windowsu se instalira preko pip wheelova. Ako `rasterio` ili `pyogrio` zapnu, prijeđi na conda-forge.
- **Web:**
  - Vite + React + TypeScript + MapLibre GL JS.
  - Podloga je otvoreni vektorski stil (npr. OpenFreeMap, N) uz atribuciju. Opcija je DGU DOF WMS (N).
- **GitHub Actions:**
  - `tests.yml`: pytest na sintetičkim podacima, bez mreže;
  - `nightly_fwi.yml`: cron dohvaća EFFIS FWI i commita `fwi_today.json`;
  - `pages.yml`: build weba i deploy na Pages.
  - Ograničenja Pagesa prema GitHub Docs: stranica do 1 GB, meki limit od 100 GB prometa mjesečno.
- **Interoperabilnost:**
  - GeoJSON (RFC 7946).
  - `docs/openapi.yaml` opisuje statičke krajnje točke (`/data/settlements.geojson`, `/data/bottlenecks.geojson`, `/data/meta.json`) i budući OGC API Features (pygeoapi).
  - `docs/dcat-ap.jsonld` opisuje izvedeni skup „Izloženost naselja s ograničenim cestovnim izlazom“, spreman za objavu na data.gov.hr.
  - Ulazni podaci dolaze iz INSPIRE tema TN (HC) i AU (DGU).
- **Integracija (za kriterij Arhitektura):**
  - podloga za procjene rizika od velikih nesreća JLS-ova i županija;
  - ŽVOC (dnevni FWI × broj izlaza);
  - Ravnateljstvo civilne zaštite MUP-a;
  - objava izvedenog skupa na data.gov.hr i NIPP-u;
  - daljnji razvoj: sustav 112, e-Građani, eVisitor (populacija u stvarnom vremenu, uz sporazum).
- **Preduvjeti:**
  - *tehnički:* dostupnost WFS/WMS servisa i noćni job;
  - *organizacijski:* tko održava alat (županija ili civilna zaštita) i tko na terenu potvrđuje „drugu cestu“;
  - *pravni:* licence (Otvorena dozvola, CC BY 4.0, ODbL share-alike za izvedene podatke s OSM geometrijom, napomena DGU-a), odricanje odgovornosti i bez osobnih podataka.
- **Licence:** kod je pod **EUPL-1.2**, a izvedeni podaci s OSM geometrijom pod **ODbL**.

### 5.1 Struktura repozitorija

```
jedan-izlaz/
├─ CLAUDE.md   README.md   LICENSE (EUPL-1.2, službeni tekst)   .gitignore
├─ etl/
│  ├─ __init__.py
│  ├─ config.py             # sve konstante D1–D12, svaka s "# izvor: …" ili "# PRETPOSTAVKA: …"
│  ├─ http.py               # Session, User-Agent, timeout, retry, cache u data/raw/
│  ├─ ckan.py               # razrješavanje resursa preko data.gov.hr CKAN API-ja + metapodaci
│  ├─ probe.py              # provjera svih izvora → docs/probe_report.md
│  ├─ load_osm.py  load_dzs.py  load_hc.py  load_effis.py  load_dgu.py  load_worldcover.py
│  ├─ match_settlements.py
│  ├─ graph_egress.py       # D2–D4
│  ├─ population.py         # D5
│  ├─ evac_time.py          # D6
│  ├─ second_road.py        # D7
│  ├─ hazard.py             # D8
│  ├─ priority.py           # D9
│  ├─ ml_susceptibility.py  # D11 (Trebalo bi)
│  ├─ fwi_today.py          # noćni job
│  ├─ mock.py               # podaci po shemi 5.2, s oznakom "nacin": "mock"
│  ├─ export.py             # GeoJSON + meta.json + kpi.json + docs/izvori.md
│  ├─ pipeline.py           # python -m etl.pipeline --county SKZ --mode live|cache|mock
│  └─ requirements.txt
├─ data/
│  ├─ raw/        # .gitignore – sirovi odgovori, preuzimanja
│  ├─ interim/    # .gitignore – međurezultati, cache OSMnx-a
│  └─ manual/     # u gitu – ručni CSV-ovi, izvor u prvom retku
├─ web/           # Vite + React + TS + MapLibre; public/data/ generira pipeline
├─ tests/
│  ├─ test_graph_egress.py  # sintetički: most → E1, dva mosta → E2-5, trajekt → E0, slijepa ulica ne mijenja status
│  ├─ test_population.py  test_evac_time.py  test_priority.py
│  └─ test_cases_real.py    # Murter E1, Zlarin/Prvić/Krapanj E0 (preskače se ako nema podataka)
├─ docs/   probe_report.md  izvori.md  arhitektura.md  metodologija.md  evaluacija.md
│          kvaliteta_podataka.md  openapi.yaml  dcat-ap.jsonld  video_scenarij.md  predaja.md
└─ .github/workflows/  tests.yml  nightly_fwi.yml  pages.yml
```

`.gitignore` obuhvaća: `.venv/`, `__pycache__/`, `data/raw/`, `data/interim/`, `cache/`, `node_modules/`, `web/dist/`, `.vscode/`, `.env`, `*.pyc`.

### 5.2 Shema izlaza (v1; mijenja se samo uz zapis u dnevnik)

**`settlements.geojson`** (Point, EPSG:4326). Svojstva:
- `id` (tekst: matični broj naselja ili `osm:<id>`), `naziv`, `jls`, `zupanija`;
- `stanovnici_2021`, `postelje_jls`, `p_ljeto: {opt, sred, pes}`, `udio_metoda`;
- `izlazi_e` (0–6, gdje 6 znači ≥ 6), `klasa_izlaza` (`E0` | `E1` | `E2-5` | `E6+`);
- `usko_grlo_id`, `ljudi_iza_reza: {opt, sred, pes}`, `t_evak_h: {opt, sred, pes}` (null za E0 i E6+);
- `pokretni_most` (bool), `trajektna_linija` (tekst ili null);
- `h_stat` (0–1), `h_razred`, `prioritet` (`A` | `B` | `C` | `-`), `iz` (0–100);
- `druga_cesta_km` (ili null), `napomene` [tekst], `izvori` [ključevi iz `meta.json`].

**`bottlenecks.geojson`** (LineString). Svojstva:
- `id`, `cesta_ref`, `naziv`, `pokretni_most`;
- `kapacitet_voz_h: {opt, sred, pes}`, `ljudi_iza: {…}`, `t_evak_h: {…}`;
- `naselja_iza` [id], `pldp: {godina, vrijednost, brojilo}` (ili null).

**`meta.json`:**
- `generirano`, `nacin` (`live` | `cache` | `mock`), `scenariji` (sve konstante);
- `izvori`: [{`kljuc`, `naziv`, `izdavac`, `url`, `licenca`, `navod`, `dohvaceno`, `metadata_modified`}];
- `odricanje`.

**Ostale datoteke:**
- **`kpi.json`** (za video i dokumentaciju): broj naselja po klasi, ljudi ljeti iza E0 i E1 (raspon), top-10 po prioritetu, datum.
- **`fwi_today.json`** / **`fwi_2026-08-13.json`**: `{datum, sloj, vrijednosti: {id: fwi}}`.

**Mock pravilo:** mock podaci imaju `"nacin": "mock"`, a UI tada prikazuje crvenu traku „MOCK“. Mock se nikad ne pojavljuje u videu ni u predaji.

---

## 6. Opseg MVP-a i ekrani

**Mora (do 4.11.):**
- [ ] `probe.py` i `docs/probe_report.md` (svi izvori iz odjeljka 3)
- [ ] mock podaci po shemi 5.2 (da web može raditi od prvog dana)
- [ ] OSM graf ŠKŽ + D4 v1 (mostovi grafa); test: Murter je E1, Zlarin i Prvić su E0
- [ ] D4 v2: broj izlaza preko minimalnog reza
- [ ] spajanje naselja ≥ 95 % (ostatak u ručnom CSV-u)
- [ ] D5 ljetna populacija (3 scenarija) i D6 vrijeme evakuacije (raspon)
- [ ] D8 statička opasnost i D9 prioritet
- [ ] export + karta + kartica naselja + prioritetna lista + stranica izvora + odricanje
- [ ] GitHub Pages deploy, `tests.yml` zelen
- [ ] `docs/izvori.md` generiran iz `meta.json`

**Trebalo bi (5.–6.11.):**
- [ ] noćni EFFIS FWI + povijesni dan 13.8.2026.
- [ ] D7 druga cesta
- [ ] PLDP na karticama uskih grla
- [ ] D11 model podložnosti (samo ako prođe evaluaciju)
- [ ] Splitsko-dalmatinska (ako je GO): Čiovo kao kontrola E2-5 (drugi most iz 2018.), Lokva Rogoznica

**Moglo bi:**
- [ ] Zadarska (Vir)
- [ ] EN prijevod
- [ ] DHMZ validacija FWI-ja
- [ ] QR stranica za goste (makete u videu)
- [ ] pygeoapi konfiguracija

**Ne ovaj put:** dnevni ML model izbijanja požara, eVisitor, sustav 112, PostGIS, svih 7 županija na karti.

**Ekrani:**
1. **Karta:**
   - naselja obojena po prioritetu, uz oznaku ili oblik (boja nikad sama ne nosi značenje);
   - uska grla prikazana kao deblje linije;
   - prekidač scenarija opt / sred / pes;
   - slojevi: FWI danas, FWI 13.8.2026., opožarene površine, gorivo.
2. **Kartica naselja (klik):**
   - broj izlaza i klasa;
   - usko grlo (pokretni most i raspored dizanja);
   - ljudi ljeti i vrijeme evakuacije (rasponi);
   - opasnost (razred + FWI);
   - druga cesta;
   - izvor uz svaku brojku;
   - odricanje.
3. **Prioritetna lista:** tablica sa sortiranjem i filtrom po JLS-u, uz izvoz u CSV (za P1 i P3).
4. **Izvori i metoda:** iz `meta.json` (izvor, izdavač, licenca, datum dohvata), uz formule i konstante.

Zahtjevi za sve ekrane: rad na mobitelu, WCAG 2.1 AA, tekstovi na hrvatskom.

---

## 7. Plan po danima i GO/NO-GO

**Uloge:**
- **PA:** podaci i analiza;
- **WEB:** karta i UX;
- **VID:** video, dokumentacija i testiranje s korisnicima;
- **M:** mentor.

| Datum | PA | WEB | VID | M |
|---|---|---|---|---|
| Sri 28.10. | repo, CLAUDE.md, venv | kostur Vite | – | upit Organizatoru (odj. 10) |
| Čet 29.10. | **probe.py + probe_report**, ažuriraj odj. 3 | mock podaci → karta | scenarij videa v0; kontakt CZ/vatrogasci | dogovor izjave stručnjaka |
| Pet 30.10. | OSM graf + D4 v1; test Murter | kartica na mocku | – | **prijava svih do 18:00** |
| Sub 31.10. | spajanje naselja, DZS, turizam; (D11 start) | prioritetna lista | – | – |
| Ned 1.11. | Svi sveti: lagano, testovi | – | – | – |
| Pon 2.11. | D5 + D6 + D4 v2 | pravi podaci umjesto mocka | snimke zaslona v0 | – |
| Uto 3.11. | D8 + D9 | slojevi, prekidač scenarija | test s 2–3 korisnika | – |
| Sri 4.11. | **sve radi s kraja na kraj** + Pages; **GO/NO-GO** | deploy, mobitel | – | pregled brojki |
| Čet 5.11. | noćni FWI, povijesni dan, D7; (GO → SDŽ) | UX popravci, pristupačnost | tekst za glas | – |
| Pet 6.11. | **feature freeze**; D11 → `evaluacija.md` | poliranje | snimanje zaslona | pregled |
| Sub 7.11. | dokumentacija: arhitektura, metodologija, izvori, OpenAPI, DCAT-AP | README, snimke | glas + montaža v1 | pregled videa v1 |
| Ned 8.11. | proba predaje iz čistog klona | provjera s drugog uređaja | video v2 ≤ 2:55, unlisted + rezerva | – |
| Pon 9.11. | tag `v1.0-predaja` | – | provjera poveznica | **slanje do 18:00** |

**Kontrolna točka 30.10.:** OSM graf mora otkriti Murter kao E1, a DZS XLSX mora biti čitljiv. Ako graf ne radi, prijeđi na Geofabrik PBF. Ako XLSX ne radi, koristi ručni CSV za pilot.

**GO/NO-GO 4.11.:**
- **GO** ako su sve kvačice „Mora“ zelene, testovi prolaze, a demo na Pagesu radi u anonimnom prozoru i na mobitelu. Tada 5.11. slijedi proširenje na SDŽ i FWI.
- **NO-GO** znači samo poliranje ŠKŽ.

---

## 8. Pravila rada za Claude Code

1. **Na početku sesije** pročitaj ovu datoteku i `git log -10`, pa reci gdje smo u odnosu na odjeljke 6, 7 i 11.
2. **Radi u malim koracima:** jedan modul ili funkcija po koraku. Nakon svakog koraka pokreni kod i `pytest -q`, pokaži rezultat i commitaj.
3. **Ne izmišljaj** endpointe, nazive stupaca, atribute ni brojke. Za sve označeno s N prvo napiši probe, spremi sirovi odgovor u `data/raw/<izvor>_probe/`, a tek onda parser. Zatim u odjeljku 3 promijeni N u P i dodaj datum.
4. **Konstante** idu isključivo u `etl/config.py`, svaka s komentarom `# izvor: …` ili `# PRETPOSTAVKA: …`.
5. **Mreža:**
   - `requests.Session` s User-Agentom `JedanIzlaz/0.1 (studentski projekt, Datathon 2026)`;
   - timeout 60 s, 3 pokušaja s backoffom, cache u `data/raw/`;
   - najviše 2 zahtjeva u sekundi prema istom servisu;
   - poštuj robots.txt i uvjete korištenja (promet-info.hr se ne struže);
   - preuzimanja veća od 100 MB samo uz potvrdu tima.
6. **Tajne:** nisu potrebne, jer su svi izvori otvoreni. Ako se ipak pojave, idu u `.env` i nikad u git.
7. **Ne commitaj** `data/raw/`, `data/interim/` ni datoteke veće od 50 MB. Prije svakog commita provjeri `git diff --staged`.
8. **Windows / PowerShell:**
   - okruženje: `python -m venv .venv` pa `.\.venv\Scripts\Activate.ps1`;
   - putanje preko `pathlib`;
   - uvijek `encoding="utf-8"`;
   - CSV-ovi s `newline=""`.
9. **Komentari i docstringovi** pišu se na hrvatskom i objašnjavaju *zašto*, jer tim kod uči naknadno. Uz veće module dodaj kratak tekst „kako ovo radi“ u `docs/`.
10. **Commit poruke** pišu se na hrvatskom, u imperativu, npr. „Dodaj izračun minimalnog reza“.
11. **U rješenju nema zatvorenih AI API-ja.** AI alate korištene u razvoju (Claude Code) navodimo u README-u.
12. **UI:**
    - tekstovi na hrvatskom;
    - odricanje odgovornosti na svakom ekranu;
    - brojke uvijek kao rasponi uz izvor;
    - boja nikad sama ne nosi značenje.
13. **Opseg:** ne dodaji značajke izvan odjeljka 6 bez dogovora. Nakon 6.11. dopušteni su samo popravci.
14. **Na kraju sesije** ažuriraj odjeljke 6, 9, 10 i 11, commitaj i pushaj, pa timu napiši kratak sažetak na hrvatskom.

**Naredbe:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r etl/requirements.txt
python -m etl.probe
python -m etl.pipeline --county SKZ --mode live
pytest -q
cd web; npm install; npm run dev
```

---

## 9. Dnevnik odluka

- 27.10. Odbačen je NišaRadar (izazov C). Obrti nisu u Sudskom registru, pa bi alat u malim općinama pokazivao „nedostaje“ tamo gdje je tržište puno.
- 28.10. Odabran je JEDAN IZLAZ u izazovu B, s pilotom u ŠKŽ.
- 28.10. PostGIS je izbačen; koristimo statični GeoJSON i GitHub Pages.
- 28.10. Popunjenost od 80 % zamijenjena je scenarijima 0,70 / 0,80 / 0,95 (DZS, kolovoz 2025.).
- 28.10. Uz mostove grafa uvedena je metrika broja izlaznih pravaca do 6 (PNAS 2026.).
- 28.10. Prioritet se prikazuje u razredima A/B/C, a T i P kao rasponi.
- 28.10. Podaci s data.gov.hr dohvaćaju se preko CKAN API-ja; PLDP Hrvatskih cesta služi za validaciju.
- 28.10. Raspored Tisna („2 × 30 min“) ispravljen je prema TZ Tisno (D10).
- 28.10. Kod je pod EUPL-1.2, a izvedeni podaci pod ODbL.

---

## 10. Otvorena pitanja / NEPROVJERENO

**Upit Organizatoru** (open.data@mpudt.hr, poslati 29.10.):
- [ ] Tko ispunjava prijavni obrazac: svaki član ili mentor?
- [ ] „Konačni broj bodova = zbroj bodova članova Povjerenstva“: odnosi li se prag od 50 bodova na prosjek po članu?
- [ ] Je li video prihvatljiv kao unlisted YouTube poveznica?

**Podaci (provjerava probe):**
- [ ] DZS po naseljima: listovi, stupci, šifre naselja, dobne skupine
- [ ] DZS stambene jedinice: stupac sa stanovima za odmor
- [ ] DZS tablica 2.11: XLSX ili PDF
- [ ] HC brojenje (ZIP): PLDP, brojila, lokacije
- [ ] HC WFS: radi li bez registracije, atributi, lokalne ceste, CRS
- [ ] HAC WFS
- [ ] EFFIS: format GetFeatureInfo, GeoTIFF s vrijednostima ili RGB, horizont prognoze, BA s BBOX-om, atributi, legenda FWI-ja
- [ ] DGU ATOM: razina naselja, matični broj naselja
- [ ] URL WorldCover tilea
- [ ] OSM: Tisno `bridge=movable`, Krapanj, oznake `access` na putevima
- [ ] Broj naselja u ŠKŽ (~200?)
- [ ] Jadrolinija: linije 505 i 532
- [ ] Tisno: podizanje u 9:00 ljeti 2026. (Općina Tisno)
- [ ] Citat Kincade (TR-D 2023) i vrijednost od oko 500 voz/h
- [ ] Licence: Eurostat grid, ENACT, DEM
- [ ] Podloga karte (OpenFreeMap ili DGU DOF)

**Tim:**
- [ ] Svi članovi i mentor prijavljeni do 30.10. u 18:00
- [ ] Izjava stručnjaka (CZ ili vatrogasci) za video (opcionalno)

---

## 11. Sljedeći korak (prvi zadatak za Claude Code)

> Pročitaj CLAUDE.md. Napravi kostur repozitorija prema 5.1:
> - `.gitignore`;
> - `LICENSE` sa **službenim tekstom EUPL-1.2** (preuzmi s joinup.ec.europa.eu ili eur-lex; ne piši po sjećanju);
> - README;
> - `etl/requirements.txt`, `etl/http.py`, `etl/ckan.py`;
> - venv.
>
> Zatim napiši `etl/probe.py`. Za svaki izvor sprema sirovi odgovor u `data/raw/<izvor>_probe/` i piše `docs/probe_report.md` (izvor, URL, HTTP kod, veličina, što je pronađeno, OK/GREŠKA):
> 1. **CKAN:** `package_show` / `package_search` za DZS Popis (stanovništvo i stambene jedinice), HC brojenje 2025. i DGU upravne jedinice.
>    - Raspakiraj ZIP HC-a, ispiši datoteke i zaglavlja te potraži „PLDP“ i „Murter“.
> 2. **DZS XLSX po naseljima:** listovi, prvih 15 redaka i gdje je Šibensko-kninska.
> 3. **HC WFS:**
>    - GetCapabilities;
>    - DescribeFeatureType za RoadLink;
>    - GetFeature s count=5 u bboxu oko Tisna.
> 4. **HAC WFS:** GetCapabilities.
> 5. **EFFIS WMS:**
>    - GetCapabilities (spremi popis slojeva i TIME dimenzije);
>    - GetFeatureInfo `ecmwf007.fwi` za točku Murter (približno 15,59 E, 43,82 N, provjeri) za TIME=danas i TIME=2026-08-13;
>    - GetMap `image/tiff` za bbox ŠKŽ: provjeri vraća li vrijednosti ili RGB.
> 6. **EFFIS opožarene površine:** WFS s BBOX-om za ŠKŽ. Ako ne radi, samo zabilježi; bez preuzimanja cijelog ZIP-a.
> 7. **WorldCover:** HEAD zahtjev za tile N42E015.
> 8. **OSMnx:** mali graf otoka Murter s Tisnom (`retain_all=True`):
>    - `nx.bridges`;
>    - ispiši je li cesta preko mosta u Tisnom most grafa i ima li `bridge=movable`.
>
> Bez pretpostavki o stupcima. Komentari na hrvatskom. Na kraju predloži izmjene odjeljka 3 (N → P), ažuriraj odjeljke 9–11, commitaj i pushaj.

---

## 12. Scenarij videa (cilj 2:50, nikad preko 3:00)

| Vrijeme | Sadržaj | Element kriterija |
|---|---|---|
| 0:00–0:20 | Lokva Rogoznica, kolovoz 2026. (HVZ): oko 2.500 evakuiranih, 43 ozlijeđena, 1 smrtno stradala osoba. „Koliko naših obalnih naselja ima samo jedan izlaz?“ | problem |
| 0:20–0:35 | stožeri CZ, ŽVOC, izrađivači procjena rizika | ciljni korisnici |
| 0:35–1:00 | izvori i način spajanja: DZS i HC (data.gov.hr API), DGU, EFFIS (uživo), OSM, WorldCover | skupovi podataka |
| 1:00–1:55 | **demo:** karta ŠKŽ → Murter (E1, most Tisno, ljudi ljeti, T kao raspon, PLDP) → Zlarin (E0, trajektna linija) → povijesni dan 13.8.2026. → prioritetna lista → druga cesta | funkcionalnosti, rješenje u primjeni |
| 1:55–2:20 | pipeline → GeoJSON → Pages; noćni EFFIS; broj izlaza preko minimalnog reza (PNAS: prag oko 6 izlaza); GeoJSON / OGC / OpenAPI / DCAT-AP | arhitektura i tehnički pristup |
| 2:20–2:40 | brojke iz `kpi.json`: [N] naselja s jednim izlazom, [M] ljudi ljeti iza jednog izlaza | korisnička vrijednost |
| 2:40–2:50 | sve obalne županije, OGC API, objava na data.gov.hr, eVisitor i 112; odricanje odgovornosti | daljnji razvoj |

Brojke u videu moraju biti jednake `kpi.json` na dan zamrzavanja (6.11.).

---

## 13. Kontrolna lista predaje

- [ ] Javni repozitorij s `LICENSE` (EUPL-1.2) i README-om: što je projekt, pokretanje u 3 naredbe, izvori, korišteni AI alati.
- [ ] `docs/izvori.md` (generiran): za svaki skup naziv, izdavač, poveznica, licenca i datum dohvata; napomena „Sadrži podatke Državne geodetske uprave“; „© OpenStreetMap contributors“; navodi za EFFIS i ESA.
- [ ] Dokumentacija (PDF + md):
  - problem i korisnici;
  - arhitektura (dijagram);
  - metodologija s konstantama i izvorima;
  - validacija (Murter, Zlarin, Prvić, Krapanj) i evaluacija (D11);
  - ograničenja;
  - tehnički, organizacijski i pravni preduvjeti.
- [ ] `meta.json` ima `"nacin": "live"`; nigdje nema MOCK-a.
- [ ] Noćni job prošao je barem jednom, a testovi su zeleni.
- [ ] Demo radi u anonimnom prozoru i na mobitelu.
- [ ] Priloženo je 5–8 snimaka zaslona.
- [ ] Video traje najviše 3:00, pokriva svih 7 elemenata i prikazuje rješenje u primjeni. Poveznica radi bez prijave, a postoji i rezervna.
- [ ] E-mail na open.data@mpudt.hr s naslovom „Datathon 2026 – izazov B – JEDAN IZLAZ – [naziv tima]“ šalje voditelj tima, ostali su u kopiji. **Poslano 9.11. do 18:00.**
- [ ] Sve poveznice rade do 23.11.2026., a predano stanje označeno je tagom `v1.0-predaja`.