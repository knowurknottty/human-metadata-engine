"""HTTP contract checks for the custom sigil endpoint."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "webapp"))

from server import Handler  # noqa: E402


class SigilApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, body):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        connection.request("POST", "/api/sigil", json.dumps(body), {"Content-Type": "application/json"})
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def test_custom_sigil_is_public_and_deterministic(self):
        status, first = self.request({"text": "North Star"})
        self.assertEqual(status, 200)
        self.assertEqual(first["render_spec"], "sigil-v1")
        self.assertIn('data-digest="', first["svg"])
        status, second = self.request({"text": "North Star"})
        self.assertEqual(status, 200)
        self.assertEqual(first["hash"], second["hash"])

    def test_invalid_text_returns_client_error(self):
        status, payload = self.request({"text": "   "})
        self.assertEqual(status, 400)
        self.assertIn("cannot be empty", payload["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
