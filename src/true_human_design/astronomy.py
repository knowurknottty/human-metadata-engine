from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
import re
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

EPHEMERIS_PROFILE = "pyswisseph-moshier-v1"
CALC_FLAGS = None if swe is None else swe.FLG_MOSEPH | swe.FLG_SPEED


_FIXED_OFFSET_RE = re.compile(r"^UTC([+-])(\d{2}):(\d{2})$")


def _resolve_timezone(timezone_name: str) -> tzinfo:
    """Resolve an IANA zone or an explicit fixed UTC offset.

    The public API currently accepts a numeric UTC offset rather than silently
    guessing an IANA zone from a place name.  Fixed offsets therefore need to
    be first-class inputs to the same astronomy path.  No DST rule is inferred
    for these values; that limitation is recorded by the public adapter.
    """
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        match = _FIXED_OFFSET_RE.fullmatch(str(timezone_name))
        if not match:
            raise ValueError(f"unknown timezone: {timezone_name}") from exc
        hours = int(match.group(2))
        minutes = int(match.group(3))
        if minutes >= 60 or hours > 14 or (hours == 14 and minutes != 0):
            raise ValueError(f"invalid fixed UTC offset: {timezone_name}")
        total_minutes = hours * 60 + minutes
        if match.group(1) == "-":
            total_minutes *= -1
        return timezone(timedelta(minutes=total_minutes), name=str(timezone_name))


@dataclass(frozen=True)
class TimeLedger:
    local_iso: str
    utc_iso: str
    timezone_name: str
    utc_offset_hours: float
    julian_day: float


@dataclass(frozen=True)
class PlanetPosition:
    body: str
    julian_day: float
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float
    retrograde: bool
    ephemeris_profile: str
    calculation_flags: int


@dataclass(frozen=True)
class DesignSolveResult:
    personality_jd: float
    design_jd: float
    days_before_birth: float
    target_arc_degrees: float
    actual_arc_degrees: float
    residual_degrees: float
    iterations: int
    tolerance_degrees: float


def _require_ephemeris() -> None:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required; no synthetic fallback is permitted")


def civil_to_julian_day(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone_name: str,
    *,
    second: int = 0,
    fold: int = 0,
) -> TimeLedger:
    _require_ephemeris()
    zone = _resolve_timezone(timezone_name)
    local = datetime(year, month, day, hour, minute, second, tzinfo=zone, fold=fold)
    utc = local.astimezone(timezone.utc)
    offset = local.utcoffset()
    if offset is None:
        raise ValueError("timezone offset could not be resolved")
    decimal_hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0 + utc.microsecond / 3_600_000_000.0
    jd = swe.julday(utc.year, utc.month, utc.day, decimal_hour, swe.GREG_CAL)
    return TimeLedger(
        local_iso=local.isoformat(),
        utc_iso=utc.isoformat(),
        timezone_name=timezone_name,
        utc_offset_hours=offset.total_seconds() / 3600.0,
        julian_day=float(jd),
    )


def _calc_body(jd_ut: float, body: str, body_id: int) -> PlanetPosition:
    _require_ephemeris()
    values, returned_flags = swe.calc_ut(jd_ut, body_id, CALC_FLAGS)
    longitude, latitude, distance, speed_longitude = values[:4]
    return PlanetPosition(
        body=body,
        julian_day=float(jd_ut),
        longitude=float(longitude % 360.0),
        latitude=float(latitude),
        distance=float(distance),
        speed_longitude=float(speed_longitude),
        retrograde=bool(speed_longitude < 0),
        ephemeris_profile=EPHEMERIS_PROFILE,
        calculation_flags=int(returned_flags),
    )


def _opposition(source: PlanetPosition, body: str) -> PlanetPosition:
    return PlanetPosition(
        body=body,
        julian_day=source.julian_day,
        longitude=(source.longitude + 180.0) % 360.0,
        latitude=-source.latitude,
        distance=source.distance,
        speed_longitude=source.speed_longitude,
        retrograde=source.retrograde,
        ephemeris_profile=source.ephemeris_profile,
        calculation_flags=source.calculation_flags,
    )


