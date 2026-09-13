"""Sidereal/Jyotish astronomical projection using Swiss Ephemeris.

v1 implements a Lahiri sidereal natal projection, 27 nakshatras/padas, and
deterministic D9 Navamsha and D10 Dasamsa projections. Interpretive meanings
and dashas are kept out of this static calculation module.
"""
from __future__ import annotations

from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from system_contracts import system_result

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_RULERS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
] * 3
PLANETS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
}


def _meta() -> dict[str, Any]:
    return {
        "system_version": "jyotish-v1",
        "tradition": "Jyotish / sidereal astrology",
        "convention": "lahiri-27-nakshatra-v1",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_instant"],
        "input_dependencies": ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates"],
        "source_ids": [
            "SRC-JYOTISH-LAHIRI", "SRC-JYOTISH-NAKSHATRA",
            "SRC-JYOTISH-NAVAMSHA", "SRC-JYOTISH-DASAMSA",
        ],
        "sensitivity": "personal",
        "license_info": {
            "calculation_code": "project-authored",
            "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"],
        },
    }


def _sign(lon: float) -> tuple[str, float, int]:
    value = lon % 360.0
    index = int(value // 30.0)
    return SIGNS[index], value % 30.0, index


def _nakshatra(lon: float) -> dict[str, Any]:
    value = lon % 360.0
    span = 360.0 / 27.0
    pada_span = span / 4.0
    index = min(26, int(value // span))
    within = value - index * span
    pada = min(4, int(within // pada_span) + 1)
    return {
        "index": index + 1,
        "name": NAKSHATRAS[index],
        "ruler": NAKSHATRA_RULERS[index],
        "pada": pada,
        "degree_within": round(within, 6),
    }


def _dasamsa(lon: float) -> dict[str, Any]:
    _, degree, sign_index = _sign(lon)
    division = min(9, int(degree // 3.0))
    # Traditional sign numbering is 1-based: odd signs begin from themselves;
    # even signs begin from the ninth sign counted inclusively.
    start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
    d10_sign_index = (start + division) % 12
    return {
        "sign": SIGNS[d10_sign_index],
        "sign_index": d10_sign_index,
        "division_index": division + 1,
    }


def _navamsha(lon: float) -> dict[str, Any]:
    _, degree, sign_index = _sign(lon)
    nav_index_within = min(8, int(degree // (30.0 / 9.0)))
    modality = sign_index % 3
    if modality == 0:
        start = sign_index
    elif modality == 1:
        start = (sign_index + 8) % 12
    else:
        start = (sign_index + 4) % 12
    nav_sign_index = (start + nav_index_within) % 12
    return {
        "sign": SIGNS[nav_sign_index],
        "sign_index": nav_sign_index,
        "division_index": nav_index_within + 1,
    }


def compute_jyotish(birth: dict[str, Any], *, ayanamsa: str = "lahiri") -> dict[str, Any]:
    required = {"year", "month", "day", "hour", "minute", "timezone_offset", "lat", "lon"}
    missing = sorted(required - set(birth))
    if missing:
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"], **_meta(),
        )
    if birth.get("time_accuracy") == "unknown":
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=["jyotish-v1 requires a known birth time and does not substitute a noon chart."],
            **_meta(),
        )
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for Jyotish calculation.")
    if ayanamsa.lower() != "lahiri":
        raise ValueError("jyotish-v1 currently supports only the Lahiri ayanamsa.")

    swe.set_ephe_path(None)
    hour_ut = birth["hour"] + birth["minute"] / 60.0 - float(birth["timezone_offset"])
    jd = swe.julday(birth["year"], birth["month"], birth["day"], hour_ut)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    planet_flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH | swe.FLG_SPEED
    ayanamsa_deg = float(swe.get_ayanamsa_ut(jd))

    planets: dict[str, Any] = {}
    for name, pid in PLANETS.items():
        data = swe.calc_ut(jd, pid, planet_flags)[0]
        lon = float(data[0]) % 360.0
        speed = float(data[3])
        sign, degree, sign_index = _sign(lon)
        planets[name] = {
            "longitude": round(lon, 6),
            "sign": sign,
            "sign_index": sign_index,
            "degree": round(degree, 6),
            "speed_longitude": round(speed, 9),
            "retrograde": speed < 0,
            "nakshatra": _nakshatra(lon),
            "d9_navamsha": _navamsha(lon),
            "d10_dasamsa": _dasamsa(lon),
        }

    cusps, ascmc = swe.houses_ex(
        jd, float(birth["lat"]), float(birth["lon"]), b"P", swe.FLG_SIDEREAL
    )
    asc_lon = float(ascmc[0]) % 360.0
    asc_sign, asc_degree, asc_index = _sign(asc_lon)
    ascendant = {
        "longitude": round(asc_lon, 6),
        "sign": asc_sign,
        "sign_index": asc_index,
        "degree": round(asc_degree, 6),
        "nakshatra": _nakshatra(asc_lon),
        "d9_navamsha": _navamsha(asc_lon),
        "d10_dasamsa": _dasamsa(asc_lon),
    }
    calculation = {
        "ayanamsa": {"name": "Lahiri", "degrees": round(ayanamsa_deg, 6)},
        "zodiac": "sidereal",
        "ephemeris_profile": "pyswisseph-moshier-sidereal-speed-v1",
        "planets": planets,
        "ascendant": ascendant,
        "house_system": "Placidus sidereal projection",
        "house_cusps": [round(float(value) % 360.0, 6) for value in cusps],
        "moon_nakshatra": planets["Moon"]["nakshatra"],
    }
    return system_result(
        "jyotish", calculation=calculation,
        limitations=[
            "This v1 layer computes astronomical/symbolic coordinates only; it does not claim empirical personality validity.",
            "Vimshottari Dasha belongs in a separate timing artifact and is not emitted by this static signature.",
            "D9 and D10 are deterministic divisional projections; interpretive meanings are intentionally not embedded here.",
            "Uranus, Neptune, and Pluto are exposed as modern optional sidereal additions; they are not classical Jyotish grahas.",
        ],
        **_meta(),
    )


__all__ = ["compute_jyotish"]
