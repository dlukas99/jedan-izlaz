"""Sve konstante projekta (odluke D1–D12 iz CLAUDE.md).

Pravilo: svaka brojka ima komentar "# izvor: …" ili "# PRETPOSTAVKA: …".
Pretpostavke ulaze u analizu osjetljivosti (docs/metodologija.md).
"""
from __future__ import annotations

from pathlib import Path

# --- Putanje ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"          # sirovi odgovori (nije u gitu)
INTERIM_DIR = DATA_DIR / "interim"  # međurezultati (nije u gitu)
MANUAL_DIR = DATA_DIR / "manual"    # ručni CSV-ovi (u gitu, izvor u prvom retku)
DOCS_DIR = ROOT / "docs"
WEB_DATA_DIR = ROOT / "web" / "public" / "data"

# --- Mreža -------------------------------------------------------------------
HTTP_USER_AGENT = "JedanIzlaz/0.1 (studentski projekt, Datathon 2026)"  # izvor: CLAUDE.md §8.5
HTTP_TIMEOUT_S = 60       # izvor: CLAUDE.md §8.5
HTTP_MIN_RAZMAK_S = 0.5   # izvor: CLAUDE.md §8.5 (najviše 2 zahtjeva/s po servisu)

CKAN_API = "https://data.gov.hr/ckan/api/3/action/"  # izvor: data.gov.hr (P 28.10.2026.)

# --- D1 Opseg i CRS ---------------------------------------------------------------
CRS_ANALIZA = "EPSG:3765"  # izvor: HTRS96/TM, službena projekcija RH (D1)
CRS_WEB = "EPSG:4326"      # izvor: RFC 7946 (GeoJSON)
KOORD_DECIMALE = 5         # izvor: D1 (≈ 1 m, dovoljno za kartu)

# Županije: šifra DZS-a (tekst!) i naziv kako ga piše DZS; ključ je argument --county.
ZUPANIJE = {
    "SKZ": {"naziv": "Šibensko-kninska", "nuts3": "HR034"},  # izvor: provjereno u probe (vidi docs/probe_report.md)
}
PUFER_KM = 15  # izvor: D3 (graf = poligon županije + 15 km, da sigurna mreža postoji izvan granice)
# Poligon županije (DGU) je KOPNENI: rive i molovi strše u more izvan njega i bez ovog pufera
# postaju „sigurni čvorovi“ na samom otoku (Murter bi bio E2-5, Žirje E1). Utvrđeno 29.10.2026.
SIGURNO_PUFER_M = 1000  # PRETPOSTAVKA: sigurna mreža počinje 1 km izvan kopnene granice županije

# --- D2 Graf ceste ---------------------------------------------------------------
# izvor: D2 — vozive OSM ceste; service bez access=private|no
HIGHWAY_GLAVNI = [
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
    "secondary", "secondary_link", "tertiary", "tertiary_link",
    "unclassified", "residential", "living_street", "service",
]
HIGHWAY_TRACK = ["track"]  # izvor: D2 (zaseban graf samo za D7)
ACCESS_ISKLJUCI = ["private", "no"]  # izvor: D2

# Radijus jezgre naselja kad nema poligona (OSM place=*): izvor: D3.3 / CLAUDE.md §3.3
RADIJUS_PLACE_M = {
    "city": 3000,       # PRETPOSTAVKA: city nije u CLAUDE.md, uzimamo nešto više od town
    "town": 2500,
    "village": 700,
    "suburb": 700,      # PRETPOSTAVKA: dijelovi grada kao village
    "neighbourhood": 500,  # PRETPOSTAVKA
    "hamlet": 300,
    "isolated_dwelling": 300,
    "locality": 300,    # PRETPOSTAVKA
}
RADIJUS_ZADANO_M = 500        # PRETPOSTAVKA: ako tip mjesta nije u tablici
MAKS_UDALJENOST_CESTE_M = 1000  # izvor: CLAUDE.md §3.3 (najviše 1 km do najbliže ceste)

# --- D4 Broj izlaza ---------------------------------------------------------------
MAKS_IZLAZA = 6  # izvor: Fong i sur., PNAS 2026 (prag ≈ 6 izlaznih cesta)
VELIKI_KAPACITET = 10**6  # tehnička konstanta: "beskonačno" za super-izvor/ponor

