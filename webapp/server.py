#!/usr/bin/env python3
"""Identity Resonance web server: API, validation, and static assets."""

import json
import math
import os
import sys
import traceback
import hashlib
import unicodedata
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from threading import BoundedSemaphore, Lock
from time import monotonic

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "src"))

from engine import compute_unified_signature  # noqa: E402
from analytics import (  # noqa: E402
    FEATURE_AGREEMENT_METRIC,
    cosine_similarity,
    cross_encoder_correlations,
    feature_agreement,
    feature_vector,
)
from analytics_v2 import composite_resonance as accuracy_composite_resonance  # noqa: E402
from report_safe import generate_report  # noqa: E402
from reference_population import famous_reference_identities  # noqa: E402
from birth_validation import (  # noqa: E402
    BirthValidationError,
    canonical_birth_record,
    validate_birth,
)
from constellation import (  # noqa: E402
    ConstellationValidationError,
    connection_summary,
    validate_constellation,
)
from etymology import analyze_name_etymology  # noqa: E402
from evidence_v3 import evidence_dashboard  # noqa: E402
from sigil import generate_custom_sigil  # noqa: E402
from snapshot import personality_snapshot  # noqa: E402
from public_contract import (  # noqa: E402
    PublicContractError,
    normalize_public_name,
    validate_mode,
    validate_observations,
    validate_psychology,
    validate_subject_type,
)

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
_DEFAULTS_LOCK = Lock()
PUBLIC_REFERENCE_IDENTITIES = famous_reference_identities()
APP_VERSION = "0.6.0"
BUILD_REVISION = os.environ.get("HME_BUILD_REVISION", "unknown")
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("HME_REQUEST_TIMEOUT_SECONDS", "15"))
MAX_REQUEST_BYTES = 64 * 1024
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("HME_RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_REQUESTS = int(os.environ.get("HME_RATE_LIMIT_REQUESTS", "20"))
RATE_LIMIT_MAX_TRACKED_IPS = int(os.environ.get("HME_RATE_LIMIT_MAX_TRACKED_IPS", "10000"))
MAX_CONCURRENT_ANALYSES = int(os.environ.get("HME_MAX_CONCURRENT_ANALYSES", "4"))
TRUST_PROXY_HEADERS = os.environ.get("HME_TRUST_PROXY_HEADERS", "").lower() in {"1", "true", "yes"}
if min(RATE_LIMIT_WINDOW_SECONDS, RATE_LIMIT_REQUESTS, RATE_LIMIT_MAX_TRACKED_IPS, MAX_CONCURRENT_ANALYSES) < 1:
    raise RuntimeError("HME rate-limit and concurrency settings must be positive integers.")
_RATE_LIMIT_LOCK = Lock()
_RECENT_ANALYSES: dict[str, deque[float]] = {}
_ANALYSIS_SLOTS = BoundedSemaphore(MAX_CONCURRENT_ANALYSES)
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; base-uri 'self'; form-action 'self'; "
        "frame-ancestors 'none'; object-src 'none'; img-src 'self' data: blob:; "
        "font-src 'self' data:; connect-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=(), payment=()",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Cross-Origin-Resource-Policy": "same-origin",
}


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
    # Unknown objects must not be stringified into an accidental data leak.
    return None


_SENSITIVE_OUTPUT_KEYS = {
    "birth", "birth_data", "birth_location", "location", "lat", "lon",
    "latitude", "longitude", "timezone_offset", "coordinates", "coord",
}


def _redact_public_output(value, key: str | None = None):
    """Remove raw location/birth fields before returning a public response."""
    if isinstance(value, dict):
        result = {}
        for child_key, child_value in value.items():
            normalized = str(child_key).lower()
            if normalized in _SENSITIVE_OUTPUT_KEYS and key != "normalized_input":
                continue
            if normalized == "text" and key == "observations":
                continue
            result[child_key] = _redact_public_output(child_value, normalized)
        return result
    if isinstance(value, list):
        return [_redact_public_output(item, key) for item in value]
    return value


