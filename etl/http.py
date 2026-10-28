"""Zajednički HTTP klijent za sve izvore.

Zašto poseban modul: pravila natječaja i dobra praksa traže da se predstavimo
(User-Agent), da ne opterećujemo javne servise (najviše 2 zahtjeva u sekundi
po poslužitelju) i da ista preuzimanja ne ponavljamo (cache u data/raw/).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from etl.config import HTTP_MIN_RAZMAK_S, HTTP_TIMEOUT_S, HTTP_USER_AGENT, RAW_DIR

_session: requests.Session | None = None
_zadnji_zahtjev: dict[str, float] = {}


def session() -> requests.Session:
    """Vrati dijeljenu Session s User-Agentom i ponovnim pokušajima (3×, backoff)."""
    global _session
    if _session is None:
        s = requests.Session()
        s.headers["User-Agent"] = HTTP_USER_AGENT
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "HEAD"),
        )
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.mount("http://", HTTPAdapter(max_retries=retry))
        _session = s
    return _session


def _pricekaj(url: str) -> None:
    """Drži razmak između zahtjeva prema istom poslužitelju (≤ 2 zahtjeva/s)."""
    host = urlparse(url).netloc
    proteklo = time.monotonic() - _zadnji_zahtjev.get(host, 0.0)
    if proteklo < HTTP_MIN_RAZMAK_S:
        time.sleep(HTTP_MIN_RAZMAK_S - proteklo)
    _zadnji_zahtjev[host] = time.monotonic()


def get(url: str, params: dict | None = None, stream: bool = False, timeout: float | None = None) -> requests.Response:
    """GET bez cachea (za probe, gdje želimo vidjeti stvarni HTTP odgovor)."""
    _pricekaj(url)
    return session().get(url, params=params, timeout=timeout or HTTP_TIMEOUT_S, stream=stream)


def head(url: str) -> requests.Response:
    _pricekaj(url)
    return session().head(url, timeout=HTTP_TIMEOUT_S, allow_redirects=True)


def puni_url(url: str, params: dict | None) -> str:
    return url if not params else f"{url}{'&' if '?' in url else '?'}{urlencode(params)}"


def preuzmi(url: str, odrediste: Path, params: dict | None = None, osvjezi: bool = False,
            timeout: float | None = None) -> Path:
    """Preuzmi datoteku u odrediste (stream) i preskoči ako već postoji.

    Uz datoteku spremamo i <ime>.meta.json s URL-om i vremenom dohvata, jer
    meta.json projekta mora navesti kada je svaki izvor dohvaćen.
    """
    odrediste = Path(odrediste)
    if odrediste.exists() and not osvjezi:
        return odrediste
    odrediste.parent.mkdir(parents=True, exist_ok=True)
    _pricekaj(url)
    with session().get(url, params=params, stream=True, timeout=timeout or HTTP_TIMEOUT_S) as r:
        r.raise_for_status()
        privremena = odrediste.with_suffix(odrediste.suffix + ".part")
        with open(privremena, "wb") as f:
            for komad in r.iter_content(chunk_size=1 << 20):
                f.write(komad)
        privremena.replace(odrediste)
        meta = {
            "url": puni_url(url, params),
            "dohvaceno": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "http_status": r.status_code,
            "content_type": r.headers.get("Content-Type"),
            "last_modified": r.headers.get("Last-Modified"),
            "velicina_b": odrediste.stat().st_size,
        }
    odrediste.with_name(odrediste.name + ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return odrediste


def cache_put(izvor: str, url: str, params: dict | None = None, nastavak: str = "") -> Path:
    """Putanja u data/raw/<izvor>/ izvedena iz URL-a (hash), za cache odgovora."""
    kljuc = hashlib.sha1(puni_url(url, params).encode("utf-8")).hexdigest()[:16]
    return RAW_DIR / izvor / f"{kljuc}{nastavak}"


def dohvati_meta(putanja: Path) -> dict:
    """Pročitaj .meta.json uz preuzetu datoteku (ili prazan dict)."""
    m = Path(str(putanja) + ".meta.json")
    return json.loads(m.read_text(encoding="utf-8")) if m.exists() else {}
