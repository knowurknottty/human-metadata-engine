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


def _safe_strength(value):
    """Safely coerce strength to numeric for comparison."""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            # Handle string representations like "1.5", "strong", etc.
            return float(value) if value.strip().replace(".", "").isdigit() else 1.0
        except (ValueError, AttributeError):
            return 1.0
    return 1.0

def validate_epistemic_strength(claims: list[dict], mode: str) -> tuple[bool, list[str]]:
    """Ensure interpretive claims don't exceed their epistemic tier."""
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
    
    return len(issues) > 0, issues


def compute_epistemic_confidence_bound(evidence_count: int, contradiction_count: int = 0) -> float:
    """Compute a confidence bound for interpretive claims based on evidence density."""
    if evidence_count == 0:
        return 0.1  # Very low confidence when no evidence
    
    # Base confidence from evidence count (diminishing returns)
    base_confidence = min(0.9, evidence_count / max(evidence_count + 5, 1))
    
    # Reduce for contradictions
    if contradiction_count > 0:
        reduction = min(0.3, contradiction_count * 0.1)
        base_confidence -= reduction
    
    return max(0.0, min(1.0, base_confidence))


def add_epistemic_metadata_to_section(section: dict, evidence_count: int, 
                                     contradiction_count: int = 0) -> dict:
    """Attach epistemic metadata to a narrative section."""
    confidence_bound = compute_epistemic_confidence_bound(evidence_count, contradiction_count)
    
    return {
        **section,
        "epistemic_metadata": {
            "evidence_density": evidence_count,
            "contradiction_preserved": bool(contradiction_count > 0),
            "confidence_bound": round(confidence_bound, 3),
            "interpretive_only": True,
            "not_empirical_validation": True,
        }
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
