"""Living Pattern rendering and bidirectional selection contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "webapp/static/app.js").read_text(encoding="utf-8")
ATLAS = (ROOT / "webapp/static/atlas.js").read_text(encoding="utf-8")
STYLES = (ROOT / "webapp/static/styles.css").read_text(encoding="utf-8")


def test_living_pattern_is_integrated_before_six_surface_rail():
    assert "The Living Pattern" in ATLAS
    assert ATLAS.index("${livingPattern(result)}") < ATLAS.index('<nav class="atlas-rail"')
    assert "const panels = [" in ATLAS


def test_mythic_mode_fetches_remote_story_while_plain_and_research_remain_local():
    assert 'data-narrative-mode="${mode}"' in ATLAS
    assert 'data-narrative-panel="${mode}"' in ATLAS
    block = APP[APP.index("setNarrativeMode(mode)"):APP.index("selectNarrativeSentence(button)")]
    assert "loadRemoteMythic" in block
    assert "plain" in block and "mythic" in block and "research" in block
    assert "/api/narrative/mythic" in APP
    assert "STATE.requestPayload" in APP


def test_sentence_to_atlas_and_atlas_to_sentence_links_are_bidirectional():
    assert "data-evidence-ids" in ATLAS
    assert "data-atlas-targets" in ATLAS
    assert "selectNarrativeSentence(button)" in APP
    assert 'document.querySelectorAll("[data-narrative-sentence]")' in APP
    assert "related narrative sentences highlighted" in APP
    assert ".narrative-sentence.narrative-linked" in STYLES
    sentence_block = APP[APP.index("selectNarrativeSentence(button)"):APP.index("selectAtlas(id)")]
    assert 'sentence.classList.remove("narrative-linked")' in sentence_block


def test_reset_state_drops_synthesis_maps_and_stale_dom():
    assert "synthesisEvidence: new Map()" in APP
    assert "STATE = newEditorialState()" in APP
    assert '$("dashboard").replaceChildren()' in APP


def test_print_and_markdown_have_text_evidence_fallbacks():
    assert "sentence-level evidence ledger" in ATLAS
    assert "@media print" in STYLES
    assert ".narrative-ledger" in STYLES
