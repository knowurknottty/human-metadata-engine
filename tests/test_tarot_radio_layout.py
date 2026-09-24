from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
FIX = (ROOT / "webapp" / "static" / "tarot-radio-fix.css").read_text(encoding="utf-8")


def test_tarot_radio_override_loads_after_primary_stylesheet():
    primary = HTML.index('/styles.css?v=1.0.1')
    override = HTML.index('/tarot-radio-fix.css?v=1.0.1')
    assert override > primary


def test_tarot_radio_override_restores_intrinsic_control_size_and_text_space():
    assert '.tarot-choices input[type="radio"]' in FIX
    assert 'width: 1.15rem' in FIX
    assert 'min-height: 0' in FIX
    assert 'flex: 0 0 auto' in FIX
    assert '.tarot-choices label > span' in FIX
    assert 'flex: 1 1 auto' in FIX
    assert 'min-width: 0' in FIX
