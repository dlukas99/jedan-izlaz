"""DZS: stanovništvo po naseljima, stanovi za odmor i turističke postelje po JLS-u.

Kako radi:
- XLSX-ove razrješavamo preko data.gov.hr CKAN API-ja (package_show), ne
  hardkodiranim URL-om. Stupce tražimo po tekstu zaglavlja (npr. „Naselje“,
  „za odmor“), jer se raspored stupaca među izdanjima može promijeniti.
- DZS u tablici po naseljima NEMA matični broj naselja, pa se naselja spajaju
  s DGU-om po paru (JLS, naziv) u match_settlements.py.
- Postelje za 2025. postoje samo u PDF-u „Turizam u 2025.“ (tablica 2.11).
  Brojevi u PDF-u imaju razmak kao razdjelnik tisućica („10 543“), pa stupce
  razdvajamo po x-koordinati riječi (razmak unutar broja ~1 pt, između stupaca ~30 pt).
"""
from __future__ import annotations

import io
import re

import pandas as pd

from etl import ckan, http, izvori
from etl.config import RAW_DIR

PAKET_POPIS = "statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021"
PAKET_STANOVI = "statistika-u-nizu-popis-stanovnistva-kucanstava-i-stanova-2021-stambene-jedinice"
TURIZAM_2025_URL = "https://podaci.dzs.hr/2026/en/122435"  # izvor: DZS Statistička izvješća 1747/2026 (PDF)


