"""Narrative keyboard, naming, reflow, and non-color contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "webapp/static/app.js").read_text(encoding="utf-8")
ATLAS = (ROOT / "webapp/static/atlas.js").read_text(encoding="utf-8")
STYLES = (ROOT / "webapp/static/styles.css").read_text(encoding="utf-8")


def test_sentences_are_native_buttons_with_meaningful_announcements():
    assert '<button type="button" class="narrative-sentence"' in ATLAS
    assert "Confidence ${esc(sentence.strength)}" in ATLAS
    assert "evidence references" in ATLAS
    assert "Contradiction retained" in ATLAS


def test_seal_and_tension_have_text_equivalents():
    assert 'role="img" aria-label="Deterministic text seal' in ATLAS
    assert 'role="group" aria-label="Unresolved tension' in ATLAS
    assert "tension.type" in ATLAS


def test_focus_touch_reflow_motion_and_non_color_cues_exist():
    assert "min-height: 44px" in STYLES
    assert ".narrative-sentence:focus-visible" in STYLES
    assert "border-left-width: 7px" in STYLES
    assert "overflow-wrap: anywhere" in STYLES
    assert "overflow-x: auto" in STYLES
    assert "@media (max-width: 720px)" in STYLES
    assert "@media (prefers-reduced-motion: reduce)" in STYLES


def test_shared_live_region_announces_narrative_selection():
    assert "Narrative sentence selected" in APP
    assert 'id="atlas-selection-status" class="sr-only" aria-live="polite"' in ATLAS
