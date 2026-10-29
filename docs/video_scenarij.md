# Scenarij videa (cilj 2:50, nikad preko 3:00)

Brojke su iz `web/public/data/kpi.json` i kartica naselja na dan **29. 10. 2026.** Prije snimanja (6. 11.)
ponovno pokreni pipeline i usporedi s `kpi.json` (brojke u videu moraju biti jednake onima na dan zamrzavanja).
Video se snima isključivo na pravim podacima (`meta.json` → `"nacin": "live"`), nikad na MOCK-u.

| Vrijeme | Slika | Tekst za glas | Kriterij |
|---|---|---|---|
| 0:00–0:20 | Fotografija/karta požarišta Lokva Rogoznica (HVZ, 15. 8. 2026.) | „Kolovoz 2026., Lokva Rogoznica: oko 2.500 evakuiranih, 43 ozlijeđena, jedna smrtno stradala osoba, cesta zatvorena. Koliko naših obalnih naselja ima samo jedan izlaz?“ | problem |
| 0:20–0:35 | Tri persone (ikone) | „JEDAN IZLAZ je za stožere civilne zaštite, županijske vatrogasne centre i izrađivače procjena rizika od velikih nesreća.“ | korisnici |
| 0:35–1:00 | Stranica „Izvori i metoda“ | „Spajamo popis stanovništva i turističke postelje DZS-a i brojenje prometa Hrvatskih cesta s portala data.gov.hr preko API-ja, upravne jedinice i Registar geografskih imena DGU-a, EFFIS indeks opasnosti od požara uživo, ESA WorldCover i OpenStreetMap — 199 od 199 naselja spojeno.“ | izvori podataka |
| 1:00–1:20 | Karta ŠKŽ → klik Murter | „Murter, Betina, Jezera i Tisno: jedan cestovni izlaz, a prije njega još i pokretni most u Tisnu. Ljeti je iza njega 20 do 30 tisuća ljudi. Evakuacija cestom: od 5 do 25 sati. Izmjereni ljetni promet na brojilu Murter: 5.835 vozila dnevno.“ | funkcionalnosti |
| 1:20–1:30 | Klik Zlarin | „Zlarin, Prvić, Krapanj, Kaprije i Žirje: izlaz samo morem — tu treba plan evakuacije brodom.“ | funkcionalnosti |
| 1:30–1:42 | Sloj „FWI 13. 8. 2026.“ | „Na dan požara kod Lokve Rogoznice 174 od 199 naselja ove županije bilo je u ekstremnoj opasnosti.“ | rješenje u primjeni |
| 1:42–1:55 | Prioritetna lista → CSV; zelena isprekidana „druga cesta“ kod Grebaštice | „Prioritetna lista s izvozom za procjene rizika, i kandidati za drugu cestu — uz napomenu: prohodnost provjeriti na terenu.“ | funkcionalnosti |
| 1:55–2:20 | Dijagram iz docs/arhitektura.md | „Broj izlaza računamo kao minimalni rez cestovnog grafa, prema studiji PNAS 2026. koja pokazuje da smrtnost u požarima pada do otprilike šest izlaza. Model strojnog učenja procjenjuje podložnost terena (AUC 0,78 na prostornoj provjeri). Sve je statični GeoJSON na GitHub Pagesu, s noćnim osvježavanjem FWI-ja, OpenAPI i DCAT-AP opisom.“ | arhitektura |
| 2:20–2:40 | Brojke iz kpi.json | „U Šibensko-kninskoj županiji 45 naselja ima samo jedan cestovni izlaz, a u njima je ljeti 40 do 56 tisuća ljudi. Još 9 naselja nema vozivu cestu do kopna.“ | korisnička vrijednost |
| 2:40–2:50 | Karta Jadrana + logotipi izvora | „Sljedeće: sve obalne županije, OGC API, objava na data.gov.hr i povezivanje s 112 i eVisitorom. JEDAN IZLAZ je alat za planiranje, ne za uzbunjivanje — u opasnosti slijedite upute 112 i civilne zaštite.“ | daljnji razvoj |

Snimke zaslona za video i predaju: `docs/snimke/` (`node web/scripts/snimke.mjs`).
