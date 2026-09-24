"""Pattern Map integrity and human-facing explanation tests."""

from narrative_helpers import exact_result
from server import analyze


def test_pattern_map_explains_alignment_without_counting_confirmations():
    result = exact_result()
    pattern = result["synthesis"]["pattern_map"]
    assert pattern["schema_version"] == "pattern-map-v1"
    assert pattern["invariants"]["adds_evidence"] is False
    assert pattern["invariants"]["adds_motif_votes"] is False
    assert pattern["invariants"]["empirical_validation"] == "not_established"
    assert pattern["agreement_explanations"]
    for item in pattern["agreement_explanations"]:
        assert item["evidence_ids"]
        assert item["system_count"] >= 1
        assert item["independence_family_count"] >= 1
        assert item["empirical_status"] == "not_established"
        assert "confirmation" not in item["relation"]
        if item["independence_family_count"] == 1:
            assert item["relation"] == "related"
            assert "shared_dependence_family" in item["reason_codes"]


def test_pattern_map_preserves_divergence_without_winner():
    pattern = exact_result()["synthesis"]["pattern_map"]
    for item in pattern["disagreement_explanations"]:
        assert item["resolution"] == "preserved"
        assert item["winner"] is None
        assert len(item["positions"]) == 2
        assert item["evidence_ids"]


def test_statement_provenance_uses_same_support_across_presentations():
    pattern = exact_result()["synthesis"]["pattern_map"]
    assert pattern["statement_provenance"]
    for item in pattern["statement_provenance"]:
        assert set(item["presentations"]) == {"plain", "mythic", "research"}
        assert item["epistemic_layer"] == "project_authored"
        assert item["support_provenance"]["evidence_ids"] == item["evidence_ids"]
        assert all(
            presentation["text_provenance"]["kind"] == "deterministic_composition"
            for presentation in item["presentations"].values()
        )


def test_complete_exact_birth_needs_no_input_sensitivity_warning():
    pattern = exact_result()["synthesis"]["pattern_map"]
    assert pattern["input_sensitivity"] == []


def test_name_only_sensitivity_names_dependencies_without_inventing_values():
    result = analyze({"name": "Ada Lovelace", "mode": "magic"})
    sensitivity = result["synthesis"]["pattern_map"]["input_sensitivity"]
    paths = {item["input"]["path"] for item in sensitivity}
    assert {"birth.date", "birth.time", "birth.location"} <= paths
    for item in sensitivity:
        assert item["raw_alternative_included"] is False
        assert item["effects"][0]["status"] == "dependency_only"
        assert "could affect" in item["wording"]
        assert item["empirical_status"] == "not_established"


def test_pattern_map_does_not_change_evidence_or_claim_counts():
    synthesis = exact_result()["synthesis"]
    evidence_count = len(synthesis["evidence"]["evidence_items"])
    claim_count = sum(
        len(section["claims"])
        for section in synthesis["plan"]["narrative_sections"]
        if section["section_id"] != "evidence_ledger"
    )
    provenance = synthesis["pattern_map"]["statement_provenance"]
    assert len(synthesis["evidence"]["evidence_items"]) == evidence_count
    assert len(provenance) == claim_count
