"""Deterministic explanation layer over one evidence/claim graph.

The Pattern Map explains dependence, divergence, authorship, and input sensitivity.
It never adds evidence, motif votes, empirical confidence, or generated facts.
"""

from __future__ import annotations

from collections import defaultdict

from .replay import namespaced_id

PATTERN_MAP_VERSION = "pattern-map-v1"


def _evidence_index(evidence_packet: dict) -> dict[str, dict]:
    return {
        item["evidence_id"]: item
        for item in evidence_packet.get("evidence_items", [])
        if item.get("evidence_id")
    }


def _members(evidence_ids: list[str], evidence: dict[str, dict]) -> list[dict]:
    result = []
    for evidence_id in sorted(set(evidence_ids)):
        item = evidence.get(evidence_id)
        if not item:
            continue
        result.append({
            "system_id": item["system"],
            "record_id": item.get("record_id"),
            "evidence_id": evidence_id,
            "independence_family": item.get("independence_group"),
            "epistemic_class": item.get("epistemic_class"),
            "source_path": item.get("source_path"),
        })
    return result


def _agreement_explanations(plan: dict, evidence: dict[str, dict]) -> list[dict]:
    output = []
    for agreement in plan.get("agreements", []):
        members = _members(agreement.get("evidence_ids", []), evidence)
        systems = sorted({item["system_id"] for item in members})
        families = sorted({
            item["independence_family"] for item in members
            if item.get("independence_family")
        })
        reasons = ["same_project_ontology_mapping"]
        if len(families) > 1:
            reasons.append("recurrence_across_distinct_dependence_families")
        else:
            reasons.append("shared_dependence_family")
        payload = {
            "topic": f"motif:{agreement['motif']}",
            "members": members,
            "families": families,
            "reason_codes": reasons,
        }
        output.append({
            "agreement_id": namespaced_id("agr_v1", payload),
            "topic": payload["topic"],
            "relation": "agreement" if len(families) > 1 else "related",
            "members": members,
            "system_count": len(systems),
            "independence_family_count": len(families),
            "reason_codes": reasons,
            "evidence_ids": sorted(set(agreement.get("evidence_ids", []))),
            "support_strength": agreement.get("support_strength", agreement.get("strength")),
            "limitation": (
                "Recurrence across symbolic systems is not empirical confirmation. "
                "Shared dependence families are related signals, not independent confirmation."
            ),
            "empirical_status": "not_established",
        })
    return output


def _disagreement_explanations(plan: dict, evidence: dict[str, dict]) -> list[dict]:
    output = []
    for tension in plan.get("productive_contradictions", []):
        positions = []
        for pole_key, ids_key in (
            ("pole_a", "pole_a_evidence_ids"),
            ("pole_b", "pole_b_evidence_ids"),
        ):
            ids = tension.get(ids_key, [])
            members = _members(ids, evidence)
            positions.append({
                "label": tension[pole_key],
                "evidence_ids": sorted(set(ids)),
                "systems": sorted({item["system_id"] for item in members}),
                "independence_families": sorted({
                    item["independence_family"] for item in members
                    if item.get("independence_family")
                }),
            })
        overlap = set(positions[0]["independence_families"]) & set(positions[1]["independence_families"])
        reasons = ["different_symbolic_axis"]
        if overlap:
            reasons.append("shared_dependence_family")
        else:
            reasons.append("distinct_dependence_families")
        payload = {"positions": positions, "reason_codes": reasons, "type": tension.get("type")}
        output.append({
            "disagreement_id": namespaced_id("dis_v1", payload),
            "relation": tension.get("type", "tension"),
            "positions": positions,
            "reason_codes": reasons,
            "resolution": "preserved",
            "winner": None,
            "support_strength": tension.get("uncertainty"),
            "evidence_ids": sorted(set(tension.get("evidence_ids", []))),
            "limitation": "The systems may answer different symbolic questions; no winner or average is inferred.",
            "empirical_status": "not_established",
        })
    return output


