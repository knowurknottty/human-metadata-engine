"""Tarot should visually behave like 1/3/5-card spreads, not prose columns."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "webapp/static/tarot.js").read_text(encoding="utf-8")
ART_JS = (ROOT / "webapp/static/tarot-art.js").read_text(encoding="utf-8")
CSS = (ROOT / "webapp/static/styles.css").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "webapp/static/assets/tarot/manifest.json").read_text(encoding="utf-8"))


def test_tarot_has_separate_spread_stage_and_interpretation_region():
    assert "tarot-spread-stage" in JS
    assert "tarot-interpretations" in JS
    assert ".dataset.spread = spread" in JS


def test_one_three_and_five_card_spreads_have_intentional_geometries():
    assert '.tarot-spread-stage[data-spread="focus"]' in CSS
    assert '.tarot-spread-stage[data-spread="situation"]' in CSS
    assert '.tarot-spread-stage[data-spread="crossroads"]' in CSS
    assert ':nth-child(1)' in CSS and ':nth-child(5)' in CSS
    assert "grid-template-areas" in CSS or "grid-column" in CSS


def test_tarot_cards_keep_card_proportions_and_mobile_returns_to_reading_order():
    assert "aspect-ratio: 2 / 3" in CSS
    assert "MAJOR_ASSETS" in ART_JS
    assert "tarot-card-art-image" in ART_JS
    assert "renderMajor(svg,card)" in ART_JS
    assert MANIFEST["finished_major_count"] == 13
    assert MANIFEST["remaining_major_indices"] == list(range(13, 22))
    assert MANIFEST["remaining_minor_count"] == 56
    mobile = CSS[CSS.index("@media (max-width: 720px)"):]
    assert "tarot-spread-stage" in mobile
    assert "grid-template-columns: 1fr" in mobile
