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
ATTACHMENT_STYLES = {
    "secure", "anxious", "avoidant", "disorganized", "fearful_avoidant",
    "anxious_preoccupied", "dismissive_avoidant", "mixed_context_dependent", "unknown",
}
ASSESSMENT_STATUSES = {"validated", "structured", "self_identified", "provisional", "unknown"}
ENNEAGRAM_WINGS = {
    1: (9, 2), 2: (1, 3), 3: (2, 4), 4: (3, 5), 5: (4, 6),
    6: (5, 7), 7: (6, 8), 8: (7, 9), 9: (8, 1),
}
INSTINCTUAL_VARIANTS = {
    "self_preservation", "social", "one_to_one",
    "sp_so", "sp_sx", "so_sp", "so_sx", "sx_sp", "sx_so", "unknown",
}
CONFLICT_STYLES = {
    "direct", "collaborative", "accommodating", "avoidant", "competitive",
    "context_dependent", "unknown",
}
MBTI_TYPES = {
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
}
BIG_FIVE = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")
_BIDI_OR_CONTROL = re.compile(r"[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]")


class PublicContractError(ValueError):
    """Raised when a request violates the public API contract."""


def _coalesced_alias(raw: dict[str, Any], canonical: str, legacy: str) -> Any:
    canonical_value = raw.get(canonical)
    legacy_value = raw.get(legacy)
    if (
        canonical_value not in (None, "")
        and legacy_value not in (None, "")
        and canonical_value != legacy_value
    ):
        raise PublicContractError(
            f"psychology.{canonical} and psychology.{legacy} disagree."
        )
    return canonical_value if canonical_value not in (None, "") else legacy_value


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
    if "<" in name or ">" in name:
        raise PublicContractError("Name contains unsupported markup characters.")
    # The encoders use the built-in transliteration profile.  Reject values
    # that produce no mapped Latin letters instead of returning an empty score.
    latin = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    if not any("A" <= char.upper() <= "Z" for char in latin):
        raise PublicContractError("Name must contain at least one encodable Latin letter.")
    return name


def validate_aliases(raw: Any, *, primary_name: str, max_items: int = 12) -> list[str]:
    if raw in (None, []):
        return []
    if not isinstance(raw, list):
        raise PublicContractError("aliases must be an array of names.")
    if len(raw) > max_items:
        raise PublicContractError(f"aliases supports at most {max_items} entries.")
    primary_key = primary_name.casefold()
    seen = {primary_key}
    aliases = []
    for index, value in enumerate(raw):
        try:
            alias = normalize_public_name(value)
        except PublicContractError as exc:
            raise PublicContractError(f"aliases[{index}]: {exc}") from exc
        key = alias.casefold()
        if key in seen:
            raise PublicContractError(f"aliases[{index}] duplicates the primary name or another alias.")
        seen.add(key)
        aliases.append(alias)
    return aliases


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


def _validate_assessment_status(raw: Any) -> dict[str, dict[str, Any]]:
    if raw in (None, {}):
        return {}
    if not isinstance(raw, dict):
        raise PublicContractError("assessment_status must be an object.")
    aliases = {
        "secondaryEnneagramInfluence": "secondary_enneagram_influence",
        "instinctualVariant": "instinctual_variant",
        "attachmentStyle": "attachment",
        "conflictStyle": "conflict_style",
    }
    allowed_fields = {
        "big_five", "mbti", "enneagram", "wing", "secondary_enneagram_influence",
        "instinctual_variant", "attachment", "conflict_style",
    }
    result: dict[str, dict[str, Any]] = {}
    for raw_key, metadata in raw.items():
        key = aliases.get(raw_key, raw_key)
        if key not in allowed_fields:
            raise PublicContractError(f"assessment_status contains unsupported field: {raw_key}.")
        if not isinstance(metadata, dict):
            raise PublicContractError(f"assessment_status.{raw_key} must be an object.")
        unknown = set(metadata) - {"status", "assessed_at", "source", "notes"}
        if unknown:
            raise PublicContractError(
                f"assessment_status.{raw_key} contains unsupported fields: {', '.join(sorted(unknown))}."
            )
        status = metadata.get("status", "unknown")
        if status not in ASSESSMENT_STATUSES:
            raise PublicContractError(
                f"assessment_status.{raw_key}.status must be one of: {', '.join(sorted(ASSESSMENT_STATUSES))}."
            )
        assessed_at = metadata.get("assessed_at")
        source = metadata.get("source")
        notes = metadata.get("notes")
        if assessed_at is not None and (not isinstance(assessed_at, str) or len(assessed_at) > 40):
            raise PublicContractError(f"assessment_status.{raw_key}.assessed_at must be a short string or null.")
        if source is not None and (not isinstance(source, str) or len(source.strip()) > 120):
            raise PublicContractError(f"assessment_status.{raw_key}.source must be a short string or null.")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 500):
            raise PublicContractError(f"assessment_status.{raw_key}.notes must be at most 500 characters or null.")
        clean = {"status": status}
        if assessed_at is not None:
            clean["assessed_at"] = assessed_at
        if source is not None:
            clean["source"] = source.strip()
        if notes is not None:
            clean["notes"] = notes
        result[key] = clean
    return result


