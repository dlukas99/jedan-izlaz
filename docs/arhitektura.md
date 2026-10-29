# Arhitektura

```
IZVORI                                   PIPELINE (Python 3.12, etl/)                 IZLAZ (statične datoteke)        KORISNICI
data.gov.hr CKAN API ─┬─ DZS Popis 2021  probe → load_dzs / load_dgu / load_osm        web/public/data/                 karta (GitHub Pages)
                      ├─ DZS stanovi     → match_settlements (DZS↔DGU↔RGI)             settlements.geojson              · stožeri civilne zaštite JLS
                      ├─ HC brojenje     → graph_egress (D3–D4, minimalni rez)  ─────► bottlenecks.geojson     ──────► · ŽVOC
                      └─ DGU AU (ATOM)   → population (D5) → evac_time (D6)            second_roads.geojson             · izrađivači procjena rizika
DGU RGI WFS ──────────────────────────── → second_road (D7) → hazard (D8)              burned.geojson                   · CSV izvoz prioriteta
HC INSPIRE WFS (validacija) ──────────── → priority (D9) → (ml_susceptibility D11)     meta.json · kpi.json
EFFIS WMS/WFS (uživo) ────────────────── → export                                       fwi_today.json · fwi_2026-08-13.json
OSM (Geofabrik PBF), ESA WorldCover COG                                                 docs/izvori.md (generirano)
DZS Turizam 2025 (PDF)                   GitHub Actions: tests · nightly_fwi · pages    EFFIS WMS izravno u pregledniku (FWI, gorivo)
```

## Načela

- **Bez poslužitelja i baze.** Pipeline jednom proizvede statični GeoJSON/JSON; web (Vite + React + TypeScript +
  MapLibre GL JS) ga čita s GitHub Pagesa. Održavanje = ponovno pokretanje pipelinea.
- **Živi API-ji gdje je to smisleno.** data.gov.hr resursi razrješavaju se preko CKAN `package_show`
  (nema hardkodiranih URL-ova resursa); EFFIS FWI dohvaća se svaku noć (GitHub Actions) i uživo u pregledniku
  (WMS sloj); HC WFS i DGU RGI WFS koriste se izravno.
- **Ponovljivost.** Svi sirovi odgovori spremaju se u `data/raw/` uz `.meta.json` (URL, vrijeme, Last-Modified);
  `meta.json` nosi datum dohvata svakog izvora. `python -m etl.probe` provjerava sve izvore prije parsiranja.
- **Mreža prema tuđim servisima**: User-Agent projekta, najviše 2 zahtjeva u sekundi po poslužitelju,
  3 pokušaja s backoffom, cache. Javni Overpass je 28.10.2026. bio preopterećen, pa se OSM čita iz Geofabrik PBF-a.

## Moduli (etl/)

| Modul | Uloga |
|---|---|
| `config.py` | sve konstante D1–D12 s izvorom ili oznakom pretpostavke |
| `http.py`, `ckan.py`, `izvori.py` | HTTP klijent s cacheom, CKAN razrješavanje, registar izvora → meta.json |
| `probe.py` | provjera svih izvora → `docs/probe_report.md` |
| `load_dzs.py` | Popis 2021. (naselja, stanovi za odmor), Turizam 2025. (PDF tab. 2.11) |
| `load_dgu.py` | Upravne jedinice (GML streaming), Registar geografskih imena (WFS) |
| `load_osm.py` | graf iz Geofabrik PBF-a (pyosmium → OSMnx), turistički objekti, mjesta |
| `load_hc.py` | PLDP iz CKAN ZIP-a, RoadLink iz INSPIRE WFS-a (validacija) |
| `load_effis.py`, `fwi_today.py` | FWI GeoTIFF i opožarene površine; noćni job |
| `match_settlements.py` | spajanje DZS ↔ DGU ↔ točka naselja |
| `graph_egress.py` | D3–D4: sigurna mreža, jezgra, mostovi grafa, maksimalni tok, minimalni rez |
| `population.py`, `evac_time.py`, `second_road.py`, `hazard.py`, `priority.py` | D5, D6, D7, D8, D9 |
| `ml_susceptibility.py`, `osjetljivost.py` | D11 model podložnosti, analiza osjetljivosti |
| `export.py`, `pipeline.py`, `mock.py` | izvoz po shemi, orkestracija, mock podaci |

## Interoperabilnost

- **GeoJSON (RFC 7946)**, EPSG:4326, 5 decimala; shema u [openapi.yaml](openapi.yaml).
- **OGC WMS/WFS** kao ulaz (EFFIS, HC INSPIRE TN-RO, DGU RGI) i **INSPIRE** teme TN (HC) i AU (DGU).
- **DCAT-AP**: izvedeni skup opisan u [dcat-ap.jsonld](dcat-ap.jsonld), spreman za objavu na data.gov.hr.
- Daljnji korak: OGC API Features (pygeoapi) nad istim GeoJSON-om.

## Integracijski potencijal

- Podloga za **procjene rizika od velikih nesreća** JLS-ova i županija (CSV izvoz prioriteta, izvori uz svaku brojku).
- **ŽVOC**: dnevni FWI × broj izlaza × ljudi iza uskog grla.
- **Ravnateljstvo civilne zaštite MUP-a**; objava izvedenog skupa na **data.gov.hr** i **NIPP-u**.
- Daljnji razvoj: sustav 112, e-Građani, eVisitor (stvarna populacija, uz sporazum), sve obalne županije.

## Preduvjeti

- **Tehnički**: dostupnost EFFIS WMS/WFS, HC i DGU servisa; GitHub Actions za noćni job; Geofabrik izvadak.
- **Organizacijski**: tko održava alat (županija ili civilna zaštita), tko na terenu potvrđuje „drugu cestu“
  i ispravlja OSM; godišnje osvježavanje turističkih podataka (DZS).
- **Pravni**: Otvorena dozvola (data.gov.hr), CC BY 4.0 (EFFIS, ESA WorldCover), ODbL 1.0 (OSM; izvedeni podaci s
  OSM geometrijom su share-alike), NN 56/2023 i napomena „Sadrži podatke Državne geodetske uprave“; odricanje
  odgovornosti na svakom ekranu; nema osobnih podataka (D12). Kod: EUPL-1.2.
