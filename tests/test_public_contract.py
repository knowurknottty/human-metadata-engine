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


class PublicContractTests(unittest.TestCase):
    def test_data_and_magic_modes_are_explicit(self):
        data = analyze({"name": "Ada Lovelace", "mode": "data"})
        magic = analyze({"name": "Ada Lovelace", "mode": "magic"})
        self.assertEqual(data["analysis_mode"], "data")
        self.assertEqual(data["report"]["mode"], "data")
        self.assertEqual(magic["analysis_mode"], "magic")
        self.assertEqual(magic["report"]["mode"], "magic")
        self.assertNotEqual(data["report"]["markdown"], magic["report"]["markdown"])

    def test_malformed_psychology_is_a_client_error(self):
        with self.assertRaisesRegex(ValueError, "finite number"):
            analyze({"name": "Test", "psychology": {"big_five": {"openness": "bad"}}})

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
