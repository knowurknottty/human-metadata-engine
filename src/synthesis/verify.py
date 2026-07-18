"""Deterministic post-realization claim and safety verifier."""

from __future__ import annotations

from .contracts import PROHIBITED_LANGUAGE, PROHIBITED_TOPICS


def verify_narrative(evidence_packet: dict, plan: dict, narrative: dict) -> dict:
    evidence_ids = {item["evidence_id"] for item in evidence_packet["evidence_items"]}
    claims = {
        claim["claim_id"]: claim
        for section in plan["narrative_sections"] for claim in section["claims"]
    }
    errors = []
    seen_claims = set()
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
                for claim_id in claim_ids:
                    if claim_id not in claims:
                        errors.append({"sentence_id": sid, "category": "unknown_claim", "detail": claim_id, "action": "reject"})
                    else:
                        seen_claims.add(claim_id)
                        if not set(referenced).issubset(set(claims[claim_id]["evidence_ids"])):
                            errors.append({"sentence_id": sid, "category": "unsupported_evidence", "detail": claim_id, "action": "reject"})
                unknown_evidence = set(referenced) - evidence_ids
                if unknown_evidence:
                    errors.append({"sentence_id": sid, "category": "unknown_evidence", "detail": ",".join(sorted(unknown_evidence)), "action": "reject"})
                lowered = sentence.get("text", "").casefold()
                for phrase in dict.fromkeys([*PROHIBITED_LANGUAGE, *PROHIBITED_TOPICS]):
                    if phrase in lowered:
                        errors.append({"sentence_id": sid, "category": "prohibited_language", "detail": phrase, "action": "rewrite"})
    planned_claims = {
        claim["claim_id"] for section in plan["narrative_sections"]
        if section["section_id"] != "evidence_ledger" for claim in section["claims"]
    }
    for missing in sorted(planned_claims - seen_claims):
        errors.append({"sentence_id": None, "category": "missing_claim", "detail": missing, "action": "reject"})
    return {"valid": not errors, "errors": errors, "checked_sentence_count": checked_sentence_count}
