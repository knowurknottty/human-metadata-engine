#!/usr/bin/env python3
"""
Identity Resonance — Web App Server
===================================

Zero-dependency (stdlib-only) HTTP server that fronts the Human
Metadata Engine. pyswisseph is optional: with it, astrology and Human
Design are exact; without it, the engine degrades gracefully to its
deterministic stub charts.

    python3 webapp/server.py            # http://localhost:8000
    PORT=3000 python3 webapp/server.py

Endpoints:
    GET  /                 the single-page app
    GET  /api/defaults     reference population (precomputed summaries)
    POST /api/analyze      {name, birth?, psychology?} -> full analysis
    GET  /api/health       liveness probe
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "src"))

from engine import compute_unified_signature, IDENTITIES  # noqa: E402
from analytics import feature_vector, cosine_similarity, \
    cross_encoder_correlations  # noqa: E402
from report import generate_report  # noqa: E402

STATIC = os.path.join(ROOT, "static")


def _jsonable(o):
    """Fallback serializer for dataclasses and other engine objects."""
    if hasattr(o, "__dict__"):
        return o.__dict__
    return str(o)

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}

# ---------------------------------------------------------------------
# Reference population: computed once at startup (fast — pure Python)
# ---------------------------------------------------------------------

_DEFAULTS = None


def get_defaults():
    global _DEFAULTS
    if _DEFAULTS is None:
        sigs = []
        for ident in IDENTITIES:
            try:
                sigs.append(compute_unified_signature(ident))
            except Exception:
                pass
        _DEFAULTS = sigs
    return _DEFAULTS


def default_summaries():
    out = []
    for s in get_defaults():
        out.append({
            "id": s["id"],
            "text": s["text"],
            "resonance": s["resonance"]["score"],
            "fingerprint": s["fingerprint"],
            "expression": s["encoders"]["pythagorean"]["expression"],
            "chaldean": s["encoders"]["chaldean"]["name_number"],
        })
    return out


def analyze(payload: dict) -> dict:
    name = (payload.get("name") or "").strip()
    if not name or not any(ch.isalpha() for ch in name):
        raise ValueError("A name containing letters is required.")
    if len(name) > 120:
        raise ValueError("Name is too long (max 120 characters).")

    identity = {"id": "user:" + "".join(c for c in name.lower() if c.isalnum())[:40],
                "text": name}

    birth = payload.get("birth") or None
    if birth and birth.get("year"):
        identity["birth"] = {
            "year": int(birth["year"]),
            "month": int(birth.get("month", 1)),
            "day": int(birth.get("day", 1)),
            "hour": int(birth.get("hour", 12)),
            "minute": int(birth.get("minute", 0)),
            "timezone_offset": float(birth.get("timezone_offset", 0)),
            "location": str(birth.get("location", ""))[:120],
        }
        if birth.get("lat") not in (None, "") and birth.get("lon") not in (None, ""):
            identity["birth"]["lat"] = float(birth["lat"])
            identity["birth"]["lon"] = float(birth["lon"])

    psychology = payload.get("psychology") or None
    if psychology:
        identity["psychology"] = psychology

    sig = compute_unified_signature(identity)

    # Comparisons against the reference population
    defaults = get_defaults()
    uv = feature_vector(sig)
    comps = []
    for d in defaults:
        comps.append({
            "id": d["id"],
            "text": d["text"],
            "resonance": d["resonance"]["score"],
            "similarity": round(cosine_similarity(uv, feature_vector(d)), 4),
        })
    comps.sort(key=lambda c: -c["similarity"])

    # Correlation view over user + population (digit agreement heatmap)
    corr = cross_encoder_correlations(defaults + [sig])

    report = generate_report(sig, psychology=psychology, comparisons=comps)

    return {
        "signature": sig,
        "comparisons": comps[:10],
        "correlations": corr,
        "report": report,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "IdentityResonance/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] %s\n" % (fmt % args))

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if ctype.startswith("application/json") else "max-age=300")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, default=_jsonable).encode(),
                   "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/health":
            return self._json(200, {"ok": True})
        if path == "/api/defaults":
            return self._json(200, {"identities": default_summaries()})
        if path == "/":
            path = "/index.html"
        # Static files — refuse traversal
        fs_path = os.path.realpath(os.path.join(STATIC, path.lstrip("/")))
        if not fs_path.startswith(os.path.realpath(STATIC)) or not os.path.isfile(fs_path):
            return self._send(404, b"Not found", "text/plain")
        ext = os.path.splitext(fs_path)[1]
        with open(fs_path, "rb") as f:
            self._send(200, f.read(), MIME.get(ext, "application/octet-stream"))

    def do_POST(self):
        if self.path.split("?")[0] != "/api/analyze":
            return self._send(404, b"Not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 64 * 1024:
                return self._json(413, {"error": "Payload too large."})
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = analyze(payload)
            return self._json(200, result)
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        except Exception:
            traceback.print_exc()
            return self._json(500, {"error": "Analysis failed — check server logs."})


def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"Warming reference population ({len(IDENTITIES)} identities)...")
    get_defaults()
    print(f"Identity Resonance running on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
