import logging
"""
Identity Comparison API
========================

REST API for real-time identity encoding.

Endpoints:
    POST /encode         — Encode a name, get full signature
    POST /compare        — Compare two identities
    POST /search         — Find similar identities
    POST /narrative      — Get personality narrative
    POST /fingerprint    — Get SVG fingerprint
    GET  /health         — Health check
    GET  /identities     — List all known identities

Usage:
    python3 -m src.api
    # or
    uvicorn src.api:app --reload
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import compute_unified_signature
from analytics import FEATURE_AGREEMENT_METRIC, feature_agreement, feature_vector
from birth_validation import validate_birth
from reference_population import famous_reference_identities
from search import IdentitySearch
from narrative import generate_narrative
from fingerprint import generate_fingerprint_svg

# Build search index on startup
_search_index = None
REFERENCE_IDENTITIES = famous_reference_identities()


def _identity_name(identity: dict) -> str:
    return identity.get("text", identity.get("name", identity.get("id", "")))


def _identity_from_encode_request(body: dict) -> dict:
    """Build an engine identity from the canonical API request shape.

    Older ``birth_date``/``birth_time``/``birth_place`` fields could never be
    consumed by the engine and therefore produced a silently name-only result.
    Reject them explicitly rather than accepting incorrect analysis.
    """
    name = body.get("name", "")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A name is required.")
    if len(name) > 120:
        raise ValueError("Name is too long (max 120 characters).")
    if any(body.get(field) is not None for field in ("birth_date", "birth_time", "birth_place")):
        raise ValueError(
            "Use the canonical 'birth' object with year, month, day, timezone_offset, lat, and lon."
        )
    identity = {"text": name.strip(), "id": name.strip()}
    birth = validate_birth(body.get("birth"), living_person=True, require_coordinates=True)
    if birth:
        identity["birth"] = birth
    return identity


def _get_search():
    global _search_index
    if _search_index is None:
        sig_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "unified_signatures.json")
        if os.path.exists(sig_path):
            _search_index = IdentitySearch.from_signatures(sig_path)
    return _search_index


class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _send_text(self, text, status=200, content_type="text/plain"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(text.encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            raise ValueError("Request body is empty.")
        if length > 64 * 1024:
            raise ValueError("Payload too large.")
        body = json.loads(self.rfile.read(length))
        if not isinstance(body, dict):
            raise ValueError("Request body must be a JSON object.")
        return body

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            self._send_json({
                "status": "ok",
                "engine": "human-metadata-engine",
                "version": "0.7.0",
                "status_note": "legacy loopback compatibility surface; use webapp/server.py for public traffic",
            })

        elif path == "/identities":
            names = [_identity_name(i) for i in REFERENCE_IDENTITIES]
            self._send_json({"identities": names, "count": len(names)})

        elif path.startswith("/identity/"):
            name = path.split("/identity/", 1)[1]
            for ident in REFERENCE_IDENTITIES:
                ident_name = _identity_name(ident)
                if ident_name.lower() == name.lower():
                    try:
                        sig = compute_unified_signature(ident)
                        self._send_json({"identity": ident_name, "signature": sig})
                    except Exception as e:
                        self._send_json({"error": str(e)}, 500)
                    return
            self._send_json({"error": f"Identity '{name}' not found"}, 404)

        else:
            self._send_json({"error": "Not found", "endpoints": ["/health", "/identities", "/identity/<name>"]}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        try:
            body = self._read_body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json({"error": str(exc)}, 400)
            return

        if path == "/encode":
            name = body.get("name", "")

            # Find in known identities or create ad-hoc
            ident = None
            for i in REFERENCE_IDENTITIES:
                if _identity_name(i).lower() == name.lower():
                    ident = i
                    break

            if ident is None:
                try:
                    ident = _identity_from_encode_request(body)
                except ValueError as exc:
                    self._send_json({"error": str(exc)}, 400)
                    return

            try:
                sig = compute_unified_signature(ident)
                narrative = generate_narrative(sig, name)
                self._send_json({
                    "identity": name,
                    "signature": sig,
                    "narrative": narrative,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/compare":
            name_a = body.get("name_a", "")
            name_b = body.get("name_b", "")
            sig_a, sig_b = None, None

            for i in REFERENCE_IDENTITIES:
                n = _identity_name(i)
                if n.lower() == name_a.lower():
                    sig_a = compute_unified_signature(i)
                if n.lower() == name_b.lower():
                    sig_b = compute_unified_signature(i)

            if sig_a is None or sig_b is None:
                missing = [n for n, s in [(name_a, sig_a), (name_b, sig_b)] if s is None]
                self._send_json({"error": f"Identities not found: {missing}"}, 404)
                return

            from analytics import identity_fingerprint
            agreement = feature_agreement(feature_vector(sig_a), feature_vector(sig_b))

            self._send_json({
                "name_a": name_a,
                "name_b": name_b,
                "comparison_metric": FEATURE_AGREEMENT_METRIC,
                "agreement": round(agreement, 6),
                "fingerprint_a": identity_fingerprint(sig_a),
                "fingerprint_b": identity_fingerprint(sig_b),
            })

        elif path == "/search":
            query = body.get("query", "")
            top_n = body.get("top_n", 5)
            search = _get_search()
            if search is None:
                self._send_json({"error": "Search index not built. Run engine first."}, 503)
                return
            results = search.find_similar(query, top_n=top_n)
            self._send_json({
                "query": query,
                "results": [{"identity": r.identity, "score": r.score, "rank": r.rank} for r in results],
            })

        elif path == "/narrative":
            name = body.get("name", "")
            ident = None
            for i in REFERENCE_IDENTITIES:
                if _identity_name(i).lower() == name.lower():
                    ident = i
                    break
            if ident is None:
                self._send_json({"error": f"Identity '{name}' not found"}, 404)
                return
            sig = compute_unified_signature(ident)
            narrative = generate_narrative(sig, name)
            self._send_json({"name": name, "narrative": narrative})

        elif path == "/fingerprint":
            name = body.get("name", "")
            ident = None
            for i in REFERENCE_IDENTITIES:
                if _identity_name(i).lower() == name.lower():
                    ident = i
                    break
            if ident is None:
                self._send_json({"error": f"Identity '{name}' not found"}, 404)
                return
            sig = compute_unified_signature(ident)
            svg = generate_fingerprint_svg(sig, identity_name=name)
            self._send_text(svg, content_type="image/svg+xml")

        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        pass  # Suppress logs


def run(port=8090):
    """Run the compatibility API on loopback only.

    The deployed public surface is ``webapp/server.py``. Keeping this legacy
    adapter local prevents README/CLI users from accidentally exposing the
    older wildcard-CORS contract to the network.
    """
    server = HTTPServer(("127.0.0.1", port), APIHandler)
    logging.info(f"Legacy compatibility API running on http://127.0.0.1:{port}")
    logging.info("Use webapp/server.py for the public API.")
    server.serve_forever()


if __name__ == "__main__":
    run()
