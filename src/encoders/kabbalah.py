"""
Kabbalistic Tree of Life Encoder
=================================

Encodes names through the 10 Sephiroth and 22 Paths of the Kabbalistic Tree of Life.

Sephiroth (Emanations):
1 Kether (Crown) — Pure existence
2 Chokmah (Wisdom) — Dynamic potential
3 Binah (Understanding) — Structured form
4 Chesed (Mercy) — Expansion
5 Geburah (Severity) — Contraction
6 Tiphareth (Beauty) — Harmony/balance
7 Netzach (Victory) — Endurance
8 Hod (Splendor) — Intellect
9 Yesod (Foundation) — Astral/psychic
10 Malkuth (Kingdom) — Physical world

22 Paths connect the Sephiroth, each associated with a Hebrew letter,
an element/zodiac sign, and a Major Arcana tarot card.

Qliphoth (Shadow Side): 10 shells/husks representing unbalanced Sephiroth.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict


# 10 Sephiroth with attributes
SEPHIROTH = {
    1: {"name": "Kether", "title": "Crown", "quality": "Pure Existence", "element": "Spirit", "color": "White", "body": "Brain"},
    2: {"name": "Chokmah", "title": "Wisdom", "quality": "Dynamic Potential", "element": "Air", "color": "Grey", "body": "Right Brain"},
    3: {"name": "Binah", "title": "Understanding", "quality": "Structured Form", "element": "Water", "color": "Black", "body": "Left Brain"},
    4: {"name": "Chesed", "title": "Mercy", "quality": "Expansion", "element": "Water", "color": "Blue", "body": "Right Arm"},
    5: {"name": "Geburah", "title": "Severity", "quality": "Contraction", "element": "Fire", "color": "Red", "body": "Left Arm"},
    6: {"name": "Tiphareth", "title": "Beauty", "quality": "Harmony", "element": "Fire", "color": "Yellow", "body": "Heart/Chest"},
    7: {"name": "Netzach", "title": "Victory", "quality": "Endurance", "element": "Earth", "color": "Green", "body": "Right Leg"},
    8: {"name": "Hod", "title": "Splendor", "quality": "Intellect", "element": "Air", "color": "Orange", "body": "Left Leg"},
    9: {"name": "Yesod", "title": "Foundation", "quality": "Psychic", "element": "Air", "color": "Violet", "body": "Reproductive"},
    10: {"name": "Malkuth", "title": "Kingdom", "quality": "Physical", "element": "Earth", "color": "Olive/Citron", "body": "Feet"},
}

# Qliphoth (shadow shells) — unbalanced aspects
QLIPHOTH = {
    1: "Thaumiel (Twin of God — duality/schism)",
    2: "Ghogiel (Hindrance — obstruction/confusion)",
    3: "Satariel (Concealer — veiling/obscuring)",
    4: "Agiel (Suffering — cruelty/oppression)",
    5: "Golab (Burning — rage/destruction)",
    6: "Tagaririm (Disputers — inner conflict)",
    7: "Ariab (Murmurers — rebellion/chaos)",
    8: "Samael (Poison of God — intellect without soul)",
    9: "Gamaliel (Obscene — perverse foundation)",
    10: "Nehemoth (Whisperers — deception through the physical)",
}

# 22 Paths: letter -> (seph1, seph2, element, tarot_major, meaning)
PATHS_22 = {
    "A": (1, 2, "Air", "The Fool", "Beginnings, innocence"),
    "B": (1, 6, "Air", "The Magician", "Willpower, creation"),
    "G": (1, 3, "Water", "The High Priestess", "Intuition, mystery"),
    "D": (2, 3, "Air", "The Empress", "Abundance, nurturing"),
    "H": (2, 6, "Fire", "The Emperor", "Authority, structure"),
    "V": (2, 4, "Fire", "The Hierophant", "Tradition, wisdom"),
    "Z": (3, 6, "Water", "The Lovers", "Choice, union"),
    "Ch": (4, 5, "Fire", "The Chariot", "Victory, willpower"),
    "T": (4, 6, "Fire", "Strength", "Courage, patience"),
    "I": (4, 7, "Air", "The Hermit", "Inner guidance"),
    "K": (5, 8, "Fire", "Wheel of Fortune", "Cycles, destiny"),
    "L": (5, 6, "Water", "Justice", "Truth, fairness"),
    "M": (6, 7, "Water", "The Hanged Man", "Surrender, new perspective"),
    "N": (6, 8, "Fire", "Death", "Transformation"),
    "S": (6, 9, "Water", "Temperance", "Balance, moderation"),
    "O": (7, 8, "Fire", "The Devil", "Shadow, attachment"),
    "P": (7, 9, "Earth", "The Tower", "Upheaval, revelation"),
    "Ts": (7, 10, "Earth", "The Star", "Hope, renewal"),
    "Q": (8, 9, "Air", "The Moon", "Illusion, subconscious"),
    "R": (8, 10, "Fire", "The Sun", "Vitality, success"),
    "Sh": (9, 10, "Water", "Judgement", "Rebirth, calling"),
    "Th": (9, 10, "Earth", "The World", "Completion, integration"),
}

# Hebrew letter numerical values
HEBREW_VALUES = {
    "A": 1, "B": 2, "G": 3, "D": 4, "H": 5, "V": 6, "Z": 7,
    "Ch": 8, "T": 9, "I": 10, "K": 20, "L": 30, "M": 40, "N": 50,
    "S": 60, "O": 60, "P": 80, "Ts": 90, "Q": 100, "R": 200,
    "Sh": 300, "Th": 400,
}

# Latin-to-Hebrew letter mapping
LATIN_TO_HEBREW = {
    "A": "A", "B": "B", "C": "K", "D": "D", "E": "H", "F": "P",
    "G": "G", "H": "Ch", "I": "I", "J": "I", "K": "K", "L": "L",
    "M": "M", "N": "N", "O": "O", "P": "P", "Q": "Q", "R": "R",
    "S": "S", "T": "T", "U": "V", "V": "V", "W": "V", "X": "Ts",
    "Y": "I", "Z": "Z",
}

HEBREW_TO_KEY = {
    "א": "A", "ב": "B", "ג": "G", "ד": "D", "ה": "H", "ו": "V", "ז": "Z",
    "ח": "Ch", "ט": "T", "י": "I", "כ": "K", "ך": "K", "ל": "L", "מ": "M",
    "ם": "M", "נ": "N", "ן": "N", "ס": "S", "ע": "O", "פ": "P", "ף": "P",
    "צ": "Ts", "ץ": "Ts", "ק": "Q", "ר": "R", "ש": "Sh", "ת": "Th",
}


def normalize(text: str) -> str:
    """Keep native Hebrew letters; transliterate other supported scripts."""
    native = [ch for ch in text if ch in HEBREW_TO_KEY]
    if native:
        return "".join(native)
    try:
        from .pipeline import prepare_encoding_input
    except ImportError:  # pragma: no cover - direct module execution
        from pipeline import prepare_encoding_input
    return "".join(
        ch for ch in prepare_encoding_input(text)["latin_transliteration"]
        if "A" <= ch <= "Z"
    )


def reduce_single(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


@dataclass(frozen=True)
class KabbalahSignature:
    original_text: str
    normalized_text: str

    # Sephirothic mapping
    total_value: int
    reduced_value: int
    sephiroth_positions: list[dict]  # Which sephiroth each letter maps to
    sephiroth_frequencies: dict[int, int]  # Count of letters in each sephirah
    dominant_sephirah: int  # Most frequent sephirah
    dominant_sephirah_name: str

    # Path analysis
    paths_activated: list[dict]  # Which of the 22 paths are touched
    path_count: int
    unique_paths: int

    # Tree traversal
    highest_sephirah: int
    lowest_sephirah: int
    tree_span: int  # highest - lowest (how far across the tree the name reaches)
    tree_depth: int  # unique sephiroth touched

    # Qliphoth (shadow)
    qliphoth_activated: list[str]

    # Hebrew correspondence
    hebrew_letters: list[dict]
    hebrew_total: int

    # Balance
    pillar_balance: dict  # Pillar of Mercy (2,4,7,10) vs Pillar of Severity (1,3,5,8) vs Middle (6,9)
    balance_ratio: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _hebrew_key(letter: str) -> str:
    return HEBREW_TO_KEY.get(letter, LATIN_TO_HEBREW.get(letter, "A"))


def _letter_to_sephirah(letter: str) -> int:
    """Map a Latin or native Hebrew letter to a sephirah index."""
    heb = _hebrew_key(letter)
    val = HEBREW_VALUES.get(heb, 1)
    # Map Hebrew value to sephirah: 1-10, 20->2, 30->3, 40->4, etc.
    if val <= 10:
        return val
    return reduce_single(val)


def kabbalah_signature(text: str) -> KabbalahSignature:
    """Compute Kabbalistic Tree of Life signature for Latin text."""
    normalized = normalize(text)

    sephiroth_positions = []
    seph_freq = {i: 0 for i in range(1, 11)}
    hebrew_letters = []
    hebrew_total = 0
    paths_activated = []
    path_set = set()

    for i, ch in enumerate(normalized):
        seph = _letter_to_sephirah(ch)
        seph_freq[seph] += 1
        heb = _hebrew_key(ch)
        hebrew_display = ch if ch in HEBREW_TO_KEY else heb
        heb_val = HEBREW_VALUES.get(heb, 0)
        hebrew_total += heb_val

        sephiroth_positions.append({
            "char": ch, "sephirah": seph,
            "sephirah_name": SEPHIROTH[seph]["name"],
            "hebrew_letter": hebrew_display, "hebrew_value": heb_val,
            "index": i,
        })

        hebrew_letters.append({
            "latin": ch, "hebrew": hebrew_display,
            "value": heb_val, "sephirah": seph,
        })

        # Activate path
        if heb in PATHS_22:
            p = PATHS_22[heb]
            paths_activated.append({
                "letter": heb, "path": f"{SEPHIROTH[p[0]]['name']}-{SEPHIROTH[p[1]]['name']}",
                "from_seph": p[0], "to_seph": p[1],
                "element": p[2], "tarot": p[3], "meaning": p[4],
            })
            path_set.add(heb)

    total_val = sum(sp["hebrew_value"] for sp in sephiroth_positions)
    reduced_val = reduce_single(total_val)

    dominant_seph = max(seph_freq, key=seph_freq.get) if any(seph_freq.values()) else 1
    active_sephiroth = [s for s, c in seph_freq.items() if c > 0]
    # The Tree's numbering runs from Kether (1, top) to Malkuth (10, bottom).
    highest_seph = min(active_sephiroth) if active_sephiroth else 1
    lowest_seph = max(active_sephiroth) if active_sephiroth else 1

    # Qliphoth
    qliphoth = [QLIPHOTH[s] for s, c in seph_freq.items() if c == 0]

    # Pillar balance
    mercy_pillar = sum(seph_freq.get(s, 0) for s in [2, 4, 7, 10])
    severity_pillar = sum(seph_freq.get(s, 0) for s in [1, 3, 5, 8])
    middle_pillar = sum(seph_freq.get(s, 0) for s in [6, 9])
    balance_ratio = mercy_pillar / severity_pillar if severity_pillar > 0 else None

    return KabbalahSignature(
        original_text=text,
        normalized_text=normalized,
        total_value=total_val,
        reduced_value=reduced_val,
        sephiroth_positions=sephiroth_positions,
        sephiroth_frequencies=seph_freq,
        dominant_sephirah=dominant_seph,
        dominant_sephirah_name=SEPHIROTH[dominant_seph]["name"],
        paths_activated=paths_activated,
        path_count=len(paths_activated),
        unique_paths=len(path_set),
        highest_sephirah=highest_seph,
        lowest_sephirah=lowest_seph,
        tree_span=lowest_seph - highest_seph,
        tree_depth=len(active_sephiroth),
        qliphoth_activated=qliphoth,
        hebrew_letters=hebrew_letters,
        hebrew_total=hebrew_total,
        pillar_balance={"mercy": mercy_pillar, "severity": severity_pillar, "middle": middle_pillar},
        balance_ratio=round(balance_ratio, 4) if balance_ratio is not None else None,
    )


if __name__ == "__main__":
    for name in ["CAPT", "JENN", "INVERSION", "TEST", "TREEOFLIFE"]:
        sig = kabbalah_signature(name)
        print(f"{name:<20} Value={sig.total_value}({sig.reduced_value})  "
              f"Dominant={sig.dominant_sephirah_name}  "
              f"Span={sig.tree_span}  Depth={sig.tree_depth}  "
              f"Paths={sig.unique_paths}")
