"""Regression coverage for the custom sigil artifact."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from sigil import generate_custom_sigil, normalize_sigil_text  # noqa: E402


class CustomSigilTests(unittest.TestCase):
    def test_normalization_is_bounded_and_stable(self):
        self.assertEqual(normalize_sigil_text("  North   Star  "), "North Star")
        self.assertEqual(generate_custom_sigil("North Star"), generate_custom_sigil("North Star"))

    def test_different_labels_change_the_artifact(self):
        first = generate_custom_sigil("North Star")
        second = generate_custom_sigil("South Star")
        self.assertNotEqual(first["hash"], second["hash"])
        self.assertNotEqual(first["svg"], second["svg"])

    def test_svg_escapes_label_and_contains_manifest(self):
        result = generate_custom_sigil("A < B")
        self.assertIn("&lt;", result["svg"])
        self.assertIn('data-render="sigil-v1"', result["svg"])
        self.assertNotIn("< B", result["svg"])

    def test_empty_and_unbounded_text_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            generate_custom_sigil("   ")
        with self.assertRaisesRegex(ValueError, "too long"):
            generate_custom_sigil("a" * 121)


if __name__ == "__main__":
    unittest.main(verbosity=2)
