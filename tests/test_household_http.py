"""HTTP contract for the future paid household mode.

The single-person product stays live/free. Paid actions remain fail-closed until
server-verified entitlement support is actually configured.
"""

from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import os
import sys
from threading import Thread

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src")]

from server import Handler  # noqa: E402


class TestHouseholdHTTP:
    @classmethod
    def setup_class(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def teardown_class(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method: str, path: str, payload=None):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=30)
        body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
        headers = {"Content-Type": "application/json"} if body is not None else {}
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        raw = response.read()
        status = response.status
        ctype = response.getheader("Content-Type") or ""
        conn.close()
        return status, json.loads(raw) if ctype.startswith("application/json") else raw

    def test_single_person_analysis_remains_free_and_complete(self):
        status, body = self.request("POST", "/api/analyze", {"name": "Ada Lovelace", "mode": "data"})
        assert status == 200
        assert body["contract_version"] == "analysis-v1"
        assert body["subject_type"] == "self"
        assert body["report"]["metadata"]["report_schema_version"] == "report-v1"

    def test_household_config_is_discoverable_without_unlocking_paid_routes(self):
        status, body = self.request("GET", "/api/household/config")
        assert status == 200
        assert body["schema_version"] == "household-config-v1"
        assert body["free_single_scan"]["enabled"] is True
        assert body["free_single_scan"]["complete_product"] is True
        assert body["paid_modes"]["pair"]["label"] == "US Pair"
        assert body["paid_modes"]["household"]["label"] == "WE Household"
        assert body["pricing"]["pair_amount"] is None
        assert body["pricing"]["household_amount"] is None
        assert body["runtime"]["public_add_subject_enabled"] is False

    def test_entitlement_status_is_honestly_disabled(self):
        status, body = self.request("GET", "/api/entitlement")
        assert status == 200
        assert body == {
            "schema_version": "entitlement-status-v1",
            "status": "disabled",
            "signature_verified": False,
            "paid_routes_enabled": False,
        }

    def test_paid_household_compose_fails_closed_and_unimplemented_persistence_routes_stay_absent(self):
        status, body = self.request("POST", "/api/household/compose", {})
        assert status == 403
        assert body["code"] == "household_paid_disabled"
        assert body["single_scan_free"] is True

        for path in ("/api/household/registry", "/api/household/export", "/webhooks/commerce"):
            status, _ = self.request("POST", path, {})
            assert status == 404

    def test_version_exposes_contract_but_not_fake_entitlement(self):
        status, body = self.request("GET", "/api/version")
        assert status == 200
        flags = body["feature_flags"]
        assert flags["household_contracts"] is True
        assert flags["household_ui"] is False
        assert flags["paid_entitlement"] is False
        assert flags["demo_checkout"] is False
