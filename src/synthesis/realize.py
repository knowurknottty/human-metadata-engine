"""Bounded deterministic realization of synthesis-plan-v1."""

from __future__ import annotations

import hashlib

from .contracts import NARRATIVE_SCHEMA_VERSION, TEMPLATE_VERSION

MODES = {"plain", "mythic", "research"}


def _sentence(claim: dict, text: str) -> dict:
    return {
        "sentence_id": f"sentence_{claim['claim_id'].removeprefix('claim_')}", "text": text,
        "claim_ids": [claim["claim_id"]], "evidence_ids": claim["evidence_ids"],
        "strength": claim["strength"], "epistemic_label": "interpretive_synthesis",
        "contradiction": bool(claim["contradicting_evidence_ids"] or claim["claim_type"] == "tension"),
    }


def _text(claim: dict, mode: str) -> str:
    motif = claim["motif"].replace("|", " and ")
    meta = claim["metadata"]
    kind = claim["claim_type"]
    if kind == "descriptive" and "central_supported" in meta:
        if not meta["central_supported"]:
            return "No single archetype dominates this partial profile; the strongest available motif remains tentative."
        partial = " The profile is partial because exact birth-derived coverage is unavailable." if meta.get("partial_profile") else ""
        if mode == "mythic":
            return f"In this symbolic telling, {meta['title']} gathers the recurring thread of {motif} without claiming it as destiny.{partial}"
        if mode == "research":
            return f"The plan ranks a combined {motif} pattern through independent-group support; this is interpretive synthesis.{partial}"
        return f"Across the available symbolic systems, the strongest recurring pattern combines {motif}; it is a reflection prompt, not a measured trait.{partial}"
    if kind == "gift":
        gift = meta["gift"]
        return (
            f"The profile's {motif} thread may be imagined as a lantern for {gift}, never a promise of ability."
            if mode == "mythic" else
            f"Evidence-linked motif: {motif}. Its bounded gift reading is {gift}."
            if mode == "research" else
            f"This pattern may favor {gift}; whether it appears in life requires direct observation."
        )
    if kind == "shadow":
        shadow = meta["shadow"]
        return (
            f"Every lantern casts an edge: the same {motif} emphasis may become {shadow}."
            if mode == "mythic" else
            f"The gift and shadow share the same evidence: a possible distortion is {shadow}."
            if mode == "research" else
            f"A possible shadow of the same pattern is {shadow}; this is not a clinical conclusion."
        )
    if kind == "tension":
        a, b = meta["pole_a"], meta["pole_b"]
        return (
            f"The story holds two currents—{a} and {b}—without pretending the river has already chosen between them."
            if mode == "mythic" else
            f"The plan preserves an unresolved {a}–{b} polarity, with evidence retained for both poles."
            if mode == "research" else
            f"The strongest tension is between {a} and {b}; both may be relevant in different contexts, and the contradiction remains unresolved."
        )
    if kind == "integrative" and "title" in meta:
        tension = meta.get("tension")
        if mode == "mythic":
            return f"{meta['title']} moves through {motif}, carrying contradiction as a question rather than converting it into prophecy."
        if tension:
            return f"The synthesis joins the central motif with the preserved {tension['pole_a']}–{tension['pole_b']} tension without claiming resolution."
        return f"The synthesis keeps {motif} as a bounded symbolic hypothesis rather than a fact."
    if kind == "integrative":
        movement = meta["movement"]
        return (
            f"Integration is pictured not as conquest, but as {movement}."
            if mode == "mythic" else
            f"The bounded developmental hypothesis is {movement}."
            if mode == "research" else
            f"A useful reflection question is whether integration could involve {movement}."
        )
    if kind == "descriptive" and "value" in meta:
        value = meta["value"]
        return f"{meta['system'].replace('_', ' ').title()} contributes the returned symbol {value}; select it to inspect its exact source and limits."
    return f"The plan records {motif} as a bounded interpretive claim."


def realize(plan: dict, mode: str) -> dict:
    if mode not in MODES:
        raise ValueError("Narrative mode must be plain, mythic, or research.")
    sections = []
    for planned in plan["narrative_sections"]:
        if planned["section_id"] == "evidence_ledger":
            continue
        sentences = [_sentence(claim, _text(claim, mode)) for claim in planned["claims"]]
        if not sentences:
            continue
        sections.append({
            "section_id": planned["section_id"], "heading": planned["purpose"],
            "paragraphs": [{"paragraph_id": f"paragraph_{planned['section_id']}",
                            "text": " ".join(item["text"] for item in sentences), "sentences": sentences}],
        })
    canonical = plan["analysis_id"] + ":" + mode + ":" + TEMPLATE_VERSION
    return {
        "schema_version": NARRATIVE_SCHEMA_VERSION, "mode": mode,
        "tone": "poetic" if mode == "mythic" else "grounded" if mode == "plain" else "evidence-first",
        "sections": sections, "summary": plan["central_archetype"]["definition"],
        "disclaimer": "A deterministic symbolic reflection, not scientific personality measurement, diagnosis, prediction, or destiny.",
        "generation_metadata": {
            "engine": "deterministic-template", "model": None, "prompt_version": None,
            "temperature": 0, "generated_at": None, "template_version": TEMPLATE_VERSION,
            "deterministic_input_hash": hashlib.sha256(canonical.encode()).hexdigest(),
            "remote_provider_used": False,
        },
    }
