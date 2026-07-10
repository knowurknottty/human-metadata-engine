"""
Ordinal Encoders
================

Three ordinal encoding systems:

1. A1Z26 (Standard Ordinal): A=1, B=2, ..., Z=26
2. Reverse Ordinal: A=26, B=25, ..., Z=1
3. Reduced Ordinal: A1Z26 with digital root reduction

These are simpler than Pythagorean/Chaldean but useful as
independent signal vectors for cross-encoder comparison.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import Counter
from typing import Optional
import re


@dataclass(frozen=True)
class LetterValue:
    char: str
    ordinal: int
    reverse: int
    reduced: int
    index: int
    token_index: int


@dataclass(frozen=True)
class OrdinalSignature:
    original_text: str
    normalized_text: str
    tokens: list[str]
    letter_values: list[LetterValue]

    # Standard ordinal (A=1..Z=26)
    ordinal_total: int
    ordinal_reduced: int

    # Reverse ordinal (A=26..Z=1)
    reverse_total: int
    reverse_reduced: int

    # Digital root of ordinal for each letter
    reduced_total: int
    reduced_reduced: int

    vowel_total: int
    consonant_total: int
    intensity_table: dict[int, int]
    hidden_passion: list[int]
    karmic_lessons: list[int]

    def to_dict(self) -> dict:
        return asdict(self)


STRICT_VOWELS = {"A", "E", "I", "O", "U"}


def normalize(text: str) -> tuple[str, list[str]]:
    try:
        from .pipeline import prepare_encoding_input
    except ImportError:  # pragma: no cover - direct module execution
        from pipeline import prepare_encoding_input

    latin_text = prepare_encoding_input(text)["latin_transliteration"]
    tokens = [t for t in re.split(r"[\s\-_]+", latin_text) if t]
    normalized = "".join(ch for ch in latin_text if "A" <= ch <= "Z")
    return normalized, tokens


def digital_root(n: int) -> int:
    """Reduce to single digit via digital root (preserves 0)."""
    if n <= 0:
        return 0
    current = n
    while current > 9:
        current = sum(int(d) for d in str(current))
    return current


def ordinal_signature(text: str) -> OrdinalSignature:
    """Compute all three ordinal encodings."""
    normalized, tokens = normalize(text)
    letter_values: list[LetterValue] = []

    global_idx = 0
    for tok_idx, token in enumerate(tokens):
        for ch in token:
            if ch < "A" or ch > "Z":
                continue
            ordinal = ord(ch) - ord("A") + 1
            reverse = 27 - ordinal
            reduced = digital_root(ordinal)
            letter_values.append(LetterValue(
                char=ch, ordinal=ordinal, reverse=reverse,
                reduced=reduced, index=global_idx, token_index=tok_idx,
            ))
            global_idx += 1

    ordinal_total = sum(lv.ordinal for lv in letter_values)
    reverse_total = sum(lv.reverse for lv in letter_values)
    reduced_total = sum(lv.reduced for lv in letter_values)

    vowel_total = sum(lv.ordinal for lv in letter_values if lv.char in STRICT_VOWELS)
    consonant_total = sum(lv.ordinal for lv in letter_values if lv.char not in STRICT_VOWELS)

    counts = Counter(lv.reduced for lv in letter_values)
    intensity_table = {i: counts.get(i, 0) for i in range(1, 10)}
    max_count = max(intensity_table.values(), default=0)
    hidden_passion = [n for n, c in intensity_table.items() if c == max_count and c > 0]
    karmic_lessons = [n for n, c in intensity_table.items() if c == 0]

    return OrdinalSignature(
        original_text=text,
        normalized_text=normalized,
        tokens=tokens,
        letter_values=letter_values,
        ordinal_total=ordinal_total,
        ordinal_reduced=digital_root(ordinal_total),
        reverse_total=reverse_total,
        reverse_reduced=digital_root(reverse_total),
        reduced_total=reduced_total,
        reduced_reduced=digital_root(reduced_total),
        vowel_total=vowel_total,
        consonant_total=consonant_total,
        intensity_table=intensity_table,
        hidden_passion=hidden_passion,
        karmic_lessons=karmic_lessons,
    )


if __name__ == "__main__":
    names = [
        "John Michael Smith", "Capt", "CAPT", "testuser42", "bioCAPT",
        "Inversion Labs", "Jenn",
    ]
    for name in names:
        sig = ordinal_signature(name)
        print(f"{name:<25} Ord={sig.ordinal_total:>4}({sig.ordinal_reduced})  "
              f"Rev={sig.reverse_total:>4}({sig.reverse_reduced})  "
              f"Red={sig.reduced_total:>3}({sig.reduced_reduced})")
