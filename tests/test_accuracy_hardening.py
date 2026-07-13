#!/usr/bin/env python3
"""Regression tests for public accuracy hardening."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "webapp"))

from analytics_v2 import numerological_convergence  # noqa: E402
from birth_validation import BirthValidationError, canonical_birth_record, validate_birth  # noqa: E402
from engine import compute_unified_signature, count_signature_dimensions  # noqa: E402
from report_safe import generate_report  # noqa: E402
from server import _disable_unvalidated_human_design  # noqa: E402


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
    def test_data_snapshot_counts_only_available_encoder_outputs(self):
        from server import _compute_signature

        signature = _compute_signature({"id": "test:name", "text": "Ada Lovelace"}, mode="data")
        available = signature["snapshot"]["available_layers"]
        self.assertEqual(len(available), 32)
        self.assertEqual(signature["snapshot"]["highlights"][0], "32 encoder outputs available")
        self.assertEqual(signature["dimensions"], 176)
        self.assertEqual(signature["computed_dimensions"], count_signature_dimensions(signature))
        self.assertEqual(signature["dimensions"] - signature["computed_dimensions"], 8)
        self.assertNotEqual(len(signature["encoders"]), len(available))

    def test_public_pipeline_does_not_compute_discarded_legacy_resonance(self):
        from server import _compute_signature

        with patch("engine.composite_resonance", side_effect=AssertionError("legacy resonance called")):
            signature = _compute_signature({"id": "test:name", "text": "Ada Lovelace"}, mode="data")
        self.assertEqual(signature["resonance"]["method_version"], "resonance-v3-chance-corrected")

    def test_public_snapshot_is_built_once_after_sanitization(self):
        from server import _compute_signature

        with patch("server.personality_snapshot", wraps=__import__("snapshot").personality_snapshot) as snapshot:
            _compute_signature({"id": "test:name", "text": "Ada Lovelace"}, mode="data")
            snapshot.assert_not_called()
            _compute_signature({"id": "test:name", "text": "Ada Lovelace"}, mode="magic")
            self.assertEqual(snapshot.call_count, 1)

    def test_public_interface_does_not_hardcode_encoder_count_as_a_landing_claim(self):
        html = (Path(ROOT) / "webapp" / "static" / "index.html").read_text(encoding="utf-8")
        script = (Path(ROOT) / "webapp" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("25</strong><span>", html)
        self.assertIn("const extensions = Object.values(encoders)", script)
        self.assertIn("${extensions.length} configured symbolic extensions", script)

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

    def test_public_report_does_not_overstate_feature_independence_or_assessment_confidence(self):
        signature = compute_unified_signature({"id": "test:name", "text": "Kirk Evan Brown"})
        report = generate_report(signature, psychology={"mbti": "INTJ"})
        markdown = report["markdown"]
        self.assertNotIn("eight independent reduced-digit categories", markdown)
        self.assertIn("eight reduced-digit feature categories", markdown)
        self.assertNotIn("confidence of its assessment method and is the only empirically-grounded", markdown)
        self.assertIn("not an independently verified capability claim", markdown)
        self.assertNotIn("quantity of divine energy the letters carry", markdown)

    def test_public_report_does_not_claim_disabled_human_design_was_computed(self):
        signature = compute_unified_signature({"id": "test:name", "text": "Kirk Evan Brown"})
        signature["encoders"]["human_design"] = {
            "available": False,
            "status": "disabled_failed_validation",
            "reason": "Legacy calculator failed validation.",
            "user_reported_type": "Manifestor",
        }
        report = generate_report(signature)
        markdown = report["markdown"]
        self.assertIn("Human Design status", markdown)
        self.assertIn("unavailable", markdown)
        self.assertIn("User-reported type: **Manifestor**", markdown)
        self.assertNotIn("Human Design encoders", markdown)
        self.assertNotIn("Human Design combines birth", markdown)
        self.assertNotIn("Human Design implementation is a simplified model", markdown)

    def test_invalidated_human_design_dimensions_are_removed_from_public_count(self):
        signature = {
            "text": "Test Identity",
            "dimensions": 40,
            "encoders": {
                "human_design": {
                    "type": "Generator",
                    "strategy": "Respond",
                    "authority": "Emotional",
                }
            },
        }
        _disable_unvalidated_human_design(signature, {"text": "Test Identity"})
        self.assertEqual(signature["dimensions"], 25)
        self.assertEqual(signature["invalidated_dimensions"]["human_design"], 15)
        self.assertFalse(signature["encoders"]["human_design"]["available"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
