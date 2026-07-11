#!/usr/bin/env python3
"""Identity Resonance web server: API, validation, and static assets."""

import json
import math
import os
import sys
import traceback
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "src"))

from engine import compute_unified_signature  # noqa: E402
from analytics import (  # noqa: E402
    FEATURE_AGREEMENT_METRIC,
    cross_encoder_correlations,
    feature_agreement,
    feature_vector,
)
from report import generate_report  # noqa: E402
from reference_population import famous_reference_identities  # noqa: E402

STATIC = os.path.join(ROOT, "static")
MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}
_DEFAULTS = None
_DEFAULT_ERRORS = []
PUBLIC_REFERENCE_IDENTITIES = famous_reference_identities()


def _safe_json(value):
    """Recursively produce strict JSON values; browsers reject NaN/Infinity."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): _safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_safe_json(v) for v in value]
    if hasattr(value, "__dict__"):
        return _safe_json(vars(value))
    return str(value)


def _validated_birth(raw):
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("Birth data must be an object.")
    required = ("year", "month", "day", "timezone_offset", "lat", "lon")
    missing = [field for field in required if raw.get(field) in (None, "")]
    if missing:
        raise ValueError("Birth data requires " + ", ".join(missing) + ".")
    try:
        birth = {
            "year": int(raw["year"]),
            "month": int(raw["month"]),
            "day": int(raw["day"]),
            "hour": int(raw.get("hour", 12)),
            "minute": int(raw.get("minute", 0)),
            "timezone_offset": float(raw["timezone_offset"]),
            "location": str(raw.get("location", "")).strip()[:120],
            "lat": float(raw["lat"]),
            "lon": float(raw["lon"]),
        }
    except (TypeError, ValueError) as exc:
        raise ValueError("Birth data contains an invalid number.") from exc
    try:
        date(birth["year"], birth["month"], birth["day"])
    except ValueError as exc:
        raise ValueError("Birth date is not a real calendar date.") from exc
    if not 0 <= birth["hour"] <= 23:
        raise ValueError("Birth hour must be between 0 and 23.")
    if not 0 <= birth["minute"] <= 59:
        raise ValueError("Birth minute must be between 0 and 59.")
    if not math.isfinite(birth["timezone_offset"]) or not -14 <= birth["timezone_offset"] <= 14:
        raise ValueError("UTC offset must be between -14 and +14.")
    if not math.isfinite(birth["lat"]) or not math.isfinite(birth["lon"]):
        raise ValueError("Latitude and longitude must be finite numbers.")
    if not -90 <= birth["lat"] <= 90 or not -180 <= birth["lon"] <= 180:
        raise ValueError("Latitude or longitude is outside its valid range.")
    birth["time_accuracy"] = "provided" if raw.get("time_accuracy") == "provided" else "unknown"
    if not birth["location"]:
        birth["location"] = f"{birth['lat']:.4f}, {birth['lon']:.4f}"
    return birth


def _normalized_reference(identity):
    """Repair legacy sentinel hours (101/102) as unknown/noon, never silently drop."""
    item = dict(identity)
    if item.get("birth"):
        birth = dict(item["birth"])
        if int(birth.get("hour", 12)) > 23:
            birth["hour"] = 12
            birth["minute"] = 0
            birth["time_accuracy"] = "unknown"
        item["birth"] = birth
    return item


def get_defaults():
    global _DEFAULTS, _DEFAULT_ERRORS
    if _DEFAULTS is None:
        _DEFAULTS, _DEFAULT_ERRORS = [], []
        for ident in PUBLIC_REFERENCE_IDENTITIES:
            try:
                _DEFAULTS.append(compute_unified_signature(_normalized_reference(ident)))
            except Exception as exc:
                _DEFAULT_ERRORS.append({"id": ident.get("id"), "error": str(exc)})
    return _DEFAULTS


def default_summaries():
    return [{
        "id": s["id"], "text": s["text"],
        "resonance": s["resonance"]["score"],
        "fingerprint": s["fingerprint"],
        "expression": s["encoders"]["pythagorean"]["expression"],
        "chaldean": s["encoders"]["chaldean"]["name_number"],
    } for s in get_defaults()]


def analyze(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    name = (payload.get("name") or "").strip()
    if not name or not any(ch.isalpha() for ch in name):
        raise ValueError("A name containing letters is required.")
    if len(name) > 120:
        raise ValueError("Name is too long (max 120 characters).")

    identity = {
        "id": "user:" + "".join(c for c in name.lower() if c.isalnum())[:40],
        "text": name,
    }
    birth = _validated_birth(payload.get("birth"))
    if birth:
        identity["birth"] = birth
    psychology = payload.get("psychology") or None
    if psychology:
        identity["psychology"] = psychology

    sig = compute_unified_signature(identity)
    defaults = get_defaults()
    uv = feature_vector(sig)
    comps = [{
        "id": d["id"], "text": d["text"],
        "resonance": d["resonance"]["score"],
        "agreement": round(feature_agreement(uv, feature_vector(d)), 4),
    } for d in defaults]
    comps.sort(key=lambda c: -c["agreement"])
    corr = cross_encoder_correlations(defaults + [sig])
    report = generate_report(sig, psychology=psychology, comparisons=comps)
    return {
        "signature": sig,
        "comparison_metric": FEATURE_AGREEMENT_METRIC,
        "comparisons": comps[:10],
        "correlations": corr,
        "report": report,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "IdentityResonance/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] %s\n" % (fmt % args))

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if ctype.startswith("application/json") else "max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        body = json.dumps(_safe_json(obj), ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            get_defaults()
            return self._json(200, {"ok": True, "reference_count": len(_DEFAULTS), "reference_errors": _DEFAULT_ERRORS})
        if path == "/api/defaults":
            return self._json(200, {"identities": default_summaries()})
        if path == "/":
            path = "/index.html"
        fs_path = os.path.realpath(os.path.join(STATIC, path.lstrip("/")))
        static_root = os.path.realpath(STATIC) + os.sep
        if not fs_path.startswith(static_root) or not os.path.isfile(fs_path):
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        with open(fs_path, "rb") as handle:
            self._send(200, handle.read(), MIME.get(os.path.splitext(fs_path)[1], "application/octet-stream"))

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/analyze":
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0:
                raise ValueError("Request body is empty.")
            if length > 64 * 1024:
                return self._json(413, {"error": "Payload too large."})
            payload = json.loads(self.rfile.read(length))
            return self._json(200, analyze(payload))
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception as exc:
            traceback.print_exc()
            return self._json(500, {"error": "Analysis failed.", "detail": str(exc) if os.environ.get("DEBUG") == "1" else None})


def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"Warming public reference population ({len(PUBLIC_REFERENCE_IDENTITIES)} identities)...")
    get_defaults()
    print(f"Loaded {len(_DEFAULTS)} references; {len(_DEFAULT_ERRORS)} failed.")
    print(f"Identity Resonance running on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
