"""Identity constellation validation and relationship modeling."""

from __future__ import annotations

from typing import Any

NODE_TYPES = {
    "person",
    "alias",
    "project",
    "brand",
    "invention",
    "work",
    "organization",
    "concept",
}

RELATION_TYPES = {
    "alias_of",
    "parent_of",
    "child_of",
    "created",
    "named",
    "founded",
    "co_created",
    "influenced",
    "derived_from",
    "part_of",
    "genetic_parent_of",
    "raised_by",
    "lineage_of",
}

PROFILE_LEVELS = {"name_only", "birth", "self_report"}
CONSENT_BASES = {"self", "explicit_consent", "parent_or_guardian", "public_record"}


class ConstellationValidationError(ValueError):
    """Raised when constellation data violates privacy or graph constraints."""


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConstellationValidationError(f"{field} must be a non-empty string.")
    return value.strip()


def validate_constellation(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate a tiered identity graph.

    People default to name-only. Birth data requires an explicit profile level.
    Psychology requires self-report or explicit consent. Minors never expose
    psychology in this version.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ConstellationValidationError("constellation must be an object.")

    raw_nodes = raw.get("nodes") or []
    raw_edges = raw.get("edges") or []
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ConstellationValidationError("constellation nodes and edges must be arrays.")
    if len(raw_nodes) > 50:
        raise ConstellationValidationError("constellation supports at most 50 nodes.")
    if len(raw_edges) > 200:
        raise ConstellationValidationError("constellation supports at most 200 edges.")

    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for index, item in enumerate(raw_nodes):
        if not isinstance(item, dict):
            raise ConstellationValidationError(f"nodes[{index}] must be an object.")
        node_id = _require_text(item.get("id"), f"nodes[{index}].id")
        if node_id in node_ids:
            raise ConstellationValidationError(f"duplicate node id: {node_id}")
        node_ids.add(node_id)

        node_type = _require_text(item.get("type"), f"nodes[{index}].type")
        if node_type not in NODE_TYPES:
            raise ConstellationValidationError(
                f"nodes[{index}].type must be one of {sorted(NODE_TYPES)}."
            )
        name = _require_text(item.get("name"), f"nodes[{index}].name")
        if len(name) > 120:
            raise ConstellationValidationError(f"nodes[{index}].name is too long.")

        profile_level = item.get("profile_level") or "name_only"
        if profile_level not in PROFILE_LEVELS:
            raise ConstellationValidationError(
                f"nodes[{index}].profile_level must be one of {sorted(PROFILE_LEVELS)}."
            )

        is_minor = bool(item.get("is_minor", False))
        consent_basis = item.get("consent_basis")
        birth = item.get("birth")
        psychology = item.get("psychology")

        if node_type != "person":
            profile_level = "name_only"
            birth = None
            psychology = None
            is_minor = False
            consent_basis = None
        else:
            if profile_level == "name_only":
                birth = None
                psychology = None
            elif profile_level == "birth":
                psychology = None
                if birth is None:
                    raise ConstellationValidationError(
                        f"nodes[{index}] requests birth analysis but supplies no birth data."
                    )
            elif profile_level == "self_report":
                if psychology is None:
                    raise ConstellationValidationError(
                        f"nodes[{index}] requests self-report analysis but supplies no psychology."
                    )
                if consent_basis not in {"self", "explicit_consent"}:
                    raise ConstellationValidationError(
                        f"nodes[{index}] psychology requires self or explicit_consent."
                    )
            if is_minor and psychology is not None:
                raise ConstellationValidationError(
                    f"nodes[{index}] is a minor; psychology is not accepted."
                )
            if consent_basis is not None and consent_basis not in CONSENT_BASES:
                raise ConstellationValidationError(
                    f"nodes[{index}].consent_basis must be one of {sorted(CONSENT_BASES)}."
                )

        nodes.append({
            "id": node_id,
            "type": node_type,
            "name": name,
            "profile_level": profile_level,
            "is_minor": is_minor,
            "consent_basis": consent_basis,
            "birth": birth,
            "psychology": psychology,
            "metadata": item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
        })

    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for index, item in enumerate(raw_edges):
        if not isinstance(item, dict):
            raise ConstellationValidationError(f"edges[{index}] must be an object.")
        source = _require_text(item.get("source"), f"edges[{index}].source")
        target = _require_text(item.get("target"), f"edges[{index}].target")
        relation = _require_text(item.get("relation"), f"edges[{index}].relation")
        if source not in node_ids or target not in node_ids:
            raise ConstellationValidationError(
                f"edges[{index}] references an unknown node."
            )
        if source == target:
            raise ConstellationValidationError(f"edges[{index}] cannot self-link.")
        if relation not in RELATION_TYPES:
            raise ConstellationValidationError(
                f"edges[{index}].relation must be one of {sorted(RELATION_TYPES)}."
            )
        key = (source, relation, target)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        edges.append({
            "source": source,
            "target": target,
            "relation": relation,
            "started_year": item.get("started_year"),
            "confidence": item.get("confidence", "user_supplied"),
            "notes": item.get("notes"),
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "privacy_model": "tiered-v1",
        "rules": [
            "People default to name-only.",
            "Birth analysis is optional and explicit.",
            "Psychology requires self-report or explicit consent.",
            "Projects, aliases, brands, inventions, and works may be analyzed as creations.",
            "Genetic lineage, lived identity, chosen identity, and creative authorship remain separate relations.",
        ],
    }


def connection_summary(graph: dict[str, Any] | None) -> dict[str, Any] | None:
    if graph is None:
        return None
    counts: dict[str, int] = {}
    for edge in graph["edges"]:
        counts[edge["relation"]] = counts.get(edge["relation"], 0) + 1
    return {
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "node_types": {
            node_type: sum(node["type"] == node_type for node in graph["nodes"])
            for node_type in sorted(NODE_TYPES)
            if any(node["type"] == node_type for node in graph["nodes"])
        },
        "relations": dict(sorted(counts.items())),
        "privacy_model": graph["privacy_model"],
    }


__all__ = [
    "ConstellationValidationError",
    "NODE_TYPES",
    "RELATION_TYPES",
    "PROFILE_LEVELS",
    "validate_constellation",
    "connection_summary",
]
