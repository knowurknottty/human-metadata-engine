"""Quantum Soul Codex / Timeline Key symbolic synthesis.

This module composes existing Pythagorean name and birth-date calculations into
an explicitly modern, deterministic symbolic profile.  "Quantum" is used only
as metaphorical product language; this encoder makes no claim about quantum
physics, souls as measurable entities, personality diagnosis, or prediction.
"""

from __future__ import annotations

from typing import Any

from .pythagorean import life_path_number, pythagorean_signature, reduce_number

SYSTEM_ID = "quantum_soul_codex"
CONVENTION = "modern-pythagorean-symbolic-synthesis-v1"
SOURCE_IDS = [
    "SRC-PYTHAGOREAN-NUMEROLOGY",
    "SRC-HME-QSC-MODERN-SYNTHESIS",
]

ARCHETYPES = {
    1: "Originator",
    2: "Mediator",
    3: "Messenger",
    4: "Builder",
    5: "Explorer",
    6: "Guardian",
    7: "Seeker",
    8: "Sovereign Builder",
    9: "Humanitarian",
    11: "Illuminator",
    22: "Master Builder",
    33: "Compassionate Teacher",
}


def _single(value: int) -> int:
    """Reduce to a single digit, never preserving master numbers."""
    return reduce_number(value, preserve_master=False)[0]


def _pinnacles(month: int, day: int, year: int) -> tuple[list[int], list[int]]:
    """Return common modern Pythagorean pinnacle and challenge sequences."""
    month_n = _single(sum(int(d) for d in f"{month:02d}"))
    day_n = _single(sum(int(d) for d in f"{day:02d}"))
    year_n = _single(sum(int(d) for d in f"{year:04d}"))

    first = _single(month_n + day_n)
    second = _single(day_n + year_n)
    third = _single(first + second)
    fourth = _single(month_n + year_n)

    c1 = abs(day_n - month_n)
    c2 = abs(day_n - year_n)
    c3 = abs(c1 - c2)
    c4 = abs(month_n - year_n)
    return [first, second, third, fourth], [c1, c2, c3, c4]


def _name_segments(text: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for token in text.split():
        sig = pythagorean_signature(token)
        segments.append({
            "token": token,
            "total": sig.total,
            "reduced": sig.reduced,
            "master_preserved": sig.master_preserved,
            "archetype": ARCHETYPES.get(sig.master_preserved or sig.reduced),
        })
    return segments


def quantum_soul_codex(text: str, birth: dict[str, Any] | None) -> dict[str, Any]:
    """Compute a reproducible symbolic codex from a name and birth date.

    The result is provenance-aware and intentionally excluded from empirical
    personality claims, clinical use, and predictive scoring.
    """
    if not birth:
        return {
            "system": SYSTEM_ID,
            "phase": "structural",
            "status": "insufficient_input",
            "interpretation_level": "symbolic_modern_synthesis",
            "provenance": {
                "convention": CONVENTION,
                "source_ids": SOURCE_IDS,
                "claim_class": "deterministic_symbolic_interpretation",
                "empirical_validity": "not_established",
                "quantum_term": "metaphorical_only",
            },
            "data": {"required": ["birth.year", "birth.month", "birth.day"]},
        }

    year = int(birth["year"])
    month = int(birth["month"])
    day = int(birth["day"])
    name = pythagorean_signature(text)
    date = life_path_number(year, month, day)
    pinnacles, challenges = _pinnacles(month, day, year)

    expression = name.master_preserved or name.reduced
    primary = [
        date.life_path_master or date.life_path_reduced,
        expression,
        name.soul_urge,
        name.personality,
        date.birthday_number,
    ]
    codex_key = "QSC-" + "".join(str(v) for v in primary)
    timeline_key = "TKP-" + "".join(str(v) for v in pinnacles) + ":" + "".join(str(v) for v in challenges)

    return {
        "system": SYSTEM_ID,
        "phase": "structural",
        "status": "computed",
        "interpretation_level": "symbolic_modern_synthesis",
        "provenance": {
            "convention": CONVENTION,
            "source_ids": SOURCE_IDS,
            "claim_class": "deterministic_symbolic_interpretation",
            "empirical_validity": "not_established",
            "quantum_term": "metaphorical_only",
            "limitations": [
                "No standardized historical system exists under this exact name.",
                "Interpretive fit is not evidence of causal or predictive validity.",
                "Do not use for diagnosis, eligibility, hiring, credit, medical, or legal decisions.",
            ],
        },
        "data": {
            "codex_key": codex_key,
            "timeline_key": timeline_key,
            "primary_sequence": primary,
            "life_path": {
                "raw": date.life_path_raw,
                "reduced": date.life_path_reduced,
                "master_preserved": date.life_path_master,
                "archetype": ARCHETYPES.get(date.life_path_master or date.life_path_reduced),
            },
            "expression": {
                "raw": name.total,
                "reduced": name.reduced,
                "master_preserved": name.master_preserved,
                "archetype": ARCHETYPES.get(expression),
            },
            "soul_urge": {
                "raw": name.soul_urge_total,
                "reduced": name.soul_urge,
                "archetype": ARCHETYPES.get(name.soul_urge),
            },
            "personality": {
                "raw": name.personality_total,
                "reduced": name.personality,
                "archetype": ARCHETYPES.get(name.personality),
            },
            "birthday": {
                "reduced": date.birthday_number,
                "archetype": ARCHETYPES.get(date.birthday_number),
            },
            "timeline": {
                "pinnacles": pinnacles,
                "challenges": challenges,
                "method": "common-modern-pythagorean-pinnacle-challenge",
            },
            "name_segments": _name_segments(text),
        },
    }