def _input_hash(payload: dict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def _data_snapshot(signature: dict, psychology: dict | None = None) -> dict:
    """A non-interpretive snapshot for Data mode."""
    encoders = signature.get("encoders", {})
    return {
        "available_layers": [
            key for key, value in encoders.items()
            if isinstance(value, dict) and not value.get("error") and value.get("available", True) is not False
        ],
        "narrative": (
            "Data mode reports reproducible string measurements and configured "
            "calculation outputs. It does not infer personality, fate, identity, "
            "or real-world similarity from a name."
        ),
        "highlights": [
            f"{len(encoders)} encoder outputs available",
            "raw input is not retained by this process",
            "interpretive claims are disabled in Data mode",
        ],
        "mode": "data",
        "psychology_present": bool(psychology),
    }


def _validated_birth(raw):
    """Validate a living person's birth data at the public API boundary."""
    if isinstance(raw, dict) and "time_accuracy" not in raw:
        raw = {**raw, "time_accuracy": "unknown"}
    return validate_birth(raw, living_person=True, require_coordinates=True)


def _allow_analysis(client_ip: str, now: float | None = None) -> bool:
    """Apply a bounded, process-local sliding-window rate limit per IP."""
    current = monotonic() if now is None else now
    cutoff = current - RATE_LIMIT_WINDOW_SECONDS
    with _RATE_LIMIT_LOCK:
        for ip, timestamps in list(_RECENT_ANALYSES.items()):
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if not timestamps:
                del _RECENT_ANALYSES[ip]
        timestamps = _RECENT_ANALYSES.get(client_ip)
        if timestamps is None:
            if len(_RECENT_ANALYSES) >= RATE_LIMIT_MAX_TRACKED_IPS:
                return False
            timestamps = _RECENT_ANALYSES[client_ip] = deque()
        if len(timestamps) >= RATE_LIMIT_REQUESTS:
            return False
        timestamps.append(current)
        return True


def _rate_limit_client_ip(peer_ip: str, headers, trust_proxy: bool = TRUST_PROXY_HEADERS) -> str:
    """Use a proxy-supplied IP only after direct public ingress is closed."""
    if trust_proxy and peer_ip in {"127.0.0.1", "::1"}:
        for header_name in ("CF-Connecting-IP", "X-Forwarded-For"):
            candidate = (headers.get(header_name) or "").split(",", 1)[0].strip()
            try:
                return str(ip_address(candidate))
            except ValueError:
                continue
    return peer_ip


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


def _disable_unvalidated_human_design(signature, identity):
    """Remove unsupported Human Design conclusions from public output."""
    encoders = signature.setdefault("encoders", {})
    previous = encoders.get("human_design")

    removed_dimensions = 0
    if (
        isinstance(previous, dict)
        and previous
        and not previous.get("error")
        and previous.get("type")
    ):
        removed_dimensions = 15
        signature["dimensions"] = max(
            0,
            int(signature.get("dimensions", 0)) - removed_dimensions,
        )

    signature.setdefault("invalidated_dimensions", {})["human_design"] = removed_dimensions
    encoders["human_design"] = {
        "available": False,
        "status": "disabled_failed_validation",
        "unavailable": "A known birth time is required for Human Design output.",
        "reason": (
            "The legacy calculator does not derive gates, centers, type, authority, "
            "profile, or design time using validated Human Design mechanics."
        ),
        "previous_result_removed": bool(previous),
        "removed_dimension_count": removed_dimensions,
        "user_reported_type": identity.get("user_reported_human_design_type"),
        "epistemic_class": "symbolic-unavailable",
    }
    signature["snapshot"] = personality_snapshot(
        identity["text"],
        astrology=encoders.get("astrology"),
        human_design=None,
        psychology=identity.get("psychology"),
    )


def _compute_signature(identity, *, mode: str = "data"):
    """Compute a signature and apply the corrected public scoring contract."""
    signature = compute_unified_signature(identity)
    _disable_unvalidated_human_design(signature, identity)
    signature["resonance"] = accuracy_composite_resonance(signature)
    if mode == "data":
        signature["snapshot"] = _data_snapshot(signature, psychology=identity.get("psychology"))
    else:
        signature.setdefault("snapshot", {})["mode"] = "magic"
    signature["analysis_mode"] = mode
    return signature


def get_defaults():
    global _DEFAULTS, _DEFAULT_ERRORS
    if _DEFAULTS is None:
        with _DEFAULTS_LOCK:
            if _DEFAULTS is None:
                _DEFAULTS, _DEFAULT_ERRORS = [], []
                for ident in PUBLIC_REFERENCE_IDENTITIES:
                    try:
                        _DEFAULTS.append(_compute_signature(_normalized_reference(ident)))
                    except Exception as exc:
                        _DEFAULT_ERRORS.append({"id": ident.get("id"), "error": type(exc).__name__})
    return _DEFAULTS


def default_summaries():
    return [{
        "id": s["id"], "text": s["text"],
        "resonance": s["resonance"]["score"],
        "fingerprint": s["fingerprint"],
        "expression": s["encoders"]["pythagorean"]["expression"],
        "chaldean": s["encoders"]["chaldean"]["name_number"],
    } for s in get_defaults()]


def _validated_lineage_surnames(raw):
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("lineage_surnames must be an array.")
    if len(raw) > 12:
        raise ValueError("lineage_surnames supports at most 12 entries.")
    result = []
    for index, value in enumerate(raw):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"lineage_surnames[{index}] must be a non-empty string.")
        if len(value.strip()) > 120:
            raise ValueError(f"lineage_surnames[{index}] is too long.")
        result.append(value.strip())
    return result


