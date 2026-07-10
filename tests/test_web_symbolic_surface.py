"""Guard the public dashboard copy and extension-summary surface."""

from __future__ import annotations

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class WebSymbolicSurfaceTests(unittest.TestCase):
    def test_dashboard_has_a_data_driven_identity_atlas(self):
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        with open(os.path.join(ROOT, "webapp", "static", "styles.css"), encoding="utf-8") as handle:
            styles = handle.read()
        self.assertIn("identityAtlasSVG", source)
        self.assertIn("bodygraphMiniSVG", source)
        self.assertIn("activeChannelKeys", source)
        self.assertIn("[64,47]", source)
        self.assertIn("Provenance Ledger", source)
        self.assertIn("64-gate activation halo", source)
        self.assertIn(".atlas-layout", styles)
        self.assertIn(".identity-atlas", styles)
        self.assertIn(".provenance-ledger", styles)
        self.assertNotIn("max-height", styles)

    def test_dashboard_renders_provenanced_extension_summary(self):
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("Provenance Ledger", source)
        self.assertIn("extension.provenance.convention", source)
        self.assertIn("extension.interpretation_level", source)
        self.assertIn("JSON.stringify(extension.data, null, 2)", source)
        self.assertNotIn(".slice(0, 3)", source)
        self.assertNotIn("max-h-96", source)

    def test_landing_copy_describes_the_expansion_without_empirical_claims(self):
        with open(os.path.join(ROOT, "webapp", "static", "index.html"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("25 provenance-aware symbolic extensions", source)
        self.assertIn("interpretive lenses, not empirical claims", source)

    def test_paywall_supports_the_evan_bonus_code(self):
        with open(os.path.join(ROOT, "webapp", "static", "index.html"), encoding="utf-8") as handle:
            markup = handle.read()
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn('id="bonus-code"', markup)
        self.assertIn("app.redeemBonus(event)", markup)
        self.assertIn('const BONUS_CODE = "evan"', source)
        self.assertIn("redeemBonus(ev)", source)
        self.assertIn("this.unlockReport()", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
