"""Regression coverage for the user-provided Kabbalah and Apollonius modules."""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from encoders.apollonius import apollonius_signature  # noqa: E402
from encoders.kabbalah import kabbalah_signature  # noqa: E402


class IntegratedPrototypeTests(unittest.TestCase):
    def test_kabbalah_handles_native_hebrew_without_nonfinite_balance(self):
        signature = kabbalah_signature("שלום")
        self.assertEqual(signature.hebrew_total, 376)
        self.assertEqual(signature.normalized_text, "שלום")
        self.assertIsNone(kabbalah_signature("B").balance_ratio)

    def test_apollonius_uses_the_shared_transliteration_profile(self):
        signature = apollonius_signature("ΑΒΓ")
        self.assertEqual(signature.normalized_name, "ABG")
        self.assertGreater(signature.total_value, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