def planetary_positions(jd_ut: float, *, node_mode: str = "true") -> dict[str, PlanetPosition]:
    _require_ephemeris()
    if not math.isfinite(jd_ut):
        raise ValueError("julian day must be finite")
    if node_mode not in {"true", "mean"}:
        raise ValueError("node_mode must be 'true' or 'mean'")

    bodies = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
        "North Node": swe.TRUE_NODE if node_mode == "true" else swe.MEAN_NODE,
    }
    result = {name: _calc_body(jd_ut, name, body_id) for name, body_id in bodies.items()}
    result["Earth"] = _opposition(result["Sun"], "Earth")
    result["South Node"] = _opposition(result["North Node"], "South Node")
    ordered_names = (
        "Sun", "Earth", "North Node", "South Node", "Moon", "Mercury", "Venus",
        "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    )
    return {name: result[name] for name in ordered_names}


def _solar_longitude(jd_ut: float) -> float:
    return _calc_body(jd_ut, "Sun", swe.SUN).longitude


def _backward_arc(personality_longitude: float, earlier_longitude: float) -> float:
    return (personality_longitude - earlier_longitude) % 360.0


def solve_design_jd(
    personality_jd: float,
    *,
    target_arc: float = 88.0,
    search_days: tuple[float, float] = (70.0, 110.0),
    tolerance_degrees: float = 1e-8,
    max_iterations: int = 100,
) -> DesignSolveResult:
    _require_ephemeris()
    if not 0 < target_arc < 180:
        raise ValueError("target_arc must be between 0 and 180 degrees")
    near_days, far_days = search_days
    if not 0 < near_days < far_days:
        raise ValueError("search_days must be increasing positive days-before-birth values")

    personality_sun = _solar_longitude(personality_jd)

    def residual(jd: float) -> float:
        return _backward_arc(personality_sun, _solar_longitude(jd)) - target_arc

    low_jd = personality_jd - far_days
    high_jd = personality_jd - near_days
    low_residual = residual(low_jd)
    high_residual = residual(high_jd)
    if low_residual == 0:
        high_jd = low_jd
        high_residual = low_residual
    elif high_residual == 0:
        low_jd = high_jd
        low_residual = high_residual
    elif low_residual * high_residual > 0:
        raise RuntimeError(
            "Design solar-arc root was not bracketed; refusing to guess "
            f"(residuals {low_residual:.6f}, {high_residual:.6f})"
        )

    mid_jd = (low_jd + high_jd) / 2.0
    mid_residual = residual(mid_jd)
    iterations = 0
    for iterations in range(1, max_iterations + 1):
        mid_jd = (low_jd + high_jd) / 2.0
        mid_residual = residual(mid_jd)
        if abs(mid_residual) <= tolerance_degrees:
            break
        if low_residual * mid_residual <= 0:
            high_jd = mid_jd
            high_residual = mid_residual
        else:
            low_jd = mid_jd
            low_residual = mid_residual
    else:
        raise RuntimeError(
            "Design solar-arc solver failed to converge within "
            f"{max_iterations} iterations; residual={mid_residual}"
        )

    actual_arc = _backward_arc(personality_sun, _solar_longitude(mid_jd))
    return DesignSolveResult(
        personality_jd=float(personality_jd),
        design_jd=float(mid_jd),
        days_before_birth=float(personality_jd - mid_jd),
        target_arc_degrees=float(target_arc),
        actual_arc_degrees=float(actual_arc),
        residual_degrees=float(actual_arc - target_arc),
        iterations=iterations,
        tolerance_degrees=float(tolerance_degrees),
    )


__all__ = [
    "DesignSolveResult", "PlanetPosition", "TimeLedger", "civil_to_julian_day",
    "planetary_positions", "solve_design_jd",
]
