"""Integrity checks for the provenance-backed public reference population."""

from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from reference_population import famous_reference_identities, load_famous_reference_catalog  # noqa: E402


class ReferencePopulationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_famous_reference_catalog()

    def test_catalog_has_resolved_unique_provenanced_records(self):
        records = self.catalog["records"]
        self.assertEqual(self.catalog["exclusions"], [])
        self.assertEqual(self.catalog["record_count"], len(records))
        self.assertGreaterEqual(len(records), 100)
        self.assertEqual(len({record["qid"] for record in records}), len(records))
        self.assertEqual(len({record["id"] for record in records}), len(records))
        for record in records:
            self.assertEqual(record["calculation_status"], "core_only")
            self.assertTrue(record["provenance"]["wikidata_url"].endswith(record["qid"]))
            self.assertTrue(record["provenance"]["enwiki_url"].startswith("https://en.wikipedia.org/wiki/"))

    def test_requested_historical_and_infamous_people_are_present(self):
        qids = {record["qid"] for record in self.catalog["records"]}
        self.assertTrue({"Q302", "Q9441", "Q720", "Q2904131"}.issubset(qids))

    def test_runtime_references_do_not_invent_birth_times(self):
        identities = famous_reference_identities()
        self.assertEqual(len(identities), self.catalog["record_count"])
        self.assertTrue(all("birth" not in identity for identity in identities))


if __name__ == "__main__":
    unittest.main(verbosity=2)
