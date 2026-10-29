"""EFFIS (Copernicus EMS / JRC, CC BY 4.0): dnevni FWI (WMS) i opožarene površine (WFS).

Nalazi probe (28.10.2026., docs/probe_report.md):
- FWI sloj se zove mf010.fwi (stari ecmwf007.fwi više ne postoji); TIME je obavezan,
  zadana vrijednost je ~3 dana unaprijed (prognoza).
- GetMap s format=image/tiff vraća float32 VRIJEDNOSTI FWI-ja (ne RGB), pa raster
  uzorkujemo u točkama naselja. GetFeatureInfo za mf010.fwi nije podržan.
- WFS ms:modis.ba.poly: bbox mora biti „lon,lat,lon,lat“ BEZ oznake CRS-a
  (s ",EPSG:4326" MapServer očekuje lat,lon i vraća prazno).
"""
from __future__ import annotations

import json

import geopandas as gpd
import numpy as np
import rasterio

from etl import http, izvori
from etl.config import CRS_ANALIZA, EFFIS_BA_SLOJ, EFFIS_FWI_SLOJ, EFFIS_WMS, FWI_RAZREDI, RAW_DIR

KORAK_STUPNJA = 0.01  # rezolucija koju tražimo u GetMap (≈ 1 km); izvorni model je grublji


def fwi_raster(datum: str, bbox: tuple[float, float, float, float], osvjezi: bool = False):
    """GeoTIFF FWI-ja za datum (YYYY-MM-DD) i bbox (lon/lat). Vraća putanju."""
    x0, y0, x1, y1 = bbox
    sirina = int(round((x1 - x0) / KORAK_STUPNJA))
    visina = int(round((y1 - y0) / KORAK_STUPNJA))
    params = {"service": "WMS", "version": "1.1.1", "request": "GetMap", "layers": EFFIS_FWI_SLOJ,
              "srs": "EPSG:4326", "bbox": f"{x0},{y0},{x1},{y1}", "width": sirina, "height": visina,
              "format": "image/tiff", "time": datum, "styles": ""}
    put = RAW_DIR / "effis" / f"fwi_{datum}_{x0:.2f}_{y0:.2f}_{x1:.2f}_{y1:.2f}.tif"
    put = http.preuzmi(EFFIS_WMS, put, params=params, osvjezi=osvjezi, timeout=180)
    with open(put, "rb") as f:
        if f.read(4) not in (b"II*\x00", b"MM\x00*"):
            put.unlink()
            raise RuntimeError(f"EFFIS nije vratio GeoTIFF za {datum} (vjerojatno pogreška servisa)")
    izvori.zabiljezi("effis_fwi", url=http.puni_url(EFFIS_WMS, params), dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    return put


def fwi_u_tockama(put, lonlat: list[tuple[float, float]]) -> list[float | None]:
    """Vrijednost FWI-ja u točkama (najbliži piksel). Ako je piksel prazan (more), uzmi max u 3×3."""
    with rasterio.open(put) as ds:
        a = ds.read(1)
        rez = []
        for lon, lat in lonlat:
            r, c = ds.index(lon, lat)
            if not (0 <= r < a.shape[0] and 0 <= c < a.shape[1]):
                rez.append(None)
                continue
            v = a[r, c]
            if not np.isfinite(v) or v <= 0:
                okolica = a[max(0, r - 1):r + 2, max(0, c - 1):c + 2]
                okolica = okolica[np.isfinite(okolica) & (okolica > 0)]
                v = okolica.max() if okolica.size else np.nan
            rez.append(None if not np.isfinite(v) else round(float(v), 1))
        return rez


def razred_fwi(v: float | None) -> str | None:
    """Razred prema EFFIS legendi (GetLegendGraphic za mf010.fwi)."""
    if v is None:
        return None
    oznaka = FWI_RAZREDI[0][1]
    for donja, ime in FWI_RAZREDI:
        if v >= donja:
            oznaka = ime
    return oznaka


def opozarene_povrsine(bbox: tuple[float, float, float, float], osvjezi: bool = False) -> gpd.GeoDataFrame:
    """Opožarene površine (EFFIS, MODIS/VIIRS, ~≥30 ha) u bboxu, EPSG:3765."""
    x0, y0, x1, y1 = bbox
    params = {"service": "WFS", "version": "1.1.0", "request": "GetFeature", "typename": EFFIS_BA_SLOJ,
              "bbox": f"{x0},{y0},{x1},{y1}", "outputformat": "geojson", "maxfeatures": 100000}
    put = RAW_DIR / "effis_ba" / f"ba_{x0:.2f}_{y0:.2f}_{x1:.2f}_{y1:.2f}.geojson"
    put = http.preuzmi(EFFIS_WMS, put, params=params, osvjezi=osvjezi, timeout=600)
    js = json.loads(put.read_text(encoding="utf-8"))
    izvori.zabiljezi("effis_ba", url=http.puni_url(EFFIS_WMS, params), dohvaceno=http.dohvati_meta(put).get("dohvaceno"))
    if not js.get("features"):
        return gpd.GeoDataFrame({"FIREDATE": [], "AREA_HA": []}, geometry=[], crs=CRS_ANALIZA)
    gdf = gpd.GeoDataFrame.from_features(js["features"], crs="EPSG:4326").to_crs(CRS_ANALIZA)
    gdf["geometry"] = gdf.geometry.make_valid()
    return gdf
