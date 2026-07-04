"""
Identity Engine — Master Orchestrator (v0.3.0)
==============================================

Runs ALL encoders on all identity strings and produces
a unified multi-dimensional signature for each identity.

Encoders:
1. Pythagorean numerology (expression, soul urge, personality)
2. Chaldean numerology (name number, compound number)
3. Ordinal A1Z26 + reverse + reduced
4. Linguistic analysis (entropy, syllables, phonetics)
5. Binary/Prime encoding
6. Hebrew Gematria (absolute + ordinal)
7. Greek Isopsephy (digital root chain)
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from encoders.pythagorean import pythagorean_signature
from encoders.chaldean import chaldean_signature
from encoders.ordinal import ordinal_signature
from encoders.linguistic import linguistic_signature
from encoders.binary_prime import binary_prime_signature
from encoders.gematria import gematria_signature
from encoders.isopsephy import isopsephy_signature

# Optional encoders (require birth data)
HAS_Astrology = False
HAS_HumanDesign = False
HAS_Psychology = False

try:
    from encoders.astrology import compute_chart
    HAS_Astrology = True
except Exception:
    pass

try:
    from encoders.human_design import compute_human_design
    HAS_HumanDesign = True
except Exception:
    pass

try:
    from encoders.psychology import create_profile
    HAS_Psychology = True
except Exception:
    pass


# ==================== IDENTITY STRINGS ====================

IDENTITIES = [
    # Person
    {
        "id": "human:kirk_evan_brown",
        "text": "Kirk Evan Brown",
        "birth": {"year": 1982, "month": 2, "day": 4, "hour": 1, "minute": 42,
                  "timezone_offset": -7, "location": "Evanston, Wyoming, USA",
                  "lat": 41.2633, "lon": -110.9631},
    },
    # Aliases
    {"id": "identity:alias:captain", "text": "Captain"},
    {"id": "identity:alias:capt", "text": "CAPT"},
    {"id": "identity:alias:capt_cortex", "text": "Capt Cortex"},
    # Handles
    {"id": "identity:handle:knowurknot", "text": "Knowurknot"},
    # Projects
    {"id": "project:capt", "text": "CAPT"},
    {"id": "project:frankencapt", "text": "FrankenCAPT"},
    {"id": "project:biocapt", "text": "bioCAPT"},
    {"id": "project:inversion_labs", "text": "Inversion Labs"},
    {"id": "project:jennai", "text": "JennAI"},
    {"id": "project:synsync", "text": "SynSync"},
    {"id": "project:sigil", "text": "Sigil"},
    {"id": "project:sentinel", "text": "Sentinel"},
    {"id": "project:titan", "text": "Titan"},
    # Partners
    {"id": "human:jenn", "text": "Jenn"},
    {"id": "partner:jenn", "text": "Jenn"},
    # Collaborators
    {"id": "collaborator:ornith", "text": "Ornith"},
    # Platform
    {"id": "platform:hermes", "text": "Hermes"},
    {"id": "platform:openrouter", "text": "OpenRouter"},
]


def compute_unified_signature(identity: dict) -> dict:
    """Run all encoders and produce a unified multi-dimensional signature."""
    text = identity["text"]
    birth = identity.get("birth")

    # Core 7 encoders (always available)
    pyth = pythagorean_signature(text)
    chald = chaldean_signature(text)
    ord_ = ordinal_signature(text)
    ling = linguistic_signature(text)
    bin_prime = binary_prime_signature(text)
    gema = gematria_signature(text)
    iso = isopsephy_signature(text)

    result = {
        "id": identity["id"],
        "text": text,
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "dimensions": 0,
        "encoders": {
            "pythagorean": {
                "total": pyth.total,
                "expression": pyth.reduced,
                "master_preserved": pyth.master_preserved,
                "soul_urge": pyth.soul_urge,
                "personality": pyth.personality,
                "soul_urge_total": pyth.soul_urge_total,
                "personality_total": pyth.personality_total,
                "balance_number": pyth.balance_number,
                "hidden_passion": pyth.hidden_passion,
                "karmic_lessons": pyth.karmic_lessons,
                "intensity_table": pyth.intensity_table,
                "vowel_ratio": round(len(pyth.vowels) / len(pyth.letter_values), 3) if pyth.letter_values else 0,
            },
            "chaldean": {
                "compound_number": chald.compound_number,
                "name_number": chald.name_number,
                "soul_urge": chald.soul_urge,
                "personality": chald.personality,
                "intensity_table": chald.intensity_table,
            },
            "ordinal": {
                "ordinal_total": ord_.ordinal_total,
                "ordinal_reduced": ord_.ordinal_reduced,
                "reverse": ord_.reverse_total,
                "reverse_reduced": ord_.reverse_reduced,
                "reduced_total": ord_.reduced_total,
            },
            "linguistic": {
                "letter_count": ling.letter_count,
                "unique_letters": ling.unique_letters,
                "shannon_entropy": ling.shannon_entropy,
                "max_possible_entropy": ling.max_possible_entropy,
                "entropy_ratio": ling.entropy_ratio,
                "vowel_ratio": ling.vowel_ratio,
                "syllable_estimate": ling.syllable_estimate,
                "plosive_count": ling.plosive_count,
                "fricative_count": ling.fricative_count,
                "nasal_count": ling.nasal_count,
                "bigrams_top5": ling.bigrams[:5] if hasattr(ling, 'bigrams') else [],
                "repetition_ratio": ling.letter_repetition_ratio,
                "is_palindrome": ling.is_palindrome,
            },
            "binary_prime": {
                "binary_string": bin_prime.binary_string,
                "binary_weight": bin_prime.binary_weight,
                "binary_entropy": bin_prime.binary_entropy,
                "prime_total": bin_prime.prime_total,
                "prime_reduced": bin_prime.prime_reduced,
                "vowel_power": bin_prime.vowel_power,
                "consonant_power": bin_prime.consonant_power,
                "polarity_score": bin_prime.polarity_score,
                "polarity_ratio": bin_prime.polarity_ratio,
            },
            "gematria": {
                "absolute_total": gema.absolute_total,
                "absolute_reduced": gema.absolute_reduced,
                "ordinal_total": gema.ordinal_total,
                "ordinal_reduced": gema.ordinal_reduced,
                "reduced_total": gema.reduced_total,
                "letter_values": gema.letter_values,
                "gematria_ordinal_ratio": gema.gematria_ordinal_ratio,
            },
            "isopsephy": {
                "total": iso.total,
                "reduced": iso.reduced,
                "digital_root_chain": iso.digital_root_chain,
                "letter_values": iso.letter_values,
                "greek_correspondence": [
                    {"letter": g["latin"], "greek": g["greek"], "value": g["value"]}
                    for g in iso.greek_correspondence
                ],
            },
        },
    }

    # Count dimensions
    dim_count = 0
    for enc in result["encoders"].values():
        dim_count += len(enc)
    result["dimensions"] = dim_count

    # Optional: Astrology (requires birth data)
    if birth and HAS_Astrology:
        try:
            chart = compute_chart(
                birth["year"], birth["month"], birth["day"],
                birth["hour"], birth["minute"],
                birth["timezone_offset"], birth["location"],
            )
            result["encoders"]["astrology"] = {
                "sun_sign": chart.sun_sign,
                "moon_sign": chart.moon_sign,
                "ascendant": chart.ascendant,
                "descendant": chart.descendant,
                "midheaven": chart.midheaven,
                "chart_ruler": chart.chart_ruler,
                "dominant_element": chart.dominant_element,
                "dominant_quality": chart.dominant_quality,
                "lunar_phase": chart.lunar_phase,
                "is_waxing": chart.is_waxing,
                "planets": [
                    {"planet": p.planet, "sign": p.sign, "degree": round(p.sign_degree, 2),
                     "retrograde": p.is_retrograde}
                    for p in chart.planets
                ],
                "aspects": [
                    {"planets": (a.planet1, a.planet2), "type": a.aspect_type,
                     "exact": a.is_exact, "orb": round(a.orb, 2)}
                    for a in chart.aspects[:15]
                ],
                "houses": chart.houses,
                "confidence": chart.confidence,
            }
            dim_count += 20
        except Exception as e:
            result["encoders"]["astrology"] = {"error": str(e)}

    # Optional: Human Design (requires birth data)
    if birth and HAS_HumanDesign:
        try:
            hd = compute_human_design(
                birth["year"], birth["month"], birth["day"],
                birth["hour"], birth["minute"],
                birth["timezone_offset"], birth["location"],
            )
            result["encoders"]["human_design"] = {
                "type": hd.hd_type,
                "strategy": hd.strategy,
                "authority": hd.authority,
                "profile": hd.profile_number,
                "not_self_theme": hd.not_self_theme,
                "signature": hd.signature,
                "definition": hd.definition,
                "personality_gates": [
                    {"gate": g.gate, "line": g.line, "planet": g.planet,
                     "color": g.color, "tone": g.tone}
                    for g in hd.personality_gates
                ],
                "design_gates": [
                    {"gate": g.gate, "line": g.line, "planet": g.planet}
                    for g in hd.design_gates
                ],
                "channels": hd.channels,
                "centers": hd.centers,
                "gates": hd.gates,
                "confidence": hd.confidence,
            }
            dim_count += 15
        except Exception as e:
            result["encoders"]["human_design"] = {"error": str(e)}

    result["dimensions"] = dim_count
    return result


def run_engine():
    """Run the complete engine and generate all outputs."""
    print("Human Metadata Engine v0.3.0")
    print("=" * 60)
    print(f"Running {len(IDENTITIES)} identities through 7+ encoders...")
    print()

    # Compute all signatures
    signatures = []
    for identity in IDENTITIES:
        try:
            sig = compute_unified_signature(identity)
            signatures.append(sig)
            dims = sig["dimensions"]
            enc = len(sig["encoders"])
            print(f"  ✓ {identity['id']:<40} {dims:>3} dimensions, {enc} encoders")
        except Exception as e:
            print(f"  ✗ {identity['id']:<40} ERROR: {e}")

    # Save signatures
    os.makedirs("output", exist_ok=True)
    with open("output/unified_signatures.json", "w") as f:
        json.dump(signatures, f, indent=2, default=str)
    print(f"\nSaved {len(signatures)} signatures to output/unified_signatures.json")

    # Summary statistics
    total_dims = sum(s["dimensions"] for s in signatures)
    avg_dims = total_dims / len(signatures) if signatures else 0
    print(f"\nTotal dimensions computed: {total_dims}")
    print(f"Average per identity: {avg_dims:.0f}")

    # Encoder coverage
    encoder_counts = {}
    for sig in signatures:
        for enc_name in sig["encoders"]:
            encoder_counts[enc_name] = encoder_counts.get(enc_name, 0) + 1
    print(f"\nEncoder coverage:")
    for name, count in sorted(encoder_counts.items()):
        print(f"  {name:<20} {count}/{len(signatures)} identities")

    return signatures


if __name__ == "__main__":
    run_engine()
