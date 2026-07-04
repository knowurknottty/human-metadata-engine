"""
Identity Engine — Master Orchestrator
=====================================

Runs ALL encoders on all identity strings and produces
a unified multi-dimensional signature for each identity.

Encoders:
1. Pythagorean numerology
2. Chaldean numerology
3. Ordinal A1Z26 + reverse + reduced
4. Linguistic analysis (entropy, bigrams, phonetics)
5. Binary letter class + prime-index encoding
6. Life path (birth date numerology)

Output: unified JSON with all encoder results per identity.
"""

from __future__ import annotations
import sys
import os
import json
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from encoders.pythagorean import pythagorean_signature, life_path_number
from encoders.chaldean import chaldean_signature
from encoders.ordinal import ordinal_signature
from encoders.linguistic import linguistic_signature
from encoders.binary_prime import binary_prime_signature


# Identity seed data
IDENTITIES = [
    {"text": "Kirk Evan Brown", "type": "birth_name", "role": "human"},
    {"text": "Capt", "type": "nickname", "role": "alias"},
    {"text": "CAPT", "type": "project", "role": "architecture"},
    {"text": "Captain", "type": "persona", "role": "archetype"},
    {"text": "Knowurknot", "type": "handle", "role": "paradox_key"},
    {"text": "Captain Knowurknot", "type": "persona", "role": "public_myth"},
    {"text": "bioCAPT", "type": "project", "role": "embodiment"},
    {"text": "FrankenCAPT", "type": "project", "role": "synthesis"},
    {"text": "Jenn-ai", "type": "agent", "role": "executive"},
    {"text": "SynSync", "type": "project", "role": "resonance"},
    {"text": "Inversion Labs", "type": "brand", "role": "container"},
    {"text": "Knowledge Bubbles", "type": "project", "role": "mining"},
    {"text": "Soul Fractal Engine", "type": "project", "role": "identity"},
    {"text": "Wyrd", "type": "project", "role": "fate"},
    {"text": "CAPT-RYS", "type": "project", "role": "research"},
    {"text": "SYNCHEF", "type": "project", "role": "curator"},
    {"text": "Jenn", "type": "nickname", "role": "partner"},
]

# Birth metadata
BIRTH = {"year": 1982, "month": 2, "day": 4, "time": "01:42", "place": "Evanston, WY, USA"}


def compute_unified_signature(identity: dict) -> dict:
    """Run all encoders on a single identity string."""
    text = identity["text"]

    # Pythagorean
    pyth = pythagorean_signature(text)

    # Chaldean
    chald = chaldean_signature(text)

    # Ordinal (all three variants)
    ordi = ordinal_signature(text)

    # Linguistic
    ling = linguistic_signature(text)

    # Binary/Prime
    bp = binary_prime_signature(text)

    return {
        "identity": identity,
        "pythagorean": {
            "expression": pyth.reduced,
            "master_preserved": pyth.master_preserved,
            "soul_urge": pyth.soul_urge,
            "personality": pyth.personality,
            "balance": pyth.balance_number,
            "total": pyth.total,
            "hidden_passion": pyth.hidden_passion,
            "karmic_lessons": pyth.karmic_lessons,
            "intensity_table": pyth.intensity_table,
            "vowel_consonant_ratio": len(pyth.vowels) / len(pyth.letter_values) if pyth.letter_values else 0,
        },
        "chaldean": {
            "name_number": chald.name_number,
            "compound_number": chald.compound_number,
            "soul_urge": chald.soul_urge,
            "personality": chald.personality,
            "intensity_table": chald.intensity_table,
        },
        "ordinal": {
            "standard": ordi.ordinal_total,
            "standard_reduced": ordi.ordinal_reduced,
            "reverse": ordi.reverse_total,
            "reverse_reduced": ordi.reverse_reduced,
            "reduced": ordi.reduced_total,
            "reduced_final": ordi.reduced_reduced,
            "vowel_total": ordi.vowel_total,
            "consonant_total": ordi.consonant_total,
        },
        "linguistic": {
            "letter_count": ling.letter_count,
            "token_count": ling.token_count,
            "vowel_ratio": ling.vowel_ratio,
            "shannon_entropy": ling.shannon_entropy,
            "entropy_ratio": ling.entropy_ratio,
            "syllable_estimate": ling.syllable_estimate,
            "unique_letters": ling.unique_letters,
            "letter_repetition_ratio": ling.letter_repetition_ratio,
            "is_palindrome": ling.is_palindrome,
            "plosive_count": ling.plosive_count,
            "fricative_count": ling.fricative_count,
            "nasal_count": ling.nasal_count,
            "liquid_count": ling.liquid_count,
            "consonant_cluster_count": ling.consonant_cluster_count,
            "bigrams_top5": [{"bigram": b.bigram, "count": b.count} for b in ling.bigrams[:5]],
        },
        "binary_prime": {
            "binary_string": bp.binary_string,
            "binary_weight": bp.binary_weight,
            "binary_entropy": bp.binary_entropy,
            "prime_total": bp.prime_total,
            "prime_reduced": bp.prime_reduced,
            "vowel_power": bp.vowel_power,
            "consonant_power": bp.consonant_power,
            "polarity_score": bp.polarity_score,
            "polarity_ratio": bp.polarity_ratio,
        },
    }