def _validated_observations(raw):
    return validate_observations(raw)


def _constellation_analysis(graph, analysis_year, *, mode: str = "data"):
    if graph is None:
        return None

    node_results = []
    signatures = {}
    for node in graph["nodes"]:
        identity = {
            "id": f"constellation:{node['id']}",
            "text": node["name"],
            "as_of_year": analysis_year,
        }
        if node["type"] == "person":
            if node["profile_level"] in {"birth", "self_report"} and node.get("birth"):
                identity["birth"] = _validated_birth(node["birth"])
            if node["profile_level"] == "self_report" and node.get("psychology"):
                identity["psychology"] = validate_psychology(node["psychology"])

        signature = _compute_signature(identity, mode=mode)
        signatures[node["id"]] = signature
        node_etymology = analyze_name_etymology(
            node["name"],
            lineage_surnames=_validated_lineage_surnames(
                node.get("metadata", {}).get("lineage_surnames")
            ),
        )
        node_results.append({
            "id": node["id"],
            "type": node["type"],
            "name": node["name"],
            "profile_level": node["profile_level"],
            "fingerprint": signature["fingerprint"],
            "expression": signature["encoders"]["pythagorean"]["expression"],
            "chaldean": signature["encoders"]["chaldean"]["name_number"],
            "resonance": signature["resonance"],
            "etymology": node_etymology,
            "evidence": evidence_dashboard(
                signature,
                psychology=identity.get("psychology"),
                observations=None,
                etymology=node_etymology,
            ),
        })

    connections = []
    node_ids = list(signatures)
    for left_index, left_id in enumerate(node_ids):
        for right_id in node_ids[left_index + 1:]:
            left = signatures[left_id]
            right = signatures[right_id]
            similarity = round(
                cosine_similarity(feature_vector(left), feature_vector(right)), 4
            )
            left_letters = {char for char in left["text"].upper() if "A" <= char <= "Z"}
            right_letters = {char for char in right["text"].upper() if "A" <= char <= "Z"}
            connections.append({
                "source": left_id,
                "target": right_id,
                "computed_similarity": similarity,
                "shared_letters": sorted(left_letters & right_letters),
                "scope": "computed name-feature similarity; not relationship strength",
            })
    connections.sort(key=lambda item: -item["computed_similarity"])

    return {
        "graph": graph,
        "summary": connection_summary(graph),
        "nodes": node_results,
        "computed_connections": connections[:100],
    }


