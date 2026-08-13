"""
Tests for the CAPT Completion & Coherence Gate.

Verifies all 10 countermeasures against autonomous-agent failure modes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coherence_gate import (
    CoherenceGate, ProofClass, ClaimType, TypedClaim,
    Role, MemoryTier,
)

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label} -- {detail}")


def make_production_ready_gate():
    """Helper: gate with all 6 production-ready proof classes + arch + cold-start."""
    gate = CoherenceGate(project="test")
    for pc in [ProofClass.UNIT, ProofClass.BEHAVIORAL, ProofClass.DEPLOYMENT,
               ProofClass.DURABILITY, ProofClass.SECURITY, ProofClass.ADVERSARIAL]:
        gate.evidence.add(pc, detail=f"{pc.value} verified")
    gate.architecture.canonical_source_changed = True
    gate.architecture.generated_artifacts_rebuilt = True
    gate.architecture.deployment_path_exercised = True
    gate.architecture.downstream_contracts_checked = True
    gate.architecture.rollback_proven = True
    gate.cold_start.fresh_checkout = True
    gate.cold_start.declared_secrets = True
    gate.cold_start.declared_dependencies = True
    gate.cold_start.deterministic_setup = True
    gate.cold_start.clean_build = True
    gate.cold_start.clean_deploy = True
    gate.cold_start.same_tests = True
    return gate


if __name__ == "__main__":
    from coherence_gate import PROOF_REQUIREMENTS, LEVEL_ORDER

    print("=== Proof Class Requirements ===")
    check("observed requires 1 class", len(PROOF_REQUIREMENTS["observed"]) == 1)
    check("verified requires 2 classes", len(PROOF_REQUIREMENTS["verified"]) == 2)
    check("durable requires 4 classes", len(PROOF_REQUIREMENTS["durable"]) == 4)
    check("production_ready requires 6 classes", len(PROOF_REQUIREMENTS["production_ready"]) == 6)
    check("proven requires all 10 classes", len(PROOF_REQUIREMENTS["proven"]) == 10)
    check("levels are ordered", LEVEL_ORDER.index("observed") < LEVEL_ORDER.index("proven"))

    print("\n=== Gate: No Evidence ===")
    gate = CoherenceGate(project="test")
    v = gate.evaluate("done")
    check("no evidence blocks", not v.allows)
    check("blocked_by non-empty", len(v.blocked_by) > 0)
    check("actual_level is none", v.actual_level == "none")
    check("allowed claim says not yet observed", "not yet observed" in v.allowed_claim)

    print("\n=== Gate: Minimal Evidence (observed) ===")
    gate = CoherenceGate(project="test")
    gate.evidence.add(ProofClass.BEHAVIORAL, detail="smoke test passed")
    v = gate.evaluate("done")
    check("behavioral only accepted", v.allows)
    check("actual_level is observed", v.actual_level == "observed")
    check("blocked_by is empty", len(v.blocked_by) == 0)

    print("\n=== Gate: Verified Level ===")
    gate = CoherenceGate(project="test")
    gate.evidence.add(ProofClass.UNIT, detail="206 tests pass")
    gate.evidence.add(ProofClass.BEHAVIORAL, detail="POST /api/analyze 200")
    v = gate.evaluate("verified")
    check("unit + behavioral accepted", v.allows)
    check("actual_level is verified", v.actual_level == "verified")

    print("\n=== Gate: Durable Level ===")
    gate = make_production_ready_gate()
    # Remove SECURITY and ADVERSARIAL to leave just 4 for durable
    gate.evidence.entries = [e for e in gate.evidence.entries
                             if e.proof_class not in (ProofClass.SECURITY, ProofClass.ADVERSARIAL)]
    v = gate.evaluate("durable")
    check("4 classes + arch + cold-start accepted", v.allows)
    check("actual_level is durable", v.actual_level == "durable")

    print("\n=== Gate: Production-Ready (incomplete) ===")
    gate = CoherenceGate(project="test")
    gate.evidence.add(ProofClass.UNIT, detail="tests pass")
    gate.evidence.add(ProofClass.BEHAVIORAL, detail="smoke test")
    gate.evidence.add(ProofClass.DEPLOYMENT, detail="deployed")
    gate.evidence.add(ProofClass.DURABILITY, detail="persists")
    v = gate.evaluate("production-ready")
    check("missing SECURITY+ADVERSARIAL blocks", not v.allows)
    check("actual_level is durable", v.actual_level == "durable")
    missing_text = " ".join(v.blocked_by)
    check("mentions missing security", "security" in missing_text.lower())
    check("mentions missing adversarial", "adversarial" in missing_text.lower())

    print("\n=== Gate: Production-Ready (complete) ===")
    gate = make_production_ready_gate()
    gate.omission.missing_threat_model = False
    gate.omission.missing_privacy_model = False
    gate.omission.missing_deletion_path = False
    gate.omission.missing_retention_policy = False
    gate.omission.missing_abuse_analysis = False
    gate.omission.missing_observability = False
    gate.omission.missing_provenance_tamper_policy = False
    gate.omission.missing_confidence_calibration = False
    v = gate.evaluate("production-ready")
    check("6 classes + arch + cold-start + omissions accepted", v.allows)
    check("actual_level is production_ready", v.actual_level == "production_ready")

    print("\n=== Architecture Impact ===")
    gate = make_production_ready_gate()
    # Clear omission audit for production-ready claim
    gate.omission.missing_threat_model = False
    gate.omission.missing_privacy_model = False
    gate.omission.missing_deletion_path = False
    gate.omission.missing_retention_policy = False
    gate.omission.missing_abuse_analysis = False
    gate.omission.missing_observability = False
    gate.omission.missing_provenance_tamper_policy = False
    gate.omission.missing_confidence_calibration = False
    v = gate.evaluate("production-ready")
    check("all gates filled accepted", v.allows)

    # Architecture alone (without cold-start) blocks at durable+
    gate2 = CoherenceGate(project="test")
    for pc in [ProofClass.UNIT, ProofClass.BEHAVIORAL, ProofClass.DEPLOYMENT,
               ProofClass.DURABILITY, ProofClass.SECURITY, ProofClass.ADVERSARIAL]:
        gate2.evidence.add(pc, detail="ok")
    gate2.architecture.canonical_source_changed = False
    v2 = gate2.evaluate("production-ready")
    check("missing arch gate blocks", not v2.allows)
    check("mentions canonical source", any("canonical" in b for b in v2.blocked_by))

    # Architecture does NOT block at verified level
    gate3 = CoherenceGate(project="test")
    gate3.evidence.add(ProofClass.UNIT, detail="tests")
    gate3.evidence.add(ProofClass.BEHAVIORAL, detail="smoke")
    v3 = gate3.evaluate("verified")
    check("arch gaps do not block at verified", v3.allows)

    print("\n=== Cold-Start Gate ===")
    gate = CoherenceGate(project="test")
    for pc in [ProofClass.UNIT, ProofClass.BEHAVIORAL, ProofClass.DEPLOYMENT,
               ProofClass.DURABILITY, ProofClass.SECURITY, ProofClass.ADVERSARIAL]:
        gate.evidence.add(pc, detail="ok")
    gate.architecture.canonical_source_changed = True
    gate.architecture.generated_artifacts_rebuilt = True
    gate.architecture.deployment_path_exercised = True
    gate.architecture.downstream_contracts_checked = True
    gate.architecture.rollback_proven = True
    v = gate.evaluate("production-ready")
    check("no cold-start blocks", not v.allows)
    check("mentions cold-start", any("cold-start" in b for b in v.blocked_by))

    gate.cold_start.fresh_checkout = True
    gate.cold_start.declared_secrets = True
    gate.cold_start.declared_dependencies = True
    gate.cold_start.deterministic_setup = True
    gate.cold_start.clean_build = True
    gate.cold_start.clean_deploy = True
    gate.cold_start.same_tests = True
    v2 = gate.evaluate("production-ready")
    check("cold-start complete but omission blocks", not v2.allows)
    check("blocked by omission audit",
          any("omission" in b for b in v2.blocked_by))

    print("\n=== Blocking Assumptions ===")
    gate = make_production_ready_gate()
    gate.assumptions.log("runtime is Python 3.9", risk="blocking")
    v = gate.evaluate("production-ready")
    check("blocking assumption blocks", not v.allows)
    check("mentions assumption", any("assumption" in b for b in v.blocked_by))

    print("\n=== Role Separation ===")
    gate = CoherenceGate(project="test")
    gate.roles.record(Role.BUILDER, "agent-1", verdict="pass")
    check("builder only same_agent_all_roles", gate.roles.same_agent_all_roles())

    gate2 = CoherenceGate(project="test")
    gate2.roles.record(Role.BUILDER, "agent-1", verdict="pass")
    gate2.roles.record(Role.VERIFIER, "agent-2", verdict="pass")
    gate2.roles.record(Role.ADVERSARIAL_REVIEWER, "agent-3", verdict="pass")
    gate2.roles.record(Role.RELEASE_GATE, "agent-4", verdict="pass")
    check("4 different agents not same", not gate2.roles.same_agent_all_roles())
    check("all roles covered", gate2.roles.all_roles_covered())

    print("\n=== Complexity Budget ===")
    gate = CoherenceGate(project="test")
    check("fresh budget not over", not gate.complexity.over_budget())
    gate.complexity.added_surface = 5
    gate.complexity.new_failure_modes = ["a", "b", "c"]
    gate.complexity.maintenance_items = ["x", "y", "z", "w", "v"]
    check("exhausted budget over", gate.complexity.over_budget())
    budget = gate.complexity.budget_remaining()
    check("surface area zero", budget["surface_area"] == 0)
    check("failure modes zero", budget["failure_modes"] == 0)
    check("maintenance zero", budget["maintenance"] == 0)

    print("\n=== Debt Ledger ===")
    gate = CoherenceGate(project="test")
    gate.debt.log("added fallback path", severity="medium", category="complexity")
    gate.debt.log("duplicate validation", severity="low", category="duplication")
    gate.debt.removed("old monolith.py")
    gate.debt.consolidated("two CORS rules into one")
    gate.debt.as_test("diacritics handling")
    check("duplication count is 1", gate.debt.duplication_count() == 1)
    check("removed paths tracked", len(gate.debt.paths_removed) == 1)
    check("consolidated rules tracked", len(gate.debt.rules_consolidated) == 1)
    check("tests-as-rules tracked", len(gate.debt.tests_as_rules) == 1)

    print("\n=== Omission Audit ===")
    gate = CoherenceGate(project="test")
    gaps = gate.omission.gaps()
    check("8 default omissions", len(gaps) == 8)
    check("mentions threat model", any("threat" in g for g in gaps))
    check("mentions privacy", any("privacy" in g for g in gaps))
    check("mentions deletion", any("deletion" in g for g in gaps))
    gate.omission.missing_threat_model = False
    gate.omission.missing_privacy_model = False
    gaps2 = gate.omission.gaps()
    check("resolved omissions removed", len(gaps2) == 6)

    print("\n=== Typed Claims ===")
    tc = TypedClaim(
        value="Brown derives from a color-based byname",
        claim_type=ClaimType.HISTORICAL_LINGUISTIC,
        evidence_class="tertiary_reference",
        confidence=0.72,
        scope="surname etymology only",
        prohibited_inferences=["psychological", "genetic", "ancestral"],
    )
    check("confidence is 0.72", tc.confidence == 0.72)
    check("scope limits to surname", "surname" in tc.scope)
    check("cross_boundary psychological True",
          tc.cross_boundary(ClaimType.PSYCHOLOGICAL))
    check("cross_boundary mathematical False",
          not tc.cross_boundary(ClaimType.MATHEMATICAL))

    print("\n=== Memory Tiers ===")
    check("OBSERVATION < PROVISIONAL",
          list(MemoryTier).index(MemoryTier.OBSERVATION) < list(MemoryTier).index(MemoryTier.PROVISIONAL))
    check("PROVISIONAL < VALIDATED",
          list(MemoryTier).index(MemoryTier.PROVISIONAL) < list(MemoryTier).index(MemoryTier.VALIDATED))

    print("\n=== Full Report ===")
    gate = CoherenceGate(project="hme")
    gate.evidence.add(ProofClass.UNIT, detail="206 tests")
    gate.evidence.add(ProofClass.BEHAVIORAL, detail="smoke")
    report = gate.full_report()
    check("report has evidence key", "evidence" in report)
    check("report has architecture key", "architecture" in report)
    check("report has assumptions key", "assumptions" in report)
    check("report has debt key", "debt" in report)
    check("report has cold_start key", "cold_start" in report)
    check("report has omission_audit key", "omission_audit" in report)
    check("report has complexity_budget key", "complexity_budget" in report)
    check("report has roles key", "roles" in report)
    check("report has typed_claims key", "typed_claims" in report)
    check("project name in report", report["project"] == "hme")

    print(f"\n{'='*50}")
    print(f"RESULTS: {PASS} passed, {FAIL} failed")
    if FAIL == 0:
        print("ALL COHERENCE GATE TESTS PASSED")
    else:
        print(f"WARNING: {FAIL} test(s) failed")

    sys.exit(1 if FAIL else 0)