# --- D5 Ljetna populacija ---------------------------------------------------------
SCENARIJI = ("opt", "sred", "pes")
POPUNJENOST = {"opt": 0.70, "sred": 0.80, "pes": 0.95}  # izvor: DZS priopćenje kolovoz 2025. (odmarališta 70,8 %, kampovi 81,7 %, hoteli 97,3 %)
OSOBA_PO_STANU_ODMOR = {"opt": 2, "sred": 3, "pes": 4}  # PRETPOSTAVKA: analiza osjetljivosti
TOURISM_OZNAKE = ["hotel", "apartment", "guest_house", "hostel", "camp_site", "chalet", "motel"]  # izvor: D5 (+motel, PRETPOSTAVKA)
MIN_TURIST_OBJEKATA_JLS = 5  # izvor: D5 (ispod toga udio po stanovnicima)

# --- D6 Vrijeme evakuacije -------------------------------------------------------
OSOBA_PO_VOZILU = {"opt": 3.0, "sred": 2.5, "pes": 2.0}  # PRETPOSTAVKA (D6), raspon iz literature o evakuaciji
KAPACITET_TRAKE_VOZ_H = {"opt": 1300, "sred": 1000, "pes": 600}  # izvor: Rohaert, Kuligowski i sur., TR-D 116 (2023) 103610 (~1.275 voz/h); planovi CA 1.000; zagušenje ~500
FAKTOR_KLASE_CESTE = {  # PRETPOSTAVKA (D6): niže klase imaju manji protok
    "motorway": 1.0, "trunk": 1.0, "primary": 1.0, "secondary": 1.0, "tertiary": 1.0,
    "unclassified": 0.6, "residential": 0.6, "living_street": 0.6, "service": 0.6, "track": 0.3,
}
T_MIN_RAZUMNO_H = 5 / 60  # izvor: D6 kontrola razumnosti
T_MAX_RAZUMNO_H = 24      # izvor: D6 kontrola razumnosti

# --- D8 Opasnost od požara ---------------------------------------------------------
H_TEZINA_GORIVO = 0.6    # PRETPOSTAVKA (D8)
H_TEZINA_POZARI = 0.4    # PRETPOSTAVKA (D8)
RADIJUS_GORIVO_M = 2000  # izvor: D8
RADIJUS_POZARI_M = 5000  # izvor: D8
WORLDCOVER_GORIVO_KLASE = [10, 20, 30]  # izvor: ESA WorldCover v200 legenda (drveće, grmlje, travnjaci)
POVIJESNI_DAN = "2026-08-13"  # izvor: HVZ, požar kod Lokve Rogoznice 13.–15.8.2026.

# --- D9 Prioritet ---------------------------------------------------------------
F_KLASE = {"E0": 1.0, "E1": 0.9, "E2-5": 0.4, "E6+": 0.0}  # PRETPOSTAVKA (D9)
T_PRAG_A_H = 1.0  # izvor: D9
T_PRAG_B_H = 3.0  # izvor: D9
T_NORMA_H = 3.0   # izvor: D9, g = min(1, T_sred / 3 h)

# --- Izvori (URL-ovi servisa) ----------------------------------------------------
HC_WFS = "https://geoportal.hrvatske-ceste.hr/inspire/tn-ro/wfs"  # izvor: NIPP registri.nipp.hr/izvori/1656
HAC_WFS = "https://geoportal.hac.hr/inspire/tn-ro/wfs"            # izvor: CLAUDE.md §3.2
EFFIS_WMS = "https://maps.effis.emergency.copernicus.eu/effis"    # izvor: EFFIS downloads-instructions
# izvor: EFFIS WMS GetCapabilities 28.10.2026. — sloj ecmwf007.fwi više ne postoji; FWI je sada mf010.fwi.
# GetMap format=image/tiff vraća float32 vrijednosti FWI-ja (EPSG:4326, ~0,01°), GetFeatureInfo nije podržan.
EFFIS_FWI_SLOJ = "mf010.fwi"
EFFIS_BA_SLOJ = "ms:modis.ba.poly"  # izvor: EFFIS WFS (bbox u redoslijedu lon,lat bez oznake CRS-a)
# izvor: EFFIS GetLegendGraphic za mf010.fwi (data/raw/effis_probe/legend_mf010_fwi.png, 28.10.2026.)
FWI_RAZREDI = [  # (donja granica, oznaka) — gornja granica je sljedeća donja
    (0.0, "nizak"), (11.2, "umjeren"), (21.3, "visok"), (38.0, "vrlo visok"), (50.0, "ekstreman"), (70.0, "vrlo ekstreman"),
]
WORLDCOVER_URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"  # izvor: ESA WorldCover

ODRICANJE = "Alat za planiranje, ne za uzbunjivanje. U opasnosti slijedite upute 112 i civilne zaštite."
