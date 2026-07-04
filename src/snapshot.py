"""
Personality Snapshot
====================

Synthesizes astrology (birth data), Human Design (birth data), and
psychology (user-supplied) into a single narrative profile. Each layer
is optional — the narrative adapts to whatever data is available.

Output is deterministic template-based prose, not an LLM call, so the
same inputs always produce the same snapshot.
"""

from __future__ import annotations

SIGN_TRAITS = {
    "Aries": ("cardinal fire", "direct, initiating energy that leads by acting first"),
    "Taurus": ("fixed earth", "steady, sensory-grounded persistence that builds durable things"),
    "Gemini": ("mutable air", "quick, connective curiosity that thrives on exchange of ideas"),
    "Cancer": ("cardinal water", "protective emotional intelligence oriented toward belonging"),
    "Leo": ("fixed fire", "expressive, warm-centered confidence that seeks creative visibility"),
    "Virgo": ("mutable earth", "precise, service-oriented analysis that perfects systems"),
    "Libra": ("cardinal air", "relational balance-seeking that weighs every perspective"),
    "Scorpio": ("fixed water", "intense, penetrating focus that transforms what it touches"),
    "Sagittarius": ("mutable fire", "expansive, meaning-hunting optimism that needs a horizon"),
    "Capricorn": ("cardinal earth", "strategic, long-game ambition that engineers outcomes"),
    "Aquarius": ("fixed air", "systems-level originality that reforms structures from outside"),
    "Pisces": ("mutable water", "porous, imaginative empathy that dissolves boundaries"),
}

ELEMENT_THEMES = {
    "Fire": "identity runs on inspiration and momentum",
    "Earth": "identity runs on tangibility and consolidation",
    "Air": "identity runs on ideas, language, and connection",
    "Water": "identity runs on feeling-tone and resonance",
}

HD_TYPE_TEXT = {
    "Generator": ("a sustainable life-force builder", "respond to what shows up rather than initiating from the mind"),
    "Manifesting Generator": ("a multi-track builder-initiator", "respond, then move fast and inform along the way"),
    "Manifestor": ("an initiating catalyst", "inform before acting so impact lands without resistance"),
    "Projector": ("a systems guide", "wait for recognition and invitation before directing others"),
    "Reflector": ("a lunar barometer of community health", "wait a full lunar cycle before major decisions"),
}

ATTACHMENT_TEXT = {
    "secure": "a secure attachment pattern, giving relationships a stable base",
    "anxious": "an anxious attachment lean, heightening sensitivity to relational signals",
    "avoidant": "an avoidant attachment lean, favoring self-reliance under stress",
    "disorganized": "a mixed attachment pattern, alternating between closeness and distance",
    "fearful_avoidant": "a fearful-avoidant pattern, both craving and guarding against closeness",
}


