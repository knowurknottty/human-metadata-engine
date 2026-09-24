"""Contract tests for the additive Atlas expansion wrapper."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "webapp/static/index.html").read_text(encoding="utf-8")
CORE = (ROOT / "webapp/static/atlas.js").read_text(encoding="utf-8")
EXPANDED = (ROOT / "webapp/static/atlas-expanded.js").read_text(encoding="utf-8")
CSS = (ROOT / "webapp/static/atlas-expanded.css").read_text(encoding="utf-8")

ENCODERS = [
    "astrology","human_design","kabbalah_tree_of_life","pythagorean","chaldean","ordinal",
    "linguistic","binary_prime","gematria","isopsephy","sacred_geometry","alchemical_transformation",
    "sumerian_sexagesimal","sumerian_me_ontology","hermetic_principles","tarot",
    "babylonian_planetary","hermes_thoth_nabu","solomonic","arabic_abjad","chinese","egyptian",
    "vedic_jyotish","mayan_tzolkin","cuneiform_magic","elder_futhark","ogham","egyptian_maat",
    "mandaean_duodecimal","tartaria_architecture","indus_valley","unicode_codepoint","apollonius",
    "temporal_numerology","esoteric_bridge",
]
SYSTEMS = ["jyotish", "bazi", "maya_classical"]
LAYERS = ["comparisons", "correlations", "evidence", "sumerian_me_reflection", "synthesis.pattern_map"]


def test_expansion_loads_after_core_before_app_and_wraps_not_replaces():
    assert INDEX.index('/atlas.js?v=1.0.0') < INDEX.index('/atlas-expanded.js?v=1.0.0') < INDEX.index('/app.js?v=1.0.0')
    assert "const baseBuildAtlas = window.HMEAtlas.buildAtlas;" in EXPANDED
    assert "window.HMEAtlas.buildAtlas = expandedBuildAtlas;" in EXPANDED
    assert "protectedPanels" in EXPANDED
    for panel in ["constellation", "astrology", "human-design", "tree-of-life", "numerology", "fingerprint"]:
        assert f'"{panel}"' in EXPANDED
        assert f'panel("{panel}"' in CORE or f'panel("{panel}",' in CORE


def test_coverage_registry_declares_every_current_backend_encoder_system_and_layer():
    for key in ENCODERS + SYSTEMS:
        assert f'"{key}"' in EXPANDED
    for key in LAYERS:
        if key == "synthesis.pattern_map":
            assert f'"{key}"' in EXPANDED
        else:
            assert f'{key}:' in EXPANDED or f'"{key}"' in EXPANDED
    assert 'window.HMEAtlas.coverageRegistry = VISUAL_COVERAGE_REGISTRY' in EXPANDED


def test_richer_calculators_are_first_class_and_distinct():
    jyotish = EXPANDED[EXPANDED.index("function jyotishPanel"):EXPANDED.index("function baziPanel")]
    assert "nakshatra" in jyotish
    assert "d9_navamsha" in jyotish
    assert "d10_dasamsa" in jyotish
    assert "distinct from the tropical astrology panel" in jyotish

    bazi = EXPANDED[EXPANDED.index("function baziPanel"):EXPANDED.index("function mayaPanel")]
    assert "pillars" in bazi and "five_phase_distribution" in bazi
    assert "not a Day-Master strength score" in bazi

    maya = EXPANDED[EXPANDED.index("function mayaPanel"):EXPANDED.index("function labPanel")]
    assert "long_count" in maya and "calendar_round" in maya
    assert "distinct from the legacy mayan_tzolkin" in maya


def test_historical_and_project_authored_boundaries_are_visually_explicit():
    assert "The script remains explicitly undeciphered" in EXPANDED
    assert "Historical-claim status remains visible" in EXPANDED
    assert "Project-authored crosswalk. It cannot count as independent evidence." in EXPANDED
    assert "No automatic personal assignment is permitted." in EXPANDED


def test_expansion_uses_existing_selection_inspector_contract():
    for token in ["jyotish:body:", "bazi:pillar:", "maya:long-count:", "evidence-layer:", "system:sumerian_me_ontology"]:
        assert token in EXPANDED
    assert "data-atlas-select" in EXPANDED
    assert "data-link-keys" in EXPANDED
    assert "return {html,selections};" in EXPANDED


def test_expansion_has_responsive_and_print_safe_styles():
    for token in [".jyotish-layout", ".bazi-pillars", ".maya-long-count", ".visual-lab-grid", ".evidence-map-summary"]:
        assert token in CSS
    assert "@media" in CSS
    assert "repeat(auto-fit,minmax(min(100%,16rem),1fr))" in CSS
    assert "returnedMetrics.slice(0,2)" in EXPANDED
    assert "More returned stats" in EXPANDED
    assert "Preview · inspect for full method" in EXPANDED


def test_grouped_labs_promote_supported_records_to_bespoke_visuals():
    assert "function bespokeVisual" in EXPANDED
    assert "const bespoke = bespokeVisual(key,record,selections);" in EXPANDED
    for function_name in [
        "sequenceVisual", "positionalVisual", "chineseCoordinateVisual",
        "sacredGeometryVisual", "planetaryOrderVisual",
    ]:
        assert f"function {function_name}" in EXPANDED
    assert "function correspondenceVisual" not in EXPANDED


def test_futhark_ogham_and_positional_views_use_returned_fields_only():
    for token in [
        "data.runes", "data.tree_letters", "data.base_60_digits",
        "data.base_12_digits", "data.codepoints", "data.binary_string",
    ]:
        assert token in EXPANDED
    assert "No divinatory meaning is added" in EXPANDED
    assert "no lexical or personal meaning is inferred" in EXPANDED


def test_chinese_geometry_and_planetary_visuals_preserve_boundaries():
    assert "hex-index-grid" in EXPANDED
    assert "does not fabricate hexagram line structure" in EXPANDED
    assert "polygon_sides" in EXPANDED and "tetractys_layer" in EXPANDED
    assert "do not establish metaphysical or empirical properties" in EXPANDED
    assert "CHALDEAN_ORDER" in EXPANDED
    assert "Traditional ordering context only" in EXPANDED


def test_evidence_panel_includes_provenance_ribbon_without_new_votes():
    assert "provenance-ribbon" in EXPANDED
    assert "Evidence provenance ribbon" in EXPANDED
    assert "same evidence graph; no added votes" in EXPANDED


def test_bespoke_styles_cover_retained_renderer_classes():
    for token in [
        ".sequence-track", ".place-strip", ".hex-index-grid", ".wuxing-row",
        ".geometry-plate", ".geometry-polygon", ".tetractys-dots",
        ".planetary-order", ".planet-order-node", ".provenance-ribbon",
    ]:
        assert token in CSS
