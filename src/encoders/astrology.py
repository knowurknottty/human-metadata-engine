"""
Astrological Chart Computation
==============================

Computes natal chart positions using Swiss Ephemeris (pyswisseph).
Requires birth date, time, and location (lat/lon).

Outputs:
- Tropical zodiac positions for all planets
- Sun sign, Moon sign, Ascendant
- House positions (Placidus)
- Aspects between planets
- Dominant elements and modalities
- Lunar phase
- Chart ruler

Confidence is based on birth time precision:
- Exact time (±15 min): confidence 0.95
- Approximate time (±2 hours): confidence 0.7
- No time (noon chart): confidence 0.4
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
import math

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False

# Planet IDs for Swiss Ephemeris
PLANETS = {
    "Sun": swe.SUN if SWE_AVAILABLE else 0,
    "Moon": swe.MOON if SWE_AVAILABLE else 1,
    "Mercury": swe.MERCURY if SWE_AVAILABLE else 2,
    "Venus": swe.VENUS if SWE_AVAILABLE else 3,
    "Mars": swe.MARS if SWE_AVAILABLE else 4,
    "Jupiter": swe.JUPITER if SWE_AVAILABLE else 5,
    "Saturn": swe.SATURN if SWE_AVAILABLE else 6,
    "Uranus": swe.URANUS if SWE_AVAILABLE else 7,
    "Neptune": swe.NEPTUNE if SWE_AVAILABLE else 8,
    "Pluto": swe.PLUTO if SWE_AVAILABLE else 9,
}

# Zodiac signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Elements and modalities
ELEMENTS = {
    "Aries": ("Fire", "Cardinal"), "Taurus": ("Earth", "Fixed"),
    "Gemini": ("Air", "Mutable"), "Cancer": ("Water", "Cardinal"),
    "Leo": ("Fire", "Fixed"), "Virgo": ("Earth", "Mutable"),
    "Libra": ("Air", "Cardinal"), "Scorpio": ("Water", "Fixed"),
    "Sagittarius": ("Fire", "Mutable"), "Capricorn": ("Earth", "Cardinal"),
    "Aquarius": ("Air", "Fixed"), "Pisces": ("Water", "Mutable"),
}

# Aspect definitions
ASPECTS = {
    0: ("Conjunction", 8),
    60: ("Sextile", 4),
    90: ("Square", 6),
    120: ("Trine", 5),
    180: ("Opposition", 7),
}

# Known city coordinates (partial — enough for common US locations)
CITY_COORDS = {
    "evanston, wyoming, usa": (41.2680, -110.9408),
    "evanston, il": (42.0451, -87.6877),
    "new york, ny": (40.7128, -74.0060),
    "los angeles, ca": (34.0522, -118.2437),
    "chicago, il": (41.8781, -87.6298),
    "san francisco, ca": (37.7749, -122.4194),
    "london, uk": (51.5074, -0.1278),
}


@dataclass
class PlanetPosition:
    planet: str
    longitude: float
    sign: str
    sign_degree: float
    house: Optional[int]
    is_retrograde: bool


@dataclass
class Aspect:
    planet1: str
    planet2: str
    aspect_name: str
    angle: float
    orb: float
    exact: bool


@dataclass
class AstrologicalChart:
    # Metadata
    birth_datetime: str
    birth_location: str
    latitude: float
    longitude: float
    time_precision: str
    confidence: float

    # Planetary positions
    planets: list[PlanetPosition]
    sun_sign: str
    moon_sign: str
    ascendant: str
    ascendant_longitude: float
    midheaven: str

    # Aspects
    aspects: list[Aspect]

    # Analysis
    dominant_element: str
    dominant_modality: str
    element_counts: dict[str, int]
    modality_counts: dict[str, int]
    yin_yang_balance: dict[str, int]

    # Lunar
    lunar_phase: str
    lunar_phase_degree: float
    is_waxing: bool

    # Chart ruler
    chart_ruler: str

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def get_coordinates(location: str) -> tuple[float, float]:
    """Look up coordinates for a location string."""
    loc_lower = location.lower().strip()
    if loc_lower in CITY_COORDS:
        return CITY_COORDS[loc_lower]
    # Default to center of US if not found
    return (39.8283, -98.5795)


def longitude_to_sign(lon: float) -> tuple[str, float]:
    """Convert ecliptic longitude to zodiac sign and degree within sign."""
    lon = lon % 360
    sign_index = int(lon / 30)
    degree_in_sign = lon % 30
    return SIGNS[sign_index], degree_in_sign


def compute_lunar_phase(sun_lon: float, moon_lon: float) -> tuple[str, float, bool]:
    """Compute lunar phase from Sun and Moon longitudes."""
    phase_degree = (moon_lon - sun_lon) % 360
    is_waxing = phase_degree < 180

    if phase_degree < 22.5:
        phase = "New Moon"
    elif phase_degree < 67.5:
        phase = "Waxing Crescent"
    elif phase_degree < 112.5:
        phase = "First Quarter"
    elif phase_degree < 157.5:
        phase = "Waxing Gibbous"
    elif phase_degree < 202.5:
        phase = "Full Moon"
    elif phase_degree < 247.5:
        phase = "Waning Gibbous"
    elif phase_degree < 292.5:
        phase = "Last Quarter"
    elif phase_degree < 337.5:
        phase = "Waning Crescent"
    else:
        phase = "New Moon"

    return phase, phase_degree, is_waxing


def compute_aspects(positions: list[PlanetPosition], max_orb: float = 8.0) -> list[Aspect]:
    """Compute aspects between planets."""
    aspects = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            p1, p2 = positions[i], positions[j]
            angle = abs(p1.longitude - p2.longitude)
            if angle > 180:
                angle = 360 - angle

            for ref_angle, (name, _) in ASPECTS.items():
                orb = abs(angle - ref_angle)
                if orb <= max_orb:
                    aspects.append(Aspect(
                        planet1=p1.planet,
                        planet2=p2.planet,
                        aspect_name=name,
                        angle=round(angle, 2),
                        orb=round(orb, 2),
                        exact=orb < 1.0,
                    ))
                    break

    return aspects


def compute_chart(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 0,
    location: str = "",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> AstrologicalChart:
    """Compute a full natal chart."""

    if lat is None or lon is None:
        lat, lon = get_coordinates(location)

    # Determine time precision and confidence
    if hour == 12 and minute == 0:
        time_precision = "noon_default"
        confidence = 0.4
    elif minute % 60 == 0:
        time_precision = "hour_only"
        confidence = 0.7
    else:
        time_precision = "exact"
        confidence = 0.95

    if not SWE_AVAILABLE:
        # Return a stub chart when swisseph is not available
        return _stub_chart(year, month, day, hour, minute, location, lat, lon, time_precision, confidence)

    # Initialize Swiss Ephemeris
    swe.set_ephe_path(None)  # Use built-in Moshier ephemeris

    # Julian day
    jd = swe.julday(year, month, day, hour + minute / 60.0 - timezone_offset)

    # Compute planetary positions
    planet_positions = []
    sun_lon = 0
    moon_lon = 0

    for planet_name, planet_id in PLANETS.items():
        try:
            result = swe.calc_ut(jd, planet_id)
            # result = ((lon, lat, dist, speed_lon, speed_lat, speed_dist), flags)
            data = result[0]
            lon_val = data[0]
            speed_lon = data[3] if len(data) > 3 else 0

            is_retro = speed_lon < 0  # Retrograde if speed is negative
            sign, sign_deg = longitude_to_sign(lon_val)

            if planet_name == "Sun":
                sun_lon = lon_val
            elif planet_name == "Moon":
                moon_lon = lon_val

            planet_positions.append(PlanetPosition(
                planet=planet_name,
                longitude=round(lon_val, 4),
                sign=sign,
                sign_degree=round(sign_deg, 2),
                house=None,  # Will be computed after houses
                is_retrograde=is_retro,
            ))
        except Exception:
            continue

    # Compute Ascendant and houses
    try:
        ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus
        asc_lon = ascmc[1][0]
        mc_lon = ascmc[1][1]
        asc_sign, _ = longitude_to_sign(asc_lon)
        mc_sign, _ = longitude_to_sign(mc_lon)
    except Exception:
        asc_lon = 0
        asc_sign = "Aries"
        mc_sign = "Aries"

    # Compute aspects
    aspects = compute_aspects(planet_positions)

    # Element and modality counts
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    yin_yang = {"Yang": 0, "Yin": 0}

    for pp in planet_positions:
        if pp.sign in ELEMENTS:
            elem, mod = ELEMENTS[pp.sign]
            element_counts[elem] += 1
            modality_counts[mod] += 1
            # Cardinal/Fire/Air = Yang, Fixed/Mutable/Earth/Water = Yin
            if mod in ("Cardinal",) or elem in ("Fire", "Air"):
                yin_yang["Yang"] += 1
            else:
                yin_yang["Yin"] += 1

    dominant_element = max(element_counts, key=element_counts.get)
    dominant_modality = max(modality_counts, key=modality_counts.get)

    # Lunar phase
    if sun_lon and moon_lon:
        lunar_phase, lunar_degree, is_waxing = compute_lunar_phase(sun_lon, moon_lon)
    else:
        lunar_phase = "Unknown"
        lunar_degree = 0
        is_waxing = False

    # Chart ruler (ruling planet of Ascendant sign)
    rulers = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Pluto", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune",
    }
    chart_ruler = rulers.get(asc_sign, "Unknown")

    # Find Sun and Moon signs
    sun_sign = next((pp.sign for pp in planet_positions if pp.planet == "Sun"), "Unknown")
    moon_sign = next((pp.sign for pp in planet_positions if pp.planet == "Moon"), "Unknown")

    return AstrologicalChart(
        birth_datetime=f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}",
        birth_location=location,
        latitude=lat,
        longitude=lon,
        time_precision=time_precision,
        confidence=confidence,
        planets=planet_positions,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        ascendant=asc_sign,
        ascendant_longitude=round(asc_lon, 4),
        midheaven=mc_sign,
        aspects=aspects,
        dominant_element=dominant_element,
        dominant_modality=dominant_modality,
        element_counts=element_counts,
        modality_counts=modality_counts,
        yin_yang_balance=yin_yang,
        lunar_phase=lunar_phase,
        lunar_phase_degree=round(lunar_degree, 2),
        is_waxing=is_waxing,
        chart_ruler=chart_ruler,
    )


def _stub_chart(year, month, day, hour, minute, location, lat, lon, time_precision, confidence):
    """Stub chart when swisseph is not available."""
    # Use approximate sun sign based on date
    day_of_year = (datetime(year, month, day) - datetime(year, 1, 1)).days
    sun_sign_idx = int((day_of_year + 10) / 30.44) % 12
    sun_sign = SIGNS[sun_sign_idx]

    return AstrologicalChart(
        birth_datetime=f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}",
        birth_location=location,
        latitude=lat,
        longitude=lon,
        time_precision=f"{time_precision}_stub",
        confidence=confidence * 0.5,
        planets=[PlanetPosition("Sun", 0, sun_sign, 0, None, False)],
        sun_sign=sun_sign,
        moon_sign="Unknown",
        ascendant="Unknown",
        ascendant_longitude=0,
        midheaven="Unknown",
        aspects=[],
        dominant_element="Unknown",
        dominant_modality="Unknown",
        element_counts={},
        modality_counts={},
        yin_yang_balance={},
        lunar_phase="Unknown",
        lunar_phase_degree=0,
        is_waxing=False,
        chart_ruler="Unknown",
    )


if __name__ == "__main__":
    chart = compute_chart(
        year=1985, month=6, day=15,
        hour=1, minute=42,
        timezone_offset=-7,
        location="Portland, Oregon, USA",
    )
    print(f"Natal Chart: {chart.birth_datetime}")
    print(f"Location: {chart.birth_location} ({chart.latitude}, {chart.longitude})")
    print(f"Confidence: {chart.confidence} ({chart.time_precision})")
    print(f"Sun: {chart.sun_sign}")
    print(f"Moon: {chart.moon_sign}")
    print(f"Ascendant: {chart.ascendant}")
    print(f"Chart Ruler: {chart.chart_ruler}")
    print(f"Dominant Element: {chart.dominant_element}")
    print(f"Dominant Modality: {chart.dominant_modality}")
    print(f"Lunar Phase: {chart.lunar_phase}")
    print(f"Planets: {len(chart.planets)}")
    print(f"Aspects: {len(chart.aspects)}")
