"""Regression tests for Unicode-aware legacy encoders and engine wiring."""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from encoders.gematria import gematria_signature  # noqa: E402
from encoders.isopsephy import isopsephy_signature  # noqa: E402
from encoders.pythagorean import pythagorean_signature  # noqa: E402
from encoders.chaldean import chaldean_signature  # noqa: E402
from encoders.ordinal import ordinal_signature  # noqa: E402
from encoders.binary_prime import binary_prime_signature  # noqa: E402
from encoders.linguistic import linguistic_signature  # noqa: E402
from engine import compute_unified_signature  # noqa: E402


class UnicodePipelineIntegrationTests(unittest.TestCase):
    def test_legacy_encoders_support_native_hebrew_and_greek(self):
        self.assertEqual(gematria_signature("שלום").absolute_total, 376)
        self.assertEqual(isopsephy_signature("ΑΒΓ").total, 6)
        self.assertEqual(pythagorean_signature("ΑΒΓ").total, 10)
        self.assertGreater(chaldean_signature("ΑΒΓ").compound_number, 0)
        self.assertEqual(ordinal_signature("ΑΒΓ").ordinal_total, 10)
        self.assertGreater(binary_prime_signature("ΑΒΓ").prime_total, 0)
        self.assertEqual(linguistic_signature("ΑΒΓ").normalized_text, "ABG")

    def test_unified_signature_embeds_all_roadmap_envelopes(self):
        signature = compute_unified_signature({
            "id": "test:muhammad",
            "text": "محمد",
            "birth": {"year": 1985, "month": 6, "day": 15},
            "as_of_year": 2026,
        })
        self.assertIn("kabbalah_tree_of_life", signature["encoders"])
        self.assertIn("esoteric_bridge", signature["encoders"])
        self.assertEqual(signature["encoders"]["arabic_abjad"]["data"]["abjad_total"], 92)
        self.assertEqual(signature["encoders"]["temporal_numerology"]["data"]["personal_year"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