def compute_cross_encoder_resonance(sigs: list[dict]) -> list[dict]:
    """Compare all pairs across all encoder dimensions."""
    comparisons = []

    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            a, b = sigs[i], sigs[j]

            # Expression matches across systems
            pyth_match = a["pythagorean"]["expression"] == b["pythagorean"]["expression"]
            chald_match = a["chaldean"]["name_number"] == b["chaldean"]["name_number"]
            ord_match = a["ordinal"]["standard_reduced"] == b["ordinal"]["standard_reduced"]
            rev_match = a["ordinal"]["reverse_reduced"] == b["ordinal"]["reverse_reduced"]

            # Linguistic similarity
            entropy_diff = abs(a["linguistic"]["shannon_entropy"] - b["linguistic"]["shannon_entropy"])
            syllable_match = a["linguistic"]["syllable_estimate"] == b["linguistic"]["syllable_estimate"]

            # Binary/prime resonance
            polarity_same_sign = (a["binary_prime"]["polarity_score"] > 0) == (b["binary_prime"]["polarity_score"] > 0)

            # Count total matches
            match_count = sum([pyth_match, chald_match, ord_match, rev_match, syllable_match, polarity_same_sign])
            match_ratio = match_count / 6

            comparisons.append({
                "pair": [a["identity"]["text"], b["identity"]["text"]],
                "pythagorean_match": pyth_match,
                "chaldean_match": chald_match,
                "ordinal_match": ord_match,
                "reverse_match": rev_match,
                "syllable_match": syllable_match,
                "polarity_same_sign": polarity_same_sign,
                "entropy_difference": round(entropy_diff, 4),
                "match_ratio": round(match_ratio, 4),
                "match_count": match_count,
            })

    # Sort by match ratio descending
    comparisons.sort(key=lambda x: -x["match_ratio"])
    return comparisons


def compute_identity_vector(sig: dict) -> dict:
    """Extract a numeric vector for each identity (for embedding/clustering)."""
    return {
        "text": sig["identity"]["text"],
        "vector": [
            sig["pythagorean"]["expression"],
            sig["pythagorean"]["soul_urge"],
            sig["pythagorean"]["personality"],
            sig["chaldean"]["name_number"],
            sig["chaldean"]["soul_urge"],
            sig["ordinal"]["standard_reduced"],
            sig["ordinal"]["reverse_reduced"],
            sig["binary_prime"]["binary_weight"],
            sig["binary_prime"]["prime_reduced"],
            sig["linguistic"]["syllable_estimate"],
            sig["linguistic"]["unique_letters"],
            round(sig["linguistic"]["shannon_entropy"]),
            round(sig["binary_prime"]["polarity_score"] / 10),  # normalize
        ],
    }


def generate_full_report() -> dict:
    """Run the complete engine and produce all outputs."""
    print("Running all encoders on 17 identities...")

    # Compute all signatures
    signatures = []
    for identity in IDENTITIES:
        sig = compute_unified_signature(identity)
        signatures.append(sig)
        print(f"  ✓ {identity['text']}")

    # Birth date numerology
    birth_lp = life_path_number(BIRTH["year"], BIRTH["month"], BIRTH["day"])

    # Cross-encoder resonance
    print("\nComputing cross-encoder resonance...")
    resonance = compute_cross_encoder_resonance(signatures)

    # Identity vectors
    print("Computing identity vectors...")
    vectors = [compute_identity_vector(sig) for sig in signatures]

    # Build output
    output = {
        "engine_version": "0.2.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "subject": {
            "id": "human:kirk_evan_brown",
            "preferred_display": "Capt",
            "birth": {
                "date": f"{BIRTH['year']}-{BIRTH['month']:02d}-{BIRTH['day']:02d}",
                "time": BIRTH["time"],
                "place": BIRTH["place"],
            },
        },
        "birth_numerology": {
            "life_path_raw": birth_lp.life_path_raw,
            "life_path_reduced": birth_lp.life_path_reduced,
            "life_path_master": birth_lp.life_path_master,
            "birthday": birth_lp.birthday_number,
            "attitude": birth_lp.attitude_number,
            "birth_year": birth_lp.birth_year_number,
        },
        "encoder_suite": {
            "pythagorean": "Standard Pythagorean letter mapping (A=1..S=1, master 11/22/33)",
            "chaldean": "Ancient Chaldean mapping (9 sacred, no master numbers)",
            "ordinal": "A1Z26 standard + reverse + digital root reduced",
            "linguistic": "Entropy, bigrams, phonetics, syllables, symmetry",
            "binary_prime": "Vowel/consonant binary + prime-index encoding",
        },
        "signatures": signatures,
        "cross_encoder_resonance": resonance[:20],  # top 20
        "identity_vectors": vectors,
        "summary": {
            "total_identities": len(signatures),
            "encoder_count": 5,
            "dimensions_per_identity": 50,
            "highest_resonance_pair": resonance[0] if resonance else None,
            "expression_distribution": {},
        },
    }

    # Expression distribution
    expr_dist = {}
    for sig in signatures:
        e = sig["pythagorean"]["expression"]
        expr_dist[e] = expr_dist.get(e, 0) + 1
    output["summary"]["expression_distribution"] = expr_dist

    return output


if __name__ == "__main__":
    output = generate_full_report()

    # Save
    out_path = os.path.join(os.path.dirname(__file__), "..", "output", "unified_signatures.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nSaved to: {out_path}")
    print(f"Total signatures: {len(output['signatures'])}")
    print(f"Dimensions per identity: ~{output['summary']['dimensions_per_identity']}")
    print(f"Highest resonance: {output['summary']['highest_resonance_pair']['pair']}")
