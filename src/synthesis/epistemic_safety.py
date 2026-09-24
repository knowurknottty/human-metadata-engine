"""Epistemic safety boundaries for Human Manual synthesis output."""
from __future__ import annotations

import re

# Prohibited language patterns that drift into overclaiming or prophecy
PROHIBITED_OVERCLAIM_PATTERNS = [
    r"\byou are destined\b",
    r"\byou were born to\b",
    r"this proves\b",
    r"\byou always\b",
    r"\byou cannot\b",
    r"will definitely\b",
    r"guaranteed\b",
    r"scientifically measured\b",
    r"exact future events\b",
]

# Patterns that indicate healthy epistemic humility (for validation)
HEALTHY_BOUNDARY_PATTERNS = [
    r"is a reflection prompt",
    r"interpretive synthesis",
    r"bounded symbolic hypothesis",
    r"not proof",
    r"may be imagined",
    r"invites",
    r"consider the point at which",
]

# Epistemic tier mapping for strength capping
EPISTEMIC_TIERS = {
    "deterministic_calculation": 1,
    "deterministic_relationship": 2,
    "traditional_symbolic_interpretation": 3,
    "user_supplied": 4,
    "interpretive_synthesis": 5,
}

MAX_INTERPRETIVE_STRENGTH = 5


def contains_overclaiming_language(text: str) -> tuple[bool, list[str]]:
    """Check if text drifts into overclaiming or prophecy language."""
    found_issues = []
    for pattern in PROHIBITED_OVERCLAIM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found_issues.append(f"Overclaim pattern detected: {pattern}")
    return len(found_issues) > 0, found_issues


def contains_healthy_boundaries(text: str) -> tuple[bool, list[str]]:
    """Check if text includes epistemic humility markers."""
    found_markers = []
    for pattern in HEALTHY_BOUNDARY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found_markers.append(f"Healthy boundary marker: {pattern}")
    return len(found_markers) > 0, found_markers


CLAIM_STRENGTH_RANK = {
    "tentative": 1.0,
    "low": 2.0,
    "medium": 3.0,
    "high": 4.0,
    "strong": 5.0,
}


def _safe_strength(value) -> float:
    """Return a validated support-strength rank; never guess or default."""
    import math

    if isinstance(value, bool) or value is None:
        raise ValueError("Claim support strength must be an explicit finite number or exact support label.")
    if isinstance(value, (int, float)):
        numeric = float(value)
        if not math.isfinite(numeric) or not 0.0 <= numeric <= MAX_INTERPRETIVE_STRENGTH:
            raise ValueError("Numeric claim support strength must be finite and between 0 and 5.")
        return numeric
    if isinstance(value, str) and value in CLAIM_STRENGTH_RANK:
        return CLAIM_STRENGTH_RANK[value]
    raise ValueError(f"Unsupported claim support strength: {value!r}")


def validate_epistemic_strength(claims: list[dict], mode: str) -> tuple[bool, list[str]]:
    """Pinned return contract for interpretive strength validation.

    Contract (asserted by ``tests/test_no_fabrication.py``):

    * Returns ``(valid, issues)`` where ``valid`` is ``True`` if and only if
      ``issues`` is empty.
    * ``valid`` is ``True`` for an empty claim list or for every claim whose
      ``strength`` stays at or below its mode threshold.
    * ``valid`` is ``False`` and ``issues`` is non-empty whenever any claim
      exceeds the mode's tier threshold. ``mythic`` permits up to
      ``MAX_INTERPRETIVE_STRENGTH``; ``plain`` and ``research`` permit up to
      ``MAX_INTERPRETIVE_STRENGTH * 0.8``.
    * Unrecognised modes are accepted and impose no threshold, so they never
      raise.
    * ``valid`` is not a truth-confidence scalar; it is a bounded
      policy-compliance flag.
    """
    issues = []
    
    # Mythic mode can be more poetic but still bounded
    if mode == "mythic":
        # Allow stronger language in mythic but check for prophecy drift
        for claim in claims:
            text = claim.get("text", "")
            strength = _safe_strength(claim.get("strength", 1))
            if strength > MAX_INTERPRETIVE_STRENGTH:
                issues.append(
                    f"Mythic mode claim exceeds max interpretive strength "
                    f"(current={strength}, max={MAX_INTERPRETIVE_STRENGTH})"
                )
    
    # Research and plain modes should be more restrained
    if mode in ("research", "plain"):
        for claim in claims:
            text = claim.get("text", "")
            strength = _safe_strength(claim.get("strength", 1))
            threshold = MAX_INTERPRETIVE_STRENGTH * 0.8
            if strength > threshold:
                issues.append(
                    f"{mode.capitalize()} mode claim has unusually high strength "
                    f"(current={strength}, recommended max={threshold})"
                )
    
    return len(issues) == 0, issues


def add_epistemic_metadata_to_section(section: dict, evidence_count: int,
                                      contradiction_count: int = 0) -> dict:
    """Attach descriptive audit metadata without implying truth-confidence."""
    return {
        **section,
        "epistemic_metadata": {
            "evidence_item_count": evidence_count,
            "contradiction_count": contradiction_count,
            "contradiction_preserved": bool(contradiction_count),
            "interpretive_only": True,
            "not_empirical_validation": True,
        },
    }


def sanitize_for_export(text: str) -> str:
    """Remove or flag any language that could be misinterpreted as empirical claim."""
    # Replace overclaiming phrases with softer alternatives
    sanitized = text
    
    replacements = [
        (r"\byou are destined\b", "you may encounter patterns of"),
        (r"this proves\b", "this suggests"),
        (r"is a fact about you", "is an interpretive observation about"),
        (r"scientifically measured", "symbolically associated with"),
    ]
    
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def verify_no_diagnosis_or_prediction(text: str) -> tuple[bool, list[str]]:
    """Ensure text doesn't drift into clinical diagnosis or prediction."""
    issues = []
    
    # Clinical/medical language
    medical_patterns = [
        r"\bdiagnosis\b",
        r"\bdisorder\b",
        r"\btrauma\b",
        r"\baddiction\b",
        r"\bsymptom\b",
        r"\btreatment\b",
    ]
    
    for pattern in medical_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"Potential clinical language detected: {pattern}")
    
    # Prediction/destiny language
    prediction_patterns = [
        r"\bwill definitely\b",
        r"\bguaranteed\b",
        r"\bexactly what will happen\b",
        r"\bdestined to\b",
    ]
    
    for pattern in prediction_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"Potential prediction language detected: {pattern}")
    
    return len(issues) > 0, issues
