"""
Chaldean Numerology Encoder
===========================

The Chaldean system is older than Pythagorean. Key differences:
- Name numbers are based on vibration, not alphabetical order
- Number 9 is sacred and excluded from name calculations
- Only single-digit reductions (no master numbers at name level)

Mapping:
1: A I J Q Y
2: B K R
3: C G L S
4: D M T
5: E H N X
6: U V W
7: O Z
8: F P

9: (sacred, not assigned to letters)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from collections import Counter
from typing import Optional
import re

# Chaldean letter-to-number mapping
CHALDEAN_MAP: dict[str, int] = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

# Vowels in Chaldean system
CHALDEAN_VOWELS = {"A", "E", "I", "O", "U"}


@dataclass(frozen=True)
class LetterValue:
    """Single letter with its Chaldean value."""
    char: str
    value: int
    index: int
    token_index: int


@dataclass(frozen=True)
class ChaldeanSignature:
    """Complete Chaldean numerology signature for a string."""
    original_text: str
    normalized_text: str
    tokens: list[str]
    letter_values: list[LetterValue]
    total: int
    reduced: int
    compound_number: int  # Unreduced total before single-digit
    vowels: list[LetterValue]
    consonants: list[LetterValue]
    name_number: int  # Chaldean name number
    soul_urge: int
    personality: int
    intensity_table: dict[int, int]
    hidden_passion: list[int]
    karmic_lessons: list[int]
    ignored_characters: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_chaldean(text: str) -> tuple[str, list[str], list[str]]:
    """Normalize text for Chaldean calculation."""
    ignored = [ch for ch in text if not ch.isalpha() and not ch.isspace() and ch not in "-_"]
    tokens = [t for t in re.split(r"[\s\-_]+", text.upper()) if t]
    normalized = "".join(ch for ch in text.upper() if ch.isalpha())
    return normalized, tokens, ignored


def reduce_chaldean(value: int) -> int:
    """Reduce to single digit. Chaldean does NOT preserve master numbers."""
    current = value
    while current > 9:
        current = sum(int(digit) for digit in str(current))
    return current


def chaldean_signature(text: str) -> ChaldeanSignature:
    """Compute Chaldean numerology signature."""
    normalized, tokens, ignored = normalize_chaldean(text)

    letter_values: list[LetterValue] = []
    vowels: list[LetterValue] = []
    consonants: list[LetterValue] = []

    global_index = 0
    for token_index, token in enumerate(tokens):
        for char in token:
            if char not in CHALDEAN_MAP:
                continue
            lv = LetterValue(
                char=char,
                value=CHALDEAN_MAP[char],
                index=global_index,
                token_index=token_index,
            )
            letter_values.append(lv)
            if char in CHALDEAN_VOWELS:
                vowels.append(lv)
            else:
                consonants.append(lv)
            global_index += 1

    total = sum(lv.value for lv in letter_values)
    reduced = reduce_chaldean(total)

    soul_total = sum(lv.value for lv in vowels)
    soul_urge = reduce_chaldean(soul_total) if soul_total > 0 else 0

    personality_total = sum(lv.value for lv in consonants)
    personality = reduce_chaldean(personality_total) if personality_total > 0 else 0

    counts = Counter(lv.value for lv in letter_values)
    intensity_table = {i: counts.get(i, 0) for i in range(1, 10)}
    max_count = max(intensity_table.values(), default=0)
    hidden_passion = [n for n, c in intensity_table.items() if c == max_count and c > 0]
    karmic_lessons = [n for n, c in intensity_table.items() if c == 0]

    return ChaldeanSignature(
        original_text=text,
        normalized_text=normalized,
        tokens=tokens,
        letter_values=letter_values,
        total=total,
        reduced=reduced,
        compound_number=total,
        vowels=vowels,
        consonants=consonants,
        name_number=reduced,
        soul_urge=soul_urge,
        personality=personality,
        intensity_table=intensity_table,
        hidden_passion=hidden_passion,
        karmic_lessons=karmic_lessons,
        ignored_characters=ignored,
    )


if __name__ == "__main__":
    names = [
        "John Michael Smith", "Capt", "CAPT", "Captain", "testuser42",
        "Captain testuser42", "bioCAPT", "FrankenCAPT", "Jenn-ai",
        "SynSync", "Inversion Labs", "Jenn",
    ]
    for name in names:
        sig = chaldean_signature(name)
        print(f"{name:<25} Chaldean={sig.reduced}  Compound={sig.compound_number}  "
              f"Soul={sig.soul_urge}  Person={sig.personality}")