def _preuzmi_ckan(paket_id: str, naziv: str, kljuc: str):
    paket = ckan.package_show(paket_id)
    res = ckan.nadji_resurs(paket, naziv_sadrzi=naziv)
    put = http.preuzmi(res["url"], RAW_DIR / "dzs" / res["url"].rsplit("/", 1)[-1], timeout=300)
    opis = ckan.opis_izvora(paket, res)
    izvori.zabiljezi(kljuc, url=opis["url"], url_paketa=opis["url_paketa"],
                     metadata_modified=opis["metadata_modified"],
                     dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    return put


def _broj(v) -> float:
    """DZS koristi '-' za nulu i 'z' za povjerljivo; oboje tretiramo kao 0 / NaN."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return float("nan")
    s = str(v).strip().replace(" ", "").replace(" ", "")
    if s in ("-", "–"):
        return 0.0
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return float("nan")


def _red_zaglavlja(df: pd.DataFrame, oznaka: str) -> int:
    """Indeks retka u kojem prvi stupac počinje s 'oznaka' (npr. 'Županija')."""
    for i, v in df[0].items():
        if isinstance(v, str) and v.strip().startswith(oznaka):
            return i
    raise ValueError(f"Zaglavlje '{oznaka}' nije pronađeno")


def _stupac(zaglavlje: pd.Series, *pojmovi: str) -> int:
    for i, v in zaglavlje.items():
        tekst = str(v).lower()
        if all(p.lower() in tekst for p in pojmovi):
            return i
    raise ValueError(f"Stupac {pojmovi} nije pronađen u zaglavlju: {list(zaglavlje.values)}")


def ucitaj_naselja(zupanija: str) -> pd.DataFrame:
    """Stanovništvo po naseljima (Popis 2021.), samo zbroj spolova ('sv.')."""
    put = _preuzmi_ckan(PAKET_POPIS, "Stanovništvo po naseljima", "dzs_popis_naselja")
    df = pd.read_excel(put, sheet_name="1.", header=None)
    h = _red_zaglavlja(df, "Županija")
    zag = df.loc[h]
    c_zup, c_tip = 0, 1
    c_jls = _stupac(zag, "grad/op")
    c_nas = _stupac(zag, "naselje")
    c_spol = _stupac(zag, "spol")
    c_uk = _stupac(zag, "ukupno")
    # Dobne skupine: zaglavlja oblika "65 – 69" … "95 i više"; 65+ = zbroj od 65 naviše.
    dobni = {i: str(v) for i, v in zag.items() if i > c_uk and re.match(r"^\s*\d+", str(v))}
    c_65 = [i for i, v in dobni.items() if int(re.match(r"\s*(\d+)", v).group(1)) >= 65]
    podaci = df.loc[h + 1:]
    p = podaci[(podaci[c_zup] == zupanija) & (podaci[c_spol] == "sv.") & podaci[c_nas].notna()]
    rez = pd.DataFrame({
        "zupanija": p[c_zup].values,
        "jls_tip": p[c_tip].values,
        "jls": p[c_jls].astype(str).str.strip().values,
        "naselje": p[c_nas].astype(str).str.strip().values,
        "stanovnici_2021": [_broj(v) for v in p[c_uk]],
        "stanovnici_65plus": [sum(_broj(r[c]) for c in c_65 if not pd.isna(_broj(r[c]))) for _, r in p.iterrows()],
    })
    # Kontrola zbroja: zbroj naselja mora odgovarati retku županije.
    ukupno_zup = podaci[(podaci[c_zup] == zupanija) & (podaci[c_spol] == "sv.") & podaci[c_jls].isna()][c_uk]
    if len(ukupno_zup) and abs(rez.stanovnici_2021.sum() - _broj(ukupno_zup.iloc[0])) > 0.5:
        raise ValueError(f"Zbroj naselja {rez.stanovnici_2021.sum()} ≠ županija {ukupno_zup.iloc[0]}")
    return rez


def ucitaj_stanove_odmor(zupanija: str) -> pd.DataFrame:
    """Broj stanova koji se povremeno koriste 'za odmor' po JLS-u (Popis 2021.)."""
    put = _preuzmi_ckan(PAKET_STANOVI, "po gradovima i općinama", "dzs_stanovi")
    df = pd.read_excel(put, sheet_name="1.", header=None)
    h = _red_zaglavlja(df, "Županija")
    zag = df.loc[h]
    c_jls = _stupac(zag, "grad/op")
    c_odmor = _stupac(zag, "za odmor")
    c_jed = c_jls + 1  # stupac s oznakom 'm2' za retke površine — uzimamo samo retke s brojem stanova
    podaci = df.loc[h + 1:]
    p = podaci[(podaci[0] == zupanija) & podaci[c_jls].notna() & podaci[c_jed].isna()]
    return pd.DataFrame({"jls": p[c_jls].astype(str).str.strip().values,
                         "stanovi_odmor": [_broj(v) for v in p[c_odmor]]})


def _redovi_pdf(stranica) -> list[tuple[str, list[float]]]:
    """Retke tablice 2.11 pretvori u (naziv, [8 brojeva]) grupiranjem riječi po x-razmaku."""
    rijeci = stranica.extract_words(keep_blank_chars=False, use_text_flow=False)
    redovi: dict[int, list] = {}
    for w in rijeci:
        redovi.setdefault(round(w["top"]), []).append(w)
    rez = []
    for top in sorted(redovi):
        ws = sorted(redovi[top], key=lambda w: w["x0"])
        # Grupe: nova grupa kad je razmak > 4 pt (unutar broja je ~1 pt).
        grupe, trenutna = [], [ws[0]]
        for a, b in zip(ws, ws[1:]):
            if b["x0"] - a["x1"] > 4:
                grupe.append(trenutna)
                trenutna = [b]
            else:
                trenutna.append(b)
        grupe.append(trenutna)
        tekstovi = [" ".join(w["text"] for w in g) for g in grupe]
        if len(tekstovi) == 9:  # naziv + 8 numeričkih stupaca
            rez.append((tekstovi[0], [_broj(t) if t != "z" else float("nan") for t in tekstovi[1:]]))
    return rez


def ucitaj_turizam_2025(zupanija: str) -> pd.DataFrame:
    """Tablica 2.11 za županiju: postelje (stalne, pomoćne), dolasci i noćenja po JLS-u, 2025."""
    import pdfplumber

    put = http.preuzmi(TURIZAM_2025_URL, RAW_DIR / "dzs" / "turizam_2025.pdf", timeout=300)
    izvori.zabiljezi("dzs_turizam_2025", url=TURIZAM_2025_URL, dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    redovi = []
    unutar = False
    with pdfplumber.open(put) as pdf:
        for st in pdf.pages:
            tekst = st.extract_text() or ""
            if "2.11." not in tekst[:200]:
                continue
            for naziv, brojevi in _redovi_pdf(st):
                if naziv.endswith("županija"):
                    unutar = naziv.startswith(zupanija)
                    continue
                if unutar:
                    redovi.append({"jls": naziv, "postelje_stalne": brojevi[0], "postelje_pomocne": brojevi[1],
                                   "dolasci": brojevi[2], "nocenja": brojevi[5]})
    df = pd.DataFrame(redovi)
    if df.empty:
        raise ValueError(f"Tablica 2.11 za '{zupanija}' nije pronađena u PDF-u")
    return df
