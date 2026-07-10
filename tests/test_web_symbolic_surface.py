"""Guard the public dashboard copy and extension-summary surface."""

from __future__ import annotations

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class WebSymbolicSurfaceTests(unittest.TestCase):
    def test_dashboard_renders_provenanced_extension_summary(self):
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("Expanded Symbolic Systems", source)
        self.assertIn("extension.provenance.convention", source)
        self.assertIn("extension.interpretation_level", source)
        self.assertNotIn(".slice(0, 3)", source)
        self.assertNotIn("max-h-96", source)

    def test_landing_copy_describes_the_expansion_without_empirical_claims(self):
        with open(os.path.join(ROOT, "webapp", "static", "index.html"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("25 provenance-aware symbolic extensions", source)
        self.assertIn("interpretive lenses, not empirical claims", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
