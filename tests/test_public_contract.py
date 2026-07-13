"""Public request, mode, privacy, and determinism contracts."""

from __future__ import annotations

import os
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src")]

from server import analyze  # noqa: E402
from sigil import generate_custom_sigil  # noqa: E402
from public_contract import (  # noqa: E402
    ENNEAGRAM_WINGS,
    PublicContractError,
    normalize_public_name,
    validate_aliases,
    validate_psychology,
)


class PublicContractTests(unittest.TestCase):
    def test_name_rejects_html_markup_characters(self):
        with self.assertRaisesRegex(PublicContractError, "markup"):
            normalize_public_name('<script>alert("x")</script>')

    def test_aliases_are_bounded_normalized_and_distinct(self):
        self.assertEqual(
            validate_aliases([" Capt ", "Captain"], primary_name="Kirk Brown"),
            ["Capt", "Captain"],
        )
        with self.assertRaisesRegex(PublicContractError, "duplicates"):
            validate_aliases(["kirk brown"], primary_name="Kirk Brown")
        with self.assertRaisesRegex(PublicContractError, "at most 12"):
            validate_aliases([f"Alias {index}" for index in range(13)], primary_name="Kirk Brown")

    def test_data_and_magic_modes_are_explicit(self):
        data = analyze({"name": "Ada Lovelace", "mode": "data"})
        magic = analyze({"name": "Ada Lovelace", "mode": "magic"})
        self.assertEqual(data["analysis_mode"], "data")
        self.assertEqual(data["report"]["mode"], "data")
        self.assertEqual(magic["analysis_mode"], "magic")
        self.assertEqual(magic["report"]["mode"], "magic")
        self.assertNotEqual(data["report"]["markdown"], magic["report"]["markdown"])
        self.assertEqual(magic["report"]["sections"], list(range(1, 11)))
        self.assertEqual(len(magic["report"]["section_metadata"]), 10)
        self.assertEqual(
            [item["section"] for item in data["report"]["section_metadata"]],
            data["report"]["sections"],
        )
        self.assertEqual(
            [item["section"] for item in magic["report"]["section_metadata"]],
            magic["report"]["sections"],
        )
        self.assertEqual(
            {item["category"] for item in magic["report"]["section_metadata"]},
            {"mathematical", "astronomical", "user_reported", "traditional_symbolic", "heuristic", "speculative_synthesis"},
        )
        self.assertEqual(magic["report"]["metadata"]["report_schema_version"], "report-v1")
        self.assertEqual(magic["report"]["metadata"]["reproducibility_id"], magic["input_hash"])

    def test_report_markdown_escapes_user_controlled_markers(self):
        result = analyze({"name": "Ada *Star*", "mode": "magic"})
        self.assertIn(r"Ada \*Star\*", result["report"]["markdown"])
        self.assertNotIn("# Ada *Star*", result["report"]["markdown"])

    def test_malformed_psychology_is_a_client_error(self):
        with self.assertRaisesRegex(ValueError, "finite number"):
            analyze({"name": "Test", "psychology": {"big_five": {"openness": "bad"}}})

    def test_all_sixteen_mbti_values_are_accepted(self):
        values = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
        ]
        for value in values:
            self.assertEqual(validate_psychology({"mbti": value.lower()})["mbti"], value)

    def test_wings_are_adjacent_and_impossible_pairings_are_rejected(self):
        for core, wings in ENNEAGRAM_WINGS.items():
            for wing in wings:
                self.assertEqual(validate_psychology({"enneagram": {"type": core, "wing": wing}})["enneagram"]["wing"], wing)
        with self.assertRaisesRegex(PublicContractError, "adjacent"):
            validate_psychology({"enneagram": {"type": 5, "wing": 8}})

    def test_know_thyself_fields_round_trip_with_status_and_legacy_attachment(self):
        psychology = validate_psychology({
            "mbti": "INTJ",
            "enneagram": {"type": 5, "wing": 4},
            "secondaryEnneagramInfluence": 8,
            "instinctualVariant": "sp_so",
            "relational_patterns": {"attachment_style": "secure"},
            "conflict_style": "context_dependent",
            "assessmentStatus": {
                "mbti": {"status": "provisional"},
                "attachment": {"status": "structured", "source": "questionnaire"},
            },
        })
        self.assertEqual(psychology["secondary_enneagram_influence"], 8)
        self.assertEqual(psychology["relational_patterns"]["attachment_style"], "secure")
        self.assertEqual(psychology["assessment_status"]["mbti"]["status"], "provisional")
        self.assertEqual(psychology["assessment_status"]["attachment"]["status"], "structured")
        self.assertIsNone(validate_psychology({"secondaryEnneagramInfluence": "unknown"})["secondary_enneagram_influence"])
        result = analyze({"name": "Know Thyself", "psychology": psychology, "mode": "magic"})
        self.assertEqual(result["psychology"]["enneagram"], {"type": 5, "wing": 4})
        self.assertTrue(any("Type 8 influence" in item for item in result["signature"]["snapshot"]["profile_summary"]))
        self.assertIn("Relational patterns", result["report"]["markdown"])

    def test_attachment_compatibility_has_explicit_no_conflict_precedence(self):
        legacy = validate_psychology({"attachment": "secure"})
        canonical = validate_psychology({"relational_patterns": {"attachment_style": "secure"}})
        self.assertEqual(legacy["relational_patterns"]["attachment_style"], "secure")
        self.assertEqual(canonical["attachment"], "secure")
        with self.assertRaisesRegex(PublicContractError, "disagree"):
            validate_psychology({
                "attachment": "secure",
                "relational_patterns": {"attachment_style": "avoidant"},
            })

    def test_legacy_psychology_aliases_cannot_silently_override_canonical_values(self):
        conflict_pairs = (
            {"secondary_enneagram_influence": 5, "secondaryEnneagramInfluence": 8},
            {"instinctual_variant": "social", "instinctualVariant": "one_to_one"},
            {"conflict_style": "direct", "conflictStyle": "avoidant"},
            {
                "mbti": "INTJ",
                "assessment_status": {"mbti": {"status": "validated"}},
                "assessmentStatus": {"mbti": {"status": "provisional"}},
            },
        )
        for payload in conflict_pairs:
            with self.subTest(payload=payload), self.assertRaisesRegex(PublicContractError, "disagree"):
                validate_psychology(payload)

    def test_public_birth_without_time_is_explicitly_unknown(self):
        result = analyze({
            "name": "Date Only",
            "birth": {
                "year": 1985, "month": 6, "day": 15,
                "timezone_offset": -7, "lat": 45.5, "lon": -122.6,
            },
        })
        self.assertEqual(result["normalized_input"]["birth"]["time_accuracy"], "unknown")
        self.assertNotIn("latitude", result["normalized_input"]["birth"])
        self.assertNotIn("longitude", result["normalized_input"]["birth"])

    def test_signature_is_deterministic_without_wall_clock_field(self):
        first = analyze({"name": "Deterministic Example"})
        second = analyze({"name": "Deterministic Example"})
        self.assertEqual(first["signature"], second["signature"])
        self.assertEqual(first["input_hash"], second["input_hash"])

    def test_reference_subject_allows_historical_birth(self):
        result = analyze({
            "name": "Jesus",
            "subject_type": "reference",
            "birth": {
                "year": 1, "month": 1, "day": 1,
                "timezone_offset": 0, "lat": 31.7, "lon": 35.2,
                "time_accuracy": "unknown",
            },
        })
        self.assertEqual(result["subject_type"], "reference")

    def test_custom_sigil_is_valid_xml_for_symbolic_glyphs(self):
        svg = generate_custom_sigil("A < B")["svg"]
        ET.fromstring(svg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
