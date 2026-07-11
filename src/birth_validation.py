"""Canonical validation for birth-dependent encoders.

The web product analyzes living people, so its public input boundary deliberately
rejects three-digit years and future dates. Internal historical datasets may use
``validate_birth(..., living_person=False)`` when pre-1900 dates are intentional.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


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


def validate_birth(
    raw: dict[str, Any] | None,
    *,
    living_person: bool = True,
    current_year: int | None = None,
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
        raise BirthValidationError(f"Invalid birth date: {exc}.") from exc

    hour = int(raw.get("hour", 12))
    minute = int(raw.get("minute", 0))
    timezone_offset = float(raw.get("timezone_offset", 0))
    if not 0 <= hour <= 23:
        raise BirthValidationError("Birth hour must be between 0 and 23.")
    if not 0 <= minute <= 59:
        raise BirthValidationError("Birth minute must be between 0 and 59.")
    if not -14 <= timezone_offset <= 14:
        raise BirthValidationError("UTC offset must be between -14 and +14.")

    birth: dict[str, Any] = {
        "year": canonical_date.year,
        "month": canonical_date.month,
        "day": canonical_date.day,
        "hour": hour,
        "minute": minute,
        "timezone_offset": timezone_offset,
        "location": str(raw.get("location", ""))[:120],
    }

    lat = raw.get("lat")
    lon = raw.get("lon")
    if (lat in (None, "")) != (lon in (None, "")):
        raise BirthValidationError("Latitude and longitude must be supplied together.")
    if lat not in (None, ""):
        birth["lat"] = float(lat)
        birth["lon"] = float(lon)
        if not -90 <= birth["lat"] <= 90:
            raise BirthValidationError("Latitude must be between -90 and 90.")
        if not -180 <= birth["lon"] <= 180:
            raise BirthValidationError("Longitude must be between -180 and 180.")

    return birth


def canonical_birth_record(birth: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a compact user-visible record of exactly what was analyzed."""
    if not birth:
        return None
    return {
        "date": f"{birth['year']:04d}-{birth['month']:02d}-{birth['day']:02d}",
        "time": f"{birth['hour']:02d}:{birth['minute']:02d}",
        "timezone_offset": birth["timezone_offset"],
        "location": birth.get("location", ""),
        "latitude": birth.get("lat"),
        "longitude": birth.get("lon"),
    }