def analyze(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    mode = validate_mode(payload.get("mode"))
    subject_type = validate_subject_type(payload.get("subject_type"))
    name = normalize_public_name(payload.get("name"))

    analysis_year = datetime.now(timezone.utc).year
    requested_year = payload.get("as_of_year", analysis_year)
    if isinstance(requested_year, bool) or not isinstance(requested_year, int):
        raise PublicContractError("as_of_year must be an integer.")
    if not 1 <= requested_year <= analysis_year:
        raise PublicContractError(f"as_of_year must be between 1 and {analysis_year}.")
    identity = {
        "id": "user:" + "".join(c for c in name.lower() if c.isalnum())[:40],
        "text": name,
        "as_of_year": requested_year,
    }
    raw_birth = payload.get("birth")
    if isinstance(raw_birth, dict) and "time_accuracy" not in raw_birth:
        raw_birth = {**raw_birth, "time_accuracy": "unknown"}
    birth = validate_birth(
        raw_birth,
        living_person=subject_type == "self",
        require_coordinates=True,
    )
    if birth:
        identity["birth"] = birth
    psychology = validate_psychology(payload.get("psychology"))
    if psychology:
        identity["psychology"] = psychology

    reported_hd_type = payload.get("user_reported_human_design_type")
    if reported_hd_type:
        if reported_hd_type not in {
            "Manifestor", "Generator", "Manifesting Generator", "Projector", "Reflector"
        }:
            raise ValueError("Unknown user_reported_human_design_type.")
        identity["user_reported_human_design_type"] = reported_hd_type

    lineage_surnames = _validated_lineage_surnames(payload.get("lineage_surnames"))
    observations = _validated_observations(payload.get("observations"))
    constellation = validate_constellation(payload.get("constellation"))

    sig = _compute_signature(identity, mode=mode)
    sig["normalized_input"] = {
        "name": name,
        "birth": canonical_birth_record(birth),
        "analysis_year": requested_year,
        "subject_type": subject_type,
        "mode": mode,
        "lineage_surnames": lineage_surnames,
    }

    etymology = analyze_name_etymology(
        name,
        lineage_surnames=lineage_surnames,
    )
    evidence = evidence_dashboard(
        sig,
        psychology=psychology,
        observations=observations,
        etymology=etymology,
    )
    constellation_result = _constellation_analysis(constellation, requested_year, mode=mode)

    defaults = get_defaults()
    uv = feature_vector(sig)
    comps = [{
        "id": d["id"], "text": d["text"],
        "resonance": d["resonance"]["score"],
        "agreement": round(feature_agreement(uv, feature_vector(d)), 4),
    } for d in defaults]
    comps.sort(key=lambda c: -c["agreement"])
    corr = cross_encoder_correlations(defaults + [sig])
    report = generate_report(sig, psychology=psychology, comparisons=comps, mode=mode)
    response = {
        "contract_version": "analysis-v1",
        "build_revision": BUILD_REVISION,
        "engine_version": "signature-v2",
        "analysis_mode": mode,
        "subject_type": subject_type,
        "input_hash": _input_hash({
            "name": name,
            "birth": birth,
            "psychology": psychology,
            "mode": mode,
            "subject_type": subject_type,
            "as_of_year": requested_year,
            "lineage_surnames": lineage_surnames,
            "observations": observations,
            "constellation": constellation,
        }),
        "privacy": {
            "retention": "not persisted by the web process",
            "response_redaction": "raw birth coordinates, locations, and observation text are omitted",
            "warning": "network, browser, and reverse-proxy logs may still exist outside this process",
        },
        "signature": sig,
        "comparison_metric": FEATURE_AGREEMENT_METRIC,
        "comparisons": comps[:10],
        "correlations": corr,
        "report": report,
        "normalized_input": sig["normalized_input"],
        "etymology": etymology,
        "evidence": evidence,
        "observations": observations,
        "constellation": constellation_result,
    }
    return _redact_public_output(response)


class Handler(BaseHTTPRequestHandler):
    server_version = f"IdentityResonance/{APP_VERSION}"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(REQUEST_TIMEOUT_SECONDS)

    def log_message(self, fmt, *args):
        sys.stderr.write("[web] %s\n" % (fmt % args))

    def version_string(self):
        return self.server_version

    def _send(self, code, body, ctype, extra_headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if ctype.startswith("application/json") else "max-age=300")
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj, extra_headers=None):
        body = json.dumps(_safe_json(obj), ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8", extra_headers)

    def _read_json_body(self, max_bytes: int = MAX_REQUEST_BYTES):
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or 0)
        except ValueError as exc:
            raise ValueError("Content-Length must be an integer.") from exc
        if length <= 0:
            raise ValueError("Request body is empty.")
        if length > max_bytes:
            raise ValueError("Payload too large.")
        body = self.rfile.read(length)
        if len(body) != length:
            raise ValueError("Request body was truncated.")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc.msg}.") from exc
        return payload

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            get_defaults()
            ready = bool(_DEFAULTS) and not _DEFAULT_ERRORS
            return self._json(200 if ready else 503, {
                "ok": ready,
                "ready": ready,
                "version": APP_VERSION,
                "build_revision": BUILD_REVISION,
                "reference_count": len(_DEFAULTS),
                "reference_errors": [{"id": item.get("id"), "error": item.get("error")} for item in _DEFAULT_ERRORS],
            })
        if path == "/api/defaults":
            return self._json(200, {"identities": default_summaries()})
        if path == "/api/modes":
            return self._json(200, {
                "modes": [
                    {"id": "data", "label": "Data", "description": "Measurements, provenance, and cautious interpretation."},
                    {"id": "magic", "label": "Magic", "description": "Symbolic reflection with explicit non-measurement limits."},
                ],
            })
        if path == "/":
            path = "/index.html"
        fs_path = os.path.realpath(os.path.join(STATIC, path.lstrip("/")))
        static_root = os.path.realpath(STATIC) + os.sep
        if not fs_path.startswith(static_root) or not os.path.isfile(fs_path):
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        with open(fs_path, "rb") as handle:
            self._send(200, handle.read(), MIME.get(os.path.splitext(fs_path)[1], "application/octet-stream"))

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/sigil":
            return self._post_sigil()
        if path != "/api/analyze":
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        client_ip = _rate_limit_client_ip(self.client_address[0], self.headers)
        if not _allow_analysis(client_ip):
            return self._json(
                429,
                {"error": "Too many analysis requests. Please try again shortly."},
                {"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        if not _ANALYSIS_SLOTS.acquire(blocking=False):
            return self._json(429, {"error": "Analysis service is busy. Please try again shortly."})
        try:
            payload = self._read_json_body()
            return self._json(200, analyze(payload))
        except (
            BirthValidationError,
            ConstellationValidationError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            traceback.print_exc()
            return self._json(500, {"error": "Analysis failed.", "detail": None})
        finally:
            _ANALYSIS_SLOTS.release()

    def _post_sigil(self):
        """Render one bounded public sigil without exposing the full signature."""
        client_ip = _rate_limit_client_ip(self.client_address[0], self.headers)
        if not _allow_analysis(client_ip):
            return self._json(
                429,
                {"error": "Too many sigil requests. Please try again shortly."},
                {"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        if not _ANALYSIS_SLOTS.acquire(blocking=False):
            return self._json(429, {"error": "Sigil service is busy. Please try again shortly."})
        try:
            payload = self._read_json_body(max_bytes=8 * 1024)
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            return self._json(200, generate_custom_sigil(payload.get("text"), size=payload.get("size", 360)))
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        finally:
            _ANALYSIS_SLOTS.release()


def main():
    port = int(os.environ.get("PORT", 8000))
    bind_host = os.environ.get("HME_BIND_HOST", "127.0.0.1")
    print(f"Warming public reference population ({len(PUBLIC_REFERENCE_IDENTITIES)} identities)...")
    get_defaults()
    print(f"Loaded {len(_DEFAULTS)} references; {len(_DEFAULT_ERRORS)} failed.")
    print(f"Identity Resonance running on http://{bind_host}:{port}")
    server = ThreadingHTTPServer((bind_host, port), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
