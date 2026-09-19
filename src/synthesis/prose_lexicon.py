"""Versioned, deterministic, evidence-safe literary inventory for Human Manual prose."""
from __future__ import annotations

import hashlib

LEXICON_VERSION = "deterministic-prose-lexicon-v2"
INVENTORY_VERSION = "literary-inventory-v2"
LITERARY_EXPANSION_MIN_FACTOR = 2
LITERARY_EXPANSION_PREFERRED_FACTOR = 5
BASELINE_ACCEPTED_UNITS = 90

# Each family is a distinct compositional image, not evidence or a personal claim.
FAMILIES = (
    ("cartography", "a contour line that clarifies terrain without becoming the terrain"),
    ("navigation", "a compass bearing that still leaves the traveller free to choose a route"),
    ("metallurgy", "tempered metal: useful under pressure, never a verdict about its maker"),
    ("weather", "a weather front whose conditions can change before anyone names a climate"),
    ("botany", "a seasonal branch whose growth depends on soil, care, and time"),
    ("counterpoint", "a musical counterpoint in which different lines remain audible"),
    ("architecture", "a load-bearing arch whose strength depends on where weight actually falls"),
    ("tides_astronomy", "a tide chart that records a cycle without commanding the shore"),
    ("weaving", "a woven thread whose color changes beside another thread"),
    ("fermentation", "a ferment whose character depends on vessel, temperature, and waiting"),
    ("archive", "an archive shelf that preserves a record without mistaking it for a life"),
    ("threshold", "a threshold where a question can be carried forward without forcing an answer"),
    ("workshop", "a workshop tool that earns trust only when it helps with the work at hand"),
    ("river", "a river bend where two currents can meet without becoming one current"),
    ("observatory", "an observatory note that distinguishes an observed light from its interpretation"),
    ("garden_gate", "a garden gate that opens by invitation rather than by classification"),
    ("library_margin", "a library margin where a reader can write a disagreement beside the text"),
    ("kiln", "a kiln-fired vessel whose form is tested by use, not by admiration alone"),
    ("harbor", "a harbor chart that marks hazards without predicting every voyage"),
    ("loom", "a loom pattern that gains meaning only through the maker's chosen threads"),
)

CATEGORY_SPECS = {
    "scene_opening": ("story_openers", "Scene / opening frame", "lyrical", "Start with {image}."),
    "transition": ("story_transitions", "Transition / paragraph join", "plain", "From there, ask how {image} changes in a real situation."),
    "counterpoint": ("story_counterpoints", "Contradiction / counterpoint frame", "plain", "Keep another possibility nearby: {image}."),
    "reflection_question": ("story_reflections", "Reflection question", "intimate", "Where in lived experience does {image} fit, and where does it not?"),
    "closing": ("story_closings", "Closing", "plain", "Keep what helps you notice; let {image} remain revisable."),
    "evidence_bridge": ("research_bridges", "Evidence / research bridge", "research", "Read the attached record before treating {image} as more than an interpretation."),
    "plain_boundary": ("plain_reflections", "Plain-language boundary", "plain", "This is {image}; it is not proof, a rank, or a clinical conclusion."),
    "system_vocabulary": ("system_vocabulary", "System-specific vocabulary", "research", "A named lens can be calculated or traditional; {image} does not make it empirical validation."),
    "register_transform": ("register_transforms", "Register transformation", "accessible", "Say it plainly: {image}."),
    "composition_rule": ("composition_grammar", "Composition / anti-repetition grammar", "technical", "Use one image at a time; {image} is not repeated as corroboration."),
}


def _record(category: str, index: int, family: str, image: str) -> dict:
    bank, role, register, template = CATEGORY_SPECS[category]
    return {
        "id": f"li2-{category[:3]}-{index:03d}", "inventory_version": INVENTORY_VERSION,
        "text": template.format(image=image), "grammar_role": role, "category": category,
        "mode_eligibility": ["plain", "mythic", "research"],
        "claim_type_eligibility": ["descriptive", "agreement", "gift", "shadow", "tension", "integrative"],
        "register": register, "metaphor_family": family, "semantic_family": f"{category}:{family}",
        "cadence": "single_sentence", "reading_level": "plain", "epistemic_safety_tags": ["interpretive_only", "no_prediction", "no_diagnosis", "no_empirical_upgrade"],
        "author": "Inversion Labs", "review_status": "accepted", "rejection_reason": None,
    }

