"""Guard the public editorial report and symbolic-method surface."""

from __future__ import annotations

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class WebSymbolicSurfaceTests(unittest.TestCase):
    def test_report_subordinates_the_deterministic_graphic_to_comprehension(self):
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        with open(os.path.join(ROOT, "webapp", "static", "styles.css"), encoding="utf-8") as handle:
            styles = handle.read()
        self.assertIn("Calculated identity graphic", source)
        self.assertIn("is not a biometric identifier", source)
        self.assertIn("fingerprintSVG", source)
        self.assertIn("fingerprint-disclosure", styles)
        self.assertIn("report-content", styles)
        self.assertNotIn("Identity Atlas", source)

    def test_report_renders_method_and_source_without_dumping_raw_extension_json(self):
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("Methods and limitations", source)
        self.assertIn("Method and source", source)
        self.assertIn("const extensions = Object.values(encoders)", source)
        self.assertIn("${extensions.length} configured symbolic extensions", source)
        self.assertIn("Complete generated report and section labels", source)
        self.assertNotIn("JSON.stringify(extension.data", source)

    def test_landing_copy_describes_the_expansion_without_empirical_claims(self):
        with open(os.path.join(ROOT, "webapp", "static", "index.html"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("A structured reflection on your name, birth data, and symbolic systems", source)
        self.assertIn("keeps calculation separate from traditional interpretation", source)
        self.assertIn("not a diagnosis, personality test, prediction, or scientific proof", source)

    def test_fake_checkout_is_removed_and_full_report_actions_are_available(self):
        with open(os.path.join(ROOT, "webapp", "static", "index.html"), encoding="utf-8") as handle:
            markup = handle.read()
        with open(os.path.join(ROOT, "webapp", "static", "app.js"), encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn('id="cc-num"', markup)
        self.assertNotIn('id="paywall"', markup)
        self.assertNotIn("BONUS_CODE", source)
        self.assertNotIn("openPaywall", source)
        self.assertIn("app.downloadReport()", source)
        self.assertIn("window.print()", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
