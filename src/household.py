"""Household composition contracts for paid multi-subject Human Manual modes.

This module intentionally sits above analysis-v1. It never changes the single-subject
engine, never mints entitlements, and never treats relational structure as compatibility.
"""

from __future__ import annotations

import re
import secrets
from itertools import combinations
from typing import Any

from encoders.pipeline import encode_selected_symbolic_systems
from synthesis.replay import content_digest

HOUSEHOLD_VERSION = "household-v1"
RELATIONAL_VIEW_VERSION = "relational-view-v1"
CHILD_PROFILE_VERSION = "child-profile-v1"
PET_PROFILE_VERSION = "pet-profile-v1"
ENTITLEMENT_VERSION = "entitlement-v1"
HOUSEHOLD_REPORT_VERSION = "report-household-v1"
HOUSEHOLD_PROJECTION_VERSION = "household-subject-projection-v1"

COMPOSITIONS = {"pair", "household"}
SUBJECT_ROLES = {"primary", "partner", "adult_family", "child", "pet", "reference"}
SUBJECT_CLASSES = {"person_adult", "person_minor", "nonhuman_animal", "historical_reference"}
MEMBERSHIPS = {"member", "context_only"}
RECORD_STATES = {"resolved", "stale", "unresolved"}
INPUT_STATES = {"ready", "partial", "stale", "unresolved"}
SYSTEM_STATES = {"complete", "partial", "unavailable", "missing"}
EVIDENCE_STATES = {"complete", "partial", "missing"}

ROLE_CLASS = {
    "primary": "person_adult",
    "partner": "person_adult",
    "adult_family": "person_adult",
    "child": "person_minor",
    "pet": "nonhuman_animal",
    "reference": "historical_reference",
}
ROLE_RELATIONSHIP = {
    "primary": "self",
    "partner": "partner",
    "adult_family": "adult_family",
    "child": "household_member",
    "pet": "animal_care",
    "reference": "reference_context",
}
ROLE_RECORD_CONTRACT = {
    "primary": "analysis-v1",
    "partner": "analysis-v1",
    "adult_family": "analysis-v1",
    "child": CHILD_PROFILE_VERSION,
    "pet": PET_PROFILE_VERSION,
    "reference": "historical-reference-v1",
}

CHILD_SAFE_SYSTEMS = (
    "unicode_codepoint",
    "sumerian_sexagesimal",
    "mandaean_duodecimal",
    "elder_futhark",
    "ogham",
)
CHILD_BIRTH_OPTIONAL_SYSTEMS: tuple[str, ...] = ()
CHILD_LABEL = (
    "Child-safe symbolic worksheet — guardian-supplied input; not predictive, "
    "diagnostic, or a claim about the child's character or future."
)
PET_LABEL = "Pet profile — care context only; no symbolic or health interpretation."
REFERENCE_LABEL = "Historical reference — source context only."
ADULT_LABEL = "Personal symbolic analysis."

FORBIDDEN_RELATIONAL_INFERENCES = (
    "compatibility",
    "soulmate",
    "best_fit",
    "ranking",
    "fate",
    "destiny",
    "parenting_suitability",
    "child_potential",
    "fertility",
    "developmental_prediction",
    "pet_diagnosis",
    "pet_temperament_diagnosis",
    "health_prediction",
    "cross_tradition_agreement",
    "relationship_outcome_prediction",
)