def _statement_provenance(narratives: dict[str, dict]) -> list[dict]:
    by_claim: dict[str, dict] = {}
    for mode, narrative in narratives.items():
        for section in narrative.get("sections", []):
            for paragraph in section.get("paragraphs", []):
                for sentence in paragraph.get("sentences", []):
                    claim_ids = sentence.get("claim_ids") or []
                    if len(claim_ids) != 1:
                        continue
                    claim_id = claim_ids[0]
                    record = by_claim.setdefault(claim_id, {
                        "claim_id": claim_id,
                        "evidence_ids": list(sentence.get("evidence_ids") or []),
                        "epistemic_layer": sentence.get("epistemic_layer"),
                        "empirical_status": sentence.get("empirical_status", "not_established"),
                        "support_provenance": sentence.get("support_provenance"),
                        "presentations": {},
                    })
                    record["presentations"][mode] = {
                        "statement_id": sentence.get("statement_id"),
                        "text_provenance": sentence.get("text_provenance"),
                    }
    return [by_claim[key] for key in sorted(by_claim)]


def _sensitivity(evidence_packet: dict) -> list[dict]:
    quality = evidence_packet.get("data_quality", {})
    records = []

    def add(path: str, status: str, systems: list[str], reason_codes: list[str], disclosure: str) -> None:
        payload = {
            "path": path,
            "status": status,
            "systems": systems,
            "reason_codes": reason_codes,
        }
        records.append({
            "sensitivity_id": namespaced_id("sens_v1", payload),
            "input": {"path": path, "status": status, "disclosure": disclosure},
            "effects": [{
                "status": "dependency_only",
                "affected_system_ids": systems,
                "affected_claim_ids": [],
                "reason_codes": reason_codes,
            }],
            "wording": "This input could affect these calculations; no replacement value was invented or recomputed.",
            "raw_alternative_included": False,
            "empirical_status": "not_established",
        })

    birth_date = quality.get("birth_date")
    birth_time = quality.get("birth_time")
    birth_location = quality.get("birth_location")
    astronomy = quality.get("astronomy")
    human_design = quality.get("human_design")

    if birth_date in {"missing", "unknown", "partial", "unavailable"}:
        add(
            "birth.date", birth_date, ["astrology", "human_design"],
            ["birth_date_required"],
            "Birth date is unavailable or incomplete.",
        )
    if birth_time in {"missing", "unknown", "approximate"}:
        add(
            "birth.time", birth_time, ["astrology", "human_design"],
            ["exact_local_time_changes_time_sensitive_fields"],
            "Exact birth time is unavailable or approximate.",
        )
    if birth_location in {"missing", "unknown", "partial", "unavailable"}:
        add(
            "birth.location", birth_location, ["astrology", "human_design"],
            ["location_required_for_time_and_geometry"],
            "Birth location is unavailable or unresolved.",
        )
    if astronomy == "partial" and not any(item["input"]["path"] == "birth.time" for item in records):
        add(
            "birth.time", "partial", ["astrology"],
            ["time_sensitive_astrology_withheld"],
            "Time-sensitive astronomy is partial.",
        )
    if human_design == "unavailable" and birth_date not in {"missing", "unknown"} and birth_time not in {"missing", "unknown", "approximate"}:
        add(
            "human_design.required_inputs", "unavailable", ["human_design"],
            ["required_input_or_adapter_unavailable"],
            "Human Design could not be calculated from the available request.",
        )
    return records


def build_pattern_map(evidence_packet: dict, plan: dict, narratives: dict[str, dict]) -> dict:
    evidence = _evidence_index(evidence_packet)
    return {
        "schema_version": PATTERN_MAP_VERSION,
        "analysis_id": evidence_packet["analysis_id"],
        "agreement_explanations": _agreement_explanations(plan, evidence),
        "disagreement_explanations": _disagreement_explanations(plan, evidence),
        "statement_provenance": _statement_provenance(narratives),
        "input_sensitivity": _sensitivity(evidence_packet),
        "invariants": {
            "adds_evidence": False,
            "adds_motif_votes": False,
            "empirical_validation": "not_established",
            "sensitivity_requires_recomputation_for_would_change_claims": True,
        },
    }
