"""Cijeli pipeline: izvori → spajanje → D4 → D5 → D6 → D7 → D8 → D9 → izvoz za web.

python -m etl.pipeline --county SKZ --mode live|cache|mock

- live:  podatke dohvaća preko API-ja (CKAN, WFS, WMS); velike datoteke (DGU AU,
         OSM graf) uzima iz cachea ako postoje, osim uz --osvjezi.
- cache: isto, ali ne osvježava ni EFFIS ni ostale male izvore.
- mock:  piše izmišljene podatke po shemi (crvena traka „MOCK“ u UI-ju).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import Counter

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from etl import (evac_time, export, fwi_today, graph_egress as ge, hazard, izvori, load_dgu, load_dzs,
                 load_effis, load_hc, load_osm, match_settlements, population, priority, second_road)
from etl.config import (CRS_ANALIZA, DOCS_DIR, MAKS_UDALJENOST_CESTE_M, MANUAL_DIR, POVIJESNI_DAN, PUFER_KM,
                        SCENARIJI, WEB_DATA_DIR, ZUPANIJE)

# D10: raspored dizanja pokretnog mosta u Tisnom — prikazuje se kao napomena, ne ulazi u formulu.
# izvor: TZ Tisno (stranica bez godine; dodatno ljetno dizanje u 9:00 je N)
NAPOMENA_TISNO = ("Pokretni most u Tisnom: ljeti (1.6.–15.9.) diže se svaki dan 18:00–18:20, "
                  "zimi (16.9.–31.5.) ponedjeljkom i petkom 09:00–09:20 (TZ Tisno). "
                  "Za vrijeme dizanja cestovnog izlaza nema.")
TISNO_LONLAT = (15.641, 43.801)  # izvor: OSM, most D121 u Tisnom (probe 28.10.2026.)


def _log(poruka: str):
    print(f"[{dt.datetime.now():%H:%M:%S}] {poruka}", flush=True)


def _trajekti() -> dict:
    put = MANUAL_DIR / "trajekti.csv"
    if not put.exists():
        return {}
    with open(put, encoding="utf-8", newline="") as f:
        redovi = list(csv.reader(f))[2:]
    return {(match_settlements.norm(r[0]), match_settlements.norm(r[1])): r[2] for r in redovi if len(r) >= 3}


def _sc(df_red, prefiks: str) -> dict:
    return {s: (None if pd.isna(df_red[f"{prefiks}_{s}"]) else float(df_red[f"{prefiks}_{s}"])) for s in SCENARIJI}


def pokreni(kljuc_zupanije: str, nacin: str, osvjezi: bool = False):
    zup_cfg = ZUPANIJE[kljuc_zupanije]
    danas = dt.date.today().isoformat()
    kvaliteta: list[str] = []

    # ---------------------------------------------------------------- izvori
    _log("DGU upravne jedinice")
    au = load_dgu.ucitaj_au(osvjezi=osvjezi)
    zup = load_dgu.zupanija(au, zup_cfg["naziv"])
    _, nas_dgu = load_dgu.jls_i_naselja(au, zup)
    poligon_zup = zup.geometry.iloc[0]
    pufer = zup.geometry.buffer(PUFER_KM * 1000).simplify(200)
    pufer_wgs = pufer.to_crs(4326).iloc[0]
    bbox_zup = tuple(round(float(x), 2) for x in zup.to_crs(4326).total_bounds)

    _log("OSM grafovi (glavni i kombinirani s putovima track)")
    G = load_osm.dohvati_graf(pufer_wgs, kljuc_zupanije, "glavni", osvjezi=osvjezi)
    C = load_osm.dohvati_graf(pufer_wgs, kljuc_zupanije, "kombinirani", osvjezi=osvjezi)
    osm_mjesta = load_osm.mjesta(pufer_wgs, osvjezi=osvjezi)
    osm_turizam = load_osm.turisticki_objekti(pufer_wgs, osvjezi=osvjezi)
    _log(f"  glavni graf: {G.number_of_nodes()} čvorova, {G.number_of_edges()} bridova; "
         f"kombinirani: {C.number_of_nodes()} / {C.number_of_edges()}")

    _log("DGU RGI točke naselja, DZS")
    rgi = load_dgu.ucitaj_rgi_naselja(bbox_zup, osvjezi=(nacin == "live" and osvjezi))
    dzs = load_dzs.ucitaj_naselja(zup_cfg["naziv"])
    stanovi = load_dzs.ucitaj_stanove_odmor(zup_cfg["naziv"])
    turizam = load_dzs.ucitaj_turizam_2025(zup_cfg["naziv"])

    # ---------------------------------------------------------------- spajanje
    naselja = match_settlements.spoji(dzs, nas_dgu, rgi, osm_mjesta)
    kvaliteta.append(f"Spajanje DZS → DGU: {len(naselja)}/{len(dzs)} naselja "
                     f"({Counter(naselja.nacin_spajanja).most_common()}); izvor točke: "
                     f"{Counter(naselja.tocka_izvor).most_common()}.")

    # ---------------------------------------------------------------- D3–D4
    _log("D3–D4: sigurna mreža, jezgre, broj izlaza")
    cvorovi = load_osm.cvorovi_gdf(G)
    sigurni = ge.sigurni_cvorovi(G, cvorovi, poligon_zup)
    komp = ge.komponente_bez_mostova(G)
    jezgre = ge.jezgre_naselja(naselja, cvorovi, komp)
    v1 = ge.klase_v1(G, jezgre, sigurni)
    po_naselju, uska = ge.izlazi_svih(G, jezgre, sigurni)
    nesklad = [nid for nid, z in po_naselju.items()
               if {"E0": "E0", "E1": "E1"}.get(z["klasa_izlaza"], "E2+") != v1[nid]]
    kvaliteta.append(f"D4 v1 (mostovi grafa) i v2 (minimalni rez) slažu se za {len(po_naselju) - len(nesklad)}"
                     f"/{len(po_naselju)} naselja" + (f"; nesklad: {nesklad}" if nesklad else "."))
    iza_pokretnog = ge.pokretni_mostovi_iza(G, sigurni)

    # ---------------------------------------------------------------- D5
    _log("D5: ljetna populacija")
    udjeli = population.udjeli_naselja(naselja, osm_turizam)
    pop = population.ljetna_populacija(naselja, udjeli, turizam, stanovi).set_index("id")

    def ljudi(ids: list) -> dict:
        return {s: float(pop.loc[ids, f"p_ljeto_{s}"].sum()) if ids else 0.0 for s in SCENARIJI}

    # ---------------------------------------------------------------- D6 + uska grla
    _log("D6: uska grla i vrijeme evakuacije")
    pldp = None
    try:
        pldp = load_hc.ucitaj_pldp(2025)
    except Exception as e:  # noqa: BLE001 — PLDP je validacija, pipeline ide dalje
        kvaliteta.append(f"PLDP HC 2025 nije učitan: {e}")
    ug_zapisi = {}
    kratko_malo: list[str] = []
    for i, (kljuc, ug) in enumerate(sorted(uska.items(), key=lambda kv: -len(kv[1].cvorovi_iza)), 1):
        atr = [G[u][v] for u, v in ug.bridovi]
        iza = ge.naselja_u_podrucju(jezgre, ug.cvorovi_iza)
        lj = ljudi(iza)
        kap = evac_time.kapacitet_reza(atr)
        t = evac_time.vrijeme_h(lj, kap)
        refovi = [a.get("ref") for a in atr if a.get("ref")]
        imena = [a.get("name") for a in atr if a.get("name")]
        geom = ge.geometrija_reza(G, ug.bridovi)
        pokretni = any(a.get("pokretni_most") for a in atr)
        nazivi_iza = list(naselja.set_index("id").loc[iza, "naziv"]) if iza else []
        ug_zapisi[kljuc] = {
            "id": f"UG-{kljuc_zupanije}-{i:03d}",
            "cesta_ref": Counter(refovi).most_common(1)[0][0] if refovi else None,
            "naziv": Counter(imena).most_common(1)[0][0] if imena else None,
            "pokretni_most": pokretni,
            "most": any(a.get("most") for a in atr),
            "broj_bridova": len(ug.bridovi),
            "highway": sorted({a.get("highway") for a in atr if a.get("highway")}),
            "kapacitet_voz_h": kap, "ljudi_iza": lj, "t_evak_h": t,
            "naselja_iza": iza,
            "pldp": load_hc.pldp_za_usko_grlo(pldp, Counter(refovi).most_common(1)[0][0] if refovi else None,
                                              nazivi_iza),
            "geometrija": geom, "bridovi": ug.bridovi, "cvorovi_iza": ug.cvorovi_iza,
        }
        if not evac_time.razumno(t) and iza:
            # T < 5 min uz malo ljudi je OČEKIVANO (npr. 60 ljudi = 24 vozila); ručno gledamo ostalo.
            if t["sred"] is not None and t["sred"] < 1 and lj["sred"] < 300:
                kratko_malo.append(ug_zapisi[kljuc]["id"])
            else:
                kvaliteta.append(f"Kontrola razumnosti D6: {ug_zapisi[kljuc]['id']} "
                                 f"({', '.join(sorted(set(nazivi_iza))[:6])}; ljudi sred {lj['sred']:.0f}) "
                                 f"T_sred = {t['sred']} h — provjeriti ručno.")

    if kratko_malo:
        kvaliteta.append(f"Kontrola razumnosti D6: {len(kratko_malo)} uskih grla ima T_sred < 5 min, ali iza "
                         f"svakog je manje od 300 ljudi ljeti — kratko vrijeme je očekivano (malo vozila), "
                         f"nije pogreška podataka. Popis: {', '.join(kratko_malo)}.")

    # ---------------------------------------------------------------- D8
    _log("D8: statička opasnost (WorldCover + EFFIS opožarene površine)")
    tocke_wgs = naselja.geometry.to_crs(4326)
    g = hazard.udio_goriva(tocke_wgs)
    bbox_pozari = tuple(round(float(x), 2) for x in zup.buffer(6000).to_crs(4326).total_bounds)
    pozari = load_effis.opozarene_povrsine(bbox_pozari, osvjezi=(nacin == "live"))
    p = hazard.udio_opozarenog(naselja.geometry, pozari)
    p_norm = hazard.min_max(p)
    h = hazard.h_stat(g, p_norm)
    granice = priority.tercili(h)

    # ---------------------------------------------------------------- D7
    _log("D7: kandidati za drugu cestu")
    C_cvorovi = load_osm.cvorovi_gdf(C)
    sigurni_C = ge.sigurni_cvorovi(C, C_cvorovi, poligon_zup)
    C_bridovi = second_road.bridovi_gdf(C)
    druge = {}
    for kljuc, z in ug_zapisi.items():
        if z["broj_bridova"] != 1:
            continue  # D7 samo za E1 uska grla
        geom_3765 = gpd.GeoSeries([z["geometrija"]], crs=4326).to_crs(CRS_ANALIZA).iloc[0]
        dc = second_road.druga_cesta(C, C_bridovi, sigurni_C, set(z["cvorovi_iza"]) & set(C.nodes), geom_3765)
        if dc:
            dc["rang"] = round(z["ljudi_iza"]["sred"] / max(dc["duljina_km"], 0.1), 1)
            druge[kljuc] = dc

    # ---------------------------------------------------------------- D9 + izvoz naselja
    _log("D9 i izvoz")
    trajekti = _trajekti()
    # Je li pokretni most u grafu baš onaj u Tisnu (D10)? U ŠKŽ je to jedini pokretni most u OSM-u.
    tisno_pokretni = any(d.get("pokretni_most") and abs(G.nodes[u]["x"] - TISNO_LONLAT[0]) < 0.01
                         and abs(G.nodes[u]["y"] - TISNO_LONLAT[1]) < 0.01 for u, _, d in G.edges(data=True))
    # Naselja bez vozive ceste: postoje li barem putovi (track) unutar 1 km?
    C_sindex = C_cvorovi.sindex
    znacajke, props_svi = [], []
    for r, gi, pi, hi in zip(naselja.itertuples(), g, p, h):
        z = po_naselju[r.id]
        jz = jezgre[r.id]
        ug = ug_zapisi.get(z["usko_grlo"]) if z["usko_grlo"] else None
        if z["klasa_izlaza"] == "E0":
            iza = ge.naselja_u_podrucju(jezgre, z["cvorovi_iza"]) if z["cvorovi_iza"] else [r.id]
            lj, t = ljudi(iza if r.id in iza else iza + [r.id]), None
        elif ug:
            lj, t = ug["ljudi_iza"], ug["t_evak_h"]
        else:
            lj, t = None, None
        pr = pop.loc[r.id]
        hr = priority.h_razred(hi, granice)
        klasa = z["klasa_izlaza"]
        t_sred = t["sred"] if t else None
        pokretni = bool(jz) and sum(n in iza_pokretnog for n in jz) * 2 > len(jz)
        napomene = []
        if pokretni and tisno_pokretni:
            napomene.append(NAPOMENA_TISNO)
        samo_putovi = False
        if not jz:
            samo_putovi = len(C_sindex.query(r.tocka.buffer(MAKS_UDALJENOST_CESTE_M), predicate="intersects")) > 0
            napomene.append("Unutar 1 km od naselja nema vozive ceste"
                            + (" — u OSM-u postoje samo šumski/poljski putovi (highway=track); izlaz ovisi o njima "
                               "ili o moru. Provjeriti na terenu." if samo_putovi else " ni puta."))
        if r.tocka_izvor != "dgu_rgi":
            napomene.append(f"Točka naselja iz izvora '{r.tocka_izvor}' (nema u DGU RGI).")
        trajekt = trajekti.get((match_settlements.norm(r.jls), match_settlements.norm(r.naziv)))
        if klasa == "E0" and not trajekt and not samo_putovi:
            napomene.append("Izlaz samo morem — redovna brodska linija nije upisana u data/manual/trajekti.csv.")
        dc = druge.get(z["usko_grlo"]) if z["usko_grlo"] else None
        props = {
            "id": r.id, "naziv": r.naziv, "jls": r.jls, "zupanija": r.zupanija,
            "stanovnici_2021": int(r.stanovnici_2021), "stanovnici_65plus": int(r.stanovnici_65plus),
            "postelje_jls": int(pr.postelje_jls), "stanovi_odmor_jls": int(pr.stanovi_odmor_jls),
            "p_ljeto": {s: int(pr[f"p_ljeto_{s}"]) for s in SCENARIJI},
            "udio_naselja": round(float(pr.udio), 4), "udio_metoda": pr.udio_metoda,
            "izlazi_e": z["izlazi_e"], "klasa_izlaza": klasa,
            "usko_grlo_id": ug["id"] if ug else None,
            "ljudi_iza_reza": {s: int(lj[s]) for s in SCENARIJI} if lj else None,
            "t_evak_h": t,
            "pokretni_most": pokretni,
            "samo_putovi": samo_putovi,
            "trajektna_linija": trajekt if klasa == "E0" else None,
            "h_stat": hi, "h_gorivo": gi, "h_pozari_udio": pi, "h_razred": hr,
            "prioritet": priority.razred(klasa, hr, t_sred),
            "iz": priority.indeks(klasa, hi, t_sred),
            "druga_cesta_km": dc["duljina_km"] if dc else None,
            "druga_cesta_udio_track": dc["udio_track"] if dc else None,
            "tocka_izvor": r.tocka_izvor,
            "napomene": napomene,
            "izvori": ["dzs_popis_naselja", "dgu_au", "dgu_rgi", "osm", "dzs_turizam_2025", "dzs_stanovi",
                       "dzs_popunjenost_2025_08", "worldcover", "effis_ba", "effis_fwi"]
                      + (["hc_brojenje_2025"] if ug and ug.get("pldp") else [])
                      + (["jadrolinija"] if trajekt else []) + (["tz_tisno_most"] if pokretni else []),
        }
        props_svi.append(props)
        znacajke.append(export.feature(gpd.GeoSeries([r.tocka], crs=CRS_ANALIZA).to_crs(4326).iloc[0], props))
    export.zapisi_geojson("settlements.geojson", znacajke)

    # ---------------------------------------------------------------- uska grla, druge ceste, požari
    ime_po_id = naselja.set_index("id").naziv.to_dict()
    ug_feat = []
    for kljuc, z in ug_zapisi.items():
        if not z["naselja_iza"]:
            continue  # rez koji ne „zatvara“ nijedno naselje nije zanimljiv za kartu
        ug_feat.append(export.feature(z["geometrija"], {
            "id": z["id"], "cesta_ref": z["cesta_ref"], "naziv": z["naziv"], "pokretni_most": z["pokretni_most"],
            "most": z["most"], "pokretni_most_iza": bool(z["cvorovi_iza"] & iza_pokretnog),
            "broj_izlaza": z["broj_bridova"], "kapacitet_voz_h": z["kapacitet_voz_h"],
            "ljudi_iza": {s: int(v) for s, v in z["ljudi_iza"].items()}, "t_evak_h": z["t_evak_h"],
            "naselja_iza": z["naselja_iza"], "naselja_iza_nazivi": [ime_po_id[n] for n in z["naselja_iza"]],
            "pldp": z["pldp"],
            "druga_cesta_km": druge[kljuc]["duljina_km"] if kljuc in druge else None,
        }))
    export.zapisi_geojson("bottlenecks.geojson", ug_feat)
    dc_feat = [export.feature(d["geometrija"], {
        "usko_grlo_id": ug_zapisi[k]["id"], "duljina_km": d["duljina_km"], "udio_track": d["udio_track"],
        "rang": d["rang"], "ljudi_iza_sred": int(ug_zapisi[k]["ljudi_iza"]["sred"]),
        "oznaka": "kandidat – prohodnost provjeriti na terenu"}) for k, d in druge.items()]
    export.zapisi_geojson("second_roads.geojson", dc_feat)
    if len(pozari):
        pz = pozari.copy()
        pz["geometry"] = pz.geometry.simplify(30)
        pz = pz.to_crs(4326)
        export.zapisi_geojson("burned.geojson", [export.feature(gm, {
            "datum": str(fd)[:10], "povrsina_ha": float(a) if a is not None else None})
            for gm, fd, a in zip(pz.geometry, pz.get("FIREDATE", [None] * len(pz)), pz.get("AREA_HA", [None] * len(pz)))])

    # ---------------------------------------------------------------- FWI (danas + povijesni dan)
    _log("EFFIS FWI: danas i povijesni dan")
    naselja_gj = {"features": znacajke}
    for datum, ime in ((danas, "fwi_today.json"), (POVIJESNI_DAN, f"fwi_{POVIJESNI_DAN}.json")):
        try:
            rez = fwi_today.izracunaj(datum, naselja_gj)
            (WEB_DATA_DIR / ime).write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            kvaliteta.append(f"EFFIS FWI za {datum} nije dohvaćen: {e}")

    # ---------------------------------------------------------------- validacija HC WFS
    _log("Validacija: pokrivenost javnih cesta HC-a u OSM grafu")
    try:
        hc = load_hc.hc_roadlinks(bbox_zup)
        osm_b = second_road.bridovi_gdf(G)
        pokr = load_hc.pokrivenost_osm(hc, osm_b, poligon_zup)
        kvaliteta.append(f"HC WFS: {pokr['hc_km']} km javnih cesta u županiji; OSM glavni graf pokriva "
                         f"{pokr['pokriveno_km']} km ({pokr['udio']:.1%}, tolerancija {pokr['tolerancija_m']} m).")
    except Exception as e:  # noqa: BLE001
        pokr = None
        kvaliteta.append(f"HC WFS validacija nije uspjela: {e}")

    # ---------------------------------------------------------------- meta, kpi, docs
    m = export.meta(nacin, {
        "zupanija": zup_cfg["naziv"],
        "validacija": {"d4_v1_v2_nesklad": nesklad, "hc_pokrivenost": pokr,
                       "spajanje_naselja": f"{len(naselja)}/{len(dzs)}"},
        "h_tercili": granice,
        "broj_uskih_grla": len(ug_feat), "broj_drugih_cesta": len(dc_feat),
    })
    (WEB_DATA_DIR / "meta.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    k = export.kpi(props_svi, danas)
    (WEB_DATA_DIR / "kpi.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    export.izvori_md(m)
    (DOCS_DIR / "kvaliteta_podataka.md").write_text(
        "# Kvaliteta podataka\n\nGenerirano naredbom `python -m etl.pipeline` "
        f"({m['generirano']}).\n\n" + "\n".join(f"- {x}" for x in kvaliteta) + "\n", encoding="utf-8")
    _log(f"Gotovo: {k['naselja_po_klasi']} | prioritet {k['naselja_po_prioritetu']}")
    return k


def main():
    ap = argparse.ArgumentParser(description="JEDAN IZLAZ pipeline")
    ap.add_argument("--county", default="SKZ", choices=list(ZUPANIJE))
    ap.add_argument("--mode", default="live", choices=["live", "cache", "mock"])
    ap.add_argument("--osvjezi", action="store_true", help="ponovno preuzmi i velike izvore (DGU AU, OSM)")
    args = ap.parse_args()
    if args.mode == "mock":
        from etl import mock
        mock.zapisi()
        return
    pokreni(args.county, args.mode, args.osvjezi)


if __name__ == "__main__":
    main()
