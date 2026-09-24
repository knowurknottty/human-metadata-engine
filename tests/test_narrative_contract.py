"""narrative-v1 mode, claim, export, and version contracts."""

from narrative_helpers import exact_result, narrative_sentences
from server import _version_payload, analyze


def test_all_modes_share_claims_evidence_strength_and_sentence_ids():
    result = exact_result()
    baseline = [
        (item["sentence_id"], item["claim_ids"], item["evidence_ids"], item["strength"])
        for item in narrative_sentences(result, "plain")
    ]
    texts = []
    for mode in ("plain", "mythic", "research"):
        narrative = result["synthesis"]["narratives"][mode]
        assert narrative["schema_version"] == "narrative-v2"
        assert narrative["generation_metadata"]["remote_provider_used"] is False
        assert narrative["generation_metadata"]["temperature"] == 0
        assert [(item["sentence_id"], item["claim_ids"], item["evidence_ids"], item["strength"]) for item in narrative_sentences(result, mode)] == baseline
        texts.append(" ".join(item["text"] for item in narrative_sentences(result, mode)))
    assert len(set(texts)) == 3


def test_every_realized_sentence_has_claim_and_evidence():
    result = exact_result()
    for mode in ("plain", "mythic", "research"):
        for sentence in narrative_sentences(result, mode):
            assert sentence["claim_ids"]
            assert sentence["evidence_ids"]
            assert sentence["epistemic_label"] == "interpretive_synthesis"


def test_version_endpoint_reports_independent_schemas():
    version = _version_payload()
    assert version["schema_version"] == "analysis-v1"
    assert version["engine_version"] == "signature-v2"
    assert version["report_schema_version"] == "report-v1"
    assert version["synthesis_evidence_schema_version"] == "synthesis-evidence-v2"
    assert version["synthesis_plan_schema_version"] == "synthesis-plan-v2"
    assert version["narrative_schema_version"] == "narrative-v2"


def test_magic_export_contains_narrative_ledger_but_data_mode_does_not():
    magic = exact_result()
    assert "## The Human Manual Narrative — The Living Pattern" in magic["report"]["markdown"]
    assert "### Evidence ledger" in magic["report"]["markdown"]
    data = analyze({"name": "Ada Lovelace", "mode": "data"})
    assert data["synthesis"]["available"] is False
    assert "The Human Manual Narrative" not in data["report"]["markdown"]


def test_statement_provenance_is_separate_from_support_evidence():
    result = exact_result()
    for sentence in narrative_sentences(result, "plain"):
        assert sentence["statement_id"].startswith("stmt_v1_")
        assert sentence["epistemic_layer"] == "project_authored"
        assert sentence["empirical_status"] == "not_established"
        assert sentence["text_provenance"]["kind"] == "deterministic_composition"
        assert sentence["support_provenance"]["evidence_ids"] == sentence["evidence_ids"]
        assert sentence["text_provenance"]["asset_sha256"] not in sentence["evidence_ids"]
