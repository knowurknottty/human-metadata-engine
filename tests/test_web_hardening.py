"""Regression tests for public web-server hardening controls."""

from __future__ import annotations

import os
import sys
from contextlib import redirect_stderr
from io import StringIO
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))

from server import (  # noqa: E402
    Handler,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
    SECURITY_HEADERS,
    _allow_analysis,
    _rate_limit_client_ip,
    _safe_request_log,
)


class WebHardeningTests(unittest.TestCase):
    def test_security_headers_cover_browser_boundaries(self):
        self.assertIn("frame-ancestors 'none'", SECURITY_HEADERS["Content-Security-Policy"])
        self.assertEqual(SECURITY_HEADERS["X-Frame-Options"], "DENY")
        self.assertEqual(SECURITY_HEADERS["Referrer-Policy"], "no-referrer")
        self.assertEqual(SECURITY_HEADERS["X-Content-Type-Options"], "nosniff")

    def test_rate_limit_blocks_then_recovers_after_window(self):
        ip = "test-rate-limit-isolated"
        start = 10_000.0
        for _ in range(RATE_LIMIT_REQUESTS):
            self.assertTrue(_allow_analysis(ip, now=start))
        self.assertFalse(_allow_analysis(ip, now=start))
        self.assertTrue(_allow_analysis(ip, now=start + RATE_LIMIT_WINDOW_SECONDS + 0.1))

    def test_netlify_static_host_uses_matching_security_headers(self):
        with open(os.path.join(ROOT, "netlify.toml"), encoding="utf-8") as handle:
            config = handle.read()
        self.assertIn("Content-Security-Policy", config)
        self.assertIn('X-Frame-Options = "DENY"', config)
        self.assertIn('Referrer-Policy = "no-referrer"', config)
        self.assertIn("Strict-Transport-Security", config)

    def test_proxy_ip_is_trusted_only_for_loopback_tunnel_traffic(self):
        headers = {"CF-Connecting-IP": "203.0.113.9", "X-Forwarded-For": "198.51.100.8"}
        self.assertEqual(_rate_limit_client_ip("127.0.0.1", headers, trust_proxy=True), "203.0.113.9")
        self.assertEqual(_rate_limit_client_ip("198.51.100.2", headers, trust_proxy=True), "198.51.100.2")
        self.assertEqual(_rate_limit_client_ip("127.0.0.1", headers, trust_proxy=False), "127.0.0.1")

    def test_request_logs_drop_query_data_and_never_include_bodies(self):
        line = _safe_request_log("GET", "/api/version?name=Private%20Name", 200)
        self.assertEqual(line, "[web] GET /api/version 200")
        self.assertNotIn("Private", line)

    def test_request_timeout_can_log_before_http_command_is_parsed(self):
        handler = object.__new__(Handler)
        output = StringIO()
        with redirect_stderr(output):
            handler.log_message("Request timed out: %r", TimeoutError())
        self.assertEqual(output.getvalue(), "[web] OTHER / -\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
