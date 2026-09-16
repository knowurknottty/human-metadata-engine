"""Zodiacal Releasing v2: L1-L4, 360-day calendar, and loosing-of-the-bond."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from encoders.jyotish import SIGNS
from system_contracts import system_result
from time_context import TimezoneResolutionError, normalize_birth_timezone
from timing_v1 import CLASSICAL_RULERS, _natal_frame, _parse_as_of

ZR_SIGN_YEARS = [15.0, 8.0, 20.0, 25.0, 19.0, 20.0, 8.0, 15.0, 12.0, 27.0, 30.0, 12.0]
ZR_LEVEL_UNIT_DAYS = {1: 360.0, 2: 30.0, 3: 2.5, 4: 5.0 / 24.0}


def _require_swe() -> None:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for Zodiacal Releasing calculations.")
    swe.set_ephe_path(None)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _from_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _period(
    sign_index: int,
    start: datetime,
    natural_end: datetime,
    parent_end: datetime,
    level: int,
    *,
    loosing_of_bond: bool = False,
) -> dict[str, Any]:
    end = min(natural_end, parent_end)
    actual_days = (end - start).total_seconds() / 86400.0
    nominal_days = ZR_SIGN_YEARS[sign_index] * ZR_LEVEL_UNIT_DAYS[level]
    return {
        "level": level,
        "sign": SIGNS[sign_index],
        "sign_index": sign_index,
        "ruler": CLASSICAL_RULERS[sign_index],
        "start_utc": _iso(start),
        "end_utc": _iso(end),
        "nominal_duration_days": round(nominal_days, 9),
        "actual_duration_days": round(actual_days, 9),
        "truncated_by_parent": natural_end > parent_end,
        "loosing_of_bond": bool(loosing_of_bond),
    }


def _generate_level_1(start_sign_index: int, start: datetime) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    cursor = start
    for offset in range(12):
        sign_index = (start_sign_index + offset) % 12
        natural_end = cursor + timedelta(days=ZR_SIGN_YEARS[sign_index] * ZR_LEVEL_UNIT_DAYS[1])
        periods.append(_period(sign_index, cursor, natural_end, natural_end, 1))
        cursor = natural_end
    return periods


def _generate_subperiods(
    parent_sign_index: int,
    parent_start: datetime,
    parent_end: datetime,
    level: int,
) -> list[dict[str, Any]]:
    if level not in (2, 3, 4):
        raise ValueError("Subperiod level must be 2, 3, or 4.")
    periods: list[dict[str, Any]] = []
    cursor = parent_start
    previous_sign: int | None = None
    count = 0
    lb_done = False
    while cursor < parent_end - timedelta(microseconds=1):
        loosing = False
        if count == 0:
            sign_index = parent_sign_index
        elif count == 12 and not lb_done:
            sign_index = (parent_sign_index + 6) % 12
            loosing = True
            lb_done = True
        else:
            sign_index = (int(previous_sign) + 1) % 12
        natural_end = cursor + timedelta(days=ZR_SIGN_YEARS[sign_index] * ZR_LEVEL_UNIT_DAYS[level])
        item = _period(sign_index, cursor, natural_end, parent_end, level, loosing_of_bond=loosing)
        periods.append(item)
        cursor = min(natural_end, parent_end)
        previous_sign = sign_index
        count += 1
        if item["truncated_by_parent"]:
            break
    return periods


def _find_active(periods: list[dict[str, Any]], as_of_utc: datetime) -> dict[str, Any] | None:
    for item in periods:
        if _from_iso(item["start_utc"]) <= as_of_utc < _from_iso(item["end_utc"]):
            return dict(item)
    return None


def _apply_spirit_same_sign_rule(fortune_sign_index: int, spirit_sign_index: int) -> tuple[int, bool]:
    if fortune_sign_index == spirit_sign_index:
        return (spirit_sign_index + 1) % 12, True
    return spirit_sign_index, False


def _lots_and_sect(birth: dict[str, Any], natal_jd: float, natal: dict[str, Any]) -> tuple[str, float, dict[str, Any]]:
    sun = natal["planets"]["Sun"]
    moon = natal["planets"]["Moon"]
    asc = natal["ascendant"]
    sun_raw = swe.calc_ut(natal_jd, swe.SUN, swe.FLG_MOSEPH)[0]
    _, sun_true_altitude, _ = swe.azalt(
        natal_jd,
        swe.ECL2HOR,
        (float(birth["lon"]), float(birth["lat"]), float(birth.get("altitude_m", 0.0))),
        0.0,
        0.0,
        (float(sun_raw[0]), float(sun_raw[1]), float(sun_raw[2])),
    )
    sect = "day" if float(sun_true_altitude) >= 0.0 else "night"
    asc_lon = float(asc["longitude"])
    sun_lon = float(sun["longitude"])
    moon_lon = float(moon["longitude"])
    if sect == "day":
        fortune_lon = (asc_lon + moon_lon - sun_lon) % 360.0
        spirit_lon = (asc_lon + sun_lon - moon_lon) % 360.0
    else:
        fortune_lon = (asc_lon + sun_lon - moon_lon) % 360.0
        spirit_lon = (asc_lon + moon_lon - sun_lon) % 360.0

    def lot_payload(lon: float) -> dict[str, Any]:
        index = int((lon % 360.0) // 30.0)
        return {
            "longitude": round(lon % 360.0, 6),
            "sign": SIGNS[index],
            "sign_index": index,
            "degree": round((lon % 360.0) % 30.0, 6),
        }

    return sect, float(sun_true_altitude), {
        "fortune": lot_payload(fortune_lon),
        "spirit": lot_payload(spirit_lon),
    }


def compute_zodiacal_releasing(
    birth: dict[str, Any],
    *,
    as_of: date | datetime | str | None = None,
    lot: str = "spirit",
) -> dict[str, Any]:
    _require_swe()
    lot_key = lot.strip().lower()
    if lot_key not in {"fortune", "spirit"}:
        raise ValueError("zodiacal-releasing-v2 lot must be 'fortune' or 'spirit'.")
    convention = "valens-modern-standard-360day-l1-l4-lb-v2"
    deps = ["birth.date", "birth.local_time", "birth.timezone_id_or_offset", "birth.coordinates", "as_of"]
    base = dict(
        system_version="zodiacal-releasing-v2",
        tradition="Hellenistic zodiacal releasing",
        convention=convention,
        artifact_class="timing",
        epistemic_class="deterministic_calculation",
        dependency_roots=["birth_instant"],
        input_dependencies=deps,
        source_ids=[
            "SRC-ZODIACAL-RELEASING-VALENS",
            "SRC-ZODIACAL-RELEASING-360DAY",
            "SRC-ZODIACAL-RELEASING-LB",
            "SRC-IANA-TZDB",
        ],
        sensitivity="personal",
        license_info={
            "calculation_code": "project-authored",
            "third_party_dependencies": [
                "pyswisseph AGPL-3.0-or-later",
                "Python zoneinfo / tzdata 2026.4 (Apache-2.0 fallback)",
            ],
        },
    )
    as_of_utc = _parse_as_of(as_of)
    if as_of_utc is None:
        return system_result(
            "zodiacal_releasing", calculation={}, status="input_insufficient",
            limitations=["zodiacal-releasing-v2 requires an explicit as_of time."], **base,
        )
    try:
        normalized, timezone_basis = normalize_birth_timezone(birth)
        birth_utc, natal_jd, natal = _natal_frame(normalized, require_coordinates=True)
    except (TimezoneResolutionError, ValueError) as exc:
        return system_result("zodiacal_releasing", calculation={}, status="input_insufficient",
                             limitations=[str(exc)], **base)
    if as_of_utc < birth_utc:
        return system_result("zodiacal_releasing", calculation={}, status="input_insufficient",
                             limitations=["as_of precedes the birth instant."], **base)

    sect, sun_altitude, lots = _lots_and_sect(normalized, natal_jd, natal)
    fortune_idx = int(lots["fortune"]["sign_index"])
    spirit_idx = int(lots["spirit"]["sign_index"])
    same_sign_rule_applied = False
    if lot_key == "spirit":
        start_index, same_sign_rule_applied = _apply_spirit_same_sign_rule(fortune_idx, spirit_idx)
    else:
        start_index = fortune_idx

    level_1 = _generate_level_1(start_index, birth_utc)
    level_2: list[dict[str, Any]] = []
    for parent in level_1:
        children = _generate_subperiods(
            int(parent["sign_index"]), _from_iso(parent["start_utc"]), _from_iso(parent["end_utc"]), 2
        )
        for child in children:
            child["parent_level_1_sign"] = parent["sign"]
            child["parent_level_1_start_utc"] = parent["start_utc"]
            level_2.append(child)

    active_l1 = _find_active(level_1, as_of_utc)
    active_l2 = None
    level_3: list[dict[str, Any]] = []
    active_l3 = None
    level_4: list[dict[str, Any]] = []
    active_l4 = None
    if active_l1 is not None:
        l2_siblings = [
            item for item in level_2
            if item.get("parent_level_1_start_utc") == active_l1["start_utc"]
        ]
        active_l2 = _find_active(l2_siblings, as_of_utc)
        if active_l2 is not None:
            level_3 = _generate_subperiods(
                int(active_l2["sign_index"]), _from_iso(active_l2["start_utc"]), _from_iso(active_l2["end_utc"]), 3
            )
            active_l3 = _find_active(level_3, as_of_utc)
            if active_l3 is not None:
                level_4 = _generate_subperiods(
                    int(active_l3["sign_index"]), _from_iso(active_l3["start_utc"]), _from_iso(active_l3["end_utc"]), 4
                )
                active_l4 = _find_active(level_4, as_of_utc)

    loosing_events: list[dict[str, Any]] = []
    for level_name, items in (("L2", level_2), ("L3", level_3), ("L4", level_4)):
        for item in items:
            if item.get("loosing_of_bond"):
                loosing_events.append({
                    "level": level_name,
                    "sign": item["sign"],
                    "start_utc": item["start_utc"],
                    "end_utc": item["end_utc"],
                })

    levels_emitted = [1, 2]
    if level_3:
        levels_emitted.append(3)
    if level_4:
        levels_emitted.append(4)
    calculation = {
        "zodiac": "tropical",
        "sect": sect,
        "sun_true_altitude_degrees": round(sun_altitude, 6),
        "lots": lots,
        "selected_lot": lot_key,
        "release_start": {"sign": SIGNS[start_index], "sign_index": start_index},
        "same_sign_spirit_rule_applied": same_sign_rule_applied,
        "timezone_basis": timezone_basis,
        "calendar_model": "idealized_360_day_year_30_day_month_recursive_twelfths",
        "level_unit_days": {"L1": 360.0, "L2": 30.0, "L3": 2.5, "L4": round(5.0 / 24.0, 12)},
        "sign_period_numbers": {SIGNS[i]: ZR_SIGN_YEARS[i] for i in range(12)},
        "level_1_periods": level_1,
        "level_2_periods": level_2,
        "level_3_periods_active_parent": level_3,
        "level_4_periods_active_parent": level_4,
        "loosing_of_bond_events": loosing_events,
        "as_of_utc": as_of_utc.isoformat().replace("+00:00", "Z"),
        "active_hierarchy": {"L1": active_l1, "L2": active_l2, "L3": active_l3, "L4": active_l4},
        "levels_emitted": levels_emitted,
    }
    limitations = [
        "v2 uses the disclosed 360-day-year / 30-day-month reconstruction; it intentionally replaces the earlier v1 365.2425-day ZR normalization.",
        "L2 is emitted across the full L1 cycle. L3 and L4 are emitted for the active parent chain at explicit as_of to keep artifacts bounded.",
        "Loosing-of-the-bond is a sequence jump after the first completed 12-sign subperiod circuit; only one such jump is applied within each parent period.",
        "If Fortune and Spirit occupy the same sign, the Spirit releasing start advances one sign while the natal Spirit Lot coordinate remains unchanged.",
        "This implementation releases only from Fortune or Spirit; Eros and interpretive peak/culmination overlays are not included.",
        "The artifact provides symbolic period coordinates only and does not predict events or outcomes.",
    ]
    if active_l1 is None:
        limitations.append("as_of lies beyond the single 12-sign L1 cycle emitted by v2; no active hierarchy is reported.")
    return system_result("zodiacal_releasing", calculation=calculation, limitations=limitations, **base)


__all__ = [
    "compute_zodiacal_releasing", "ZR_SIGN_YEARS", "ZR_LEVEL_UNIT_DAYS",
    "_generate_subperiods", "_apply_spirit_same_sign_rule",
]