def validate_psychology(raw: Any) -> dict[str, Any] | None:
    """Validate and canonicalize user-supplied self-knowledge fields.

    ``relational_patterns.attachment_style`` is the canonical attachment path.
    The legacy top-level ``attachment`` alias is retained in normalized output
    for existing consumers. If both paths are supplied they must match exactly;
    there is intentionally no silent precedence rule for conflicting values.
    """
    if raw in (None, {}):
        return None
    if not isinstance(raw, dict):
        raise PublicContractError("psychology must be an object.")
    unknown = sorted(set(raw) - {
        "big_five", "mbti", "enneagram", "attachment", "relational_patterns",
        "secondary_enneagram_influence", "secondaryEnneagramInfluence",
        "instinctual_variant", "instinctualVariant", "assessment_status",
        "assessmentStatus", "conflict_style", "conflictStyle",
    })
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
        if wing is not None and wing not in ENNEAGRAM_WINGS[core_type]:
            allowed_wings = ", ".join(str(value) for value in ENNEAGRAM_WINGS[core_type])
            raise PublicContractError(
                f"psychology.enneagram.wing must be adjacent to core type {core_type} ({allowed_wings})."
            )
        result["enneagram"] = {"type": core_type, "wing": wing}

    secondary = _coalesced_alias(
        raw, "secondary_enneagram_influence", "secondaryEnneagramInfluence"
    )
    if secondary not in (None, "", "unknown"):
        if isinstance(secondary, bool) or not isinstance(secondary, int) or not 1 <= secondary <= 9:
            raise PublicContractError("psychology.secondary_enneagram_influence must be an integer from 1 to 9 or null.")
        result["secondary_enneagram_influence"] = secondary
    elif secondary == "unknown":
        result["secondary_enneagram_influence"] = None

    instinctual = _coalesced_alias(raw, "instinctual_variant", "instinctualVariant")
    if instinctual not in (None, ""):
        if instinctual not in INSTINCTUAL_VARIANTS:
            raise PublicContractError(
                "psychology.instinctual_variant must be a supported dominant or stacked variant."
            )
        result["instinctual_variant"] = instinctual

    attachment = raw.get("attachment")
    relational = raw.get("relational_patterns")
    if relational is not None:
        if not isinstance(relational, dict) or set(relational) - {"attachment_style"}:
            raise PublicContractError("psychology.relational_patterns only accepts attachment_style.")
        relational_attachment = relational.get("attachment_style")
        if attachment not in (None, "") and relational_attachment not in (None, "", attachment):
            raise PublicContractError("psychology.attachment and psychology.relational_patterns.attachment_style disagree.")
        if attachment in (None, ""):
            attachment = relational_attachment
    if attachment not in (None, ""):
        if attachment not in ATTACHMENT_STYLES:
            raise PublicContractError(
                "psychology.attachment must be one of: " + ", ".join(sorted(ATTACHMENT_STYLES)) + "."
            )
        result["attachment"] = attachment
        result["relational_patterns"] = {"attachment_style": attachment}

    conflict_style = _coalesced_alias(raw, "conflict_style", "conflictStyle")
    if conflict_style not in (None, ""):
        if conflict_style not in CONFLICT_STYLES:
            raise PublicContractError("psychology.conflict_style is not a supported self-observation value.")
        result["conflict_style"] = conflict_style

    statuses = _validate_assessment_status(
        _coalesced_alias(raw, "assessment_status", "assessmentStatus")
    )
    supplied_fields = set(result)
    if "relational_patterns" in supplied_fields:
        supplied_fields.add("attachment")
    if isinstance(result.get("enneagram"), dict) and result["enneagram"].get("wing") is not None:
        supplied_fields.add("wing")
    for field in (
        "big_five", "mbti", "enneagram", "secondary_enneagram_influence",
        "instinctual_variant", "attachment", "conflict_style",
    ):
        if field in supplied_fields and field not in statuses:
            statuses[field] = {"status": "self_identified"}
    if statuses:
        result["assessment_status"] = statuses

    value_fields = set(result) - {"assessment_status", "relational_patterns"}
    if not value_fields:
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
    "ASSESSMENT_STATUSES",
    "BIG_FIVE",
    "CONFLICT_STYLES",
    "ENNEAGRAM_WINGS",
    "INSTINCTUAL_VARIANTS",
    "MBTI_TYPES",
    "MODES",
    "SUBJECT_TYPES",
    "PublicContractError",
    "TIME_ACCURACIES",
    "normalize_public_name",
    "validate_aliases",
    "validate_mode",
    "validate_subject_type",
    "validate_observations",
    "validate_psychology",
]
