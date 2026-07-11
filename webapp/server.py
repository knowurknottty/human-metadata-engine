#!/usr/bin/env python3
"""Identity Resonance web server: API, validation, and static assets."""

import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "src"))

from engine import compute_unified_signature, IDENTITIES  # noqa: E402
from analytics import feature_vector, cosine_similarity, cross_encoder_correlations  # noqa: E402
from analytics_v2 import composite_resonance  # noqa: E402
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
from report_safe import generate_report  # noqa: E402
from snapshot import personality_snapshot  # noqa: E402

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
    """Validate a living person's birth data at the public API boundary."""
    return validate_birth(raw, living_person=True)


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


def _compute_signature(identity):
    """Compute a signature and apply the corrected public scoring contract."""
    signature = compute_unified_signature(identity)
    _disable_unvalidated_human_design(signature, identity)
    signature["resonance"] = composite_resonance(signature)
    return signature


def get_defaults():
    global _DEFAULTS, _DEFAULT_ERRORS
    if _DEFAULTS is None:
        _DEFAULTS, _DEFAULT_ERRORS = [], []
        for ident in IDENTITIES:
            try:
                _DEFAULTS.append(_compute_signature(_normalized_reference(ident)))
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
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("observations must be an array.")
    if len(raw) > 100:
        raise ValueError("observations supports at most 100 entries.")
    observations = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"observations[{index}] must be an object.")
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"observations[{index}].text must be a non-empty string.")
        observations.append({
            "text": text.strip(),
            "source": item.get("source", "user_supplied"),
            "confidence": item.get("confidence", "unrated"),
            "occurred_at": item.get("occurred_at"),
        })
    return observations


def _constellation_analysis(graph, analysis_year):
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
                identity["psychology"] = node["psychology"]

        signature = _compute_signature(identity)
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
    name = (payload.get("name") or "").strip()
    if not name or not any(ch.isalpha() for ch in name):
        raise ValueError("A name containing letters is required.")
    if len(name) > 120:
        raise ValueError("Name is too long (max 120 characters).")

    analysis_year = datetime.now(timezone.utc).year
    identity = {
        "id": "user:" + "".join(c for c in name.lower() if c.isalnum())[:40],
        "text": name,
        "as_of_year": analysis_year,
    }
    birth = _validated_birth(payload.get("birth"))
    if birth:
        identity["birth"] = birth
    psychology = payload.get("psychology") or None
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

    sig = _compute_signature(identity)
    sig["normalized_input"] = {
        "name": name,
        "birth": canonical_birth_record(birth),
        "analysis_year": analysis_year,
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
    constellation_result = _constellation_analysis(constellation, analysis_year)

    defaults = get_defaults()
    uv = feature_vector(sig)
    comps = [{
        "id": d["id"], "text": d["text"],
        "resonance": d["resonance"]["score"],
        "similarity": round(cosine_similarity(uv, feature_vector(d)), 4),
    } for d in defaults]
    comps.sort(key=lambda c: -c["similarity"])
    corr = cross_encoder_correlations(defaults + [sig])
    report = generate_report(sig, psychology=psychology, comparisons=comps)
    return {
        "signature": sig,
        "comparisons": comps[:10],
        "correlations": corr,
        "report": report,
        "normalized_input": sig["normalized_input"],
        "etymology": etymology,
        "evidence": evidence,
        "observations": observations,
        "constellation": constellation_result,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "IdentityResonance/1.3"

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
        except (
            BirthValidationError,
            ConstellationValidationError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception as exc:
            traceback.print_exc()
            return self._json(500, {"error": "Analysis failed.", "detail": str(exc) if os.environ.get("DEBUG") == "1" else None})


def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"Warming reference population ({len(IDENTITIES)} identities)...")
    get_defaults()
    print(f"Loaded {len(_DEFAULTS)} references; {len(_DEFAULT_ERRORS)} failed.")
    print(f"Identity Resonance running on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
