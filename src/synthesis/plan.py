"""Build the deterministic synthesis-plan-v1 claim graph."""

from __future__ import annotations

import hashlib

from .contracts import PLAN_SCHEMA_VERSION, PROHIBITED_TOPICS, SYNTHESIS_LIMITATION
from .readings import CHAPTERS, reading_entries

GIFT_LANGUAGE = {
    "analysis": ("pattern discrimination", "overfitting meaning to every detail"),
    "communication": ("translation and expression", "speaking before the pattern is sufficiently tested"),
    "structure": ("building durable form", "letting form become rigidity"),
    "freedom": ("adaptive movement", "leaving before a useful constraint has done its work"),
    "autonomy": ("self-directed initiation", "excluding support in order to preserve independence"),
    "belonging": ("reciprocal connection", "overadjusting to preserve connection"),
    "discernment": ("careful selection", "withholding until every uncertainty disappears"),
    "service": ("useful contribution", "measuring worth only through usefulness"),
    "integration": ("holding several frames together", "forcing incompatible frames into false agreement"),
    "transformation": ("working through meaningful change", "treating every disruption as a demand for reinvention"),
    "persistence": ("sustained attention", "continuing after the evidence has changed"),
    "creativity": ("forming new combinations", "valuing novelty over fit"),
    "visibility": ("making work legible", "performing certainty"),
    "privacy": ("protecting depth and boundaries", "making the inner pattern impossible to verify"),
    "intuition": ("noticing implicit patterns", "treating an impression as proof"),
    "embodiment": ("testing ideas through lived response", "confusing immediate response with settled evidence"),
    "adaptability": ("changing form without losing the thread", "changing direction before a pattern can mature"),
    "leadership": ("coordinating direction", "mistaking direction for certainty"),
    "initiation": ("starting movement", "starting faster than context can support"),
    "receptivity": ("responding to what is actually present", "waiting so long that choice disappears"),
}


def _claim_id(section: str, motif: str, evidence_ids: list[str]) -> str:
    digest = hashlib.sha256((section + motif + "|".join(evidence_ids)).encode()).hexdigest()[:10]
    return f"claim_{section}_{digest}"


def _claim(section: str, claim_type: str, motif: str, evidence_ids: list[str], strength: str,
           *, contradicting: list[str] | None = None, metadata: dict | None = None) -> dict:
    return {
        "claim_id": _claim_id(section, motif, evidence_ids), "claim_type": claim_type,
        "motif": motif, "evidence_ids": sorted(set(evidence_ids)), "strength": strength,
        "allowed_language": ["may", "favors", "symbolizes", "emphasizes", "suggests as reflection"],
        "forbidden_language": ["destined", "always", "cannot", "proves", "diagnoses"],
        "contradicting_evidence_ids": sorted(set(contradicting or [])),
        "limitation": SYNTHESIS_LIMITATION, "metadata": metadata or {},
    }


def _archetype_title(primary: str, secondary: str | None) -> str:
    first = primary.title()
    return f"The {first}–{secondary.title()} Pattern" if secondary else f"The {first} Pattern"


