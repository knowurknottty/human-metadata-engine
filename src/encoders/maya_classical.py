"""Classical Maya calendar coordinates under the GMT 584283 correlation.

This module is calendrical, not predictive. It keeps Classical Maya Long Count,
Tzolk'in, Haab', Calendar Round, and G-series calculations distinct from modern
Dreamspell/Tzolkin systems.
"""
from __future__ import annotations

from typing import Any

from system_contracts import system_result

GMT_CORRELATION = 584283
TZOLKIN_NAMES = [
    "Imix", "Ik'", "Ak'bal", "K'an", "Chikchan", "Kimi", "Manik'", "Lamat",
    "Muluk", "Ok", "Chuwen", "Eb'", "B'en", "Ix", "Men", "Kib'",
    "Kab'an", "Etz'nab'", "Kawak", "Ajaw",
]
HAAB_MONTHS = [
    "Pop", "Wo", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en",
    "Yax", "Sak'", "Keh", "Mak", "K'ank'in", "Muwan'", "Pax", "K'ayab",
    "Kumk'u", "Wayeb'",
]


def _jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _long_count(elapsed: int) -> dict[str, int | str]:
    remainder = elapsed
    baktun, remainder = divmod(remainder, 144000)
    katun, remainder = divmod(remainder, 7200)
    tun, remainder = divmod(remainder, 360)
    winal, kin = divmod(remainder, 20)
    return {
        "baktun": baktun, "katun": katun, "tun": tun, "winal": winal, "kin": kin,
        "notation": f"{baktun}.{katun}.{tun}.{winal}.{kin}",
    }


def _meta() -> dict[str, Any]:
    return {
        "system_version": "maya-classical-gmt-v1",
        "tradition": "Classical Maya calendrical systems",
        "convention": "gmt-584283-v1",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_date"],
        "input_dependencies": ["birth.date"],
        "source_ids": ["SRC-MAYAN-GMT", "SRC-MAYAN-TZOLKIN", "SRC-MAYAN-HAAB", "SRC-MAYAN-G-SERIES"],
        "sensitivity": "personal",
        "license_info": {"calculation_code": "project-authored", "third_party_dependencies": []},
    }


def compute_classical_maya(birth: dict[str, Any]) -> dict[str, Any]:
    required = {"year", "month", "day"}
    missing = sorted(required - set(birth))
    if missing:
        return system_result(
            "maya_classical", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"], **_meta(),
        )

    jdn = _jdn(int(birth["year"]), int(birth["month"]), int(birth["day"]))
    elapsed = jdn - GMT_CORRELATION
    if elapsed < 0:
        return system_result(
            "maya_classical", calculation={}, status="unavailable",
            limitations=["maya-classical-gmt-v1 currently emits non-negative Long Count dates only."],
            **_meta(),
        )

    long_count = _long_count(elapsed)
    tz_number = ((elapsed + 3) % 13) + 1
    tz_name = TZOLKIN_NAMES[(elapsed + 19) % 20]
    haab_index = (elapsed + 348) % 365
    if haab_index < 360:
        haab_month_index, haab_day = divmod(haab_index, 20)
    else:
        haab_month_index, haab_day = 18, haab_index - 360
    haab_month = HAAB_MONTHS[haab_month_index]
    lord_number = ((elapsed + 8) % 9) + 1

    calculation = {
        "correlation": {
            "name": "Goodman-Martinez-Thompson",
            "constant": GMT_CORRELATION,
            "alternative_published_constants": [584285, 584289],
        },
        "julian_day_number": jdn,
        "elapsed_days": elapsed,
        "long_count": long_count,
        "tzolkin": {"number": tz_number, "day_name": tz_name, "label": f"{tz_number} {tz_name}"},
        "haab": {"day": haab_day, "month": haab_month, "label": f"{haab_day} {haab_month}"},
        "calendar_round": f"{tz_number} {tz_name} {haab_day} {haab_month}",
        "lord_of_night": f"G{lord_number}",
    }
    return system_result(
        "maya_classical", calculation=calculation,
        limitations=[
            "This is the GMT 584283 correlation; alternative published correlations shift the mapped Gregorian date.",
            "This module computes calendrical coordinates only and does not infer personality, destiny, or future events.",
            "Modern Dreamspell systems are intentionally separate from this Classical Maya artifact.",
        ],
        **_meta(),
    )


__all__ = ["compute_classical_maya", "GMT_CORRELATION"]
