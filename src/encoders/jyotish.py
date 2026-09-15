"""Sidereal/Jyotish astronomical projection using Swiss Ephemeris.

v2 supports explicit Lahiri or Raman ayanamsa selection, 27 nakshatras/padas,
D9 Navamsha, D10 Dasamsa, and explicit mean/true lunar-node conventions.
Interpretive meanings and dashas remain outside this static calculation module.
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
AYANAMSA_MODES = {
    "lahiri": ("Lahiri", 1),
    "raman": ("Raman", 3),
}
NODE_MODES = {
    "mean": ("mean", 10),
    "true": ("true", 11),
}


def _meta(*, ayanamsa: str, lunar_node: str) -> dict[str, Any]:
    aya_key = ayanamsa.strip().lower()
    node_key = lunar_node.strip().lower()
    aya_name = AYANAMSA_MODES[aya_key][0]
    node_name = NODE_MODES[node_key][0]
    source_ids = [
        "SRC-SWISSEPH-SIDEREAL", "SRC-JYOTISH-NAKSHATRA",
        "SRC-JYOTISH-NAVAMSHA", "SRC-JYOTISH-DASAMSA", "SRC-JYOTISH-LUNAR-NODES",
    ]
    source_ids.append("SRC-JYOTISH-LAHIRI" if aya_key == "lahiri" else "SRC-JYOTISH-RAMAN")
    return {
        "system_version": "jyotish-v2",
        "tradition": "Jyotish / sidereal astrology",
        "convention": f"{aya_key}-{node_name}-node-27-nakshatra-v2",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_instant"],
        "input_dependencies": ["birth.date", "birth.local_time", "birth.utc_offset", "birth.coordinates"],
        "source_ids": source_ids,
        "sensitivity": "personal",
        "license_info": {
            "calculation_code": "project-authored",
            "third_party_dependencies": ["pyswisseph AGPL-3.0-or-later"],
        },
        "ayanamsa_name": aya_name,
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


def _point(lon: float, speed: float) -> dict[str, Any]:
    sign, degree, sign_index = _sign(lon)
    return {
        "longitude": round(lon % 360.0, 6),
        "sign": sign,
        "sign_index": sign_index,
        "degree": round(degree, 6),
        "speed_longitude": round(speed, 9),
        "retrograde": speed < 0,
        "nakshatra": _nakshatra(lon),
        "d9_navamsha": _navamsha(lon),
        "d10_dasamsa": _dasamsa(lon),
    }


def compute_jyotish(
    birth: dict[str, Any],
    *,
    ayanamsa: str = "lahiri",
    lunar_node: str = "mean",
) -> dict[str, Any]:
    aya_key = ayanamsa.strip().lower()
    node_key = lunar_node.strip().lower()
    if aya_key not in AYANAMSA_MODES:
        raise ValueError(f"jyotish-v2 ayanamsa must be one of: {', '.join(sorted(AYANAMSA_MODES))}")
    if node_key not in NODE_MODES:
        raise ValueError(f"jyotish-v2 lunar_node must be one of: {', '.join(sorted(NODE_MODES))}")
    meta = _meta(ayanamsa=aya_key, lunar_node=node_key)
    aya_name = meta.pop("ayanamsa_name")

    required = {"year", "month", "day", "hour", "minute", "timezone_offset", "lat", "lon"}
    missing = sorted(required - set(birth))
    if missing:
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"], **meta,
        )
    if birth.get("time_accuracy") == "unknown":
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=["jyotish-v2 requires a known birth time and does not substitute a noon chart."],
            **meta,
        )
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for Jyotish calculation.")

    swe.set_ephe_path(None)
    hour_ut = birth["hour"] + birth["minute"] / 60.0 - float(birth["timezone_offset"])
    jd = swe.julday(birth["year"], birth["month"], birth["day"], hour_ut)
    sid_mode = AYANAMSA_MODES[aya_key][1]
    swe.set_sid_mode(sid_mode)
    planet_flags = swe.FLG_SIDEREAL | swe.FLG_MOSEPH | swe.FLG_SPEED
    ayanamsa_deg = float(swe.get_ayanamsa_ut(jd))

    planets: dict[str, Any] = {}
    for name, pid in PLANETS.items():
        data = swe.calc_ut(jd, pid, planet_flags)[0]
        planets[name] = _point(float(data[0]), float(data[3]))

    node_id = NODE_MODES[node_key][1]
    node_data = swe.calc_ut(jd, node_id, planet_flags)[0]
    rahu_lon = float(node_data[0]) % 360.0
    rahu_speed = float(node_data[3])
    lunar_nodes = {
        "mode": node_key,
        "Rahu": _point(rahu_lon, rahu_speed),
        "Ketu": _point((rahu_lon + 180.0) % 360.0, rahu_speed),
        "relationship": "Ketu is emitted exactly 180 degrees opposite the selected ascending lunar node.",
    }

    cusps, ascmc = swe.houses_ex(
        jd, float(birth["lat"]), float(birth["lon"]), b"P", swe.FLG_SIDEREAL
    )
    asc_lon = float(ascmc[0]) % 360.0
    ascendant = _point(asc_lon, 0.0)
    ascendant.pop("speed_longitude")
    ascendant.pop("retrograde")

    calculation = {
        "ayanamsa": {"name": aya_name, "key": aya_key, "degrees": round(ayanamsa_deg, 6)},
        "zodiac": "sidereal",
        "ephemeris_profile": "pyswisseph-moshier-sidereal-speed-v2",
        "planets": planets,
        "lunar_nodes": lunar_nodes,
        "ascendant": ascendant,
        "house_system": "Placidus sidereal projection",
        "house_cusps": [round(float(value) % 360.0, 6) for value in cusps],
        "moon_nakshatra": planets["Moon"]["nakshatra"],
    }
    return system_result(
        "jyotish", calculation=calculation,
        limitations=[
            "This layer computes astronomical/symbolic coordinates only; it does not claim empirical personality validity.",
            "Lahiri and Raman are alternative sidereal zero-point conventions and are not blended into one result.",
            "Mean and true lunar nodes are alternative astronomical conventions; the selected mode is recorded explicitly.",
            "Vimshottari Dasha belongs in a separate timing artifact and is not emitted by this static signature.",
            "D9 and D10 are deterministic divisional projections; interpretive meanings are intentionally not embedded here.",
            "Uranus, Neptune, and Pluto are exposed as modern optional sidereal additions; they are not classical Jyotish grahas.",
        ],
        **meta,
    )


__all__ = [
    "compute_jyotish", "SIGNS", "NAKSHATRAS", "AYANAMSA_MODES", "NODE_MODES",
    "_nakshatra", "_navamsha", "_dasamsa",
]
