"""Feature 2: IP Geolocation using ip-api.com (free, no key required)."""

import httpx
from typing import Optional
from app.utils.logger import get_logger

log = get_logger(__name__)

GEO_URL = "http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"

# Simple in-process cache to avoid hammering the free API
_cache: dict[str, dict] = {}


async def get_geo(ip: str) -> dict:
    """Return {country, city, lat, lon} for *ip*, or empty dict on failure."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return {}
    if ip in _cache:
        return _cache[ip]
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(GEO_URL.format(ip=ip))
            data = r.json()
            if data.get("status") == "success":
                result = {
                    "country": data.get("country"),
                    "city":    data.get("city"),
                    "lat":     data.get("lat"),
                    "lon":     data.get("lon"),
                }
                _cache[ip] = result
                return result
    except Exception as exc:
        log.debug("Geo lookup failed for %s: %s", ip, exc)
    return {}


def get_geo_sync(ip: str) -> dict:
    """Synchronous version (used in background threads)."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return {}
    if ip in _cache:
        return _cache[ip]
    try:
        import httpx as _httpx
        with _httpx.Client(timeout=3.0) as client:
            r = client.get(GEO_URL.format(ip=ip))
            data = r.json()
            if data.get("status") == "success":
                result = {
                    "country": data.get("country"),
                    "city":    data.get("city"),
                    "lat":     data.get("lat"),
                    "lon":     data.get("lon"),
                }
                _cache[ip] = result
                return result
    except Exception as exc:
        log.debug("Geo lookup (sync) failed for %s: %s", ip, exc)
    return {}
