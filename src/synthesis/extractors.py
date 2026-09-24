"""Fail-closed evidence extractors over structured analysis data."""

from __future__ import annotations

import re
from typing import Callable

from .contracts import (
    EVIDENCE_ID_SCHEME_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    MAPPING_POLICY_VERSION,
    POLICY_VERSIONS,
    PROHIBITED_TOPICS,
    SYMBOLIC_LIMITATION,
)
from .ontology import mapping_for
from .replay import content_digest, namespaced_id


def _slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")[:48] or "value"


def _evidence_id(
    system: str,
    path: str,
    value: object,
    *,
    analysis_id: str | None = None,
    record_id: str | None = None,
    source_contract_id: str | None = None,
    mapping_version: str | None = None,
) -> str:
    digest = content_digest({
        "scheme_version": EVIDENCE_ID_SCHEME_VERSION,
        "analysis_id": analysis_id,
        "record_id": record_id,
        "system": system,
        "source_path": path,
        "source_value": value,
        "source_contract_id": source_contract_id,
        "mapping_version": mapping_version,
    })
    return f"ev_v2_{_slug(system)}_{_slug(path.rsplit('.', 1)[-1])}_{digest}"


def _item(
    *, system: str, subsystem: str, source_path: str, value: object,
    symbol_family: str, ontology_system: str | None = None, role: str = "other",
    epistemic_class: str = "deterministic_calculation", confidence: str = "high",
    provenance_ref: str, atlas_targets: list[str], report_target: str,
    limitations: list[str] | None = None, independence_group: str | None = None,
    interpretation_class: str | None = None, claim_eligible: bool = True,
) -> dict:
    mapping_source_system = ontology_system or system
    mapping = mapping_for(mapping_source_system, value)
    inferred_interpretation = (
        "user_supplied" if epistemic_class == "user_supplied"
        else "traditional_symbolic_interpretation" if mapping
        else "none"
    )
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
        "mapping_source_system": mapping_source_system,
        "mapping_strength": mapping["strength"] if mapping else None,
        "mapping_provenance": MAPPING_POLICY_VERSION if mapping else None,
        "mapping_notes": mapping["notes"] if mapping else None,
        "mapping_rejected": None,
        "epistemic_class": epistemic_class,
        "interpretation_class": interpretation_class or inferred_interpretation,
        "claim_eligible": bool(claim_eligible),
        "confidence": confidence,
        "support_strength": confidence,
        "provenance_ref": provenance_ref,
        "atlas_targets": atlas_targets,
        "report_target": report_target,
        "limitations": limitations or ([SYMBOLIC_LIMITATION] if mapping else []),
        "independence_group": independence_group or system,
    }


def _record_payload_for_item(item: dict, analysis_id: str) -> dict:
    return {
        "schema_version": "system-result-v2",
        "analysis_id": analysis_id,
        "system": item["system"],
        "subsystem": item["subsystem"],
        "source_path": item["source_path"],
        "source_value": item["source_value"],
        "provenance_ref": item["source_contract_id"],
        "epistemic_class": item["epistemic_class"],
        "interpretation_class": item["interpretation_class"],
        "claim_eligible": item["claim_eligible"],
        "mapping_source_system": item.get("mapping_source_system"),
        "interpretive_tags": item.get("interpretive_tags") or [],
        "mapping_strength": item.get("mapping_strength"),
        "mapping_provenance": item.get("mapping_provenance"),
        "mapping_notes": item.get("mapping_notes"),
        "independence_group": item["independence_group"],
        "limitations": item.get("limitations") or [],
    }


def evidence_packet_digest(packet: dict) -> str:
    material = {key: value for key, value in packet.items() if key != "packet_digest"}
    return content_digest(material)


