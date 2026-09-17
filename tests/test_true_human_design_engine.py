import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from true_human_design.engine import BirthRecord, calculate_chart


SYNTHETIC = BirthRecord(
    year=1982,
    month=2,
    day=4,
    hour=1,
    minute=42,
    timezone_name="America/Denver",
    latitude=41.2680,
    longitude=-110.9408,
    subject_id="private-anchor",
)


class EngineTests(unittest.TestCase):
    def test_expected_result_cannot_change_calculation(self):
        manifestor = calculate_chart(SYNTHETIC, expected_result={"type": "Manifestor"})
        generator = calculate_chart(SYNTHETIC, expected_result={"type": "Generator"})
        self.assertEqual(manifestor["resolutions"]["type"]["value"], generator["resolutions"]["type"]["value"])
        self.assertNotEqual(manifestor["comparison"]["expected_type"], generator["comparison"]["expected_type"])

    def test_profile_comes_from_sun_lines(self):
        chart = calculate_chart(SYNTHETIC)
        expected = f"{chart['activations']['personality']['Sun']['line']}/{chart['activations']['design']['Sun']['line']}"
        self.assertEqual(chart["resolutions"]["profile"]["value"], expected)
        self.assertIn("Personality Sun line", chart["resolutions"]["profile"]["reasons"][0])

    def test_every_resolution_has_reasons(self):
        chart = calculate_chart(SYNTHETIC)
        for key in ("type", "authority", "definition", "profile", "cross_signature"):
            with self.subTest(key=key):
                self.assertTrue(chart["resolutions"][key]["reasons"])

    def test_private_input_is_not_copied_by_default(self):
        chart = calculate_chart(SYNTHETIC)
        serialized = json.dumps(chart, sort_keys=True)
        self.assertNotIn("private-anchor", serialized)
        self.assertNotIn("41.268", serialized)
        self.assertNotIn("-110.94", serialized)
        self.assertIn("input_fingerprint", chart["ledger"])

    def test_ledger_hash_is_stable(self):
        left = calculate_chart(SYNTHETIC)
        right = calculate_chart(SYNTHETIC)
        self.assertEqual(left["ledger"]["calculation_hash"], right["ledger"]["calculation_hash"])

    def test_design_solver_residual_is_exposed(self):
        chart = calculate_chart(SYNTHETIC)
        self.assertLess(abs(chart["ledger"]["design_solver"]["residual_degrees"]), 1e-6)
        self.assertNotEqual(round(chart["ledger"]["design_solver"]["days_before_birth"], 6), 88.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
