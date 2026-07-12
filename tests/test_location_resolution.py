"""Tests for automatic birth-place resolution."""

import unittest
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from location_resolution import LocationResolutionError, resolve_birth_location
from server import _resolve_birth_location


class LocationResolutionTests(unittest.TestCase):
    def test_resolves_coordinates_and_historical_offset(self):
        payload = {
            "results": [{
                "name": "Chicago", "admin1": "Illinois", "country": "United States",
                "latitude": 41.85003, "longitude": -87.65005, "timezone": "America/Chicago",
            }],
        }

        result = resolve_birth_location(
            "Chicago, USA", year=1982, month=4, day=17, hour=12, minute=0,
            fetch_json=lambda url, timeout: payload,
        )

        self.assertEqual(result["timezone_name"], "America/Chicago")
        self.assertEqual(result["timezone_offset"], -6.0)
        self.assertAlmostEqual(result["latitude"], 41.85003)

    def test_no_match_fails_closed(self):
        with self.assertRaisesRegex(LocationResolutionError, "No location match"):
            resolve_birth_location(
                "zzzzzzzz", year=1982, month=4, day=17, hour=12, minute=0,
                fetch_json=lambda url, timeout: {"results": []},
            )

    @patch("server.resolve_birth_location")
    def test_server_fills_location_only_birth(self, resolver):
        resolver.return_value = {
            "latitude": 41.85003,
            "longitude": -87.65005,
            "timezone_name": "America/Chicago",
            "timezone_offset": -6.0,
            "location": "Chicago, Illinois, United States",
        }
        result = _resolve_birth_location({
            "year": 1982, "month": 4, "day": 17, "hour": 12, "minute": 0,
            "location": "Chicago, USA", "time_accuracy": "exact",
        })
        self.assertEqual(result["lat"], 41.85003)
        self.assertEqual(result["lon"], -87.65005)
        self.assertEqual(result["timezone_offset"], -6.0)
        self.assertEqual(result["timezone_name"], "America/Chicago")


if __name__ == "__main__":
    unittest.main(verbosity=2)
