"""Accuracy-hardened analytics for the public web product.

The legacy analytics module counts Pythagorean and A1Z26 ordinal roots as
independent votes even though Pythagorean values are ordinal values reduced
modulo nine. This module keeps one result per mapping family and corrects
remaining pair agreement for the 1/9 coincidence expected under a simple null.
"""

from __future__ import annotations

from analytics import (
    RESONANCE_WEIGHTS,
    identity_fingerprint,
    linguistic_harmony,
    polarity_balance,
    symbolic_depth,
)
from evidence_v3 import chance_corrected_pair_agreement, independent_numerology_digits


INDEPENDENT_DIGIT_FAMILIES = {
    "pythagorean_ordinal_family": ("pythagorean", "expression"),
    "chaldean": ("chaldean", "name_number"),
    "gematria": ("gematria", "absolute_reduced"),
    "isopsephy": ("isopsephy", "reduced"),
}

DEPENDENT_OUTPUTS = {
    "ordinal.ordinal_reduced": "Mathematically coupled to the Pythagorean whole-name digital root.",
}


def numerological_convergence(sig: dict) -> float:
    """Return pair agreement above a simple one-in-nine coincidence baseline."""
    detail = chance_corrected_pair_agreement(independent_numerology_digits(sig))
    return float(detail["chance_corrected_agreement"])


def composite_resonance(sig: dict) -> dict:
    """Return the legacy-shaped symbolic index with chance-corrected agreement."""
    agreement_detail = chance_corrected_pair_agreement(
        independent_numerology_digits(sig)
    )
    components = {
        "numerological_convergence": round(
            float(agreement_detail["chance_corrected_agreement"]), 4
        ),
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
        "method_version": "resonance-v3-chance-corrected",
        "independent_families": list(INDEPENDENT_DIGIT_FAMILIES),
        "dependent_outputs_excluded": dict(DEPENDENT_OUTPUTS),
        "numerology_agreement_detail": agreement_detail,
        "disclaimer": "This is a deterministic symbolic index, not an accuracy, probability, or psychological validity score.",
    }


__all__ = [
    "INDEPENDENT_DIGIT_FAMILIES",
    "DEPENDENT_OUTPUTS",
    "numerological_convergence",
    "composite_resonance",
    "identity_fingerprint",
]
