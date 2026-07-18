"""Motif independence, agreement, contradiction, and claim-plan tests."""

from copy import deepcopy

from narrative_helpers import exact_result
from synthesis.analysis import detect_agreements, detect_contradictions, rank_motifs


def _item(identifier: str, group: str = "astrology") -> dict:
    return {
        "evidence_id": identifier, "interpretive_tags": ["analysis"],
        "mapping_strength": "strong", "independence_group": group,
        "epistemic_class": "deterministic_calculation", "system": group,
    }


def test_within_system_recurrence_is_not_independent_convergence():
    packet = {"data_quality": {"astronomy": "available"}, "evidence_items": [_item("one"), _item("two")]}
    motif = rank_motifs(packet)[0]
    assert motif["independent_group_count"] == 1
    assert motif["within_system_recurrence"] == 1
    assert motif["confidence"] == "low"
    assert detect_agreements([motif]) == []


def test_cross_group_support_creates_bounded_agreement():
    packet = {"data_quality": {"astronomy": "available"}, "evidence_items": [_item("one"), _item("two", "name_number")]}
    motif = rank_motifs(packet)[0]
    agreement = detect_agreements([motif])[0]
    assert motif["independent_group_count"] == 2
    assert agreement["kind"] == "thematic_agreement"
    assert "not independent empirical" in agreement["ambiguity"]


def test_plan_is_deterministic_and_preserves_contradiction_evidence():
    first = exact_result()["synthesis"]["plan"]
    second = exact_result()["synthesis"]["plan"]
    assert first == second
    assert first["schema_version"] == "synthesis-plan-v1"
    if first["originating_tension"]:
        tension = first["originating_tension"]
        assert tension["unresolved"] is True
        assert tension["pole_a_evidence_ids"]
        assert tension["pole_b_evidence_ids"]
        tension_claims = next(section for section in first["narrative_sections"] if section["section_id"] == "originating_tension")["claims"]
        assert set(tension_claims[0]["evidence_ids"]) == set(tension["evidence_ids"])


def test_two_part_central_title_cites_both_motifs():
    plan = exact_result()["synthesis"]["plan"]
    assert len(plan["central_archetype"]["motif_ids"]) == 2
    motif_lookup = {item["motif_id"]: item for item in plan["dominant_motifs"]}
    expected = {
        evidence_id
        for motif_id in plan["central_archetype"]["motif_ids"]
        for evidence_id in motif_lookup[motif_id]["evidence_ids"]
    }
    central_claim = next(
        section["claims"][0]
        for section in plan["narrative_sections"]
        if section["section_id"] == "central_pattern"
    )
    assert set(plan["central_archetype"]["evidence_ids"]) == expected
    assert set(central_claim["evidence_ids"]) == expected


def test_polarity_detection_requires_both_supported_poles():
    motif = {"label": "autonomy", "evidence_ids": ["a"], "independence_groups": ["one"], "confidence": "low"}
    assert detect_contradictions([deepcopy(motif)]) == []
