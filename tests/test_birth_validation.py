"""Boundary tests for birth-data parsing and chart input validation."""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from server import _validated_birth, analyze  # noqa: E402
from encoders.astrology import compute_chart  # noqa: E402


class BirthValidationTests(unittest.TestCase):
    def valid_birth(self, **overrides):
        birth = {
            "year": 1985,
            "month": 6,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "timezone_offset": -7,
            "location": "Portland, Oregon, USA",
            "lat": 45.5152,
            "lon": -122.6765,
            "time_accuracy": "provided",
        }
        birth.update(overrides)
        return birth

    def test_rejects_impossible_calendar_date(self):
        with self.assertRaisesRegex(ValueError, "real calendar date"):
            _validated_birth(self.valid_birth(month=2, day=30))

    def test_requires_coordinates_and_timezone(self):
        for field in ("lat", "lon", "timezone_offset"):
            birth = self.valid_birth()
            del birth[field]
            with self.assertRaisesRegex(ValueError, field):
                _validated_birth(birth)

    def test_unknown_time_is_explicit_and_uses_noon(self):
        birth = _validated_birth(self.valid_birth(hour=12, minute=0, time_accuracy="unknown"))
        self.assertEqual(birth["time_accuracy"], "unknown")
        self.assertEqual((birth["hour"], birth["minute"]), (12, 0))

    def test_date_only_analysis_withholds_time_sensitive_outputs(self):
        result = analyze({
            "name": "Date Only Example",
            "birth": self.valid_birth(hour=12, minute=0, time_accuracy="unknown"),
        })
        astrology = result["signature"]["encoders"]["astrology"]
        self.assertTrue(astrology["date_only"])
        self.assertTrue(astrology["time_sensitive_fields_withheld"])
        self.assertIsNone(astrology["moon_sign"])
        self.assertIsNone(astrology["ascendant"])
        self.assertEqual(astrology["aspects"], [])
        human_design = result["signature"]["encoders"]["human_design"]
        self.assertIn("known birth time", human_design["unavailable"])

    def test_web_comparison_uses_public_references_and_agreement(self):
        result = analyze({"name": "Kirk Evan Brown"})
        self.assertEqual(result["comparison_metric"], "feature_agreement_v1")
        self.assertTrue(result["comparisons"])
        self.assertTrue(all(item["id"].startswith("figure:wikidata:")
                            for item in result["comparisons"]))
        self.assertLess(max(item["agreement"] for item in result["comparisons"]), 0.9)

    def test_chart_rejects_unknown_location_without_coordinates(self):
        with self.assertRaisesRegex(ValueError, "Latitude and longitude"):
            compute_chart(1985, 6, 15, 10, 30, -7, "An unlisted place")


if __name__ == "__main__":
    unittest.main(verbosity=2)
