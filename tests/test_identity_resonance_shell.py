from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "webapp" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
SHELL = (STATIC / "identity-resonance-shell.css").read_text(encoding="utf-8")


class IdentityResonanceShellTests(unittest.TestCase):
    def test_shell_stylesheet_is_loaded_after_canonical_styles(self):
        base = '/styles.css?v=1.0.0'
        shell = '/identity-resonance-shell.css?v=1.0.0'
        self.assertIn(base, HTML)
        self.assertIn(shell, HTML)
        self.assertLess(HTML.index(base), HTML.index(shell))

    def test_current_atlas_and_application_script_order_is_preserved(self):
        self.assertIn('/atlas.js?v=1.0.0', HTML)
        self.assertIn('/app.js?v=1.0.0', HTML)
        self.assertLess(HTML.index('/atlas.js?v=1.0.0'), HTML.index('/app.js?v=1.0.0'))

    def test_original_visual_hierarchy_maps_to_all_current_primary_surfaces(self):
        for selector in (
            '#atlas-fingerprint', '#atlas-astrology', '#atlas-tree-of-life',
            '#atlas-human-design', '#atlas-numerology', '#atlas-constellation',
        ):
            self.assertIn(selector, SHELL)
        self.assertIn('grid-template-areas:', SHELL)
        self.assertIn('"fingerprint astrology numerology"', SHELL)

    def test_narrow_layout_keeps_every_atlas_panel_visible(self):
        self.assertIn('@media (max-width: 760px)', SHELL)
        mobile = SHELL[SHELL.index('@media (max-width: 760px)'):]
        self.assertIn('.atlas-panel, .atlas-panel--featured { display: block;', mobile)
        self.assertNotIn('.atlas-panel { display: none', SHELL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
