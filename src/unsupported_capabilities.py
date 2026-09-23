"""Negative-fact ledger for explicitly unimplemented calculator capabilities.

This registry is the machine-readable form of the no-fabrication doctrine: it
records what the engine deliberately does **not** do, so disclosure stays an
executable gate instead of review-time prose.

Design rules (enforced by ``tests/test_no_fabrication.py``):

* For every ``system -> capability -> fragment`` entry the fragment must still
  appear in that system's published ``limitations``. The encoder limitations
  remain the published wording; the registry only pins the claim, so it cannot
  become a second drifting source of truth.
* No entry may describe an unimplemented capability as a configurable mode.
* Nothing here may be read as evidence of true-solar correction, 23:00
  rollover, Gene Keys support, birth-time precision, or a numeric
  truth-confidence scalar.
"""
from __future__ import annotations

UNSUPPORTED_CAPABILITY_FRAGMENTS: dict[str, dict[str, str]] = {
    "bazi": {
        "true_solar_time_correction": "true/apparent solar-time correction is not applied",
        "late_zi_2300_rollover": "alternate late-Zi rollover schools are not blended",
        "day_master_strength_score": "not a Day-Master strength score",
    },
    "jyotish": {
        "vimshottari_dasha_in_static_signature": (
            "belongs in a separate timing artifact and is not emitted by this static signature"
        ),
        "noon_substitution_for_unknown_birth_time": "does not substitute a noon chart",
        "classical_graha_set": "they are not classical Jyotish grahas",
    },
    "maya_classical": {
        "negative_long_count_dates": "currently emits non-negative Long Count dates only",
        "dreamspell_modern_system": "Modern Dreamspell systems are intentionally separate",
        "alternative_correlation_constants": "alternative published correlations shift the mapped Gregorian date",
    },
}

# Systems/capabilities with no backend anywhere in the engine, encoder registry,
# or evidence extractors.
SYSTEMS_WITHOUT_BACKEND: tuple[str, ...] = ("gene_keys",)

# Epistemic keys permanently removed from the produced surface (CD-07 / CD-08:
# descriptive counts replaced the numeric truth-confidence scalar).
REMOVED_EPISTEMIC_KEYS: tuple[str, ...] = ("confidence_bound", "evidence_density")

# Markers that must never appear as a produced result key or as a function name
# in a result-producing module. Disclosure *text* may name an absent capability;
# keys and symbols may not.
PROHIBITED_SUPPORT_MARKERS: tuple[str, ...] = (
    "true_solar", "true-solar", "23:00", "gene_keys",
)

# Result keys whose names imply a truth-confidence scalar rather than a count.
PROHIBITED_SCALAR_KEY_TOKENS: tuple[str, ...] = (
    "confidence_bound", "truth_score", "truth_confidence",
)

__all__ = [
    "UNSUPPORTED_CAPABILITY_FRAGMENTS",
    "SYSTEMS_WITHOUT_BACKEND",
    "REMOVED_EPISTEMIC_KEYS",
    "PROHIBITED_SUPPORT_MARKERS",
    "PROHIBITED_SCALAR_KEY_TOKENS",
]
