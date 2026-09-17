"""Compose specific local readings from evidence, without changing motif scores."""
from __future__ import annotations

from .reading_library import (
    ASPECTS, AUTHORITIES, CENTERS, GATE_PROMPTS, HD_TYPES, HOUSES,
    LIBRARY_VERSION, NUMBERS, PLANETS, PROFILE_LINES, SIGN_THEMES, TAROT,
)

CHAPTERS = {
    "name_reading": "The language of your name",
    "natal_reading": "Your natal sky: placement by placement",
    "aspect_reading": "Conversations within the chart",
    "design_reading": "Your Human Design: pace and participation",
    "center_reading": "Defined and undefined centers",
    "gate_reading": "Your active gates: questions to explore",
    "channel_reading": "Your complete channels",
    "tarot_reading": "Your name-derived tarot archetype",
    "symbol_reading": "Other symbolic lenses",
}


def reading_entries(packet: dict) -> list[dict]:
    entries = []
    items = packet["evidence_items"]
    placements = {(i["role"], i["subsystem"]): i for i in items if i["symbol_family"].startswith("planet_")}

    def add(section, item, title, plain, mythic, related=()):
        evidence = [item, *related]
        research = (
            f"{title}. " + " ".join(f"{e['source_path']} returns {e['source_value']}." for e in evidence)
            + f" The reading applies {LIBRARY_VERSION}, an authored reflection layer, without adding calculated traits or independent support. "
            + plain
        )
        entries.append({"section": section, "title": title, "evidence_ids": sorted({e["evidence_id"] for e in evidence}),
                        "texts": {"plain": plain, "mythic": mythic, "research": research},
                        "library_version": LIBRARY_VERSION})

    for item in items:
        family, value, role = item["symbol_family"], item["source_value"], item["role"]
        if family == "reduced_number" and value in NUMBERS:
            theme, gift, balance, image = NUMBERS[value]
            field = item["source_path"].rsplit(".", 1)[-1]
            lens = {"expression": "the whole name as an expressive pattern", "soul_urge": "the vowels as an inward-facing symbolic lens", "personality": "the consonants as an outward-facing symbolic lens"}.get(field, "the name through this particular alphabet and reduction convention")
            title = f"{item['system'].title()} · {field.replace('_', ' ')} {value}"
            add("name_reading", item, title,
                f"{title} explores {lens}. Here, {value} is read through {theme}: {gift}. The useful counterweight is {balance}. Choose a recent situation and ask where each approach would have helped. A matching number in another alphabet can be interesting, but the shared name input does not turn repetition into independent confirmation.",
                f"For {title}, imagine {image}. This image gives {lens} a story: the invitation is {gift}, while the turning point asks for {balance}. Place a real moment beside this scene. Keep the detail that illuminates it, and leave the rest on the page.")
        elif family == "planet_sign" and value in SIGN_THEMES and role in PLANETS:
            theme, practice, balance, image = SIGN_THEMES[value]
            related = []
            house = placements.get((role, "planet_house"))
            retro = placements.get((role, "planet_retrograde"))
            house_text = ""
            if house and type(house["source_value"]) is int and house["source_value"] in HOUSES:
                related.append(house)
                house_text = f" Its returned house {house['source_value']} places this reflection in the arena of {HOUSES[house['source_value']]} in this house convention."
            retro_text = ""
            if retro and retro["source_value"] is True:
                related.append(retro)
                retro_text = " The returned retrograde flag describes apparent motion; use review and reconsideration as an optional metaphor, not a forecast of setbacks."
            add("natal_reading", item, f"{role} in {value}",
                f"{role} in {value} brings the symbolic lens of {PLANETS[role]} into the vocabulary of {theme}. Explore it by {practice}; balance that with {balance}.{house_text}{retro_text} Recall an example that fits and one that does not, so the reading remains a conversation with your experience.",
                f"{role} in {value}: picture {image}. In this scene, {PLANETS[role]} becomes a question of {theme}. The next movement might be {practice}; the scene gains depth through {balance}.{house_text}{retro_text} You decide whether this image belongs in your story.", related)
        elif family == "zodiac_sign" and item["source_path"].endswith(".ascendant") and value in SIGN_THEMES:
            theme, practice, balance, image = SIGN_THEMES[value]
            add("natal_reading", item, f"Ascendant in {value}",
                f"The returned ascendant is {value}. As a lens on first approaches, it invites reflection on {theme}. Compare how you enter a familiar setting and an unfamiliar one: where does {practice} help, and where is {balance} more useful? This angle depends on the supplied birth time and location.",
                f"At the threshold of the chart stands {value}, pictured here as {image}. Consider the first movement into a room, a project, or a conversation. The image asks about {practice}, with room for {balance}. It is a time-dependent chart angle, not a fixed description of every encounter.")
        elif family == "aspect" and value.get("type") in ASPECTS and all(p in PLANETS for p in value.get("planets", [])):
            a, b = value["planets"]
            theme, meaning, practice = ASPECTS[value["type"]]
            title = f"{a}–{b} {value['type'].lower()}"
            add("aspect_reading", item, title,
                f"{title}: the chart pairs {PLANETS[a]} with {PLANETS[b]}. In this symbolic reading, {meaning}; the theme is {theme}. Try to {practice}. This is a prompt for comparing two needs in one concrete situation, not evidence that a conflict or talent must exist.",
                f"In the {title}, two characters meet: one carries {PLANETS[a]}, the other {PLANETS[b]}. Their scene is written around {theme}, not a verdict about either one. To explore the scene, {practice}. Let the actual situation determine whether the metaphor earns its place.")
        elif family == "human_design_type" and value in HD_TYPES:
            theme, practice, image = HD_TYPES[value]
            add("design_reading", item, value,
                f"Your returned Human Design type is {value}. This reading uses {theme} as a lens on participation. To make it concrete, {practice}. Record what supports your involvement and what drains your attention, without assuming that a chart category decides your capacity. The type belongs to a symbolic classification, not a measure of ability.",
                f"The {value} chapter opens with {image}. The story asks about {theme}: where does effort meet an invitation worth answering? To bring the image down to earth, {practice}. A role in this symbolic story is something to explore, not an instruction to limit yourself.")
        elif family == "human_design_strategy":
            if value not in {"Respond", "Wait for the Invitation", "Inform", "Wait a Lunar Cycle"}:
                continue
            add("design_reading", item, f"Strategy · {value}",
                f"The returned strategy is {value}. Treat it as a question about the timing and context of participation. Compare an action taken because the situation invited it with an action taken to relieve pressure. What differed in the response you received? Keep your practical judgment and responsibilities in the foreground.",
                f"The instruction on this chapter's doorway reads {value}. Rather than a command, imagine it as a pause before entering the scene: what is being asked, who is involved, and what would make your next move welcome? The story offers a rhythm to examine, not a rule that outranks your judgment.")
        elif family == "human_design_authority" and value in AUTHORITIES:
            practice = AUTHORITIES[value]
            add("design_reading", item, f"Authority · {value}",
                f"The calculation returns {value} authority. For an optional experiment, {practice}. Write down both your initial preference and what the experience teaches you afterward. This compares a symbolic decision style with observation; it does not replace information, deliberation, or appropriate advice for consequential choices.",
                f"In the {value} authority chapter, the compass is an image for attention rather than an infallible instrument. Try to {practice}. Return to the page after the experience and see whether the direction still makes sense. The metaphor is useful only while it leaves you free to reconsider.")
        elif family == "human_design_profile" and isinstance(value, list) and len(value) == 2 and all(type(v) is int and v in PROFILE_LINES for v in value):
            a, b = (PROFILE_LINES[v] for v in value)
            title = f"Profile {value[0]}/{value[1]}"
            add("design_reading", item, title,
                f"{title} combines the line themes of {a[0]} and {b[0]}. Keep both in view rather than reducing the profile to a single personality label. Ask {a[1]}, then ask {b[1]}. The two questions may fit different settings; noticing that difference is more useful than making them agree in every situation.",
                f"{title} gives this chapter two voices: {a[0]} and {b[0]}. One asks {a[1]}; the other asks {b[1]}. Let them take turns describing a recent experience. Their conversation can remain unfinished without either voice being wrong.")
        elif family == "human_design_definition" and value in {"Single", "Split", "Triple Split", "Quadruple Split", "None"}:
            add("design_reading", item, f"Definition · {value}",
                f"The returned definition is {value}. Definition describes connectivity among defined centers in the chart, not personal completeness. Use it to inspect which centers and channels the engine groups together. If you compare this with how you process an experience alone or in company, keep the comparison exploratory rather than treating relationships as missing chart parts.",
                f"Definition is the map's account of its connected roads: here it reads {value}. It does not decide whether the traveler is whole. Follow the drawn connections, then notice how an idea develops in solitude and in conversation. The person is larger than the map.")
        elif family == "human_design_center" and isinstance(value, dict) and value.get("name") in CENTERS:
            name, defined = value["name"], value["defined"]
            state = "defined" if defined else "undefined"
            question = "when a familiar response is useful and when it needs updating" if defined else "what changes with the setting and what remains your own preference"
            add("center_reading", item, f"{name} · {state}",
                f"{name} is returned as {state}; this chapter associates it with {CENTERS[name]}. Consider {question}. Definition is a property of the returned channel map, not a higher or lower score. An undefined center is not a missing human capacity, and a defined center does not establish consistency in every real situation.",
                f"In the map's room for {CENTERS[name]}, {name} is marked {state}. Imagine this as a question about the room's use, not its worth: {question}? No room makes the traveler more or less complete. Compare the image with experience before carrying it into your story.")
        elif family == "human_design_gate" and value in GATE_PROMPTS:
            practice = GATE_PROMPTS[value]
            add("gate_reading", item, f"Gate {value}",
                f"Gate {value} is active in the returned chart. Its authored reflection prompt is to {practice}. Choose one recent example and describe what helped, what complicated it, and what you would try differently. An active gate alone does not establish a complete channel or a measured personal trait.",
                f"At gate {value}, the story pauses to ask you to {practice}. Set a real scene beside that invitation: who was there, what was possible, and what changed? The gate is a doorway for reflection; it does not decide the shape of the whole journey.")
        elif family == "human_design_channel" and isinstance(value, dict):
            gates = value.get("gates", [])
            if len(gates) != 2 or not all(type(g) is int and g in GATE_PROMPTS for g in gates):
                continue
            a, b = gates
            add("channel_reading", item, f"Channel {a}–{b}",
                f"The engine returns the complete channel {a}–{b}. Read its two gate prompts together: {GATE_PROMPTS[a]}; and {GATE_PROMPTS[b]}. Explore a situation in which these invitations support each other and another in which they pull attention in different directions. Completeness describes chart topology, not mastery of either theme.",
                f"A returned road connects gates {a} and {b}. At one end: {GATE_PROMPTS[a]}. At the other: {GATE_PROMPTS[b]}. Imagine a scene that needs both movements, without requiring them to happen at the same moment. The drawn road is real within the calculation; its story remains yours to question.")
        elif family == "tarot_correspondence" and type(value) is int and 0 <= value < len(TAROT):
            title, theme, practice, image = TAROT[value]
            add("tarot_reading", item, f"{title} · index {value}",
                f"Your name calculation maps to {title}, at Major Arcana index {value}. This is a fixed correspondence, not a shuffled draw. The authored theme is {theme}: {practice}. Think of one experience where that question feels useful, and one where it misses the point. The card is a reflective image, not a prediction or a hidden fact about you.",
                f"The name-derived card places {image} on the page: {title}. Its theme of {theme} becomes an invitation to {practice}. Let a memory answer the image, and allow the answer to complicate it. This scene comes from a fixed name mapping, not chance selection or a message about the future.")
        elif family in {"sephirah", "wu_xing_element"} and item["interpretive_tags"]:
            themes = ", ".join(item["interpretive_tags"])
            add("symbol_reading", item, f"{item['system'].replace('_', ' ').title()} · {value}",
                f"The returned symbol {value} is mapped here to {themes}. This is the project's comparison vocabulary, not a claim that different traditions teach the same thing. Pick one of those themes and find a concrete example before drawing a connection with the rest of the reading. Keep the source tradition's separate context visible.",
                f"Another margin of the atlas carries {value}, with the authored threads {themes}. Let this image sit beside the other chapters without dissolving its own history into theirs. A useful connection should illuminate a real question; resemblance alone need not become agreement.")
    # Stable, human-readable order; never choose symbols by opaque hash order.
    order = {k: i for i, k in enumerate(CHAPTERS)}
    entries.sort(key=lambda e: (order[e["section"]], e["title"]))
    return entries
