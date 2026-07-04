"""
Full Human Design Report Generator
====================================

Generates a comprehensive, beautifully formatted markdown report
covering every aspect of the Human Design chart.

Sections:
1. Chart Overview
2. Type & Strategy
3. Authority
4. Profile
5. Centers (defined & undefined)
6. Channels & Gates
7. Incarnation Cross
8. Variables & Environment
9. Planetary Positions
10. Synthesis & Life Strategy
"""

from typing import Optional


def generate_hd_report(chart, name: str = "") -> str:
    """Generate a full Human Design report from a chart object."""
    sections = []

    # ── Header ──
    sections.append(f"# Human Design Reading — {name}")
    sections.append("")
    sections.append(f"**Chart Date:** {chart.birth_datetime}")
    sections.append(f"**Location:** {chart.birth_location}")
    sections.append(f"**Confidence:** {chart.confidence:.0%}")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 1: Chart Overview ──
    sections.append("## 1. Chart Overview")
    sections.append("")
    sections.append(f"Your Human Design chart reveals a **{chart.hd_type}** with **{chart.authority} Authority**.")
    sections.append(f"You carry **Profile {chart.profile_number[0]}.{chart.profile_number[1]}** — {chart.profile_description}.")
    sections.append("")
    sections.append(f"Your life strategy is **\"{chart.strategy}\"** and your signature state is **{chart.signature}**.")
    sections.append(f"When you are not living according to your design, you experience **{chart.not_self_theme}**.")
    sections.append("")
    sections.append(f"Your definition type is **{chart.definition_type}**, meaning your energy is structured in "
                    f"{'a single continuous channel' if chart.definition_type == 'Single Definition' else 'multiple connected channels'}.")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 2: Type & Strategy ──
    sections.append("## 2. Type & Strategy")
    sections.append("")
    sections.append(f"### {chart.hd_type}")
    sections.append("")
    sections.append(f"**{chart.type_description}**")
    sections.append("")
    sections.append(f"**Population:** {chart.type_percentage}")
    sections.append("")
    sections.append(f"**Aura:** {chart.type_aura}")
    sections.append("")
    sections.append(f"**Strategy:** {chart.strategy}")
    sections.append("")
    sections.append(f"**Signature (when living correctly):** {chart.signature}")
    sections.append("")
    sections.append(f"**Not-Self Theme (when off-track):** {chart.not_self_theme}")
    sections.append("")

    # Detailed type explanation
    type_explanations = {
        "Manifestor": (
            "As a Manifestor, you are one of the rare initiators. You have a closed, "
            "repelling aura that protects your energy but can feel intimidating to others. "
            "Your gift is the ability to start things — to impact the world through action. "
            "However, you don't have sustained energy to follow through. Your strategy is to "
            "inform those who will be affected before you act. This removes resistance and "
            "allows your natural peace to emerge. When you try to push through without "
            "informing, you encounter anger — both in yourself and from others."
        ),
        "Generator": (
            "As a Generator, you are the life force of the planet. You have a defined Sacral "
            "center — a powerful motor that generates life force energy when properly engaged. "
            "Your strategy is to respond to what shows up in your life rather than initiating. "
            "When you wait to respond, your sacral gives you a clear gut response: \"uh-huh\" "
            "(yes) or \"un-un\" (no). Following this response leads to deep satisfaction. "
            "When you try to initiate or say yes to things that don't resonate, you experience "
            "frustration."
        ),
        "Manifesting Generator": (
            "As a Manifesting Generator, you are the fastest and most efficient type. You "
            "combine the Generator's life force with the Manifestor's ability to impact. You're "
            "multi-passionate, capable of doing many things at once, and often skip steps — "
            "which can be your genius or your pitfall. Your strategy is to first respond, then "
            "inform. You learn through trial and error, and your signature is satisfaction "
            "and peace."
        ),
        "Projector": (
            "As a Projector, you are here to guide and manage the energy of others. You have "
            "a focused, absorbing aura that takes in and directs the energy around you. You "
            "see deeply into systems and people — but you must wait to be recognized and "
            "invited before sharing your gifts. When you try to push your way in, you experience "
            "bitterness. When you wait for the right invitations, you experience success."
        ),
        "Reflector": (
            "As a Reflector, you are the rarest type — approximately 1% of the population. "
            "You have no consistent definition in your chart, which means you take in and "
            "reflect the energy of your environment and the people around you. Your strategy "
            "is to wait a full lunar cycle (28 days) before making major decisions. Your "
            "experience of life is deeply tied to the health of your community. When you're "
            "in the right environment, you experience surprise and delight."
        ),
    }

    sections.append(type_explanations.get(chart.hd_type, ""))
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 3: Authority ──
    sections.append("## 3. Authority")
    sections.append("")
    sections.append(f"### {chart.authority} Authority")
    sections.append("")
    sections.append(f"**{chart.authority_description}**")
    sections.append("")
    sections.append(f"**Process:** {chart.authority_process}")
    sections.append("")

    # Authority-specific guidance
    authority_guidance = {
        "Emotional": (
            "Your Emotional Authority means you never make decisions in the moment. "
            "The emotional system creates a wave — highs and lows — and clarity only comes "
            "with time. When you first hear about an opportunity or receive a proposal, "
            "you'll likely feel excitement or fear. Neither is clarity. Wait. Sleep on it. "
            "Check in again tomorrow, and the day after. When the emotional charge has "
            "settled and you feel a calm knowing, that's your clarity. The key principle: "
            "\"There is no truth in the now\" for the emotionally defined."
        ),
        "Sacral": (
            "Your Sacral Authority is the most straightforward. Your gut responds with a "
            "clear physical sensation to what shows up in your life. It's either an \"uh-huh\" "
            "(a rising, opening, life-force yes) or an \"un-un\" (a closing, contracting no). "
            "The sacral can only respond to what is presented — it cannot initiate. Wait for "
            "something to respond to, then feel your gut. The sacral response is immediate "
            "and unmistakable when you're paying attention."
        ),
        "Splenic": (
            "Your Splenic Authority is the most primal and fleeting. Your splenic center "
            "gives you intuitive hits in the moment — a quiet knowing that comes once and "
            "is gone. Unlike the emotional wave, there is no waiting with splenic authority. "
            "The hit comes, and you must trust it or lose it. This can feel scary because "
            "there's no second guessing. The splenic always knows what is safe and what is "
            "not — but it speaks in whispers, not shouts."
        ),
        "Ego/Heart": (
            "Your Ego/Heart Authority means you follow your will and your heart. What you "
            "want, and what you're willing to commit to, is your authority. This is rare "
            "and powerful. You don't wait for responses or invitations — you know what you "
            "want and you go for it. The key is genuine desire, not conditioned \"shoulds.\" "
            "When you follow your authentic will, you experience success."
        ),
        "Self-Projected": (
            "Your Self-Projected Authority means you hear your truth through speaking it. "
            "You need to talk through decisions with trusted others — not for their advice, "
            "but to hear yourself speak. Your inner authority emerges through your own voice. "
            "Find a sounding board — a trusted friend or mentor — and talk through your "
            "decisions. You'll know your truth when you hear it."
        ),
        "Mental": (
            "As a Mental Projector, you have no consistent inner authority. Your clarity "
            "comes through outer authority — discussing decisions with trusted advisors and "
            "reflecting on their input. You need the right environment and the right people "
            "to help you hear your own truth. This is not a weakness — it's your design. "
            "You are here to synthesize multiple perspectives into wise counsel."
        ),
        "Lunar": (
            "Your Lunar Authority means you need a full 28-day lunar cycle to find clarity "
            "on major decisions. Each day, check in with how the decision feels. Notice how "
            "your perspective shifts as the moon moves through different gates. After a full "
            "cycle, your body will have processed the decision at every level. This is not "
            "indecision — it's your unique way of knowing."
        ),
    }

    sections.append(authority_guidance.get(chart.authority, ""))
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 4: Profile ──
    sections.append("## 4. Profile")
    sections.append("")
    sections.append(f"### Profile {chart.profile_number[0]}.{chart.profile_number[1]}")
    sections.append("")
    sections.append(f"**{chart.profile_description}**")
    sections.append("")

    # Profile line descriptions
    line_descriptions = {
        1: "Investigator — Foundation through investigation. Needs depth and security before sharing.",
        2: "Hermit — Natural talent that emerges through solitude. Needs to be called out.",
        3: "Martyr — Trial and error through experience. Learns by doing and failing.",
        4: "Opportunist — Influence through networks. Needs a strong foundation of friends.",
        5: "Heretic — Universalization through projection. Others project their needs onto you.",
        6: "Role Model — Three phases of life: trial, retreat, and emergence as a role model.",
    }

    sections.append(f"**Line {chart.profile_number[0]} (Conscious):** {line_descriptions.get(chart.profile_number[0], '')}")
    sections.append("")
    sections.append(f"**Line {chart.profile_number[1]} (Unconscious):** {line_descriptions.get(chart.profile_number[1], '')}")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 5: Centers ──
    sections.append("## 5. Centers")
    sections.append("")
    sections.append("Your bodygraph contains 9 centers. Defined centers (colored) represent consistent "
                    "energy you can rely on. Undefined centers (white) are where you are open to "
                    "influence and amplification from others.")
    sections.append("")

    for center in chart.centers:
        status = "DEFINED" if center.is_defined else "Undefined"
        symbol = "◆" if center.is_defined else "◇"
        sections.append(f"### {symbol} {center.name} — {status}")
        sections.append("")
        sections.append(f"**Theme:** {center.theme}")
        sections.append("")
        sections.append(f"**Not-Self Question:** {center.not_self}")
        sections.append("")
        if center.gates:
            sections.append(f"**Active Gates:** {', '.join(str(g) for g in center.gates)}")
            sections.append("")
        if center.is_defined:
            sections.append(f"You have consistent access to {center.name} energy. "
                          f"This is a reliable resource you can count on.")
        else:
            sections.append(f"The {center.name} center is open in your chart. "
                          f"You are susceptible to conditioning here — be aware of "
                          f"amplifying the themes of this center when around others.")
        sections.append("")

    sections.append("---")
    sections.append("")

    # ── Section 6: Channels & Gates ──
    sections.append("## 6. Channels & Gates")
    sections.append("")
    sections.append(f"### Active Channels ({len(chart.channels)})")
    sections.append("")

    if chart.channels:
        for ch in chart.channels:
            g1, g2 = ch["gates"]
            sections.append(f"#### Channel {g1}–{g2}: {ch['name']}")
            sections.append("")
            sections.append(f"**Centers:** {' → '.join(ch['centers'])}")
            sections.append("")
            sections.append(f"**{ch['description']}**")
            sections.append("")

            # Gate details
            for g in [g1, g2]:
                gate_info = None
                for gp in chart.personality_gates + chart.design_gates:
                    if gp.gate == g:
                        gate_info = gp
                        break
                if gate_info:
                    sections.append(f"- **Gate {g}** ({gate_info.gate_name}): {gate_info.keynote}")
            sections.append("")
    else:
        sections.append("No fully defined channels. This is typical for Reflectors and some Projectors.")
        sections.append("")

    # Active gates
    personality_gates_unique = list({g.gate: g for g in chart.personality_gates}.values())
    design_gates_unique = list({g.gate: g for g in chart.design_gates}.values())

    sections.append(f"### Personality Gates (Conscious — Black) ({len(personality_gates_unique)})")
    sections.append("")
    for g in personality_gates_unique:
        sections.append(f"- **{g.gate}** {g.gate_name} ({g.planet} in {g.sign}) — {g.keynote}")
    sections.append("")

    sections.append(f"### Design Gates (Unconscious — Red) ({len(design_gates_unique)})")
    sections.append("")
    for g in design_gates_unique:
        sections.append(f"- **{g.gate}** {g.gate_name} ({g.planet} in {g.sign}) — {g.keynote}")
    sections.append("")

    sections.append("---")
    sections.append("")

    # ── Section 7: Incarnation Cross ──
    sections.append("## 7. Incarnation Cross")
    sections.append("")
    sections.append(f"### {chart.incarnation_cross}")
    sections.append("")
    sections.append(f"**{chart.incarnation_cross_description}**")
    sections.append("")
    sections.append("Your Incarnation Cross represents your life purpose — the theme you are here "
                    "to embody and express. It is determined by the position of the Sun at your "
                    "birth (Personality) and 88 days before (Design). This is not something you "
                    "achieve — it is something you become as you live correctly by your design.")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 8: Variables & Environment ──
    sections.append("## 8. Variables & Environment")
    sections.append("")
    sections.append(f"### Variable: {chart.variable}")
    sections.append("")
    sections.append(f"### Environment: {chart.environment}")
    sections.append("")
    sections.append(f"### Determination: {chart.determination}")
    sections.append("")
    sections.append(f"### Cognition: {chart.cognition}")
    sections.append("")
    sections.append(f"### Perspective: {chart.perspective}")
    sections.append("")
    sections.append(f"### Tone: {chart.tone}")
    sections.append("")
    sections.append(f"### Color: {chart.color}")
    sections.append("")
    sections.append(f"### Base: {chart.base}")
    sections.append("")
    sections.append("Your Variables describe the specific way your body processes information and "
                    "nourishment. The Environment is the physical setting where you thrive. "
                    "Determination is how your body takes in food and nourishment. "
                    "Cognition is your strongest sense for perceiving the world.")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 9: Planetary Positions ──
    sections.append("## 9. Planetary Positions")
    sections.append("")
    sections.append("### Personality (Conscious — Black)")
    sections.append("")
    sections.append("| Planet | Gate | Line | Sign | Degree |")
    sections.append("|--------|------|------|------|--------|")
    for g in chart.personality_gates:
        sections.append(f"| {g.planet} | **{g.gate}** {g.gate_name} | {g.line} | {g.sign} | {g.sign_degree}° |")
    sections.append("")

    sections.append("### Design (Unconscious — Red)")
    sections.append("")
    sections.append("| Planet | Gate | Line | Sign | Degree |")
    sections.append("|--------|------|------|------|--------|")
    for g in chart.design_gates:
        sections.append(f"| {g.planet} | **{g.gate}** {g.gate_name} | {g.line} | {g.sign} | {g.sign_degree}° |")
    sections.append("")
    sections.append("---")
    sections.append("")

    # ── Section 10: Synthesis ──
    sections.append("## 10. Synthesis & Life Strategy")
    sections.append("")
    sections.append(f"### The Big Picture")
    sections.append("")
    sections.append(f"You are a **{chart.hd_type}** with **{chart.authority} Authority**, "
                    f"living as a **{chart.profile_number[0]}.{chart.profile_number[1]}**. "
                    f"Your life purpose is encoded in the **{chart.incarnation_cross}**.")
    sections.append("")
    sections.append(f"### Daily Practice")
    sections.append("")
    sections.append(f"1. **Strategy:** {chart.strategy}")
    sections.append(f"2. **Authority:** {chart.authority_description}")
    sections.append(f"3. **Signature:** Move toward {chart.signature}")
    sections.append(f"4. **Not-Self:** Notice when you feel {chart.not_self_theme}")
    sections.append("")
    sections.append(f"### Life Theme")
    sections.append("")
    sections.append(f"Your Incarnation Cross — **{chart.incarnation_cross}** — is the overarching "
                    f"theme of your life. Everything in your chart serves this purpose. When you "
                    f"follow your strategy and authority, your cross naturally unfolds.")
    sections.append("")
    sections.append(f"### Key Insight")
    sections.append("")
    if chart.hd_type == "Manifestor":
        sections.append("You are here to initiate. Don't wait for permission. Inform those who "
                      "will be impacted, then act. Your peace comes from informed action, not "
                      "from waiting for the perfect moment.")
    elif chart.hd_type == "Generator":
        sections.append("You are here to respond. Wait for life to come to you, then follow "
                      "your gut. Your satisfaction comes from doing work that lights you up — "
                      "not from forcing things to happen.")
    elif chart.hd_type == "Manifesting Generator":
        sections.append("You are here to respond and then inform. Trust your process of "
                      "trial and error. You don't need to know the whole path — just the "
                      "next step. Your satisfaction comes from efficient, multi-passionate action.")
    elif chart.hd_type == "Projector":
        sections.append("You are here to guide. Wait for recognition and invitation. Your "
                      "gifts are profound — but they must be invited. When you try to push, "
                      "you meet resistance. When you wait, you meet success.")
    elif chart.hd_type == "Reflector":
        sections.append("You are here to reflect. Wait a lunar cycle for major decisions. "
                      "Your experience of life mirrors the health of your environment. "
                      "Find the right community, and you will flourish.")
    sections.append("")
    sections.append("---")
    sections.append("")
    sections.append("*Generated by the Human Metadata Engine — Full Human Design System*")
    sections.append("")

    return "\n".join(sections)
