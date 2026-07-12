"""Resolve a human-entered birth place into chart inputs.

The public form accepts a place name instead of asking users to calculate
coordinates or UTC offsets. Open-Meteo's free geocoding endpoint returns WGS84
coordinates and an IANA timezone; ``zoneinfo`` then derives the historical
offset for the supplied birth date and local time.
"""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "human-metadata-engine/0.6 location-resolution"


class LocationResolutionError(ValueError):
    """Raised when a place cannot be safely resolved for chart calculation."""


def _fetch_json(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310: fixed HTTPS endpoint
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network and malformed upstream responses are one public failure
        raise LocationResolutionError("The location lookup service could not be reached.") from exc
    if not isinstance(payload, dict):
        raise LocationResolutionError("The location lookup returned an invalid response.")
    return payload


def resolve_birth_location(
    location: str,
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timeout: float = 5.0,
    fetch_json: Callable[[str, float], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return coordinates, IANA timezone, and date-specific UTC offset.

    The caller's place string is sent to the configured geocoder. The returned
    display label is retained only for the current analysis request; callers
    must not persist it as a user profile.
    """
    query = str(location or "").strip()
    if len(query) < 2:
        raise LocationResolutionError("Enter a city, town, or postal code for birth location.")
    fetch = fetch_json or _fetch_json
    params = urlencode({"name": query, "count": 5, "language": "en", "format": "json"})
    payload = fetch(f"{GEOCODING_URL}?{params}", timeout)
    results = payload.get("results")
    # Some place-name searches are more reliable without a country suffix.
    if not results and "," in query:
        fallback = query.split(",", 1)[0].strip()
        if len(fallback) >= 2:
            params = urlencode({"name": fallback, "count": 5, "language": "en", "format": "json"})
            payload = fetch(f"{GEOCODING_URL}?{params}", timeout)
            results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise LocationResolutionError(f"No location match was found for {query!r}.")

    candidate = next((item for item in results if isinstance(item, dict) and item.get("timezone")), None)
    if not candidate:
        raise LocationResolutionError("The matched location has no timezone data.")
    try:
        latitude = float(candidate["latitude"])
        longitude = float(candidate["longitude"])
        timezone_name = str(candidate["timezone"])
        local = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(timezone_name))
        offset = local.utcoffset()
        if offset is None:
            raise ValueError("timezone offset unavailable")
        timezone_offset = offset.total_seconds() / 3600
    except Exception as exc:
        raise LocationResolutionError("The matched location could not produce a valid chart timezone.") from exc

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone_name": timezone_name,
        "timezone_offset": timezone_offset,
        "location": ", ".join(str(candidate.get(key)) for key in ("name", "admin1", "country") if candidate.get(key)),
        "geocoder": "open-meteo-geocoding",
    }


__all__ = ["LocationResolutionError", "resolve_birth_location"]
