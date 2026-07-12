"""
CAPT Claim Compiler — intercepts semantic inflation of completion.

Intercepts words like "done", "fixed", "verified", "production-ready",
"complete", "shipped", "deployed" and requires machine-readable evidence
before permitting the claim.

Usage:
    from claim_compiler import compile_claim, ClaimLevel

    result = compile_claim(
        claim="production-ready",
        evidence=[
            {"type": "test_pass", "detail": "206 passed, 1 skipped"},
            {"type": "source_control", "detail": "commit abc123"},
        ]
    )
    # result.status == "rejected"
    # result.allowed_claim == "verified"
    # result.missing_evidence == ["rebuild_passes", "redeploy_persists", ...]
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ClaimLevel(Enum):
    """Evidence tiers for completion claims, ordered by rigor."""
    OBSERVED = "observed"           # Smoke test passed once
    VERIFIED = "verified"           # Repeatable tests + acceptance criteria
    DURABLE = "durable"             # Source-controlled + survives rebuild
    PRODUCTION_READY = "production_ready"  # Security + rollback + monitoring
    PROVEN = "proven"               # Independent reproduction in clean env


# Required evidence types for each claim level
EVIDENCE_REQUIREMENTS: dict[ClaimLevel, list[str]] = {
    ClaimLevel.OBSERVED: [
        "smoke_test_pass",
    ],
    ClaimLevel.VERIFIED: [
        "smoke_test_pass",
        "repeatable_test_pass",
        "acceptance_criteria_defined",
    ],
    ClaimLevel.DURABLE: [
        "repeatable_test_pass",
        "source_control_commit",
        "rebuild_passes",
        "redeploy_persists",
    ],
    ClaimLevel.PRODUCTION_READY: [
        "repeatable_test_pass",
        "source_control_commit",
        "rebuild_passes",
        "redeploy_persists",
        "security_audit",
        "rollback_tested",
        "regression_suite",
        "schema_compatible",
    ],
    ClaimLevel.PROVEN: [
        "repeatable_test_pass",
        "source_control_commit",
        "rebuild_passes",
        "redeploy_persists",
        "security_audit",
        "rollback_tested",
        "regression_suite",
        "schema_compatible",
        "independent_reproduction",
        "clean_environment_pass",
    ],
}

# Evidence type descriptions for human-readable output
EVIDENCE_DESCRIPTIONS = {
    "smoke_test_pass": "At least one end-to-end smoke test passed",
    "repeatable_test_pass": "Test suite passes consistently (not flaky)",
    "acceptance_criteria_defined": "Written acceptance criteria exist and are met",
    "source_control_commit": "Changes committed to source control with meaningful message",
    "rebuild_passes": "Image/package rebuilds from source without errors",
    "redeploy_persists": "Changes survive container/instance recreation",
    "security_audit": "Security review completed (CORS, auth, input validation, secrets)",
    "rollback_tested": "Rollback to previous version verified",
    "regression_suite": "Full regression test suite passes",
    "schema_compatible": "API response schema matches contract, version identifiers present",
    "independent_reproduction": "Another agent or clean environment reproduces the result",
    "clean_environment_pass": "Works from a fresh checkout with no cached state",
}

# Claim keywords that trigger the compiler
_LEVEL_ORDER = {level: i for i, level in enumerate(ClaimLevel)}


def _level_gte(a: ClaimLevel, b: ClaimLevel) -> bool:
    """Compare claim levels by ordinal position, not string value."""
    return _LEVEL_ORDER[a] >= _LEVEL_ORDER[b]


CLAIM_KEYWORDS = re.compile(
    r"\b(done|finished|complete|completed|shipped|deployed|fixed|verified|"
    r"production[- ]?ready|ready|live|working|operational|secured|hardened|"
    r"tested|passing|green|all (?:tests |checks )?pass)\b",
    re.IGNORECASE,
)


@dataclass
class EvidenceItem:
    type: str
    detail: str = ""
    timestamp: str = ""


@dataclass
class ClaimAssessment:
    claim: str
    requested_level: ClaimLevel
    status: str  # "accepted", "rejected", "downgraded"
    actual_level: Optional[ClaimLevel]
    allowed_claim: str
    provided_evidence: list[EvidenceItem]
    missing_evidence: list[str]
    missing_descriptions: dict[str, str]


def classify_claim(text: str) -> Optional[ClaimLevel]:
    """Map a claim keyword to the highest ClaimLevel it implies."""
    text_lower = text.lower().strip()
    if any(w in text_lower for w in ["production-ready", "production ready", "shipped"]):
        return ClaimLevel.PRODUCTION_READY
    if any(w in text_lower for w in ["proven", "reproduced"]):
        return ClaimLevel.PROVEN
    if any(w in text_lower for w in ["durable", "persisted", "survived"]):
        return ClaimLevel.DURABLE
    if any(w in text_lower for w in ["verified", "validated", "confirmed", "hardened", "secured"]):
        return ClaimLevel.VERIFIED
    if any(w in text_lower for w in ["done", "finished", "complete", "completed",
                                       "deployed", "live", "working", "fixed",
                                       "passing", "green", "tested", "operational"]):
        return ClaimLevel.OBSERVED
    return None


def compile_claim(
    claim: str,
    evidence: Optional[List[EvidenceItem]] = None,
    provided_types: Optional[List[str]] = None,
) -> ClaimAssessment:
    """
    Compile a completion claim against available evidence.

    Args:
        claim: The claim text (e.g. "production-ready", "done and verified")
        evidence: List of EvidenceItem objects with type and detail
        provided_types: Simple list of evidence type strings (alternative to evidence)

    Returns:
        ClaimAssessment with status, allowed_claim, missing_evidence
    """
    evidence = evidence or []
    provided_types = provided_types or [e.type for e in evidence]

    # If only provided_types given, create synthetic EvidenceItems for serialization
    if not evidence and provided_types:
        evidence = [EvidenceItem(type=t) for t in provided_types]

    # Determine what level the claim implies
    requested_level = classify_claim(claim)
    if requested_level is None:
        # Not a completion claim — no gate needed
        return ClaimAssessment(
            claim=claim,
            requested_level=ClaimLevel.OBSERVED,
            status="accepted",
            actual_level=None,
            allowed_claim=claim,
            provided_evidence=evidence,
            missing_evidence=[],
            missing_descriptions={},
        )

    # Check each level from requested down to see what's actually supported
    provided_set = set(provided_types)
    supported_level = None

    for level in reversed(list(ClaimLevel)):
        required = set(EVIDENCE_REQUIREMENTS[level])
        if required.issubset(provided_set):
            supported_level = level
            break

    # Build the assessment
    if supported_level is None:
        # No level fully satisfied — find what's closest
        closest = ClaimLevel.OBSERVED
        required_for_closest = EVIDENCE_REQUIREMENTS[ClaimLevel.OBSERVED]
        missing = [e for e in required_for_closest if e not in provided_set]

        return ClaimAssessment(
            claim=claim,
            requested_level=requested_level,
            status="rejected",
            actual_level=None,
            allowed_claim="not yet observed (no evidence provided)",
            provided_evidence=evidence,
            missing_evidence=missing,
            missing_descriptions={k: EVIDENCE_DESCRIPTIONS[k] for k in missing},
        )

    if _level_gte(supported_level, requested_level):
        # Evidence meets or exceeds the claim
        return ClaimAssessment(
            claim=claim,
            requested_level=requested_level,
            status="accepted",
            actual_level=supported_level,
            allowed_claim=claim,
            provided_evidence=evidence,
            missing_evidence=[],
            missing_descriptions={},
        )

    # Evidence is insufficient — downgrade
    # Find what's missing at the requested level
    required_at_claimed = EVIDENCE_REQUIREMENTS[requested_level]
    missing = [e for e in required_at_claimed if e not in provided_set]

    # Build the allowed claim from the highest supported level
    level_names = {
        ClaimLevel.OBSERVED: "observed (smoke-tested once)",
        ClaimLevel.VERIFIED: "verified (tests pass, criteria met)",
        ClaimLevel.DURABLE: "durable (source-controlled, survives rebuild)",
        ClaimLevel.PRODUCTION_READY: "production-ready (security + rollback + monitoring)",
        ClaimLevel.PROVEN: "proven (independently reproduced)",
    }

    return ClaimAssessment(
        claim=claim,
        requested_level=requested_level,
        status="rejected",
        actual_level=supported_level,
        allowed_claim=level_names.get(supported_level, str(supported_level)),
        provided_evidence=evidence,
        missing_evidence=missing,
        missing_descriptions={k: EVIDENCE_DESCRIPTIONS[k] for k in missing},
    )


def scan_text(text: str) -> list[str]:
    """Scan text for claim keywords and return them."""
    return CLAIM_KEYWORDS.findall(text)


def format_assessment(a: ClaimAssessment) -> str:
    """Format an assessment for human-readable output."""
    lines = []
    status_icon = {"accepted": "✓", "rejected": "✗", "downgraded": "↓"}.get(a.status, "?")
    q = '"'
    lines.append(f"Claim: {q}{a.claim}{q}")
    lines.append(f"Status: {status_icon} {a.status.upper()}")
    lines.append(f"Requested level: {a.requested_level.value}")
    if a.actual_level:
        lines.append(f"Supported level: {a.actual_level.value}")
    lines.append(f"Allowed claim: {q}{a.allowed_claim}{q}")

    if a.provided_evidence:
        lines.append(f"\nProvided evidence ({len(a.provided_evidence)}):")
        for e in a.provided_evidence:
            lines.append(f"  ✓ {e.type}: {e.detail}")

    if a.missing_evidence:
        lines.append(f"\nMissing evidence ({len(a.missing_evidence)}):")
        for e in a.missing_evidence:
            desc = a.missing_descriptions.get(e, "")
            lines.append(f"  ✗ {e}: {desc}")

    return "\n".join(lines)


# --- JSON output for tool integration ---

def to_json(a: ClaimAssessment) -> dict:
    """Serialize assessment to machine-readable dict."""
    return {
        "claim": a.claim,
        "status": a.status,
        "requested_level": a.requested_level.value,
        "actual_level": a.actual_level.value if a.actual_level else None,
        "allowed_claim": a.allowed_claim,
        "provided_evidence": [{"type": e.type, "detail": e.detail} for e in a.provided_evidence],
        "provided_types": [e.type for e in a.provided_evidence],
        "missing_evidence": a.missing_evidence,
    }
