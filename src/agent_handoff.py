"""Versioned, redacted semantic capsules for Human Manual exports."""
from __future__ import annotations

from copy import deepcopy

AGENT_HANDOFF_VERSION = "human-manual-agent-handoff-v1"
HANDOFF_V2_VERSION = "human-manual-agent-handoff-v2"
SENSITIVE_TOKENS = ("lat", "lon", "location", "timezone", "observation", "text")


def _safe(value):
    """Remove raw location and observation material from a handoff projection."""
    if isinstance(value, dict):
        return {key: _safe(item) for key, item in value.items() if not any(token in key.casefold() for token in SENSITIVE_TOKENS)}
    if isinstance(value, list):
        return [_safe(item) for item in value]
    return value


def _evidence_projection(item: dict) -> dict:
    projected = _safe({
        "evidence_id": item.get("evidence_id"), "system": item.get("system"),
        "source_path": item.get("source_path"), "source_value": item.get("source_value"),
        "epistemic_class": item.get("epistemic_class"), "mapping_provenance": item.get("mapping_provenance"),
        "independence_group": item.get("independence_group"), "limitations": item.get("limitations", []),
    })
    # Handle nested sensitive data in source_value (dict, list, or scalar)
    if isinstance(projected.get("source_value"), dict):
        projected["source_value"] = _safe(projected["source_value"])
    elif isinstance(projected.get("source_value"), list):
        # Recursively sanitize each element of the list
        sanitized_list = []
        for elem in projected["source_value"]:
            if isinstance(elem, dict):
                sanitized_list.append(_safe(elem))
            elif isinstance(elem, list):
                sanitized_list.append(sanitize_nested_list(elem))
            else:
                sanitized_list.append(elem)
        projected["source_value"] = sanitized_list
    return projected

def sanitize_nested_list(lst: list) -> list:
    """Recursively sanitize a nested list for sensitive tokens."""
    result = []
    for item in lst:
        if isinstance(item, dict):
            result.append(_safe(item))
        elif isinstance(item, list):
            result.append(sanitize_nested_list(item))
        else:
            result.append(item)
    return result


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
        "subject_inputs": _safe({"normalized_input": deepcopy(normalized), "included": ["name", "birth availability", "self-report availability"], "intentionally_excluded": excluded}),
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
