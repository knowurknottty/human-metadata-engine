"""Historical-textual ontology for the Sumerian me (𒈨).

This module encodes only named items visible in the ETCSL translation of
*Inana and Enki* (ETCSL 1.3.1), chiefly Segment I. Damaged/illegible entries
are excluded rather than reconstructed.

The inventory is a corpus reference, not a personality test. No historical
evidence is known that maps a modern person's name, birth data, or numerical
signature to a particular me, so personal assignment is disabled by default.
"""

from __future__ import annotations

from typing import Any, Final


ONTOLOGY_VERSION: Final[str] = "etcsl-1.3.1-visible-inventory-v1"
SOURCE_TEXT_ID: Final[str] = "ETCSL-1.3.1"
SOURCE_TEXT_TITLE: Final[str] = "Inana and Enki"
CUNEIFORM_SIGN: Final[str] = "𒈨"
CUNEIFORM_CODEPOINT: Final[str] = "U+12228"

ME_CATEGORIES: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": "sovereignty_and_offices",
        "label": "Sovereignty, offices, and regalia",
        "items": (
            "office of en priest", "office of lagar priest", "divinity",
            "great and good crown", "royal throne", "noble sceptre",
            "staff and crook", "noble dress", "black garment", "colourful garment",
            "shepherdship", "kingship",
            "office of egir-zid priestess", "office of nin-diĝir priestess",
            "office of išib priest", "office of lu-maḫ priest",
            "office of gudug priest", "mistress of heaven",
        ),
    },
    {
        "id": "liminality_and_cult",
        "label": "Liminality, cult, and sacred function",
        "items": (
            "constancy", "going down to the underworld",
            "coming up from the underworld", "kur-ĝara priest",
            "cultic functionary saĝ-ursaĝ", "holy purification rites",
            "holy niĝin-ĝar shrine",
        ),
    },
    {
        "id": "conflict_and_power",
        "label": "Conflict, power, and civic disruption",
        "items": (
            "sword and club", "standard", "quiver", "heroism", "power",
            "wickedness", "righteousness", "plundering of cities",
            "rebel lands", "strife", "triumph",
        ),
    },
    {
        "id": "sexuality_and_social_space",
        "label": "Sexuality and social space",
        "items": (
            "sexual intercourse", "kissing", "prostitution",
            "cultic prostitute", "holy tavern", "attractiveness of women",
        ),
    },
    {
        "id": "speech_music_and_performance",
        "label": "Speech, music, and performance",
        "items": (
            "forthright speech", "deceitful speech", "grandiloquent speech",
            "loud musical instruments", "art of song", "making lamentations",
            "rejoicing", "holy tigi, lilis, ub, meze and ala drums",
        ),
    },
    {
        "id": "crafts_and_technical_practice",
        "label": "Crafts and technical practice",
        "items": (
            "craft of the carpenter", "craft of the coppersmith",
            "craft of the scribe", "craft of the smith",
            "craft of the leather-worker", "craft of the fuller",
            "craft of the builder", "craft of the reed-worker",
        ),
    },
    {
        "id": "knowledge_and_judgment",
        "label": "Knowledge, counsel, and judgment",
        "items": (
            "wisdom", "attentiveness", "counselling", "comforting",
            "judging", "decision-making", "establishing of plans (?)",
        ),
    },
    {
        "id": "household_pastoral_and_labor",
        "label": "Household, pastoral life, fire, and labor",
        "items": (
            "shepherd's hut", "piling up glowing charcoals", "sheepfold",
            "kindling of fire", "extinguishing of fire", "hard work",
            "assembled family", "descendants", "being on the move",
            "being sedentary", "venerable old age",
        ),
    },
    {
        "id": "social_affect_and_norms",
        "label": "Social affect and norms",
        "items": ("deceit", "kindness", "respect", "awe", "reverent silence"),
    },
)


