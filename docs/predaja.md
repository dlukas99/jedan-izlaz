# Predaja — kontrolna lista

Rok: **9. 11. 2026. u 24:00** (interni cilj 18:00), samo e-mailom na **open.data@mpudt.hr**.
Šalje voditelj tima, ostali u kopiji. Naslov: „Datathon 2026 – izazov B – JEDAN IZLAZ – [naziv tima]“.

## Sadržaj e-maila

1. **Izvorni kod**: https://github.com/dlukas99/jedan-izlaz (EUPL-1.2), tag `v1.0-predaja`.
2. **Dokumentacija**:
   - arhitektura: [arhitektura.md](arhitektura.md)
   - metodologija s konstantama i izvorima: [metodologija.md](metodologija.md)
   - popis skupova podataka s izdavačem i poveznicom: [izvori.md](izvori.md)
   - evaluacija modela D11: [evaluacija.md](evaluacija.md), analiza osjetljivosti: [osjetljivost.md](osjetljivost.md)
   - kvaliteta podataka i validacija: [kvaliteta_podataka.md](kvaliteta_podataka.md), [probe_report.md](probe_report.md)
   - OpenAPI: [openapi.yaml](openapi.yaml), DCAT-AP: [dcat-ap.jsonld](dcat-ap.jsonld)
3. **Demo**: https://dlukas99.github.io/jedan-izlaz/ i snimke zaslona iz [snimke/](snimke/).
4. **Video** (≤ 3:00): poveznica bez prijave + rezervna poveznica.

## Provjere prije slanja

- [ ] `python -m etl.pipeline --county SKZ --mode live` prošao; `meta.json` ima `"nacin": "live"`
- [ ] `pytest -q` zelen lokalno i u GitHub Actions (`tests`)
- [ ] noćni job `nightly_fwi` prošao barem jednom
- [ ] demo radi u anonimnom prozoru i na mobitelu
- [ ] brojke u videu = `kpi.json` na dan zamrzavanja (6. 11.)
- [ ] Jadrolinijine linije u `data/manual/trajekti.csv` provjerene (sada N)
- [ ] proba predaje iz čistog klona (8. 11.)
- [ ] `git tag v1.0-predaja && git push --tags`
- [ ] sve poveznice rade do 23. 11. 2026.

## Ručni korak na GitHubu (jednokratno)

Settings → Pages → Build and deployment → Source: **GitHub Actions**. Nakon toga `pages.yml` objavljuje
`web/dist` na https://dlukas99.github.io/jedan-izlaz/.
