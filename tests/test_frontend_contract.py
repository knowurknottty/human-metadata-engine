"""Static and semantic contracts for the public v0.8 interface."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
SCRIPT = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "webapp" / "static" / "styles.css").read_text(encoding="utf-8")


class EditorialFrontendContractTests(unittest.TestCase):
    def test_primary_heading_and_truthful_product_boundary_are_exact(self):
        self.assertIn(
            "A structured reflection on your name, birth data, and symbolic systems",
            HTML,
        )
        self.assertIn("What this is", HTML)
        self.assertIn("What this is not", HTML)
        self.assertIn("not a diagnosis, personality test, prediction, or scientific proof", HTML)

    def test_banned_oracle_and_checkout_copy_is_absent(self):
        public_copy = HTML.lower()
        for phrase in ("decode your identity", "reveal your destiny", "unlock your potential", "begin journey"):
            self.assertNotIn(phrase, public_copy)
        self.assertNotIn('id="paywall"', HTML)
        self.assertNotIn('id="cc-num"', HTML)
        self.assertNotIn("openPaywall", SCRIPT)

    def test_aliases_use_keyboard_operable_tokens_with_duplicate_protection(self):
        self.assertIn('id="alias-input"', HTML)
        self.assertIn('id="alias-list"', HTML)
        self.assertIn('id="alias-status"', HTML)
        self.assertIn("handleAliasKeydown", SCRIPT)
        self.assertIn("handleAliasPaste", SCRIPT)
        self.assertIn("removeAlias", SCRIPT)
        self.assertIn("That other name has already been added.", SCRIPT)
        self.assertIn("must be different from the primary name", SCRIPT)
        self.assertIn("payload.aliases", SCRIPT)

    def test_birth_date_unknown_time_and_location_contracts_are_explicit(self):
        self.assertIn('type="text" id="b-date"', HTML)
        self.assertIn('placeholder="YYYY-MM-DD"', HTML)
        self.assertIn("function normalizeBirthDateInput", SCRIPT)
        self.assertIn("function parseBirthDateInput", SCRIPT)
        self.assertIn('id="b-time-unknown"', HTML)
        self.assertIn("I do not know my exact birth time", HTML)
        self.assertIn('time_accuracy: unknownTime ? "unknown" : "exact"', SCRIPT)
        self.assertIn("time-sensitive results will be unavailable", HTML.lower())

    def test_ambiguity_is_a_choice_interaction_not_a_generic_error(self):
        self.assertIn("Which place did you mean?", HTML)
        self.assertIn('role="radiogroup"', HTML)
        self.assertIn('role="radio"', SCRIPT)
        self.assertIn("renderLocationChoices", SCRIPT)
        self.assertIn("selectLocation", SCRIPT)
        self.assertIn("timezone", SCRIPT)
        self.assertIn("Technical location details", SCRIPT)

    def test_errors_are_field_associated_and_move_focus(self):
        self.assertIn('role="alert" aria-live="assertive" tabindex="-1"', HTML)
        self.assertIn('control.setAttribute("aria-invalid", "true")', SCRIPT)
        self.assertIn('describedBy.add("form-error")', SCRIPT)
        self.assertIn("firstControl.focus()", SCRIPT)
        self.assertIn("summary.focus()", SCRIPT)
        self.assertIn("ERROR_COPY", SCRIPT)
        self.assertIn("collectEditorialValidationErrors", SCRIPT)
        self.assertIn("generated-inline-error", SCRIPT)
        self.assertIn("Correct these", SCRIPT)

    def test_loading_is_honest_live_and_duplicate_submits_are_blocked(self):
        self.assertIn("Creating your analysis…", HTML)
        self.assertIn('role="status" aria-live="polite"', HTML)
        self.assertIn("if (STATE.submitting) return", SCRIPT)
        self.assertIn("submitButton.disabled = true", SCRIPT)
        self.assertNotIn("PROCESSING_STEPS[step]", SCRIPT[SCRIPT.index("v0.8 editorial workflow"):])

    def test_report_has_navigation_coverage_and_information_types(self):
        for label in (
            "Overview", "Name calculations", "Birth chart", "Human Design",
            "Personal context", "Cross-system synthesis", "Tensions", "Methods and limitations",
        ):
            self.assertIn(label, SCRIPT)
        for label in (
            "Mathematical calculation", "Astronomical calculation", "Supplied by you",
            "Traditional interpretation", "Rule-based estimate", "Interpretive synthesis",
        ):
            self.assertIn(label, SCRIPT)
        self.assertIn("Data quality and coverage", SCRIPT)
        self.assertIn('· API ${esc(result.contract_version || "analysis-v1")}', SCRIPT)
        self.assertIn('result.application_version || "not supplied"', SCRIPT)
        self.assertNotIn("· application ${esc(result.contract_version", SCRIPT)

    def test_advanced_settings_translate_timezone_terms(self):
        self.assertIn("Advanced birth settings", HTML)
        self.assertIn('id="b-zone"', HTML)
        self.assertIn('id="b-lat"', HTML)
        self.assertIn('id="b-lon"', HTML)
        self.assertIn('id="b-tz"', HTML)
        self.assertIn("geographic timezone identifier", HTML)
        self.assertIn("Coordinated Universal Time", HTML)
        self.assertIn("Most people should leave these fields alone", HTML)

    def test_personal_context_is_collapsed_plain_language_and_self_reported(self):
        self.assertIn("Add personal context", HTML)
        self.assertIn("These answers are supplied by you", HTML)
        for field in ("p-mbti", "p-enne", "p-wing", "p-secondary", "p-instinct", "p-attach", "p-conflict"):
            self.assertIn(f'id="{field}"', HTML)
        self.assertNotIn("Optional psychological metadata", HTML)
        self.assertNotIn("Epistemic metadata", HTML)

    def test_untouched_big_five_values_are_not_submitted(self):
        self.assertIn('data-touched="false"', SCRIPT)
        self.assertIn('dataset.touched === "true"', SCRIPT)
        self.assertIn("Not supplied", SCRIPT)

    def test_fingerprint_is_explained_as_non_biometric_and_subordinate(self):
        self.assertIn("Calculated identity graphic", SCRIPT)
        self.assertIn("is not a biometric identifier", SCRIPT)
        self.assertIn("fingerprint-disclosure", SCRIPT)
        self.assertGreater(SCRIPT.index("id=\"overview\""), SCRIPT.index("report-header"))

    def test_privacy_copy_is_bounded_and_names_provider(self):
        self.assertIn("does not intentionally include your name, exact birth time, or coordinates", HTML)
        self.assertIn("birthplace text may be sent to the configured location provider", HTML.lower())
        self.assertIn("Open-Meteo geocoding", SCRIPT)
        self.assertIn("Network and infrastructure logs may still exist", SCRIPT)

    def test_mobile_breakpoints_prevent_fixed_width_workflow(self):
        for width in (800, 560, 340):
            self.assertRegex(STYLES, rf"@media \(max-width: {width}px\)")
        self.assertIn("grid-template-columns: 1fr", STYLES)
        self.assertIn("overflow-wrap: anywhere", STYLES)
        self.assertIn("min-height: 3rem", STYLES)
        self.assertNotRegex(STYLES, r"min-width:\s*[4-9]\d\dpx")

    def test_print_and_reduced_motion_contracts_are_present(self):
        self.assertIn("@media print", STYLES)
        self.assertIn("break-after: avoid-page", STYLES)
        self.assertIn("break-inside: avoid-page", STYLES)
        self.assertRegex(STYLES, r"\.skip-link[^\{]*\{?[^}]*display:\s*none\s*!important")
        self.assertRegex(STYLES, r"\.technical-details[^\{]*\{?[^}]*display:\s*none\s*!important")
        self.assertRegex(STYLES, r"\.report-section\s*\{\s*break-inside:\s*avoid-page")
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        self.assertIn("Print or save as PDF", SCRIPT)
        self.assertIn("Download Markdown", SCRIPT)
        self.assertIn("Edit inputs", SCRIPT)
        self.assertIn("Start a new analysis", SCRIPT)

    def test_empty_and_omitted_sections_are_explained(self):
        self.assertIn("Not included", SCRIPT)
        self.assertIn("No birth details were supplied", SCRIPT)
        self.assertIn("No optional personal context was supplied", SCRIPT)
        self.assertIn("withholds rising sign, house cusps, aspects", SCRIPT)
        self.assertIn("instead of presenting an estimated noon as exact", SCRIPT)

    def test_css_defines_complete_editorial_token_set(self):
        for token in (
            "--font-body", "--font-display", "--text-primary", "--text-secondary", "--text-muted",
            "--surface-page", "--surface-raised", "--surface-subtle", "--border-default", "--border-strong",
            "--accent", "--accent-hover", "--focus-ring", "--danger", "--warning", "--success",
            "--space-1", "--radius-small", "--radius-medium", "--content-width", "--reading-width",
        ):
            self.assertIn(token, STYLES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
