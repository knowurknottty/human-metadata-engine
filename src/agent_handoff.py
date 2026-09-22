"""Versioned, redacted semantic capsules for Human Manual exports."""
from __future__ import annotations

from copy import deepcopy

AGENT_HANDOFF_VERSION = "human-manual-agent-handoff-v1"
HANDOFF_V2_VERSION = "human-manual-agent-handoff-v2"
SENSITIVE_KEYS = frozenset({
    "lat", "latitude", "lon", "lng", "longitude",
    "location", "place", "birth_place", "birthplace", "address",
    "timezone", "timezone_name", "timezone_id", "tz", "tz_id",
    "coords", "coordinates", "geo", "position",
    "observation", "observation_text", "raw_observation",
    "note", "notes", "comment", "comments", "subject_notes", "text",
})
SENSITIVE_KEY_FRAGMENTS = (
    "latitude", "longitude", "coordinate", "coords", "timezone",
    "birth_place", "birthplace", "observation", "subject_notes",
)
NORMALIZED_INPUT_EXPORT_KEYS = (
    "name", "birth_availability", "birth_available", "time_accuracy",
    "self_report_availability", "self_report_available",
    "observation_availability", "observation_available",
)
SAFE_EVIDENCE_SOURCE_PREFIXES = ("signature.encoders.", "signature.systems.")


def _normalized_key(key: str) -> str:
    return key.casefold().replace("-", "_").replace(" ", "_")


def _is_sensitive_key(key: str) -> bool:
    normalized = _normalized_key(key)
    if normalized in SENSITIVE_KEYS:
        return True
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def _safe(value):
    """Recursively remove fields whose schema keys are explicitly sensitive."""
    if isinstance(value, dict):
        return {
            key: _safe(item)
            for key, item in value.items()
            if not _is_sensitive_key(str(key))
        }
    if isinstance(value, list):
        return [_safe(item) for item in value]
    return value


def _normalized_input_projection(normalized: dict) -> dict:
    """Export only reviewed descriptors; arbitrary normalized-input fields never transit v2."""
    return {
        key: deepcopy(normalized[key])
        for key in NORMALIZED_INPUT_EXPORT_KEYS
        if key in normalized
    }


def _source_path_is_safe(path: object) -> bool:
    if not isinstance(path, str):
        return False
    lowered = path.casefold()
    if any(token in lowered for token in (
        "latitude", "longitude", "location", "timezone",
        "birth_place", "birthplace", "observation",
    )):
        return False
    return path.startswith(SAFE_EVIDENCE_SOURCE_PREFIXES)


def _evidence_projection(item: dict) -> dict:
    """Project evidence through an allowlist; include source values only from reviewed paths."""
    projected = {
        "evidence_id": item.get("evidence_id"),
        "system": item.get("system"),
        "source_path": item.get("source_path"),
        "epistemic_class": item.get("epistemic_class"),
        "mapping_provenance": item.get("mapping_provenance"),
        "independence_group": item.get("independence_group"),
        "limitations": _safe(item.get("limitations", [])),
    }
    if "source_value" in item:
        if _source_path_is_safe(item.get("source_path")):
            projected["source_value"] = _safe(deepcopy(item.get("source_value")))
        else:
            projected["source_value_excluded"] = "unreviewed_or_sensitive_source_path"
    return projected


def sanitize_nested_list(lst: list) -> list:
    """Compatibility helper retained for callers; delegates to the same schema-key policy."""
    return [_safe(item) for item in lst]


