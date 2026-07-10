"""
Apollonius of Tyana Encoder
============================
Encodes identity through the neo-Pythagorean wisdom tradition
of Apollonius of Tyana (ca. 1-97 CE).

Core concepts from Apollonius's teachings:
1. Divine Contemplation — direct communion with the divine through silence and meditation
2. Seven Planetary Rings — each planet governs a day, creating a 7-day wisdom cycle
3. Ascetic Purity — simplicity as path to truth (few needs, high wisdom)
4. Universal Reason — truth transcends all religious boundaries
5. Silence as Power — 5 years of vow of silence before teaching
6. Anti-Sacrifice — the divine needs nothing from us
7. Wandering Sage — wisdom comes from journey, not station

The encoding maps a name through these 7 dimensions to produce
an Apollonius Identity Signature.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


# Planetary correspondences (Chaldean order)
PLANETS = {
    1: {"name": "Saturn", "day": "Saturday", "virtue": "Discipline", "shadow": "Rigidity", "element": "Earth"},
    2: {"name": "Jupiter", "day": "Thursday", "virtue": "Wisdom", "shadow": "Excess", "element": "Fire"},
    3: {"name": "Mars", "day": "Tuesday", "virtue": "Courage", "shadow": "Aggression", "element": "Fire"},
    4: {"name": "Sun", "day": "Sunday", "virtue": "Authority", "shadow": "Ego", "element": "Fire"},
    5: {"name": "Venus", "day": "Friday", "virtue": "Harmony", "shadow": "Vanity", "element": "Water"},
    6: {"name": "Mercury", "day": "Wednesday", "virtue": "Communication", "shadow": "Deception", "element": "Air"},
    7: {"name": "Moon", "day": "Monday", "virtue": "Intuition", "shadow": "Illusion", "element": "Water"},
}

# Apollonius's 7 Virtues (from his teachings)
VIRTUES = [
    "Contemplation",    # Direct communion with the divine
    "Silence",          # Power of the unspoken word
    "Purity",           # Ascetic simplicity
    "Reason",           # Universal truth beyond dogma
    "Wandering",        # Wisdom through journey
    "Compassion",       # Mercy for all beings
    "Courage",          # Standing against tyranny
]

# Sacred Numbers from Pythagorean tradition
SACRED_NUMBERS = {
    1: "Monad — The One, source of all",
    2: "Dyad — Duality, reflection",
    3: "Triad — Harmony, creation",
    4: "Tetractys — Foundation, earth",
    5: "Pentad — Life, humanity",
    6: "Hexad — Balance, cosmic order",
    7: "Heptad — Wisdom, the planets",
    8: "Ogdoad — Infinity, regeneration",
    9: "Ennead — Completion, return to One",
}


def normalize_name(text: str) -> str:
    """Normalize through the shared named transliteration profile."""
    try:
        from .pipeline import prepare_encoding_input
    except ImportError:  # pragma: no cover - direct module execution
        from pipeline import prepare_encoding_input
    return prepare_encoding_input(text)["latin_transliteration"]


def letter_to_number(letter: str) -> int:
    """Pythagorean letter-to-number mapping."""
    mapping = {
        'A': 1, 'J': 1, 'S': 1,
        'B': 2, 'K': 2, 'T': 2,
        'C': 3, 'L': 3, 'U': 3,
        'D': 4, 'M': 4, 'V': 4,
        'E': 5, 'N': 5, 'W': 5,
        'F': 6, 'O': 6, 'X': 6,
        'G': 7, 'P': 7, 'Y': 7,
        'H': 8, 'Q': 8, 'Z': 8,
        'I': 9, 'R': 9,
    }
    return mapping.get(letter, 0)


def reduce_to_single(n: int, preserve_master: bool = True) -> int:
    """Reduce number to single digit, preserving master numbers 11, 22."""
    while n > 9:
        if preserve_master and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return n


def planetary_position(index: int, total: int) -> int:
    """Map letter position to planetary influence (1-7 cycle)."""
    return ((index % 7) + 1)


@dataclass
class PlanetaryRing:
    """One of the seven planetary rings Apollonius wore."""
    planet: str
    day: str
    virtue: str
    shadow: str
    element: str
    resonance: float  # 0-1, how strongly this planet influences the name


@dataclass
class SilenceScore:
    """Apollonius's vow of silence encoded."""
    silence_years: int  # He kept 5 years
    consonant_ratio: float  # Higher = more silent potential
    vowel_ratio: float  # Higher = more expressive
    silence_depth: float  # 0-1, depth of inner silence


