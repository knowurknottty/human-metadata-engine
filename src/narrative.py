"""
Personality Narrative Generator
================================

Converts numeric identity signatures into human-readable
personality descriptions. No LLM required — pure template-based.

Usage:
    from src.narrative import generate_narrative
    story = generate_narrative(signature_dict)
"""

from typing import Optional


def generate_narrative(sig: dict, identity_name: str = "") -> str:
    """Generate a personality narrative from a unified signature."""
    encoders = sig.get("encoders", {})
    analytics = sig.get("analytics", {})
    name = identity_name or sig.get("id", "Unknown")

    sections = []

    # Header
    sections.append(f"# {name} — Symbolic Description\n")
    sections.append("> This is a deterministic reflection built from configured name mappings. It is not a personality assessment, cultural-origin inference, or prediction.\n")

    # Numerological Core
    pyth = encoders.get("pythagorean", {})
    chal = encoders.get("chaldean", {})
    expr = pyth.get("expression", pyth.get("life_path", "?"))
    soul = pyth.get("soul_urge", "?")
    pers = pyth.get("personality", "?")

    if isinstance(expr, (int, float)):
        expr_trait = _numerology_trait("expression", expr)
        sections.append(f"## Core Identity (Expression {expr})")
        sections.append(f"{name} carries the energy of {expr_trait}.\n")
        if isinstance(soul, (int, float)):
            soul_trait = _numerology_trait("soul_urge", soul)
            sections.append(f"Internally, {name} is driven by {soul_trait} (Soul Urge {soul}).")
        if isinstance(pers, (int, float)):
            pers_trait = _numerology_trait("personality", pers)
            sections.append(f"To the world, {name} presents as {pers_trait} (Personality {pers}).")
        sections.append("")

    # Linguistic Profile
    ling = encoders.get("linguistic", {})
    entropy = ling.get("entropy", ling.get("shannon_entropy", 0))
    syllables = ling.get("syllables", ling.get("syllable_count", 0))
    vowel_ratio = ling.get("vowel_ratio", 0)

    if entropy or syllables:
        sections.append("## Name Linguistics")
        if isinstance(entropy, (int, float)) and entropy > 0:
            if entropy > 3.5:
                sections.append(f"The name has high phonetic complexity (entropy {entropy:.2f}), suggesting depth and layers.")
            elif entropy > 2.5:
                sections.append(f"The name has balanced phonetic structure (entropy {entropy:.2f}), suggesting clarity and approachability.")
            else:
                sections.append(f"The name has simple phonetic structure (entropy {entropy:.2f}), suggesting directness and strength.")
        if isinstance(syllables, (int, float)) and syllables > 0:
            if syllables <= 2:
                sections.append(f"At {int(syllables)} syllables, the name is concise — quick to say, hard to forget.")
            elif syllables <= 4:
                sections.append(f"At {int(syllables)} syllables, the name has a natural rhythm — easy to carry in conversation.")
            else:
                sections.append(f"At {int(syllables)} syllables, the name is substantial — it takes space, and fills it.")
        sections.append("")

    # Polarity & Balance
    binary = encoders.get("binary_prime", {})
    polarity = binary.get("polarity_score", binary.get("vowel_power", 0))
    consonant_power = binary.get("consonant_power", 0)

    if polarity or consonant_power:
        sections.append("## Polarity & Balance")
        total = (polarity or 0) + (consonant_power or 0)
        if total > 0:
            v_ratio = (polarity or 0) / total
            if v_ratio > 0.6:
                sections.append(f"The name has a vowel-forward polarity ({v_ratio:.0%} vowel energy); this describes the string, not the person.")
            elif v_ratio < 0.4:
                sections.append(f"The name has a consonant-forward polarity ({v_ratio:.0%} vowel energy); this describes the string, not the person.")
            else:
                sections.append(f"The name is balanced in polarity ({v_ratio:.0%} vowel energy — near perfect equilibrium).")
        sections.append("")

    # Symbolic Depth
    gem = encoders.get("gematria", {})
    iso = encoders.get("isopsephy", {})
    gem_val = gem.get("absolute_value", gem.get("value", 0))
    iso_val = iso.get("absolute_value", iso.get("value", 0))

    if gem_val or iso_val:
        sections.append("## Symbolic Depth")
        if gem_val:
            sections.append(f"Hebrew Gematria value: {gem_val} (reduced: {_digital_root(gem_val)}).")
        if iso_val:
            sections.append(f"Greek Isopsephy value: {iso_val} (reduced: {_digital_root(iso_val)}).")
        if gem_val and iso_val:
            cross = abs(gem_val - iso_val)
            if cross < 10:
                sections.append(f"The Hebrew and Greek values are remarkably close (Δ={cross}), suggesting deep cross-cultural resonance.")
        sections.append("")

    # Composite Resonance
    resonance = analytics.get("composite_resonance", analytics.get("resonance_score", 0))
    if resonance:
        sections.append("## Overall Resonance")
        if resonance > 80:
            sections.append(f"Resonance score: {resonance:.0f}/100 — Exceptional. This identity shows extraordinary alignment across all symbolic systems.")
        elif resonance > 60:
            sections.append(f"Resonance score: {resonance:.0f}/100 — Strong. This identity shows meaningful alignment across symbolic systems.")
        elif resonance > 40:
            sections.append(f"Resonance score: {resonance:.0f}/100 — Moderate. This identity has areas of alignment and areas of contrast.")
        else:
            sections.append(f"Resonance score: {resonance:.0f}/100 — Complex. This identity shows deliberate tension across symbolic systems.")
        sections.append("")

    # Karmic Lessons
    if pyth:
        karmic = pyth.get("karmic_lessons", pyth.get("missing_numbers", []))
        if karmic:
            sections.append("## Karmic Lessons")
            lesson_map = {
                1: "leadership and self-assertion",
                2: "cooperation and patience",
                3: "self-expression and creativity",
                4: "stability and foundation-building",
                5: "freedom and adaptability",
                6: "responsibility and service",
                7: "introspection and spiritual seeking",
                8: "material mastery and authority",
                9: "compassion and completion",
            }
            lessons = [lesson_map.get(l, f"the energy of {l}") for l in karmic if isinstance(l, int)]
            if lessons:
                sections.append(f"The name carries karmic lessons in: {', '.join(lessons)}.")
                sections.append("These are areas of growth — challenges that forge strength.")
            sections.append("")

    # Conclusion
    sections.append("---")
    sections.append("*Generated by the Human Metadata Engine — symbolic narrative only; no personality or real-world outcome is inferred.*")

    return "\n".join(sections)