def validate_evidence_packet_integrity(packet: dict) -> str:
    if packet.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        raise ValueError(f"Unsupported evidence schema: {packet.get('schema_version')!r}.")
    analysis_id = packet.get("analysis_id")
    if not isinstance(analysis_id, str) or not analysis_id:
        raise ValueError("Evidence packet requires a non-empty analysis_id.")

    items = packet.get("evidence_items")
    if not isinstance(items, list):
        raise ValueError("Evidence packet evidence_items must be a list.")

    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Evidence records must be objects.")
        if item.get("packet_schema_version") != EVIDENCE_SCHEMA_VERSION:
            raise ValueError("Mixed or unsupported evidence record version.")
        if item.get("analysis_id") != analysis_id:
            raise ValueError("Evidence record analysis binding mismatch.")
        if item.get("mapping_version") != item.get("mapping_provenance"):
            raise ValueError("Evidence mapping-version binding mismatch.")
        if item.get("source_contract_id") != item.get("provenance_ref"):
            raise ValueError("Evidence source-contract provenance mismatch.")
        source_hash = content_digest(item.get("source_value"))
        if item.get("source_value_sha256") != source_hash:
            raise ValueError(f"Evidence source-value digest mismatch: {item.get('evidence_id', 'unknown')}.")
        expected_record_id = namespaced_id("sys_v2", _record_payload_for_item(item, analysis_id))
        if item.get("record_id") != expected_record_id:
            raise ValueError(f"Evidence record identity mismatch: {item.get('evidence_id', 'unknown')}.")
        expected_evidence_id = _evidence_id(
            item["system"],
            item["source_path"],
            item.get("source_value"),
            analysis_id=analysis_id,
            record_id=expected_record_id,
            source_contract_id=item.get("source_contract_id"),
            mapping_version=item.get("mapping_version"),
        )
        if item.get("evidence_id") != expected_evidence_id:
            raise ValueError(f"Evidence identity mismatch: {item.get('evidence_id', 'unknown')}.")
        if expected_evidence_id in seen:
            raise ValueError("Duplicate evidence identity in active synthesis packet.")
        seen.add(expected_evidence_id)

    computed = evidence_packet_digest(packet)
    supplied = packet.get("packet_digest")
    if supplied is not None and supplied != computed:
        raise ValueError("Evidence packet digest mismatch.")
    return computed


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



ROADMAP_EVIDENCE_CONFIG = {
    "alchemical_transformation": (("stage", "stage_index"), "name_derived_symbolic"),
    "apollonius": (("total_value", "reduced_total", "dominant_planet", "primary_virtue", "divine_contemplation"), "name_derived_symbolic"),
    "arabic_abjad": (("abjad_total", "reduced", "input_mode"), "name_derived_symbolic"),
    "babylonian_planetary": (("planet", "chaldean_order_index"), "name_derived_symbolic"),
    "cuneiform_magic": (("sign_count", "lexical_decoding", "scope"), "name_derived_symbolic"),
    "egyptian": (("decan_index", "decan_scope", "hieroglyphic_unicode_count", "uniliteral_transliteration"), "mixed_symbolic"),
    "egyptian_maat": (("symbolic_balance", "vowels", "consonants", "scope"), "name_derived_symbolic"),
    "elder_futhark": (("rune_total", "unmapped_latin"), "name_derived_symbolic"),
    "esoteric_bridge": (("bridge_type", "birth_data_used", "scope"), "crosswalk_comparison"),
    "hermes_thoth_nabu": (("letter_total", "scope"), "name_derived_symbolic"),
    "hermetic_principles": (("principle", "principle_index"), "name_derived_symbolic"),
    "indus_valley": (("symbol_count", "undeciphered"), "name_derived_symbolic"),
    "mandaean_duodecimal": (("decimal_total", "scope"), "name_derived_symbolic"),
    "mayan_tzolkin": (("available", "correlation", "tzolkin_day", "tzolkin_number"), "birth_derived_symbolic"),
    "ogham": (("tree_count",), "name_derived_symbolic"),
    "sacred_geometry": (("digital_root", "polygon_sides", "tetractys_layer", "geometric_operation"), "name_derived_symbolic"),
    "solomonic": (("shem_index", "planet", "entity_name_included", "scope"), "name_derived_symbolic"),
    "sumerian_me_ontology": (("source_text_id", "named_item_count", "category_count", "evidence_layer", "identity_input_used", "personal_mapping_policy", "attestation_status"), "historical_reference"),
    "sumerian_sexagesimal": (("decimal_total", "place_value_base"), "name_derived_symbolic"),
    "tartaria_architecture": (("proportion_index", "polygon_sides", "historical_claim_status", "scope"), "name_derived_symbolic"),
    "temporal_numerology": (("available", "life_path", "birthday_number", "personal_year", "as_of_year"), "birth_derived_symbolic"),
    "unicode_codepoint": (("codepoint_sum", "utf8_byte_length"), "name_derived_symbolic"),
    "vedic_jyotish": (("birth_data_available", "calculation_status", "nakshatra", "scope"), "birth_derived_symbolic"),
}


