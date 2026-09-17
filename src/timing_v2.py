"""Timezone-aware v2 civil/environment timing artifacts."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from encoders.jyotish import SIGNS
from system_contracts import system_result
from time_context import (
    TimezoneResolutionError,
    local_midnight_utc,
    normalize_birth_timezone,
    timezone_basis_for_instant,
)
from timing_v1 import (
    CHALDEAN_ORDER,
    CLASSICAL_RULERS,
    WEEKDAY_RULERS,
    _datetime_from_jd,
    _jd_from_datetime,
    _natal_frame,
    _parse_as_of,
)


def _require_swe() -> None:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for timing calculations.")
    swe.set_ephe_path(None)


def _license() -> dict[str, Any]:
    return {
        "calculation_code": "project-authored",
        "third_party_dependencies": [
            "pyswisseph AGPL-3.0-or-later",
            "Python zoneinfo / tzdata 2026.4 (Apache-2.0 fallback)",
        ],
    }


def compute_annual_profection(
    birth: dict[str, Any], *, as_of: date | datetime | str | None,
) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "whole-sign-civil-birthday-classical-rulers-zoneinfo-v2"
    sources = ["SRC-PROFECTIONS-WHOLE-SIGN", "SRC-IANA-TZDB"]
    deps = ["birth.date", "birth.local_time", "birth.timezone_id_or_offset", "birth.coordinates", "as_of"]
    base = dict(
        system_version="annual-profection-v2",
        tradition="Annual profections",
        convention=convention,
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=["birth_instant"],
        input_dependencies=deps,
        source_ids=sources,
        sensitivity="personal",
        license_info=_license(),
    )
    if as_of_utc is None:
        return system_result("annual_profection", calculation={}, status="input_insufficient",
                             limitations=["annual-profection-v2 requires an explicit as_of time."], **base)
    try:
        normalized, timezone_basis = normalize_birth_timezone(birth)
        birth_utc, _, natal = _natal_frame(normalized, require_coordinates=True)
        local_now, as_of_basis = timezone_basis_for_instant(birth, as_of_utc)
    except (TimezoneResolutionError, ValueError) as exc:
        return system_result("annual_profection", calculation={}, status="input_insufficient",
                             limitations=[str(exc)], **base)
    if as_of_utc < birth_utc:
        return system_result("annual_profection", calculation={}, status="input_insufficient",
                             limitations=["as_of precedes the birth instant."], **base)
    age = local_now.year - int(birth["year"])
    if (local_now.month, local_now.day) < (int(birth["month"]), int(birth["day"])):
        age -= 1
    asc_index = int(natal["ascendant"]["sign_index"])
    activated_index = (asc_index + age) % 12
    return system_result(
        "annual_profection",
        calculation={
            "zodiac": "tropical",
            "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
            "as_of_local": local_now.isoformat(),
            "completed_civil_years": age,
            "natal_rising_sign": natal["ascendant"]["sign"],
            "profected_house": age % 12 + 1,
            "activated_sign": SIGNS[activated_index],
            "activated_sign_index": activated_index,
            "lord_of_year": CLASSICAL_RULERS[activated_index],
            "ruler_scheme": "classical-seven-planet",
            "birth_timezone_basis": timezone_basis,
            "as_of_timezone_basis": as_of_basis,
        },
        limitations=[
            "v2 advances one whole sign per completed civil birthday from the natal rising sign.",
            "When timezone_id is supplied, IANA zone rules determine the civil birthday boundary; a numeric offset remains an explicit fixed-offset fallback.",
            "For Feb 29 births, the civil-age boundary remains Mar 1 in non-leap years under this implementation.",
            "This artifact supplies symbolic timing coordinates only and does not predict events.",
        ],
        **base,
    )


def _sun_events_for_local_date(local_date: date, context: dict[str, Any]) -> tuple[float, float]:
    midnight_utc, _ = local_midnight_utc(local_date, context)
    start_jd = _jd_from_datetime(midnight_utc)
    geopos = (float(context["lon"]), float(context["lat"]), float(context.get("altitude_m", 0.0)))
    flags = swe.FLG_MOSEPH
    rise_res, rise = swe.rise_trans(start_jd, swe.SUN, swe.CALC_RISE, geopos, 0.0, 0.0, flags)
    set_res, setting = swe.rise_trans(start_jd, swe.SUN, swe.CALC_SET, geopos, 0.0, 0.0, flags)
    if rise_res < 0 or set_res < 0:
        raise ValueError("Sunrise or sunset is unavailable for this date/location.")
    return float(rise[0]), float(setting[0])


def _event_local_iso(jd: float, context: dict[str, Any]) -> str:
    utc_value = _datetime_from_jd(jd)
    local, _ = timezone_basis_for_instant(context, utc_value)
    return local.isoformat()


def compute_planetary_hours(
    context: dict[str, Any], *, as_of: date | datetime | str | None,
) -> dict[str, Any]:
    _require_swe()
    as_of_utc = _parse_as_of(as_of)
    convention = "chaldean-sunrise-sunset-zoneinfo-v2"
    deps = ["timing_context.coordinates", "timing_context.timezone_id_or_offset", "as_of"]
    base = dict(
        system_version="planetary-hours-v2",
        tradition="Planetary hours / chronocrators",
        convention=convention,
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=["environment_context"],
        input_dependencies=deps,
        source_ids=["SRC-SWISSEPH-RISE-SET", "SRC-PLANETARY-HOURS-CHALDEAN", "SRC-IANA-TZDB"],
        sensitivity="personal",
        license_info=_license(),
    )
    missing = sorted({"lat", "lon"} - set(context))
    if as_of_utc is None or missing:
        return system_result("planetary_hours", calculation={}, status="input_insufficient",
                             limitations=["planetary-hours-v2 requires explicit as_of, latitude/longitude, and timezone_id or timezone_offset."], **base)
    try:
        local_now, timezone_basis = timezone_basis_for_instant(context, as_of_utc)
        today_rise, today_set = _sun_events_for_local_date(local_now.date(), context)
        if _jd_from_datetime(as_of_utc) < today_rise:
            base_date = local_now.date() - timedelta(days=1)
            rise_jd, set_jd = _sun_events_for_local_date(base_date, context)
            next_rise, _ = _sun_events_for_local_date(local_now.date(), context)
        else:
            base_date = local_now.date()
            rise_jd, set_jd = today_rise, today_set
            next_rise, _ = _sun_events_for_local_date(base_date + timedelta(days=1), context)
    except (TimezoneResolutionError, ValueError) as exc:
        return system_result("planetary_hours", calculation={}, status="unavailable", limitations=[str(exc)], **base)

    now_jd = _jd_from_datetime(as_of_utc)
    if rise_jd <= now_jd < set_jd:
        phase = "day"
        segment = (set_jd - rise_jd) / 12.0
        index = min(11, max(0, int((now_jd - rise_jd) / segment)))
        hour_number = index + 1
        start = rise_jd + index * segment
        end = start + segment
        sequence_offset = index
    else:
        phase = "night"
        segment = (next_rise - set_jd) / 12.0
        index = min(11, max(0, int((now_jd - set_jd) / segment)))
        hour_number = index + 13
        start = set_jd + index * segment
        end = start + segment
        sequence_offset = 12 + index

    day_ruler = WEEKDAY_RULERS[base_date.weekday()]
    first_index = CHALDEAN_ORDER.index(day_ruler)
    ruler = CHALDEAN_ORDER[(first_index + sequence_offset) % len(CHALDEAN_ORDER)]
    return system_result(
        "planetary_hours",
        calculation={
            "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
            "as_of_local": local_now.isoformat(),
            "timezone_basis": timezone_basis,
            "local_date_basis": base_date.isoformat(),
            "day_ruler": day_ruler,
            "chaldean_order": list(CHALDEAN_ORDER),
            "sunrise_utc": _datetime_from_jd(rise_jd).isoformat().replace("+00:00", "Z"),
            "sunrise_local": _event_local_iso(rise_jd, context),
            "sunset_utc": _datetime_from_jd(set_jd).isoformat().replace("+00:00", "Z"),
            "sunset_local": _event_local_iso(set_jd, context),
            "next_sunrise_utc": _datetime_from_jd(next_rise).isoformat().replace("+00:00", "Z"),
            "next_sunrise_local": _event_local_iso(next_rise, context),
            "phase": phase,
            "planetary_hour_number": hour_number,
            "ruler": ruler,
            "hour_start_utc": _datetime_from_jd(start).isoformat().replace("+00:00", "Z"),
            "hour_end_utc": _datetime_from_jd(end).isoformat().replace("+00:00", "Z"),
            "segment_length_minutes": round(segment * 24.0 * 60.0, 6),
        },
        limitations=[
            "Hours divide sunrise-to-sunset and sunset-to-next-sunrise into twelve equal temporal hours.",
            "IANA timezone rules are used when timezone_id is supplied; timezone_offset remains a fixed-offset fallback.",
            "Swiss Ephemeris rise/set defaults are used; local terrain horizon and custom atmosphere are not modeled.",
            "This is an environmental timing artifact and is not independent evidence about a person.",
        ],
        **base,
    )


__all__ = ["compute_annual_profection", "compute_planetary_hours"]
