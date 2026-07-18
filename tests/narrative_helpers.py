"""Shared deterministic fixtures for narrative tests."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "webapp"), os.path.join(ROOT, "src")]

from server import analyze  # noqa: E402


def exact_payload(name: str = "Kirk Evan Brown", *, year: int = 1982, month: int = 2, day: int = 4) -> dict:
    return {
        "name": name, "mode": "magic",
        "birth": {
            "year": year, "month": month, "day": day, "hour": 1, "minute": 42,
            "time_accuracy": "exact", "lat": 41.2683, "lon": -110.9632,
            "timezone_name": "America/Denver",
        },
    }


def exact_result(**kwargs) -> dict:
    return analyze(exact_payload(**kwargs))


def resolve_path(result: dict, path: str):
    root = {"signature": result["signature"], "psychology": result.get("psychology")}
    value = root
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, (list, str)) else value[part]
    return value


def narrative_sentences(result: dict, mode: str = "plain") -> list[dict]:
    return [
        sentence
        for section in result["synthesis"]["narratives"][mode]["sections"]
        for paragraph in section["paragraphs"]
        for sentence in paragraph["sentences"]
    ]
