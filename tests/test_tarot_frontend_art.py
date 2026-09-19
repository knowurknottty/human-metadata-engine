from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "webapp/static/index.html").read_text(encoding="utf-8")
JS = (ROOT / "webapp/static/tarot.js").read_text(encoding="utf-8")
CSS = (ROOT / "webapp/static/styles.css").read_text(encoding="utf-8")
ART_PATH = ROOT / "webapp/static/tarot-art.js"


def test_tarot_loads_a_dedicated_offline_art_renderer_before_draw_logic():
    assert ART_PATH.exists(), "Tarot needs a real local card-art renderer, not one generic glyph per suit"
    art = ART_PATH.read_text(encoding="utf-8")
    assert HTML.index("/tarot-art.js") < HTML.index("/tarot.js")
    remote = art.replace("http://www.w3.org/2000/svg", "")
    assert "http://" not in remote and "https://" not in remote
    assert "fetch(" not in art and "new Image" not in art
    assert "renderCardArt" in art
    assert "TarotArt.renderCardArt(card)" in JS


def test_renderer_distinguishes_major_pip_and_court_visual_grammars():
    assert ART_PATH.exists()
    art = ART_PATH.read_text(encoding="utf-8")
    for marker in ("MAJOR_SCENES", "renderMajor", "renderPips", "renderCourt", "pipPositions"):
        assert marker in art
    assert "22" in art
    assert "Wands" in art and "Cups" in art and "Swords" in art and "Pentacles" in art


def test_card_art_has_a_real_visual_surface_without_breaking_card_proportions():
    assert ART_PATH.exists()
    assert ".tarot-card-art" in CSS
    assert ".tarot-card-art svg" in CSS
    assert "aspect-ratio: 2 / 3" in CSS
