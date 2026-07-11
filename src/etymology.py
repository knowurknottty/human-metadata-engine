"""Source-backed name etymology with explicit epistemic boundaries.

This module stores curated lexical claims only. It never infers personality,
ancestry, social status, or genetic origin from a name.
"""

from __future__ import annotations

import re
from typing import Any

SOURCES: dict[str, dict[str, str]] = {
    "familysearch_armenian_surnames": {
        "title": "Discovering the Meaning of Your Armenian Family Name",
        "publisher": "FamilySearch",
        "url": "https://www.familysearch.org/en/blog/your-armenian-surname",
        "quality": "secondary-genealogy-guide",
    },
    "armeniapedia_surname_dictionary_a": {
        "title": "Dictionary of Armenian Surnames — A",
        "publisher": "Armeniapedia / C. K. Garabed",
        "url": "https://www.armeniapedia.org/wiki/Dictionary_of_Armenian_Surnames_A",
        "quality": "community-compiled-secondary",
    },
    "kirk_word": {
        "title": "Kirk (word)",
        "publisher": "reference summary",
        "url": "https://en.wikipedia.org/wiki/Kirk_(word)",
        "quality": "tertiary-reference",
    },
    "evan_name": {
        "title": "Evan",
        "publisher": "reference summary",
        "url": "https://en.wikipedia.org/wiki/Evan",
        "quality": "tertiary-reference",
    },
    "brown_surname": {
        "title": "Brown (surname)",
        "publisher": "reference summary",
        "url": "https://en.wikipedia.org/wiki/Brown_(surname)",
        "quality": "tertiary-reference",
    },
    "agha_title": {
        "title": "Agha (title)",
        "publisher": "reference summary",
        "url": "https://en.wikipedia.org/wiki/Agha_(title)",
        "quality": "tertiary-reference",
    },
}

KNOWN_COMPONENTS: dict[str, dict[str, Any]] = {
    "KIRK": {
        "kind": "given_name",
        "language_path": ["Scots / Northern English", "Old Norse kirkja", "Greek kyriakon"],
        "literal_glosses": ["church", "the Lord's house"],
        "confidence": "high",
        "source_ids": ["kirk_word"],
        "scope": "lexical history only; no personality inference",
    },
    "EVAN": {
        "kind": "given_name",
        "language_path": ["Welsh Evan / Iefan / Ieuan", "Latin Johannes", "Hebrew Yohanan"],
        "literal_glosses": ["God is gracious", "YHWH has shown favor"],
        "confidence": "high",
        "source_ids": ["evan_name"],
        "scope": "name-family etymology; not a claim about the bearer",
    },
    "BROWN": {
        "kind": "surname",
        "language_path": ["Middle English brun / broun", "Old English brun"],
        "literal_glosses": ["brown-colored", "historically descriptive of hair, complexion, or clothing"],
        "confidence": "high",
        "source_ids": ["brown_surname"],
        "scope": "common surname origin; a specific Brown line can have a different path",
    },
    "AGHYARIAN": {
        "kind": "armenian_surname",
        "variants": ["AGHIARIAN"],
        "morphology": [
            {
                "form": "agha",
                "role": "root",
                "origin": "Turkic / Ottoman honorific",
                "glosses": ["master", "lord", "respected or influential man"],
            },
            {
                "form": "-ian",
                "role": "Armenian patronymic suffix",
                "glosses": ["issued from", "family of", "descendant of"],
            },
        ],
        "literal_glosses": ["family or descendants of Agha"],
        "confidence": "moderate-high",
        "source_ids": [
            "armeniapedia_surname_dictionary_a",
            "familysearch_armenian_surnames",
            "agha_title",
        ],
        "scope": (
            "surname morphology only; it does not prove that a particular ancestor "
            "held land, office, nobility, or the Ottoman title"
        ),
        "cautions": [
            "Aghyarian and Aghiarian are treated as spelling variants.",
            "Similar-looking surnames are not automatically the same lineage.",
            "Native Armenian spelling and ancestral locality remain unresolved.",
        ],
    },
    "AGHIARIAN": {
        "alias_of": "AGHYARIAN",
    },
}


def _record_for(token: str) -> dict[str, Any] | None:
    record = KNOWN_COMPONENTS.get(token.upper())
    if not record:
        return None
    if "alias_of" in record:
        canonical = record["alias_of"]
        resolved = dict(KNOWN_COMPONENTS[canonical])
        resolved["matched_variant"] = token
        resolved["canonical_form"] = canonical.title()
        return resolved
    resolved = dict(record)
    resolved["canonical_form"] = token.title()
    return resolved


def analyze_name_etymology(
    name: str,
    *,
    lineage_surnames: list[str] | None = None,
) -> dict[str, Any]:
    """Return curated etymology records and unresolved components.

    The function deliberately avoids composing the meanings into a factual
    sentence. Any poetic synthesis belongs in an explicitly interpretive layer.
    """
    tokens = [part for part in re.split(r"[\s\-_]+", name.strip()) if part]
    components: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for position, token in enumerate(tokens):
        record = _record_for(token)
        if record is None:
            unresolved.append(token)
            continue
        record["input_form"] = token
        record["position"] = position
        components.append(record)

    lineage_records: list[dict[str, Any]] = []
    for surname in lineage_surnames or []:
        record = _record_for(surname)
        if record is None:
            lineage_records.append({
                "input_form": surname,
                "status": "unresolved",
                "scope": "preserved exactly as supplied; no guessed normalization",
            })
        else:
            record["input_form"] = surname
            record["relationship"] = "lineage_surname"
            lineage_records.append(record)

    source_ids = sorted({
        source_id
        for record in components + lineage_records
        for source_id in record.get("source_ids", [])
    })

    return {
        "name": name,
        "components": components,
        "lineage_surnames": lineage_records,
        "unresolved_components": unresolved,
        "sources": {source_id: SOURCES[source_id] for source_id in source_ids},
        "epistemic_status": "historical-linguistic",
        "personality_inference": False,
        "genetic_inference": False,
    }


__all__ = ["SOURCES", "KNOWN_COMPONENTS", "analyze_name_etymology"]