MODERN_CAPACITY_CROSSWALK: Final[dict[str, tuple[str, ...]]] = {
    "sovereignty_and_offices": ("governance", "role", "authority", "stewardship"),
    "liminality_and_cult": ("transition", "ritual", "boundary", "transformation"),
    "conflict_and_power": ("agency", "conflict", "defense", "collective_order"),
    "sexuality_and_social_space": ("intimacy", "attraction", "social_exchange"),
    "speech_music_and_performance": ("communication", "expression", "performance"),
    "crafts_and_technical_practice": ("making", "technical_skill", "recording"),
    "knowledge_and_judgment": ("knowledge", "counsel", "evaluation", "planning"),
    "household_pastoral_and_labor": ("care", "labor", "maintenance", "mobility", "lineage"),
    "social_affect_and_norms": ("social_norms", "respect", "awe", "prosociality"),
}


def build_modern_capacity_crosswalk() -> dict[str, Any]:
    """Return an explicitly modern analytical projection over the historical inventory."""
    return {
        "version": "inversion-labs-human-capacity-crosswalk-v1",
        "epistemic_layer": "modern_analytic",
        "historical_claim": False,
        "mappings": [
            {"category_id": category_id, "capacity_domains": list(domains)}
            for category_id, domains in MODERN_CAPACITY_CROSSWALK.items()
        ],
        "personalization_policy": {
            "status": "disabled_by_default",
            "permitted_basis": "explicit observed or self-reported evidence under a separately versioned mapping",
            "forbidden_basis": ["name", "birth_data", "numerology", "astrology", "symbolic_resonance_score"],
        },
    }


def build_sumerian_me_ontology() -> dict[str, Any]:
    """Return the bounded historical inventory and its epistemic contract."""
    categories = [
        {
            "id": entry["id"],
            "label": entry["label"],
            "items": list(entry["items"]),
            "classification_epistemic_layer": "modern_analytic",
        }
        for entry in ME_CATEGORIES
    ]
    named_item_count = sum(len(entry["items"]) for entry in categories)
    return {
        "ontology_version": ONTOLOGY_VERSION,
        "source_text_id": SOURCE_TEXT_ID,
        "source_text_title": SOURCE_TEXT_TITLE,
        "cuneiform_sign": CUNEIFORM_SIGN,
        "cuneiform_codepoint": CUNEIFORM_CODEPOINT,
        "evidence_layer": "historical_textual",
        "inventory_scope": (
            "Named items visible in the ETCSL translation of Inana and Enki, "
            "especially Segment I; damaged and illegible entries are omitted."
        ),
        "category_count": len(categories),
        "named_item_count": named_item_count,
        "attestation_status": "81 legible named items in the surviving ETCSL final recitation; damaged placeholders excluded",
        "categories": categories,
        "category_policy": (
            "The nine thematic categories are modern analytical groupings created by the Human Metadata project. "
            "They are not categories asserted by the Sumerian text and they do not preserve source order."
        ),
        "modern_capacity_crosswalk": build_modern_capacity_crosswalk(),
        "narrative_transport": {
            "origin": "Eridug / Enki's abzu",
            "recipient_and_carrier": "Inana",
            "vehicle": "Boat of Heaven",
            "destination": "Unug (Uruk)",
            "scope": "narrative structure in ETCSL 1.3.1, not a literal logistics claim",
        },
        "ontology_observation_epistemic_layer": "analytical_inference",
        "ontology_observation": (
            "The surviving list is heterogeneous: it includes offices, regalia, "
            "ritual roles, social practices, crafts, speech forms, affects, "
            "knowledge, conflict, kinship, music, and civic institutions. "
            "The me should therefore not be modeled as one narrow object type."
        ),
        "lacunae_present": True,
        "uncertain_items_retained": ["establishing of plans (?)"],
        "damaged_items_policy": "exclude rather than reconstruct",
        "personal_mapping": None,
        "personal_mapping_policy": (
            "disabled by default: the historical corpus does not establish a "
            "mapping from a modern person's name, birth data, or numeric signature "
            "to a particular me"
        ),
        "modern_interpretive_projection": {
            "status": "disabled",
            "requirement": (
                "Any future Human Metadata correspondence must be a separately "
                "versioned modern convention and must never be presented as "
                "Sumerian historical evidence."
            ),
        },
    }
