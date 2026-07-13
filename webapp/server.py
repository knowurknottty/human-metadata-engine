#!/usr/bin/env python3
"""Identity Resonance web server: API, validation, and static assets."""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
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

from engine import (  # noqa: E402
    available_encoder_names,
    compute_unified_signature,
    count_signature_dimensions,
)
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
    validate_birth_datetime_fields,
)
from constellation import (  # noqa: E402
    ConstellationValidationError,
    connection_summary,
    validate_constellation,
)
from etymology import analyze_name_etymology  # noqa: E402
from evidence_v3 import evidence_dashboard  # noqa: E402
from encoders.pipeline import MANIFEST_VERSION as CONVENTION_SET_VERSION  # noqa: E402
from sigil import generate_custom_sigil  # noqa: E402
from snapshot import personality_snapshot  # noqa: E402
from true_human_design.public_adapter import calculate_public_human_design  # noqa: E402
from location_resolution import (  # noqa: E402
    LocationResolutionError,
    resolve_birth_location,
    resolve_local_datetime,
)
from public_contract import (  # noqa: E402
    PublicContractError,
    normalize_public_name,
    validate_aliases,
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
APP_VERSION = "0.7.0"
SCHEMA_VERSION = "analysis-v1"
ENGINE_VERSION = "signature-v2"


def _build_revision() -> str:
    configured = os.environ.get("HME_BUILD_REVISION", "").strip()
    if configured and configured != "unknown":
        return configured[:64] if re.fullmatch(r"[A-Za-z0-9._-]+", configured) else "unknown"
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
            timeout=1,
        )
        revision = completed.stdout.strip()
        return revision if re.fullmatch(r"[0-9a-f]{7,40}", revision) else "unknown"
    except (FileNotFoundError, subprocess.SubprocessError):
        return "unknown"


BUILD_REVISION = _build_revision()
try:
    import swisseph as _swisseph  # type: ignore
except ImportError:
    _swisseph = None
