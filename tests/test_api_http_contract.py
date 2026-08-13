"""HTTP-level request, error, health, readiness, and version contracts."""

from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import os
import sys
from threading import Thread
import unittest
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import server as server_module  # noqa: E402
from server import Handler  # noqa: E402


class APIHTTPContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        with server_module._RATE_LIMIT_LOCK:
            server_module._RECENT_ANALYSES.clear()
        with server_module._DOWNLOAD_LOCK:
            server_module._PENDING_DOWNLOADS.clear()

    def request(self, method: str, path: str, body: bytes | None = None, content_type: str | None = None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=30)
        headers = {"Content-Type": content_type} if content_type else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        headers = dict(response.getheaders())
        connection.close()
        parsed = json.loads(payload) if headers.get("Content-Type", "").startswith("application/json") else payload
        return response.status, headers, parsed

    def post_json(self, payload):
        return self.request(
            "POST", "/api/analyze", json.dumps(payload, separators=(",", ":")).encode(), "application/json"
        )

    def test_operational_endpoints_have_distinct_contracts(self):
        live_status, _, live = self.request("GET", "/healthz")
        ready_status, _, ready = self.request("GET", "/readyz")
        version_status, _, version = self.request("GET", "/api/version")
        self.assertEqual(live_status, 200)
        self.assertEqual(live["status"], "alive")
        self.assertEqual(ready_status, 200)
        self.assertTrue(ready["ready"])
        self.assertEqual(version_status, 200)
        self.assertEqual(version["application_version"], "1.0.0")
        self.assertEqual(version["schema_version"], "analysis-v1")
        self.assertEqual(version["engine_version"], "signature-v2")
        self.assertEqual(version["report_schema_version"], "report-v1")
        self.assertTrue(version["ephemeris"]["available"])
        self.assertIn("location_resolution", version["feature_flags"])

    def test_security_headers_are_returned_by_api(self):
        _, headers, _ = self.request("GET", "/api/version")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_malformed_json_has_stable_error_code(self):
        status, _, payload = self.request(
            "POST", "/api/analyze", b'{"name":', "application/json"
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "invalid_json")
        self.assertEqual(payload["error"], payload["message"])

    def test_wrong_content_type_is_rejected(self):
        status, _, payload = self.request(
            "POST", "/api/analyze", b'{"name":"Example"}', "text/plain"
        )
        self.assertEqual(status, 415)
        self.assertEqual(payload["code"], "invalid_content_type")

    def test_markdown_download_is_a_no_store_attachment(self):
        markdown = "# Human Metadata Atlas\n\nCalculated test report.\n"
        body = json.dumps({
            "filename": "human_metadata_example.md",
            "markdown": markdown,
        }).encode()
        status, _, queued = self.request(
            "POST", "/api/report-download", body, "application/json"
        )
        self.assertEqual(status, 201)
        self.assertEqual(queued["expires_in_seconds"], server_module.DOWNLOAD_TTL_SECONDS)
        status, headers, payload = self.request("GET", queued["download_url"])
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/markdown; charset=utf-8")
        self.assertEqual(headers["Content-Disposition"], 'attachment; filename="human_metadata_example.md"')
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(payload, markdown.encode())

    def test_user_initiated_form_download_redirects_to_retryable_get(self):
        markdown = "# Physical browser report\n"
        body = urlencode({"filename": "human_metadata_physical.md", "markdown": markdown}).encode()
        status, headers, payload = self.request(
            "POST", "/api/report-download", body, "application/x-www-form-urlencoded"
        )
        self.assertEqual(status, 303)
        self.assertEqual(payload, b"")
        self.assertTrue(headers["Location"].startswith("/api/report-download?token="))
        status, headers, payload = self.request("GET", headers["Location"])
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Disposition"], 'attachment; filename="human_metadata_physical.md"')
        self.assertEqual(payload, markdown.encode())

    def test_markdown_download_rejects_unsafe_filenames(self):
        body = json.dumps({"filename": "../private.md", "markdown": "# Report"}).encode()
        status, _, payload = self.request(
            "POST", "/api/report-download", body, "application/json"
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "invalid_download_filename")

    def test_markdown_download_rejects_unknown_or_expired_tokens(self):
        status, _, payload = self.request("GET", "/api/report-download?token=unknown")
        self.assertEqual(status, 404)
        self.assertEqual(payload["code"], "download_not_found")

    def test_oversized_body_is_rejected_with_413(self):
        body = b'{"name":"' + (b"x" * (server_module.MAX_REQUEST_BYTES + 1)) + b'"}'
        status, _, payload = self.request("POST", "/api/analyze", body, "application/json")
        self.assertEqual(status, 413)
        self.assertEqual(payload["code"], "payload_too_large")

    def test_unknown_top_level_fields_are_rejected(self):
        status, _, payload = self.post_json({"name": "Example", "unexpected": True})
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "invalid_request")
        self.assertIn("unsupported fields", payload["message"])

    def test_html_markup_in_name_is_rejected_without_echoing_input(self):
        attack = '<script>alert("private")</script>'
        status, _, payload = self.post_json({"name": attack})
        self.assertEqual(status, 400)
        self.assertEqual(payload["code"], "invalid_request")
        self.assertNotIn("private", json.dumps(payload))

    def test_explicit_coordinates_and_timezone_derive_historical_offset(self):
        status, _, payload = self.post_json({
            "name": "Example",
            "birth": {
                "year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
                "time_accuracy": "exact", "lat": 41.2683, "lon": -110.9632,
                "timezone_name": "America/Denver",
            },
        })
        self.assertEqual(status, 200)
        self.assertEqual(payload["normalized_input"]["birth"]["timezone_basis"], "resolved_iana")

    def test_aliases_receive_separate_bounded_calculation_summaries(self):
        status, _, payload = self.post_json({
            "name": "Kirk Brown",
            "aliases": ["Capt", "Captain"],
        })
        self.assertEqual(status, 200)
        self.assertEqual(payload["normalized_input"]["aliases"], ["Capt", "Captain"])
        self.assertEqual([item["name"] for item in payload["aliases"]], ["Capt", "Captain"])
        self.assertTrue(all(item["deterministic"] for item in payload["aliases"]))
        self.assertTrue(all("pythagorean_expression" in item["calculations"] for item in payload["aliases"]))

    def test_invalid_calendar_date_is_rejected_before_geocoding(self):
        original = server_module.resolve_birth_location
        called = False

        def forbidden(*args, **kwargs):
            nonlocal called
            called = True
            raise AssertionError("geocoder should not run")

        server_module.resolve_birth_location = forbidden
        try:
            status, _, payload = self.post_json({
                "name": "Example",
                "birth": {"year": 2023, "month": 2, "day": 30, "location": "Chicago"},
            })
        finally:
            server_module.resolve_birth_location = original
        self.assertEqual(status, 400)
        self.assertFalse(called)
        self.assertIn("not a real calendar date", payload["message"])

    def test_birth_numbers_use_strict_json_types_and_partial_coordinates_fail(self):
        status, _, payload = self.post_json({
            "name": "Example",
            "birth": {"year": "1982", "month": 2, "day": 4, "location": "Chicago"},
        })
        self.assertEqual(status, 400)
        self.assertIn("JSON integer", payload["message"])

        status, _, payload = self.post_json({
            "name": "Example",
            "birth": {"year": 1982, "month": 2, "day": 4, "location": "Chicago", "lat": 41.8},
        })
        self.assertEqual(status, 400)
        self.assertIn("supplied together", payload["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
