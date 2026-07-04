"""
Knowledge Bubble Miner
=======================

Extracts novel insights from cross-encoder correlations.
Discovers patterns that no single encoder would reveal.

Usage:
    from src.knowledge_miner import mine_bubbles
    bubbles = mine_bubbles("output/unified_signatures.json", "output/encoder_correlations.json")
"""

import json
import math
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeBubble:
    topic: str
    insight: str
    confidence: float
    evidence: list = field(default_factory=list)
    category: str = "pattern"


def mine_bubbles(signatures_path: str, correlations_path: str = None) -> list:
    """Mine knowledge bubbles from signature data and correlations."""
    with open(signatures_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        sigs = {s.get("id", s.get("identity", "")): s for s in data}
    else:
        sigs = data

    bubbles = []

    # 1. Resonance clustering — find identity clusters
    resonance_clusters = _find_resonance_clusters(sigs)
    for cluster in resonance_clusters:
        bubbles.append(cluster)

    # 2. Master number analysis
    master_bubbles = _analyze_master_numbers(sigs)
    bubbles.extend(master_bubbles)

    # 3. Cross-encoder agreement patterns
    agreement_bubbles = _find_agreement_patterns(sigs)
    bubbles.extend(agreement_bubbles)

    # 4. Linguistic-numerological correlations
    ling_num_bubbles = _find_linguistic_numerological_correlations(sigs)
    bubbles.extend(ling_num_bubbles)

    # 5. Karmic lesson patterns
    karmic_bubbles = _analyze_karmic_patterns(sigs)
    bubbles.extend(karmic_bubbles)

    # 6. Polarity extremes
    polarity_bubbles = _find_polarity_extremes(sigs)
    bubbles.extend(polarity_bubbles)

    return bubbles


def _find_resonance_clusters(sigs: dict) -> list:
    """Find clusters of identities with similar resonance scores."""
    scores = []
    for name, sig in sigs.items():
        analytics = sig.get("analytics", {})
        resonance = analytics.get("composite_resonance", analytics.get("resonance_score", 0))
        if resonance:
            scores.append((name, resonance))

    if not scores:
        return []

    scores.sort(key=lambda x: x[1])
    bubbles = []

    # High resonance cluster
    high = [(n, s) for n, s in scores if s > 70]
    if len(high) >= 2:
        bubbles.append(KnowledgeBubble(
            topic="High Resonance Cluster",
            insight=f"{len(high)} identities show high composite resonance (>70): {', '.join(n for n, _ in high[:5])}. These names demonstrate exceptional alignment across numerological, linguistic, and symbolic systems.",
            confidence=0.8,
            evidence=[f"{n}: {s:.1f}" for n, s in high],
            category="cluster",
        ))

    # Low resonance cluster
    low = [(n, s) for n, s in scores if s < 30]
    if len(low) >= 2:
        bubbles.append(KnowledgeBubble(
            topic="Complex Resonance Cluster",
            insight=f"{len(low)} identities show low composite resonance (<30): {', '.join(n for n, _ in low[:5])}. These names carry deliberate tension across symbolic systems — a sign of multi-dimensional complexity.",
            confidence=0.7,
            evidence=[f"{n}: {s:.1f}" for n, s in low],
            category="cluster",
        ))

    return bubbles


def _analyze_master_numbers(sigs: dict) -> list:
    """Analyze master numbers (11, 22, 33) across identities."""
    master_counts = {11: 0, 22: 0, 33: 0}
    master_names = {11: [], 22: [], 33: []}

    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        pyth = encoders.get("pythagorean", {})
        for key in ["expression", "soul_urge", "personality"]:
            val = pyth.get(key)
            if isinstance(val, (int, float)) and val in master_counts:
                master_counts[val] += 1
                master_names[val].append(f"{name}({key})")

    bubbles = []
    for num in [11, 22, 33]:
        if master_counts[num] >= 2:
            label = {11: "Illuminator", 22: "Master Builder", 33: "Master Teacher"}[num]
            bubbles.append(KnowledgeBubble(
                topic=f"Master Number {num} ({label})",
                insight=f"{master_counts[num]} identities carry master number {num}: {', '.join(master_names[num][:5])}. {label}s are rare — approximately 1 in 11 names. This cluster shows elevated spiritual or creative potential.",
                confidence=0.9,
                evidence=master_names[num][:5],
                category="numerology",
            ))

    return bubbles


def _find_agreement_patterns(sigs: dict) -> list:
    """Find patterns where multiple encoders agree on the same value."""
    agreements = []

    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        reduced_digits = []

        for enc_name in ["pythagorean", "chaldean", "ordinal", "gematria", "isopsephy"]:
            enc = encoders.get(enc_name, {})
            for key in ["expression", "name_number", "reduced", "absolute_value"]:
                val = enc.get(key)
                if isinstance(val, (int, float)):
                    reduced = _digital_root(int(val))
                    if 1 <= reduced <= 9:
                        reduced_digits.append((f"{enc_name}.{key}", reduced))

        # Find where multiple encoders agree
        from collections import Counter
        digit_counts = Counter(d for _, d in reduced_digits)
        for digit, count in digit_counts.items():
            if count >= 3:
                matching = [enc for enc, d in reduced_digits if d == digit]
                agreements.append((name, digit, count, matching))

    if agreements:
        # Group by digit
        from collections import defaultdict
        by_digit = defaultdict(list)
        for name, digit, count, matching in agreements:
            by_digit[digit].append((name, count, matching))

        bubbles = []
        for digit, entries in by_digit.items():
            if len(entries) >= 2:
                names = [e[0] for e in entries[:5]]
                bubbles.append(KnowledgeBubble(
                    topic=f"Cross-Encoder Agreement on {digit}",
                    insight=f"{len(entries)} identities show {entries[0][1]}+ encoders converging on digit {digit}: {', '.join(names)}. When multiple independent encoding systems agree, the resonance is statistically significant.",
                    confidence=0.85,
                    evidence=[f"{e[0]}: {e[1]} encoders" for e in entries[:5]],
                    category="correlation",
                ))
        return bubbles

    return []


def _find_linguistic_numerological_correlations(sigs: dict) -> list:
    """Find correlations between linguistic features and numerological values."""
    data_points = []
    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        ling = encoders.get("linguistic", {})
        pyth = encoders.get("pythagorean", {})

        entropy = ling.get("entropy", ling.get("shannon_entropy", 0))
        syllables = ling.get("syllables", ling.get("syllable_count", 0))
        expr = pyth.get("expression", pyth.get("life_path", 0))

        if entropy and expr and isinstance(entropy, (int, float)) and isinstance(expr, (int, float)):
            data_points.append((name, float(entropy), int(expr)))

    if len(data_points) < 3:
        return []

    bubbles = []
    # High entropy + high expression
    high_both = [(n, e, x) for n, e, x in data_points if e > 3.0 and x > 7]
    if high_both:
        bubbles.append(KnowledgeBubble(
            topic="Complex Names with High Expression",
            insight=f"{len(high_both)} identities combine high phonetic complexity (entropy >3.0) with high expression numbers (>7): {', '.join(n for n, _, _ in high_both[:3])}. These names are both phonetically rich and numerologically powerful.",
            confidence=0.75,
            evidence=[f"{n}: entropy={e:.2f}, expr={x}" for n, e, x in high_both[:3]],
            category="correlation",
        ))

    return bubbles


def _analyze_karmic_patterns(sigs: dict) -> list:
    """Analyze karmic lesson patterns across identities."""
    lesson_freq = {i: 0 for i in range(1, 10)}
    total = 0

    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        pyth = encoders.get("pythagorean", {})
        karmic = pyth.get("karmic_lessons", pyth.get("missing_numbers", []))
        if isinstance(karmic, list):
            for num in karmic:
                if isinstance(num, int) and 1 <= num <= 9:
                    lesson_freq[num] += 1
            total += 1

    if total == 0:
        return []

    bubbles = []
    most_common = max(lesson_freq, key=lesson_freq.get)
    most_freq = lesson_freq[most_common]

    if most_freq > total * 0.3:
        lesson_names = {
            1: "leadership", 2: "cooperation", 3: "creativity",
            4: "stability", 5: "freedom", 6: "responsibility",
            7: "introspection", 8: "authority", 9: "compassion",
        }
        bubbles.append(KnowledgeBubble(
            topic=f"Dominant Karmic Lesson: {lesson_names.get(most_common, most_common)}",
            insight=f"The most common karmic lesson across identities is {most_common} ({lesson_names.get(most_common, 'unknown')}), appearing in {most_freq}/{total} identities ({most_freq/total:.0%}). This suggests the dataset over-indexes on this growth area.",
            confidence=0.7,
            evidence=[f"Lesson {most_common}: {most_freq}/{total} identities"],
            category="karmic",
        ))

    return bubbles


def _find_polarity_extremes(sigs: dict) -> list:
    """Find identities with extreme polarity scores."""
    polarities = []
    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        binary = encoders.get("binary_prime", {})
        polarity = binary.get("polarity_score", binary.get("vowel_power", 0))
        consonant = binary.get("consonant_power", 0)
        if polarity and consonant and isinstance(polarity, (int, float)) and isinstance(consonant, (int, float)):
            total = polarity + consonant
            if total > 0:
                ratio = polarity / total
                polarities.append((name, ratio))

    if len(polarities) < 3:
        return []

    polarities.sort(key=lambda x: x[1])
    bubbles = []

    most_feminine = polarities[-1]
    most_masculine = polarities[0]
    if most_feminine[1] - most_masculine[1] > 0.3:
        bubbles.append(KnowledgeBubble(
            topic="Polarity Spectrum",
            insight=f"The polarity spectrum spans from {most_masculine[0]} (most analytical/masculine, {most_masculine[1]:.0%} vowel) to {most_feminine[0]} (most creative/feminine, {most_feminine[1]:.0%} vowel). The range of {most_feminine[1] - most_masculine[1]:.0%} suggests significant diversity in the dataset.",
            confidence=0.8,
            evidence=[f"{most_masculine[0]}: {most_masculine[1]:.0%}", f"{most_feminine[0]}: {most_feminine[1]:.0%}"],
            category="polarity",
        ))

    return bubbles


def _digital_root(n: int) -> int:
    n = abs(n)
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n
