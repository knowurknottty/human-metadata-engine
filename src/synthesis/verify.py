"""Deterministic post-realization claim, evidence, version, and safety verifier."""

from __future__ import annotations

from collections import Counter

from .analysis import detect_agreements, detect_contradictions, rank_motifs
from .extractors import validate_evidence_packet_integrity
from .plan import build_plan
from .realize import realize
from .contracts import (
    EVIDENCE_SCHEMA_VERSION,
    NARRATIVE_SCHEMA_VERSION,
    PLAN_SCHEMA_VERSION,
    PROHIBITED_LANGUAGE,
    PROHIBITED_TOPICS,
)


def verify_narrative(evidence_packet: dict, plan: dict, narrative: dict) -> dict:
    errors: list[dict] = []
    if evidence_packet.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        errors.append({"sentence_id": None, "category": "unsupported_evidence_schema", "detail": str(evidence_packet.get("schema_version")), "action": "reject"})
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append({"sentence_id": None, "category": "unsupported_plan_schema", "detail": str(plan.get("schema_version")), "action": "reject"})
    if narrative.get("schema_version") != NARRATIVE_SCHEMA_VERSION:
        errors.append({"sentence_id": None, "category": "unsupported_narrative_schema", "detail": str(narrative.get("schema_version")), "action": "reject"})

    expected_plan = None
    expected_narrative = None
    try:
        validate_evidence_packet_integrity(evidence_packet)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append({"sentence_id": None, "category": "evidence_integrity_mismatch", "detail": str(exc), "action": "reject"})
    else:
        try:
            motifs = rank_motifs(evidence_packet)
            agreements = detect_agreements(motifs)
            contradictions = detect_contradictions(motifs)
            expected_plan = build_plan(evidence_packet, motifs, agreements, contradictions)
            if plan != expected_plan:
                errors.append({"sentence_id": None, "category": "plan_derivation_mismatch", "detail": "Plan does not exactly match deterministic derivation from the active evidence packet.", "action": "reject"})
            expected_narrative = realize(expected_plan, narrative.get("mode"))
            if narrative != expected_narrative:
                errors.append({"sentence_id": None, "category": "narrative_derivation_mismatch", "detail": "Narrative does not exactly match deterministic realization of the derived plan.", "action": "reject"})
        except (KeyError, TypeError, ValueError) as exc:
            errors.append({"sentence_id": None, "category": "derivation_failure", "detail": str(exc), "action": "reject"})

    evidence_list = evidence_packet.get("evidence_items") or []
    evidence_id_list = [item.get("evidence_id") for item in evidence_list]
    duplicate_evidence = sorted(item for item, count in Counter(evidence_id_list).items() if item and count > 1)
    if duplicate_evidence:
        errors.append({"sentence_id": None, "category": "duplicate_evidence_id", "detail": ",".join(duplicate_evidence), "action": "reject"})

    mixed_versions = sorted({
        str(item.get("packet_schema_version"))
        for item in evidence_list
        if item.get("packet_schema_version") != EVIDENCE_SCHEMA_VERSION
    })
    if mixed_versions:
        errors.append({"sentence_id": None, "category": "mixed_record_versions", "detail": ",".join(mixed_versions), "action": "reject"})

    evidence_ids = {item for item in evidence_id_list if item}
    claims = {
        claim["claim_id"]: claim
        for section in plan.get("narrative_sections", []) for claim in section.get("claims", [])
    }
    for claim_id, claim in claims.items():
        missing = set(claim.get("evidence_ids") or []) - evidence_ids
        if missing:
            errors.append({"sentence_id": None, "category": "claim_unknown_evidence", "detail": f"{claim_id}:{','.join(sorted(missing))}", "action": "reject"})

    seen_claim_counts: Counter[str] = Counter()
    checked_sentence_count = 0
    for section in narrative.get("sections", []):
        for paragraph in section.get("paragraphs", []):
            for sentence in paragraph.get("sentences", []):
                checked_sentence_count += 1
                sid = sentence.get("sentence_id", "unknown")
                claim_ids = sentence.get("claim_ids") or []
                referenced = sentence.get("evidence_ids") or []
                if sentence.get("epistemic_label") == "interpretive_synthesis" and not claim_ids:
                    errors.append({"sentence_id": sid, "category": "unsupported_claim", "detail": "Interpretive sentence has no claim ID.", "action": "reject"})
                if len(claim_ids) != 1:
                    errors.append({"sentence_id": sid, "category": "claim_cardinality", "detail": f"expected exactly one claim ID, got {len(claim_ids)}", "action": "reject"})
                for claim_id in claim_ids:
                    claim = claims.get(claim_id)
                    if claim is None:
                        errors.append({"sentence_id": sid, "category": "unknown_claim", "detail": claim_id, "action": "reject"})
                        continue
                    seen_claim_counts[claim_id] += 1
                    if set(referenced) != set(claim.get("evidence_ids") or []):
                        errors.append({"sentence_id": sid, "category": "evidence_mismatch", "detail": claim_id, "action": "reject"})
                    if claim.get("claim_type") == "reading":
                        expected = claim.get("metadata", {}).get("texts", {}).get(narrative.get("mode"))
                        actual = sentence.get("text") or ""
                        text_matches = actual == expected or (
                            narrative.get("mode") == "mythic" and isinstance(expected, str) and actual.startswith(expected + " ")
                        )
                        if not text_matches:
                            errors.append({"sentence_id": sid, "category": "reading_mismatch", "detail": "Reading must preserve its planned authored text before deterministic Story enrichment.", "action": "reject"})
                if not referenced:
                    errors.append({"sentence_id": sid, "category": "missing_evidence", "detail": "Every passage needs evidence.", "action": "reject"})
                unknown_evidence = set(referenced) - evidence_ids
                if unknown_evidence:
                    errors.append({"sentence_id": sid, "category": "unknown_evidence", "detail": ",".join(sorted(unknown_evidence)), "action": "reject"})
                lowered = sentence.get("text", "").casefold()
                for phrase in dict.fromkeys([*PROHIBITED_LANGUAGE, *PROHIBITED_TOPICS]):
                    if phrase in lowered:
                        errors.append({"sentence_id": sid, "category": "prohibited_language", "detail": phrase, "action": "rewrite"})

    planned_claims = {
        claim["claim_id"] for section in plan.get("narrative_sections", [])
        if section.get("section_id") != "evidence_ledger" for claim in section.get("claims", [])
    }
    for claim_id in sorted(planned_claims):
        count = seen_claim_counts[claim_id]
        if count == 0:
            errors.append({"sentence_id": None, "category": "missing_claim", "detail": claim_id, "action": "reject"})
        elif count > 1:
            errors.append({"sentence_id": None, "category": "duplicate_claim_realization", "detail": f"{claim_id}:{count}", "action": "reject"})

    return {"valid": not errors, "errors": errors, "checked_sentence_count": checked_sentence_count}
