"""End-to-end narrative generation pipeline tests with epistemic validation."""
import pytest
from src.synthesis.prose_lexicon import enrich_synthesis_sentence
from src.synthesis.realize import _base_text, _sentence
from src.synthesis.epistemic_safety import (
    contains_overclaiming_language,
    validate_epistemic_strength,
    add_epistemic_metadata_to_section,
)


@pytest.fixture
def sample_claim():
    """Minimal claim for pipeline testing."""
    return {
        "claim_id": "claim_001",
        "motif": "navigation|compass bearing",
        "strength": 3.2,
        "evidence_ids": ["ev-astrology-ascendant"],
        "contradicting_evidence_ids": [],
        "claim_type": "reading",
        "metadata": {
            "texts": {
                "plain": "The theme of navigation appears across the available symbolic systems.",
                "mythic": "In mythic framing, this becomes a journey through celestial maps.",
                "research": "Research mode treats this as an empirical hypothesis to test."
            },
            "participating_systems": ["astrology", "tarot"],
            "independence_groups": ["group_A", "group_B"],
            "ambiguity": "Ambiguity exists in how recurrence is interpreted.",
            "alternative_reading": "Consider this as one possible reading among others."
        }
    }


def test_pipeline_run_1(sample_claim):
    """Pipeline run #1: basic flow with epistemic metadata."""
    mode = "plain"

    # 1. Base text generation
    base = _base_text(sample_claim, mode)
    assert len(base) > 0

    # 2. Lexicon enrichment (requires keyword args per prose_lexicon signature)
    enriched = enrich_synthesis_sentence(
        base=base,
        seed="pipeline_test_seed",
        mode=mode,
        claim_type=sample_claim["claim_type"],
        contradiction=bool(sample_claim.get("contradicting_evidence_ids")),
        return_metadata=True
    )
    enriched_text, lexicon_records = enriched
    assert isinstance(enriched_text, str)

    # 3. Sentence construction with metadata (use enriched lexicon records)
    sentence = _sentence(claim=sample_claim, text=enriched_text, lexicon_records=lexicon_records)

    # 4. Epistemic validation checks
    overclaim_result = contains_overclaiming_language(enriched_text)
    has_overclaiming, _ = overclaim_result
    assert not has_overclaiming, f"Overclaiming language detected: {overclaim_result}"
    is_valid, issues = validate_epistemic_strength([sentence], mode)
    assert is_valid is True
    assert issues == []

    # 5. Add epistemic metadata to section (requires evidence/contradiction counts)
    section_data = {"text": enriched_text, "mode": mode}
    section_with_meta = add_epistemic_metadata_to_section(section_data, evidence_count=1, contradiction_count=0)

    # Verify metadata propagation (Defect 4: no confidence_bound, only descriptive counts)
    assert "epistemic_metadata" in section_with_meta
    meta = section_with_meta["epistemic_metadata"]
    assert "evidence_item_count" in meta
    assert "contradiction_count" in meta
    assert "interpretive_only" in meta
    # confidence_bound removed per Defect 4 closure
    assert "confidence_bound" not in meta

    print(f"✓ Pipeline run 1 complete: {len(enriched_text)} chars, evidence_items={meta['evidence_item_count']}")


def test_pipeline_run_2(sample_claim):
    """Pipeline run #2: mythic mode with higher strength."""
    sample_claim["strength"] = 4.8
    mode = "mythic"

    base = _base_text(sample_claim, mode)
    enriched = enrich_synthesis_sentence(
        base=base,
        seed="pipeline_test_seed",
        mode=mode,
        claim_type=sample_claim["claim_type"],
        contradiction=bool(sample_claim.get("contradicting_evidence_ids")),
        return_metadata=True
    )
    enriched_text, lexicon_records = enriched

    # Mythic mode should still pass epistemic checks (interpretive framing)
    mythic_result = contains_overclaiming_language(enriched_text)
    has_overclaiming, _ = mythic_result
    assert not has_overclaiming, "Mythic overclaim detected"

    sentence = _sentence(claim=sample_claim, text=enriched_text, lexicon_records=lexicon_records)
    is_valid, issues = validate_epistemic_strength([sentence], mode)
    assert is_valid is True
    assert issues == []

    section_data = {"text": enriched_text, "mode": mode}
    section_with_meta = add_epistemic_metadata_to_section(section_data, evidence_count=1, contradiction_count=0)

    # Mythic mode should have descriptive metadata only (no confidence_bound per Defect 4)
    assert "confidence_bound" not in section_with_meta["epistemic_metadata"]

    print(f"✓ Pipeline run 2 complete: mythic mode, evidence_items={section_with_meta['epistemic_metadata']['evidence_item_count']}")


def test_pipeline_run_3(sample_claim):
    """Pipeline run #3: research mode with contradiction tracking."""
    sample_claim["strength"] = 2.9
    sample_claim["contradicting_evidence_ids"] = ["ev-astrology-descendant"]
    mode = "research"

    base = _base_text(sample_claim, mode)
    enriched = enrich_synthesis_sentence(
        base=base,
        seed="pipeline_test_seed",
        mode=mode,
        claim_type=sample_claim["claim_type"],
        contradiction=bool(sample_claim.get("contradicting_evidence_ids")),
        return_metadata=True
    )
    enriched_text, lexicon_records = enriched

    # Research mode should flag contradictions explicitly
    sentence = _sentence(claim=sample_claim, text=enriched_text, lexicon_records=lexicon_records)
    assert sentence.get("contradiction", False) == True

    is_valid, issues = validate_epistemic_strength([sentence], mode)
    assert is_valid is True
    assert issues == []

    section_data = {"text": enriched_text, "mode": mode}
    section_with_meta = add_epistemic_metadata_to_section(section_data, evidence_count=1, contradiction_count=1)

    # Contradictions tracked descriptively (no confidence_bound per Defect 4)
    assert "confidence_bound" not in section_with_meta["epistemic_metadata"]

    print(f"✓ Pipeline run 3 complete: research mode with contradiction, evidence_items={section_with_meta['epistemic_metadata']['evidence_item_count']}")


def test_pipeline_determinism(sample_claim):
    """Verify deterministic output across runs."""
    modes = ["plain", "mythic", "research"]
    outputs = []

    for m in modes:
        base = _base_text(sample_claim, m)
        enriched = enrich_synthesis_sentence(
            base=base,
            seed="pipeline_test_seed",
            mode=m,
            claim_type=sample_claim["claim_type"],
            contradiction=bool(sample_claim.get("contradicting_evidence_ids")),
            return_metadata=True
        )
        outputs.append(enriched[0])

    # All three runs should produce consistent output for same inputs
    assert len(set(outputs)) == 3, "Different modes produced identical text"

    print(f"✓ Determinism verified: {len(modes)} distinct mode outputs generated")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


@pytest.mark.parametrize("bad_strength", [None, True, False, "Strong", " strong", "4.5", "", [], {}, float("nan"), float("inf")])
def test_epistemic_strength_rejects_malformed_values(bad_strength):
    claim = {"claim_id": "bad-strength", "strength": bad_strength}
    valid, issues = validate_epistemic_strength([claim], "plain")
    assert valid is False
    assert issues
    assert "bad-strength" in issues[0]


@pytest.mark.parametrize("good_strength", ["tentative", "low", "medium", "high", "strong", 0, 2.5, 5])
def test_epistemic_strength_accepts_exact_support_labels_and_finite_range(good_strength):
    claim = {"claim_id": "good-strength", "strength": good_strength}
    valid, issues = validate_epistemic_strength([claim], "plain")
    assert valid is True
    assert issues == []
