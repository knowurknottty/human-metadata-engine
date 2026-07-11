"""Shared validation for user-supplied birth data.

The web application and legacy HTTP API must apply the same constraints so a
birth payload cannot be accepted by one surface and silently ignored by
another.
"""

from __future__ import annotations

from datetime import date
import math


def validate_birth(raw: object) -> dict | None:
    """Validate and normalize the canonical ``birth`` request object.

    A date-only request is allowed when ``time_accuracy`` is ``unknown``. It
    deliberately retains noon only as a deterministic calculation placeholder;
    the engine withholds time-sensitive output in that case.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("Birth data must be an object.")
    required = ("year", "month", "day", "timezone_offset", "lat", "lon")
    missing = [field for field in required if raw.get(field) in (None, "")]
    if missing:
        raise ValueError("Birth data requires " + ", ".join(missing) + ".")
    try:
        birth = {
            "year": int(raw["year"]),
            "month": int(raw["month"]),
            "day": int(raw["day"]),
            "hour": int(raw.get("hour", 12)),
            "minute": int(raw.get("minute", 0)),
            "timezone_offset": float(raw["timezone_offset"]),
            "location": str(raw.get("location", "")).strip()[:120],
            "lat": float(raw["lat"]),
            "lon": float(raw["lon"]),
        }
    except (TypeError, ValueError) as exc:
        raise ValueError("Birth data contains an invalid number.") from exc
    try:
        date(birth["year"], birth["month"], birth["day"])
    except ValueError as exc:
        raise ValueError("Birth date is not a real calendar date.") from exc
    if not 0 <= birth["hour"] <= 23:
        raise ValueError("Birth hour must be between 0 and 23.")
    if not 0 <= birth["minute"] <= 59:
        raise ValueError("Birth minute must be between 0 and 59.")
    if not math.isfinite(birth["timezone_offset"]) or not -14 <= birth["timezone_offset"] <= 14:
        raise ValueError("UTC offset must be between -14 and +14.")
    if not math.isfinite(birth["lat"]) or not math.isfinite(birth["lon"]):
        raise ValueError("Latitude and longitude must be finite numbers.")
    if not -90 <= birth["lat"] <= 90 or not -180 <= birth["lon"] <= 180:
        raise ValueError("Latitude or longitude is outside its valid range.")
    birth["time_accuracy"] = "provided" if raw.get("time_accuracy") == "provided" else "unknown"
    if not birth["location"]:
        birth["location"] = f"{birth['lat']:.4f}, {birth['lon']:.4f}"
    return birth
