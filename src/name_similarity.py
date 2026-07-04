"""
Name Similarity Scorer
=======================

Computes linguistic distance between names using:
- Levenshtein edit distance
- Phonetic similarity (Soundex-like)
- Character frequency overlap
- N-gram Jaccard similarity

Usage:
    from src.name_similarity import name_distance
    d = name_distance("Captain", "CAPT")
"""

import hashlib
from collections import Counter


def name_distance(a: str, b: str) -> dict:
    """Compute multi-dimensional name similarity."""
    a_lower = a.lower().strip()
    b_lower = b.lower().strip()

    if a_lower == b_lower:
        return {"distance": 0.0, "similarity": 1.0, "components": {"edit": 1.0, "phonetic": 1.0, "frequency": 1.0, "ngram": 1.0}}

    edit = _edit_similarity(a_lower, b_lower)
    phonetic = _phonetic_similarity(a_lower, b_lower)
    frequency = _frequency_similarity(a_lower, b_lower)
    ngram = _ngram_similarity(a_lower, b_lower, n=2)

    # Weighted combination
    similarity = 0.3 * edit + 0.25 * phonetic + 0.2 * frequency + 0.25 * ngram
    distance = 1.0 - similarity

    return {
        "distance": round(distance, 4),
        "similarity": round(similarity, 4),
        "components": {
            "edit": round(edit, 4),
            "phonetic": round(phonetic, 4),
            "frequency": round(frequency, 4),
            "ngram": round(ngram, 4),
        },
    }


def _edit_similarity(a: str, b: str) -> float:
    """Levenshtein-based similarity (0-1)."""
    la, lb = len(a), len(b)
    if la == 0 and lb == 0:
        return 1.0
    if la == 0 or lb == 0:
        return 0.0

    # DP matrix
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        dp[i][0] = i
    for j in range(lb + 1):
        dp[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)

    max_len = max(la, lb)
    return 1.0 - dp[la][lb] / max_len


def _phonetic_similarity(a: str, b: str) -> float:
    """Soundex-like phonetic coding similarity."""
    sa = _soundex(a)
    sb = _soundex(b)
    if sa == sb:
        return 1.0
    # Compare first 4 characters
    matches = sum(1 for i in range(min(4, len(sa), len(sb))) if sa[i] == sb[i])
    return matches / 4.0


def _soundex(name: str) -> str:
    """Simplified Soundex encoding."""
    if not name:
        return ""
    result = name[0].upper()
    prev = _soundex_code(name[0])
    for c in name[1:]:
        code = _soundex_code(c)
        if code and code != prev:
            result += code
            prev = code
        elif code == 0:
            prev = code
    return (result + "0000")[:4]


def _soundex_code(c: str) -> str:
    mapping = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6',
    }
    return mapping.get(c.lower(), '0')


def _frequency_similarity(a: str, b: str) -> float:
    """Character frequency overlap (Jaccard on character sets)."""
    ca = set(a)
    cb = set(b)
    if not ca and not cb:
        return 1.0
    intersection = ca & cb
    union = ca | cb
    return len(intersection) / len(union)


def _ngram_similarity(a: str, b: str, n: int = 2) -> float:
    """N-gram Jaccard similarity."""
    if len(a) < n and len(b) < n:
        return 1.0 if a == b else 0.0
    ng_a = set()
    ng_b = set()
    for i in range(len(a) - n + 1):
        ng_a.add(a[i:i+n])
    for i in range(len(b) - n + 1):
        ng_b.add(b[i:i+n])
    if not ng_a and not ng_b:
        return 1.0
    intersection = ng_a & ng_b
    union = ng_a | ng_b
    return len(intersection) / len(union) if union else 0.0


def find_closest_names(target: str, names: list, top_n: int = 5) -> list:
    """Find the most similar names to a target."""
    scored = []
    for name in names:
        if name.lower() == target.lower():
            continue
        result = name_distance(target, name)
        scored.append((name, result["similarity"], result))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"name": n, "similarity": s, "details": d} for n, s, d in scored[:top_n]]
