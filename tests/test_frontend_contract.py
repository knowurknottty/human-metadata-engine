"""Static checks for browser-sensitive public form contracts."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BirthDateFieldTests(unittest.TestCase):
    def test_birth_date_uses_iso_text_entry_and_client_normalization(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('type="text" id="b-date"', html)
        self.assertIn('placeholder="YYYY-MM-DD"', html)
        self.assertNotIn('type="date" id="b-date"', html)
        self.assertIn('/app.js?v=date-input-1', html)
        self.assertIn("function normalizeBirthDateInput", script)
        self.assertIn("function parseBirthDateInput", script)
        self.assertIn('Enter a real birth date in YYYY-MM-DD format.', script)

    def test_birth_location_resolves_chart_inputs_for_regular_users(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn("Coordinates and the historical UTC offset are resolved automatically", html)
        self.assertIn("The place is sent to a geocoding service", html)
        self.assertIn('Enter a birth location so the chart timezone and coordinates can be resolved.', script)
        self.assertIn('const hasManualChartInputs', script)

    def test_report_can_switch_modes_after_generation(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('data-report-mode="data"', script)
        self.assertIn('data-report-mode="magic"', script)
        self.assertIn("async switchMode(nextMode)", script)
        self.assertIn("STATE.requestPayload", script)
        self.assertIn("payload.mode = nextMode", script)

    def test_self_report_dropdowns_explain_values_and_discovery(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")

        for field in ("mbti", "enne", "wing", "attach"):
            self.assertIn(f'aria-describedby="p-{field}-help"', html)
            self.assertIn(f'id="p-{field}-help"', html)
        self.assertIn("validated MBTI", html)
        self.assertIn("Enneagram assessment", html)
        self.assertIn("supports a wing", html)
        self.assertIn("professionally assessed", html)

    def test_know_thyself_profile_is_separated_and_accessible(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        for field in ("p-secondary", "p-instinct", "p-attach", "p-conflict"):
            self.assertIn(f'id="{field}"', html)
        self.assertIn("Core cognition and motivation", html)
        self.assertIn("Relational patterns", html)
        self.assertIn("Self-regulation", html)
        self.assertIn("assessment_status", script)
        self.assertIn("updateWingOptions", script)
        self.assertIn("Same as the core type", script)

    def test_untouched_big_five_sliders_are_not_submitted_as_scores(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('data-touched="false"', script)
        self.assertIn('v.dataset.touched === "true"', script)
        self.assertIn('>Not answered</span>', script)

    def test_release_first_view_explains_evidence_and_index(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
        report = (ROOT / "src" / "report_safe.py").read_text(encoding="utf-8")

        for phrase in ("Your result in plain English", "What this does not mean", "What each layer means",
                       "Computed", "Birth data", "You reported", "Traditional lens", "Experimental index",
                       "Pattern convergence index"):
            self.assertIn(phrase, script)
        self.assertIn("Pattern convergence index", report)
        self.assertNotIn("Interpretive engine index: `", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
