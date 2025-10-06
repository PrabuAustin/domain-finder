import os
import time
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GODADDY_API_KEY = os.getenv("GODADDY_API_KEY", "")
GODADDY_API_SECRET = os.getenv("GODADDY_API_SECRET", "")
GODADDY_ENV = os.getenv("GODADDY_ENV", "PROD").upper()  # PROD or OTE

DOMAINR_API_KEY = os.getenv("DOMAINR_API_KEY", "")

BASE_URL_PROD = "https://api.godaddy.com"
BASE_URL_OTE = "https://api.ote-godaddy.com"

# Respect ~60 requests/min per endpoint. We'll pace to ~1 req/sec by default.
DEFAULT_SLEEP_SECONDS = 1.1


def _godaddy_base_url() -> str:
    return BASE_URL_OTE if GODADDY_ENV == "OTE" else BASE_URL_PROD


def _godaddy_headers() -> dict:
    if not GODADDY_API_KEY or not GODADDY_API_SECRET:
        raise RuntimeError("Missing GoDaddy credentials: set GODADDY_API_KEY and GODADDY_API_SECRET")
    return {
        "Accept": "application/json",
        "Authorization": f"sso-key {GODADDY_API_KEY}:{GODADDY_API_SECRET}",
    }


def godaddy_is_available(domain: str, check_type: str = "FAST", timeout: int = 10) -> bool:
    """Call GoDaddy availability endpoint for a single domain.

    check_type: FAST or FULL
    """
    url = f"{_godaddy_base_url()}/v1/domains/available"
    params = {"domain": domain, "checkType": check_type}
    resp = requests.get(url, headers=_godaddy_headers(), params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json() or {}
    return bool(data.get("available"))


def godaddy_find_available(domains: Iterable[str], check_type: str = "FAST", sleep_seconds: float = DEFAULT_SLEEP_SECONDS) -> List[str]:
    available: List[str] = []
    for d in domains:
        try:
            if godaddy_is_available(d, check_type=check_type):
                available.append(d)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                time.sleep(2.0)  # simple backoff on rate limit
                continue
        time.sleep(sleep_seconds)
    return available


# Optional Domainr prefilter: quick status checks across many TLDs
# Domainr docs: https://domainr.com

def domainr_status(domain: str, timeout: int = 10) -> Optional[str]:
    if not DOMAINR_API_KEY:
        return None
    url = "https://api.domainr.com/v2/status"
    params = {"mashape-key": DOMAINR_API_KEY, "domain": domain}
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json() or {}
    # Expect shape {"status":[{"domain":"example.com","status":"active|inactive|undelegated|unknown|parked|etc"}]} 
    try:
        return data.get("status", [{}])[0].get("status")
    except Exception:
        return None


def domainr_prefilter(domains: Iterable[str]) -> List[str]:
    """Return domains that appear available-ish per Domainr.

    We keep domains whose status does NOT include strings like 'active' or 'taken'.
    Exact semantics vary; this is just a fast prefilter before registrar verification.
    """
    if not DOMAINR_API_KEY:
        return list(domains)

    result: List[str] = []
    for d in domains:
        try:
            status = domainr_status(d)
            # If status suggests taken (e.g., 'active'), skip; else keep
            if not status or ("active" not in status and "taken" not in status):
                result.append(d)
        except requests.HTTPError:
            # If Domainr fails, just include; we'll verify at GoDaddy anyway
            result.append(d)
        time.sleep(0.2)  # be gentle
    return result
