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


def test_all_narrative_modes_are_local_deterministic_views():
    assert 'data-narrative-mode="${mode}"' in ATLAS
    assert 'data-narrative-panel="${mode}"' in ATLAS
    block = APP[APP.index("setNarrativeMode(mode)"):APP.index("selectNarrativeSentence(button)")]
    assert "plain" in block and "mythic" in block and "research" in block
    assert "loadRemoteMythic" not in APP
    assert "/api/narrative/mythic" not in APP
    assert 'mythic: "Story"' in ATLAS
    assert "generated in-process" in ATLAS


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


def test_pattern_map_is_exposed_before_narrative_chapters():
    assert 'class="pattern-map"' in ATLAS
    assert "Why the maps meet, diverge, and change" in ATLAS
    assert "Together" in ATLAS and "Divergent" in ATLAS
    assert "Statement provenance" in ATLAS and "Input sensitivity" in ATLAS
    assert ATLAS.index("$" + "{patternMapHTML}") < ATLAS.index('<div class="living-pattern-narratives">')
    assert ".pattern-map-grid" in STYLES


def test_synthesis_ui_uses_support_strength_not_empirical_confidence():
    living = ATLAS[ATLAS.index("function livingPattern"):ATLAS.index("function buildAtlas")]
    assert "support strength" in living
    assert "empirical validation not established" in living
    assert " confidence · " not in living


def test_submit_invalidates_and_aborts_stale_analysis_requests():
    assert "let REQUEST_EPOCH = 0;" in APP
    assert "let ACTIVE_REQUEST_CONTROLLER = null;" in APP
    assert "invalidateActiveAnalysisRequest();" in APP
    assert "new AbortController()" in APP
    assert "signal: requestController.signal" in APP
    assert "requestEpoch !== REQUEST_EPOCH" in APP
    assert 'error?.name === "AbortError"' in APP


def test_submit_clears_previous_analysis_before_fetch_and_reset_invalidates_epoch():
    submit = APP[APP.index("async submit(event)"):APP.index("reset() { this.startNew(); }")]
    assert submit.index("clearRenderedAnalysisState();") < submit.index('fetch("/api/analyze"')
    start = APP[APP.index("  startNew() {"):APP.index("  downloadReport() {")]
    assert "invalidateActiveAnalysisRequest();" in start
    assert '$("dashboard").replaceChildren()' in start
