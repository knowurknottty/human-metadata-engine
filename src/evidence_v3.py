"""Evidence-weighted interpretation controls.

The dashboard distinguishes evidence coverage from symbolic resonance.
Weights encode absolute maximum influence on a personalized claim, not truth
values. Missing evidence is never renormalized into artificial certainty.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

EVIDENCE_WEIGHTS: dict[str, float] = {
    "observed_behavior": 0.35,
    "self_report": 0.35,
    "measurable_name_structure": 0.10,
    "etymology": 0.08,
    "astrology": 0.06,
    "numerology": 0.04,
    "experimental_correspondence": 0.02,
}

EVIDENCE_META: dict[str, dict[str, str]] = {
    "observed_behavior": {
        "class": "observed",
        "label": "Observed behavior",
        "description": "Repeated behavior or documented outcomes.",
    },
    "self_report": {
        "class": "self-reported",
        "label": "Self-report",
        "description": "The subject's own assessment or validated questionnaire response.",
    },
    "measurable_name_structure": {
        "class": "computed",
        "label": "Measurable name structure",
        "description": "Letter counts, phonetics, entropy, and other reproducible string properties.",
    },
    "etymology": {
        "class": "historical-linguistic",
        "label": "Etymology",
        "description": "Documented lexical and surname morphology; not personality evidence.",
    },
    "astrology": {
        "class": "symbolic",
        "label": "Astrology",
        "description": "Correctly calculated symbolic placements used only as reflection prompts.",
    },
    "numerology": {
        "class": "symbolic",
        "label": "Numerology",
        "description": "Deterministic name/date transformations with capped interpretive influence.",
    },
    "experimental_correspondence": {
        "class": "experimental",
        "label": "Experimental correspondences",
        "description": "Unvalidated cross-system mappings; never decisive.",
    },
}

SYMBOLIC_LAYERS = {
    "astrology",
    "numerology",
    "experimental_correspondence",
}


def _fold_digit(value: int) -> int:
    current = int(value)
    while current > 9:
        current = sum(int(char) for char in str(current))
    return current


def independent_numerology_digits(signature: dict[str, Any]) -> list[int]:
    """Extract one digital-root result per mapping family."""
    encoders = signature.get("encoders", {})
    paths = (
        ("pythagorean", "expression"),
        ("chaldean", "name_number"),
        ("gematria", "absolute_reduced"),
        ("isopsephy", "reduced"),
    )
    digits: list[int] = []
    for encoder, field in paths:
        value = encoders.get(encoder, {}).get(field)
        if isinstance(value, int) and value > 0:
            digits.append(_fold_digit(value))
    return digits


def chance_corrected_pair_agreement(digits: list[int]) -> dict[str, float | int]:
    """Correct pair agreement for the 1/9 coincidence expected under a simple null.

    This does not assert that real numerology outputs are independent or uniform;
    it is a conservative baseline that prevents one ordinary duplicate from being
    described as strong convergence.
    """
    values = [int(value) for value in digits if 1 <= int(value) <= 9]
    pair_count = len(values) * (len(values) - 1) // 2
    if pair_count == 0:
        return {
            "systems": len(values),
            "pairs": 0,
            "matching_pairs": 0,
            "raw_pair_agreement": 0.0,
            "null_pair_agreement": 1 / 9,
            "chance_corrected_agreement": 0.0,
        }

    matching_pairs = sum(left == right for left, right in combinations(values, 2))
    raw = matching_pairs / pair_count
    null = 1 / 9
    corrected = max(0.0, min(1.0, (raw - null) / (1.0 - null)))
    return {
        "systems": len(values),
        "pairs": pair_count,
        "matching_pairs": matching_pairs,
        "raw_pair_agreement": round(raw, 4),
        "null_pair_agreement": round(null, 4),
        "chance_corrected_agreement": round(corrected, 4),
    }


def evidence_dashboard(
    signature: dict[str, Any],
    *,
    psychology: dict[str, Any] | None = None,
    observations: list[dict[str, Any]] | None = None,
    etymology: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe evidence coverage and fixed influence limits.

    The dashboard deliberately does not redistribute the weight of missing layers.
    A symbolic layer with six percent maximum influence remains six percent even
    when stronger evidence is absent.
    """
    encoders = signature.get("encoders", {})
    available = {
        "observed_behavior": bool(observations),
        "self_report": bool(psychology),
        "measurable_name_structure": bool(encoders.get("linguistic")),
        "etymology": bool(etymology and etymology.get("components")),
        "astrology": bool(
            encoders.get("astrology")
            and not encoders["astrology"].get("error")
            and encoders["astrology"].get("available", True)
        ),
        "numerology": bool(encoders.get("pythagorean")),
        "experimental_correspondence": any(
            isinstance(value, dict)
            and value.get("status") == "computed"
            and value.get("interpretation_level") == "symbolic"
            and isinstance(value.get("provenance"), dict)
            for value in encoders.values()
        ),
    }

    available_weight = sum(
        EVIDENCE_WEIGHTS[key] for key, present in available.items() if present
    )

    layers = []
    for key in EVIDENCE_WEIGHTS:
        layers.append({
            "id": key,
            **EVIDENCE_META[key],
            "available": available[key],
            "maximum_influence": EVIDENCE_WEIGHTS[key],
            "available_influence": EVIDENCE_WEIGHTS[key] if available[key] else 0.0,
        })

    numerology = chance_corrected_pair_agreement(
        independent_numerology_digits(signature)
    )
    return {
        "method_version": "evidence-v3-absolute-weights",
        "layers": layers,
        "coverage": round(available_weight, 4),
        "normalization": "absolute_weights",
        "numerology_agreement": numerology,
        "rules": [
            "Direct behavioral contradiction outranks symbolic agreement.",
            "Etymology describes word history, not the bearer.",
            "Symbolic and experimental layers cannot exceed 12% combined influence.",
            "Missing high-weight evidence is shown as missing, not imputed or redistributed.",
            "Consensus is a source category, not a truth status.",
            "Primary evidence, translation history, institutional claims, and interpretation remain separate layers.",
        ],
    }


def weighted_claim_support(evidence: dict[str, float | None]) -> dict[str, Any]:
    """Combine claim-specific support values in [-1, 1] using absolute weights.

    Missing layers contribute zero rather than causing present layers to be
    renormalized. This preserves every layer's configured maximum influence.
    A strong observed contradiction also marks attempted symbolic override.
    """
    used: dict[str, float] = {}
    score = 0.0
    coverage = 0.0
    for key, weight in EVIDENCE_WEIGHTS.items():
        value = evidence.get(key)
        if value is None:
            continue
        clipped = max(-1.0, min(1.0, float(value)))
        used[key] = clipped
        score += weight * clipped
        coverage += weight

    veto = None
    observed = used.get("observed_behavior")
    positive_symbolic = any(used.get(key, 0.0) > 0 for key in SYMBOLIC_LAYERS)
    if observed is not None and observed <= -0.5 and positive_symbolic:
        veto = "observed_behavior_contradiction"
        if score > 0:
            score = 0.0

    return {
        "support": round(score, 4),
        "coverage": round(coverage, 4),
        "normalization": "absolute_weights",
        "evidence": used,
        "veto": veto,
    }


__all__ = [
    "EVIDENCE_WEIGHTS",
    "SYMBOLIC_LAYERS",
    "chance_corrected_pair_agreement",
    "evidence_dashboard",
    "independent_numerology_digits",
    "weighted_claim_support",
]
