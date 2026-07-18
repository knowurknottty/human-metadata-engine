"""Interaction, provenance, rendering, and responsive contracts for the Atlas."""

from pathlib import Path
import re
import unittest

from src.encoders.kabbalah import PATHS_22


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
ATLAS = (ROOT / "webapp" / "static" / "atlas.js").read_text(encoding="utf-8")
STYLES = (ROOT / "webapp" / "static" / "styles.css").read_text(encoding="utf-8")


class VisualAtlasContractTests(unittest.TestCase):
    def test_visualization_layer_is_separate_and_loaded_before_interactions(self):
        self.assertIn('/atlas.js?v=1.0.0', HTML)
        self.assertLess(HTML.index('/atlas.js?v=1.0.0'), HTML.index('/app.js?v=1.0.0'))
        self.assertIn("window.HMEAtlas = {buildAtlas}", ATLAS)
        self.assertIn("window.HMEAtlas.buildAtlas", APP)

    def test_six_primary_visual_surfaces_are_present(self):
        for title in (
            "Identity constellation",
            "Astrology wheel",
            "Human Design bodygraph",
            "Tree of Life",
            "Numerology matrix",
            "Identity fingerprint",
        ):
            self.assertIn(title, ATLAS)
        self.assertIn('"chinese", "I Ching / Wu Xing"', ATLAS)

    def test_visual_marks_are_bound_to_returned_response_fields(self):
        for field in (
            "astrology.planets",
            "astrology.aspects",
            "humanDesign.centers",
            "humanDesign.channels",
            "humanDesign.personality_gates",
            "humanDesign.design_gates",
            "data.dominant_sephirah",
            "signature.fingerprint",
            "encoders.esoteric_bridge",
        ):
            self.assertIn(field, ATLAS)
        self.assertNotIn("Math.random", ATLAS)

    def test_shared_inspector_exposes_complete_provenance_contract(self):
        self.assertIn('id="atlas-inspector-content"', ATLAS)
        for label in (
            '"Source"',
            '"Method"',
            '"Inputs"',
            '"Confidence category"',
            '"Interpretation type"',
            '"Limitations"',
        ):
            self.assertIn(label, APP)
        self.assertIn("data-report-target", APP)

    def test_selection_mapping_is_keyboard_operable_and_live_announced(self):
        self.assertIn('data-atlas-select', ATLAS)
        self.assertIn('tabindex="0" role="button"', ATLAS)
        self.assertIn('event.key === "Enter" || event.key === " "', APP)
        self.assertIn('id="atlas-selection-status"', ATLAS)
        self.assertIn('aria-live="polite"', ATLAS)
        self.assertIn('data-link-keys="${[id, ...dataLinks].join(" ")}"', ATLAS)

    def test_explorer_and_research_modes_change_presentation_only(self):
        self.assertIn('data-atlas-mode-button="explorer"', ATLAS)
        self.assertIn('data-atlas-mode-button="research"', ATLAS)
        self.assertIn("setAtlasMode(mode)", APP)
        self.assertNotIn("fetch(", APP[APP.index("setAtlasMode(mode)"):APP.index("selectAtlas(id)")])
        self.assertIn('[data-atlas-mode="explorer"] .research-only', STYLES)

    def test_bodygraph_keeps_all_gates_and_mobile_keeps_all_panels(self):
        self.assertIn("Array.from({length:64}", ATLAS)
        self.assertIn('aria-label="64-gate Human Design activation index"', ATLAS)
        self.assertIn("does not place gates at canonical channel endpoints", ATLAS)
        self.assertIn("@media (max-width: 720px)", STYLES)
        self.assertIn(".atlas-panels { grid-template-columns: 1fr; }", STYLES)
        self.assertNotIn(".atlas-panel { display: none", STYLES)
        self.assertIn("data-atlas-expand", ATLAS)
        self.assertIn("toggleAtlasFullscreen(id)", APP)
        self.assertIn('event.key === "Escape"', APP)
        self.assertIn("setAtlasFallback(expanded, false)", APP)

    def test_reference_relationships_are_complete_and_not_invented(self):
        self.assertIn("const TREE_PATHS_22", ATLAS)
        self.assertIn('data-reference-path="${esc(letter)}"', ATLAS)
        self.assertNotIn("system-edge--bridge", ATLAS)
        self.assertIn("they do not assert relationships between systems", ATLAS)
        self.assertIn("Configured correspondence record", ATLAS)
        block = ATLAS[ATLAS.index("const TREE_PATHS_22"):ATLAS.index("];", ATLAS.index("const TREE_PATHS_22"))]
        rendered = [(letter, int(first), int(second)) for letter, first, second in re.findall(r'\["([^"]+)",(\d+),(\d+)\]', block)]
        expected = [(letter, path[0], path[1]) for letter, path in PATHS_22.items()]
        self.assertEqual(rendered, expected)

    def test_visual_text_print_and_reduced_motion_fallbacks_exist(self):
        self.assertIn("atlas-text-equivalent", ATLAS)
        self.assertIn("@media print", STYLES)
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        self.assertIn("role=\"group\"", ATLAS)
        self.assertIn("<desc", ATLAS)
        print_rules = STYLES[STYLES.index("@media print"):]
        self.assertNotIn(".gate-grid,", print_rules)
        self.assertIn("min-height: 2.75rem", STYLES)

    def test_bodygraph_normalizes_public_center_names_before_drawing_channels(self):
        self.assertIn('"Heart/Will":"Heart/Ego"', ATLAS)
        self.assertIn('Splenic:"Spleen"', ATLAS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
