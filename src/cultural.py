"""
Cultural Origin Mapper
=======================

Maps names to likely cultural/linguistic origins based on
character patterns, phonetics, and naming conventions.

Usage:
    from src.cultural import map_cultural_origin
    result = map_cultural_origin("Mohammed")
"""

import re
from typing import Optional


# Pattern-based cultural origin detection
PATTERNS = [
    # (pattern, origin, confidence, language)
    (r"^(muhammad|mohammed|mohamed|mo|moj)", "Arabic/Islamic", 0.9, "Arabic"),
    (r"(stein|berg|mann|hoff|feld|baum)", "Germanic", 0.85, "German"),
    (r"(son|sen)$", "Scandinavian", 0.7, "Norse"),
    (r"(ov|ev|in|ova|eva|ina)$", "Slavic", 0.8, "Russian/Slavic"),
    (r"(escu|escu)$", "Romanian", 0.9, "Romanian"),
    (r"(opoulos|idis|akis)$", "Greek", 0.85, "Greek"),
    (r"(elli|ello|elli)$", "Italian", 0.75, "Italian"),
    (r"(ez|es)$", "Spanish/Portuguese", 0.7, "Spanish"),
    (r"(chan|kun|sama|san)$", "Japanese", 0.85, "Japanese"),
    (r"(singh|kaur|gupt|sharma|patel)", "Indian/South Asian", 0.85, "Hindi/Sanskrit"),
    (r"(ka|ki|nen|lahti)", "Finnish", 0.8, "Finnish"),
    (r"(berg|dahl|ström)", "Scandinavian", 0.8, "Swedish"),
    (r"(wang|liu|zhang|chen|yang)", "Chinese", 0.9, "Chinese"),
    (r"(kim|park|lee|choi|jeong)", "Korean", 0.9, "Korean"),
    (r"(nguyen|pham|tran|le)", "Vietnamese", 0.9, "Vietnamese"),
    (r"(johnson|williams|smith|brown|jones)", "English", 0.95, "English"),
]

# Hebrew/Aramaic patterns (for Gematria context)
HEBREW_PATTERNS = [
    (r"(el|iah|yah|shua|iel)", "Hebrew", 0.8, "Hebrew"),
    (r"(david|moshe|avraham|yaakov)", "Hebrew", 0.9, "Hebrew"),
]

# Latin/Roman patterns
LATIN_PATTERNS = [
    (r"(us|um|a|ae)$", "Latin/Roman", 0.6, "Latin"),
    (r"(maximus|optimus|verus)", "Latin", 0.85, "Latin"),
]


def map_cultural_origin(name: str) -> dict:
    """Map a name to likely cultural origins."""
    name_lower = name.lower().strip()

    matches = []

    # Check all pattern sets
    for pattern_set in [PATTERNS, HEBREW_PATTERNS, LATIN_PATTERNS]:
        for pattern, origin, confidence, language in pattern_set:
            if re.search(pattern, name_lower):
                matches.append({
                    "origin": origin,
                    "language": language,
                    "confidence": confidence,
                    "pattern": pattern,
                })

    # Deduplicate by origin, keep highest confidence
    seen = {}
    for m in matches:
        key = m["origin"]
        if key not in seen or m["confidence"] > seen[key]["confidence"]:
            seen[key] = m

    results = sorted(seen.values(), key=lambda x: x["confidence"], reverse=True)

    # If no matches, try phonetic heuristics
    if not results:
        results = _phonetic_heuristic(name_lower)

    return {
        "name": name,
        "origins": results[:5],
        "primary_origin": results[0] if results else None,
        "method": "pattern_matching" if matches else "phonetic_heuristic",
    }


def _phonetic_heuristic(name: str) -> list:
    """Fallback phonetic heuristics."""
    results = []

    # Vowel-heavy names suggest Romance languages
    vowel_count = sum(1 for c in name if c in "aeiou")
    vowel_ratio = vowel_count / len(name) if name else 0

    if vowel_ratio > 0.5:
        results.append({
            "origin": "Romance (likely)",
            "language": "Italian/Spanish/Portuguese (probable)",
            "confidence": 0.4,
            "pattern": "high_vowel_ratio",
        })
    elif vowel_ratio < 0.3:
        results.append({
            "origin": "Germanic/Slavic (likely)",
            "language": "German/Russian (probable)",
            "confidence": 0.35,
            "pattern": "low_vowel_ratio",
        })

    # Hard consonants suggest Germanic
    hard_consonants = sum(1 for c in name if c in "kxzqj")
    if hard_consonants >= 2:
        results.append({
            "origin": "Germanic (likely)",
            "language": "German/Dutch (probable)",
            "confidence": 0.3,
            "pattern": "hard_consonants",
        })

    return results