def personality_snapshot(name: str,
                         astrology: dict | None = None,
                         human_design: dict | None = None,
                         psychology: dict | None = None) -> dict:
    """Build a narrative snapshot from whichever layers are present.

    astrology / human_design: the encoder dicts from the unified signature.
    psychology: {"big_five": {...}, "mbti": "XXXX", "enneagram": {"type": n,
                 "wing": n}, "attachment": "secure"} (all keys optional).
    Returns {"available_layers": [...], "narrative": str, "highlights": [...]}
    """
    layers = []
    paragraphs = []
    highlights = []

    if astrology and not astrology.get("error") and astrology.get("sun_sign"):
        layers.append("astrology")
        sun = astrology.get("sun_sign", "")
        moon = astrology.get("moon_sign", "")
        asc = astrology.get("ascendant", "")
        element = astrology.get("dominant_element", "")
        lunar = astrology.get("lunar_phase", "")
        sun_q, sun_desc = SIGN_TRAITS.get(sun, ("", "distinctive solar energy"))
        moon_q, moon_desc = SIGN_TRAITS.get(moon, ("", "a distinctive emotional signature"))
        asc_q, asc_desc = SIGN_TRAITS.get(asc, ("", "a distinctive first impression"))
        p = (f"Celestially, {name} carries a {sun} Sun ({sun_q}): {sun_desc}. "
             f"The {moon} Moon colors the inner life with {moon_desc}, "
             f"while a {asc} Ascendant means others first meet {asc_desc}.")
        if element:
            p += f" The chart is weighted toward {element}: {ELEMENT_THEMES.get(element, '')}."
        if lunar:
            p += (f" Born under a {lunar} moon, there is a native orientation toward "
                  + ("building and increase." if astrology.get("is_waxing")
                     else "release, distillation, and completion."))
        paragraphs.append(p)
        highlights.append(f"{sun} Sun / {moon} Moon / {asc} Rising")

    if human_design and not human_design.get("error") and human_design.get("type"):
        layers.append("human_design")
        hd_type = human_design.get("type", "")
        strategy = human_design.get("strategy", "")
        authority = human_design.get("authority", "")
        profile = human_design.get("profile", [])
        channels = human_design.get("channels", [])
        role, advice = HD_TYPE_TEXT.get(hd_type, ("a unique energetic type", "follow strategy"))
        p = (f"In the Human Design system, {name} operates as a {hd_type} — {role}. "
             f"The working strategy is \"{strategy}\" with {authority} authority: "
             f"decisions land best when they {advice}.")
        if profile:
            p += f" The {profile[0]}/{profile[1]} profile shapes how learning and purpose interlock."
        if channels:
            names = ", ".join(c["name"] for c in channels[:4])
            p += f" Defined channels ({names}) mark where this energy is consistent and reliable."
        paragraphs.append(p)
        highlights.append(f"{hd_type}, {authority} authority")

    if psychology:
        b5 = psychology.get("big_five")
        mbti = psychology.get("mbti")
        enne = psychology.get("enneagram") or {}
        attach = psychology.get("attachment")
        bits = []
        if b5:
            traits = {"openness": "openness to experience",
                      "conscientiousness": "conscientiousness",
                      "extraversion": "extraversion",
                      "agreeableness": "agreeableness",
                      "neuroticism": "emotional reactivity"}
            top = max(b5, key=lambda k: b5[k] if k in traits else -1)
            low = min(b5, key=lambda k: b5[k] if k in traits else 2)
            bits.append(f"self-reported Big Five scores peak in {traits.get(top, top)} "
                        f"({round(b5[top]*100)}th pct) and sit lowest in "
                        f"{traits.get(low, low)} ({round(b5[low]*100)}th pct)")
        if mbti:
            bits.append(f"the MBTI type is {mbti}")
        if enne.get("type"):
            wing = f"w{enne['wing']}" if enne.get("wing") else ""
            bits.append(f"the Enneagram core is Type {enne['type']}{wing}")
        if attach:
            bits.append(ATTACHMENT_TEXT.get(attach, f"a {attach} attachment style"))
        if bits:
            layers.append("psychology")
            paragraphs.append(
                f"Psychologically, {name} shows " + "; ".join(bits) +
                ". Unlike the symbolic layers, these are self-reported "
                "measures and carry their stated confidence levels.")
            highlights.append("Psychology layer present (self-reported)")

    if not paragraphs:
        narrative = (f"No birth data or psychological assessments were supplied for "
                     f"{name}, so the snapshot rests on name-derived encoders alone. "
                     "Add a birth date/time/place to unlock the celestial and Human "
                     "Design layers, or supply assessments for the psychology layer.")
    else:
        opener = (f"{name} — a composite read across "
                  f"{len(layers)} layer{'s' if len(layers) != 1 else ''} "
                  f"({', '.join(layers)}).")
        narrative = opener + "\n\n" + "\n\n".join(paragraphs)

    return {
        "available_layers": layers,
        "narrative": narrative,
        "highlights": highlights,
    }