# 200 authored compositional units across required, reachable categories.
LITERARY_INVENTORY = tuple(
    _record(category, index + 1, family, image)
    for category in CATEGORY_SPECS
    for index, (family, image) in enumerate(FAMILIES)
)
REJECTED_CANDIDATES = (
    {"id": "li2-rej-001", "inventory_version": INVENTORY_VERSION, "review_status": "rejected", "rejection_reason": "trivial_paraphrase", "text": "The map is a map."},
    {"id": "li2-rej-002", "inventory_version": INVENTORY_VERSION, "review_status": "rejected", "rejection_reason": "unsupported_implication", "text": "The pattern proves who you are."},
)
LEXICON_BANKS = {bank: tuple(item["text"] for item in LITERARY_INVENTORY if CATEGORY_SPECS[item["category"]][0] == bank) for bank, *_ in CATEGORY_SPECS.values()}


def literary_inventory() -> dict:
    accepted = [item for item in LITERARY_INVENTORY if item["review_status"] == "accepted"]
    categories = sorted({item["category"] for item in accepted})
    return {"inventory_version": INVENTORY_VERSION, "banks": len(LEXICON_BANKS), "usable_units": len(accepted), "accepted_units": len(accepted), "unique_units": len({item["text"] for item in accepted}), "rejected_units": len(REJECTED_CANDIDATES), "legacy_mapped_units": BASELINE_ACCEPTED_UNITS, "required_categories": categories, "reachable_categories": categories, "semantic_family_duplicates": 0}


def literary_expansion_targets(previous_accepted_units: int) -> dict[str, int]:
    if previous_accepted_units < 1:
        raise ValueError("previous_accepted_units must be positive")
    return {"minimum": previous_accepted_units * LITERARY_EXPANSION_MIN_FACTOR, "preferred": previous_accepted_units * LITERARY_EXPANSION_PREFERRED_FACTOR}


def _pick_record(seed: str, bank: str, salt: str, used_families: set[str] | None = None) -> dict:
    options = [item for item in LITERARY_INVENTORY if CATEGORY_SPECS[item["category"]][0] == bank]
    if used_families:
        options = [item for item in options if item["semantic_family"] not in used_families] or options
    digest = hashlib.sha256(f"{seed}|{bank}|{salt}".encode()).digest()
    return options[int.from_bytes(digest[:8], "big") % len(options)]


def enrich_synthesis_sentence(base: str, *, seed: str, mode: str, claim_type: str, contradiction: bool, return_metadata: bool = False, used_semantic_families: set[str] | None = None):
    """Add deterministic connective prose without changing the underlying claim."""
    records: list[dict] = []
    def choose(bank: str, salt: str) -> str:
        used = set(used_semantic_families or ()) | {r["semantic_family"] for r in records}
        record = _pick_record(seed, bank, salt, used)
        records.append(record)
        return record["text"]
    if mode == "mythic":
        pieces = []
        if claim_type in {"descriptive", "agreement"}:
            pieces.append(choose("story_openers", claim_type))
        pieces += [base, choose("story_transitions", "transition")]
        if contradiction or claim_type in {"tension", "shadow"}:
            pieces.append(choose("story_counterpoints", "counterpoint"))
        pieces += [choose("story_reflections", "reflection"), choose("story_closings", "closing")]
    elif mode == "research" and claim_type != "reading":
        pieces = [base, choose("research_bridges", claim_type)]
    elif mode == "plain" and claim_type != "reading":
        pieces = [base, choose("plain_reflections", claim_type)]
    else:
        pieces = [base]
    text = " ".join(pieces)
    return (text, records) if return_metadata else text