@dataclass
class WanderingPath:
    """The journey of the sage encoded."""
    countries_visited: int  # Symbolic: based on name length
    elements_encountered: List[str]  # Based on letter composition
    wisdom_gathered: int  # Sum of all letter values


@dataclass
class ApolloniusSignature:
    """Complete Apollonius of Tyana identity encoding."""
    original_name: str
    normalized_name: str

    # Core numerology
    total_value: int
    reduced_total: int
    digital_root: int

    # Planetary ring system
    planetary_rings: List[PlanetaryRing]
    dominant_planet: str
    planetary_day: str

    # Seven virtues alignment
    virtue_scores: dict  # virtue_name -> score 0-1
    primary_virtue: str
    secondary_virtue: str

    # Silence encoding
    silence: SilenceScore

    # Wandering path
    wandering: WanderingPath

    # Sacred geometry
    tetractys_sum: int  # Sum of first 4 letter values
    heptad_resonance: float  # Alignment with number 7 (wisdom)

    # Apollonius-specific metrics
    divine_contemplation: float  # 0-1, capacity for direct divine communion
    universal_reason: float  # 0-1, transcendence of dogma
    ascetic_purity: float  # 0-1, simplicity of form

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "original_name": self.original_name,
            "normalized_name": self.normalized_name,
            "total_value": self.total_value,
            "reduced_total": self.reduced_total,
            "digital_root": self.digital_root,
            "dominant_planet": self.dominant_planet,
            "planetary_day": self.planetary_day,
            "primary_virtue": self.primary_virtue,
            "secondary_virtue": self.secondary_virtue,
            "silence_depth": self.silence.silence_depth,
            "wandering_wisdom": self.wandering.wisdom_gathered,
            "tetractys_sum": self.tetractys_sum,
            "heptad_resonance": self.heptad_resonance,
            "divine_contemplation": self.divine_contemplation,
            "universal_reason": self.universal_reason,
            "ascetic_purity": self.ascetic_purity,
            "virtue_scores": self.virtue_scores,
            "planetary_rings": [
                {"planet": r.planet, "day": r.day, "virtue": r.virtue,
                 "shadow": r.shadow, "element": r.element, "resonance": r.resonance}
                for r in self.planetary_rings
            ],
        }

    def __repr__(self) -> str:
        return (
            f"ApolloniusSignature(name='{self.original_name}', "
            f"total={self.total_value}, planet={self.dominant_planet}, "
            f"virtue={self.primary_virtue}, contemplation={self.divine_contemplation:.2f})"
        )


