"""
Pythagorean Numerology Encoder
==============================

Implements the standard Pythagorean letter-to-number mapping.
Produces reproducible identity signatures for any input string.

Mapping:
1: A J S
2: B K T
3: C L U
4: D M V
5: E N W
6: F O X
7: G P Y
8: H Q Z
9: I R
"""

from __future__ import annotations
from dataclasses import dataclass, asdict, field
from collections import Counter
from typing import Optional, Literal
import re
import math
import json


# =============================================================================
# Constants
# =============================================================================

PYTHAGOREAN_MAP: dict[str, int] = {
    "A": 1, "J": 1, "S": 1,
    "B": 2, "K": 2, "T": 2,
    "C": 3, "L": 3, "U": 3,
    "D": 4, "M": 4, "V": 4,
    "E": 5, "N": 5, "W": 5,
    "F": 6, "O": 6, "X": 6,
    "G": 7, "P": 7, "Y": 7,
    "H": 8, "Q": 8, "Z": 8,
    "I": 9, "R": 9,
}

MASTER_NUMBERS = {11, 22, 33}
STRICT_VOWELS = {"A", "E", "I", "O", "U"}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass(frozen=True)
class LetterValue:
    char: str
    value: int
    index: int
    token_index: int


@dataclass
class PythagoreanSignature:
    original_text: str
    normalized_text: str
    tokens: list[str]
    letter_values: list[LetterValue]
    total: int
    reduced: int
    master_preserved: Optional[int]
    vowels: list[LetterValue]
    consonants: list[LetterValue]
    soul_urge_total: int
    soul_urge: int
    personality_total: int
    personality: int
    balance_number: Optional[int]
    intensity_table: dict[int, int]
    hidden_passion: list[int]
    karmic_lessons: list[int]
    ignored_characters: list[str]
    y_mode_used: str

    def to_dict(self) -> dict:
        data = asdict(self)
        # Convert LetterValue objects to dicts
        data['letter_values'] = [asdict(lv) for lv in self.letter_values]
        data['vowels'] = [asdict(lv) for lv in self.vowels]
        data['consonants'] = [asdict(lv) for lv in self.consonants]
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class BirthDateNumerology:
    date: str
    year: int
    month: int
    day: int
    year_digits: list[int]
    month_digits: list[int]
    day_digits: list[int]
    year_total: int
    month_total: int
    day_total: int
    life_path_raw: int
    life_path_reduced: int
    life_path_master: Optional[int]
    birthday_number: int
    attitude_number: int
    birth_year_number: int

    def to_dict(self) -> dict:
        return asdict(self)


# =============================================================================
# Core Functions
# =============================================================================

def normalize_identity(text: str) -> tuple[str, list[str], list[str]]:
    """Normalize identity text for numerology calculation.
    
    Returns: (normalized_uppercase, tokens, ignored_characters)
    """
    try:
        from .pipeline import prepare_encoding_input
    except ImportError:  # pragma: no cover - direct module execution
        from pipeline import prepare_encoding_input

    prepared = prepare_encoding_input(text)
    latin_text = prepared["latin_transliteration"]
    ignored = [ch for ch in text if not ch.isalpha() and not ch.isspace() and ch not in "-_"]
    # Tokens are produced from the sanitized transliteration stream; discarded
    # digits and punctuation remain auditable in ``ignored``.
    tokens = [t for t in re.split(r"[\s\-_]+", latin_text) if t]
    normalized = "".join(ch for ch in latin_text if "A" <= ch <= "Z")
    return normalized, tokens, ignored


def reduce_number(value: int, preserve_master: bool = True) -> tuple[int, Optional[int]]:
    """Reduce a number to single digit, optionally preserving master numbers.
    
    Returns: (final_reduced, master_number_if_preserved)
    """
    if value <= 0:
        return 0, None
    
    current = value
    while current > 9:
        if preserve_master and current in MASTER_NUMBERS:
            return current, current
        current = sum(int(digit) for digit in str(current))
    
    return current, None


