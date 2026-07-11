"""Identity constellation validation and relationship modeling."""

from __future__ import annotations

from typing import Any

try:
    from public_contract import normalize_public_name, validate_psychology
except ImportError:  # pragma: no cover - package-style import
    from .public_contract import normalize_public_name, validate_psychology

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
SENSITIVE_METADATA_KEYS = {
    "birth",
    "birth_data",
    "psychology",
    "psychological_profile",
    "health",
    "medical",
    "medical_data",
    "biometrics",
    "genetics",
    "genetic_data",
}


class ConstellationValidationError(ValueError):
    """Raised when constellation data violates privacy or graph constraints."""


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConstellationValidationError(f"{field} must be a non-empty string.")
    return value.strip()


def _validated_metadata(item: dict[str, Any], *, node_type: str, index: int) -> dict[str, Any]:
    raw_metadata = item.get("metadata")
    if raw_metadata is None:
        return {}
    if not isinstance(raw_metadata, dict):
        raise ConstellationValidationError(f"nodes[{index}].metadata must be an object.")

    metadata = dict(raw_metadata)
    if len(metadata) > 20:
        raise ConstellationValidationError(f"nodes[{index}].metadata supports at most 20 fields.")
    if node_type == "person":
        hidden_sensitive = sorted(
            key for key in metadata
            if str(key).strip().lower() in SENSITIVE_METADATA_KEYS
        )
        if hidden_sensitive:
            joined = ", ".join(hidden_sensitive)
            raise ConstellationValidationError(
                f"nodes[{index}].metadata contains reserved sensitive fields: {joined}. "
                "Use the structured birth and psychology fields so privacy rules apply."
            )
    for key, value in metadata.items():
        if not isinstance(key, str) or len(key) > 60:
            raise ConstellationValidationError(f"nodes[{index}].metadata keys must be short strings.")
        if isinstance(value, (dict, list)):
            raise ConstellationValidationError(
                f"nodes[{index}].metadata.{key} must be a scalar; sensitive structured data has a typed field."
            )
        if value is not None and len(str(value)) > 240:
            raise ConstellationValidationError(f"nodes[{index}].metadata.{key} is too long.")
    return metadata


def validate_constellation(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate a tiered identity graph.

    People default to name-only. Birth data requires an explicit profile level.
    Psychology requires self-report or explicit consent. Minors never expose
    psychology in this version. Sensitive person data cannot be hidden inside
    free-form metadata.
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
        try:
            name = normalize_public_name(name)
        except ValueError as exc:
            raise ConstellationValidationError(f"nodes[{index}].name is not encodable: {exc}") from exc

        profile_level = item.get("profile_level") or "name_only"
        if profile_level not in PROFILE_LEVELS:
            raise ConstellationValidationError(
                f"nodes[{index}].profile_level must be one of {sorted(PROFILE_LEVELS)}."
            )

        is_minor = bool(item.get("is_minor", False))
        consent_basis = item.get("consent_basis")
        birth = item.get("birth")
        psychology = item.get("psychology")
        metadata = _validated_metadata(item, node_type=node_type, index=index)

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
                try:
                    psychology = validate_psychology(psychology)
                except ValueError as exc:
                    raise ConstellationValidationError(
                        f"nodes[{index}].psychology is invalid: {exc}"
                    ) from exc
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
            "metadata": metadata,
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
        started_year = item.get("started_year")
        if started_year is not None and (
            isinstance(started_year, bool) or not isinstance(started_year, int) or not 1 <= started_year <= 9999
        ):
            raise ConstellationValidationError(f"edges[{index}].started_year must be a year from 1 to 9999.")
        confidence = item.get("confidence", "user_supplied")
        if not isinstance(confidence, str) or confidence not in {"user_supplied", "low", "medium", "high"}:
            raise ConstellationValidationError(f"edges[{index}].confidence is invalid.")
        notes = item.get("notes")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 500):
            raise ConstellationValidationError(f"edges[{index}].notes must be at most 500 characters.")
        key = (source, relation, target)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        edges.append({
            "source": source,
            "target": target,
            "relation": relation,
            "started_year": started_year,
            "confidence": confidence,
            "notes": notes,
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "privacy_model": "tiered-v1",
        "rules": [
            "People default to name-only.",
            "Birth analysis is optional and explicit.",
            "Psychology requires self-report or explicit consent.",
            "Sensitive person data cannot bypass privacy rules through metadata.",
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
    "SENSITIVE_METADATA_KEYS",
    "validate_constellation",
    "connection_summary",
]
