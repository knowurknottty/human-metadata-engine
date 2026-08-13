"""Resolve human birth-place text into historically correct chart inputs.

Network geocoding is isolated behind :class:`GeocodingProvider`.  The default
provider uses Open-Meteo, keeps a small process-local TTL cache, and never logs
the submitted place.  Timezone conversion uses ``zoneinfo`` for the exact
local birth date and rejects daylight-saving gaps and folds instead of guessing.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import re
import socket
from threading import Lock
from time import monotonic, sleep
from typing import Any, Callable, Protocol
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "human-metadata-engine/0.7 location-resolution"
MAX_LOCATION_LENGTH = 160


@dataclass(frozen=True)
class ResolvedBirthLocation:
    query: str
    display_name: str
    city: str | None
    region: str | None
    country: str
    country_code: str
    latitude: float
    longitude: float
    timezone_name: str
    utc_offset_hours: float
    local_datetime_iso: str
    utc_datetime_iso: str
    resolution_source: str
    confidence: float | None


@dataclass(frozen=True)
class LocationChoice:
    display_name: str
    city: str | None
    region: str | None
    country: str
    country_code: str
    latitude: float
    longitude: float
    timezone_name: str
    confidence: float | None


@dataclass(frozen=True)
class GeocodingCandidate:
    city: str | None
    region: str | None
    country: str
    country_code: str
    latitude: float
    longitude: float
    timezone_name: str
    population: int | None = None

    @property
    def display_name(self) -> str:
        return ", ".join(part for part in (self.city, self.region, self.country) if part)


class LocationResolutionError(ValueError):
    """Structured, frontend-safe location or local-time failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "location_resolution_failed",
        choices: tuple[LocationChoice, ...] = (),
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.choices = choices
        self.retryable = retryable

    def details(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.choices:
            result["choices"] = [asdict(choice) for choice in self.choices]
        if self.retryable:
            result["retryable"] = True
        return result


class GeocodingProvider(Protocol):
    source: str

    def search(self, query: str, *, timeout: float) -> list[GeocodingCandidate]: ...


class GeocodingCache:
    """Bounded process-local cache for successful provider responses."""

    def __init__(self, *, max_entries: int = 256, ttl_seconds: float = 86400.0) -> None:
        if max_entries < 1 or ttl_seconds <= 0:
            raise ValueError("Cache limits must be positive.")
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._entries: OrderedDict[str, tuple[float, tuple[GeocodingCandidate, ...]]] = OrderedDict()
        self._lock = Lock()

    def get(self, query: str) -> list[GeocodingCandidate] | None:
        now = monotonic()
        with self._lock:
            item = self._entries.get(query)
            if item is None:
                return None
            expires_at, candidates = item
            if expires_at <= now:
                del self._entries[query]
                return None
            self._entries.move_to_end(query)
            return list(candidates)

    def put(self, query: str, candidates: list[GeocodingCandidate]) -> None:
        if not candidates:
            return
        with self._lock:
            self._entries[query] = (monotonic() + self.ttl_seconds, tuple(candidates))
            self._entries.move_to_end(query)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


def normalize_location_query(raw: Any) -> str:
    if not isinstance(raw, str):
        raise LocationResolutionError(
            "Birth location must be text.", code="invalid_location_query"
        )
    query = unicodedata.normalize("NFC", raw)
    query = re.sub(r"\s+", " ", query).strip()
    query = re.sub(r"\s*[,;]\s*", ", ", query).strip(" ,")
    if len(query) < 2:
        raise LocationResolutionError(
            "Enter a city, town, or postal code for birth location.",
            code="invalid_location_query",
        )
    if len(query) > MAX_LOCATION_LENGTH:
        raise LocationResolutionError(
            f"Birth location is too long (max {MAX_LOCATION_LENGTH} characters).",
            code="invalid_location_query",
        )
    if any(unicodedata.category(char) in {"Cc", "Cf"} for char in query):
        raise LocationResolutionError(
            "Birth location contains unsupported control characters.",
            code="invalid_location_query",
        )
    return query


def _fetch_json(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310: fixed HTTPS endpoint
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        retryable = exc.code == 429 or 500 <= exc.code <= 599
        raise LocationResolutionError(
            "The location lookup service returned an error.",
            code="location_provider_unavailable" if retryable else "location_provider_rejected",
            retryable=retryable,
        ) from exc
    except (TimeoutError, socket.timeout, URLError) as exc:
        raise LocationResolutionError(
            "The location lookup service timed out or could not be reached.",
            code="location_provider_unavailable",
            retryable=True,
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocationResolutionError(
            "The location lookup returned malformed JSON.",
            code="malformed_location_provider_response",
        ) from exc
    if not isinstance(payload, dict):
        raise LocationResolutionError(
            "The location lookup returned an invalid response.",
            code="malformed_location_provider_response",
        )
    return payload


def _parse_candidates(payload: dict[str, Any]) -> list[GeocodingCandidate]:
    results = payload.get("results", [])
    if results is None:
        results = []
    if not isinstance(results, list):
        raise LocationResolutionError(
            "The location lookup returned an invalid results list.",
            code="malformed_location_provider_response",
        )
    candidates: list[GeocodingCandidate] = []
    malformed = 0
    for item in results:
        if not isinstance(item, dict):
            malformed += 1
            continue
        try:
            latitude = float(item["latitude"])
            longitude = float(item["longitude"])
            timezone_name = str(item["timezone"]).strip()
            country = str(item["country"]).strip()
            country_code = str(item.get("country_code", "")).strip().upper()
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError("coordinate out of range")
            if not timezone_name or not country:
                raise ValueError("missing required provider field")
            population_raw = item.get("population")
            population = int(population_raw) if population_raw not in (None, "") else None
        except (KeyError, TypeError, ValueError):
            malformed += 1
            continue
        candidates.append(GeocodingCandidate(
            city=str(item.get("name") or "").strip() or None,
            region=str(item.get("admin1") or "").strip() or None,
            country=country,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            timezone_name=timezone_name,
            population=population,
        ))
    if results and not candidates and malformed:
        raise LocationResolutionError(
            "The location lookup returned no usable location records.",
            code="malformed_location_provider_response",
        )
    return candidates


class OpenMeteoGeocodingProvider:
    source = "open-meteo-geocoding"

    def __init__(
        self,
        *,
        fetch_json: Callable[[str, float], dict[str, Any]] = _fetch_json,
        retries: int = 1,
        cache: GeocodingCache | None = None,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if not 0 <= retries <= 3:
            raise ValueError("Geocoding retries must be between 0 and 3.")
        self.fetch_json = fetch_json
        self.retries = retries
        self.cache = cache
        self.sleeper = sleeper

    def _request(self, query: str, timeout: float) -> list[GeocodingCandidate]:
        params = urlencode({"name": query, "count": 10, "language": "en", "format": "json"})
        last_error: LocationResolutionError | None = None
        for attempt in range(self.retries + 1):
            try:
                payload = self.fetch_json(f"{GEOCODING_URL}?{params}", timeout)
                if not isinstance(payload, dict):
                    raise LocationResolutionError(
                        "The location lookup returned an invalid response.",
                        code="malformed_location_provider_response",
                    )
                return _parse_candidates(payload)
            except LocationResolutionError as exc:
                last_error = exc
            except (TimeoutError, socket.timeout, URLError) as exc:
                last_error = LocationResolutionError(
                    "The location lookup service timed out or could not be reached.",
                    code="location_provider_unavailable",
                    retryable=True,
                )
            except Exception as exc:
                raise LocationResolutionError(
                    "The location lookup provider failed unexpectedly.",
                    code="location_provider_unavailable",
                    retryable=True,
                ) from exc
            if not last_error.retryable or attempt >= self.retries:
                raise last_error
            self.sleeper(0.15 * (attempt + 1))
        raise last_error or AssertionError("unreachable")

    def search(self, query: str, *, timeout: float) -> list[GeocodingCandidate]:
        cached = self.cache.get(query) if self.cache else None
        if cached is not None:
            return cached
        candidates = self._request(query, timeout)
        # Open-Meteo often handles the city token better than a complete
        # "city, region, country" string. Ranking still uses the full query.
        if not candidates and "," in query:
            city_query = query.split(",", 1)[0].strip()
            candidates = self._request(city_query, timeout)
        if self.cache:
            self.cache.put(query, candidates)
        return candidates


_DEFAULT_CACHE = GeocodingCache()
_DEFAULT_PROVIDER = OpenMeteoGeocodingProvider(cache=_DEFAULT_CACHE)


def _normalized_match_text(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _country_token(value: str) -> str:
    normalized = _normalized_match_text(value).replace(" ", "")
    if normalized in {"usa", "us", "unitedstates", "unitedstatesofamerica"}:
        return "us"
    if normalized in {"uk", "unitedkingdom", "greatbritain"}:
        return "gb"
    return normalized


def _score_candidate(query: str, candidate: GeocodingCandidate) -> tuple[float, int]:
    query_parts = [part.strip() for part in query.split(",") if part.strip()]
    city_query = _normalized_match_text(query_parts[0] if query_parts else query)
    city = _normalized_match_text(candidate.city)
    score = 0.0
    if city_query == city:
        score += 0.55
    elif city_query and (city_query in city or city in city_query):
        score += 0.35
    region = _normalized_match_text(candidate.region)
    country = _normalized_match_text(candidate.country)
    country_code = _country_token(candidate.country_code)
    for qualifier in query_parts[1:]:
        normalized = _normalized_match_text(qualifier)
        if normalized and normalized == region:
            score += 0.25
        elif _country_token(qualifier) in {country_code, _country_token(country)}:
            score += 0.15
        elif normalized and (normalized in region or normalized in country):
            score += 0.10
    return min(score, 1.0), candidate.population or 0


def _choice(candidate: GeocodingCandidate, confidence: float | None) -> LocationChoice:
    return LocationChoice(
        display_name=candidate.display_name,
        city=candidate.city,
        region=candidate.region,
        country=candidate.country,
        country_code=candidate.country_code,
        latitude=candidate.latitude,
        longitude=candidate.longitude,
        timezone_name=candidate.timezone_name,
        confidence=confidence,
    )


def _select_candidate(query: str, candidates: list[GeocodingCandidate]) -> tuple[GeocodingCandidate, float]:
    if not candidates:
        raise LocationResolutionError(
            f"No location match was found for {query!r}.", code="location_not_found"
        )
    ranked = sorted(
        ((candidate, *_score_candidate(query, candidate)) for candidate in candidates),
        key=lambda item: (item[1], item[2]),
        reverse=True,
    )
    top, top_score, _ = ranked[0]
    qualifiers = [part for part in query.split(",") if part.strip()][1:]
    distinct_places = {
        (_normalized_match_text(item.city), _normalized_match_text(item.region), item.country_code)
        for item, _, _ in ranked
    }
    tied = len(ranked) > 1 and abs(top_score - ranked[1][1]) < 0.10
    ambiguous = (not qualifiers and len(distinct_places) > 1) or top_score < 0.55 or tied
    if ambiguous:
        choices = tuple(_choice(item, round(score, 3)) for item, score, _ in ranked[:5])
        raise LocationResolutionError(
            "More than one location matches. Choose a city and region from the provided options.",
            code="ambiguous_location",
            choices=choices,
        )
    return top, round(top_score, 3)


def resolve_local_datetime(
    timezone_name: str,
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> tuple[datetime, datetime]:
    """Resolve one local wall time, rejecting DST gaps and ambiguous folds."""
    try:
        naive = datetime(year, month, day, hour, minute)
    except (TypeError, ValueError) as exc:
        raise LocationResolutionError(
            f"Birth date or time is invalid: {exc}.", code="invalid_birth_datetime"
        ) from exc
    try:
        zone = ZoneInfo(timezone_name)
    except (TypeError, ZoneInfoNotFoundError) as exc:
        raise LocationResolutionError(
            "The supplied IANA timezone is not recognized.", code="invalid_timezone"
        ) from exc

    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    first_utc = first.astimezone(timezone.utc)
    second_utc = second.astimezone(timezone.utc)
    first_valid = first_utc.astimezone(zone).replace(tzinfo=None) == naive
    second_valid = second_utc.astimezone(zone).replace(tzinfo=None) == naive
    if not first_valid and not second_valid:
        raise LocationResolutionError(
            "That local birth time did not exist because the clock moved forward. Enter a valid local time.",
            code="nonexistent_local_time",
        )
    if first_valid and second_valid and first.utcoffset() != second.utcoffset():
        raise LocationResolutionError(
            "That local birth time occurred twice because the clock moved backward. Provide an unambiguous time.",
            code="ambiguous_local_time",
        )
    local = first if first_valid else second
    return local, local.astimezone(timezone.utc)


def resolve_birth_location(
    location: str,
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timeout: float = 5.0,
    provider: GeocodingProvider | None = None,
    fetch_json: Callable[[str, float], dict[str, Any]] | None = None,
) -> ResolvedBirthLocation:
    """Resolve coordinates, IANA timezone, and date-specific UTC offset."""
    query = normalize_location_query(location)
    # Validate the calendar before transmitting a place to an external service.
    try:
        datetime(year, month, day, hour, minute)
    except (TypeError, ValueError) as exc:
        raise LocationResolutionError(
            f"Birth date or time is invalid: {exc}.", code="invalid_birth_datetime"
        ) from exc
    if timeout <= 0 or timeout > 30:
        raise LocationResolutionError(
            "Location lookup timeout must be between 0 and 30 seconds.",
            code="invalid_location_timeout",
        )
    if provider is not None and fetch_json is not None:
        raise ValueError("Pass provider or fetch_json, not both.")
    active_provider: GeocodingProvider
    if provider is not None:
        active_provider = provider
    elif fetch_json is not None:
        active_provider = OpenMeteoGeocodingProvider(fetch_json=fetch_json, retries=0)
    else:
        active_provider = _DEFAULT_PROVIDER
    candidates = active_provider.search(query, timeout=timeout)
    candidate, confidence = _select_candidate(query, candidates)
    local, utc = resolve_local_datetime(
        candidate.timezone_name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
    )
    offset = local.utcoffset()
    if offset is None:
        raise LocationResolutionError(
            "The matched timezone has no UTC offset for that date.", code="invalid_timezone"
        )
    return ResolvedBirthLocation(
        query=query,
        display_name=candidate.display_name,
        city=candidate.city,
        region=candidate.region,
        country=candidate.country,
        country_code=candidate.country_code,
        latitude=candidate.latitude,
        longitude=candidate.longitude,
        timezone_name=candidate.timezone_name,
        utc_offset_hours=offset.total_seconds() / 3600.0,
        local_datetime_iso=local.isoformat(),
        utc_datetime_iso=utc.isoformat().replace("+00:00", "Z"),
        resolution_source=active_provider.source,
        confidence=confidence,
    )


__all__ = [
    "GeocodingCache",
    "GeocodingCandidate",
    "GeocodingProvider",
    "LocationChoice",
    "LocationResolutionError",
    "OpenMeteoGeocodingProvider",
    "ResolvedBirthLocation",
    "normalize_location_query",
    "resolve_birth_location",
    "resolve_local_datetime",
]
