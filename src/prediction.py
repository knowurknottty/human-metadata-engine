"""
Ensemble Prediction
====================

Uses all encoder outputs as features for personality/career prediction.
Lightweight ML without external dependencies.

Usage:
    from src.prediction import predict_personality
    result = predict_personality(signature_dict)
"""

import math
import hashlib
import os
from collections import Counter


def predict_personality(sig: dict) -> dict:
    """Predict personality traits from signature using ensemble heuristics.

    Returns a dict with:
    - big_five: estimated OCEAN scores (0-100)
    - mbti_guess: estimated MBTI type
    - career_affinity: ranked career affinities
    - confidence: overall confidence (0-1)
    """
    if os.environ.get("HME_ENABLE_UNSAFE_EXPERIMENTAL_INFERENCE", "").lower() not in {"1", "true", "yes"}:
        return {
            "status": "disabled",
            "reason": "Name-derived personality, career, and MBTI inference is disabled because it is not validated.",
            "method": "disabled-unvalidated-inference",
        }

    encoders = sig.get("encoders", {})
    analytics = sig.get("analytics", {})

    # Extract features
    features = _extract_features(encoders, analytics)

    # Big Five estimation
    big_five = _estimate_big_five(features)

    # MBTI estimation
    mbti = _estimate_mbti(big_five)

    # Career affinity
    careers = _estimate_career_affinity(features, big_five)

    # Confidence
    num_features = len([v for v in features.values() if v != 0])
    confidence = min(1.0, num_features / 20)

    return {
        "big_five": big_five,
        "mbti_guess": mbti,
        "career_affinity": careers,
        "confidence": round(confidence, 2),
        "method": "ensemble_heuristic",
        "feature_count": num_features,
    }


def _extract_features(encoders: dict, analytics: dict) -> dict:
    f = {}
    # Pythagorean
    pyth = encoders.get("pythagorean", {})
    f["expression"] = pyth.get("expression", 0) or 0
    f["soul_urge"] = pyth.get("soul_urge", 0) or 0
    f["personality"] = pyth.get("personality", 0) or 0
    # Linguistic
    ling = encoders.get("linguistic", {})
    f["entropy"] = ling.get("entropy", ling.get("shannon_entropy", 0)) or 0
    f["syllables"] = ling.get("syllables", ling.get("syllable_count", 0)) or 0
    f["vowel_ratio"] = ling.get("vowel_ratio", 0) or 0
    # Binary
    binary = encoders.get("binary_prime", {})
    f["polarity"] = binary.get("polarity_score", 0) or 0
    f["consonant_power"] = binary.get("consonant_power", 0) or 0
    # Resonance
    f["resonance"] = analytics.get("composite_resonance", analytics.get("resonance_score", 0)) or 0
    return f


def _estimate_big_five(f: dict) -> dict:
    expr = f.get("expression", 5)
    soul = f.get("soul_urge", 5)
    pers = f.get("personality", 5)
    entropy = f.get("entropy", 2.5)
    vowel = f.get("vowel_ratio", 0.4)

    openness = _clamp(40 + (entropy - 2.5) * 20 + (expr - 5) * 5)
    conscientiousness = _clamp(50 + (5 - abs(expr - 5)) * 8 - (entropy - 2.5) * 10)
    extraversion = _clamp(45 + (vowel - 0.35) * 80 + (pers - 5) * 5)
    agreeableness = _clamp(50 + (soul - 5) * 8 + (vowel - 0.35) * 40)
    neuroticism = _clamp(50 - (f.get("resonance", 50) - 50) * 0.5 + abs(expr - soul) * 3)

    return {
        "openness": round(openness),
        "conscientiousness": round(conscientiousness),
        "extraversion": round(extraversion),
        "agreeableness": round(agreeableness),
        "neuroticism": round(neuroticism),
    }


def _estimate_mbti(big_five: dict) -> str:
    e = big_five["extraversion"]
    a = big_five["agreeableness"]
    o = big_five["openness"]
    c = big_five["conscientiousness"]

    ie = "E" if e > 50 else "I"
    sn = "N" if o > 55 else "S"
    tf = "F" if a > 50 else "T"
    jp = "J" if c > 50 else "P"

    return f"{ie}{sn}{tf}{jp}"


def _estimate_career_affinity(f: dict, big_five: dict) -> list:
    careers = []
    expr = f.get("expression", 5)
    soul = f.get("soul_urge", 5)
    entropy = f.get("entropy", 2.5)
    resonance = f.get("resonance", 50)

    if expr >= 8 and big_five["extraversion"] > 55:
        careers.append(("Leadership / Executive", 0.8))
    if entropy > 3.0 and big_five["openness"] > 60:
        careers.append(("Creative / Arts", 0.75))
    if soul >= 7 and big_five["agreeableness"] > 55:
        careers.append(("Counseling / Therapy", 0.7))
    if expr <= 4 and big_five["conscientiousness"] > 55:
        careers.append(("Engineering / Technical", 0.7))
    if entropy > 2.5 and entropy < 3.5:
        careers.append(("Communication / Writing", 0.65))
    if resonance > 70:
        careers.append(("Research / Academia", 0.7))
    if big_five["neuroticism"] > 55:
        careers.append(("Analysis / Quality Assurance", 0.6))

    if not careers:
        careers.append(("Generalist / Multi-disciplinary", 0.5))

    careers.sort(key=lambda x: x[1], reverse=True)
    return [{"career": c, "affinity": round(a, 2)} for c, a in careers[:5]]


def _clamp(val, low=0, high=100):
    return max(low, min(high, val))
