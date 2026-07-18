"""Cross-fixture specificity, sparse behavior, and psychology-context tests."""

from narrative_helpers import exact_result, narrative_sentences
from server import analyze


def _texts(result):
    return {sentence["text"] for sentence in narrative_sentences(result)}


def test_meaningfully_different_exact_fixtures_do_not_collapse_to_same_plan():
    first = exact_result(name="Kirk Evan Brown", year=1982, month=2, day=4)
    second = exact_result(name="Mara Solenne Vale", year=1994, month=9, day=17)
    first_motifs = [item["label"] for item in first["synthesis"]["plan"]["dominant_motifs"][:5]]
    second_motifs = [item["label"] for item in second["synthesis"]["plan"]["dominant_motifs"][:5]]
    assert first_motifs != second_motifs
    overlap = len(_texts(first) & _texts(second)) / max(len(_texts(first)), len(_texts(second)))
    assert overlap < 0.7


def test_name_only_narrative_is_shorter_and_explicitly_partial():
    sparse = analyze({"name": "Ada Lovelace", "mode": "magic"})
    full = exact_result(name="Ada Lovelace")
    sparse_text = " ".join(item["text"] for item in narrative_sentences(sparse))
    full_text = " ".join(item["text"] for item in narrative_sentences(full))
    assert "profile is partial" in sparse_text.lower()
    assert len(sparse_text) < len(full_text)
    assert not any(item["system"] in {"astrology", "human_design"} for item in sparse["synthesis"]["evidence"]["evidence_items"])


def test_composite_central_pattern_reads_as_a_combination():
    result = exact_result()
    first = narrative_sentences(result)[0]["text"]
    assert "the strongest recurring pattern combines" in first
    assert " and " in first


def test_user_context_can_reinforce_but_remains_one_independence_group():
    absent = analyze({"name": "Context Example", "mode": "magic"})
    supplied = analyze({"name": "Context Example", "mode": "magic", "psychology": {"mbti": "INTJ", "conflict_style": "collaborative"}})
    assert supplied["synthesis"]["evidence"]["data_quality"]["psychology"] == "user_supplied"
    context = [item for item in supplied["synthesis"]["evidence"]["evidence_items"] if item["system"] == "user_context"]
    assert context and {item["independence_group"] for item in context} == {"user_context"}
    assert supplied["synthesis"]["plan"]["dominant_motifs"] != absent["synthesis"]["plan"]["dominant_motifs"]
