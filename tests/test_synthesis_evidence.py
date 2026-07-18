"""Normalized evidence contract and provenance tests."""

from narrative_helpers import exact_result, resolve_path
from server import analyze


def test_evidence_paths_values_ids_provenance_and_atlas_targets_resolve():
    result = exact_result()
    packet = result["synthesis"]["evidence"]
    assert packet["schema_version"] == "synthesis-evidence-v1"
    assert packet["analysis_id"] == result["input_hash"]
    ids = [item["evidence_id"] for item in packet["evidence_items"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))
    for item in packet["evidence_items"]:
        assert resolve_path(result, item["source_path"]) == item["source_value"]
        assert item["provenance_ref"]
        assert item["atlas_targets"]
        assert item["epistemic_class"]


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
