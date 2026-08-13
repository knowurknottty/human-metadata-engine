"""
CAPT Completion & Coherence Gate

Prevents the ten major autonomous-agent failure modes by requiring
machine-readable evidence before any completion claim is permitted.

Architecture:
  - Evidence Ontology: 10 proof classes with explicit coverage tracking
  - Four Mandatory Ledgers: evidence, architecture-impact, assumptions, debt
  - Cold-Start Gate: no "done" without reproducibility evidence
  - Epistemic Type System: every claim has a type, evidence class, confidence, scope
  - Memory Promotion Tiers: observation → provisional → validated → deprecated
  - Complexity Budget: marginal value vs added surface area

Usage:
    from coherence_gate import CoherenceGate, ProofClass, Ledger

    gate = CoherenceGate(project="hme")
    gate.evidence.add(ProofClass.UNIT, detail="206/206 tests pass")
    gate.evidence.add(ProofClass.BEHAVIORAL, detail="smoke test: POST /api/analyze → 200")
    gate.architecture.canonical_source_changed = True
    gate.architecture.rebuild_passes = True
    gate.architecture.deployment_exercised = True
    gate.assumptions.log("Python 3.9 runtime assumed", resolved=False)
    gate.debt.log("add CORS headers", severity="medium")

    result = gate.evaluate("production-ready")
    # result.allows = False
    # result.blocked_by = [...]
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════
# PROOF CLASSES — the formal evidence ontology
# ═══════════════════════════════════════════════════════════════════

class ProofClass(Enum):
    """10 proof classes. Every completion claim must specify which exist."""
    SYNTACTIC = "syntactic"              # parses / compiles
    UNIT = "unit"                        # isolated tests pass
    INTEGRATION = "integration"          # multi-component tests pass
    BEHAVIORAL = "behavioral"            # end-to-end / smoke test
    ADVERSARIAL = "adversarial"          # someone tried to break it
    DEPLOYMENT = "deployment"            # artifact built, deployed, persists
    REPRODUCIBILITY = "reproducibility"  # fresh checkout produces same result
    SECURITY = "security"                # threat model, auth, input validation
    DURABILITY = "durability"            # survives rebuild, redeploy, rollback
    INDEPENDENT = "independent"          # another agent or human verified


# Required proof classes per claim level
PROOF_REQUIREMENTS = {
    "observed": {ProofClass.BEHAVIORAL},
    "verified": {ProofClass.UNIT, ProofClass.BEHAVIORAL},
    "durable": {ProofClass.UNIT, ProofClass.BEHAVIORAL, ProofClass.DEPLOYMENT, ProofClass.DURABILITY},
    "production_ready": {ProofClass.UNIT, ProofClass.BEHAVIORAL, ProofClass.DEPLOYMENT,
                         ProofClass.DURABILITY, ProofClass.SECURITY, ProofClass.ADVERSARIAL},
    "proven": {pc for pc in ProofClass},  # all 10
}

LEVEL_ORDER = ["observed", "verified", "durable", "production_ready", "proven"]

def _level_index(level):
    if level == "none":
        return -1
    return LEVEL_ORDER.index(level)


# ═══════════════════════════════════════════════════════════════════
# EPISTEMIC TYPE SYSTEM — typed claims, not narrative blur
# ═══════════════════════════════════════════════════════════════════

class ClaimType(Enum):
    """Typed claims prevent epistemic collapse."""
    HISTORICAL_LINGUISTIC = "historical_linguistic"
    NUMEROLOGICAL = "numerological"
    SYMBOLIC = "symbolic"
    PSYCHOLOGICAL = "psychological"
    GENETIC = "genetic"
    ANCESTRAL = "ancestral"
    MATHEMATICAL = "mathematical"
    COMPUTATIONAL = "computational"
    OPERATIONAL = "operational"
    SECURITY = "security"
    ARCHITECTURAL = "architectural"


@dataclass
class TypedClaim:
    """A claim with explicit epistemic boundaries."""
    value: str
    claim_type: ClaimType
    evidence_class: str           # "primary_source", "secondary", "tertiary", "inference"
    confidence: float             # 0.0–1.0
    scope: str                    # what this applies to
    prohibited_inferences: list[str] = field(default_factory=list)
    disclaimer: str = ""

    def cross_boundary(self, target_type: ClaimType) -> bool:
        """Check if this claim would be misused across epistemic categories."""
        return target_type.value in self.prohibited_inferences


# ═══════════════════════════════════════════════════════════════════
# FOUR MANDATORY LEDGERS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class EvidenceEntry:
    proof_class: ProofClass
    detail: str
    timestamp: str = ""
    artifact_url: str = ""       # link to proof artifact
    reproducible: bool = False    # can someone else reproduce this?


class EvidenceLedger:
    """Tracks which proof classes have been satisfied."""
    def __init__(self):
        self.entries: list[EvidenceEntry] = []

    def add(self, proof_class: ProofClass, detail: str,
            artifact_url: str = "", reproducible: bool = False):
        self.entries.append(EvidenceEntry(
            proof_class=proof_class,
            detail=detail,
            timestamp=datetime.now(timezone.utc).isoformat(),
            artifact_url=artifact_url,
            reproducible=reproducible,
        ))

    def covered_classes(self) -> set[ProofClass]:
        return {e.proof_class for e in self.entries}

    def missing_for(self, level: str) -> list[ProofClass]:
        required = PROOF_REQUIREMENTS.get(level, set())
        return sorted(required - self.covered_classes(), key=lambda pc: pc.value)

    def to_dict(self) -> list[dict]:
        return [
            {"proof_class": e.proof_class.value, "detail": e.detail,
             "timestamp": e.timestamp, "reproducible": e.reproducible}
            for e in self.entries
        ]


@dataclass
class ArchitectureImpactEntry:
    canonical_source_changed: bool = False
    generated_artifacts_rebuilt: bool = False
    deployment_path_exercised: bool = False
    downstream_contracts_checked: bool = False
    rollback_proven: bool = False
    orphan_patches: list[str] = field(default_factory=list)

    def has_orphans(self) -> bool:
        return len(self.orphan_patches) > 0

    def to_dict(self) -> dict:
        return {
            "canonical_source_changed": self.canonical_source_changed,
            "generated_artifacts_rebuilt": self.generated_artifacts_rebuilt,
            "deployment_path_exercised": self.deployment_path_exercised,
            "downstream_contracts_checked": self.downstream_contracts_checked,
            "rollback_proven": self.rollback_proven,
            "orphan_patches": self.orphan_patches,
        }

    def gaps(self) -> list[str]:
        issues = []
        if not self.canonical_source_changed:
            issues.append("canonical source not confirmed changed")
        if not self.generated_artifacts_rebuilt:
            issues.append("generated artifacts not rebuilt")
        if not self.deployment_path_exercised:
            issues.append("deployment path not exercised")
        if not self.downstream_contracts_checked:
            issues.append("downstream contracts not checked")
        if not self.rollback_proven:
            issues.append("rollback not proven")
        if self.orphan_patches:
            issues.append(f"{len(self.orphan_patches)} orphan live patch(es)")
        return issues


@dataclass
class AssumptionEntry:
    text: str
    resolved: bool
    resolved_by: str = ""
    risk: str = "unknown"     # "low", "medium", "high", "blocking"

    def to_dict(self) -> dict:
        return {"text": self.text, "resolved": self.resolved,
                "resolved_by": self.resolved_by, "risk": self.risk}


class AssumptionLedger:
    """Tracks unresolved assumptions that could invalidate claims."""
    def __init__(self):
        self.entries: list[AssumptionEntry] = []

    def log(self, text: str, resolved: bool = False,
            resolved_by: str = "", risk: str = "unknown"):
        self.entries.append(AssumptionEntry(
            text=text, resolved=resolved, resolved_by=resolved_by, risk=risk
        ))

    def unresolved(self) -> list[AssumptionEntry]:
        return [e for e in self.entries if not e.resolved]

    def blocking(self) -> list[AssumptionEntry]:
        return [e for e in self.entries if not e.resolved and e.risk == "blocking"]

    def to_dict(self) -> list[dict]:
        return [e.to_dict() for e in self.entries]


@dataclass
class DebtEntry:
    description: str
    severity: str               # "low", "medium", "high", "critical"
    category: str = "unspecified"  # "complexity", "duplication", "workaround", "missing_test"
    added_by: str = ""
    general_invariant: bool = False  # True = this is a general rule, False = one-off

    def to_dict(self) -> dict:
        return {"description": self.description, "severity": self.severity,
                "category": self.category, "added_by": self.added_by,
                "general_invariant": self.general_invariant}


class DebtLedger:
    """Tracks architectural complexity and debt introduced."""
    def __init__(self):
        self.entries: list[DebtEntry] = []
        self.paths_removed: list[str] = []
        self.rules_consolidated: list[str] = []
        self.tests_as_rules: list[str] = []  # behaviors captured as tests instead of instructions

    def log(self, description: str, severity: str, category: str = "unspecified",
            added_by: str = "", general_invariant: bool = False):
        self.entries.append(DebtEntry(
            description=description, severity=severity, category=category,
            added_by=added_by, general_invariant=general_invariant
        ))

    def removed(self, path: str):
        self.paths_removed.append(path)

    def consolidated(self, rule: str):
        self.rules_consolidated.append(rule)

    def as_test(self, behavior: str):
        self.tests_as_rules.append(behavior)

    def net_complexity(self) -> int:
        """Positive = more complexity added than removed."""
        severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        added = sum(severity_weight.get(e.severity, 1) for e in self.entries)
        removed = len(self.paths_removed) * 2 + len(self.rules_consolidated) * 2
        return added - removed

    def duplication_count(self) -> int:
        return sum(1 for e in self.entries if e.category == "duplication")

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "paths_removed": self.paths_removed,
            "rules_consolidated": self.rules_consolidated,
            "tests_as_rules": self.tests_as_rules,
            "net_complexity": self.net_complexity(),
        }


# ═══════════════════════════════════════════════════════════════════
# COLD-START GATE — reproducibility without ambient state
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ColdStartChecklist:
    """Every verified result must survive loss of ambient state."""
    fresh_checkout: bool = False
    declared_secrets: bool = False
    declared_dependencies: bool = False
    deterministic_setup: bool = False
    clean_build: bool = False
    clean_deploy: bool = False
    same_tests: bool = False

    def complete(self) -> bool:
        return all([
            self.fresh_checkout, self.declared_secrets, self.declared_dependencies,
            self.deterministic_setup, self.clean_build, self.clean_deploy,
            self.same_tests,
        ])

    def gaps(self) -> list[str]:
        issues = []
        if not self.fresh_checkout:
            issues.append("fresh checkout not verified")
        if not self.declared_secrets:
            issues.append("secrets not declared")
        if not self.declared_dependencies:
            issues.append("dependencies not declared")
        if not self.deterministic_setup:
            issues.append("setup not deterministic")
        if not self.clean_build:
            issues.append("clean build not verified")
        if not self.clean_deploy:
            issues.append("clean deploy not verified")
        if not self.same_tests:
            issues.append("same tests not verified on clean env")
        return issues

    def to_dict(self) -> dict:
        return {
            "fresh_checkout": self.fresh_checkout,
            "declared_secrets": self.declared_secrets,
            "declared_dependencies": self.declared_dependencies,
            "deterministic_setup": self.deterministic_setup,
            "clean_build": self.clean_build,
            "clean_deploy": self.clean_deploy,
            "same_tests": self.same_tests,
        }


# ═══════════════════════════════════════════════════════════════════
# MEMORY PROMOTION TIERS
# ═══════════════════════════════════════════════════════════════════

class MemoryTier(Enum):
    OBSERVATION = "observation"           # seen once, not yet validated
    PROVISIONAL = "provisional"           # lesson learned, needs validation
    VALIDATED = "validated"               # confirmed across multiple incidents
    DEPRECATED = "deprecated"             # superseded or known-wrong


@dataclass
class MemoryEntry:
    content: str
    tier: MemoryTier
    source_incidents: list[str] = field(default_factory=list)
    promoted_at: str = ""

    def to_dict(self) -> dict:
        return {"content": self.content, "tier": self.tier.value,
                "source_incidents": self.source_incidents}


# ═══════════════════════════════════════════════════════════════════
# COMPLEXITY BUDGET
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ComplexityBudget:
    """Stopping rule for autonomous improvement."""
    max_added_surface_area: int = 5       # max new public API surface points
    max_new_failure_modes: int = 3        # max new ways this can break
    max_maintenance_burden: int = 5       # max new things to monitor/maintain

    added_surface: int = 0
    new_failure_modes: list[str] = field(default_factory=list)
    maintenance_items: list[str] = field(default_factory=list)

    def budget_remaining(self) -> dict:
        return {
            "surface_area": max(0, self.max_added_surface_area - self.added_surface),
            "failure_modes": max(0, self.max_new_failure_modes - len(self.new_failure_modes)),
            "maintenance": max(0, self.max_maintenance_burden - len(self.maintenance_items)),
        }

    def over_budget(self) -> bool:
        b = self.budget_remaining()
        return b["surface_area"] == 0 or b["failure_modes"] == 0 or b["maintenance"] == 0

    def to_dict(self) -> dict:
        return {
            "budget": self.budget_remaining(),
            "over_budget": self.over_budget(),
            "added_surface": self.added_surface,
            "new_failure_modes": self.new_failure_modes,
            "maintenance_items": self.maintenance_items,
        }


# ═══════════════════════════════════════════════════════════════════
# OMISSION AUDIT — negative-space analysis
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OmissionAudit:
    """What should exist but does not."""
    missing_threat_model: bool = True
    missing_privacy_model: bool = True
    missing_deletion_path: bool = True
    missing_retention_policy: bool = True
    missing_abuse_analysis: bool = True
    missing_observability: bool = True
    missing_provenance_tamper_policy: bool = True
    missing_confidence_calibration: bool = True
    custom_omissions: list[str] = field(default_factory=list)

    def gaps(self) -> list[str]:
        issues = []
        if self.missing_threat_model:
            issues.append("no threat model")
        if self.missing_privacy_model:
            issues.append("no privacy model")
        if self.missing_deletion_path:
            issues.append("no deletion path")
        if self.missing_retention_policy:
            issues.append("no data retention policy")
        if self.missing_abuse_analysis:
            issues.append("no abuse-case analysis")
        if self.missing_observability:
            issues.append("no observability contract")
        if self.missing_provenance_tamper_policy:
            issues.append("no provenance tamper policy")
        if self.missing_confidence_calibration:
            issues.append("no confidence calibration evaluation")
        issues.extend(self.custom_omissions)
        return issues

    def to_dict(self) -> dict:
        return {
            "threat_model": not self.missing_threat_model,
            "privacy_model": not self.missing_privacy_model,
            "deletion_path": not self.missing_deletion_path,
            "retention_policy": not self.missing_retention_policy,
            "abuse_analysis": not self.missing_abuse_analysis,
            "observability": not self.missing_observability,
            "provenance_tamper": not self.missing_provenance_tamper_policy,
            "confidence_calibration": not self.missing_confidence_calibration,
            "custom_omissions": self.custom_omissions,
            "total_gaps": len(self.gaps()),
        }


# ═══════════════════════════════════════════════════════════════════
# ROLE SEPARATION — prevent self-confirmation loops
# ═══════════════════════════════════════════════════════════════════

class Role(Enum):
    BUILDER = "builder"
    VERIFIER = "verifier"
    ADVERSARIAL_REVIEWER = "adversarial_reviewer"
    RELEASE_GATE = "release_gate"


@dataclass
class RoleRecord:
    role: Role
    agent_id: str
    timestamp: str = ""
    verdict: str = ""           # "pass", "fail", "conditional"
    evidence: str = ""
    conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"role": self.role.value, "agent_id": self.agent_id,
                "timestamp": self.timestamp, "verdict": self.verdict,
                "evidence": self.evidence, "conditions": self.conditions}


class RoleLedger:
    """Separation of duties: builder ≠ verifier ≠ reviewer ≠ gate."""
    def __init__(self):
        self.records: list[RoleRecord] = []

    def record(self, role: Role, agent_id: str, verdict: str = "",
               evidence: str = "", conditions: list[str] = None):
        self.records.append(RoleRecord(
            role=role, agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            verdict=verdict, evidence=evidence,
            conditions=conditions or [],
        ))

    def has_role(self, role: Role) -> bool:
        return any(r.role == role for r in self.records)

    def all_roles_covered(self) -> bool:
        return all(self.has_role(r) for r in Role)

    def same_agent_all_roles(self) -> bool:
        """Detect if one agent filled multiple roles (anti-pattern)."""
        agents_by_role = {}
        for r in self.records:
            agents_by_role.setdefault(r.role, set()).add(r.agent_id)
        return len(agents_by_role) > 0 and len(set.union(*agents_by_role.values())) == 1

    def to_dict(self) -> list[dict]:
        return [r.to_dict() for r in self.records]


# ═══════════════════════════════════════════════════════════════════
# THE GATE — evaluates all ledgers and returns verdict
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GateVerdict:
    claim: str
    allows: bool
    actual_level: str
    blocked_by: list[str]
    allowed_claim: str
    evidence_summary: dict
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "allows": self.allows,
            "actual_level": self.actual_level,
            "blocked_by": self.blocked_by,
            "allowed_claim": self.allowed_claim,
            "evidence_summary": self.evidence_summary,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class CoherenceGate:
    """
    The Completion & Coherence Gate.

    Four mandatory ledgers plus cold-start, omission audit, complexity
    budget, role separation, memory tiers, and typed claims.

    Evaluate a completion claim against all of these before permitting it.
    """

    def __init__(self, project: str = ""):
        self.project = project
        self.evidence = EvidenceLedger()
        self.architecture = ArchitectureImpactEntry()
        self.assumptions = AssumptionLedger()
        self.debt = DebtLedger()
        self.cold_start = ColdStartChecklist()
        self.omission = OmissionAudit()
        self.complexity = ComplexityBudget()
        self.roles = RoleLedger()
        self.typed_claims: list[TypedClaim] = []

    def evaluate(self, claim: str) -> GateVerdict:
        """Evaluate a completion claim against all gate criteria."""
        blocked = []
        covered = self.evidence.covered_classes()

        # 1. Determine highest supported proof-class level
        supported_level = "none"
        for level in reversed(LEVEL_ORDER):
            required = PROOF_REQUIREMENTS[level]
            if required.issubset(covered):
                supported_level = level
                break

        # 2. Map claim text to requested level
        requested_level = _classify_claim_level(claim)

        # 3. Evidence check
        if requested_level and _level_index(supported_level) < _level_index(requested_level):
            missing = self.evidence.missing_for(requested_level)
            blocked.append(
                f"evidence: missing {', '.join(pc.value for pc in missing)} "
                f"for '{requested_level}' (have '{supported_level}')"
            )

        # 4. Architecture impact (only at durable+)
        if requested_level and _level_index(requested_level) >= _level_index("durable"):
            arch_gaps = self.architecture.gaps()
            if arch_gaps:
                blocked.extend(f"architecture: {g}" for g in arch_gaps)

        # 5. Cold-start reproducibility (only at durable+)
        if requested_level and _level_index(requested_level) >= _level_index("durable"):
            cold_gaps = self.cold_start.gaps()
            if cold_gaps:
                blocked.extend(f"cold-start: {g}" for g in cold_gaps)

        # 6. Unresolved assumptions
        blocking_assumptions = self.assumptions.blocking()
        if blocking_assumptions:
            blocked.extend(
                f"assumption (blocking): {a.text}" for a in blocking_assumptions
            )

        # 7. Omission audit (only blocks production-ready and above)
        if requested_level and _level_index(requested_level) >= _level_index("production_ready"):
            omission_gaps = self.omission.gaps()
            if omission_gaps:
                blocked.extend(f"omission: {g}" for g in omission_gaps)

        # 8. Complexity budget
        if self.complexity.over_budget():
            budget = self.complexity.budget_remaining()
            blocked.append(
                f"complexity budget exhausted: surface={budget['surface_area']}, "
                f"failures={budget['failure_modes']}, maintenance={budget['maintenance']}"
            )

        # 9. Role separation (warning, not blocking)
        if self.roles.same_agent_all_roles():
            blocked.append("role: same agent filled builder+verifier (self-confirmation loop)")

        # Determine allowed level
        actual = supported_level
        if not blocked:
            actual = supported_level
        elif supported_level != "none":
            actual = supported_level  # downgrade to what evidence supports

        allows = len(blocked) == 0 and requested_level is not None and _level_index(actual) >= _level_index(requested_level)

        level_labels = {
            "observed": "observed (smoke-tested once)",
            "verified": "verified (tests pass, criteria met)",
            "durable": "durable (source-controlled, survives rebuild)",
            "production_ready": "production-ready (security + rollback + monitoring)",
            "proven": "proven (independently reproduced)",
            "none": "not yet observed (no evidence provided)",
        }

        return GateVerdict(
            claim=claim,
            allows=allows,
            actual_level=actual,
            blocked_by=blocked,
            allowed_claim=level_labels.get(actual, actual),
            evidence_summary={
                "covered_classes": sorted(pc.value for pc in covered),
                "total_entries": len(self.evidence.entries),
                "reproducible_count": sum(1 for e in self.evidence.entries if e.reproducible),
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def full_report(self) -> dict:
        """Complete snapshot of all four ledgers + gates."""
        return {
            "project": self.project,
            "evidence": self.evidence.to_dict(),
            "architecture": self.architecture.to_dict(),
            "assumptions": self.assumptions.to_dict(),
            "debt": self.debt.to_dict(),
            "cold_start": self.cold_start.to_dict(),
            "omission_audit": self.omission.to_dict(),
            "complexity_budget": self.complexity.to_dict(),
            "roles": self.roles.to_dict(),
            "typed_claims": [
                {"value": tc.value, "type": tc.claim_type.value,
                 "confidence": tc.confidence, "scope": tc.scope}
                for tc in self.typed_claims
            ],
        }


def _classify_claim_level(text: str) -> Optional[str]:
    text_lower = text.lower().strip()
    if any(w in text_lower for w in ["proven", "reproduced"]):
        return "proven"
    if any(w in text_lower for w in ["production-ready", "production ready", "shipped"]):
        return "production_ready"
    if any(w in text_lower for w in ["durable", "persisted", "survived"]):
        return "durable"
    if any(w in text_lower for w in ["verified", "validated", "confirmed", "hardened", "secured"]):
        return "verified"
    if any(w in text_lower for w in ["done", "finished", "complete", "completed",
                                       "deployed", "live", "working", "fixed",
                                       "passing", "green", "tested", "operational"]):
        return "observed"
    return None