EPHEMERIS_AVAILABLE = _swisseph is not None
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("HME_REQUEST_TIMEOUT_SECONDS", "15"))
MAX_REQUEST_BYTES = 64 * 1024
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("HME_RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_REQUESTS = int(os.environ.get("HME_RATE_LIMIT_REQUESTS", "20"))
RATE_LIMIT_MAX_TRACKED_IPS = int(os.environ.get("HME_RATE_LIMIT_MAX_TRACKED_IPS", "10000"))
MAX_CONCURRENT_ANALYSES = int(os.environ.get("HME_MAX_CONCURRENT_ANALYSES", "4"))
MAX_CONNECTIONS = int(os.environ.get("HME_MAX_CONNECTIONS", "64"))
TRUST_PROXY_HEADERS = os.environ.get("HME_TRUST_PROXY_HEADERS", "").lower() in {"1", "true", "yes"}
if min(RATE_LIMIT_WINDOW_SECONDS, RATE_LIMIT_REQUESTS, RATE_LIMIT_MAX_TRACKED_IPS, MAX_CONCURRENT_ANALYSES, MAX_CONNECTIONS) < 1:
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

ANALYSIS_REQUEST_FIELDS = {
    "name", "aliases", "mode", "subject_type", "as_of_year", "birth", "psychology",
    "user_reported_human_design_type", "lineage_surnames", "observations", "constellation",
}
PUBLIC_BIRTH_FIELDS = {
    "year", "month", "day", "hour", "minute", "time_accuracy", "location",
    "lat", "lon", "timezone_name", "timezone_offset",
}


class HTTPRequestError(ValueError):
    def __init__(self, message: str, *, code: str, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def _error_payload(exc: Exception, *, code: str = "invalid_request") -> dict:
    error_code = getattr(exc, "code", code)
    payload = {"error": str(exc), "code": error_code, "message": str(exc)}
    if isinstance(exc, LocationResolutionError):
        details = exc.details()
        if details:
            payload["details"] = details
    return payload


def _safe_request_log(method: str, target: str, status: object) -> str:
    """Format a request log without query parameters or request bodies."""
    clean_method = method if method in {"GET", "HEAD", "POST", "OPTIONS"} else "OTHER"
    path = target.split("?", 1)[0][:256]
    return f"[web] {clean_method} {path} {status}"


def _version_payload() -> dict:
    return {
        "application_version": APP_VERSION,
        "schema_version": SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "git_commit": BUILD_REVISION,
        "ephemeris": {
            "available": EPHEMERIS_AVAILABLE,
            "library": "pyswisseph" if EPHEMERIS_AVAILABLE else None,
            "version": getattr(_swisseph, "__version__", None),
        },
        "feature_flags": {
            "location_resolution": True,
            "historical_timezone": True,
            "demo_checkout": False,
            "persistence": False,
        },
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
    "latitude", "longitude", "timezone_offset", "timezone_name", "coordinates", "coord",
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
    available_layers = available_encoder_names(signature)
    return {
        "available_layers": available_layers,
        "narrative": (
            "Data mode reports reproducible string measurements and configured "
            "calculation outputs. It does not infer personality, fate, identity, "
            "or real-world similarity from a name."
        ),
        "highlights": [
            f"{len(available_layers)} encoder outputs available",
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


def _resolve_birth_location(raw, *, living_person: bool = True):
    """Resolve or verify public chart coordinates and historical timezone."""
    if raw in (None, {}):
        return raw
    if not isinstance(raw, dict):
        return raw
    unsupported = sorted(set(raw) - PUBLIC_BIRTH_FIELDS)
    if unsupported:
        raise BirthValidationError(
            "Birth data contains unsupported fields: " + ", ".join(unsupported) + "."
        )
    for field in ("year", "month", "day"):
        if isinstance(raw.get(field), bool) or not isinstance(raw.get(field), int):
            raise BirthValidationError(f"Birth {field} must be a JSON integer.")
    for field in ("hour", "minute"):
        if field in raw and (isinstance(raw[field], bool) or not isinstance(raw[field], int)):
            raise BirthValidationError(f"Birth {field} must be a JSON integer.")
    if raw.get("time_accuracy") == "provided":
        raise BirthValidationError(
            "Public birth data must label time_accuracy as unknown, hour_only, approximate, or exact."
        )
    clock = validate_birth_datetime_fields(raw, living_person=living_person)
    enriched = dict(raw)
    timezone_name = enriched.get("timezone_name")
    explicit_offset = enriched.get("timezone_offset") not in (None, "")
    latitude_present = enriched.get("lat") not in (None, "")
    longitude_present = enriched.get("lon") not in (None, "")
    if latitude_present != longitude_present:
        raise BirthValidationError("Latitude and longitude must be supplied together.")
    has_coordinates = latitude_present and longitude_present

    if timezone_name not in (None, ""):
        local, _ = resolve_local_datetime(str(timezone_name), **{
            field: clock[field] for field in ("year", "month", "day", "hour", "minute")
        })
        derived_offset = local.utcoffset()
        if derived_offset is None:
            raise LocationResolutionError(
                "The supplied timezone has no UTC offset for the birth date.",
                code="invalid_timezone",
            )
        derived_hours = derived_offset.total_seconds() / 3600.0
        if explicit_offset:
            try:
                supplied_hours = float(enriched["timezone_offset"])
            except (TypeError, ValueError) as exc:
                raise BirthValidationError("UTC offset must be numeric.") from exc
            if abs(supplied_hours - derived_hours) > 1e-9:
                raise BirthValidationError(
                    "The supplied UTC offset conflicts with the IANA timezone for that birth date and local time."
                )
            enriched["timezone_reliability"] = "verified_iana"
        else:
            enriched["timezone_offset"] = derived_hours
            enriched["timezone_reliability"] = "resolved_iana"

    # Explicit coordinates plus an IANA timezone intentionally bypass the
    # external geocoder. Their historical offset was derived above.
    if has_coordinates and enriched.get("timezone_offset") not in (None, ""):
        enriched.setdefault(
            "timezone_reliability",
            "offset_only_unverified" if not timezone_name else "verified_iana",
        )
        enriched.setdefault("resolution_source", "manual")
        return enriched

    location = enriched.get("location")
    if location in (None, ""):
        return enriched
    resolved = resolve_birth_location(
        location,
        year=clock["year"],
        month=clock["month"],
        day=clock["day"],
        hour=clock["hour"],
        minute=clock["minute"],
    )
    if timezone_name not in (None, "") and str(timezone_name) != resolved.timezone_name:
        raise BirthValidationError("The supplied timezone conflicts with the resolved birth location.")
    if explicit_offset and abs(float(enriched["timezone_offset"]) - resolved.utc_offset_hours) > 1e-9:
        raise BirthValidationError("The supplied UTC offset conflicts with the resolved birth location.")
    if has_coordinates:
        if (
            abs(float(enriched["lat"]) - resolved.latitude) > 0.25
            or abs(float(enriched["lon"]) - resolved.longitude) > 0.25
        ):
            raise BirthValidationError("The supplied coordinates conflict with the resolved birth location.")
    enriched.update({
        "location": resolved.display_name,
        "timezone_offset": resolved.utc_offset_hours,
        "lat": resolved.latitude,
        "lon": resolved.longitude,
        "timezone_name": resolved.timezone_name,
        "timezone_reliability": "resolved_iana",
        "resolution_source": resolved.resolution_source,
    })
    return enriched


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
    """Replace unsupported Human Design conclusions with an unavailable envelope.

    This function intentionally does not build a personality snapshot. The
    public pipeline computes its final snapshot once, after this sanitization.
    """
    encoders = signature.setdefault("encoders", {})
    previous = encoders.get("human_design")

    # Preserve the versioned public core result.  The legacy calculator is not
    # allowed to overwrite or downgrade a chart produced by this adapter.
    if (
        isinstance(previous, dict)
        and previous.get("available") is True
        and previous.get("status") == "provisional_calculation"
    ):
        signature.setdefault("invalidated_dimensions", {})["human_design"] = 0
        return
    if isinstance(previous, dict) and previous.get("status") == "unavailable_uncertain_birth_time":
        signature.setdefault("invalidated_dimensions", {})["human_design"] = 0
        return

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

def _compute_signature(identity, *, mode: str = "data"):
    """Compute a signature and apply the corrected public scoring contract."""
    signature = compute_unified_signature(
        identity,
        resonance_fn=accuracy_composite_resonance,
        snapshot_fn=None,
        human_design_fn=calculate_public_human_design,
    )
    _disable_unvalidated_human_design(signature, identity)
    if mode == "data":
        signature["snapshot"] = _data_snapshot(signature, psychology=identity.get("psychology"))
    else:
        signature["snapshot"] = personality_snapshot(
            identity["text"],
            astrology=signature["encoders"].get("astrology"),
            human_design=signature["encoders"].get("human_design"),
            psychology=identity.get("psychology"),
        )
        signature["snapshot"]["mode"] = "magic"
    signature["computed_dimensions"] = count_signature_dimensions(signature)
    signature["dimensions"] = count_signature_dimensions(signature, include_unavailable=True)
    signature["analysis_mode"] = mode
    return signature


def _alias_summaries(aliases: list[str], analysis_year: int) -> list[dict]:
    """Return bounded calculations for aliases without duplicating full reports."""
    summaries = []
    for index, alias in enumerate(aliases):
        signature = _compute_signature({
            "id": f"user-alias:{index}",
            "text": alias,
            "as_of_year": analysis_year,
        }, mode="data")
        encoders = signature["encoders"]
        summaries.append({
            "name": alias,
            "category": "traditional_symbolic",
            "deterministic": True,
            "scientific_validation": "not_established",
            "calculations": {
                "pythagorean_expression": encoders["pythagorean"]["expression"],
                "chaldean_name_number": encoders["chaldean"]["name_number"],
                "ordinal_total": encoders["ordinal"]["ordinal_total"],
            },
            "fingerprint": signature["fingerprint"],
            "pattern_convergence": signature["resonance"],
        })
    return summaries


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
    unknown_fields = sorted(set(payload) - ANALYSIS_REQUEST_FIELDS)
    if unknown_fields:
        raise PublicContractError(
            "Request contains unsupported fields: " + ", ".join(unknown_fields) + "."
        )
    mode = validate_mode(payload.get("mode"))
    subject_type = validate_subject_type(payload.get("subject_type"))
    name = normalize_public_name(payload.get("name"))
    aliases = validate_aliases(payload.get("aliases"), primary_name=name)

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
    raw_birth = _resolve_birth_location(raw_birth, living_person=subject_type == "self")
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
        "aliases": aliases,
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
    request_fingerprint = _input_hash({
        "name": name,
        "aliases": aliases,
        "birth": birth,
        "psychology": psychology,
        "mode": mode,
        "subject_type": subject_type,
        "as_of_year": requested_year,
        "lineage_surnames": lineage_surnames,
        "observations": observations,
        "constellation": constellation,
    })
    report = generate_report(sig, psychology=psychology, comparisons=comps, mode=mode)
    report["metadata"] = {
        "report_schema_version": "report-v1",
        "analysis_schema_version": SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "convention_set_version": CONVENTION_SET_VERSION,
        "build_revision": BUILD_REVISION,
        "reproducibility_id": request_fingerprint,
    }
    report["markdown"] = report["markdown"].replace(
        "\n",
        (
            f"\n\n> Report schema `report-v1` · engine `{ENGINE_VERSION}` · "
            f"conventions `{CONVENTION_SET_VERSION}` · build `{BUILD_REVISION}` · "
            f"reproduction `{request_fingerprint}`\n"
        ),
        1,
    )
    report["word_count"] = len(report["markdown"].split())
    response = {
        "contract_version": SCHEMA_VERSION,
        "build_revision": BUILD_REVISION,
        "engine_version": ENGINE_VERSION,
        "analysis_mode": mode,
        "subject_type": subject_type,
        "input_hash": request_fingerprint,
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
        "psychology": psychology,
        "aliases": _alias_summaries(aliases, requested_year),
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
        status = args[1] if len(args) > 1 else "-"
        sys.stderr.write(_safe_request_log(self.command, self.path, status) + "\n")

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
        content_type = (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise HTTPRequestError(
                "Content-Type must be application/json.", code="invalid_content_type", status=415
            )
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or 0)
        except ValueError as exc:
            raise HTTPRequestError(
                "Content-Length must be an integer.", code="invalid_content_length"
            ) from exc
        if length <= 0:
            raise HTTPRequestError("Request body is empty.", code="empty_request_body")
        if length > max_bytes:
            raise HTTPRequestError("Payload too large.", code="payload_too_large", status=413)
        body = self.rfile.read(length)
        if len(body) != length:
            raise HTTPRequestError("Request body was truncated.", code="truncated_request_body")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise HTTPRequestError(
                f"Invalid JSON: {exc.msg}.", code="invalid_json"
            ) from exc
        return payload

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            return self._json(200, {
                "ok": True,
                "status": "alive",
                "application_version": APP_VERSION,
            })
        if path in {"/api/health", "/readyz"}:
            get_defaults()
            ready = EPHEMERIS_AVAILABLE and bool(_DEFAULTS) and not _DEFAULT_ERRORS
            return self._json(200 if ready else 503, {
                "ok": ready,
                "ready": ready,
                "version": APP_VERSION,
                "build_revision": BUILD_REVISION,
                "ephemeris_available": EPHEMERIS_AVAILABLE,
                "reference_count": len(_DEFAULTS),
                "reference_errors": [{"id": item.get("id"), "error": item.get("error")} for item in _DEFAULT_ERRORS],
            })
        if path == "/api/version":
            return self._json(200, _version_payload())
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
                {"error": "Too many analysis requests. Please try again shortly.",
                 "message": "Too many analysis requests. Please try again shortly.",
                 "code": "rate_limited"},
                {"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        if not _ANALYSIS_SLOTS.acquire(blocking=False):
            return self._json(429, {
                "error": "Analysis service is busy. Please try again shortly.",
                "message": "Analysis service is busy. Please try again shortly.",
                "code": "service_busy",
            })
        try:
            payload = self._read_json_body()
            return self._json(200, analyze(payload))
        except HTTPRequestError as exc:
            return self._json(exc.status, _error_payload(exc))
        except LocationResolutionError as exc:
            return self._json(400, _error_payload(exc))
        except (
            BirthValidationError,
            ConstellationValidationError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return self._json(400, _error_payload(exc))
        except Exception:
            traceback.print_exc()
            return self._json(500, {
                "error": "Analysis failed.",
                "message": "Analysis failed.",
                "code": "internal_error",
            })
        finally:
            _ANALYSIS_SLOTS.release()

    def _post_sigil(self):
        """Render one bounded public sigil without exposing the full signature."""
        client_ip = _rate_limit_client_ip(self.client_address[0], self.headers)
        if not _allow_analysis(client_ip):
            return self._json(
                429,
                {"error": "Too many sigil requests. Please try again shortly.",
                 "message": "Too many sigil requests. Please try again shortly.",
                 "code": "rate_limited"},
                {"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        if not _ANALYSIS_SLOTS.acquire(blocking=False):
            return self._json(429, {
                "error": "Sigil service is busy. Please try again shortly.",
                "message": "Sigil service is busy. Please try again shortly.",
                "code": "service_busy",
            })
        try:
            payload = self._read_json_body(max_bytes=8 * 1024)
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            return self._json(200, generate_custom_sigil(payload.get("text"), size=payload.get("size", 360)))
        except HTTPRequestError as exc:
            return self._json(exc.status, _error_payload(exc))
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, _error_payload(exc))
        finally:
            _ANALYSIS_SLOTS.release()


class BoundedThreadingHTTPServer(ThreadingHTTPServer):
    """Threaded server with a hard connection ceiling and daemon workers."""

    daemon_threads = True
    request_queue_size = 64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_slots = BoundedSemaphore(MAX_CONNECTIONS)

    def process_request(self, request, client_address):
        if not self.connection_slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.connection_slots.release()


def main():
    if not EPHEMERIS_AVAILABLE:
        raise SystemExit(
            "Swiss Ephemeris is required. Install the pinned requirements before starting the server."
        )
    port = int(os.environ.get("PORT", 8000))
    bind_host = os.environ.get("HME_BIND_HOST", "127.0.0.1")
    print(f"Warming public reference population ({len(PUBLIC_REFERENCE_IDENTITIES)} identities)...")
    get_defaults()
    print(f"Loaded {len(_DEFAULTS)} references; {len(_DEFAULT_ERRORS)} failed.")
    print(f"Identity Resonance running on http://{bind_host}:{port}")
    server = BoundedThreadingHTTPServer((bind_host, port), Handler)
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
