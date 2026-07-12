"""
Tests for the CAPT Claim Compiler.

Verifies the semantic inflation gate: agents cannot claim "done",
"verified", or "production-ready" without machine-readable evidence.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from claim_compiler import (
    compile_claim, classify_claim, scan_text, format_assessment,
    to_json, ClaimLevel, ClaimAssessment, EvidenceItem,
    EVIDENCE_REQUIREMENTS, EVIDENCE_DESCRIPTIONS,
)

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        print(f"  ✗ FAIL: {label} — {detail}")


if __name__ == "__main__":
    print("=== Claim Keyword Classification ===")

    check("done → OBSERVED", classify_claim("done") == ClaimLevel.OBSERVED)
    check("finished → OBSERVED", classify_claim("finished") == ClaimLevel.OBSERVED)
    check("complete → OBSERVED", classify_claim("complete") == ClaimLevel.OBSERVED)
    check("deployed → OBSERVED", classify_claim("deployed") == ClaimLevel.OBSERVED)
    check("working → OBSERVED", classify_claim("working") == ClaimLevel.OBSERVED)
    check("fixed → OBSERVED", classify_claim("fixed") == ClaimLevel.OBSERVED)
    check("passing → OBSERVED", classify_claim("passing") == ClaimLevel.OBSERVED)

    check("verified → VERIFIED", classify_claim("verified") == ClaimLevel.VERIFIED)
    check("hardened → VERIFIED", classify_claim("hardened") == ClaimLevel.VERIFIED)
    check("secured → VERIFIED", classify_claim("secured") == ClaimLevel.VERIFIED)

    check("durable → DURABLE", classify_claim("durable") == ClaimLevel.DURABLE)
    check("persisted → DURABLE", classify_claim("persisted") == ClaimLevel.DURABLE)

    check("production-ready → PRODUCTION_READY", classify_claim("production-ready") == ClaimLevel.PRODUCTION_READY)
    check("production ready → PRODUCTION_READY", classify_claim("production ready") == ClaimLevel.PRODUCTION_READY)
    check("shipped → PRODUCTION_READY", classify_claim("shipped") == ClaimLevel.PRODUCTION_READY)

    check("proven → PROVEN", classify_claim("proven") == ClaimLevel.PROVEN)

    check("non-claim text → None", classify_claim("the code uses Python 3.9") is None)


    print("\n=== Claim Compilation: Rejected (no evidence) ===")

    r = compile_claim("done", provided_types=[])
    check("done with no evidence → rejected", r.status == "rejected")
    check("allowed claim downgrades to not-yet-observed", "not yet observed" in r.allowed_claim)
    check("missing smoke_test_pass", "smoke_test_pass" in r.missing_evidence)

    r = compile_claim("production-ready", provided_types=["smoke_test_pass"])
    check("production-ready with only smoke → rejected", r.status == "rejected")
    check("actual_level is OBSERVED", r.actual_level == ClaimLevel.OBSERVED)
    check("allowed claim is 'observed (smoke-tested once)'", "observed" in r.allowed_claim)
    missing = r.missing_evidence
    check("missing source_control_commit", "source_control_commit" in missing)
    check("missing security_audit", "security_audit" in missing)
    check("missing rollback_tested", "rollback_tested" in missing)
    check("missing independent_reproduction (not required for PRODUCTION_READY)",
          "independent_reproduction" not in missing)


    print("\n=== Claim Compilation: Accepted (evidence sufficient) ===")

    r = compile_claim("done", provided_types=["smoke_test_pass"])
    check("done + smoke → accepted", r.status == "accepted")
    check("allowed claim = 'done'", r.allowed_claim == "done")

    r = compile_claim("verified", provided_types=[
        "smoke_test_pass", "repeatable_test_pass", "acceptance_criteria_defined",
    ])
    check("verified + 3 items → accepted", r.status == "accepted")

    durable_evidence = [
        "repeatable_test_pass", "source_control_commit", "rebuild_passes", "redeploy_persists",
    ]
    r = compile_claim("durable", provided_types=durable_evidence)
    check("durable + 4 items → accepted", r.status == "accepted")

    prod_evidence = durable_evidence + [
        "security_audit", "rollback_tested", "regression_suite", "schema_compatible",
    ]
    r = compile_claim("production-ready", provided_types=prod_evidence)
    check("production-ready + 8 items → accepted", r.status == "accepted")


    print("\n=== Claim Compilation: Downgrade (partial evidence) ===")

    r = compile_claim("production-ready", provided_types=[
        "smoke_test_pass", "repeatable_test_pass", "acceptance_criteria_defined",
    ])
    check("production-ready with VERIFIED-tier evidence → rejected", r.status == "rejected")
    check("actual_level is VERIFIED", r.actual_level == ClaimLevel.VERIFIED)
    check("allowed claim mentions 'verified'", "verified" in r.allowed_claim)


    print("\n=== Non-claim text passes through ===")

    r = compile_claim("The encoder processes 34 input fields", provided_types=[])
    check("descriptive text → accepted", r.status == "accepted")
    check("no evidence check on non-claims", r.missing_evidence == [])


    print("\n=== Text scanning ===")

    claims = scan_text("I'm done. The tests verified the fix and it's production-ready now.")
    check("found 'done'", "done" in claims)
    check("found 'verified'", "verified" in claims)
    check("found 'production-ready'", "production-ready" in claims)

    claims = scan_text("No claims here, just code changes.")
    check("no claims in neutral text", len(claims) == 0)


    print("\n=== Evidence Requirement Coverage ===")

    for level in ClaimLevel:
        reqs = EVIDENCE_REQUIREMENTS[level]
        check(f"{level.value} has {len(reqs)} requirements", len(reqs) > 0)
        for r_type in reqs:
            check(f"  {r_type} has description", r_type in EVIDENCE_DESCRIPTIONS)


    print("\n=== JSON serialization ===")

    r = compile_claim("production-ready", provided_types=["smoke_test_pass", "repeatable_test_pass"])
    j = to_json(r)
    check("JSON has claim field", j["claim"] == "production-ready")
    check("JSON has status field", j["status"] == "rejected")
    check("JSON has missing_evidence list", isinstance(j["missing_evidence"], list))
    check("JSON has provided_evidence list", isinstance(j["provided_evidence"], list))
    check("JSON provided_evidence has type+detail", j["provided_evidence"][0]["type"] == "smoke_test_pass")


    print("\n=== Format assessment ===")

    r = compile_claim("done", provided_types=[])
    formatted = format_assessment(r)
    check("format contains claim text", "done" in formatted)
    check("format contains REJECTED", "REJECTED" in formatted)
    check("format contains missing evidence", "smoke_test_pass" in formatted)


    print(f"\n{'='*50}")
    print(f"RESULTS: {PASS} passed, {FAIL} failed")
    if FAIL == 0:
        print("ALL CLAIM COMPILER TESTS PASSED")
    else:
        print(f"WARNING: {FAIL} test(s) failed")

    sys.exit(1 if FAIL else 0)