def build_plan(evidence_packet: dict, motifs: list[dict], agreements: list[dict], contradictions: list[dict]) -> dict:
    supported = [item for item in motifs if item["independent_group_count"] >= 2]
    primary = supported[0] if supported else (motifs[0] if motifs else None)
    secondary = supported[1] if len(supported) > 1 else None
    central_supported = primary is not None and primary["independent_group_count"] >= 2
    central_motifs = [item for item in (primary, secondary) if item]
    central_evidence = sorted({
        evidence_id
        for item in central_motifs
        for evidence_id in item["evidence_ids"]
    })
    central_systems = sorted({
        system
        for item in central_motifs
        for system in item["systems"]
    })
    central_title = _archetype_title(primary["label"], secondary["label"] if secondary else None) if central_supported else "No single archetype dominates this profile"
    central = {
        "title": central_title,
        "definition": (
            f"The strongest normalized recurrences combine {' and '.join(item['label'] for item in central_motifs)}." if central_supported
            else "The available evidence does not support a cross-system central archetype."
        ),
        "motif_ids": [item["motif_id"] for item in central_motifs],
        "evidence_ids": central_evidence, "systems": central_systems,
        "confidence": primary["confidence"] if central_supported else "low",
        "partial_profile": evidence_packet["data_quality"]["astronomy"] != "available",
    }
    tension = contradictions[0] if contradictions else None
    claims_by_section: dict[str, list[dict]] = {
        "central_pattern": [], "originating_tension": [], "gifts": [], "shadow_expressions": [],
        "path_of_integration": [], "recurring_symbols": [], "mythic_telling": [], "evidence_ledger": [],
    }
    if primary:
        central_motif = "|".join(item["label"] for item in central_motifs)
        claims_by_section["central_pattern"].append(_claim(
            "central", "descriptive", central_motif, central_evidence,
            primary["confidence"] if central_supported else "tentative",
            metadata={"central_supported": central_supported, "title": central_title, "systems": central_systems, "partial_profile": central["partial_profile"]},
        ))
        gift, shadow = GIFT_LANGUAGE.get(primary["label"], (f"a reflective emphasis on {primary['label']}", f"overidentifying with {primary['label']}"))
        claims_by_section["gifts"].append(_claim(
            "gift", "gift", primary["label"], primary["evidence_ids"], primary["confidence"],
            metadata={"gift": gift},
        ))
        claims_by_section["shadow_expressions"].append(_claim(
            "shadow", "shadow", primary["label"], primary["evidence_ids"], primary["confidence"],
            metadata={"gift": gift, "shadow": shadow},
        ))
    if tension:
        claims_by_section["originating_tension"].append(_claim(
            "tension", "tension", f"{tension['pole_a']}|{tension['pole_b']}", tension["evidence_ids"],
            tension["uncertainty"], metadata=tension,
        ))
        claims_by_section["path_of_integration"].append(_claim(
            "integration", "integrative", f"{tension['pole_a']}|{tension['pole_b']}", tension["evidence_ids"],
            tension["uncertainty"], metadata={"movement": tension["integrated_expression"]},
        ))
    elif primary:
        claims_by_section["path_of_integration"].append(_claim(
            "integration", "integrative", primary["label"], primary["evidence_ids"], primary["confidence"],
            metadata={"movement": f"testing where {primary['label']} is useful and where another response fits better"},
        ))
    symbol_items = [
        item for item in evidence_packet["evidence_items"]
        if item["symbol_family"] in {"zodiac_sign", "reduced_number", "human_design_gate", "human_design_channel", "sephirah", "wu_xing_element"}
    ][:12]
    for item in symbol_items:
        claims_by_section["recurring_symbols"].append(_claim(
            "symbol", "descriptive", item["normalized_symbol"], [item["evidence_id"]], "strong",
            metadata={"system": item["system"], "value": item["source_value"], "atlas_targets": item["atlas_targets"]},
        ))
    if primary:
        claims_by_section["mythic_telling"].append(_claim(
            "mythic", "integrative", primary["label"], primary["evidence_ids"], primary["confidence"],
            contradicting=tension["evidence_ids"] if tension else [],
            metadata={"title": central_title, "tension": tension},
        ))
    # Several supported themes and polarities survive into the reading, not
    # just the top-ranked label. Preserve the original first claims and IDs.
    for motif in motifs[1:4]:
        gift, shadow = GIFT_LANGUAGE.get(motif["label"],
            (f"exploring {motif['label']} in a concrete situation", f"overidentifying with {motif['label']}"))
        claims_by_section["gifts"].append(_claim("gift", "gift", motif["label"], motif["evidence_ids"], motif["confidence"], metadata={"gift": gift}))
        claims_by_section["shadow_expressions"].append(_claim("shadow", "shadow", motif["label"], motif["evidence_ids"], motif["confidence"], metadata={"gift": gift, "shadow": shadow}))
    for other in contradictions[1:3]:
        claims_by_section["originating_tension"].append(_claim(
            "tension", "tension", f"{other['pole_a']}|{other['pole_b']}", other["evidence_ids"], other["uncertainty"], metadata=other))
    for agreement in agreements[:3]:
        claims_by_section.setdefault("shared_threads", []).append(_claim(
            "agreement", "agreement", agreement["motif"], agreement["evidence_ids"], agreement["strength"], metadata=agreement))
    for entry in reading_entries(evidence_packet):
        claims_by_section.setdefault(entry["section"], []).append(_claim(
            entry["section"], "reading", entry["title"], entry["evidence_ids"], "tentative", metadata=entry))
    claims_by_section["evidence_ledger"] = [claim for section, claims in claims_by_section.items() if section != "evidence_ledger" for claim in claims]
    headings = {
        "central_pattern": "The Central Pattern", "originating_tension": "The Originating Tension",
        "gifts": "Gifts", "shadow_expressions": "Possible Shadow Expressions",
        "path_of_integration": "The Path of Integration", "recurring_symbols": "Recurring Symbols",
        "mythic_telling": "The Mythic Telling", "evidence_ledger": "Evidence Ledger",
    }
    headings.update(CHAPTERS)
    headings["shared_threads"] = "Where the systems meet"
    sections = [
        {"section_id": key, "purpose": headings[key], "claims": claims}
        for key, claims in claims_by_section.items() if claims
    ]
    quality = evidence_packet["data_quality"]
    missing = [f"{key}: {value}" for key, value in quality.items() if value in {"missing", "unknown", "partial", "unavailable", "absent"}]
    return {
        "schema_version": PLAN_SCHEMA_VERSION, "analysis_id": evidence_packet["analysis_id"],
        "central_archetype": central, "originating_tension": tension,
        "dominant_motifs": motifs[:8], "agreements": agreements,
        "productive_contradictions": contradictions, "gifts": claims_by_section["gifts"],
        "shadow_expressions": claims_by_section["shadow_expressions"],
        "developmental_movements": claims_by_section["path_of_integration"],
        "repeated_symbols": symbol_items, "missing_or_uncertain_dimensions": missing,
        "prohibited_claims": PROHIBITED_TOPICS, "narrative_sections": sections,
    }
