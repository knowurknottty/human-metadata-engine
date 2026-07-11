#!/usr/bin/env python3
"""Regression tests for public accuracy hardening."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "webapp"))

from analytics_v2 import numerological_convergence  # noqa: E402
from birth_validation import BirthValidationError, canonical_birth_record, validate_birth  # noqa: E402
from engine import compute_unified_signature  # noqa: E402
from report_safe import generate_report  # noqa: E402


class BirthValidationTests(unittest.TestCase):
    def test_three_digit_year_is_rejected_for_public_product(self):
        with self.assertRaisesRegex(BirthValidationError, "four digits"):
            validate_birth({"year": 982, "month": 2, "day": 4}, living_person=True, current_year=2026)

    def test_known_1982_birth_is_preserved_character_for_character(self):
        birth = validate_birth(
            {
                "year": 1982,
                "month": 2,
                "day": 4,
                "hour": 1,
                "minute": 42,
                "timezone_offset": -7,
                "location": "Evanston, Wyoming, USA",
                "lat": 41.2680,
                "lon": -110.9408,
            },
            living_person=True,
            current_year=2026,
        )
        self.assertEqual(birth["year"], 1982)
        self.assertEqual(canonical_birth_record(birth)["date"], "1982-02-04")

    def test_invalid_calendar_date_is_rejected(self):
        with self.assertRaisesRegex(BirthValidationError, "Invalid birth date"):
            validate_birth({"year": 1982, "month": 2, "day": 31}, living_person=True, current_year=2026)


class TemporalAndAstrologyRegressionTests(unittest.TestCase):
    def test_temporal_numerology_uses_analysis_year_not_birth_year(self):
        analysis_year = datetime.now(timezone.utc).year
        birth = validate_birth(
            {
                "year": 1982,
                "month": 2,
                "day": 4,
                "hour": 1,
                "minute": 42,
                "timezone_offset": -7,
                "location": "Evanston, Wyoming, USA",
                "lat": 41.2680,
                "lon": -110.9408,
            },
            living_person=True,
            current_year=analysis_year,
        )
        signature = compute_unified_signature({
            "id": "test:kirk-1982",
            "text": "Kirk Evan Brown",
            "birth": birth,
            "as_of_year": analysis_year,
        })
        temporal = signature["encoders"]["temporal_numerology"]["data"]
        self.assertEqual(temporal["life_path"], 8)
        self.assertEqual(temporal["as_of_year"], analysis_year)
        astrology = signature["encoders"]["astrology"]
        self.assertEqual(astrology["sun_sign"], "Aquarius")
        self.assertEqual(astrology["moon_sign"], "Gemini")
        self.assertEqual(astrology["ascendant"], "Scorpio")


class ConvergenceTests(unittest.TestCase):
    def test_ordinal_does_not_create_a_second_independent_vote(self):
        signature = {
            "encoders": {
                "pythagorean": {"expression": 1},
                "ordinal": {"ordinal_reduced": 1},
                "chaldean": {"name_number": 2},
                "gematria": {"absolute_reduced": 3},
                "isopsephy": {"reduced": 4},
            }
        }
        self.assertEqual(numerological_convergence(signature), 0.0)

    def test_public_report_labels_symbolic_evidence(self):
        signature = compute_unified_signature({"id": "test:name", "text": "Kirk Evan Brown"})
        report = generate_report(signature)
        self.assertIn("How to read this report", report["markdown"])
        self.assertIn("not a percentage of accuracy", report["markdown"])
        self.assertNotIn("third, independent digit-vote", report["markdown"])


if __name__ == "__main__":
    unittest.main()
