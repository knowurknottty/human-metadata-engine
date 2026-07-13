"""Canonical validation for birth-dependent encoders.

The web product analyzes living people, so its public input boundary deliberately
rejects three-digit years and future dates. Internal historical datasets may use
``validate_birth(..., living_person=False)`` when pre-1900 dates are intentional.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import math
from typing import Any

# ``provided`` remains accepted for older internal callers; public clients
# should use ``exact``. It is deliberately not inferred when the field is
# omitted.
TIME_ACCURACIES = {"unknown", "hour_only", "approximate", "exact", "provided"}


class BirthValidationError(ValueError):
    """Raised when birth input cannot be safely normalized."""


def _required_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if value in (None, ""):
        raise BirthValidationError(f"Birth {field} is required.")
    if isinstance(value, bool):
        raise BirthValidationError(f"Birth {field} must be an integer.")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise BirthValidationError(f"Birth {field} must be an integer.") from exc
    if str(value).strip().lstrip("+-").isdigit() is False and not isinstance(value, int):
        raise BirthValidationError(f"Birth {field} must be an integer.")
    return parsed


def validate_birth_datetime_fields(
    raw: dict[str, Any],
    *,
    living_person: bool = True,
    current_year: int | None = None,
) -> dict[str, Any]:
    """Validate calendar and local-clock fields before any location lookup."""
    if not isinstance(raw, dict):
        raise BirthValidationError("Birth data must be a JSON object.")
    year = _required_int(raw, "year")
    month = _required_int(raw, "month")
    day = _required_int(raw, "day")
    now_year = current_year or datetime.now(timezone.utc).year
    minimum_year = 1900 if living_person else 1
    if year < minimum_year:
        if living_person:
            raise BirthValidationError(
                f"Birth year must be four digits between {minimum_year} and {now_year}; received {year}."
            )
        raise BirthValidationError("Birth year must be between 1 and 9999.")
    if year > now_year:
        raise BirthValidationError(f"Birth year cannot be later than {now_year}.")
    try:
        canonical_date = date(year, month, day)
    except ValueError as exc:
        raise BirthValidationError(f"Invalid birth date; birth date is not a real calendar date: {exc}.") from exc

    time_accuracy = raw.get("time_accuracy", "provided")
    if time_accuracy not in TIME_ACCURACIES:
        raise BirthValidationError(
            "time_accuracy must be one of: unknown, hour_only, approximate, exact."
        )
    try:
        hour = int(raw.get("hour", 12))
        minute = int(raw.get("minute", 0))
    except (TypeError, ValueError) as exc:
        raise BirthValidationError("Birth time must be numeric.") from exc
    if not 0 <= hour <= 23:
        raise BirthValidationError("Birth hour must be between 0 and 23.")
    if not 0 <= minute <= 59:
        raise BirthValidationError("Birth minute must be between 0 and 59.")
    return {
        "year": canonical_date.year,
        "month": canonical_date.month,
        "day": canonical_date.day,
        "hour": hour,
        "minute": minute,
        "time_accuracy": time_accuracy,
    }


def validate_birth(
    raw: dict[str, Any] | None,
    *,
    living_person: bool = True,
    current_year: int | None = None,
    require_coordinates: bool = False,
) -> dict[str, Any] | None:
    """Normalize and validate one birth record.

    ``living_person=True`` is the correct mode for the public web form. It
    rejects years before 1900, which prevents accidental values such as 982
    from silently contaminating astrology, Human Design, and temporal systems.
    """
    if not raw:
        return None
    if not isinstance(raw, dict):
        raise BirthValidationError("Birth data must be a JSON object.")
    if require_coordinates and raw.get("timezone_offset") in (None, ""):
        raise BirthValidationError("Birth data requires timezone_offset.")

    clock = validate_birth_datetime_fields(
        raw,
        living_person=living_person,
        current_year=current_year,
    )
    try:
        timezone_offset = float(raw.get("timezone_offset", 0))
    except (TypeError, ValueError) as exc:
        raise BirthValidationError("UTC offset must be numeric.") from exc
    if not math.isfinite(timezone_offset) or not -14 <= timezone_offset <= 14:
        raise BirthValidationError("UTC offset must be between -14 and +14.")

    location = raw.get("location", "")
    if not isinstance(location, str):
        raise BirthValidationError("Birth location must be a string.")
    location = " ".join(location.split()).strip()
    if len(location) > 160:
        raise BirthValidationError("Birth location must be at most 160 characters.")

    birth: dict[str, Any] = {
        **clock,
        "timezone_offset": timezone_offset,
        "location": location,
    }
    timezone_name = raw.get("timezone_name")
    if timezone_name not in (None, ""):
        if not isinstance(timezone_name, str) or len(timezone_name) > 120:
            raise BirthValidationError("timezone_name must be a short IANA timezone string.")
        birth["timezone_name"] = timezone_name
    reliability = raw.get("timezone_reliability")
    if reliability not in (None, ""):
        if reliability not in {"resolved_iana", "verified_iana", "offset_only_unverified"}:
            raise BirthValidationError("timezone_reliability is invalid.")
        birth["timezone_reliability"] = reliability
    resolution_source = raw.get("resolution_source")
    if resolution_source not in (None, ""):
        if not isinstance(resolution_source, str) or len(resolution_source) > 80:
            raise BirthValidationError("resolution_source must be a short string.")
        birth["resolution_source"] = resolution_source

    lat = raw.get("lat")
    lon = raw.get("lon")
    if require_coordinates and (lat in (None, "") or lon in (None, "")):
        missing = "latitude" if lat in (None, "") else "longitude"
        raise BirthValidationError(f"Birth data requires {missing}.")
    if (lat in (None, "")) != (lon in (None, "")):
        raise BirthValidationError("Latitude and longitude must be supplied together.")
    if lat not in (None, ""):
        try:
            birth["lat"] = float(lat)
            birth["lon"] = float(lon)
        except (TypeError, ValueError) as exc:
            raise BirthValidationError("Latitude and longitude must be numeric.") from exc
        if not math.isfinite(birth["lat"]) or not math.isfinite(birth["lon"]):
            raise BirthValidationError("Latitude and longitude must be finite numbers.")
        if not -90 <= birth["lat"] <= 90:
            raise BirthValidationError("Latitude must be between -90 and 90.")
        if not -180 <= birth["lon"] <= 180:
            raise BirthValidationError("Longitude must be between -180 and 180.")
        if not birth["location"]:
            birth["location"] = f"{birth['lat']:.4f}, {birth['lon']:.4f}"

    return birth


def canonical_birth_record(birth: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a compact user-visible record of exactly what was analyzed."""
    if not birth:
        return None
    return {
        "date": f"{birth['year']:04d}-{birth['month']:02d}-{birth['day']:02d}",
        "time": f"{birth['hour']:02d}:{birth['minute']:02d}",
        "time_accuracy": birth.get("time_accuracy", "unknown"),
        "timezone_offset": birth["timezone_offset"],
        "timezone_basis": birth.get("timezone_reliability", "offset_only_unverified"),
        "resolution_source": birth.get("resolution_source", "manual"),
        "location_provided": bool(birth.get("location")),
        "coordinates_provided": "lat" in birth and "lon" in birth,
    }
