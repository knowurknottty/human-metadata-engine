"""
Confidence Scorer
==================

Evaluates how reliable each encoder's output is for a given name.
Based on: name length, character set, encoder coverage, and
cross-encoder agreement.

Usage:
    from src.confidence import score_confidence
    result = score_confidence(signature_dict, "Captain")
"""

import math
from typing import Optional


def score_confidence(sig: dict, name: str = "") -> dict:
    """Score the confidence of each encoder's output."""
    encoders = sig.get("encoders", {})
    resonance = sig.get("resonance", {})
    name_len = len(name.strip()) if name else 0

    encoder_scores = {}

    # Base confidence from name characteristics
    base_confidence = _name_quality_score(name)

    for enc_name, enc_data in encoders.items():
        if not isinstance(enc_data, dict):
            encoder_scores[enc_name] = {"score": 0.5, "reasons": ["empty output"]}
            continue

        reasons = []
        score = base_confidence

        # Length factor: very short names reduce confidence
        if name_len < 3:
            score *= 0.6
            reasons.append("name_too_short")
        elif name_len < 5:
            score *= 0.8
            reasons.append("name_short")

        # Encoder-specific adjustments
        if enc_name in ["gematria", "isopsephy"]:
            # These need Hebrew/Greek alphabet knowledge
            if name.isascii():
                score *= 0.7
                reasons.append("ascii_name_with_non_latin_encoder")

        if enc_name in ["astrology", "human_design"]:
            # These need birth data
            has_birth = bool(sig.get("birth"))
            if not has_birth:
                score *= 0.5
                reasons.append("no_birth_data")

        if enc_name == "linguistic":
            # Linguistic analysis is most reliable for longer names
            if name_len >= 6:
                score *= 1.1
                reasons.append("name_long_enough_for_linguistic")
            bigrams = enc_data.get("bigrams", [])
            if len(bigrams) > 5:
                score *= 1.05
                reasons.append("rich_bigram_data")

        if enc_name == "pythagorean":
            # Pythagorean is reliable for all ASCII names
            if name.isascii() and name_len >= 4:
                score *= 1.1
                reasons.append("reliable_for_ascii")

        # Cross-encoder agreement boost
        if enc_name in ["pythagorean", "chaldean", "ordinal"]:
            # These three should agree on similar values
            pyth = encoders.get("pythagorean", {})
            chal = encoders.get("chaldean", {})
            ord_ = encoders.get("ordinal", {})

            pyth_val = pyth.get("expression", pyth.get("life_path", 0))
            chal_val = chal.get("expression", 0)
            ord_val = ord_.get("name_number", 0)

            if isinstance(pyth_val, (int, float)) and isinstance(chal_val, (int, float)):
                if abs(pyth_val - chal_val) < 5:
                    score *= 1.05
                    reasons.append("pyth_chal_agree")

        score = max(0.1, min(1.0, score))

        encoder_scores[enc_name] = {
            "score": round(score, 3),
            "reasons": reasons,
        }

    # Overall confidence
    scores = [e["score"] for e in encoder_scores.values()]
    overall = sum(scores) / len(scores) if scores else 0

    return {
        "name": name,
        "overall_confidence": round(overall, 3),
        "encoder_scores": encoder_scores,
        "name_quality": _name_quality_score(name),
        "method": "heuristic_scoring",
    }


def _name_quality_score(name: str) -> float:
    """Score name quality for encoding (0-1)."""
    if not name:
        return 0.3

    score = 0.7  # Base

    # Length bonus
    length = len(name)
    if length >= 5:
        score += 0.1
    if length >= 8:
        score += 0.05

    # Mixed case bonus (real names)
    if any(c.isupper() for c in name) and any(c.islower() for c in name):
        score += 0.05

    # No weird characters
    if name.replace(" ", "").replace("-", "").replace("'", "").isalpha():
        score += 0.05

    return min(1.0, score)
