"""Motif ranking, independent agreement, and contradiction analysis."""

from __future__ import annotations

from collections import defaultdict

STRENGTH_WEIGHT = {"strong": 1.0, "moderate": 0.65, "weak": 0.35, None: 0.0}
POLARITIES = (
    ("autonomy", "belonging"), ("visibility", "privacy"), ("freedom", "structure"),
    ("intensity", "stability"), ("analysis", "intuition"), ("service", "sovereignty"),
    ("initiation", "receptivity"), ("conflict", "harmony"), ("expansion", "contraction"),
)


def rank_motifs(evidence_packet: dict) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in evidence_packet["evidence_items"]:
        for motif in item.get("interpretive_tags") or []:
            grouped[motif].append(item)
    quality = evidence_packet["data_quality"]
    missing_penalty = 0.15 if quality["astronomy"] == "unavailable" else 0.05 if quality["astronomy"] == "partial" else 0.0
    ranked = []
    for motif, items in grouped.items():
        by_group: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            by_group[item["independence_group"]].append(item)
        group_support = sum(max(STRENGTH_WEIGHT[item.get("mapping_strength")] for item in group) for group in by_group.values())
        within_recurrence = sum(max(0, len(group) - 1) for group in by_group.values())
        recurrence_bonus = min(0.3, within_recurrence * 0.05)
        directness = round(sum(1 for item in items if item["epistemic_class"] in {"deterministic_calculation", "deterministic_relationship"}) / len(items), 3)
        score = round(group_support + recurrence_bonus - missing_penalty, 3)
        confidence = "high" if len(by_group) >= 3 and score >= 2.4 else "medium" if len(by_group) >= 2 else "low"
        ranked.append({
            "motif_id": f"motif_{motif}", "label": motif.replace("_", " "),
            "evidence_ids": sorted(item["evidence_id"] for item in items),
            "systems": sorted({item["system"] for item in items}),
            "independence_groups": sorted(by_group),
            "distinct_system_count": len({item["system"] for item in items}),
            "independent_group_count": len(by_group),
            "weighted_support": score,
            "within_system_recurrence": within_recurrence,
            "contradiction_penalty": 0.0,
            "data_quality_penalty": missing_penalty,
            "novelty_penalty": 0.0,
            "directness": directness,
            "confidence": confidence,
            "excluded_evidence": [],
            "explanation": "Each independence group contributes only its strongest mapping; repeated records add a capped recurrence bonus.",
        })
    ranked.sort(key=lambda item: (-item["weighted_support"], -item["independent_group_count"], item["label"]))
    return ranked


def detect_agreements(motifs: list[dict]) -> list[dict]:
    agreements = []
    for motif in motifs:
        groups = motif["independence_groups"]
        if len(groups) < 2:
            continue
        agreements.append({
            "agreement_id": f"agreement_{motif['label'].replace(' ', '_')}",
            "motif_id": motif["motif_id"], "motif": motif["label"],
            "participating_systems": motif["systems"], "independence_groups": groups,
            "evidence_ids": motif["evidence_ids"], "normalization_path": "motif-ontology-v1",
            "strength": motif["confidence"], "kind": "thematic_agreement",
            "ambiguity": "Symbolic systems are not independent empirical measurements.",
            "alternative_reading": "The recurrence may reflect project-authored normalization rather than a stable personal quality.",
        })
    return agreements


def detect_contradictions(motifs: list[dict]) -> list[dict]:
    lookup = {item["label"]: item for item in motifs}
    contradictions = []
    for pole_a, pole_b in POLARITIES:
        left, right = lookup.get(pole_a), lookup.get(pole_b)
        if not left or not right:
            continue
        if not left["independence_groups"] or not right["independence_groups"]:
            continue
        overlap = set(left["independence_groups"]) & set(right["independence_groups"])
        kind = "contextual_tension" if overlap else "polarity"
        confidence = "medium" if left["confidence"] != "low" and right["confidence"] != "low" else "low"
        contradictions.append({
            "contradiction_id": f"tension_{pole_a}_{pole_b}", "type": kind,
            "pole_a": pole_a, "pole_b": pole_b,
            "pole_a_evidence_ids": left["evidence_ids"], "pole_b_evidence_ids": right["evidence_ids"],
            "evidence_ids": sorted(set(left["evidence_ids"] + right["evidence_ids"])),
            "contexts": [f"{pole_a} may describe one symbolic emphasis", f"{pole_b} may describe another"],
            "possible_shadow": f"overidentifying with {pole_a} while excluding {pole_b}, or the reverse",
            "integrated_expression": f"testing when {pole_a} is useful and when {pole_b} is useful",
            "uncertainty": confidence,
            "unresolved": True,
        })
    contradictions.sort(key=lambda item: (item["uncertainty"] == "low", item["contradiction_id"]))
    return contradictions
