"""Opt-in modern reflection over the historical Sumerian me ontology.

This layer never derives a me from a name, birth record, numerology, astrology,
or resonance score. It only aggregates capacity-domain tags explicitly attached
to user-supplied observations, then shows the corresponding modern analytical
category beside the historically attested corpus inventory.
"""
from __future__ import annotations

from typing import Any, Final

from encoders.sumerian_me import ME_CATEGORIES, MODERN_CAPACITY_CROSSWALK, ONTOLOGY_VERSION

REFLECTION_VERSION: Final[str] = "sumerian-me-reflection-v1"
CAPACITY_CATEGORY_IDS: Final[tuple[str, ...]] = tuple(entry["id"] for entry in ME_CATEGORIES)


def build_sumerian_me_reflection(
    observations: list[dict[str, Any]] | None,
    *,
    enabled: bool = False,
) -> dict[str, Any]:
    """Build a bounded reflection from explicit observation tags only."""
    base: dict[str, Any] = {
        "version": REFLECTION_VERSION,
        "source_ontology_version": ONTOLOGY_VERSION,
        "epistemic_layer": "modern_interpretive",
        "historical_claim": False,
        "enabled": bool(enabled),
        "mapping_basis": "explicit user-supplied observation capacity_domains tags",
        "forbidden_automatic_bases": [
            "name", "birth_data", "numerology", "astrology", "symbolic_resonance_score",
        ],
        "domain_matches": [],
    }
    if not enabled:
        return {
            **base,
            "available": False,
            "status": "disabled_by_default",
            "reason": "Enable sumerian_me_reflection explicitly to use the modern crosswalk.",
        }

    observations = observations or []
    category_lookup = {entry["id"]: entry for entry in ME_CATEGORIES}
    tagged: dict[str, list[dict[str, Any]]] = {category_id: [] for category_id in CAPACITY_CATEGORY_IDS}
    for index, observation in enumerate(observations):
        for category_id in observation.get("capacity_domains") or []:
            if category_id in tagged:
                tagged[category_id].append({
                    "evidence_id": f"observation:{index}",
                    "source": observation.get("source", "user_supplied"),
                    "confidence": observation.get("confidence", "unrated"),
                    "occurred_at": observation.get("occurred_at"),
                })

    matches: list[dict[str, Any]] = []
    for category_id in CAPACITY_CATEGORY_IDS:
        evidence = tagged[category_id]
        if not evidence:
            continue
        category = category_lookup[category_id]
        matches.append({
            "category_id": category_id,
            "category_label": category["label"],
            "capacity_domains": list(MODERN_CAPACITY_CROSSWALK[category_id]),
            "support_observation_count": len(evidence),
            "evidence_refs": evidence,
            "historical_me_items": list(category["items"]),
            "historical_scope": "attested corpus items grouped by a modern Human Metadata taxonomy",
        })

    if not matches:
        return {
            **base,
            "available": False,
            "status": "no_explicit_capacity_evidence",
            "reason": "No observation supplied an explicit capacity_domains tag.",
        }
    return {
        **base,
        "available": True,
        "status": "mapped_from_explicit_observations",
        "domain_matches": matches,
        "limitations": [
            "The category grouping and crosswalk are modern Human Metadata constructs, not Sumerian categories.",
            "A tagged observation supports only the modern comparison; it does not show that a person possesses an ancient me.",
            "Observation text is not copied into this reflection output.",
        ],
    }
