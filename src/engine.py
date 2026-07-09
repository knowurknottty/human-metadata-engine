import logging
"""
Identity Engine — Master Orchestrator (v0.4.0)
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
8. Astrology (Swiss Ephemeris, requires birth data)
9. Human Design (requires birth data)

New in v0.4.0 (second-order analytics on top of the encoders):
- Composite resonance score (0-100) per identity
- Identity fingerprint (deterministic visual-hash spec)
- Cross-encoder correlation matrix (Pearson + digit agreement)
- Identity similarity matrix + batch comparative report
- Personality snapshots (astrology + HD + psychology narrative)
- Famous-figure reference identities with real birth data
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

from analytics import (
    composite_resonance, identity_fingerprint,
    cross_encoder_correlations, identity_similarity_matrix, batch_report,
)
from snapshot import personality_snapshot

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
        "id": "human:john_michael_smith",
        "text": "John Michael Smith",
        "birth": {"year": 1985, "month": 6, "day": 15, "hour": 10, "minute": 30,
                  "timezone_offset": -7, "location": "Portland, Oregon, USA",
                  "lat": 45.5152, "lon": -122.6765},
    },
    # Aliases
    {"id": "identity:alias:captain", "text": "Captain"},
    {"id": "identity:alias:capt", "text": "CAPT"},
    {"id": "identity:alias:capt_cortex", "text": "Capt Cortex"},
    # Handles
    {"id": "identity:handle:testuser42", "text": "testuser42"},
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
    {
        "id": "human:jennifer_larson",
        "text": "Jennifer Jean Larson",
        "birth": {"year": 1985, "month": 12, "day": 31, "hour": 4, "minute": 5,
                  "timezone_offset": -5, "location": "Tampa, Florida, USA",
                  "lat": 27.9506, "lon": -82.4572},
    },
    # Collaborators
    {"id": "collaborator:ornith", "text": "Ornith"},
    # Platform
    {"id": "platform:hermes", "text": "Hermes"},
    {"id": "platform:openrouter", "text": "OpenRouter"},
    # Reference figures (well-known names, demonstrating range; birth
    # data from public record — times approximate where noted)
    {
        "id": "figure:albert_einstein",
        "text": "Albert Einstein",
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 101, "minute": 30,
                  "timezone_offset": 0.67, "location": "Ulm, Germany",
                  "lat": 48.4011, "lon": 9.9876},
    },
    {
        "id": "figure:nikola_tesla",
        "text": "Nikola Tesla",
        "birth": {"year": 1856, "month": 7, "day": 10, "hour": 0, "minute": 0,
                  "timezone_offset": 1, "location": "Smiljan, Croatia",
                  "lat": 44.5794, "lon": 15.3089},
    },
    {
        "id": "figure:marie_curie",
        "text": "Marie Curie",
        "birth": {"year": 1867, "month": 11, "day": 7, "hour": 102, "minute": 0,
                  "timezone_offset": 1.4, "location": "Warsaw, Poland",
                  "lat": 52.2297, "lon": 21.0122},
    },
    {
        "id": "figure:ada_lovelace",
        "text": "Ada Lovelace",
        "birth": {"year": 1815, "month": 12, "day": 10, "hour": 102, "minute": 0,
                  "timezone_offset": 0, "location": "London, England",
                  "lat": 51.5074, "lon": -0.1278},
    },
    {
        "id": "figure:alan_turing",
        "text": "Alan Turing",
        "birth": {"year": 1912, "month": 6, "day": 23, "hour": 2, "minute": 15,
                  "timezone_offset": 0, "location": "London, England",
                  "lat": 51.5237, "lon": -0.1585},
    },
    {
        "id": "figure:leonardo_da_vinci",
        "text": "Leonardo da Vinci",
        "birth": {"year": 1452, "month": 4, "day": 15, "hour": 21, "minute": 40,
                  "timezone_offset": 0.73, "location": "Vinci, Italy",
                  "lat": 43.7842, "lon": 10.9236},
    },
    {"id": "figure:frida_kahlo", "text": "Frida Kahlo"},
    {"id": "figure:david_bowie", "text": "David Bowie"},
    {"id": "figure:hypatia", "text": "Hypatia of Alexandria"},
    {"id": "figure:carl_jung", "text": "Carl Gustav Jung"},
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
                lat=birth.get("lat"), lon=birth.get("lon"),
            )
            result["encoders"]["astrology"] = {
                "sun_sign": chart.sun_sign,
                "moon_sign": chart.moon_sign,
                "ascendant": chart.ascendant,
                "midheaven": chart.midheaven,
                "chart_ruler": chart.chart_ruler,
                "dominant_element": chart.dominant_element,
                "dominant_modality": chart.dominant_modality,
                "element_counts": chart.element_counts,
                "modality_counts": chart.modality_counts,
                "yin_yang_balance": chart.yin_yang_balance,
                "lunar_phase": chart.lunar_phase,
                "is_waxing": chart.is_waxing,
                "planets": [
                    {"planet": p.planet, "sign": p.sign, "degree": round(p.sign_degree, 2),
                     "retrograde": p.is_retrograde}
                    for p in chart.planets
                ],
                "aspects": [
                    {"planets": (a.planet1, a.planet2), "type": a.aspect_name,
                     "exact": a.exact, "orb": round(a.orb, 2)}
                    for a in chart.aspects[:15]
                ],
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
                lat=birth.get("lat"), lon=birth.get("lon"),
            )
            result["encoders"]["human_design"] = {
                "type": hd.hd_type,
                "strategy": hd.strategy,
                "authority": hd.authority,
                "profile": list(hd.profile_number),
                "profile_description": hd.profile_description,
                "not_self_theme": hd.not_self_theme,
                "signature": hd.signature,
                "definition": hd.definition_type,
                "incarnation_cross": hd.incarnation_cross,
                "personality_gates": [
                    {"gate": g.gate, "line": g.line, "planet": g.planet, "sign": g.sign}
                    for g in hd.personality_gates
                ],
                "design_gates": [
                    {"gate": g.gate, "line": g.line, "planet": g.planet}
                    for g in hd.design_gates
                ],
                "channels": hd.channels,
                "centers": [
                    {"name": c.name, "defined": c.defined}
                    for c in hd.centers
                ],
                "gates": hd.all_gates,
                "confidence": hd.confidence,
            }
            dim_count += 15
        except Exception as e:
            result["encoders"]["human_design"] = {"error": str(e)}

    # Second-order analytics (v0.4.0)
    result["resonance"] = composite_resonance(result)
    result["fingerprint"] = identity_fingerprint(result)
    result["snapshot"] = personality_snapshot(
        text,
        astrology=result["encoders"].get("astrology"),
        human_design=result["encoders"].get("human_design"),
        psychology=identity.get("psychology"),
    )
    dim_count += len(result["resonance"]["components"]) + 1  # score + components
    dim_count += len(result["fingerprint"]["spokes"]) + 2    # spokes + hash + symmetry

    result["dimensions"] = dim_count
    return result


def run_engine():
    """Run the complete engine and generate all outputs."""
    logging.info("Human Metadata Engine v0.4.0")
    logging.info("=" * 60)
    logging.info(f"Running {len(IDENTITIES)} identities through 9 encoders + analytics...")
    logging.info()

    # Compute all signatures
    signatures = []
    for identity in IDENTITIES:
        try:
            sig = compute_unified_signature(identity)
            signatures.append(sig)
            dims = sig["dimensions"]
            enc = len(sig["encoders"])
            logging.info(f"  ✓ {identity['id']:<40} {dims:>3} dimensions, {enc} encoders")
        except Exception as e:
            logging.info(f"  ✗ {identity['id']:<40} ERROR: {e}")

    # Save signatures
    os.makedirs("output", exist_ok=True)
    with open("output/unified_signatures.json", "w") as f:
        json.dump(signatures, f, indent=2, default=str)
    logging.info(f"\nSaved {len(signatures)} signatures to output/unified_signatures.json")

    # Summary statistics
    total_dims = sum(s["dimensions"] for s in signatures)
    avg_dims = total_dims / len(signatures) if signatures else 0
    logging.info(f"\nTotal dimensions computed: {total_dims}")
    logging.info(f"Average per identity: {avg_dims:.0f}")

    # Encoder coverage
    encoder_counts = {}
    for sig in signatures:
        for enc_name in sig["encoders"]:
            encoder_counts[enc_name] = encoder_counts.get(enc_name, 0) + 1
    logging.info(f"\nEncoder coverage:")
    for name, count in sorted(encoder_counts.items()):
        logging.info(f"  {name:<20} {count}/{len(signatures)} identities")

    # ---- v0.4.0 analytics outputs ----
    correlations = cross_encoder_correlations(signatures)
    with open("output/encoder_correlations.json", "w") as f:
        json.dump(correlations, f, indent=2)
    logging.info("\nSaved cross-encoder correlation matrix to output/encoder_correlations.json")

    report_json, report_md = batch_report(signatures)
    with open("output/comparative_report.json", "w") as f:
        json.dump(report_json, f, indent=2)
    with open("output/comparative_report.md", "w") as f:
        f.write(report_md)
    logging.info("Saved batch comparative report to output/comparative_report.{json,md}")

    top = report_json["ranking"][0]
    logging.info(f"\nHighest resonance: {top['text']} ({top['resonance']}/100)")

    return signatures


if __name__ == "__main__":
    run_engine()
