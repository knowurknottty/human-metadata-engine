"""Fail-closed evidence extractors over structured analysis data."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Callable

from .contracts import EVIDENCE_SCHEMA_VERSION, PROHIBITED_TOPICS, SYMBOLIC_LIMITATION
from .ontology import mapping_for


def _slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")[:48] or "value"


def _evidence_id(system: str, path: str, value: object) -> str:
    canonical = json.dumps([path, value], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()[:10]
    return f"ev_{_slug(system)}_{_slug(path.rsplit('.', 1)[-1])}_{digest}"


def _item(
    *, system: str, subsystem: str, source_path: str, value: object,
    symbol_family: str, ontology_system: str | None = None, role: str = "other",
    epistemic_class: str = "deterministic_calculation", confidence: str = "high",
    provenance_ref: str, atlas_targets: list[str], report_target: str,
    limitations: list[str] | None = None, independence_group: str | None = None,
) -> dict:
    mapping = mapping_for(ontology_system or system, value)
    return {
        "evidence_id": _evidence_id(system, source_path, value),
        "system": system,
        "subsystem": subsystem,
        "source_path": source_path,
        "source_value": value,
        "normalized_symbol": _slug(value),
        "symbol_family": symbol_family,
        "role": role,
        "interpretive_tags": list(mapping["motifs"]) if mapping else [],
        "mapping_strength": mapping["strength"] if mapping else None,
        "mapping_provenance": "project-authored-symbolic-normalization-v1" if mapping else None,
        "mapping_notes": mapping["notes"] if mapping else None,
        "epistemic_class": epistemic_class,
        "interpretation_class": (
            "user_supplied" if epistemic_class == "user_supplied"
            else "traditional_symbolic_interpretation" if mapping
            else "none"
        ),
        "confidence": confidence,
        "provenance_ref": provenance_ref,
        "atlas_targets": atlas_targets,
        "report_target": report_target,
        "limitations": limitations or ([SYMBOLIC_LIMITATION] if mapping else []),
        "independence_group": independence_group or system,
    }


def extract_numerology(signature: dict, _psychology: dict | None) -> list[dict]:
    enc = signature.get("encoders") or {}
    fields = [
        ("pythagorean", "expression"), ("pythagorean", "soul_urge"),
        ("pythagorean", "personality"), ("chaldean", "name_number"),
        ("ordinal", "ordinal_reduced"), ("gematria", "absolute_reduced"),
        ("isopsephy", "reduced"),
    ]
    items = []
    for system, field in fields:
        value = (enc.get(system) or {}).get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        items.append(_item(
            system=system, subsystem="name_number", source_path=f"signature.encoders.{system}.{field}",
            value=value, symbol_family="reduced_number", ontology_system="numerology",
            role="identity", provenance_ref=f"signature-v2:{system}:{field}",
            atlas_targets=[f"numerology:{system}", f"value:{value}"], report_target="name-calculations",
            independence_group="name_number",
        ))
    return items


def extract_name_structure(signature: dict, _psychology: dict | None) -> list[dict]:
    linguistic = (signature.get("encoders") or {}).get("linguistic") or {}
    items = []
    for field in ("letter_count", "unique_letters", "entropy_ratio", "vowel_ratio", "syllable_estimate"):
        value = linguistic.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        items.append(_item(
            system="linguistic", subsystem="measurable_name_structure",
            source_path=f"signature.encoders.linguistic.{field}", value=value,
            symbol_family="name_measurement", role="other", epistemic_class="deterministic_calculation",
            provenance_ref=f"signature-v2:linguistic:{field}", atlas_targets=["system:linguistic"],
            report_target="name-calculations", limitations=["This measures the name string, not the person."],
            independence_group="name_structure",
        ))
    return items


def extract_astrology(signature: dict, _psychology: dict | None) -> list[dict]:
    astrology = (signature.get("encoders") or {}).get("astrology") or {}
    if astrology.get("error") or not astrology.get("sun_sign"):
        return []
    provenance = astrology.get("calculation_engine") or "signature-v2 astrology calculation"
    planet_index = {item.get("planet"): item for item in astrology.get("planets") or []}
    fields = [("sun_sign", "Sun", "identity"), ("moon_sign", "Moon", "emotion")]
    if not astrology.get("time_sensitive_fields_withheld"):
        fields.append(("ascendant", None, "visibility"))
    items = []
    for field, planet, role in fields:
        value = astrology.get(field)
        if not value:
            continue
        target = f"planet:{planet}" if planet and planet in planet_index else "system:astrology"
        items.append(_item(
            system="astrology", subsystem="planetary_position", source_path=f"signature.encoders.astrology.{field}",
            value=value, symbol_family="zodiac_sign", ontology_system="astrology_sign", role=role,
            provenance_ref=provenance, atlas_targets=[target], report_target="birth-chart",
            independence_group="astrology",
        ))
    for field, ontology_system, family in (
        ("dominant_element", "astrology_element", "element"),
        ("dominant_modality", "astrology_modality", "modality"),
    ):
        value = astrology.get(field)
        if value:
            items.append(_item(
                system="astrology", subsystem=field, source_path=f"signature.encoders.astrology.{field}",
                value=value, symbol_family=family, ontology_system=ontology_system,
                provenance_ref=provenance, atlas_targets=["system:astrology"], report_target="birth-chart",
                independence_group="astrology",
            ))
    for index, planet in enumerate(astrology.get("planets") or []):
        if not planet.get("planet") or not planet.get("sign"):
            continue
        # Withheld charts must not reintroduce time-sensitive fields through a
        # compound placement record, even if an upstream caller supplies them.
        fields_to_read = ["sign"] if astrology.get("time_sensitive_fields_withheld") else ["sign", "house", "retrograde"]
        for field in fields_to_read:
            value = planet.get(field)
            if value is None:
                continue
            items.append(_item(
                system="astrology", subsystem=f"planet_{field}",
                source_path=f"signature.encoders.astrology.planets.{index}.{field}", value=value,
                symbol_family=f"planet_{field}", role=planet["planet"],
                ontology_system="reading_only", provenance_ref=provenance,
                atlas_targets=[f"planet:{planet['planet']}"], report_target="birth-chart",
                limitations=[SYMBOLIC_LIMITATION], independence_group="astrology",
            ))
    for index, aspect in enumerate(astrology.get("aspects") or []):
        planets = aspect.get("planets") or []
        if len(planets) != 2 or not aspect.get("type"):
            continue
        value = dict(aspect)
        items.append(_item(
            system="astrology", subsystem="aspect", source_path=f"signature.encoders.astrology.aspects.{index}",
            value=value, symbol_family="aspect", role="relationship",
            epistemic_class="deterministic_relationship", confidence="high",
            provenance_ref=provenance, atlas_targets=[f"aspect:{index}"], report_target="birth-chart",
            limitations=["The geometric aspect is calculated; its personal meaning is traditional interpretation."],
            independence_group="astrology",
        ))
    return items


def extract_human_design(signature: dict, _psychology: dict | None) -> list[dict]:
    hd = (signature.get("encoders") or {}).get("human_design") or {}
    if hd.get("available") is not True or hd.get("status") != "provisional_calculation":
        return []
    provenance = hd.get("calculation_standard") or hd.get("calculation_engine") or "true-human-design-core-v1"
    items = []
    for field, ontology_system in (("type", "human_design_type"), ("strategy", "human_design_strategy")):
        value = hd.get(field)
        if value:
            items.append(_item(
                system="human_design", subsystem=field, source_path=f"signature.encoders.human_design.{field}",
                value=value, symbol_family=f"human_design_{field}", ontology_system=ontology_system,
                provenance_ref=provenance, atlas_targets=["system:human_design"], report_target="human-design",
                independence_group="human_design",
            ))
    for field in ("authority", "profile", "definition"):
        value = hd.get(field)
        if value is not None:
            items.append(_item(
                system="human_design", subsystem=field,
                source_path=f"signature.encoders.human_design.{field}", value=value,
                symbol_family=f"human_design_{field}", ontology_system="reading_only",
                provenance_ref=provenance, atlas_targets=["system:human_design"],
                report_target="human-design", limitations=[SYMBOLIC_LIMITATION], independence_group="human_design",
            ))
    for index, gate in enumerate(hd.get("gates") or []):
        if not isinstance(gate, int) or not 1 <= gate <= 64:
            continue
        items.append(_item(
            system="human_design", subsystem="active_gate", source_path=f"signature.encoders.human_design.gates.{index}",
            value=gate, symbol_family="human_design_gate", epistemic_class="deterministic_relationship",
            provenance_ref=provenance, atlas_targets=[f"gate:{gate}"], report_target="human-design",
            limitations=[SYMBOLIC_LIMITATION], independence_group="human_design",
        ))
    for index, channel in enumerate(hd.get("channels") or []):
        gates = channel.get("gates") or []
        if len(gates) != 2:
            continue
        items.append(_item(
            system="human_design", subsystem="channel", source_path=f"signature.encoders.human_design.channels.{index}",
            value=dict(channel), symbol_family="human_design_channel",
            epistemic_class="deterministic_relationship", provenance_ref=provenance,
            atlas_targets=[f"channel:{'-'.join(str(g) for g in gates)}"], report_target="human-design",
            limitations=[SYMBOLIC_LIMITATION], independence_group="human_design",
        ))
    for index, center in enumerate(hd.get("centers") or []):
        if not isinstance(center.get("defined"), bool) or not center.get("name"):
            continue
        items.append(_item(
            system="human_design", subsystem="center_state", source_path=f"signature.encoders.human_design.centers.{index}",
            value=dict(center), symbol_family="human_design_center", epistemic_class="deterministic_relationship",
            provenance_ref=provenance, atlas_targets=[f"center:{center['name']}"], report_target="human-design",
            limitations=[SYMBOLIC_LIMITATION], independence_group="human_design",
        ))
    return items


def _envelope_provenance(envelope: dict) -> str:
    provenance = envelope.get("provenance") or {}
    ids = provenance.get("source_ids") or []
    return ":".join([provenance.get("convention") or "versioned-convention", *map(str, ids)])


def extract_tree_of_life(signature: dict, _psychology: dict | None) -> list[dict]:
    envelope = (signature.get("encoders") or {}).get("kabbalah_tree_of_life") or {}
    data = envelope.get("data") if envelope.get("status") == "computed" else None
    value = data.get("dominant_sephirah") if isinstance(data, dict) else None
    if not value:
        return []
    return [_item(
        system="kabbalah_tree_of_life", subsystem="dominant_sephirah",
        source_path="signature.encoders.kabbalah_tree_of_life.data.dominant_sephirah", value=value,
        symbol_family="sephirah", ontology_system="tree_of_life", provenance_ref=_envelope_provenance(envelope),
        atlas_targets=[f"sephirah:{value}"], report_target="name-calculations",
        independence_group="tree_of_life",
    )]


def extract_chinese(signature: dict, _psychology: dict | None) -> list[dict]:
    envelope = (signature.get("encoders") or {}).get("chinese") or {}
    data = envelope.get("data") if envelope.get("status") == "computed" else None
    if not isinstance(data, dict):
        return []
    items = []
    value = data.get("wu_xing_element")
    if value:
        items.append(_item(
            system="chinese", subsystem="wu_xing", source_path="signature.encoders.chinese.data.wu_xing_element",
            value=value, symbol_family="wu_xing_element", ontology_system="wu_xing",
            provenance_ref=_envelope_provenance(envelope), atlas_targets=["system:chinese"],
            report_target="name-calculations", independence_group="chinese_symbolic",
        ))
    for field, family in (("iching_hexagram_index", "iching_hexagram"), ("trigram", "iching_trigram")):
        value = data.get(field)
        if value not in (None, ""):
            items.append(_item(
                system="chinese", subsystem=field, source_path=f"signature.encoders.chinese.data.{field}",
                value=value, symbol_family=family, provenance_ref=_envelope_provenance(envelope),
                atlas_targets=["system:chinese"], report_target="name-calculations",
                limitations=[SYMBOLIC_LIMITATION], independence_group="chinese_symbolic",
            ))
    return items


def extract_tarot(signature: dict, _psychology: dict | None) -> list[dict]:
    envelope = (signature.get("encoders") or {}).get("tarot") or {}
    data = envelope.get("data") if envelope.get("status") == "computed" else None
    if not isinstance(data, dict):
        return []
    index = data.get("major_arcana_index")
    if type(index) is not int or not 0 <= index < 22:
        return []
    return [_item(
        system="tarot", subsystem="name_correspondence",
        source_path="signature.encoders.tarot.data.major_arcana_index", value=index,
        symbol_family="tarot_correspondence", ontology_system="reading_only",
        provenance_ref=_envelope_provenance(envelope), atlas_targets=["system:tarot"],
        report_target="name-calculations", independence_group="name_number",
        limitations=["A deterministic name-derived correspondence, not a shuffled card draw.", SYMBOLIC_LIMITATION],
    )]


def extract_psychology(_signature: dict, psychology: dict | None) -> list[dict]:
    if not psychology:
        return []
    items = []
    mbti = psychology.get("mbti")
    if isinstance(mbti, str) and len(mbti) == 4:
        for index, preference in enumerate(mbti):
            items.append(_item(
                system="user_context", subsystem="mbti_preference", source_path=f"psychology.mbti.{index}",
                value=preference, symbol_family="self_report", ontology_system="psychology_mbti_axis",
                epistemic_class="user_supplied", confidence="medium", provenance_ref="public request psychology field",
                atlas_targets=["system:user_context"], report_target="personal-context-report",
                limitations=["User supplied; not calculated or independently verified."], independence_group="user_context",
            ))
    for field in ("mbti", "secondary_enneagram_influence", "instinctual_variant", "conflict_style"):
        value = psychology.get(field)
        if value in (None, ""):
            continue
        ontology_system = "psychology_conflict" if field == "conflict_style" else None
        items.append(_item(
            system="user_context", subsystem=field, source_path=f"psychology.{field}", value=value,
            symbol_family="self_report", ontology_system=ontology_system,
            epistemic_class="user_supplied", confidence="medium",
            provenance_ref="public request psychology field", atlas_targets=["system:user_context"],
            report_target="personal-context-report",
            limitations=["User supplied; not calculated or independently verified."], independence_group="user_context",
        ))
    enneagram = psychology.get("enneagram") or {}
    if enneagram.get("type"):
        items.append(_item(
            system="user_context", subsystem="enneagram", source_path="psychology.enneagram.type",
            value=enneagram["type"], symbol_family="self_report", epistemic_class="user_supplied",
            confidence="medium", provenance_ref="public request psychology field",
            atlas_targets=["system:user_context"], report_target="personal-context-report",
            limitations=["User supplied; not calculated or independently verified."], independence_group="user_context",
        ))
    for trait, value in sorted((psychology.get("big_five") or {}).items()):
        items.append(_item(
            system="user_context", subsystem="big_five", source_path=f"psychology.big_five.{trait}",
            value=value, symbol_family="self_report", epistemic_class="user_supplied", confidence="medium",
            provenance_ref="public request psychology field", atlas_targets=["system:user_context"],
            report_target="personal-context-report",
            limitations=["User supplied; not calculated or independently verified."], independence_group="user_context",
        ))
    return items


EXTRACTORS: tuple[Callable[[dict, dict | None], list[dict]], ...] = (
    extract_numerology, extract_name_structure, extract_astrology, extract_human_design,
    extract_tree_of_life, extract_chinese, extract_tarot, extract_psychology,
)


def data_quality(signature: dict, psychology: dict | None) -> dict:
    normalized = signature.get("normalized_input") or {}
    birth = normalized.get("birth")
    astrology = (signature.get("encoders") or {}).get("astrology") or {}
    hd = (signature.get("encoders") or {}).get("human_design") or {}
    if not birth:
        birth_date, birth_time, location = "missing", "missing", "missing"
    else:
        birth_date = "exact"
        accuracy = birth.get("time_accuracy", "unknown")
        birth_time = accuracy if accuracy in {"exact", "approximate", "unknown"} else "approximate"
        location = "resolved" if birth.get("timezone_name") else "missing"
    astronomy = "unavailable" if not astrology.get("sun_sign") else (
        "partial" if astrology.get("time_sensitive_fields_withheld") else "available"
    )
    return {
        "birth_date": birth_date,
        "birth_time": birth_time,
        "birth_location": location,
        "astronomy": astronomy,
        "human_design": "available" if hd.get("available") is True else "unavailable",
        "psychology": "user_supplied" if psychology else "absent",
    }


def extract_evidence(signature: dict, psychology: dict | None, analysis_id: str) -> dict:
    items: list[dict] = []
    for extractor in EXTRACTORS:
        items.extend(extractor(signature, psychology))
    items.sort(key=lambda item: item["evidence_id"])
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "source_contracts": {"analysis": "analysis-v1", "signature": "signature-v2", "report": "report-v1"},
        "data_quality": data_quality(signature, psychology),
        "evidence_items": items,
        "unsupported_topics": list(PROHIBITED_TOPICS),
        "warnings": [
            "Interpretive tags use a versioned project-authored ontology.",
            "Repeated records inside one independence group do not count as independent convergence.",
        ],
    }
