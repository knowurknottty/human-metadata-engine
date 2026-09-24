"""Frontend contract for dormant paid US/WE composition views."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "webapp/static/index.html").read_text(encoding="utf-8")
HOUSEHOLD = (ROOT / "webapp/static/household.js").read_text(encoding="utf-8")
CSS = (ROOT / "webapp/static/household.css").read_text(encoding="utf-8")
APP = (ROOT / "webapp/static/app.js").read_text(encoding="utf-8")


def test_household_renderer_loads_after_atlas_extension_before_app():
    assert INDEX.index('/atlas-expanded.js?v=1.0.0') < INDEX.index('/household.js?v=1.0.0') < INDEX.index('/app.js?v=1.0.0')
    assert '/household.css?v=1.0.0' in INDEX
    assert 'window.HMEHousehold' in HOUSEHOLD
    assert 'renderRelationalView' in HOUSEHOLD


def test_household_module_exposes_local_intake_without_paid_compose_or_fake_checkout():
    assert 'fetch("/api/household/compose"' not in HOUSEHOLD
    assert 'fetch("/api/household/compose"' not in APP
    assert 'data-household-add' in INDEX
    assert 'household-intake-v1' in HOUSEHOLD
    assert 'transmission_state:"local_only"' in HOUSEHOLD
    assert 'Spouse / partner' in INDEX
    assert 'Child / adolescent' in INDEX
    assert 'Pet / companion animal' in INDEX
    assert 'does <strong>not</strong> submit, analyze, persist, or purchase anything' in INDEX
    assert 'Build my manual” submits only the primary profile' in INDEX
    assert 'localStorage' not in HOUSEHOLD
    assert 'sessionStorage' not in HOUSEHOLD
    assert 'checkout' not in HOUSEHOLD.casefold()
    assert 'unlock' not in HOUSEHOLD.casefold()


def test_us_pair_view_uses_neutral_composition_language():
    assert 'ME → YOU → US' in HOUSEHOLD
    assert 'US · Pair composition' in HOUSEHOLD
    assert 'composition, not ranking' in HOUSEHOLD
    assert 'does not produce a compatibility, soulmate, fit, harmony, or outcome judgment' in HOUSEHOLD
    assert 'Same returned marker' in HOUSEHOLD
    assert 'Different returned markers' in HOUSEHOLD


def test_we_household_view_preserves_child_and_pet_policy_boundaries():
    assert 'ME → YOU → US → WE' in HOUSEHOLD
    assert 'roster metadata only' in INDEX
    assert 'human symbolic engine is not applied to animals' in INDEX
    assert 'guardian' in HOUSEHOLD
    assert 'WE · Household composition' in HOUSEHOLD
    assert 'Children use child-safe worksheet policy' in HOUSEHOLD
    assert 'Pets use care-context policy' in HOUSEHOLD
    assert 'Neither is scored or interpreted as an adult relationship subject' in HOUSEHOLD


def test_stale_relational_view_renders_unavailable_instead_of_partial_result():
    assert 'Composition unavailable' in HOUSEHOLD
    assert 'stale or unresolved' in HOUSEHOLD
    assert 'relational output is suppressed' in HOUSEHOLD


def test_household_visuals_are_responsive_and_print_safe():
    for token in ['.household-pair-lanes', '.household-member-grid', '.household-observation-table', '.household-boundary', '.household-intake-grid', '.household-roster-card']:
        assert token in CSS
    assert '@media(max-width:720px)' in CSS
    assert '@media print' in CSS
