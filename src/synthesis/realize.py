"""Bounded deterministic realization of synthesis-plan-v1."""

from __future__ import annotations

import hashlib

from .contracts import NARRATIVE_SCHEMA_VERSION, TEMPLATE_VERSION
from .reading_library import LIBRARY_VERSION

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
    if kind == "reading":
        return meta["texts"][mode]
    if kind == "agreement":
        systems = ", ".join(meta["participating_systems"])
        if mode == "mythic":
            return f"The thread of {motif} appears in several margins of the atlas: {systems}. Let the images speak beside one another without pretending they share a single origin. Where does this theme help you describe an experience, and where does another reading fit better?"
        if mode == "research":
            return f"{motif.title()} is supported by the normalization groups {', '.join(meta['independence_groups'])}. {meta['ambiguity']} {meta['alternative_reading']} Inspect the linked records before treating recurrence as informative."
        return f"The theme of {motif} appears across {systems}. These records meet through the project's shared vocabulary; agreement may reflect that vocabulary rather than an enduring quality in you. Try a concrete example and a counterexample. Repeated name calculations do not become independent evidence merely because they use different alphabets."
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
            f"The {motif} theme invites {gift}. Recall a time when that approach made a situation clearer or more workable. What conditions helped: enough time, a receptive collaborator, a clear boundary, or a specific task? Those conditions tell you more than a label alone."
        )
    if kind == "shadow":
        shadow = meta["shadow"]
        return (
            f"Every lantern casts an edge: the same {motif} emphasis may become {shadow}."
            if mode == "mythic" else
            f"The gift and shadow share the same evidence: a possible distortion is {shadow}."
            if mode == "research" else
            f"The counterweight to {motif} is noticing {shadow}. Consider the point at which a useful approach stops serving the situation. What small sign would tell you to pause, ask for feedback, or try another response? This is an invitation to observe a pattern, not an assertion that it describes you."
        )
    if kind == "tension":
        a, b = meta["pole_a"], meta["pole_b"]
        return (
            f"The story holds two currents—{a} and {b}—without pretending the river has already chosen between them."
            if mode == "mythic" else
            f"The plan preserves an unresolved {a}–{b} polarity, with evidence retained for both poles."
            if mode == "research" else
            f"A supported tension is between {a} and {b}; both may be relevant in different contexts, and the contradiction remains unresolved. Describe a situation that asks for {a}, then one that needs {b}. Instead of choosing a permanent winner, identify the cue that would help you change your approach. The records for both poles remain available."
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
            "paragraphs": [{"paragraph_id": f"paragraph_{planned['section_id']}_{index}",
                            "text": item["text"], "sentences": [item]} for index, item in enumerate(sentences)],
        })
    canonical = plan["analysis_id"] + ":" + mode + ":" + TEMPLATE_VERSION + ":" + LIBRARY_VERSION
    return {
        "schema_version": NARRATIVE_SCHEMA_VERSION, "mode": mode,
        "tone": "poetic" if mode == "mythic" else "grounded" if mode == "plain" else "evidence-first",
        "sections": sections, "summary": plan["central_archetype"]["definition"],
        "disclaimer": "A deterministic symbolic reflection, not scientific personality measurement, diagnosis, prediction, or destiny.",
        "generation_metadata": {
            "engine": "deterministic-template", "model": None, "prompt_version": None,
            "temperature": 0, "generated_at": None, "template_version": TEMPLATE_VERSION,
            "deterministic_input_hash": hashlib.sha256(canonical.encode()).hexdigest(),
            "remote_provider_used": False, "reading_library_version": LIBRARY_VERSION,
        },
    }
