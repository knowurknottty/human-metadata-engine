"""Accuracy-hardened analytics for the public web product.

The legacy analytics module counts Pythagorean and A1Z26 ordinal roots as
independent votes even though Pythagorean values are ordinal values reduced
modulo nine. This module preserves the existing component contract while
counting one vote per independent mapping family.
"""

from __future__ import annotations

from analytics import (
    RESONANCE_WEIGHTS,
    _clip01,
    _get,
    identity_fingerprint,
    linguistic_harmony,
    polarity_balance,
    symbolic_depth,
)


INDEPENDENT_DIGIT_FAMILIES = {
    "pythagorean_ordinal_family": ("pythagorean", "expression"),
    "chaldean": ("chaldean", "name_number"),
    "gematria": ("gematria", "absolute_reduced"),
    "isopsephy": ("isopsephy", "reduced"),
}

DEPENDENT_OUTPUTS = {
    "ordinal.ordinal_reduced": "Mathematically coupled to the Pythagorean whole-name digital root.",
}


def _fold_digit(value: int) -> int:
    digit = value
    while digit > 9:
        digit = sum(int(char) for char in str(digit))
    return digit


def numerological_convergence(sig: dict) -> float:
    """Concentration across independent mapping families only."""
    digits: list[int] = []
    for encoder, field in INDEPENDENT_DIGIT_FAMILIES.values():
        value = _get(sig, encoder, field)
        if isinstance(value, int) and value > 0:
            digits.append(_fold_digit(value))
    if len(digits) < 2:
        return 0.0
    counts: dict[int, int] = {}
    for digit in digits:
        counts[digit] = counts.get(digit, 0) + 1
    maximum = max(counts.values())
    return _clip01((maximum - 1) / (len(digits) - 1))


def composite_resonance(sig: dict) -> dict:
    """Return the legacy-shaped score with corrected convergence semantics."""
    components = {
        "numerological_convergence": round(numerological_convergence(sig), 4),
        "linguistic_harmony": round(linguistic_harmony(sig), 4),
        "polarity_balance": round(polarity_balance(sig), 4),
        "symbolic_depth": round(symbolic_depth(sig), 4),
    }
    score = sum(RESONANCE_WEIGHTS[key] * value for key, value in components.items())
    return {
        "score": round(100.0 * score, 1),
        "components": components,
        "weights": dict(RESONANCE_WEIGHTS),
        "score_type": "interpretive_index",
        "method_version": "resonance-v2-independent-families",
        "independent_families": list(INDEPENDENT_DIGIT_FAMILIES),
        "dependent_outputs_excluded": dict(DEPENDENT_OUTPUTS),
        "disclaimer": "This is a deterministic symbolic index, not an accuracy, probability, or psychological validity score.",
    }


__all__ = [
    "INDEPENDENT_DIGIT_FAMILIES",
    "DEPENDENT_OUTPUTS",
    "numerological_convergence",
    "composite_resonance",
    "identity_fingerprint",
]