def apollonius_signature(name: str) -> ApolloniusSignature:
    """
    Encode a name through the Apollonius of Tyana wisdom tradition.

    Maps the name through 7 dimensions:
    1. Planetary Ring System (7 planets, 7 virtues)
    2. Silence Score (consonant/vowel balance)
    3. Wandering Path (journey through knowledge)
    4. Sacred Geometry (tetractys, heptad)
    5. Divine Contemplation (direct communion capacity)
    6. Universal Reason (transcendence of boundaries)
    7. Ascetic Purity (simplicity of form)
    """
    normalized = normalize_name(name)
    letters = [c for c in normalized if c.isalpha()]

    if not letters:
        raise ValueError(f"Name must contain at least one letter: {name}")

    # Core numerology
    letter_values = [letter_to_number(l) for l in letters]
    total_value = sum(letter_values)
    reduced_total = reduce_to_single(total_value)
    digital_root = reduce_to_single(total_value, preserve_master=False)

    # Planetary Ring System
    planetary_rings = []
    planet_influence = {i: 0.0 for i in range(1, 8)}

    for i, (letter, value) in enumerate(zip(letters, letter_values)):
        planet_num = planetary_position(i, len(letters))
        planet_influence[planet_num] += value / total_value if total_value > 0 else 0

    for planet_num in range(1, 8):
        info = PLANETS[planet_num]
        resonance = planet_influence[planet_num]
        planetary_rings.append(PlanetaryRing(
            planet=info["name"],
            day=info["day"],
            virtue=info["virtue"],
            shadow=info["shadow"],
            element=info["element"],
            resonance=resonance,
        ))

    dominant_planet_num = max(planet_influence, key=planet_influence.get)
    dominant_planet = PLANETS[dominant_planet_num]["name"]
    planetary_day = PLANETS[dominant_planet_num]["day"]

    # Seven Virtues Alignment
    vowel_count = sum(1 for l in letters if l in 'AEIOU')
    consonant_count = len(letters) - vowel_count
    vowel_ratio = vowel_count / len(letters) if letters else 0
    consonant_ratio = consonant_count / len(letters) if letters else 0

    # Virtue scores based on letter composition and planetary alignment
    virtue_scores = {}

    # Contemplation: higher with more silence (consonants)
    virtue_scores["Contemplation"] = consonant_ratio * 0.7 + (planet_influence[1] * 0.3)

    # Silence: higher with fewer vowels
    virtue_scores["Silence"] = consonant_ratio * 0.8 + (1 - vowel_ratio) * 0.2

    # Purity: higher with simpler names (fewer letters)
    virtue_scores["Purity"] = max(0, 1 - (len(letters) / 20)) * 0.6 + (1 - vowel_ratio) * 0.4

    # Reason: higher with balanced composition
    balance = 1 - abs(vowel_ratio - 0.5) * 2
    virtue_scores["Reason"] = balance * 0.5 + (planet_influence[6] * 0.5)  # Mercury = reason

    # Wandering: higher with longer names (more journey)
    virtue_scores["Wandering"] = min(1, len(letters) / 15) * 0.7 + (planet_influence[3] * 0.3)  # Mars = courage to journey

    # Compassion: higher with Venus influence
    virtue_scores["Compassion"] = planet_influence[5] * 0.6 + vowel_ratio * 0.4

    # Courage: higher with Mars influence
    virtue_scores["Courage"] = planet_influence[3] * 0.5 + consonant_ratio * 0.5

    sorted_virtues = sorted(virtue_scores.items(), key=lambda x: x[1], reverse=True)
    primary_virtue = sorted_virtues[0][0]
    secondary_virtue = sorted_virtues[1][0]

    # Silence Score
    silence_depth = consonant_ratio * 0.6 + (planet_influence[1] * 0.4)  # Saturn = discipline
    silence = SilenceScore(
        silence_years=5,  # Apollonius's actual vow
        consonant_ratio=consonant_ratio,
        vowel_ratio=vowel_ratio,
        silence_depth=silence_depth,
    )

    # Wandering Path
    elements_encountered = []
    if any(l in 'AEIOU' for l in letters):
        elements_encountered.append("Air")  # Vowels = breath = Air
    if any(l in 'BCDFG' for l in letters):
        elements_encountered.append("Earth")  # Grounded consonants
    if any(l in 'JKLM' for l in letters):
        elements_encountered.append("Fire")  # Rising consonants
    if any(l in 'NPQRST' for l in letters):
        elements_encountered.append("Water")  # Flowing consonants

    wandering = WanderingPath(
        countries_visited=min(7, len(letters) // 2),  # Symbolic
        elements_encountered=elements_encountered,
        wisdom_gathered=total_value,
    )

    # Sacred Geometry
    tetractys_sum = sum(letter_values[:4]) if len(letter_values) >= 4 else sum(letter_values)
    heptad_resonance = planet_influence[7] if 7 in planet_influence else 0  # Moon = intuition

    # Apollonius-specific metrics
    divine_contemplation = virtue_scores["Contemplation"] * 0.4 + silence_depth * 0.3 + heptad_resonance * 0.3
    universal_reason = virtue_scores["Reason"] * 0.5 + balance * 0.3 + planet_influence[6] * 0.2
    ascetic_purity = virtue_scores["Purity"] * 0.5 + (1 - min(1, len(letters) / 20)) * 0.3 + consonant_ratio * 0.2

    return ApolloniusSignature(
        original_name=name,
        normalized_name=normalized,
        total_value=total_value,
        reduced_total=reduced_total,
        digital_root=digital_root,
        planetary_rings=planetary_rings,
        dominant_planet=dominant_planet,
        planetary_day=planetary_day,
        virtue_scores=virtue_scores,
        primary_virtue=primary_virtue,
        secondary_virtue=secondary_virtue,
        silence=silence,
        wandering=wandering,
        tetractys_sum=tetractys_sum,
        heptad_resonance=heptad_resonance,
        divine_contemplation=divine_contemplation,
        universal_reason=universal_reason,
        ascetic_purity=ascetic_purity,
    )
