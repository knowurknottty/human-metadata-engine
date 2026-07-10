"""
Binary & Prime Encoders
=======================

Specialized encodings for cross-encoder analysis:

1. Binary Letter Class: V=0, C=1 (vowel/consonant binary string)
2. Prime-Index Encoding: Map each letter to its index in the prime sequence
3. Vowel/Consonant Polarity: Net vowel-consonant balance

These are useful as independent signal vectors for
comparing identity strings across different representations.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import re


# First 26 primes (A=2, B=3, C=5, ..., Z=101)
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
          47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]

PRIME_MAP = {chr(i + ord("A")): PRIMES[i] for i in range(26)}

STRICT_VOWELS = {"A", "E", "I", "O", "U"}


@dataclass(frozen=True)
class BinaryPrimeSignature:
    original_text: str
    normalized_text: str

    # Binary letter class (V=0, C=1)
    binary_string: str
    binary_as_int: int
    binary_weight: int  # number of 1s (consonants)
    binary_entropy: float  # balance of 0s and 1s

    # Prime-index encoding
    prime_values: list[int]
    prime_total: int
    prime_product: int  # might be huge, stored as string
    prime_reduced: int

    # Vowel/consonant polarity
    vowel_power: float
    consonant_power: float
    polarity_score: float  # positive = vowel-dominant
    polarity_ratio: float

    def to_dict(self) -> dict:
        d = asdict(self)
        d["prime_product"] = self.prime_product  # already string
        return d


def normalize(text: str) -> str:
    try:
        from .pipeline import prepare_encoding_input
    except ImportError:  # pragma: no cover - direct module execution
        from pipeline import prepare_encoding_input
    return "".join(
        ch for ch in prepare_encoding_input(text)["latin_transliteration"]
        if "A" <= ch <= "Z"
    )


def digital_root(n: int) -> int:
    if n <= 0:
        return 0
    current = n
    while current > 9:
        current = sum(int(d) for d in str(current))
    return current


def binary_prime_signature(text: str) -> BinaryPrimeSignature:
    """Compute binary and prime encodings."""
    normalized = normalize(text)

    # Binary letter class
    binary_chars = []
    for ch in normalized:
        if ch in STRICT_VOWELS:
            binary_chars.append("0")
        else:
            binary_chars.append("1")
    binary_string = "".join(binary_chars)
    binary_as_int = int(binary_string, 2) if binary_string else 0
    binary_weight = binary_string.count("1")

    # Binary entropy (Shannon)
    if binary_string:
        p0 = binary_string.count("0") / len(binary_string)
        p1 = binary_string.count("1") / len(binary_string)
        binary_entropy = 0.0
        if p0 > 0:
            binary_entropy -= p0 * __import__("math").log2(p0)
        if p1 > 0:
            binary_entropy -= p1 * __import__("math").log2(p1)
    else:
        binary_entropy = 0.0

    # Prime-index encoding
    prime_values = [PRIME_MAP[ch] for ch in normalized if ch in PRIME_MAP]
    prime_total = sum(prime_values)
    prime_product = 1
    for v in prime_values:
        prime_product *= v
    # For display, use logarithmic reduction
    prime_reduced = digital_root(prime_total)

    # Vowel/consonant polarity
    vowel_power = sum(PRIME_MAP[ch] for ch in normalized if ch in STRICT_VOWELS and ch in PRIME_MAP)
    consonant_power = sum(PRIME_MAP[ch] for ch in normalized if ch not in STRICT_VOWELS and ch in PRIME_MAP)
    total_power = vowel_power + consonant_power
    polarity_score = vowel_power - consonant_power
    polarity_ratio = vowel_power / consonant_power if consonant_power > 0 else float("inf")

    return BinaryPrimeSignature(
        original_text=text,
        normalized_text=normalized,
        binary_string=binary_string,
        binary_as_int=binary_as_int,
        binary_weight=binary_weight,
        binary_entropy=round(binary_entropy, 4),
        prime_values=prime_values,
        prime_total=prime_total,
        prime_product=str(prime_product) if len(str(prime_product)) < 50 else f"{prime_product:.4e}",
        prime_reduced=prime_reduced,
        vowel_power=vowel_power,
        consonant_power=consonant_power,
        polarity_score=polarity_score,
        polarity_ratio=round(polarity_ratio, 4) if polarity_ratio != float("inf") else 999.0,
    )


if __name__ == "__main__":
    names = [
        "John Michael Smith", "Capt", "CAPT", "testuser42", "bioCAPT",
        "Inversion Labs", "Jenn", "FrankenCAPT",
    ]
    for name in names:
        sig = binary_prime_signature(name)
        print(f"{name:<25} Binary={sig.binary_string[:15]:<15}  "
              f"Prime={sig.prime_total:>5}({sig.prime_reduced})  "
              f"Pol={sig.polarity_score:>+4}")