def _numerology_trait(system: str, value: int) -> str:
    """Map numerology value to personality trait."""
    traits = {
        "expression": {
            1: "natural leadership and independence",
            2: "diplomacy and sensitivity",
            3: "creative expression and communication",
            4: "building, structure, and discipline",
            5: "freedom, adventure, and versatility",
            6: "nurturing, responsibility, and harmony",
            7: "introspection, analysis, and spiritual depth",
            8: "material mastery, ambition, and authority",
            9: "compassion, completion, and universal service",
        },
        "soul_urge": {
            1: "a desire for independence and personal achievement",
            2: "a desire for partnership and peace",
            3: "a desire for creative self-expression",
            4: "a desire for stability and order",
            5: "a desire for freedom and experience",
            6: "a desire for love and service to others",
            7: "a desire for knowledge and inner truth",
            8: "a desire for material success and recognition",
            9: "a desire to make a global difference",
        },
        "personality": {
            1: "confidence, assertiveness, and a pioneering spirit",
            2: "grace, cooperativeness, and attentiveness",
            3: "charm, humor, and magnetic social energy",
            4: "reliability, practicality, and grounded presence",
            5: "dynamic energy, curiosity, and adventurous spirit",
            6: "warmth, beauty, and a caretaker's aura",
            7: "mystery, wisdom, and quiet intensity",
            8: "power, success, and commanding presence",
            9: "generosity, idealism, and worldly compassion",
        },
    }
    reduced = _digital_root(value) if isinstance(value, int) else value
    system_traits = traits.get(system, {})
    return system_traits.get(reduced, f"the energy of {value}")


def _digital_root(n: int) -> int:
    """Compute digital root (repeated sum of digits)."""
    if not isinstance(n, int):
        return 0
    n = abs(n)
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n