def classify_vowel(char: str, y_mode: Literal["strict", "flexible"] = "strict") -> bool:
    """Classify a character as vowel or consonant."""
    if char in STRICT_VOWELS:
        return True
    if char == "Y" and y_mode == "flexible":
        return True
    return False


def pythagorean_signature(
    text: str,
    *,
    preserve_master: bool = True,
    y_mode: Literal["strict", "flexible"] = "strict",
) -> PythagoreanSignature:
    """Compute the Pythagorean numerology signature for an identity string.
    
    Args:
        text: The identity string to analyze
        preserve_master: If True, preserve master numbers 11, 22, 33
        y_mode: How to treat the letter Y ('strict' or 'flexible')
    
    Returns:
        PythagoreanSignature with all computed values
    """
    normalized, tokens, ignored = normalize_identity(text)
    
    letter_values: list[LetterValue] = []
    vowels: list[LetterValue] = []
    consonants: list[LetterValue] = []
    
    global_index = 0
    for token_index, token in enumerate(tokens):
        for char in token:
            if char not in PYTHAGOREAN_MAP:
                continue
            lv = LetterValue(
                char=char,
                value=PYTHAGOREAN_MAP[char],
                index=global_index,
                token_index=token_index,
            )
            letter_values.append(lv)
            if classify_vowel(char, y_mode=y_mode):
                vowels.append(lv)
            else:
                consonants.append(lv)
            global_index += 1
    
    # Total and reduction
    total = sum(lv.value for lv in letter_values)
    reduced, master = reduce_number(total, preserve_master=preserve_master)
    
    # Soul Urge (vowels only)
    soul_total = sum(lv.value for lv in vowels)
    soul, _ = reduce_number(soul_total, preserve_master=preserve_master)
    
    # Personality (consonants only)
    personality_total = sum(lv.value for lv in consonants)
    personality, _ = reduce_number(personality_total, preserve_master=preserve_master)
    
    # Balance number (initials)
    initials_values = []
    for token in tokens:
        if token and token[0] in PYTHAGOREAN_MAP:
            initials_values.append(PYTHAGOREAN_MAP[token[0]])
    
    if initials_values:
        balance_sum = sum(initials_values)
        balance, _ = reduce_number(balance_sum, preserve_master=False)
    else:
        balance = None
    
    # Intensity table
    counts = Counter(lv.value for lv in letter_values)
    intensity_table = {i: counts.get(i, 0) for i in range(1, 10)}
    
    # Hidden passion (most frequent)
    max_count = max(intensity_table.values(), default=0)
    hidden_passion = [
        number for number, count in intensity_table.items()
        if count == max_count and count > 0
    ]
    
    # Karmic lessons (missing numbers)
    karmic_lessons = [
        number for number, count in intensity_table.items()
        if count == 0
    ]
    
    return PythagoreanSignature(
        original_text=text,
        normalized_text=normalized,
        tokens=tokens,
        letter_values=letter_values,
        total=total,
        reduced=reduced,
        master_preserved=master,
        vowels=vowels,
        consonants=consonants,
        soul_urge_total=soul_total,
        soul_urge=soul,
        personality_total=personality_total,
        personality=personality,
        balance_number=balance,
        intensity_table=intensity_table,
        hidden_passion=hidden_passion,
        karmic_lessons=karmic_lessons,
        ignored_characters=ignored,
        y_mode_used=y_mode,
    )