def build_handoff_v2(*, response: dict, synthesis: dict, analysis_mode: str) -> dict:
    """Build an additive manifest from already public/redacted response data only."""
    evidence_items = synthesis.get("evidence", {}).get("evidence_items", []) if synthesis.get("available", True) else []
    plan = synthesis.get("plan", {}) if synthesis.get("available", True) else {}
    normalized = response.get("normalized_input", {})
    excluded = [
        {"category": "raw_coordinates_and_location", "reason": "Public export policy redacts raw coordinates, location text, and timezone."},
        {"category": "raw_observation_text", "reason": "Public export policy redacts observation text; only explicit high-level availability may be represented."},
        {"category": "Tarot", "reason": "Tarot is a separate optional reflection and is excluded unless a user explicitly chooses to include it."},
    ]
    coverage = [
        {"category": "subject_inputs", "representation": "included", "reason": "Normalized descriptors identify supplied layers without raw sensitive values."},
        {"category": "deterministic_calculations", "representation": "included", "reason": "Returned signature and evidence records are indexed."},
        {"category": "unavailable_states", "representation": "included", "reason": "Data-quality and missing-dimension records are preserved."},
        {"category": "historical_textual_references", "representation": "included", "reason": "Evidence records retain epistemic class and provenance."},
        {"category": "traditional_interpretations", "representation": "included", "reason": "Evidence records retain epistemic class and limitations."},
        {"category": "project_authored_interpretations", "representation": "included", "reason": "Narrative plan and evidence-linked narratives are represented."},
        {"category": "explicit_observations", "representation": "excluded", "reason": "Raw observation text is redacted by policy."},
        {"category": "contradictions", "representation": "included", "reason": "Plan contradiction records are retained."},
        {"category": "source_provenance", "representation": "included", "reason": "Evidence index retains source paths, epistemic class, and limits."},
    ]
    return {
        "schema_version": HANDOFF_V2_VERSION,
        "analysis_mode": analysis_mode,
        "subject_inputs": {"normalized_input": _normalized_input_projection(normalized), "included": ["name", "birth availability", "self-report availability"], "intentionally_excluded": excluded},
        "deterministic_replay": {"input_hash": response.get("input_hash"), "engine_version": response.get("engine_version"), "build_revision": response.get("build_revision"), "synthesis_versions": synthesis.get("versions", {})},
        "unavailable_calculations": _safe({"data_quality": synthesis.get("evidence", {}).get("data_quality", {}), "missing_or_uncertain_dimensions": plan.get("missing_or_uncertain_dimensions", [])}),
        "evidence_index": [_evidence_projection(item) for item in evidence_items],
        "contradictions": _safe(plan.get("contradictions", []) or ([plan.get("originating_tension")] if plan.get("originating_tension") else [])),
        "dependence_families": sorted({item.get("independence_group") for item in evidence_items if item.get("independence_group")}),
        "uncertainty_limitations": sorted({limit for item in evidence_items for limit in item.get("limitations", [])}),
        "redaction_rules": {"raw_coordinates_location_timezone": "redacted", "raw_observation_text": "redacted", "policy": response.get("privacy", {}).get("response_redaction")},
        "prohibited_inference_classes": ["diagnosis", "prediction", "destiny", "compatibility_score", "relationship_quality", "social_surveillance", "empirical_validation_from_symbolic_recurrence"],
        "source_provenance_index": [{"evidence_id": item.get("evidence_id"), "source_path": item.get("source_path"), "epistemic_class": item.get("epistemic_class")} for item in evidence_items],
        "public_response_coverage": coverage + [{"category": item["category"], "representation": "excluded", "reason": item["reason"]} for item in excluded],
    }


def handoff_v2_markdown(manifest: dict) -> str:
    coverage = manifest["public_response_coverage"]
    lines = [
        "## Agent Handoff v2 — semantic capsule", "", f"- Handoff contract: `{HANDOFF_V2_VERSION}`", f"- Analysis mode: `{manifest['analysis_mode']}`", "",
        "### What will be shared", "",
    ]
    lines.extend(f"- **{item['category'].replace('_', ' ').title()}** — {item['representation']}: {item['reason']}" for item in coverage)
    lines += ["", "### Instructions for the receiving agent", "", "1. Treat material explicitly labeled **Supplied by you**, **Calculated**, **Historical/textual reference**, **Traditional interpretation**, and **Project-authored interpretation** as distinct classes.", "2. Preserve unavailable states, contradictions, dependence families, and limitations; do not fill them with plausible prose.", "3. Do not infer diagnosis, prediction, destiny, compatibility, relationship quality, social facts, or empirical validation from symbolic recurrence.", "4. Raw coordinates, location, timezone, and observation text were intentionally redacted. Do not reconstruct them.", "5. This manifest is a loss-resistant export capsule, not proof about a person.", ""]
    return "\n".join(lines)


def agent_handoff_markdown(*, analysis_mode: str, synthesis_available: bool) -> str:
    narrative_note = "The deterministic Living Pattern is included above and may be rewritten stylistically, but its evidence links and limitations remain authoritative." if synthesis_available else "Narrative synthesis was disabled for this Data-mode export; work only from the structured material present above."
    return "\n".join(["## Agent Handoff — tell this story in another voice", "", f"- Handoff contract: `{AGENT_HANDOFF_VERSION}`", f"- Analysis mode: `{analysis_mode}`", "", "This Markdown file is intentionally formatted for a favorite agent, local model, or other assistant to digest without needing access to this application.", narrative_note, "", "### Instructions for the receiving agent", "", "1. Treat the material above as the supplied record. Do not silently replace calculations, source values, or provenance with your own assumptions.", "2. Keep calculated, historical, user-supplied, traditional, and project-authored material visibly distinct.", "3. Do not invent missing personal facts, birth details, observations, diagnoses, motives, memories, relationships, or biographical events.", "4. Preserve contradictions instead of forcing every system into agreement. Different maps are allowed to disagree.", "5. You may make the prose vivid, funny, intimate, lyrical, technical, or story-like, but clearly mark any new interpretation as your own narration.", "6. Do not turn symbolic material into prediction, diagnosis, certainty, spiritual rank, or a claim that a system has scientifically measured the person.", "7. Prefer specific examples already present in the file. When no example exists, ask the human for one rather than manufacturing it.", "8. Keep provenance and limitations available even when simplifying the explanation for a nontechnical reader.", ""])
