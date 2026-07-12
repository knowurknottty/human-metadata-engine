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

    def test_report_can_switch_modes_after_generation(self):
        script = (ROOT / "webapp" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('data-report-mode="data"', script)
        self.assertIn('data-report-mode="magic"', script)
        self.assertIn("async switchMode(nextMode)", script)
        self.assertIn("STATE.requestPayload", script)
        self.assertIn("payload.mode = nextMode", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
