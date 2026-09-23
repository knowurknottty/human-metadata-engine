"""Sidereal/Jyotish astronomical projection using Swiss Ephemeris.

v3 supports explicit Lahiri or Raman ayanamsa selection, 27 nakshatras/padas,
D9 Navamsha, D10 Dasamsa, explicit mean/true lunar-node conventions, and
zone-aware conversion of civil birth time to one UTC instant.
Interpretive meanings and dashas remain outside this static calculation module.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

from system_contracts import system_result
from time_context import TimezoneResolutionError, normalize_birth_timezone

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


def _uses_iana(birth: dict[str, Any]) -> bool:
    return bool(birth.get("timezone_id") or birth.get("tzid") or birth.get("timezone_name"))


def _meta(*, ayanamsa: str, lunar_node: str, use_iana: bool) -> dict[str, Any]:
    aya_key = ayanamsa.strip().lower()
    node_key = lunar_node.strip().lower()
    aya_name = AYANAMSA_MODES[aya_key][0]
    node_name = NODE_MODES[node_key][0]
    source_ids = [
        "SRC-SWISSEPH-SIDEREAL", "SRC-JYOTISH-NAKSHATRA",
        "SRC-JYOTISH-NAVAMSHA", "SRC-JYOTISH-DASAMSA", "SRC-JYOTISH-LUNAR-NODES",
    ]
    source_ids.append("SRC-JYOTISH-LAHIRI" if aya_key == "lahiri" else "SRC-JYOTISH-RAMAN")
    if use_iana:
        source_ids.append("SRC-IANA-TZDB")
    zone_dependency = "birth.timezone_id" if use_iana else "birth.utc_offset"
    return {
        "system_version": "jyotish-v3",
        "tradition": "Jyotish / sidereal astrology",
        "convention": f"{aya_key}-{node_name}-node-27-nakshatra-zone-aware-v3",
        "artifact_class": "static_signature",
        "epistemic_class": "deterministic_calculation",
        "dependency_roots": ["birth_instant"],
        "input_dependencies": ["birth.date", "birth.local_time", zone_dependency, "birth.coordinates"],
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
        raise ValueError(f"jyotish-v3 ayanamsa must be one of: {', '.join(sorted(AYANAMSA_MODES))}")
    if node_key not in NODE_MODES:
        raise ValueError(f"jyotish-v3 lunar_node must be one of: {', '.join(sorted(NODE_MODES))}")
    use_iana = _uses_iana(birth)
    meta = _meta(ayanamsa=aya_key, lunar_node=node_key, use_iana=use_iana)
    aya_name = meta.pop("ayanamsa_name")

    required = {"year", "month", "day", "hour", "minute", "lat", "lon"}
    missing = sorted(required - set(birth))
    if not use_iana and "timezone_offset" not in birth:
        missing.append("timezone_id|timezone_offset")
    if missing:
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=[f"Missing required birth fields: {', '.join(missing)}"], **meta,
        )
    if birth.get("time_accuracy") == "unknown":
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=["jyotish-v3 requires a known birth time and does not substitute a noon chart."],
            **meta,
        )
    if swe is None:
        raise RuntimeError("Swiss Ephemeris is required for Jyotish calculation.")

    try:
        _, timezone_basis = normalize_birth_timezone(birth)
    except TimezoneResolutionError as exc:
        return system_result(
            "jyotish", calculation={}, status="input_insufficient",
            limitations=[str(exc)], **meta,
        )

    utc_value = datetime.fromisoformat(timezone_basis["birth_utc_iso"].replace("Z", "+00:00"))
    hour_ut = (
        utc_value.hour
        + utc_value.minute / 60.0
        + utc_value.second / 3600.0
        + utc_value.microsecond / 3_600_000_000.0
    )
    swe.set_ephe_path(None)
    jd = swe.julday(utc_value.year, utc_value.month, utc_value.day, hour_ut)
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
        "ephemeris_profile": "pyswisseph-moshier-sidereal-speed-v3",
        "timezone_basis": timezone_basis,
        "planets": planets,
        "lunar_nodes": lunar_nodes,
        "ascendant": ascendant,
        "house_system": "Placidus sidereal projection",
        "house_cusps": [round(float(value) % 360.0, 6) for value in cusps],
        "moon_nakshatra": planets["Moon"]["nakshatra"],
    }
    return system_result(
        "jyotish", calculation=calculation,
        interpretation={
            "disclosure": {
                "convention": meta["convention"],
                "approximation_precision": "undisclosed",
                "precision_basis": (
                    "No documented arcsecond figure for this sidereal projection is published in the "
                    "implementation docs, so precision is disclosed as undisclosed rather than invented. "
                    "This label never implies birth-time precision or true-solar support."
                ),
            }
        },
        limitations=[
            "This layer computes astronomical/symbolic coordinates only; it does not claim empirical personality validity.",
            "Lahiri and Raman are alternative sidereal zero-point conventions and are not blended into one result.",
            "Mean and true lunar nodes are alternative astronomical conventions; the selected mode is recorded explicitly.",
            "An explicit IANA timezone_id is authoritative when supplied; a numeric offset remains the compatibility fallback.",
            "Ambiguous civil times require timezone_fold and nonexistent civil times fail closed rather than selecting an instant silently.",
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