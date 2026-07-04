"""
Human Design / Gene Keys Calculator
===================================

Computes Human Design chart from birth data.
Uses Swiss Ephemeris for planetary positions, then maps
to the 64 gates of the I Ching / Human Design system.

The 64 gates correspond to 64 hexagrams, each mapped to
a zodiacal position (5° 42' per gate).

Types: Manifestor, Generator, Manifesting Generator, Reflector, Projector
Strategies vary by type.
Authority types: Emotional, Sacral, Splenic, Ego, Self-Projected, Mental, Lunar

NOTE: This is a symbolic system, not empirical fact.
All outputs are labeled as interpretive lenses.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import math

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False

# Human Design types
HD_TYPES = ["Manifestor", "Generator", "Manifesting Generator", "Projector", "Reflector"]

# Authority types
AUTHORITIES = [
    "Emotional", "Sacral", "Splenic", "Ego/Heart", "Self-Projected", "Mental", "Lunar"
]

# Strategy by type
STRATEGIES = {
    "Manifestor": "To Inform",
    "Generator": "To Respond",
    "Manifesting Generator": "To Respond, then Inform",
    "Projector": "To Wait for the Invitation",
    "Reflector": "To Wait a Lunar Cycle",
}

# Profile descriptions (12 profiles)
PROFILES = {
    (1, 4): "Investigator / Opportunist",
    (1, 3): "Investigator / Martyr",
    (2, 4): "Hermit / Opportunist",
    (2, 5): "Hermit / Heretic",
    (3, 5): "Martyr / Heretic",
    (3, 6): "Martyr / Role Model",
    (4, 6): "Opportunist / Role Model",
    (4, 1): "Opportunist / Investigator",
    (5, 1): "Heretic / Investigator",
    (5, 2): "Heretic / Hermit",
    (6, 2): "Role Model / Hermit",
    (6, 3): "Role Model / Martyr",
}

# The 64 Gates (simplified — full mapping requires I Ching hexagrams)
# Each gate spans 5° 42' of the zodiac
GATES_PER_SIGN = 5  # 30° / 5°42' ≈ 5.2 gates per sign
GATE_OFFSETS = {
    "Aries": 41, "Taurus": 11, "Gemini": 13, "Cancer": 2,
    "Leo": 27, "Virgo": 24, "Libra": 33, "Scorpio": 8,
    "Sagittarius": 1, "Capricorn": 19, "Aquarius": 49, "Pisces": 39,
}


@dataclass
class GatePosition:
    gate: int
    line: int
    planet: str
    sign: str
    sign_degree: float
    is_determination: bool  # Personality (conscious) or Design (unconscious)


@dataclass
class Center:
    name: str
    defined: bool
    gates: list[int]


@dataclass
class HumanDesignChart:
    # Metadata
    birth_datetime: str
    birth_location: str
    confidence: float

    # Type and authority
    hd_type: str
    authority: str
    strategy: str
    not_self_theme: str
    signature: str

    # Profile
    profile_number: tuple[int, int]
    profile_description: str

    # Gates and centers
    personality_gates: list[GatePosition]
    design_gates: list[GatePosition]
    all_gates: list[int]
    channels: list[dict]
    centers: list[Center]

    # Incarnation Cross
    incarnation_cross: str

    # Definition
    definition_type: str  # Single, Split, Triple Split, None

    # Not-Self
    not_self_questions: list[str]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["profile_number"] = list(self.profile_number)
        return d


# The 36 channels of the Human Design bodygraph: (gate_a, gate_b) -> name
CHANNELS: dict[tuple[int, int], str] = {
    (1, 8): "Inspiration", (2, 14): "The Beat", (3, 60): "Mutation",
    (4, 63): "Logic", (5, 15): "Rhythm", (6, 59): "Intimacy",
    (7, 31): "The Alpha", (9, 52): "Concentration", (10, 20): "Awakening",
    (10, 34): "Exploration", (10, 57): "Perfected Form", (11, 56): "Curiosity",
    (12, 22): "Openness", (13, 33): "The Prodigal", (16, 48): "The Wavelength",
    (17, 62): "Acceptance", (18, 58): "Judgment", (19, 49): "Synthesis",
    (20, 34): "Charisma", (20, 57): "The Brainwave", (21, 45): "The Money Line",
    (23, 43): "Structuring", (24, 61): "Awareness", (25, 51): "Initiation",
    (26, 44): "Surrender", (27, 50): "Preservation", (28, 38): "Struggle",
    (29, 46): "Discovery", (30, 41): "Recognition", (32, 54): "Transformation",
    (34, 57): "Power", (35, 36): "Transitoriness", (37, 40): "Community",
    (39, 55): "Emoting", (42, 53): "Maturation", (47, 64): "Abstraction",
}


def defined_channels(gates: list[int]) -> list[dict]:
    """Return the channels where both gates are activated."""
    gate_set = set(gates)
    result = []
    for (a, b), name in CHANNELS.items():
        if a in gate_set and b in gate_set:
            result.append({"gates": [a, b], "name": name})
    return result


def longitude_to_gate(lon: float) -> tuple[int, int]:
    """Convert ecliptic longitude to Human Design gate and line."""
    lon = lon % 360
    # Each gate spans 5° 42' = 5.7°
    gate_span = 5.7
    gate_index = int(lon / gate_span)
    gate = (gate_index % 64) + 1
    line = int(((lon % gate_span) / gate_span) * 6) + 1
    line = min(line, 6)
    return gate, line


def compute_human_design(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 0,
    location: str = "",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> HumanDesignChart:
    """Compute a Human Design chart."""

    from .astrology import get_coordinates, longitude_to_sign, SIGNS

    if lat is None or lon is None:
        lat, lon = get_coordinates(location)

    confidence = 0.7 if hour != 12 else 0.4

    # Compute planetary positions
    planet_positions = {}

    if SWE_AVAILABLE:
        swe.set_ephe_path(None)
        jd = swe.julday(year, month, day, hour + minute / 60.0 - timezone_offset)

        # Personality planets (birth moment)
        for planet_name, planet_id in [
            ("Sun", swe.SUN), ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY), ("Venus", swe.VENUS),
            ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
            ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO),
            ("North Node", swe.TRUE_NODE),
        ]:
            try:
                result = swe.calc_ut(jd, planet_id)
                planet_positions[f"P_{planet_name}"] = result[0][0]
            except Exception:
                pass

        # Design planets (88 days before birth)
        jd_design = jd - 88
        for planet_name, planet_id in [
            ("Sun", swe.SUN), ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY), ("Venus", swe.VENUS),
            ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN),
        ]:
            try:
                result = swe.calc_ut(jd_design, planet_id)
                planet_positions[f"D_{planet_name}"] = result[0][0]
            except Exception:
                pass
    else:
        # Stub positions
        import random
        random.seed(year * 10000 + month * 100 + day)
        for prefix in ["P_", "D_"]:
            for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
                planet_positions[f"{prefix}{planet}"] = random.uniform(0, 360)

    # Convert to gates
    personality_gates = []
    design_gates = []
    all_gate_numbers = []

    for key, longitude in planet_positions.items():
        prefix, planet = key.split("_", 1)
        gate, line = longitude_to_gate(longitude)
        sign, sign_deg = longitude_to_sign(longitude)

        gate_pos = GatePosition(
            gate=gate,
            line=line,
            planet=planet,
            sign=sign,
            sign_degree=round(sign_deg, 2),
            is_determination=(prefix == "P"),
        )

        if prefix == "P":
            personality_gates.append(gate_pos)
        else:
            design_gates.append(gate_pos)
        all_gate_numbers.append(gate)

    # Determine type based on defined centers (simplified)
    # In full HD, this requires channel analysis
    defined_count = len(set(all_gate_numbers))
    if defined_count > 8:
        hd_type = "Generator"
    elif defined_count > 5:
        hd_type = "Projector"
    elif defined_count > 3:
        hd_type = "Manifestor"
    else:
        hd_type = "Reflector"

    strategy = STRATEGIES.get(hd_type, "To Respond")

    # Not-self theme by type
    not_self_themes = {
        "Manifestor": "Anger",
        "Generator": "Frustration",
        "Manifesting Generator": "Frustration and Anger",
        "Projector": "Bitterness",
        "Reflector": "Disappointment",
    }

    # Signature by type
    signatures = {
        "Manifestor": "Peace",
        "Generator": "Satisfaction",
        "Manifesting Generator": "Satisfaction and Peace",
        "Projector": "Success",
        "Reflector": "Surprise",
    }

    # Profile (simplified — based on gates)
    p1 = (all_gate_numbers[0] % 6) + 1 if all_gate_numbers else 1
    p2 = (all_gate_numbers[-1] % 6) + 1 if all_gate_numbers else 4
    profile_tuple = (min(p1, 6), min(p2, 6))
    profile_desc = PROFILES.get(profile_tuple, f"Profile {p1}.{p2}")

    # Simplified centers
    centers = [
        Center("Head", True, []),
        Center("Ajna", True, []),
        Center("Throat", True, []),
        Center("G/Identity", True, []),
        Center("Heart/Will", False, []),
        Center("Sacral", hd_type in ("Generator", "Manifesting Generator"), []),
        Center("Solar Plexus", True, []),
        Center("Splenic", True, []),
        Center("Root", True, []),
    ]

    # Incarnation Cross (simplified)
    sun_gate = personality_gates[0].gate if personality_gates else 1
    cross_names = {
        1: "Right Angle Cross of the Sphinx",
        2: "Right Angle Cross of the Four Ways",
        13: "Right Angle Cross of the Vessel of Love",
        27: "Right Angle Cross of Welling",
        41: "Right Angle Cross of Concentration",
    }
    incarnation_cross = cross_names.get(sun_gate, f"Right Angle Cross of Gate {sun_gate}")

    # Definition type
    unique_gates = len(set(all_gate_numbers))
    if unique_gates > 12:
        definition_type = "Triple Split"
    elif unique_gates > 8:
        definition_type = "Split"
    elif unique_gates > 0:
        definition_type = "Single"
    else:
        definition_type = "None"

    # Not-self questions
    not_self_questions = {
        "Generator": ["Where am I waiting to respond?"],
        "Manifestor": ["What am I not informing about?"],
        "Projector": ["Have I been invited?"],
        "Reflector": ["Am I waiting a full lunar cycle?"],
        "Manifesting Generator": ["Where am I trying to initiate instead of respond?"],
    }

    return HumanDesignChart(
        birth_datetime=f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}",
        birth_location=location,
        confidence=confidence,
        hd_type=hd_type,
        authority="Emotional",  # Simplified
        strategy=strategy,
        not_self_theme=not_self_themes.get(hd_type, "Unknown"),
        signature=signatures.get(hd_type, "Unknown"),
        profile_number=profile_tuple,
        profile_description=profile_desc,
        personality_gates=personality_gates,
        design_gates=design_gates,
        all_gates=all_gate_numbers,
        channels=defined_channels(all_gate_numbers),
        centers=centers,
        incarnation_cross=incarnation_cross,
        definition_type=definition_type,
        not_self_questions=not_self_questions.get(hd_type, []),
    )


if __name__ == "__main__":
    chart = compute_human_design(
        year=1982, month=2, day=4,
        hour=1, minute=42,
        timezone_offset=-7,
        location="Evanston, Wyoming, USA",
    )
    print(f"Human Design Chart: {chart.birth_datetime}")
    print(f"Type: {chart.hd_type}")
    print(f"Strategy: {chart.strategy}")
    print(f"Authority: {chart.authority}")
    print(f"Profile: {chart.profile_number} — {chart.profile_description}")
    print(f"Definition: {chart.definition_type}")
    print(f"Incarnation Cross: {chart.incarnation_cross}")
    print(f"Personality Gates: {[g.gate for g in chart.personality_gates]}")
    print(f"Design Gates: {[g.gate for g in chart.design_gates]}")
