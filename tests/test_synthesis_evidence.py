"""Normalized evidence contract and provenance tests."""

from narrative_helpers import exact_result, resolve_path
from server import analyze


def test_evidence_paths_values_ids_provenance_and_atlas_targets_resolve():
    result = exact_result()
    packet = result["synthesis"]["evidence"]
    assert packet["schema_version"] == "synthesis-evidence-v2"
    assert packet["analysis_id"] == result["input_hash"]
    ids = [item["evidence_id"] for item in packet["evidence_items"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))
    for item in packet["evidence_items"]:
        assert resolve_path(result, item["source_path"]) == item["source_value"]
        assert item["provenance_ref"]
        assert item["atlas_targets"]
        assert item["epistemic_class"]
        assert item["packet_schema_version"] == "synthesis-evidence-v2"
        assert item["analysis_id"] == result["input_hash"]
        assert item["record_id"].startswith("sys_v2_")
        assert len(item["record_id"].removeprefix("sys_v2_")) == 64
        assert item["evidence_id"].startswith("ev_v2_")
        assert len(item["evidence_id"].rsplit("_", 1)[-1]) == 64
        assert len(item["source_value_sha256"]) == 64


def test_name_only_fails_closed_for_birth_derived_systems():
    result = analyze({"name": "Ada Lovelace", "mode": "magic"})
    systems = {item["system"] for item in result["synthesis"]["evidence"]["evidence_items"]}
    assert "astrology" not in systems
    assert "human_design" not in systems
    quality = result["synthesis"]["evidence"]["data_quality"]
    assert quality["astronomy"] == "unavailable"
    assert quality["human_design"] == "unavailable"
    assert result["synthesis"]["plan"]["central_archetype"]["partial_profile"] is True


def test_user_context_is_labeled_as_supplied_not_calculated():
    result = analyze({"name": "Context Example", "mode": "magic", "psychology": {"mbti": "INTJ", "conflict_style": "collaborative"}})
    items = [item for item in result["synthesis"]["evidence"]["evidence_items"] if item["system"] == "user_context"]
    assert items
    assert all(item["epistemic_class"] == "user_supplied" for item in items)
    assert all("not calculated" in " ".join(item["limitations"]).lower() for item in items)

def test_resolved_birth_location_quality():
    result = exact_result()
    quality = result["synthesis"]["evidence"]["data_quality"]
    missing = result["synthesis"]["plan"]["missing_or_uncertain_dimensions"]
    assert quality["birth_location"] == "resolved"
    assert "birth_location: missing" not in missing


def test_roadmap_epistemic_taxonomy_separates_state_crosswalk_and_history():
    result = exact_result()
    items = result["synthesis"]["evidence"]["evidence_items"]
    bridge = [item for item in items if item["system"] == "esoteric_bridge"]
    if bridge:
        assert all(item["epistemic_class"] == "project_authored_crosswalk" for item in bridge)
        assert all(item["claim_eligible"] is False for item in bridge)
    sumerian = [item for item in items if item["system"] == "sumerian_me_ontology"]
    for item in sumerian:
        if item["subsystem"] in {"evidence_layer", "identity_input_used", "personal_mapping_policy", "attestation_status"}:
            assert item["epistemic_class"] == "system_state"
            assert item["claim_eligible"] is False
        else:
            assert item["epistemic_class"] == "historical_textual_reference"


def test_evidence_packet_digest_and_ids_are_deterministic():
    first = exact_result()["synthesis"]["evidence"]
    second = exact_result()["synthesis"]["evidence"]
    assert first["packet_digest"] == second["packet_digest"]
    assert [item["evidence_id"] for item in first["evidence_items"]] == [
        item["evidence_id"] for item in second["evidence_items"]
    ]
