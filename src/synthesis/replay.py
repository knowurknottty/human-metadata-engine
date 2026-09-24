"""Canonical content identities for synthesis records and deterministic replay."""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from typing import Any

from .contracts import SYNTHESIS_REPLAY_SCHEMA_VERSION


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite numbers cannot participate in deterministic identities.")
        return value
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(key)): _normalize(item)
            for key, item in value.items()
        }
    raise TypeError(f"Unsupported deterministic identity value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def namespaced_id(namespace: str, payload: Any) -> str:
    return f"{namespace}_{content_digest(payload)}"


def build_replay_identity(*, kind: str, payload: Any) -> str:
    return namespaced_id(
        "replay",
        {
            "schema_version": SYNTHESIS_REPLAY_SCHEMA_VERSION,
            "kind": kind,
            "payload": payload,
        },
    )
