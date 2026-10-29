"""D8: statička opasnost od požara oko naselja.

H_stat = 0,6·g + 0,4·p
- g: udio goriva (WorldCover klase 10 drveće, 20 grmlje, 30 travnjaci) u krugu
  od 2 km oko točke naselja. Udio računamo na KOPNENIM pikselima (bez mora,
  klasa 80), jer bi inače obalna naselja izgledala „sigurnije“ samo zato što
  je pola kruga more. (Odluka zapisana u dnevnik, CLAUDE.md §9.)
- p: udio površine kruga od 5 km koja je izgorjela u EFFIS-u (svi dostupni
  događaji), min–max normaliziran unutar pilota.
Razredi H su tercili unutar pilota — RELATIVNO unutar županije.

WorldCover čitamo izravno iz COG-a na AWS-u (/vsicurl/), samo prozore oko naselja.
"""
from __future__ import annotations

import math

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.windows import from_bounds

from etl import izvori
from etl.config import (H_TEZINA_GORIVO, H_TEZINA_POZARI, RADIJUS_GORIVO_M, RADIJUS_POZARI_M,
                        WORLDCOVER_GORIVO_KLASE, WORLDCOVER_URL)

GDAL_ENV = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
            "GDAL_HTTP_USERAGENT": "JedanIzlaz/0.1 (studentski projekt, Datathon 2026)",
            "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif"}
MORE = 80   # izvor: WorldCover legenda (Permanent water bodies)
NODATA = 0


def _tile(lon: float, lat: float) -> str:
    """WorldCover tileovi su 3°×3°, imenovani po donjem lijevom kutu (npr. N42E015)."""
    la = int(math.floor(lat / 3) * 3)
    lo = int(math.floor(lon / 3) * 3)
    return f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"


def udio_goriva(tocke_wgs84: gpd.GeoSeries, radijus_m: float = RADIJUS_GORIVO_M) -> list[float | None]:
    rez = []
    otvoreni: dict = {}
    with rasterio.Env(**GDAL_ENV):
        try:
            for p in tocke_wgs84:
                tile = _tile(p.x, p.y)
                if tile not in otvoreni:
                    otvoreni[tile] = rasterio.open("/vsicurl/" + WORLDCOVER_URL.format(tile=tile))
                ds = otvoreni[tile]
                dlat = radijus_m / 111_320
                dlon = radijus_m / (111_320 * math.cos(math.radians(p.y)))
                w = from_bounds(p.x - dlon, p.y - dlat, p.x + dlon, p.y + dlat, ds.transform)
                a = ds.read(1, window=w, boundless=True, fill_value=NODATA)
                # Krug: piksele izvan radijusa izbacujemo maskom.
                h, wd = a.shape
                yy, xx = np.mgrid[0:h, 0:wd]
                krug = ((xx - wd / 2 + 0.5) / (wd / 2)) ** 2 + ((yy - h / 2 + 0.5) / (h / 2)) ** 2 <= 1
                kopno = krug & (a != MORE) & (a != NODATA)
                if kopno.sum() == 0:
                    rez.append(None)
                    continue
                rez.append(round(float(np.isin(a[kopno], WORLDCOVER_GORIVO_KLASE).mean()), 3))
        finally:
            for ds in otvoreni.values():
                ds.close()
    izvori.zabiljezi("worldcover", url=WORLDCOVER_URL.format(tile="N42E015"))
    return rez


def udio_opozarenog(tocke: gpd.GeoSeries, pozari: gpd.GeoDataFrame, radijus_m: float = RADIJUS_POZARI_M) -> list[float]:
    """Udio kruga (EPSG:3765) koji je izgorio barem jednom (unija poligona, bez dvostrukog brojanja)."""
    if len(pozari) == 0:
        return [0.0] * len(tocke)
    unija = pozari.geometry.union_all()
    rez = []
    for p in tocke:
        krug = p.buffer(radijus_m)
        rez.append(round(krug.intersection(unija).area / krug.area, 4))
    return rez


def min_max(v: list[float]) -> list[float]:
    a = np.array(v, dtype=float)
    lo, hi = np.nanmin(a), np.nanmax(a)
    if hi - lo <= 0:
        return [0.0] * len(v)
    return [round(float(x), 4) for x in (a - lo) / (hi - lo)]


def h_stat(g: list[float | None], p_norm: list[float]) -> list[float | None]:
    return [None if gi is None else round(H_TEZINA_GORIVO * gi + H_TEZINA_POZARI * pi, 3)
            for gi, pi in zip(g, p_norm)]
