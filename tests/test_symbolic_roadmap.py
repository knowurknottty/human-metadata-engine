"""Acceptance tests for the four-phase symbolic-systems roadmap.

Run with: python3 tests/test_symbolic_roadmap.py
"""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from encoders.pipeline import (  # noqa: E402
    ROADMAP_SYSTEMS,
    encode_symbolic_systems,
    prepare_encoding_input,
)


class SymbolicRoadmapTests(unittest.TestCase):
    def test_every_roadmap_system_is_registered_and_provenanced(self):
        expected = {
            "kabbalah_tree_of_life", "sacred_geometry",
            "alchemical_transformation", "sumerian_sexagesimal",
            "hermetic_principles", "tarot", "babylonian_planetary",
            "hermes_thoth_nabu", "solomonic", "arabic_abjad", "chinese",
            "egyptian", "vedic_jyotish", "mayan_tzolkin", "cuneiform_magic",
            "elder_futhark", "ogham", "egyptian_maat", "mandaean_duodecimal",
            "tartaria_architecture", "indus_valley", "unicode_codepoint",
            "apollonius", "temporal_numerology", "esoteric_bridge",
        }
        self.assertEqual(set(ROADMAP_SYSTEMS), expected)
        results = encode_symbolic_systems("CAPT")
        self.assertEqual(set(results), expected)
        for system, result in results.items():
            with self.subTest(system=system):
                self.assertEqual(result["system"], system)
                self.assertEqual(result["status"], "computed")
                self.assertIn("convention", result["provenance"])
                self.assertTrue(result["provenance"]["source_ids"])
                self.assertIsInstance(result["data"], dict)

    def test_unicode_input_preserves_native_script_and_uses_named_transliteration(self):
        prepared = prepare_encoding_input("שלום محمد ΑΒΓ")
        self.assertEqual(prepared["original_text"], "שלום محمد ΑΒΓ")
        self.assertEqual(prepared["scripts"], ["Hebrew", "Arabic", "Greek"])
        self.assertIn("SHLVM", prepared["latin_transliteration"])
        self.assertIn("MHMD", prepared["latin_transliteration"])
        self.assertEqual(prepared["transliteration_profile"], "builtin-v1")

    def test_native_abjad_and_temporal_systems_have_canonical_outputs(self):
        results = encode_symbolic_systems(
            "محمد",
            birth={"year": 1985, "month": 6, "day": 15},
            as_of_year=2026,
        )
        self.assertEqual(results["arabic_abjad"]["data"]["abjad_total"], 92)
        temporal = results["temporal_numerology"]["data"]
        self.assertEqual(temporal["life_path"], 8)
        self.assertEqual(temporal["personal_year"], 4)

    def test_cross_system_bridge_only_reports_explicit_correspondences(self):
        bridge = encode_symbolic_systems(
            "CAPT", birth={"year": 1985, "month": 6, "day": 15}
        )["esoteric_bridge"]
        self.assertEqual(bridge["data"]["bridge_type"], "Tarot-Kabbalah-Astrology-Numerology")
        self.assertIn("tarot", bridge["data"]["links"])
        self.assertIn("kabbalah", bridge["data"]["links"])
        self.assertIn("astrology", bridge["data"]["links"])
        self.assertIn("numerology", bridge["data"]["links"])

    def test_output_is_deterministic_and_does_not_claim_decipherment(self):
        first = encode_symbolic_systems("𒀭𒈹")
        second = encode_symbolic_systems("𒀭𒈹")
        self.assertEqual(first, second)
        indus = first["indus_valley"]
        self.assertTrue(indus["data"]["undeciphered"])
        self.assertEqual(indus["interpretation_level"], "symbolic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
