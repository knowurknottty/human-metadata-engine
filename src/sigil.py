"""Deterministic, public custom-sigil generation.

The custom sigil is a visual encoding of the supplied text, not a personality
claim.  The response exposes only the public fingerprint projection, render
metadata, and SVG artifact.
"""

from __future__ import annotations

import re
from typing import Any

from engine import compute_unified_signature
from fingerprint import generate_fingerprint_svg


MAX_SIGIL_TEXT = 120


def normalize_sigil_text(raw: Any) -> str:
    """Validate and normalize a custom sigil label at the public boundary."""
    if not isinstance(raw, str):
        raise ValueError("Sigil text must be a string.")
    text = re.sub(r"\s+", " ", raw).strip()
    if not text:
        raise ValueError("Sigil text cannot be empty.")
    if len(text) > MAX_SIGIL_TEXT:
        raise ValueError(f"Sigil text is too long (max {MAX_SIGIL_TEXT} characters).")
    if not any(char.isalnum() for char in text):
        raise ValueError("Sigil text must contain at least one letter or number.")
    return text


def generate_custom_sigil(raw: Any, *, size: int = 360) -> dict[str, Any]:
    """Return a deterministic sigil artifact for one user-supplied label."""
    text = normalize_sigil_text(raw)
    if not isinstance(size, int) or not 160 <= size <= 720:
        raise ValueError("Sigil size must be an integer between 160 and 720.")
    identity = {
        "id": "custom-sigil:" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60],
        "text": text,
    }
    signature = compute_unified_signature(identity)
    fingerprint = signature["fingerprint"]
    return {
        "name": text,
        "svg": generate_fingerprint_svg(signature, size=size, identity_name=text),
        "hash": fingerprint["hash"],
        "symmetry": fingerprint["symmetry"],
        "render_spec": "sigil-v1",
        "disclaimer": "Deterministic visual encoding of the supplied text; not a personality or factual inference.",
    }


__all__ = ["MAX_SIGIL_TEXT", "generate_custom_sigil", "normalize_sigil_text"]
