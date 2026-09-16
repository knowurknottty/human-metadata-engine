"""Contracts for the opt-in Sumerian me modern reflection layer."""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src")]

from public_contract import PublicContractError, validate_observations  # noqa: E402
from server import analyze  # noqa: E402
from sumerian_me_reflection import build_sumerian_me_reflection  # noqa: E402


def test_reflection_is_disabled_by_default():
    result = build_sumerian_me_reflection([
        {"text": "I build systems", "capacity_domains": ["crafts_and_technical_practice"]}
    ])
    assert result["available"] is False
    assert result["status"] == "disabled_by_default"
    assert result["domain_matches"] == []
    assert result["historical_claim"] is False


def test_reflection_maps_only_explicit_observation_tags():
    observations = validate_observations([
        {
            "text": "I make and repair technical systems.",
            "source": "self_report",
            "confidence": "high",
            "capacity_domains": ["crafts_and_technical_practice", "knowledge_and_judgment"],
        },
        {
            "text": "This untagged statement must not be semantically inferred.",
            "source": "self_report",
        },
    ])
    result = build_sumerian_me_reflection(observations, enabled=True)
    assert result["available"] is True
    assert result["epistemic_layer"] == "modern_interpretive"
    assert result["mapping_basis"] == "explicit user-supplied observation capacity_domains tags"
    assert [item["category_id"] for item in result["domain_matches"]] == [
        "crafts_and_technical_practice", "knowledge_and_judgment"
    ]
    for item in result["domain_matches"]:
        assert item["support_observation_count"] == 1
        assert item["evidence_refs"][0]["evidence_id"] == "observation:0"
        assert "text" not in item["evidence_refs"][0]
        assert item["historical_me_items"]
    assert "score" not in result


def test_unknown_or_duplicate_capacity_tags_are_rejected():
    with pytest.raises(PublicContractError, match="unknown ids"):
        validate_observations([{
            "text": "test", "capacity_domains": ["not_a_domain"]
        }])
    with pytest.raises(PublicContractError, match="duplicates"):
        validate_observations([{
            "text": "test",
            "capacity_domains": ["knowledge_and_judgment", "knowledge_and_judgment"],
        }])


def test_public_analysis_requires_explicit_opt_in_and_redacts_observation_text():
    payload = {
        "name": "Ada Lovelace",
        "mode": "data",
        "observations": [{
            "text": "I repeatedly document technical work and make systems.",
            "source": "self_report",
            "confidence": "medium",
            "capacity_domains": ["crafts_and_technical_practice"],
        }],
    }
    default = analyze(payload)
    assert default["sumerian_me_reflection"]["status"] == "disabled_by_default"
    enabled = analyze({**payload, "sumerian_me_reflection": True})
    reflection = enabled["sumerian_me_reflection"]
    assert reflection["available"] is True
    assert reflection["domain_matches"][0]["category_id"] == "crafts_and_technical_practice"
    assert enabled["observations"][0]["capacity_domains"] == ["crafts_and_technical_practice"]
    assert "text" not in enabled["observations"][0]
    assert "document technical work" not in str(reflection)


def test_reflection_flag_must_be_boolean():
    with pytest.raises(PublicContractError, match="must be a boolean"):
        analyze({"name": "Test", "sumerian_me_reflection": "yes"})
