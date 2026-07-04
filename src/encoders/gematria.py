"""
Hebrew Gematria Encoder
=======================

Maps Latin letters to their Hebrew Gematria equivalents.
Uses the standard English-to-Hebrew transliteration mapping.

Two systems:
1. Standard Gematria (Mispar Hechrachi / Absolute Value)
2. Ordinal Gematria (Mispar Siduri)

The English-to-Hebrew mapping follows common transliteration:
A=1(Aleph), B=2(Bet), G=3(Gimel), D=4(Dalet), H=5(He),
V/W=6(Vav), Z=7(Zayin), Ch=8(Chet), T=9(Tet), Y=10(Yod),
K=20(Kaf), L=30(Lamed), M=40(Mem), N=50(Nun), S=60(Samekh),
O=60(Ayin), P/Ph=80(Pe), Tz=90(Tsade), Q=100(Qof), R=200(Resh),
Sh=300(Shin), Th/S=400(Tav)

For Latin text, we use a simplified mapping that assigns Hebrew
numerical values to their closest Latin equivalents.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import Counter
import re


# Standard Gematria mapping (Latin letter → Hebrew absolute value)
GEMATRIA_MAP: dict[str, int] = {
    "A": 1,    # Aleph
    "B": 2,    # Bet
    "G": 3,    # Gimel
    "D": 4,    # Dalet
    "H": 5,    # He
    "V": 6,    # Vav
    "W": 6,    # Vav (alternate)
    "Z": 7,    # Zayin
    "J": 8,    # Chet (closest)
    "T": 9,    # Tet
    "Y": 10,   # Yod
    "K": 20,   # Kaf
    "L": 30,   # Lamed
    "M": 40,   # Mem
    "N": 50,   # Nun
    "S": 60,   # Samekh
    "O": 60,   # Ayin
    "P": 80,   # Pe
    "F": 80,   # Pe (alternate)
    "X": 90,   # Tsade (closest)
    "Q": 100,  # Qof
    "R": 200,  # Resh
    "C": 300,  # Shin (soft C / closest)
    "U": 300,  # Shin (alternate)
    "E": 300,  # Shin (alternate)
    "I": 10,   # Yod (alternate)
}

# Ordinal Gematria (A=1, B=2, ..., Z=26) - same as standard ordinal
ORDINAL_GEMATRIA = {chr(i + ord("A")): i + 1 for i in range(26)}

# Jewish Reduced (reduce each letter to single digit before summing)
def jewish_reduced_value(letter: str) -> int:
    """Reduce gematria value to single digit."""
    val = GEMATRIA_MAP.get(letter.upper(), 0)
    while val > 9:
        val = sum(int(d) for d in str(val))
    return val


@dataclass(frozen=True)
class GematriaSignature:
    original_text: str
    normalized_text: str

    # Standard Gematria
    absolute_total: int
    absolute_reduced: int

    # Ordinal Gematria
    ordinal_total: int
    ordinal_reduced: int

    # Jewish Reduced
    reduced_total: int
    reduced_reduced: int

    # Letter-by-letter breakdown
    letter_values: list[dict]

    # Intensity
    intensity_table: dict[int, int]
    hidden_passion: list[int]
    karmic_lessons: list[int]

    # Comparison metrics
    gematria_ordinal_ratio: float

    def to_dict(self) -> dict:
        return asdict(self)


def normalize(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalpha())


def reduce_single(n: int) -> int:
    current = n
    while current > 9:
        current = sum(int(d) for d in str(current))
    return current


def gematria_signature(text: str) -> GematriaSignature:
    """Compute Hebrew Gematria signature for Latin text."""
    normalized = normalize(text)

    letter_values = []
    abs_total = 0
    ord_total = 0
    red_total = 0

    for i, ch in enumerate(normalized):
        abs_val = GEMATRIA_MAP.get(ch, 0)
        ord_val = ORDINAL_GEMATRIA.get(ch, 0)
        red_val = jewish_reduced_value(ch)

        letter_values.append({
            "char": ch,
            "absolute": abs_val,
            "ordinal": ord_val,
            "reduced": red_val,
            "index": i,
        })

        abs_total += abs_val
        ord_total += ord_val
        red_total += red_val

    abs_reduced = reduce_single(abs_total)
    ord_reduced = reduce_single(ord_total)
    red_reduced = reduce_single(red_total)

    # Intensity of absolute values
    counts = Counter(lv["absolute"] for lv in letter_values if lv["absolute"] > 0)
    intensity_table = {i: counts.get(i, 0) for i in range(1, 10)}
    max_count = max(intensity_table.values(), default=0)
    hidden_passion = [n for n, c in intensity_table.items() if c == max_count and c > 0]
    karmic_lessons = [n for n, c in intensity_table.items() if c == 0]

    ratio = abs_total / ord_total if ord_total > 0 else 0

    return GematriaSignature(
        original_text=text,
        normalized_text=normalized,
        absolute_total=abs_total,
        absolute_reduced=abs_reduced,
        ordinal_total=ord_total,
        ordinal_reduced=ord_reduced,
        reduced_total=red_total,
        reduced_reduced=red_reduced,
        letter_values=letter_values,
        intensity_table=intensity_table,
        hidden_passion=hidden_passion,
        karmic_lessons=karmic_lessons,
        gematria_ordinal_ratio=round(ratio, 4),
    )


if __name__ == "__main__":
    names = ["CAPT", "Knowurknot", "Kirk Evan Brown", "Jenn", "Inversion Labs"]
    for name in names:
        sig = gematria_signature(name)
        print(f"{name:<25} Absolute={sig.absolute_total:>4}({sig.absolute_reduced})  "
              f"Ordinal={sig.ordinal_total:>4}({sig.ordinal_reduced})  "
              f"Reduced={sig.reduced_total:>4}({sig.reduced_reduced})")
