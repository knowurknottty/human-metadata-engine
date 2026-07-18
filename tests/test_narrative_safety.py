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
