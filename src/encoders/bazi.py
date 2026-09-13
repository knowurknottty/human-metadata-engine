"""Deterministic BaZi/Four-Pillars calculation with explicit conventions.

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


def _meta() -> dict[str, Any]:
    return {
        "system_version": "bazi-v1",
        "tradition": "Chinese Four Pillars / BaZi",
        "convention": "li-chun-jie-civil-time-v1",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_instant"],
        "input_dependencies": ["birth.date", "birth.local_time", "birth.utc_offset"],
        "source_ids": ["SRC-BAZI-SEXAGENARY", "SRC-BAZI-JIEQI"],
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


def _solar_longitude(birth: dict[str, Any]) -> float:
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for BaZi solar-term calculation.")
    swe.set_ephe_path(None)
    hour_ut = birth["hour"] + birth["minute"] / 60.0 - float(birth["timezone_offset"])
    jd = swe.julday(birth["year"], birth["month"], birth["day"], hour_ut)
    return float(swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH)[0][0]) % 360.0


def compute_bazi(birth: dict[str, Any]) -> dict[str, Any]:
    required = {"year", "month", "day", "hour", "minute", "timezone_offset"}
    missing = sorted(required - set(birth))
    if missing:
        return system_result(
            "bazi", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"], **_meta(),
        )
    if birth.get("time_accuracy") == "unknown":
        return system_result(
            "bazi", calculation={}, status="input_insufficient",
            limitations=["bazi-v1 requires a known birth time and does not substitute a noon hour pillar."],
            **_meta(),
        )
    datetime(int(birth["year"]), int(birth["month"]), int(birth["day"]), int(birth["hour"]), int(birth["minute"]))
    sun_lon = _solar_longitude(birth)

    bazi_year = int(birth["year"])
    if int(birth["month"]) <= 2 and sun_lon < 315.0:
        bazi_year -= 1
    year_index = (bazi_year - 4) % 60
    year = _pillar(year_index)

    month_offset = int(((sun_lon - 315.0) % 360.0) // 30.0)
    month_branch = (2 + month_offset) % 12
    first_month_stem = ((year["stem_index"] % 5) * 2 + 2) % 10
    month_stem = (first_month_stem + month_offset) % 10
    month_cycle = next(i for i in range(60) if i % 10 == month_stem and i % 12 == month_branch)
    month = _pillar(month_cycle)

    day_index = (_jdn(int(birth["year"]), int(birth["month"]), int(birth["day"])) + 49) % 60
    day = _pillar(day_index)

    hour_branch = ((int(birth["hour"]) + 1) // 2) % 12
    zi_stem = (day["stem_index"] % 5) * 2
    hour_stem = (zi_stem + hour_branch) % 10
    hour_cycle = next(i for i in range(60) if i % 10 == hour_stem and i % 12 == hour_branch)
    hour = _pillar(hour_cycle)

    pillars = {"year": year, "month": month, "day": day, "hour": hour}
    counts: Counter[str] = Counter()
    for pillar in pillars.values():
        counts[pillar["stem_element"]] += 1.0
        hidden = HIDDEN_STEMS[pillar["branch_index"]]
        share = 1.0 / len(hidden)
        for stem in hidden:
            counts[STEM_ELEMENT[stem]] += share
    total = sum(counts.values()) or 1.0
    elements = {name: round(counts[name] / total, 6) for name in ["Wood", "Fire", "Earth", "Metal", "Water"]}

    ten_gods = {}
    for label, pillar in pillars.items():
        stem_index = pillar["stem_index"]
        ten_gods[label] = "Day Master" if label == "day" else _ten_god(day["stem_index"], stem_index)
        ten_gods[f"{label}_hidden"] = [
            {"stem": STEMS[index], "relation": _ten_god(day["stem_index"], index)}
            for index in HIDDEN_STEMS[pillar["branch_index"]]
        ]

    calculation = {
        "pillars": pillars,
        "day_master": {
            "stem": day["stem"], "element": day["stem_element"], "polarity": day["stem_polarity"]
        },
        "ten_gods": ten_gods,
        "five_phase_distribution": elements,
        "solar_longitude": round(sun_lon, 6),
        "bazi_year": bazi_year,
    }
    return system_result(
        "bazi", calculation=calculation,
        limitations=[
            "Five-phase distribution is an equal-share structural count of visible and hidden stems, not a Day-Master strength score.",
            "v1 uses supplied civil time and UTC offset; true/apparent solar-time correction is not applied.",
            "v1 changes the day at civil midnight; alternate late-Zi rollover schools are not blended.",
        ],
        **_meta(),
    )


__all__ = ["compute_bazi"]
