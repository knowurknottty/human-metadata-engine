"""Behavioral coverage for expanded local prose, sparse inputs, and replay."""
from copy import deepcopy

from narrative_helpers import exact_result, narrative_sentences, resolve_path
from server import analyze
from synthesis.pipeline import build_synthesis
from synthesis.reading_library import GATE_PROMPTS, TAROT
from synthesis.verify import verify_narrative


def test_full_and_sparse_readings_have_specific_substantial_chapters():
    full = exact_result()
    sparse = analyze({"name": "Ada Lovelace", "mode": "magic"})
    chapters = {s["section_id"] for s in full["synthesis"]["narratives"]["plain"]["sections"]}
    assert {"name_reading", "natal_reading", "aspect_reading", "design_reading", "center_reading", "gate_reading", "channel_reading", "tarot_reading"} <= chapters
    assert len(" ".join(s["text"] for s in narrative_sentences(full)).split()) > 2500
    assert len(" ".join(s["text"] for s in narrative_sentences(sparse)).split()) > 800
    sparse_chapters = {s["section_id"] for s in sparse["synthesis"]["narratives"]["plain"]["sections"]}
    assert not {"natal_reading", "design_reading", "gate_reading"} & sparse_chapters
    assert {"name_reading", "tarot_reading"} <= sparse_chapters


def test_new_evidence_resolves_and_does_not_inflate_independence():
    result = exact_result()
    for item in result["synthesis"]["evidence"]["evidence_items"]:
        assert resolve_path(result, item["source_path"]) == item["source_value"]
        if item["symbol_family"].startswith("planet_") or item["system"] == "tarot":
            assert item["interpretive_tags"] == []
    for motif in result["synthesis"]["plan"]["dominant_motifs"]:
        assert "tarot" not in motif["independence_groups"]


def test_unknown_time_does_not_reintroduce_houses_or_design():
    result = analyze({"name":"Unknown Time", "mode":"magic", "birth":{"year":1990,"month":5,"day":12,"time_accuracy":"unknown","lat":41.8,"lon":-87.6,"timezone_name":"America/Chicago"}})
    items = result["synthesis"]["evidence"]["evidence_items"]
    assert not any(i["system"] == "human_design" or i["subsystem"] == "planet_house" for i in items)
    assert not any(i["source_path"].endswith(".ascendant") for i in items)


def test_rich_reading_cannot_be_changed_or_stripped_of_evidence():
    synthesis = exact_result()["synthesis"]
    narrative = deepcopy(synthesis["narratives"]["plain"])
    chapter = next(s for s in narrative["sections"] if s["section_id"] == "natal_reading")
    passage = chapter["paragraphs"][0]["sentences"][0]
    passage["text"] += " You are objectively exceptional."
    passage["evidence_ids"] = []
    errors = verify_narrative(synthesis["evidence"], synthesis["plan"], narrative)["errors"]
    assert {e["category"] for e in errors} >= {"reading_mismatch", "missing_evidence"}


def test_each_tarot_archetype_and_all_gate_prompts_can_be_realized():
    assert set(GATE_PROMPTS) == set(range(1,65))
    assert len(TAROT) == 22
    signature = deepcopy(exact_result()["signature"])
    signature["encoders"]["human_design"]["gates"] = list(range(1,65))
    for index in range(22):
        signature["encoders"]["tarot"]["data"]["major_arcana_index"] = index
        synthesis = build_synthesis(signature, None, f"catalog-{index}")
        assert all(v["valid"] for v in synthesis["verification"].values())
        chapter = next(s for s in synthesis["narratives"]["plain"]["sections"] if s["section_id"] == "gate_reading")
        assert len(chapter["paragraphs"]) == 64


def test_modes_change_reading_prose_but_keep_evidence():
    synthesis = exact_result()["synthesis"]
    selected = [next(s for s in synthesis["narratives"][mode]["sections"] if s["section_id"] == "name_reading")["paragraphs"][0]["sentences"][0] for mode in ("plain","mythic","research")]
    assert len({s["text"] for s in selected}) == 3
    assert selected[0]["evidence_ids"] == selected[1]["evidence_ids"] == selected[2]["evidence_ids"]
