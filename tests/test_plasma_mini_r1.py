"""Focused acceptance contracts for PLASMA-MINI implementation R1."""
from __future__ import annotations

from pathlib import Path

from narrative_helpers import exact_payload
from server import analyze
from synthesis.prose_lexicon import literary_inventory

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "webapp/static/app.js").read_text(encoding="utf-8")
ATLAS = (ROOT / "webapp/static/atlas.js").read_text(encoding="utf-8")
STYLES = (ROOT / "webapp/static/identity-resonance-shell.css").read_text(encoding="utf-8")


def test_first_map_is_a_semantic_progressive_checkpoint_not_a_new_fetch():
    assert "Your first map" in APP
    assert "What was calculated" in APP
    assert "What is intentionally unavailable" in APP
    assert "What this map cannot know" in APP
    for boundary in (
        "not proof", "not a score", "not a diagnosis",
        "lived experience, choice, and future", "not empirical validation",
    ):
        assert boundary in APP
    assert "openFullAtlas" in APP
    assert "Open the full Atlas" in APP
    assert "fetch(" not in APP[APP.index("openFullAtlas"):APP.index("setAtlasMode(mode)")]
    assert 'id="first-map-title"' in APP
    assert "<ul>" in APP
    assert ".first-map" in STYLES


def test_first_map_preserves_full_atlas_and_sources_surfaces():
    assert 'id="full-atlas-content"' in APP
    assert "window.HMEAtlas.buildAtlas" in APP
    assert "Open research mode" in APP
    assert "sentence-level evidence ledger" in ATLAS


def test_literary_inventory_v2_is_reviewable_and_materially_expanded():
    inventory = literary_inventory()
    assert inventory["inventory_version"] == "literary-inventory-v2"
    assert inventory["accepted_units"] >= 180
    assert inventory["accepted_units"] == inventory["usable_units"]
    assert inventory["rejected_units"] >= 1
    assert inventory["legacy_mapped_units"] == 90
    assert set(inventory["required_categories"]) <= set(inventory["reachable_categories"])
    assert inventory["semantic_family_duplicates"] == 0


def test_lexicon_version_and_selection_are_replayable_without_family_repetition():
    result_a = analyze(exact_payload())
    result_b = analyze(exact_payload())
    for mode in ("plain", "mythic", "research"):
        assert result_a["synthesis"]["narratives"][mode] == result_b["synthesis"]["narratives"][mode]
        assert result_a["synthesis"]["narratives"][mode]["generation_metadata"]["lexicon_version"] == "deterministic-prose-lexicon-v2"
        for section in result_a["synthesis"]["narratives"][mode]["sections"]:
            families = [
                family for paragraph in section["paragraphs"]
                for family in paragraph["sentences"][0].get("lexicon_semantic_families", [])
            ]
            assert len(families) == len(set(families))


def test_handoff_v2_covers_categories_and_redacts_sensitive_material():
    result = analyze(exact_payload())
    handoff = result["handoff_v2"]
    assert handoff["schema_version"] == "human-manual-agent-handoff-v2"
    assert handoff["deterministic_replay"]["input_hash"] == result["input_hash"]
    assert handoff["public_response_coverage"]
    assert handoff["prohibited_inference_classes"]
    assert handoff["contradictions"]
    handoff_text = str(handoff).casefold()
    assert "41.2683" not in handoff_text
    assert "-110.9632" not in handoff_text
    assert "america/denver" not in handoff_text
    markdown = result["report"]["markdown"]
    assert "Agent Handoff v2" in markdown
    assert "What will be shared" in markdown
    assert "Supplied by you" in markdown
    assert "Project-authored interpretation" in markdown
