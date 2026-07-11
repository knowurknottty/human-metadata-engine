"""Strict public request contracts shared by the web surface.

The engine accepts a deliberately broad internal identity shape.  The public
surface must be narrower: bounded strings, finite numeric values, explicit
mode selection, and no silently invented psychological or birth precision.
"""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any


MODES = {"data", "magic"}
SUBJECT_TYPES = {"self", "reference"}
TIME_ACCURACIES = {"unknown", "hour_only", "approximate", "exact"}
ATTACHMENT_STYLES = {"secure", "anxious", "avoidant", "disorganized", "fearful_avoidant"}
MBTI_TYPES = {
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
}
BIG_FIVE = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")
_BIDI_OR_CONTROL = re.compile(r"[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]")


class PublicContractError(ValueError):
    """Raised when a request violates the public API contract."""


def normalize_public_name(raw: Any, *, max_length: int = 120) -> str:
    if not isinstance(raw, str):
        raise PublicContractError("name must be a string.")
    name = unicodedata.normalize("NFC", raw).strip()
    if not name:
        raise PublicContractError("A name containing letters is required.")
    if len(name) > max_length:
        raise PublicContractError(f"Name is too long (max {max_length} characters).")
    if _BIDI_OR_CONTROL.search(name):
        raise PublicContractError("Name contains unsupported control or bidirectional characters.")
    # The encoders use the built-in transliteration profile.  Reject values
    # that produce no mapped Latin letters instead of returning an empty score.
    latin = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    if not any("A" <= char.upper() <= "Z" for char in latin):
        raise PublicContractError("Name must contain at least one encodable Latin letter.")
    return name


def validate_mode(raw: Any) -> str:
    mode = "data" if raw in (None, "") else raw
    if mode not in MODES:
        raise PublicContractError("mode must be either 'data' or 'magic'.")
    return mode


def validate_subject_type(raw: Any) -> str:
    subject_type = "self" if raw in (None, "") else raw
    if subject_type not in SUBJECT_TYPES:
        raise PublicContractError("subject_type must be either 'self' or 'reference'.")
    return subject_type


def validate_psychology(raw: Any) -> dict[str, Any] | None:
    if raw in (None, {}):
        return None
    if not isinstance(raw, dict):
        raise PublicContractError("psychology must be an object.")
    unknown = sorted(set(raw) - {"big_five", "mbti", "enneagram", "attachment"})
    if unknown:
        raise PublicContractError(f"psychology contains unsupported fields: {', '.join(unknown)}.")

    result: dict[str, Any] = {}
    big_five = raw.get("big_five")
    if big_five is not None:
        if not isinstance(big_five, dict):
            raise PublicContractError("psychology.big_five must be an object.")
        unknown_traits = sorted(set(big_five) - set(BIG_FIVE))
        if unknown_traits:
            raise PublicContractError(
                f"psychology.big_five contains unsupported fields: {', '.join(unknown_traits)}."
            )
        validated_b5 = {}
        for trait, value in big_five.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise PublicContractError(f"psychology.big_five.{trait} must be a finite number.")
            if not 0 <= float(value) <= 1:
                raise PublicContractError(f"psychology.big_five.{trait} must be between 0 and 1.")
            validated_b5[trait] = round(float(value), 4)
        if not validated_b5:
            raise PublicContractError("psychology.big_five must contain at least one trait.")
        result["big_five"] = validated_b5

    mbti = raw.get("mbti")
    if mbti not in (None, ""):
        if not isinstance(mbti, str) or mbti.upper() not in MBTI_TYPES:
            raise PublicContractError("psychology.mbti must be a valid four-letter MBTI type.")
        result["mbti"] = mbti.upper()

    enneagram = raw.get("enneagram")
    if enneagram not in (None, {}):
        if not isinstance(enneagram, dict):
            raise PublicContractError("psychology.enneagram must be an object.")
        if set(enneagram) - {"type", "wing"}:
            raise PublicContractError("psychology.enneagram only accepts type and wing.")
        core_type = enneagram.get("type")
        wing = enneagram.get("wing")
        if isinstance(core_type, bool) or not isinstance(core_type, int) or not 1 <= core_type <= 9:
            raise PublicContractError("psychology.enneagram.type must be an integer from 1 to 9.")
        if wing is not None and (isinstance(wing, bool) or not isinstance(wing, int) or not 1 <= wing <= 9):
            raise PublicContractError("psychology.enneagram.wing must be an integer from 1 to 9.")
        result["enneagram"] = {"type": core_type, "wing": wing}

    attachment = raw.get("attachment")
    if attachment not in (None, ""):
        if attachment not in ATTACHMENT_STYLES:
            raise PublicContractError(
                "psychology.attachment must be one of: " + ", ".join(sorted(ATTACHMENT_STYLES)) + "."
            )
        result["attachment"] = attachment

    if not result:
        raise PublicContractError("psychology must contain at least one assessment.")
    return result


def validate_observations(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise PublicContractError("observations must be an array.")
    if len(raw) > 40:
        raise PublicContractError("observations supports at most 40 entries.")
    allowed_confidence = {"unrated", "low", "medium", "high"}
    result = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise PublicContractError(f"observations[{index}] must be an object.")
        if set(item) - {"text", "source", "confidence", "occurred_at"}:
            raise PublicContractError(f"observations[{index}] contains unsupported fields.")
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise PublicContractError(f"observations[{index}].text must be a non-empty string.")
        text = unicodedata.normalize("NFC", text).strip()
        if len(text) > 500:
            raise PublicContractError(f"observations[{index}].text is too long (max 500 characters).")
        source = item.get("source", "user_supplied")
        if not isinstance(source, str) or not 1 <= len(source.strip()) <= 80:
            raise PublicContractError(f"observations[{index}].source must be a short string.")
        confidence = item.get("confidence", "unrated")
        if confidence not in allowed_confidence:
            raise PublicContractError(f"observations[{index}].confidence is invalid.")
        occurred_at = item.get("occurred_at")
        if occurred_at is not None and (not isinstance(occurred_at, str) or len(occurred_at) > 40):
            raise PublicContractError(f"observations[{index}].occurred_at must be a short string.")
        result.append({
            "text": text,
            "source": source.strip(),
            "confidence": confidence,
            "occurred_at": occurred_at,
        })
    return result


__all__ = [
    "ATTACHMENT_STYLES",
    "BIG_FIVE",
    "MBTI_TYPES",
    "MODES",
    "SUBJECT_TYPES",
    "PublicContractError",
    "TIME_ACCURACIES",
    "normalize_public_name",
    "validate_mode",
    "validate_subject_type",
    "validate_observations",
    "validate_psychology",
]