def life_path_number(
    year: int,
    month: int,
    day: int,
    preserve_master: bool = True,
) -> BirthDateNumerology:
    """Compute life path numerology from birth date.
    
    Args:
        year: Birth year (e.g., 1985)
        month: Birth month (1-12)
        day: Birth day (1-31)
        preserve_master: If True, preserve master numbers
    
    Returns:
        BirthDateNumerology with all computed values
    """
    # Split into individual digits
    year_digits = [int(d) for d in f"{year:04d}"]
    month_digits = [int(d) for d in f"{month:02d}"]
    day_digits = [int(d) for d in f"{day:02d}"]
    
    year_total = sum(year_digits)
    month_total = sum(month_digits)
    day_total = sum(day_digits)
    
    # Life path: sum all digits, then reduce
    all_digits = year_digits + month_digits + day_digits
    life_path_raw = sum(all_digits)
    life_path_reduced, life_path_master = reduce_number(life_path_raw, preserve_master=preserve_master)
    
    # Birthday number
    birthday_number, _ = reduce_number(day_total, preserve_master=False)
    
    # Attitude number (month + day)
    attitude_raw = month_total + day_total
    attitude_number, _ = reduce_number(attitude_raw, preserve_master=False)
    
    # Birth year number
    birth_year_number, _ = reduce_number(year_total, preserve_master=False)
    
    return BirthDateNumerology(
        date=f"{year:04d}-{month:02d}-{day:02d}",
        year=year,
        month=month,
        day=day,
        year_digits=year_digits,
        month_digits=month_digits,
        day_digits=day_digits,
        year_total=year_total,
        month_total=month_total,
        day_total=day_total,
        life_path_raw=life_path_raw,
        life_path_reduced=life_path_reduced,
        life_path_master=life_path_master,
        birthday_number=birthday_number,
        attitude_number=attitude_number,
        birth_year_number=birth_year_number,
    )


# =============================================================================
# Main: Generate signatures for all identities
# =============================================================================

if __name__ == "__main__":
    names = [
        ("John Michael Smith", "birth_name"),
        ("Capt", "nickname"),
        ("CAPT", "project"),
        ("Captain", "persona"),
        ("testuser42", "handle"),
        ("Captain testuser42", "persona"),
        ("bioCAPT", "project"),
        ("FrankenCAPT", "project"),
        ("Jenn-ai", "agent"),
        ("SynSync", "project"),
        ("Inversion Labs", "brand"),
        ("Knowledge Bubbles", "project"),
        ("Soul Fractal Engine", "project"),
        ("Wyrd", "project"),
        ("CAPT-RYS", "project"),
        ("SYNCHEF", "project"),
        ("Jenn", "nickname"),
    ]
    
    print("=" * 80)
    print("PYTHAGOREAN NUMEROLOGY SIGNATURES")
    print("=" * 80)
    
    for name, id_type in names:
        sig = pythagorean_signature(name)
        master_str = f"/{sig.master_preserved}" if sig.master_preserved else ""
        print(f"\n{name} ({id_type}):")
        print(f"  Expression: {sig.total} → {sig.reduced}{master_str}")
        print(f"  Soul Urge: {sig.soul_urge_total} → {sig.soul_urge}")
        print(f"  Personality: {sig.personality_total} → {sig.personality}")
        if sig.balance_number:
            print(f"  Balance: {sig.balance_number}")
        print(f"  Hidden Passion: {sig.hidden_passion}")
        print(f"  Karmic Lessons: {sig.karmic_lessons}")
    
    # Life path for John Michael Smith
    print("\n" + "=" * 80)
    print("BIRTH DATE NUMEROLOGY")
    print("=" * 80)
    
    lp = life_path_number(1985, 6, 15)
    print(f"\nBirth Date: {lp.date}")
    print(f"  Year: {lp.year_total} → {reduce_number(lp.year_total, False)[0]}")
    print(f"  Month: {lp.month_total} → {reduce_number(lp.month_total, False)[0]}")
    print(f"  Day: {lp.day_total} → {reduce_number(lp.day_total, False)[0]}")
    print(f"  Life Path: {lp.life_path_raw} → {lp.life_path_reduced}")
    print(f"  Birthday: {lp.birthday_number}")
    print(f"  Attitude: {lp.attitude_number}")
