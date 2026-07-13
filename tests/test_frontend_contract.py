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

        self.assertIn("Location resolves coordinates and the historical timezone", html)
        self.assertIn("The place is sent to Open-Meteo", html)
        self.assertIn('Enter a birth location, or provide latitude, longitude, and an IANA timezone', script)
        self.assertIn('const hasManualChartInputs', script)

    def test_advanced_birth_inputs_support_iana_timezone_without_manual_offset(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="b-zone"', html)
        self.assertIn("Advanced chart inputs", html)
        self.assertIn("payload.birth.timezone_name", script)
        self.assertIn('timezoneName !== "" || timezoneOffset !== ""', script)

    def test_simulated_checkout_is_not_present(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn('id="cc-num"', html)
        self.assertNotIn("openPaywall", script)
        self.assertIn("app.downloadReport()", script)

    def test_aliases_are_optional_bounded_and_rendered_separately(self):
        html = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="aliases"', html)
        self.assertIn("per line", html)
        self.assertIn("payload.aliases", script)
        self.assertIn("Alias calculations", script)

    def test_recoverable_errors_are_field_associated_and_preserve_the_form(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function showFormError(message, fieldId)", script)
        self.assertIn('control.setAttribute("aria-invalid", "true")', script)
        self.assertIn('describedBy.add("form-error")', script)
        self.assertIn("requestError.fieldId = apiErrorField(data)", script)

    def test_focus_and_print_styles_cover_interactive_and_report_surfaces(self):
        styles = (ROOT / "webapp" / "static" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("textarea:focus-visible", styles)
        self.assertIn("summary:focus-visible", styles)
        self.assertIn("break-after:avoid-page", styles)
        self.assertIn("break-inside:avoid-page", styles)

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
