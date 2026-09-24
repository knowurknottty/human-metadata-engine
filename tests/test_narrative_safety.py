"""Verifier, prohibited-language, and epistemic safety tests."""

from copy import deepcopy

from narrative_helpers import exact_result, narrative_sentences
from synthesis.contracts import PROHIBITED_LANGUAGE
from synthesis.verify import verify_narrative


def test_generated_sentences_avoid_prohibited_language():
    result = exact_result()
    for mode in ("plain", "mythic", "research"):
        text = " ".join(item["text"] for item in narrative_sentences(result, mode)).casefold()
        assert not [phrase for phrase in PROHIBITED_LANGUAGE if phrase in text]


def test_verifier_rejects_unknown_claim_and_evidence():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    sentence = narrative["sections"][0]["paragraphs"][0]["sentences"][0]
    sentence["claim_ids"] = ["claim_invented"]
    sentence["evidence_ids"] = ["ev_invented"]
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    assert report["valid"] is False
    assert {error["category"] for error in report["errors"]} >= {"unknown_claim", "unknown_evidence"}


def test_verifier_rejects_destiny_and_diagnostic_language():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    sentence = narrative["sections"][0]["paragraphs"][0]["sentences"][0]
    sentence["text"] = "You are destined for a diagnosis."
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    categories = {error["category"] for error in report["errors"]}
    assert "prohibited_language" in categories


def test_verifier_rejects_configured_prohibited_topics():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    sentence = narrative["sections"][0]["paragraphs"][0]["sentences"][0]
    sentence["text"] += " It reveals criminality."
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    assert report["valid"] is False
    assert any(error["detail"] == "criminality" for error in report["errors"])


def test_symbolic_and_user_supplied_items_are_never_empirical_personality_evidence():
    result = exact_result()
    assert {"medical diagnosis", "criminality", "exact future events"}.issubset(
        result["synthesis"]["evidence"]["unsupported_topics"]
    )
    for item in result["synthesis"]["evidence"]["evidence_items"]:
        if item["interpretive_tags"]:
            assert item["interpretation_class"] in {"traditional_symbolic_interpretation", "user_supplied"}
            assert item["limitations"]


def test_verifier_rejects_dropped_planned_evidence():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    sentence = next(
        sentence
        for section in narrative["sections"]
        for paragraph in section["paragraphs"]
        for sentence in paragraph["sentences"]
        if len(sentence["evidence_ids"]) > 1
    )
    sentence["evidence_ids"] = sentence["evidence_ids"][:-1]
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    assert report["valid"] is False
    assert "evidence_mismatch" in {error["category"] for error in report["errors"]}


def test_verifier_rejects_mixed_evidence_packet_versions():
    result = exact_result()
    synthesis = result["synthesis"]
    evidence = deepcopy(synthesis["evidence"])
    evidence["evidence_items"][0]["packet_schema_version"] = "synthesis-evidence-v1"
    report = verify_narrative(evidence, synthesis["plan"], synthesis["narratives"]["plain"])
    assert report["valid"] is False
    assert "mixed_record_versions" in {error["category"] for error in report["errors"]}


def test_verifier_rejects_duplicate_claim_realization():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    paragraph = narrative["sections"][0]["paragraphs"][0]
    paragraph["sentences"].append(deepcopy(paragraph["sentences"][0]))
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    assert report["valid"] is False
    assert "duplicate_claim_realization" in {error["category"] for error in report["errors"]}



def test_verifier_rejects_stale_packet_digest():
    result = exact_result()
    synthesis = result["synthesis"]
    evidence = deepcopy(synthesis["evidence"])
    evidence["warnings"] = [*evidence["warnings"], "mutated after digest"]
    report = verify_narrative(evidence, synthesis["plan"], synthesis["narratives"]["plain"])
    assert report["valid"] is False
    assert "evidence_integrity_mismatch" in {error["category"] for error in report["errors"]}


def test_verifier_rejects_source_value_changed_under_same_identity():
    result = exact_result()
    synthesis = result["synthesis"]
    evidence = deepcopy(synthesis["evidence"])
    evidence["evidence_items"][0]["source_value"] = "forged-value"
    report = verify_narrative(evidence, synthesis["plan"], synthesis["narratives"]["plain"])
    assert report["valid"] is False
    assert "evidence_integrity_mismatch" in {error["category"] for error in report["errors"]}


def test_verifier_rejects_plan_strength_mutation_even_with_existing_ids():
    result = exact_result()
    synthesis = result["synthesis"]
    plan = deepcopy(synthesis["plan"])
    claim = next(
        claim
        for section in plan["narrative_sections"]
        if section["section_id"] != "evidence_ledger"
        for claim in section["claims"]
    )
    claim["strength"] = "tentative" if claim["strength"] != "tentative" else "high"
    report = verify_narrative(synthesis["evidence"], plan, synthesis["narratives"]["plain"])
    assert report["valid"] is False
    assert "plan_derivation_mismatch" in {error["category"] for error in report["errors"]}


def test_verifier_rejects_benign_nonreading_prose_mutation():
    result = exact_result()
    synthesis = result["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    sentence = narrative["sections"][0]["paragraphs"][0]["sentences"][0]
    sentence["text"] += " Extra unplanned but harmless-looking prose."
    report = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)
    assert report["valid"] is False
    assert "narrative_derivation_mismatch" in {error["category"] for error in report["errors"]}
