"""
Name Generator
===============

Generate names with desired numerological properties.
Brute-force search through name combinations to find matches.

Usage:
    from src.name_generator import generate_names
    results = generate_names(target_expression=11, target_soul_urge=22)
"""

import itertools
from typing import Optional


# Common name syllables for generation
SYLLABLES = [
    "a", "al", "an", "ar", "ba", "be", "bi", "bo", "ca", "da", "de", "di",
    "el", "en", "er", "fa", "ga", "ha", "ia", "ja", "ka", "la", "ma", "na",
    "ol", "pa", "ra", "sa", "ta", "va", "za", "zen", "ra", "mi", "lu", "ki",
]

CONSONANT_STARTS = [
    "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s",
    "t", "v", "w", "z",
]

VOWELS = list("aeiou")


def generate_names(
    target_expression: int = None,
    target_soul_urge: int = None,
    target_personality: int = None,
    syllable_range: tuple = (2, 3),
    max_results: int = 10,
) -> list:
    """Generate names matching target numerological properties."""
    from encoders.pythagorean import pythagorean_signature

    results = []
    attempts = 0
    max_attempts = 50000

    # Strategy: build 2-3 syllable names from consonant+vowel pairs
    for num_syllables in range(syllable_range[0], syllable_range[1] + 1):
        for combo in itertools.product(CONSONANT_STARTS + VOWELS, repeat=num_syllables * 2):
            attempts += 1
            if attempts > max_attempts:
                break

            name = "".join(combo).capitalize()
            if len(name) < 3 or len(name) > 10:
                continue

            # Must contain at least one vowel
            if not any(c in VOWELS for c in name.lower()):
                continue

            try:
                sig = pythagorean_signature(name)
                expr = sig.total if hasattr(sig, 'total') else 0
                soul = sig.soul_urge if hasattr(sig, 'soul_urge') else 0
                pers = sig.personality if hasattr(sig, 'personality') else 0

                match = True
                if target_expression is not None and _digital_root(expr) != target_expression:
                    match = False
                if target_soul_urge is not None and _digital_root(soul) != target_soul_urge:
                    match = False
                if target_personality is not None and _digital_root(pers) != target_personality:
                    match = False

                if match:
                    results.append({
                        "name": name,
                        "expression": expr,
                        "soul_urge": soul,
                        "personality": pers,
                        "expression_rd": _digital_root(expr),
                        "soul_urge_rd": _digital_root(soul),
                        "personality_rd": _digital_root(pers),
                    })
                    if len(results) >= max_results:
                        break
            except Exception:
                continue

        if len(results) >= max_results:
            break

    return results


def _digital_root(n: int) -> int:
    if not isinstance(n, int):
        return 0
    n = abs(n)
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n