def extract_binary_prime(signature: dict, _psychology: dict | None) -> list[dict]:
    data = (signature.get("encoders") or {}).get("binary_prime") or {}
    items = []
    for field in ("prime_reduced", "binary_weight", "polarity_ratio", "binary_entropy"):
        value = data.get(field)
        if value is None or isinstance(value, (dict, list)):
            continue
        items.append(_item(
            system="binary_prime", subsystem=field,
            source_path=f"signature.encoders.binary_prime.{field}", value=value,
            symbol_family=f"binary_prime_{field}", ontology_system="reading_only",
            epistemic_class="deterministic_calculation",
            provenance_ref=f"signature-v2:binary_prime:{field}",
            atlas_targets=["system:binary_prime"], report_target="name-calculations",
            limitations=["This is a deterministic transform of the supplied name string, not a measurement of the person."],
            independence_group="name_structure",
        ))
    return items


def extract_roadmap_envelopes(signature: dict, _psychology: dict | None) -> list[dict]:
    encoders = signature.get("encoders") or {}
    items = []
    for system, (fields, independence_group) in ROADMAP_EVIDENCE_CONFIG.items():
        envelope = encoders.get(system) or {}
        data = envelope.get("data") if envelope.get("status") == "computed" else None
        if not isinstance(data, dict):
            continue
        historical = system == "sumerian_me_ontology"
        scope = data.get("scope")
        base_limit = (
            "Historical/textual evidence is preserved without inferring a modern personal mapping."
            if historical else
            "The returned value is deterministic within the named convention; personal meaning remains symbolic or project-authored interpretation."
        )
        for field in fields:
            value = data.get(field)
            if value is None or isinstance(value, (dict, list)):
                continue
            limits = [base_limit, "This record does not independently validate a personal trait."]
            if isinstance(scope, str) and scope and field != "scope":
                limits.append(scope)
            items.append(_item(
                system=system, subsystem=field,
                source_path=f"signature.encoders.{system}.data.{field}",
                value=value, symbol_family=f"roadmap_{system}_{field}",
                ontology_system="reading_only", role="other",
                epistemic_class="historical_textual_reference" if historical else "deterministic_calculation",
                provenance_ref=_envelope_provenance(envelope),
                atlas_targets=[f"system:{system}"], report_target="symbolic-systems",
                limitations=limits, independence_group=independence_group,
            ))
    return items

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
    extract_numerology, extract_name_structure, extract_binary_prime,
    extract_astrology, extract_human_design,
    extract_tree_of_life, extract_chinese, extract_tarot,
    extract_roadmap_envelopes, extract_psychology,
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
        location = "resolved" if (birth.get("location_provided") or birth.get("coordinates_provided") or birth.get("timezone_basis") in {"resolved_iana", "provided_utc_offset"}) else "missing"
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
    source_contracts = {"analysis": "analysis-v1", "signature": "signature-v2", "report": "report-v1"}
    for item in items:
        source_contract_id = item.get("provenance_ref") or "unknown"
        item["packet_schema_version"] = EVIDENCE_SCHEMA_VERSION
        item["analysis_id"] = analysis_id
        item["source_value_sha256"] = content_digest(item["source_value"])
        item["source_contract_id"] = source_contract_id
        item["mapping_version"] = item.get("mapping_provenance")
        item["record_id"] = namespaced_id("sys_v2", _record_payload_for_item(item, analysis_id))
        item["evidence_id"] = _evidence_id(
            item["system"], item["source_path"], item["source_value"],
            analysis_id=analysis_id,
            record_id=item["record_id"],
            source_contract_id=source_contract_id,
            mapping_version=item.get("mapping_provenance"),
        )
    items.sort(key=lambda item: item["evidence_id"])
    if len({item["evidence_id"] for item in items}) != len(items):
        raise ValueError("Duplicate evidence identity in active synthesis packet.")
    packet = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "source_contracts": source_contracts,
        "policy_versions": dict(POLICY_VERSIONS),
        "data_quality": data_quality(signature, psychology),
        "evidence_items": items,
        "unsupported_topics": list(PROHIBITED_TOPICS),
        "warnings": [
            "Interpretive tags use a versioned project-authored ontology.",
            "Repeated records inside one independence group do not count as independent convergence.",
            "Support strength describes this synthesis policy; it is not empirical confidence.",
        ],
    }
    packet["packet_digest"] = evidence_packet_digest(packet)
    validate_evidence_packet_integrity(packet)
    return packet