_SUBJECT_ID = re.compile(r"^subj_[0-9a-f]{32}$")
_HOUSEHOLD_ID = re.compile(r"^hh_[0-9a-f]{24}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class HouseholdContractError(ValueError):
    """Raised when a household composition violates the public contract."""


def new_subject_id() -> str:
    return "subj_" + secrets.token_hex(16)


def new_household_id() -> str:
    return "hh_" + secrets.token_hex(12)


def record_digest(payload: dict[str, Any]) -> str:
    return "sha256:" + content_digest(payload)


def _bounded_text(value: Any, *, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise HouseholdContractError(f"{field} must be a string.")
    cleaned = value.strip()
    if not cleaned or len(cleaned) > max_length:
        raise HouseholdContractError(f"{field} must contain 1-{max_length} characters.")
    if any(ord(char) < 32 or char in "<>" for char in cleaned):
        raise HouseholdContractError(f"{field} contains unsupported characters.")
    return cleaned


def _validate_authority(authority: Any, *, role: str) -> dict[str, Any]:
    if not isinstance(authority, dict):
        raise HouseholdContractError(f"{role} requires an authority block.")
    kind = authority.get("kind")
    allowed = {
        "primary": {"self_attested"},
        "partner": {"self_attested", "adult_consent_attested"},
        "adult_family": {"self_attested", "adult_consent_attested"},
        "child": {"guardian_attested"},
        "pet": {"owner_attested"},
        "reference": {"public_source"},
    }[role]
    if kind not in allowed:
        raise HouseholdContractError(f"{role} authority must be one of {sorted(allowed)}.")
    version = authority.get("attestation_version")
    if version != "authority-v1":
        raise HouseholdContractError("authority.attestation_version must be authority-v1.")
    return {"kind": kind, "attestation_version": version}


def build_child_profile(
    *,
    subject_id: str,
    display_alias: str,
    age_band: str,
    authority: dict[str, Any],
    birth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build only the narrow child-safe worksheet; adult engines are never invoked."""

    if not _SUBJECT_ID.fullmatch(subject_id):
        raise HouseholdContractError("Invalid child subject_id.")
    alias = _bounded_text(display_alias, field="display_alias", max_length=80)
    if age_band not in {"child", "adolescent"}:
        raise HouseholdContractError("age_band must be child or adolescent.")
    normalized_authority = _validate_authority(authority, role="child")
    selected = list(CHILD_SAFE_SYSTEMS)
    if isinstance(birth, dict) and all(birth.get(key) is not None for key in ("year", "month", "day")):
        selected.extend(CHILD_BIRTH_OPTIONAL_SYSTEMS)
    worksheets = encode_selected_symbolic_systems(alias, systems=selected, birth=birth)
    payload = {
        "contract_version": CHILD_PROFILE_VERSION,
        "subject_id": subject_id,
        "subject_class": "person_minor",
        "age_band": age_band,
        "authority": normalized_authority,
        "label": CHILD_LABEL,
        "interpretation_policy": "structure_only",
        "worksheets": worksheets,
        "forbidden_inferences": list(FORBIDDEN_RELATIONAL_INFERENCES),
    }
    payload["record_digest"] = record_digest(payload)
    return payload


def build_pet_profile(
    *,
    subject_id: str,
    display_alias: str,
    species: str,
    authority: dict[str, Any],
    breed: str | None = None,
    age_band: str = "unknown",
) -> dict[str, Any]:
    """Build a care-context record without invoking any human symbolic engine."""

    if not _SUBJECT_ID.fullmatch(subject_id):
        raise HouseholdContractError("Invalid pet subject_id.")
    alias = _bounded_text(display_alias, field="display_alias", max_length=80)
    species_value = _bounded_text(species, field="species", max_length=80)
    breed_value = None if breed in (None, "") else _bounded_text(breed, field="breed", max_length=120)
    if age_band not in {"unknown", "juvenile", "adult", "senior"}:
        raise HouseholdContractError("Unsupported pet age_band.")
    normalized_authority = _validate_authority(authority, role="pet")
    payload = {
        "contract_version": PET_PROFILE_VERSION,
        "subject_id": subject_id,
        "subject_class": "nonhuman_animal",
        "authority": normalized_authority,
        "label": PET_LABEL,
        "care_context": {
            "display_alias": alias,
            "species": species_value,
            "breed": breed_value,
            "age_band": age_band,
        },
        "symbolic_systems": {},
        "interpretation_policy": "care_context_only",
        "forbidden_inferences": list(FORBIDDEN_RELATIONAL_INFERENCES),
    }
    payload["record_digest"] = record_digest(payload)
    return payload


COMPARABLE_SIGNATURE_FIELDS: dict[str, tuple[str, ...]] = {
    "pythagorean": ("expression", "soul_urge", "personality", "balance_number"),
    "chaldean": ("name_number",),
    "ordinal": ("ordinal_reduced",),
    "gematria": ("absolute_reduced",),
    "isopsephy": ("reduced",),
    "astrology": ("sun_sign", "moon_sign", "ascendant", "dominant_element", "dominant_modality"),
    "human_design": ("type", "authority", "profile", "definition"),
    "kabbalah_tree_of_life": ("reduced_value", "dominant_sephirah", "tree_depth"),
    "sacred_geometry": ("digital_root", "polygon_sides", "tetractys_layer"),
    "alchemical_transformation": ("stage_index", "stage"),
    "hermetic_principles": ("principle_index", "principle"),
    "tarot": ("major_arcana_index", "major_arcana", "minor_arcana_suit", "minor_arcana_rank"),
    "babylonian_planetary": ("chaldean_order_index", "planet"),
    "solomonic": ("planet", "shem_index"),
    "arabic_abjad": ("reduced",),
    "chinese": ("iching_hexagram_index", "trigram", "wu_xing_element", "year_pillar"),
    "egyptian": ("decan_index",),
    "mayan_tzolkin": ("tzolkin_number", "tzolkin_day"),
    "egyptian_maat": ("symbolic_balance",),
    "apollonius": ("reduced_total", "dominant_planet", "primary_virtue"),
    "temporal_numerology": ("life_path", "birthday_number", "personal_year"),
}


def _marker_source(system_payload: Any) -> dict[str, Any]:
    if not isinstance(system_payload, dict):
        return {}
    data = system_payload.get("data")
    return data if isinstance(data, dict) else system_payload


def _projection_markers_from_signature(signature: dict[str, Any]) -> list[dict[str, Any]]:
    encoders = signature.get("encoders") or {}
    markers: list[dict[str, Any]] = []
    for system, fields in COMPARABLE_SIGNATURE_FIELDS.items():
        payload = encoders.get(system)
        source = _marker_source(payload)
        if not source:
            continue
        provenance = payload.get("provenance") if isinstance(payload, dict) else None
        provenance_ref = None
        if isinstance(provenance, dict):
            source_ids = provenance.get("source_ids")
            if isinstance(source_ids, list) and source_ids:
                provenance_ref = "|".join(str(value) for value in source_ids)
            elif provenance.get("convention"):
                provenance_ref = str(provenance["convention"])
        for field in fields:
            value = source.get(field)
            if isinstance(value, (str, int, float, bool)) or value is None:
                if value is None:
                    continue
                markers.append({
                    "evidence_id": "household_marker_" + content_digest({
                        "system": system, "field": field, "value": value,
                    }),
                    "system": system,
                    "source_path": f"signature.encoders.{system}.{field}",
                    "source_value": value,
                    "provenance_ref": provenance_ref or f"{system}:signature-v2",
                    "epistemic_class": (
                        payload.get("interpretation_level")
                        if isinstance(payload, dict) and payload.get("interpretation_level")
                        else "deterministic_calculation"
                    ),
                })
    markers.sort(key=lambda item: (item["system"], item["source_path"], item["evidence_id"]))
    return markers


def analysis_record(subject_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """Project a full analysis-v1 result into a privacy-minimized household record."""
    if not _SUBJECT_ID.fullmatch(subject_id):
        raise HouseholdContractError("Invalid adult subject_id.")
    if not isinstance(result, dict) or result.get("contract_version") != "analysis-v1":
        raise HouseholdContractError("Adult household records must originate from analysis-v1 results.")
    if result.get("subject_type") != "self":
        raise HouseholdContractError("Adult household members must use self analysis records.")
    signature = result.get("signature") or {}
    markers = _projection_markers_from_signature(signature)
    projection = {
        "projection_version": HOUSEHOLD_PROJECTION_VERSION,
        "source_contract": "analysis-v1",
        "analysis_id": result.get("input_hash"),
        "systems": sorted(set((signature.get("encoders") or {}).keys()) | set((signature.get("systems") or {}).keys())),
        "markers": markers,
    }
    digest = record_digest(projection)
    return {
        "record_contract": "analysis-v1",
        "subject_id": subject_id,
        "record_digest": digest,
        "payload": projection,
    }


def profile_record(profile: dict[str, Any]) -> dict[str, Any]:
    contract = profile.get("contract_version")
    if contract not in {CHILD_PROFILE_VERSION, PET_PROFILE_VERSION, "historical-reference-v1"}:
        raise HouseholdContractError("Unsupported household profile contract.")
    subject_id = profile.get("subject_id")
    if not isinstance(subject_id, str) or not _SUBJECT_ID.fullmatch(subject_id):
        raise HouseholdContractError("Profile has invalid subject_id.")
    supplied = profile.get("record_digest")
    material = {key: value for key, value in profile.items() if key != "record_digest"}
    expected = record_digest(material)
    if supplied != expected:
        raise HouseholdContractError("Profile record digest mismatch.")
    return {
        "record_contract": contract,
        "subject_id": subject_id,
        "record_digest": supplied,
        "payload": profile,
    }


def validate_household_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise HouseholdContractError("household-v1 must be an object.")
    allowed_top = {
        "contract_version", "household_id", "composition", "primary_subject_id",
        "subjects", "requested_dimensions",
    }
    extra = set(manifest) - allowed_top
    if extra:
        raise HouseholdContractError(f"Unexpected household fields: {sorted(extra)}.")
    if manifest.get("contract_version") != HOUSEHOLD_VERSION:
        raise HouseholdContractError("contract_version must be household-v1.")
    household_id = manifest.get("household_id")
    if not isinstance(household_id, str) or not _HOUSEHOLD_ID.fullmatch(household_id):
        raise HouseholdContractError("Invalid household_id.")
    composition = manifest.get("composition")
    if composition not in COMPOSITIONS:
        raise HouseholdContractError("composition must be pair or household.")
    primary_subject_id = manifest.get("primary_subject_id")
    if not isinstance(primary_subject_id, str) or not _SUBJECT_ID.fullmatch(primary_subject_id):
        raise HouseholdContractError("Invalid primary_subject_id.")
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or not 2 <= len(subjects) <= 12:
        raise HouseholdContractError("household-v1 requires 2-12 subject entries.")

    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    member_entries: list[dict[str, Any]] = []
    for raw in subjects:
        if not isinstance(raw, dict):
            raise HouseholdContractError("Each household subject must be an object.")
        allowed_subject = {
            "subject_id", "subject_role", "subject_class", "membership",
            "record_contract", "record_digest", "record_state", "authority",
        }
        unknown = set(raw) - allowed_subject
        if unknown:
            raise HouseholdContractError(f"Unexpected household subject fields: {sorted(unknown)}.")
        subject_id = raw.get("subject_id")
        role = raw.get("subject_role")
        subject_class = raw.get("subject_class")
        membership = raw.get("membership", "member")
        record_contract = raw.get("record_contract")
        digest = raw.get("record_digest")
        state = raw.get("record_state", "resolved")
        if not isinstance(subject_id, str) or not _SUBJECT_ID.fullmatch(subject_id):
            raise HouseholdContractError("Invalid subject_id.")
        if subject_id in ids:
            raise HouseholdContractError("Duplicate subject_id.")
        ids.add(subject_id)
        if role not in SUBJECT_ROLES:
            raise HouseholdContractError("Invalid subject_role.")
        if subject_class != ROLE_CLASS[role]:
            raise HouseholdContractError(f"{role} requires subject_class {ROLE_CLASS[role]}.")
        expected_membership = "context_only" if role == "reference" else "member"
        if membership != expected_membership:
            raise HouseholdContractError(f"{role} requires membership {expected_membership}.")
        if record_contract != ROLE_RECORD_CONTRACT[role]:
            raise HouseholdContractError(f"{role} requires record_contract {ROLE_RECORD_CONTRACT[role]}.")
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise HouseholdContractError("Invalid record_digest.")
        if state not in RECORD_STATES:
            raise HouseholdContractError("Invalid record_state.")
        authority = _validate_authority(raw.get("authority"), role=role)
        item = {
            "subject_id": subject_id,
            "subject_role": role,
            "subject_class": subject_class,
            "membership": membership,
            "record_contract": record_contract,
            "record_digest": digest,
            "record_state": state,
            "authority": authority,
        }
        normalized.append(item)
        if membership == "member":
            member_entries.append(item)

    primaries = [item for item in member_entries if item["subject_role"] == "primary"]
    if len(primaries) != 1 or primaries[0]["subject_id"] != primary_subject_id:
        raise HouseholdContractError("Exactly one primary member must match primary_subject_id.")
    if len(member_entries) > 8:
        raise HouseholdContractError("A household supports at most 8 paid/member records.")
    if composition == "pair":
        if len(member_entries) != 2 or {item["subject_role"] for item in member_entries} != {"primary", "partner"}:
            raise HouseholdContractError("pair requires exactly primary + partner members.")
    elif len(member_entries) < 2:
        raise HouseholdContractError("household requires a primary plus at least one added member.")

    requested = manifest.get("requested_dimensions") or [
        "composition_scope", "role_presence", "declared_relationship",
        "input_readiness", "system_availability", "evidence_state",
    ]
    allowed_dimensions = {
        "composition_scope", "role_presence", "declared_relationship",
        "input_readiness", "system_availability", "evidence_state",
        "same_system_observations",
    }
    if not isinstance(requested, list) or not requested or len(requested) > 7:
        raise HouseholdContractError("requested_dimensions must contain 1-7 entries.")
    if len(set(requested)) != len(requested) or any(item not in allowed_dimensions for item in requested):
        raise HouseholdContractError("requested_dimensions contains unsupported values.")

    return {
        "contract_version": HOUSEHOLD_VERSION,
        "household_id": household_id,
        "composition": composition,
        "primary_subject_id": primary_subject_id,
        "subjects": normalized,
        "requested_dimensions": list(requested),
    }


def _record_envelope(record: Any, subject_id: str) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise HouseholdContractError(f"Registry record missing for {subject_id}.")
    if record.get("subject_id") != subject_id:
        raise HouseholdContractError(f"Registry subject binding mismatch for {subject_id}.")
    if record.get("record_contract") not in {
        "analysis-v1", CHILD_PROFILE_VERSION, PET_PROFILE_VERSION, "historical-reference-v1"
    }:
        raise HouseholdContractError(f"Unsupported registry contract for {subject_id}.")
    digest = record.get("record_digest")
    if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
        raise HouseholdContractError(f"Registry digest invalid for {subject_id}.")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        raise HouseholdContractError(f"Registry payload missing for {subject_id}.")
    actual = record_digest(payload) if record["record_contract"] == "analysis-v1" else payload.get("record_digest")
    if actual != digest:
        raise HouseholdContractError(f"Registry digest mismatch for {subject_id}.")
    return record


def _adult_evidence(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    if payload.get("projection_version") != HOUSEHOLD_PROJECTION_VERSION:
        raise HouseholdContractError("Adult household record must use the household subject projection.")
    comparable: dict[tuple[str, str], dict[str, Any]] = {}
    for item in payload.get("markers") or []:
        if not isinstance(item, dict):
            continue
        value = item.get("source_value")
        if isinstance(value, (str, int, float, bool)) or value is None:
            key = (str(item.get("system")), str(item.get("source_path")))
            comparable[key] = item
    return comparable


def _system_inventory(record: dict[str, Any]) -> set[str]:
    contract = record["record_contract"]
    payload = record["payload"]
    if contract == "analysis-v1":
        if payload.get("projection_version") != HOUSEHOLD_PROJECTION_VERSION:
            return set()
        return {str(name) for name in (payload.get("systems") or [])}
    if contract == CHILD_PROFILE_VERSION:
        return set((payload.get("worksheets") or {}).keys())
    if contract == PET_PROFILE_VERSION:
        return set()
    return set()


def compose_relational_view(manifest: dict[str, Any], registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compose deterministic household metadata and same-system adult observations.

    Names, birth inputs, and record bodies are intentionally omitted from the returned view.
    """

    validated = validate_household_manifest(manifest)
    resolved: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for subject in validated["subjects"]:
        subject_id = subject["subject_id"]
        if subject["record_state"] != "resolved":
            failures.append(f"{subject_id}:{subject['record_state']}")
            continue
        try:
            record = _record_envelope(registry.get(subject_id), subject_id)
        except HouseholdContractError:
            failures.append(f"{subject_id}:unresolved")
            continue
        if record["record_contract"] != subject["record_contract"] or record["record_digest"] != subject["record_digest"]:
            failures.append(f"{subject_id}:stale")
            continue
        resolved[subject_id] = record
    if failures:
        return {
            "schema_version": RELATIONAL_VIEW_VERSION,
            "household_id": validated["household_id"],
            "composition": validated["composition"],
            "status": "unavailable",
            "degraded": True,
            "degradation_reasons": sorted(failures),
            "subjects": [],
            "observations": [],
            "forbidden_inferences": list(FORBIDDEN_RELATIONAL_INFERENCES),
            "policy_note": "Stale or unresolved subject records suppress the composed view.",
        }

    subject_summaries = []
    for subject in validated["subjects"]:
        record = resolved[subject["subject_id"]]
        systems = sorted(_system_inventory(record))
        subject_summaries.append({
            "subject_id": subject["subject_id"],
            "subject_role": subject["subject_role"],
            "subject_class": subject["subject_class"],
            "membership": subject["membership"],
            "record_contract": subject["record_contract"],
            "record_digest": subject["record_digest"],
            "input_readiness": "ready",
            "system_availability": "complete" if systems else (
                "unavailable" if subject["subject_class"] in {"nonhuman_animal", "historical_reference"} else "partial"
            ),
            "systems": systems,
            "declared_relationship": ROLE_RELATIONSHIP[subject["subject_role"]],
            "label": {
                "person_adult": ADULT_LABEL,
                "person_minor": CHILD_LABEL,
                "nonhuman_animal": PET_LABEL,
                "historical_reference": REFERENCE_LABEL,
            }[subject["subject_class"]],
        })

    observations: list[dict[str, Any]] = []
    adults = [
        subject for subject in validated["subjects"]
        if subject["membership"] == "member" and subject["subject_class"] == "person_adult"
    ]
    for left, right in combinations(adults, 2):
        left_record = resolved[left["subject_id"]]
        right_record = resolved[right["subject_id"]]
        if left_record["record_contract"] != "analysis-v1" or right_record["record_contract"] != "analysis-v1":
            continue
        left_evidence = _adult_evidence(left_record["payload"])
        right_evidence = _adult_evidence(right_record["payload"])
        for key in sorted(set(left_evidence) & set(right_evidence)):
            a, b = left_evidence[key], right_evidence[key]
            same = a.get("source_value") == b.get("source_value")
            observations.append({
                "observation_id": "rel_" + content_digest({
                    "subjects": sorted([left["subject_id"], right["subject_id"]]),
                    "system": key[0], "source_path": key[1],
                    "left": a.get("source_value"), "right": b.get("source_value"),
                }),
                "kind": "same_marker" if same else "different_marker",
                "dimension": "same_system_observation",
                "subjects": [left["subject_id"], right["subject_id"]],
                "system": key[0],
                "source_path": key[1],
                "values": [a.get("source_value"), b.get("source_value")],
                "evidence_ids": [a.get("evidence_id"), b.get("evidence_id")],
                "provenance_refs": [a.get("provenance_ref"), b.get("provenance_ref")],
                "policy_note": (
                    "Same returned marker under the same system and field; not a compatibility measure."
                    if same else
                    "Different returned markers under the same system and field; not conflict or incompatibility."
                ),
                "forbidden_inferences": ["compatibility", "relationship_quality", "outcome_prediction"],
            })
            if len(observations) >= 64:
                break
        if len(observations) >= 64:
            break

    payload = {
        "schema_version": RELATIONAL_VIEW_VERSION,
        "household_id": validated["household_id"],
        "composition": validated["composition"],
        "status": "computed",
        "degraded": False,
        "degradation_reasons": [],
        "dimensions": {
            "composition_scope": validated["composition"],
            "role_presence": sorted({item["subject_role"] for item in validated["subjects"] if item["membership"] == "member"}),
            "input_readiness": "ready",
            "evidence_state": "complete",
        },
        "subjects": subject_summaries,
        "observations": observations,
        "forbidden_inferences": list(FORBIDDEN_RELATIONAL_INFERENCES),
        "policy_note": (
            "This view composes provenance-bound records. It does not score compatibility, "
            "relationship quality, parenting, child potential, or pet temperament."
        ),
    }
    payload["view_digest"] = "sha256:" + content_digest(payload)
    return payload
