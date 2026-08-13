"""Load and validate the explicit v1 motif normalization ontology."""

from __future__ import annotations

import json
from pathlib import Path

from .contracts import ONTOLOGY_VERSION

_PATH = Path(__file__).with_name("data") / "motif_ontology_v1.json"


def load_ontology() -> dict:
    data = json.loads(_PATH.read_text(encoding="utf-8"))
    if data.get("schema_version") != ONTOLOGY_VERSION:
        raise ValueError("Unexpected motif ontology version.")
    keys: set[tuple[str, str]] = set()
    for item in data.get("mappings", []):
        key = (item["source_system"], item["source_symbol"].casefold())
        if key in keys:
            raise ValueError(f"Duplicate motif mapping: {key}")
        keys.add(key)
        if not item.get("motifs") or item.get("strength") not in {"strong", "moderate", "weak"}:
            raise ValueError(f"Invalid motif mapping: {key}")
    return data


ONTOLOGY = load_ontology()
_INDEX = {
    (item["source_system"], item["source_symbol"].casefold()): item
    for item in ONTOLOGY["mappings"]
}


def mapping_for(source_system: str, source_symbol: object) -> dict | None:
    return _INDEX.get((source_system, str(source_symbol).casefold()))
