# Kvaliteta podataka

Generirano naredbom `python -m etl.pipeline` (2026-10-29T06:07:16).

- Spajanje DZS → DGU: 199/199 naselja ([('tocno', 199)]); izvor točke: [('dgu_rgi', 194), ('osm_place', 4), ('dgu_poligon', 1)].
- D4 v1 (mostovi grafa) i v2 (minimalni rez) slažu se za 199/199 naselja.
- Kontrola razumnosti D6: UG-SKZ-011 (Kninsko Polje, Vrpolje; ljudi sred 976) T_sred = 0.08 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-015 (Markovac, Orlić, Ramljane, Riđane, Uzdolje, Zvjerinac; ljudi sred 671) T_sred = 0.05 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-017 (Kljake, Mirlović Polje, Umljanović, Čavoglave; ljudi sred 736) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-022 (Bogatić, Mratovo, Puljane, Čitluk; ljudi sred 759) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-025 (Ivoševci; ljudi sred 303) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-028 (Gračac, Sonković, Ždrapanj; ljudi sred 477) T_sred = 0.05 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-030 (Donje Planjane, Ostrogašica, Pakovo Selo; ljudi sred 306) T_sred = 0.03 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-033 (Podumci, Unešić; ljudi sred 535) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-037 (Kaočine, Ključ; ljudi sred 308) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-038 (Unešić; ljudi sred 426) T_sred = 0.06 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-039 (Bogatić, Brištani; ljudi sred 618) T_sred = 0.08 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-041 (Kadina Glavica, Kanjane, Otavice, Parčić; ljudi sred 477) T_sred = 0.06 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-043 (Danilo, Danilo Kraljice; ljudi sred 406) T_sred = 0.05 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-045 (Markovac, Orlić, Riđane, Štikovo; ljudi sred 325) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-048 (Bratiškovci, Gorice, Ićevo, Kakanj, Plastovo; ljudi sred 657) T_sred = 0.05 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-049 (Sitno Donje; ljudi sred 457) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-051 (Vrbnik; ljudi sred 309) T_sred = 0.03 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-057 (Boraja, Lepenica, Vrsno; ljudi sred 341) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-059 (Danilo Biranj; ljudi sred 416) T_sred = 0.06 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-060 (Kijevo; ljudi sred 443) T_sred = 0.06 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-061 (Gošić, Krnjeuve, Đevrske; ljudi sred 313) T_sred = 0.03 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-068 (Baljci, Gradac; ljudi sred 377) T_sred = 0.08 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-070 (Čista Velika; ljudi sred 405) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-073 (Dubrava kod Tisna, Putičanje; ljudi sred 550) T_sred = 0.07 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-083 (Razvođe; ljudi sred 335) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: UG-SKZ-102 (Piramatovci; ljudi sred 327) T_sred = 0.04 h — provjeriti ručno.
- Kontrola razumnosti D6: 99 uskih grla ima T_sred < 5 min, ali iza svakog je manje od 300 ljudi ljeti — kratko vrijeme je očekivano (malo vozila), nije pogreška podataka. Popis: UG-SKZ-029, UG-SKZ-031, UG-SKZ-034, UG-SKZ-035, UG-SKZ-042, UG-SKZ-044, UG-SKZ-047, UG-SKZ-050, UG-SKZ-054, UG-SKZ-055, UG-SKZ-056, UG-SKZ-058, UG-SKZ-063, UG-SKZ-064, UG-SKZ-065, UG-SKZ-066, UG-SKZ-067, UG-SKZ-069, UG-SKZ-071, UG-SKZ-072, UG-SKZ-074, UG-SKZ-075, UG-SKZ-076, UG-SKZ-077, UG-SKZ-078, UG-SKZ-079, UG-SKZ-080, UG-SKZ-081, UG-SKZ-082, UG-SKZ-084, UG-SKZ-088, UG-SKZ-089, UG-SKZ-090, UG-SKZ-091, UG-SKZ-092, UG-SKZ-093, UG-SKZ-094, UG-SKZ-095, UG-SKZ-097, UG-SKZ-098, UG-SKZ-099, UG-SKZ-100, UG-SKZ-101, UG-SKZ-103, UG-SKZ-104, UG-SKZ-106, UG-SKZ-108, UG-SKZ-109, UG-SKZ-110, UG-SKZ-111, UG-SKZ-112, UG-SKZ-113, UG-SKZ-114, UG-SKZ-115, UG-SKZ-117, UG-SKZ-118, UG-SKZ-119, UG-SKZ-120, UG-SKZ-121, UG-SKZ-122, UG-SKZ-123, UG-SKZ-125, UG-SKZ-127, UG-SKZ-129, UG-SKZ-130, UG-SKZ-131, UG-SKZ-132, UG-SKZ-133, UG-SKZ-135, UG-SKZ-136, UG-SKZ-137, UG-SKZ-138, UG-SKZ-140, UG-SKZ-141, UG-SKZ-142, UG-SKZ-143, UG-SKZ-144, UG-SKZ-145, UG-SKZ-146, UG-SKZ-147, UG-SKZ-148, UG-SKZ-149, UG-SKZ-150, UG-SKZ-151, UG-SKZ-152, UG-SKZ-153, UG-SKZ-154, UG-SKZ-155, UG-SKZ-156, UG-SKZ-157, UG-SKZ-159, UG-SKZ-160, UG-SKZ-161, UG-SKZ-162, UG-SKZ-163, UG-SKZ-165, UG-SKZ-166, UG-SKZ-167, UG-SKZ-168.
- D8: komponenta p = model podložnosti D11 (prosjek u krugu 5 km).
- HC WFS: 1188.3 km javnih cesta u županiji; OSM glavni graf pokriva 1182.5 km (99.5%, tolerancija 30 m).
