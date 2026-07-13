"""Deterministic location, historical timezone, and DST-boundary tests."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from location_resolution import (  # noqa: E402
    GeocodingCache,
    LocationResolutionError,
    OpenMeteoGeocodingProvider,
    ResolvedBirthLocation,
    normalize_location_query,
    resolve_birth_location,
    resolve_local_datetime,
)
from server import _resolve_birth_location, analyze  # noqa: E402


def payload(
    name: str,
    region: str,
    country: str,
    country_code: str,
    latitude: float,
    longitude: float,
    timezone_name: str,
    *,
    population: int = 100_000,
) -> dict:
    return {"results": [{
        "name": name,
        "admin1": region,
        "country": country,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_name,
        "population": population,
    }]}


def resolved_fixture() -> ResolvedBirthLocation:
    return ResolvedBirthLocation(
        query="Evanston, Wyoming, USA",
        display_name="Evanston, Wyoming, United States",
        city="Evanston",
        region="Wyoming",
        country="United States",
        country_code="US",
        latitude=41.2683,
        longitude=-110.9632,
        timezone_name="America/Denver",
        utc_offset_hours=-7.0,
        local_datetime_iso="1982-02-04T01:42:00-07:00",
        utc_datetime_iso="1982-02-04T08:42:00Z",
        resolution_source="recorded-test-provider",
        confidence=0.95,
    )


class LocationResolutionTests(unittest.TestCase):
    def resolve(self, query: str, provider_payload: dict, **date_fields) -> ResolvedBirthLocation:
        fields = {"year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42}
        fields.update(date_fields)
        return resolve_birth_location(
            query,
            fetch_json=lambda url, timeout: provider_payload,
            **fields,
        )

    def test_evanston_wyoming_golden_birth_fixture(self):
        result = self.resolve(
            "Evanston, Wyoming, USA",
            payload(
                "Evanston", "Wyoming", "United States", "US",
                41.2683, -110.9632, "America/Denver",
            ),
        )
        self.assertEqual(result.timezone_name, "America/Denver")
        self.assertEqual(result.utc_offset_hours, -7.0)
        self.assertEqual(result.local_datetime_iso, "1982-02-04T01:42:00-07:00")
        self.assertEqual(result.utc_datetime_iso, "1982-02-04T08:42:00Z")
        self.assertEqual(result.display_name, "Evanston, Wyoming, United States")

    def test_chicago_summer_and_winter_offsets(self):
        chicago = payload(
            "Chicago", "Illinois", "United States", "US",
            41.8781, -87.6298, "America/Chicago",
        )
        summer = self.resolve("Chicago, Illinois, USA", chicago, year=2020, month=7, day=1, hour=12)
        winter = self.resolve("Chicago, Illinois, USA", chicago, year=2020, month=1, day=1, hour=12)
        self.assertEqual(summer.utc_offset_hours, -5.0)
        self.assertEqual(winter.utc_offset_hours, -6.0)

    def test_arizona_does_not_apply_dst(self):
        phoenix = payload(
            "Phoenix", "Arizona", "United States", "US",
            33.4484, -112.0740, "America/Phoenix",
        )
        summer = self.resolve("Phoenix, Arizona, USA", phoenix, year=2020, month=7, day=1, hour=12)
        winter = self.resolve("Phoenix, Arizona, USA", phoenix, year=2020, month=1, day=1, hour=12)
        self.assertEqual(summer.utc_offset_hours, -7.0)
        self.assertEqual(winter.utc_offset_hours, -7.0)

    def test_newfoundland_fractional_offset_is_not_truncated(self):
        result = self.resolve(
            "St. John's, Newfoundland, Canada",
            payload(
                "St. John's", "Newfoundland and Labrador", "Canada", "CA",
                47.5615, -52.7126, "America/St_Johns",
            ),
            year=2020, month=1, day=1, hour=12,
        )
        self.assertEqual(result.utc_offset_hours, -3.5)

    def test_india_fractional_offset_is_not_truncated(self):
        result = self.resolve(
            "Kolkata, West Bengal, India",
            payload(
                "Kolkata", "West Bengal", "India", "IN",
                22.5726, 88.3639, "Asia/Kolkata",
            ),
            year=2020, month=1, day=1, hour=12,
        )
        self.assertEqual(result.utc_offset_hours, 5.5)

    def test_ambiguous_city_returns_ranked_choices(self):
        provider_payload = {"results": [
            payload("Springfield", "Illinois", "United States", "US", 39.78, -89.64, "America/Chicago", population=114_000)["results"][0],
            payload("Springfield", "Missouri", "United States", "US", 37.21, -93.29, "America/Chicago", population=169_000)["results"][0],
        ]}
        with self.assertRaises(LocationResolutionError) as raised:
            self.resolve("Springfield", provider_payload)
        self.assertEqual(raised.exception.code, "ambiguous_location")
        self.assertEqual(len(raised.exception.choices), 2)
        self.assertIn("Missouri", raised.exception.choices[0].display_name)

    def test_no_match_fails_closed(self):
        with self.assertRaises(LocationResolutionError) as raised:
            self.resolve("zzzzzzzz", {"results": []})
        self.assertEqual(raised.exception.code, "location_not_found")

    def test_provider_timeout_retries_once_then_fails(self):
        attempts = 0

        def timeout(url, seconds):
            nonlocal attempts
            attempts += 1
            raise TimeoutError("recorded timeout")

        provider = OpenMeteoGeocodingProvider(fetch_json=timeout, retries=1, sleeper=lambda _: None)
        with self.assertRaises(LocationResolutionError) as raised:
            resolve_birth_location(
                "Chicago, Illinois", year=1982, month=2, day=4, hour=1, minute=42,
                provider=provider,
            )
        self.assertEqual(attempts, 2)
        self.assertEqual(raised.exception.code, "location_provider_unavailable")
        self.assertTrue(raised.exception.retryable)

    def test_malformed_provider_payload_fails_explicitly(self):
        with self.assertRaises(LocationResolutionError) as raised:
            self.resolve("Chicago, Illinois", {"results": {"not": "a list"}})
        self.assertEqual(raised.exception.code, "malformed_location_provider_response")

    def test_nonexistent_spring_forward_time_is_rejected(self):
        with self.assertRaises(LocationResolutionError) as raised:
            resolve_local_datetime(
                "America/Chicago", year=2024, month=3, day=10, hour=2, minute=30
            )
        self.assertEqual(raised.exception.code, "nonexistent_local_time")

    def test_ambiguous_fall_back_time_is_rejected(self):
        with self.assertRaises(LocationResolutionError) as raised:
            resolve_local_datetime(
                "America/Chicago", year=2024, month=11, day=3, hour=1, minute=30
            )
        self.assertEqual(raised.exception.code, "ambiguous_local_time")

    def test_query_is_normalized_and_bounded(self):
        self.assertEqual(normalize_location_query("  Chicago  ,   Illinois  "), "Chicago, Illinois")
        with self.assertRaises(LocationResolutionError):
            normalize_location_query("x" * 161)

    def test_successful_provider_response_is_cached(self):
        calls = 0
        chicago = payload(
            "Chicago", "Illinois", "United States", "US", 41.8781, -87.6298, "America/Chicago"
        )

        def fetch(url, timeout):
            nonlocal calls
            calls += 1
            return chicago

        provider = OpenMeteoGeocodingProvider(
            fetch_json=fetch, retries=0, cache=GeocodingCache(max_entries=2, ttl_seconds=60)
        )
        for _ in range(2):
            resolve_birth_location(
                "Chicago, Illinois", year=1982, month=2, day=4, hour=12, minute=0,
                provider=provider,
            )
        self.assertEqual(calls, 1)

    @patch("server.resolve_birth_location")
    def test_server_fills_location_only_birth(self, resolver):
        resolver.return_value = resolved_fixture()
        result = _resolve_birth_location({
            "year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
            "location": "Evanston, Wyoming, USA", "time_accuracy": "exact",
        })
        self.assertEqual(result["lat"], 41.2683)
        self.assertEqual(result["lon"], -110.9632)
        self.assertEqual(result["timezone_offset"], -7.0)
        self.assertEqual(result["timezone_name"], "America/Denver")
        self.assertEqual(result["timezone_reliability"], "resolved_iana")

    @patch("server.resolve_birth_location")
    def test_kirk_location_alias_and_chart_integration_fixture(self, resolver):
        resolver.return_value = resolved_fixture()
        result = analyze({
            "name": "Kirk Evan Brown",
            "aliases": ["Capt", "Captain", "Knowurknot"],
            "mode": "magic",
            "birth": {
                "year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
                "location": "Evanston, Wyoming, USA", "time_accuracy": "exact",
            },
        })
        normalized = result["normalized_input"]["birth"]
        astrology = result["signature"]["encoders"]["astrology"]
        self.assertEqual(normalized["date"], "1982-02-04")
        self.assertEqual(normalized["timezone_basis"], "resolved_iana")
        self.assertEqual(astrology["sun_sign"], "Aquarius")
        self.assertEqual(astrology["moon_sign"], "Gemini")
        self.assertEqual(astrology["ascendant"], "Scorpio")
        self.assertEqual(astrology["house_system"], "Placidus")
        self.assertEqual(len(astrology["house_cusps"]), 12)
        self.assertAlmostEqual(astrology["house_cusps"][0], 229.8936, places=4)
        planet_houses = {item["planet"]: item["house"] for item in astrology["planets"]}
        self.assertEqual(planet_houses["Sun"], 3)
        self.assertEqual(planet_houses["Moon"], 8)
        self.assertEqual([item["name"] for item in result["aliases"]], ["Capt", "Captain", "Knowurknot"])

    @patch("server.resolve_birth_location")
    def test_coordinates_and_timezone_bypass_geocoding(self, resolver):
        result = _resolve_birth_location({
            "year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
            "lat": 41.2683, "lon": -110.9632, "timezone_name": "America/Denver",
            "time_accuracy": "exact",
        })
        resolver.assert_not_called()
        self.assertEqual(result["timezone_offset"], -7.0)
        self.assertEqual(result["timezone_reliability"], "resolved_iana")

    def test_conflicting_timezone_offset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "conflicts"):
            _resolve_birth_location({
                "year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
                "lat": 41.2683, "lon": -110.9632,
                "timezone_name": "America/Denver", "timezone_offset": -6,
                "time_accuracy": "exact",
            })


if __name__ == "__main__":
    unittest.main(verbosity=2)
