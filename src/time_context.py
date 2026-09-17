"""Explicit timezone resolution for signature-v3 timing artifacts."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone, tzinfo
from importlib.metadata import PackageNotFoundError, version
import math
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneResolutionError(ValueError):
    """Raised when civil time cannot be mapped to one unambiguous UTC instant."""


def _tzdata_version() -> str | None:
    try:
        return version("tzdata")
    except PackageNotFoundError:
        return None


def _zone_from_context(context: dict[str, Any]) -> tuple[tzinfo, str, str | None]:
    zone_id = context.get("timezone_id") or context.get("tzid")
    if zone_id:
        try:
            return ZoneInfo(str(zone_id)), "iana_zoneinfo", str(zone_id)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise TimezoneResolutionError(f"Unknown or invalid IANA timezone_id: {zone_id}") from exc
    if "timezone_offset" not in context:
        raise TimezoneResolutionError("Provide timezone_id or timezone_offset.")
    offset = float(context["timezone_offset"])
    if not math.isfinite(offset) or not -14.0 <= offset <= 14.0:
        raise TimezoneResolutionError("timezone_offset must be a finite number between -14 and +14 hours.")
    return timezone(timedelta(hours=offset)), "fixed_utc_offset", None


def _public_basis(resolved: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": resolved["model"],
        "timezone_id": resolved.get("timezone_id"),
        "effective_offset_hours": resolved["effective_offset_hours"],
        "abbreviation": resolved.get("abbreviation"),
        "fold": resolved.get("fold", 0),
        "tzdata_version": resolved.get("tzdata_version"),
    }


def resolve_local_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    context: dict[str, Any],
    *,
    second: int = 0,
) -> dict[str, Any]:
    zone, model, zone_id = _zone_from_context(context)
    naive = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    if model == "fixed_utc_offset":
        aware = naive.replace(tzinfo=zone)
        utc_value = aware.astimezone(timezone.utc)
        return {
            "tzinfo": zone,
            "model": model,
            "timezone_id": None,
            "effective_offset_hours": aware.utcoffset().total_seconds() / 3600.0,
            "abbreviation": aware.tzname(),
            "fold": 0,
            "tzdata_version": None,
            "local_datetime": aware,
            "utc_datetime": utc_value,
        }

    candidates: list[tuple[int, datetime, datetime]] = []
    seen_utc: set[datetime] = set()
    for fold in (0, 1):
        aware = naive.replace(tzinfo=zone, fold=fold)
        utc_value = aware.astimezone(timezone.utc)
        round_trip = utc_value.astimezone(zone)
        if round_trip.replace(tzinfo=None) == naive and utc_value not in seen_utc:
            seen_utc.add(utc_value)
            candidates.append((fold, aware, utc_value))

    if not candidates:
        raise TimezoneResolutionError(
            f"Local time {naive.isoformat(timespec='minutes')} does not exist in {zone_id}; "
            "it falls in a timezone transition gap."
        )

    if len(candidates) > 1:
        if "timezone_fold" not in context:
            raise TimezoneResolutionError(
                f"Local time {naive.isoformat(timespec='minutes')} is ambiguous in {zone_id}; "
                "provide timezone_fold=0 or timezone_fold=1."
            )
        requested_fold = int(context["timezone_fold"])
        if requested_fold not in (0, 1):
            raise TimezoneResolutionError("timezone_fold must be 0 or 1.")
        selected = next((item for item in candidates if item[0] == requested_fold), None)
        if selected is None:
            raise TimezoneResolutionError("Requested timezone_fold does not resolve this local time.")
    else:
        selected = candidates[0]

    fold, aware, utc_value = selected
    return {
        "tzinfo": zone,
        "model": model,
        "timezone_id": zone_id,
        "effective_offset_hours": aware.utcoffset().total_seconds() / 3600.0,
        "abbreviation": aware.tzname(),
        "fold": fold,
        "tzdata_version": _tzdata_version(),
        "local_datetime": aware,
        "utc_datetime": utc_value,
    }


def normalize_birth_timezone(birth: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    required = {"year", "month", "day", "hour", "minute"}
    missing = sorted(required - set(birth))
    if missing:
        raise TimezoneResolutionError(f"Missing required birth fields: {', '.join(missing)}")
    if birth.get("time_accuracy") == "unknown":
        raise TimezoneResolutionError("A known birth time is required for timezone resolution.")
    resolved = resolve_local_datetime(
        int(birth["year"]), int(birth["month"]), int(birth["day"]),
        int(birth["hour"]), int(birth["minute"]), birth,
    )
    normalized = dict(birth)
    supplied_offset = birth.get("timezone_offset")
    normalized["timezone_offset"] = resolved["effective_offset_hours"]
    basis = _public_basis(resolved)
    basis["source_precedence"] = "timezone_id" if resolved["model"] == "iana_zoneinfo" else "timezone_offset"
    basis["supplied_timezone_offset"] = float(supplied_offset) if supplied_offset is not None else None
    basis["supplied_offset_mismatch"] = (
        supplied_offset is not None
        and abs(float(supplied_offset) - float(resolved["effective_offset_hours"])) > 1e-9
    )
    basis["birth_local_iso"] = resolved["local_datetime"].isoformat()
    basis["birth_utc_iso"] = resolved["utc_datetime"].isoformat().replace("+00:00", "Z")
    return normalized, basis


def timezone_basis_for_instant(context: dict[str, Any], instant_utc: datetime) -> tuple[datetime, dict[str, Any]]:
    if instant_utc.tzinfo is None:
        instant_utc = instant_utc.replace(tzinfo=timezone.utc)
    else:
        instant_utc = instant_utc.astimezone(timezone.utc)
    zone, model, zone_id = _zone_from_context(context)
    local = instant_utc.astimezone(zone)
    resolved = {
        "model": model,
        "timezone_id": zone_id,
        "effective_offset_hours": local.utcoffset().total_seconds() / 3600.0,
        "abbreviation": local.tzname(),
        "fold": local.fold,
        "tzdata_version": _tzdata_version() if model == "iana_zoneinfo" else None,
    }
    return local, resolved


def local_midnight_utc(local_date: date, context: dict[str, Any]) -> tuple[datetime, dict[str, Any]]:
    resolved = resolve_local_datetime(local_date.year, local_date.month, local_date.day, 0, 0, context)
    return resolved["utc_datetime"], _public_basis(resolved)


__all__ = [
    "TimezoneResolutionError", "resolve_local_datetime", "normalize_birth_timezone",
    "timezone_basis_for_instant", "local_midnight_utc",
]
