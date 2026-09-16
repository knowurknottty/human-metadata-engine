"""Deterministic BaZi/Four-Pillars calculation with explicit civil-time conventions.

This module computes pillars and structural relationships. It intentionally does
not convert elemental counts into a fortune claim or a generic Day-Master
"strength" score; those require a separately versioned interpretive school.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from system_contracts import system_result
from time_context import TimezoneResolutionError, normalize_birth_timezone, resolve_local_datetime

STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
STEM_ELEMENT = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
STEM_POLARITY = ["Yang", "Yin"] * 5
BRANCH_ELEMENT = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire", "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]
HIDDEN_STEMS = {
    0: [9], 1: [5, 9, 7], 2: [0, 2, 4], 3: [1],
    4: [4, 1, 9], 5: [2, 4, 6], 6: [3, 5], 7: [5, 3, 1],
    8: [6, 8, 4], 9: [7], 10: [4, 7, 3], 11: [8, 0],
}
GENERATES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLS = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}


def _uses_iana(birth: dict[str, Any]) -> bool:
    return bool(birth.get("timezone_id") or birth.get("tzid"))


def _meta(*, time_known: bool, use_iana: bool) -> dict[str, Any]:
    zone_dependency = "birth.timezone_id" if use_iana else "birth.utc_offset"
    source_ids = ["SRC-BAZI-SEXAGENARY", "SRC-BAZI-JIEQI"]
    if use_iana:
        source_ids.append("SRC-IANA-TZDB")
    dependencies = ["birth.date", zone_dependency]
    if time_known:
        dependencies.append("birth.local_time")
    return {
        "system_version": "bazi-v2",
        "tradition": "Chinese Four Pillars / BaZi",
        "convention": "li-chun-jie-civil-time-zone-aware-v2",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_instant"] if time_known else ["birth_date"],
        "input_dependencies": dependencies,
        "source_ids": source_ids,
        "sensitivity": "personal",
        "license_info": {
            "calculation_code": "project-authored",
            "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"],
        },
    }


def _jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _pillar(index: int) -> dict[str, Any]:
    stem = index % 10
    branch = index % 12
    return {
        "cycle_index": index % 60,
        "stem": STEMS[stem],
        "stem_index": stem,
        "stem_element": STEM_ELEMENT[stem],
        "stem_polarity": STEM_POLARITY[stem],
        "branch": BRANCHES[branch],
        "branch_index": branch,
        "branch_element": BRANCH_ELEMENT[branch],
        "hidden_stems": [STEMS[item] for item in HIDDEN_STEMS[branch]],
    }


def _ten_god(day_stem: int, other_stem: int) -> str:
    dm_element = STEM_ELEMENT[day_stem]
    other_element = STEM_ELEMENT[other_stem]
    same_polarity = STEM_POLARITY[day_stem] == STEM_POLARITY[other_stem]
    if other_element == dm_element:
        return "Friend" if same_polarity else "Rob Wealth"
    if GENERATES[dm_element] == other_element:
        return "Eating God" if same_polarity else "Hurting Officer"
    if GENERATES[other_element] == dm_element:
        return "Indirect Resource" if same_polarity else "Direct Resource"
    if CONTROLS[dm_element] == other_element:
        return "Indirect Wealth" if same_polarity else "Direct Wealth"
    if CONTROLS[other_element] == dm_element:
        return "Seven Killings" if same_polarity else "Direct Officer"
    raise AssertionError("unreachable five-phase relationship")


def _solar_longitude_utc(utc_value: datetime) -> float:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for BaZi solar-term calculation.")
    swe.set_ephe_path(None)
    hour_ut = (
        utc_value.hour
        + utc_value.minute / 60.0
        + utc_value.second / 3600.0
        + utc_value.microsecond / 3_600_000_000.0
    )
    jd = swe.julday(utc_value.year, utc_value.month, utc_value.day, hour_ut)
    return float(swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH)[0][0]) % 360.0


def _year_month_pillars(year_value: int, month_value: int, sun_lon: float) -> tuple[int, dict[str, Any], dict[str, Any]]:
    bazi_year = year_value
    if month_value <= 2 and sun_lon < 315.0:
        bazi_year -= 1
    year_index = (bazi_year - 4) % 60
    year = _pillar(year_index)

    month_offset = int(((sun_lon - 315.0) % 360.0) // 30.0)
    month_branch = (2 + month_offset) % 12
    first_month_stem = ((year["stem_index"] % 5) * 2 + 2) % 10
    month_stem = (first_month_stem + month_offset) % 10
    month_cycle = next(i for i in range(60) if i % 10 == month_stem and i % 12 == month_branch)
    return bazi_year, year, _pillar(month_cycle)


def _structure(pillars: dict[str, dict[str, Any] | None], day: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any], list[str]]:
    counts: Counter[str] = Counter()
    available = []
    for label, pillar in pillars.items():
        if pillar is None:
            continue
        available.append(label)
        counts[pillar["stem_element"]] += 1.0
        hidden = HIDDEN_STEMS[pillar["branch_index"]]
        share = 1.0 / len(hidden)
        for stem in hidden:
            counts[STEM_ELEMENT[stem]] += share
    total = sum(counts.values()) or 1.0
    elements = {
        name: round(counts[name] / total, 6)
        for name in ["Wood", "Fire", "Earth", "Metal", "Water"]
    }

    ten_gods: dict[str, Any] = {}
    for label, pillar in pillars.items():
        if pillar is None:
            ten_gods[label] = None
            ten_gods[f"{label}_hidden"] = []
            continue
        stem_index = pillar["stem_index"]
        ten_gods[label] = "Day Master" if label == "day" else _ten_god(day["stem_index"], stem_index)
        ten_gods[f"{label}_hidden"] = [
            {"stem": STEMS[index], "relation": _ten_god(day["stem_index"], index)}
            for index in HIDDEN_STEMS[pillar["branch_index"]]
        ]
    return elements, ten_gods, available


def _unknown_day_timezone_basis(start: dict[str, Any], end: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": start["model"],
        "timezone_id": start.get("timezone_id"),
        "source_precedence": "timezone_id" if start["model"] == "iana_zoneinfo" else "timezone_offset",
        "day_start_effective_offset_hours": start["effective_offset_hours"],
        "day_end_effective_offset_hours": end["effective_offset_hours"],
        "day_start_abbreviation": start.get("abbreviation"),
        "day_end_abbreviation": end.get("abbreviation"),
        "tzdata_version": start.get("tzdata_version"),
    }


def compute_bazi(birth: dict[str, Any]) -> dict[str, Any]:
    time_known = birth.get("time_accuracy") != "unknown"
    use_iana = _uses_iana(birth)
    meta = _meta(time_known=time_known, use_iana=use_iana)
    required = {"year", "month", "day"}
    if time_known:
        required.update({"hour", "minute"})
    missing = sorted(required - set(birth))
    if not use_iana and "timezone_offset" not in birth:
        missing.append("timezone_id|timezone_offset")
    if missing:
        return system_result(
            "bazi", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"],
            **meta,
        )

    year_value = int(birth["year"])
    month_value = int(birth["month"])
    day_value = int(birth["day"])
    datetime(year_value, month_value, day_value)
    day = _pillar((_jdn(year_value, month_value, day_value) + 49) % 60)

    if time_known:
        hour_value = int(birth["hour"])
        minute_value = int(birth["minute"])
        datetime(year_value, month_value, day_value, hour_value, minute_value)
        try:
            _, timezone_basis = normalize_birth_timezone(birth)
        except TimezoneResolutionError as exc:
            return system_result(
                "bazi", calculation={}, status="input_insufficient",
                limitations=[str(exc)], **meta,
            )
        utc_value = datetime.fromisoformat(timezone_basis["birth_utc_iso"].replace("Z", "+00:00"))
        sun_lon = _solar_longitude_utc(utc_value)
        bazi_year, year, month = _year_month_pillars(year_value, month_value, sun_lon)
        hour_branch = ((hour_value + 1) // 2) % 12
        zi_stem = (day["stem_index"] % 5) * 2
        hour_stem = (zi_stem + hour_branch) % 10
        hour_cycle = next(i for i in range(60) if i % 10 == hour_stem and i % 12 == hour_branch)
        hour = _pillar(hour_cycle)
        solar_payload: float | None = round(sun_lon, 6)
        solar_range = None
        limitations = [
            "Five-phase distribution is an equal-share structural count of visible and hidden stems, not a Day-Master strength score.",
            "v2 resolves an explicit IANA timezone_id when supplied; otherwise it uses the explicit fixed UTC offset.",
            "v2 uses civil clock time for the hour pillar; true/apparent solar-time correction is not applied.",
            "v2 changes the day at civil midnight; alternate late-Zi rollover schools are not blended.",
        ]
    else:
        try:
            start = resolve_local_datetime(year_value, month_value, day_value, 0, 0, birth)
            end = resolve_local_datetime(year_value, month_value, day_value, 23, 59, birth)
        except TimezoneResolutionError as exc:
            return system_result(
                "bazi", calculation={}, status="input_insufficient",
                limitations=[str(exc)], **meta,
            )
        timezone_basis = _unknown_day_timezone_basis(start, end)
        start_lon = _solar_longitude_utc(start["utc_datetime"])
        end_lon = _solar_longitude_utc(end["utc_datetime"])
        start_bazi_year, start_year, start_month = _year_month_pillars(year_value, month_value, start_lon)
        end_bazi_year, end_year, end_month = _year_month_pillars(year_value, month_value, end_lon)
        year = start_year if start_year["cycle_index"] == end_year["cycle_index"] else None
        month = start_month if start_month["cycle_index"] == end_month["cycle_index"] else None
        bazi_year = start_bazi_year if start_bazi_year == end_bazi_year else None
        hour = None
        solar_payload = None
        solar_range = {"start_local_day": round(start_lon, 6), "end_local_day": round(end_lon, 6)}
        limitations = [
            "Birth time is unknown; the hour pillar is unavailable rather than imputed.",
            "Year and month pillars are emitted only when they are stable across the entire supplied local birth date.",
            "If the birth date crosses a Li Chun or Jie boundary, the affected pillar is withheld because exact time is required.",
            "Five-phase distribution uses only available pillars and is marked partial when the hour pillar is absent.",
            "v2 resolves the local date boundaries through an explicit IANA timezone_id when supplied, including offset changes within that date.",
            "v2 changes the day at civil midnight; alternate late-Zi rollover schools are not blended.",
        ]

    pillars: dict[str, dict[str, Any] | None] = {
        "year": year, "month": month, "day": day, "hour": hour,
    }
    elements, ten_gods, available_pillars = _structure(pillars, day)
    calculation = {
        "pillars": pillars,
        "day_master": {
            "stem": day["stem"], "element": day["stem_element"], "polarity": day["stem_polarity"]
        },
        "ten_gods": ten_gods,
        "five_phase_distribution": elements,
        "five_phase_distribution_basis": {
            "available_pillars": available_pillars,
            "complete": len(available_pillars) == 4,
        },
        "solar_longitude": solar_payload,
        "solar_longitude_range": solar_range,
        "bazi_year": bazi_year,
        "time_accuracy": "known" if time_known else "unknown",
        "timezone_basis": timezone_basis,
    }
    return system_result(
        "bazi", calculation=calculation, limitations=limitations,
        **meta,
    )


__all__ = ["compute_bazi"]