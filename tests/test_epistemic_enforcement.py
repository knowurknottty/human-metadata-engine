"""Regression tests for tier-aware narrative enforcement and export sanitization."""

from synthesis.epistemic_safety import (
    EPISTEMIC_TIERS,
    _safe_strength,
    contains_overclaiming_language,
    validate_epistemic_strength,
)
from synthesis.realize import realize


def test_epistemic_tier_is_an_enforced_ceiling():
    claim = {
        "claim_id": "tier-1-overreach",
        "epistemic_class": "deterministic_calculation",
        "strength": 4.0,
    }
    valid, issues = validate_epistemic_strength([claim], "plain")
    assert valid is False
    assert issues
    assert "max=1.0" in issues[0]


def test_epistemic_tier_boundary_passes():
    claim = {
        "claim_id": "tier-1-boundary",
        "epistemic_class": "deterministic_calculation",
        "strength": EPISTEMIC_TIERS["deterministic_calculation"],
    }
    assert validate_epistemic_strength([claim], "plain") == (True, [])


def test_malformed_strength_fails_closed():
    claim = {
        "claim_id": "malformed-strength",
        "epistemic_class": "interpretive_synthesis",
        "strength": "abc",
    }
    valid, issues = validate_epistemic_strength([claim], "plain")
    assert valid is False
    assert "must be numeric or a known strength label" in issues[0]


def test_strength_labels_remain_compatible():
    assert _safe_strength("tentative") == 1.0
    assert _safe_strength("medium") == 3.0
    assert _safe_strength("strong") == 4.0


def test_realize_sanitizes_before_export():
    plan = {
        "analysis_id": "audit-sanitize",
        "central_archetype": {"definition": "This proves you are destined for certainty."},
        "narrative_sections": [
            {
                "section_id": "reading",
                "purpose": "Reading",
                "claims": [
                    {
                        "claim_id": "claim_injected",
                        "claim_type": "reading",
                        "motif": "test",
                        "evidence_ids": ["ev-1"],
                        "strength": "tentative",
                        "allowed_language": [],
                        "forbidden_language": [],
                        "contradicting_evidence_ids": [],
                        "limitation": "test",
                        "metadata": {
                            "epistemic_class": "traditional_symbolic_interpretation",
                            "allow_lexicon_enrichment": False,
                            "texts": {
                                "plain": "You are destined to always know exact future events.",
                                "mythic": "You are destined to always know exact future events.",
                                "research": "You are destined to always know exact future events.",
                            },
                        },
                    }
                ],
            }
        ],
    }
    narrative = realize(plan, "plain")
    text = " ".join(
        sentence["text"]
        for section in narrative["sections"]
        for paragraph in section["paragraphs"]
        for sentence in paragraph["sentences"]
    )
    has_overclaim, issues = contains_overclaiming_language(text)
    assert has_overclaim is False, issues
    assert "destined" not in text.casefold()
    assert "always" not in text.casefold()
    assert "exact future events" not in text.casefold()
    assert "this proves" not in narrative["summary"].casefold()
