"""
Long-Form Identity Report Generator
===================================

Produces the detailed (3,000+ word) ten-section text report that is the
paid deliverable of the Identity Resonance product. Entirely
deterministic template synthesis over the unified signature + analytics
— the same inputs always produce the same report.

Sections:
 1. Executive Summary
 2. Numerological Analysis (Pythagorean, Chaldean, Ordinal, synthesis)
 3. Linguistic Identity
 4. Symbolic Systems (Gematria, Isopsephy)
 5. Celestial Profile (only if birth data)
 6. Psychological Profile (only if supplied)
 7. Graph Position
 8. Cross-Encoder Synthesis
 9. Practical Implications
10. Methodology & Caveats
"""

from __future__ import annotations

try:
    from analytics import composite_resonance, identity_fingerprint, \
        feature_vector, cosine_similarity, DIGIT_FIELDS
except ImportError:  # pragma: no cover - package-style import
    from .analytics import composite_resonance, identity_fingerprint, \
        feature_vector, cosine_similarity, DIGIT_FIELDS

try:
    from snapshot import SIGN_TRAITS, HD_TYPE_TEXT
except ImportError:  # pragma: no cover
    from .snapshot import SIGN_TRAITS, HD_TYPE_TEXT


# =====================================================================
# Interpretation content
# =====================================================================

NUMBER_MEANINGS = {
    1: ("the Initiator", "independence, originality, and the will to begin",
        "leadership that does not wait for permission, an instinct to originate rather than imitate, and the stamina to stand alone when a vision is not yet shared",
        "impatience with slower processes, a tendency to equate asking for help with weakness, and friction with structures that demand conformity"),
    2: ("the Diplomat", "sensitivity, partnership, and the intelligence of nuance",
        "an unusual talent for hearing what is not said, patience with process, and the ability to hold two truths at once without collapsing either",
        "over-accommodation, decision paralysis when both options carry a cost, and absorbing tension that belongs to other people"),
    3: ("the Communicator", "expression, imagination, and social radiance",
        "verbal and creative fluency, an instinct for timing and delivery, and the gift of making complex things feel light",
        "scattering energy across too many openings, performing instead of connecting, and avoiding depths that cannot be joked about"),
    4: ("the Builder", "order, endurance, and the dignity of work",
        "systems thinking, reliability under load, and the rare willingness to do the unglamorous middle of long projects",
        "rigidity when plans change, mistaking control for safety, and undervaluing intuition because it cannot be documented"),
    5: ("the Freedom-Seeker", "change, versatility, and sensory appetite",
        "adaptability that reads new environments in minutes, persuasive energy, and courage at thresholds where others hesitate",
        "restlessness that abandons things at 80 percent, overstimulation, and confusing novelty with progress"),
    6: ("the Guardian", "responsibility, harmony, and the aesthetics of care",
        "a gravitational pull toward stewardship, an eye for beauty and proportion, and loyalty that outlasts convenience",
        "perfectionism aimed at loved ones, martyrdom bookkeeping, and difficulty receiving the care so freely given"),
    7: ("the Analyst", "depth, skepticism, and the search for underlying pattern",
        "penetrating research instinct, comfort with solitude, and immunity to superficial consensus",
        "over-isolation, analysis loops that defer commitment, and a guardedness that reads as distance"),
    8: ("the Executive", "power, material mastery, and consequence",
        "strategic ambition, an instinct for leverage and value, and the capacity to carry decisions that affect many people",
        "measuring worth in outcomes only, control battles, and impatience with those not built for pressure"),
    9: ("the Humanitarian", "completion, compassion, and wide-angle vision",
        "the ability to synthesize many perspectives, generosity of interpretation, and grace in endings",
        "diffuse boundaries, romanticizing potential over reality, and quiet resentment when giving goes unreciprocated"),
    11: ("the Illuminator (master number)", "heightened intuition and nervous-system voltage",
         "visionary perception that arrives whole rather than assembled, and a magnetic effect on collective moods",
         "anxiety when the voltage has no outlet, and oscillation between inspiration and self-doubt"),
    22: ("the Master Builder (master number)", "the capacity to make visions structural",
         "the rare pairing of idealism with engineering patience — dreams that survive contact with budgets",
         "crushing self-expectation and postponement of life until the great work is done"),
    33: ("the Master Teacher (master number)", "compassion raised to a discipline",
         "healing presence and instruction through example rather than argument",
         "self-erasure in service and difficulty tolerating ordinary selfishness"),
}

CHALDEAN_COMPOUND = {
    10: "the Wheel of Fortune — a self-contained cycle; plans rise or fall on the clarity of intention behind them",
    11: "the Clenched Hand — hidden trials and the necessity of choosing courage over comfort",
    12: "the Sacrifice — learning through the suspension of ego; wisdom bought with patience",
    13: "Regeneration — wrongly feared, it signals transformation through upheaval and power over form",
    14: "Movement — combination and risk; fortune through exchange, danger through excess",
    15: "the Magician — eloquence and personal magnetism used to shape circumstances",
    16: "the Shattered Tower — sudden reversals that clear false structures; build on rock, not reputation",
    17: "the Star of the Magi — peace after struggle; a name that tends to be remembered",
    18: "Materialism at war with Spirit — conflict between profit and principle demanding conscious resolution",
    19: "the Prince of Heaven — sunrise energy; victory after difficulty, honor and recognition",
    20: "the Awakening — a call to purpose that makes ordinary ambitions feel small",
    21: "the Crown of the Magi — advancement, honors, and success after long testing",
    22: "the Good Man Under Illusion — talent that must guard against misplaced trust",
    23: "the Royal Star of the Lion — protection and success through the help of superiors",
    24: "assistance from those in power — gains through partnership and love",
    25: "strength gained through observed experience — success arriving in the second half of efforts",
    26: "partnerships requiring caution — power collected through others cuts both ways",
    27: "the Sceptre — authority earned by productive intellect; a commanding compound",
    28: "promising beginnings that must be secured — protect gains from having to be won twice",
    29: "uncertainty and tests of trust — resilience is the actual curriculum",
    30: "thoughtful deduction — a contemplative number that trades worldly noise for mental power",
    31: "self-contained genius — isolation as both strength and cost",
    32: "communicative magic — crowds, movements, and messages; power when instincts are trusted",
    33: "generosity magnified — favor through relationships and creative courage",
    34: "as 25 — strength from experience and late-arriving mastery",
    35: "as 26 — collaborative power requiring vigilant bookkeeping",
    36: "as 27 — earned command and creative authority",
    37: "fortunate friendships and partnership luck in matters of art and heart",
    38: "as 29 — trust as the recurring test",
    39: "as 30 — the thinker's compound",
    40: "as 31 — the hermit-genius compound",
    41: "as 32 — the communicator's compound",
    42: "as 24 — assistance and reciprocity",
    43: "upheaval and radical restructuring — revolutionary energy needing a worthy target",
    44: "as 26 — collected power, shared risk",
    45: "as 27 — productive authority",
    46: "as 28 — secure the win",
    47: "as 29 — resilience curriculum",
    48: "as 30 — contemplative power",
    49: "as 31 — sovereign solitude",
    50: "as 32 — magnetic communication",
    51: "the Warrior's star — sudden advancement in contested fields, with a caution against enemies made carelessly",
    52: "as 25 — experience converted to strength",
}

PHONETIC_NOTES = {
    "plosive": "percussive attack — speech and presence that lands in discrete, decisive beats",
    "fricative": "sustained friction — a texture of continuous pressure, useful for persuasion and urgency",
    "nasal": "resonant hum — warmth and continuity that carries feeling even in plain words",
}

MBTI_FUNCTION_TEXT = {
    "Ni": "introverted intuition (convergent foresight)",
    "Ne": "extraverted intuition (divergent possibility-scanning)",
    "Si": "introverted sensing (embodied precedent and continuity)",
    "Se": "extraverted sensing (real-time environmental contact)",
    "Ti": "introverted thinking (internal logical consistency)",
    "Te": "extraverted thinking (external organization and metrics)",
    "Fi": "introverted feeling (inner value fidelity)",
    "Fe": "extraverted feeling (group atmosphere calibration)",
}

ENNEAGRAM_TEXT = {
    1: "the Reformer — integrity as an engine, with an inner critic that never clocks out",
    2: "the Helper — attunement to need, with the lesson of naming one's own",
    3: "the Achiever — adaptive excellence, with the task of separating worth from performance",
    4: "the Individualist — depth and authenticity, with longing as both muse and trap",
    5: "the Investigator — perceptive economy, with the challenge of staying in the room",
    6: "the Loyalist — vigilant commitment, with courage as the developmental edge",
    7: "the Enthusiast — generative optimism, with depth found by staying past the peak",
    8: "the Challenger — protective intensity, with vulnerability as the hidden strength",
    9: "the Peacemaker — synthetic calm, with self-assertion as the growth direction",
}

LUNAR_TEXT = {
    "New Moon": "instinctive beginnings — comfort operating before outcomes are visible",
    "Waxing Crescent": "emergent determination — energy organized around getting traction",
    "First Quarter": "crisis-of-action energy — decisiveness sharpened by obstacles",
    "Waxing Gibbous": "refinement drive — the urge to perfect what is almost complete",
    "Full Moon": "peak visibility — living in the tension between opposites, publicly",
    "Waning Gibbous": "disseminating wisdom — the teacher's phase, sharing what was learned",
    "Last Quarter": "reorientation — dismantling what no longer serves the trajectory",
    "Waning Crescent": "distillation — closing cycles and conserving essence",
}


def _fold(v: int) -> int:
    while v > 9:
        v = sum(int(c) for c in str(v))
    return v


def _num(sig, enc, field, default=0):
    e = sig.get("encoders", {}).get(enc, {})
    return e.get(field, default) if isinstance(e, dict) else default


def _meaning(n: int) -> tuple[str, str, str, str]:
    return NUMBER_MEANINGS.get(n, NUMBER_MEANINGS.get(_fold(n), NUMBER_MEANINGS[9]))


def _wc(text: str) -> int:
    return len(text.split())


# =====================================================================
# Section builders
# =====================================================================

def _sec1_executive(name, sig, resonance, findings):
    score = resonance["score"]
    if score >= 75:
        band = ("exceptionally high", "the independent symbolic systems converge on this name far more often than chance would suggest")
    elif score >= 60:
        band = ("high", "several independent systems arrive at compatible readings")
    elif score >= 45:
        band = ("moderate", "the systems partially agree, producing a layered rather than singular identity signal")
    else:
        band = ("distributed", "the systems disagree productively — this is a multi-frequency identity rather than a single note")
    top3 = "\n".join(f"{i}. {f}" for i, f in enumerate(findings[:3], 1))
    return f"""## 1. Executive Summary

This report is a full-spectrum symbolic and structural analysis of the identity **"{name}"**, computed across nine independent encoding systems: Pythagorean numerology, Chaldean numerology, ordinal ciphers, quantitative linguistics, binary/prime encoding, Hebrew Gematria, Greek Isopsephy, and — where birth data permits — tropical astrology and Human Design. It is written for the person who carries this name, and for anyone who wants a structured, reproducible portrait of how this specific arrangement of letters (and, if provided, this specific birth moment) behaves under nine very different analytical lenses.

**Composite Resonance Score: {score}/100.** This is a {band[0]} reading: {band[1]}. The score synthesizes four measurable components — numerological convergence ({resonance['components']['numerological_convergence']:.2f}), linguistic harmony ({resonance['components']['linguistic_harmony']:.2f}), polarity balance ({resonance['components']['polarity_balance']:.2f}), and symbolic depth ({resonance['components']['symbolic_depth']:.2f}) — into one comparable number.

**Top findings:**

{top3}

Everything below is deterministic: run the engine again on the same inputs and you will get the same result, character for character.
"""


def _sec2_numerology(name, sig):
    p = sig["encoders"]["pythagorean"]
    c = sig["encoders"]["chaldean"]
    o = sig["encoders"]["ordinal"]
    exp = p["expression"]; su = p["soul_urge"]; pe = p["personality"]
    exp_t, exp_ess, exp_str, exp_shadow = _meaning(exp)
    su_t, su_ess, su_str, su_shadow = _meaning(su)
    pe_t, pe_ess, pe_str, pe_shadow = _meaning(pe)
    cn = c["name_number"]; comp = c["compound_number"]
    cn_t, cn_ess, cn_str, cn_shadow = _meaning(cn)
    comp_text = CHALDEAN_COMPOUND.get(comp,
        f"compound {comp}, which reduces through {_fold(comp)} — read it through the single digit's lens with the added weight of a larger, unrepeated total")
    master_note = ""
    if p.get("master_preserved"):
        m = p["master_preserved"]
        mt, mess, mstr, mshadow = _meaning(m)
        master_note = (f"\n\nCritically, the raw expression total preserves the master number **{m} — {mt}**. "
                       f"Master numbers are not reduced because they signal {mess}: {mstr}. The cost side is real: {mshadow}. "
                       f"A master number is best read as the {_fold(m)} energy under higher voltage — more potential, less stability.")
    agree = "agree" if _fold(exp) == _fold(cn) else "disagree"
    if agree == "agree":
        synth = (f"Here the two systems **agree**: both reduce \"{name}\" to the {_fold(exp)} frequency. When the modern and the ancient "
                 f"mapping — built from entirely different letter-value logics — land on the same digit, numerologists read the name as "
                 f"\"locked in\": the outer instrument and the inner vibration are playing the same note. Practically, it suggests that the way "
                 f"this name performs socially and the way it works on its carrier are aligned, with little internal static.")
    else:
        synth = (f"Here the two systems **disagree**: Pythagorean arithmetic yields {_fold(exp)} while the Chaldean vibration table yields {cn}. "
                 f"This is not a defect — it is information. The Pythagorean {_fold(exp)} describes the name's structural, alphabetical skeleton; "
                 f"the Chaldean {cn} describes its sonic-symbolic surface. A person carrying both frequencies tends to be experienced differently "
                 f"in writing than in person, and can deploy either register deliberately: the {_fold(exp)}'s {_meaning(exp)[1].split(',')[0]} or the {cn}'s {cn_ess.split(',')[0]}.")
    karmic = p.get("karmic_lessons", [])
    karmic_txt = ("no missing digits — every one of the nine numerological classes is represented in the name, which traditional "
                  "numerology reads as an unusually complete toolkit") if not karmic else \
                 (f"missing digit(s) {', '.join(map(str, karmic))} — the so-called karmic lessons, the energies this name does not natively "
                  f"supply and must be developed consciously or borrowed from partners and collaborators")
    hp = p.get("hidden_passion", [])
    hp_txt = ", ".join(map(str, hp)) if hp else "none"
    return f"""## 2. Numerological Analysis

### Pythagorean Reading

The Pythagorean system maps A–Z onto the digits 1–9 in alphabetical order and reads three separate channels from a name. For **"{name}"** the letters total **{p['total']}**, reducing to an **Expression Number of {exp} — {exp_t}**. The expression number is the name's overall operating system: its essence here is {exp_ess}. In its strong form this looks like {exp_str}. Its shadow side, the pattern to watch for under stress, is {exp_shadow}.

The vowels alone — the breath inside the name — total {p['soul_urge_total']}, giving a **Soul Urge of {su} — {su_t}**. The soul urge is what the identity *wants* rather than what it does: {su_ess}. When this channel is fed, you see {su_str}. When starved, {su_shadow}.

The consonants — the name's bone structure, what strangers meet first — total {p['personality_total']}, giving a **Personality Number of {pe} — {pe_t}**. This is the outer surface: {pe_ess}. It presents as {pe_str}; its failure mode is {pe_shadow}.{master_note}

The intensity analysis shows a hidden passion on **{hp_txt}** (the most repeated numerological energy in the name) and {karmic_txt}.

### Chaldean Reading

The Chaldean system is older — Babylonian rather than Greek — and assigns values by sound-vibration rather than alphabetical position, excluding the sacred 9 from its letter table. It produces a **Name Number of {cn} — {cn_t}** ({cn_ess}) and, more importantly, a **Compound Number of {comp}**. Chaldean practice treats the compound as the occult signature behind the visible digit: {comp}, traditionally read as {comp_text}. The compound describes circumstances and karmic weather; the single digit describes the character that meets them.

### Ordinal Structure

Stripped of all symbolism, the raw alphabet arithmetic gives a standard A1Z26 total of **{o['ordinal_total']}** (reducing to {o['ordinal_reduced']}), a reverse-alphabet total of **{o['reverse']}** (reducing to {o['reverse_reduced']}), and a per-letter-reduced total of **{o['reduced_total']}**. The standard and reverse totals always sum to 27 × letter-count; what matters is the *split*. This name sits {'below' if o['ordinal_total'] < o['reverse'] else 'above'} the alphabet's midpoint — its letters cluster toward the {'front (A-M): early-alphabet names read as primary, initiating, label-like' if o['ordinal_total'] < o['reverse'] else 'back (N-Z): late-alphabet names read as accumulated, complex, pressure-bearing'}. The reduced total {o['reduced_total']} → {_fold(o['reduced_total'])} gives a third, independent digit-vote that feeds the convergence analysis below.

### Cross-Numerology Synthesis

Pythagorean and Chaldean are the two great rival systems, so their relationship is the first thing a professional numerologist checks. {synth}
"""


def _sec3_linguistic(name, sig):
    l = sig["encoders"]["linguistic"]
    b = sig["encoders"]["binary_prime"]
    er = l["entropy_ratio"]; vr = l["vowel_ratio"]
    if er >= 0.9:
        etxt = "near-maximal — almost no letter repeats; the name is informationally dense, memorable precisely because it refuses pattern"
    elif er >= 0.75:
        etxt = "high — rich variety with light internal rhyme; the sweet spot where names feel both fresh and pronounceable"
    elif er >= 0.55:
        etxt = "moderate — noticeable repetition gives the name rhythm and stickiness at the cost of surprise"
    else:
        etxt = "low — strong repetition makes the name chant-like: instantly learnable, almost mantric"
    if vr >= 0.5:
        vtxt = "vowel-dominant: open, breath-forward, emotionally legible — a name that sings before it states"
    elif vr >= 0.35:
        vtxt = "balanced: alternating openness and structure, the classic profile of high-trust names"
    else:
        vtxt = "consonant-dominant: armored, percussive, intellect-forward — a name that states before it sings"
    phon = []
    for label, count in (("plosive", l["plosive_count"]), ("fricative", l["fricative_count"]), ("nasal", l["nasal_count"])):
        if count:
            phon.append(f"{count} {label}{'s' if count != 1 else ''} ({PHONETIC_NOTES[label]})")
    phon_txt = "; ".join(phon) if phon else "an unusually soft phonetic profile with no plosives, fricatives, or nasals"
    pol = b["polarity_score"]
    return f"""## 3. Linguistic Identity

Setting symbolism aside entirely, the name **"{name}"** is a measurable signal: {l['letter_count']} letters, {l['unique_letters']} of them unique, estimated at {l['syllable_estimate']} syllable{'s' if l['syllable_estimate'] != 1 else ''}.

**Entropy.** Its Shannon entropy is {l['shannon_entropy']:.3f} bits against a theoretical maximum of {l['max_possible_entropy']:.3f} for its length — an entropy ratio of {er:.2f}. That is {etxt}. Entropy is the honest mathematical answer to "how predictable is this name": high-entropy names cost more attention to learn but are harder to confuse with anything else; low-entropy names trade uniqueness for immediate retention.

**Vowel/consonant polarity.** At a vowel ratio of {vr:.2f}, the name is {vtxt}. In the prime-weighted polarity model, vowel power is {b['vowel_power']} against consonant power {b['consonant_power']} — a net polarity of {pol}, i.e. {'a vowel-tilted (emotionally forward) signature' if pol > 0 else 'a consonant-tilted (structurally forward) signature' if pol < 0 else 'perfect equilibrium between the two channels'}. The vowel/consonant binary string `{b['binary_string']}` has a pattern entropy of {b['binary_entropy']:.2f}/1.00 — {'a highly balanced alternation' if b['binary_entropy'] > 0.9 else 'a moderately patterned alternation' if b['binary_entropy'] > 0.7 else 'a strongly skewed pattern'}.

**Phonetic presence.** The consonant inventory contains {phon_txt}. Together these describe the name's *vocal footprint* — how it physically occupies a room when spoken: the attack, the sustain, and the resonance of its sound envelope.

**What this suggests.** Communication-style research on sound symbolism (the bouba/kiki effect and its descendants) consistently shows listeners infer character from phonology. A name with this profile is heard as {'warm and approachable before a word of content is processed' if vr >= 0.45 else 'precise and consequential before a word of content is processed' if vr < 0.35 else 'both credible and approachable — the phonetic middle path'} — worth knowing, whether to lean into it or deliberately counter-signal.
"""


def _sec4_symbolic(name, sig):
    g = sig["encoders"]["gematria"]
    i = sig["encoders"]["isopsephy"]
    chain = " → ".join(map(str, i["digital_root_chain"]))
    g_red = g["absolute_reduced"]; i_red = i["reduced"]
    gt, gess, _, _ = _meaning(g_red)
    it, iess, _, _ = _meaning(i_red)
    if g_red == i_red:
        cross = (f"The two ancient systems **converge on {g_red}**. Hebrew and Greek letter-values were assigned by different cultures, "
                 f"in different centuries, over different alphabets — when both reduce this name to the same root, the tradition reads it as a "
                 f"name whose meaning survives translation: the same essence ({gess}) appears whether the name is weighed in Jerusalem or Athens.")
    else:
        cross = (f"The two ancient systems diverge: the Hebrew weighing yields {g_red} ({gt}) while the Greek yields {i_red} ({it}). "
                 f"Divergence between the Semitic and Hellenic lenses marks a *bilingual* identity — one that presents different faces to "
                 f"tradition and to philosophy, and can act as a translator between value-systems that do not natively understand each other.")
    return f"""## 4. Symbolic Systems

### Hebrew Gematria

Transliterated into the Hebrew number-alphabet, **"{name}"** carries an absolute (Mispar Hechrachi) value of **{g['absolute_total']}**, an ordinal (Mispar Siduri) value of **{g['ordinal_total']}**, and a reduced (Mispar Katan) value of **{g['reduced_total']}**. In the gematria tradition, the absolute total is the name's full metaphysical weight — the quantity of divine energy the letters carry — while the ordinal total is its worldly rank, and the reduced total its essence when all ornament is stripped. The absolute value reduces to **{g_red} — {gt}**: {gess}. Practitioners would search scripture for words sharing the total {g['absolute_total']}; structurally, what matters here is that this total is *independent* of the Pythagorean arithmetic — Hebrew values jump by tens and hundreds (K=20, R=200), so agreement between the systems is never automatic.

### Greek Isopsephy

The Greek weighing gives a total of **{i['total']}**, and its digital-root cascade — the chain of sums a Greek arithmologist would compute — runs **{chain}**. Each arrow is one act of distillation; a chain of {len(i["digital_root_chain"])} steps means the name {'holds three orders of magnitude of numeric structure before yielding its essence — a deep name in the Pythagorean-mystical sense' if len(i["digital_root_chain"]) >= 3 else 'yields its essence quickly — a transparent name whose surface and depth are close together'}. The terminal root is **{i_red} — {it}**: {iess}. The Greeks used isopsephy comparatively (two words with equal totals were held to share a hidden identity), and philosophically the cascade models emanation: the One unfolding into multiplicity and returning.

### Cross-Symbolic Synthesis

{cross}
"""


def _sec5_celestial(name, sig):
    a = sig["encoders"].get("astrology")
    h = sig["encoders"].get("human_design")
    if not a or a.get("error") or not a.get("sun_sign"):
        return ""
    sun, moon, asc = a["sun_sign"], a["moon_sign"], a["ascendant"]
    sq, sdesc = SIGN_TRAITS.get(sun, ("", ""))
    mq, mdesc = SIGN_TRAITS.get(moon, ("", ""))
    aq, adesc = SIGN_TRAITS.get(asc, ("", ""))
    aspects = a.get("aspects", [])[:5]
    asp_lines = []
    ASPECT_MEANING = {
        "Conjunction": "fusion — the two functions act as one instrument",
        "Sextile": "opportunity — an easy channel that rewards deliberate use",
        "Square": "productive friction — the growth engine of the chart",
        "Trine": "native talent — flow so natural it risks being taken for granted",
        "Opposition": "polarity — a see-saw demanding conscious balance",
    }
    for asp in aspects:
        p1, p2 = asp["planets"]
        asp_lines.append(f"- **{p1} {asp['type']} {p2}** (orb {asp['orb']}°{', exact' if asp.get('exact') else ''}): {ASPECT_MEANING.get(asp['type'], 'a significant angular relationship')}")
    asp_txt = "\n".join(asp_lines) if asp_lines else "- No major aspects within orb."
    lunar = a.get("lunar_phase", "")
    lunar_txt = LUNAR_TEXT.get(lunar, "a distinctive lunar signature")
    hd_txt = ""
    if h and not h.get("error") and h.get("type"):
        role, advice = HD_TYPE_TEXT.get(h["type"], ("a unique type", "follow strategy"))
        channels = h.get("channels", [])
        ch_txt = "; ".join(f"**{c['name']}** (gates {c['gates'][0]}-{c['gates'][1]})" for c in channels[:5]) or "no fully defined channels — a highly open, environment-sampling design"
        profile = h.get("profile", [1, 3])
        PROFILE_LINE = {1: "the Investigator (needs a secure foundation of knowledge)",
                        2: "the Hermit (natural talent that must be called out by others)",
                        3: "the Martyr (learns by trial, error, and collision)",
                        4: "the Opportunist (advances through network and friendship)",
                        5: "the Heretic (projected upon; saves or scapegoated)",
                        6: "the Role Model (three-act life arc toward exemplarhood)"}
        hd_txt = f"""
### Human Design

The Human Design synthesis casts **{name}** as a **{h['type']}** — {role}. Type is the chassis of the design; everything else is trim. The operating **strategy is "{h['strategy']}"** and the inner **authority is {h['authority']}**: decisions are reliable when they {advice}, and the recurring not-self signal — the emotional smoke-alarm indicating strategy has been abandoned — is **{h.get('not_self_theme', 'resistance')}**. The promised signature state, when living correctly by design, is **{h.get('signature', 'flow')}**.

The **{profile[0]}/{profile[1]} profile** combines line {profile[0]} — {PROFILE_LINE.get(profile[0], 'a distinctive learning style')} — with line {profile[1]} — {PROFILE_LINE.get(profile[1], 'a distinctive social role')}. Read together: the conscious personality learns one way while the body's design socializes another, and maturity is learning to run both without apology.

Defined channels: {ch_txt}. Definition type is **{h.get('definition', 'Single')}**, and the incarnation cross — the life's thematic axis — is *{h.get('incarnation_cross', 'undetermined')}*.
"""
    return f"""## 5. Celestial Profile

*Computed with Swiss Ephemeris from the supplied birth data (confidence {a.get('confidence', 0.5)}).*

**Sun in {sun}** ({sq}). The Sun is the chart's engine — the identity's core generative principle. In {sun} it expresses as {sdesc}. This is not mood but *fuel type*: the activities that recharge rather than drain all share this signature.

**Moon in {moon}** ({mq}). The Moon governs the pre-verbal emotional landscape — what safety feels like, what hunger feels like, how the nervous system self-soothes. In {moon}, the inner life runs on {mdesc}. Where the Sun describes what this identity is *for*, the Moon describes what it *needs*, and the distance between {sun} and {moon} agendas is the chart's primary inner dialogue.

**Ascendant in {asc}** ({aq}). The rising sign is the chart's user interface — the involuntary first impression. Others meet {adesc} before they meet anything else. The Ascendant is neither mask nor lie; it is the genuine outermost layer, and its ruler ({a.get('chart_ruler', 'the chart ruler')}) becomes the chart's steering planet.

**Dominant element: {a.get('dominant_element', '—')}; dominant modality: {a.get('dominant_modality', '—')}.** Elemental weighting describes the identity's home medium; modality describes its relationship to change — cardinal initiates, fixed sustains, mutable adapts. This chart's center of gravity is {a.get('dominant_element', '')}-{a.get('dominant_modality', '')}: read every other placement through that climate.

**Key aspects:**

{asp_txt}

**Lunar phase: {lunar}** ({'waxing' if a.get('is_waxing') else 'waning'}). Born under this phase, the identity carries {lunar_txt}.
{hd_txt}"""


def _sec6_psychology(name, sig, psychology):
    if not psychology:
        return ""
    parts = [f"""## 6. Psychological Profile

*This layer is self-reported, not name-derived. It carries the confidence of its assessment method and is the only empirically-grounded section of this report.*
"""]
    b5 = psychology.get("big_five")
    if b5:
        rows = []
        INTERP = {
            "openness": ("conventional, practical, preferring the proven", "curious, aesthetic, drawn to novelty and abstraction"),
            "conscientiousness": ("flexible, spontaneous, deadline-elastic", "organized, reliable, plan-driven"),
            "extraversion": ("energized by solitude and depth", "energized by people and stimulation"),
            "agreeableness": ("skeptical, competitive, comfortable with friction", "cooperative, trusting, harmony-seeking"),
            "neuroticism": ("emotionally stable under load", "emotionally responsive, threat-sensitive"),
        }
        for trait, (low, high) in INTERP.items():
            v = b5.get(trait)
            if v is None:
                continue
            pct = round(v * 100)
            desc = high if v >= 0.5 else low
            strength = "strongly " if (v >= 0.8 or v <= 0.2) else ""
            rows.append(f"- **{trait.capitalize()}: {pct}th percentile** — {strength}{desc}.")
        parts.append("**Big Five (OCEAN):**\n\n" + "\n".join(rows) + "\n")
    mbti = psychology.get("mbti")
    if mbti:
        try:
            try:
                from encoders.psychology import MBTI
            except ImportError:
                from .encoders.psychology import MBTI
            funcs = MBTI.get_cognitive_functions(mbti)
        except Exception:
            funcs = []
        if funcs:
            stack = "\n".join(
                f"{i}. **{f}** — {MBTI_FUNCTION_TEXT.get(f, f)} ({role})"
                for i, (f, role) in enumerate(zip(funcs, ["dominant: the identity's default cognition", "auxiliary: the trusted co-pilot", "tertiary: the developing relief function", "inferior: the aspirational stress point"]), 1))
            parts.append(f"**MBTI: {mbti}.** The cognitive function stack:\n\n{stack}\n\nThe practical read: the dominant-auxiliary pair is where this identity is effortlessly competent; the inferior function is where it is either defensive or, with maturity, most surprisingly creative.\n")
        else:
            parts.append(f"**MBTI: {mbti}.**\n")
    enne = psychology.get("enneagram") or {}
    if enne.get("type"):
        t = enne["type"]
        wing = enne.get("wing")
        wing_txt = f" with a {wing} wing, borrowing {ENNEAGRAM_TEXT.get(wing, 'adjacent flavor').split('—')[0].strip()} as seasoning" if wing else ""
        parts.append(f"**Enneagram: Type {t}{f'w{wing}' if wing else ''}** — {ENNEAGRAM_TEXT.get(t, 'a distinctive core pattern')}{wing_txt}. The Enneagram adds a motivational X-ray the trait models lack: it names the core fear the personality is organized to avoid, which is why type knowledge tends to be uncomfortable before it is useful.\n")
    attach = psychology.get("attachment")
    if attach:
        ATT = {"secure": "a **secure** base: conflict is survivable, closeness is not a threat, and repair comes naturally",
               "anxious": "an **anxious** lean: high relational vigilance — the gift is attunement, the tax is protest behavior under uncertainty",
               "avoidant": "an **avoidant** lean: self-regulation over co-regulation — the gift is composure, the tax is under-asking",
               "disorganized": "a **disorganized** pattern: approach and avoidance both active — integration work pays the highest dividends here",
               "fearful_avoidant": "a **fearful-avoidant** pattern: longing and guarding in the same gesture"}
        parts.append(f"**Attachment style:** {ATT.get(attach, attach)}. In collaboration and partnership, this is the invisible variable that decides how the rest of the profile behaves under relational stress.\n")
    return "\n".join(parts)


def _sec7_graph(name, sig, comparisons):
    if comparisons:
        top = comparisons[:3]
        nbr_lines = "\n".join(
            f"- **{c['text']}** (`{c['id']}`) — cosine similarity {c['similarity']:.2f}: shares {c.get('shared', 'multiple digit-level agreements')}"
            for c in top)
        centrality = ("a well-connected position — its feature vector sits near the population centroid, making it a natural bridge node"
                      if top and top[0]["similarity"] >= 0.9 else
                      "a peripheral position — its nearest neighbor is relatively distant, marking it as an outlier signature in this population")
    else:
        nbr_lines = "- No comparison population supplied."
        centrality = "an unmapped position (no reference population)"
    return f"""## 7. Graph Position

Every identity the engine has processed lives in a shared 14-dimensional feature space (eight reduced digits, entropy ratio, vowel ratio, binary balance, polarity, syllables, root-chain depth). Placing **"{name}"** into that space and measuring cosine similarity against the reference population of pre-analyzed identities yields its *graph position* — where this name sits in the constellation of names.

**Nearest neighbors:**

{nbr_lines}

In network terms, this identity occupies {centrality}. Names that cluster tightly with famous or archetypal identities inherit a useful shorthand ("numerologically adjacent to X"); names in sparse regions are, measurably, rare signatures. Community-detection over the full graph groups identities by convergent digit-votes and linguistic texture rather than by surface spelling — which is why near-neighbors often *look* nothing alike while *behaving* alike under the encoders.
"""


def _sec8_synthesis(name, sig, resonance, fingerprint):
    digits = {}
    for label, (enc, field) in DIGIT_FIELDS.items():
        v = _num(sig, enc, field)
        if isinstance(v, int) and v > 0:
            digits[label] = _fold(v)
    counts = {}
    for d in digits.values():
        counts[d] = counts.get(d, 0) + 1
    if counts:
        mode_digit, mode_n = max(counts.items(), key=lambda kv: kv[1])
    else:
        mode_digit, mode_n = 0, 0
    conv_systems = [k for k, v in digits.items() if v == mode_digit]
    div_systems = [f"{k}→{v}" for k, v in digits.items() if v != mode_digit]
    t, ess, _, _ = _meaning(mode_digit) if mode_digit else ("", "", "", "")
    conv_txt = (f"**{mode_n} of {len(digits)} digit-producing systems converge on {mode_digit} ({t})** — {', '.join(conv_systems)} all "
                f"reduce this name to the same root despite using unrelated letter-value tables. The shared theme: {ess}."
                if mode_n >= 2 else
                "**No two digit-producing systems agree** — all five arrive at different roots. This is the rarest configuration: a "
                "prismatic identity that refracts differently under every lens, resisting any single-number summary.")
    div_txt = (f" The dissenting systems ({', '.join(div_systems)}) are not noise: each divergence marks a register in which the name "
               f"behaves differently — a reminder that identity is measured, not possessed." if div_systems and mode_n >= 2 else "")
    return f"""## 8. Cross-Encoder Synthesis

The deepest question this engine can ask is: *where do nine unrelated systems agree?*

{conv_txt}{div_txt}

The composite resonance score of **{resonance['score']}/100** quantifies exactly this: convergence weighted at 35%, linguistic harmony at 25%, structural polarity balance at 20%, and symbolic depth at 20%. Component values — convergence {resonance['components']['numerological_convergence']:.2f}, harmony {resonance['components']['linguistic_harmony']:.2f}, balance {resonance['components']['polarity_balance']:.2f}, depth {resonance['components']['symbolic_depth']:.2f} — show precisely which channels carry this identity's signal.

**The identity fingerprint** distills all of it into a single reproducible glyph: hash `{fingerprint['hash']}`, rendered as a {fingerprint['symmetry']}-fold rotationally symmetric figure (symmetry order = the expression number) whose nine spokes are the nine encoders — each spoke's length its normalized magnitude, each hue its system's color — ringed by the name's own vowel/consonant binary pattern `{fingerprint['ring_pattern']}`. No two names produce the same figure unless they are numerologically identical; the fingerprint is the visual proof-of-analysis, a barcode of the whole report.
"""


def _sec9_practical(name, sig, resonance):
    l = sig["encoders"]["linguistic"]
    p = sig["encoders"]["pythagorean"]
    vr = l["vowel_ratio"]
    exp = p["expression"]
    _, _, strengths, shadow = _meaning(exp)
    comm = ("Lead with warmth and let structure follow — this name's phonetics already sound approachable, so credibility is the thing to establish deliberately."
            if vr >= 0.45 else
            "Lead with structure and let warmth follow — this name's phonetics already sound authoritative, so approachability is the thing to establish deliberately."
            if vr < 0.35 else
            "The name's phonetics are balanced — match register to context freely; neither warmth nor authority needs compensating.")
    return f"""## 9. Practical Implications

**Communication style.** {comm} With an expression energy of {exp}, the natural communication strengths are {strengths}.

**Strengths to lean on.** The convergent themes of this analysis point to reliable capacities — the qualities multiple systems agree on are the ones to build strategy around rather than treat as accidents.

**Blind spots to budget for.** Every number's shadow is the strength overdrawn: for this identity, watch for {shadow}. The linguistic profile adds its own caution: {'a highly distinctive name is memorable but effortful — expect misspellings and use them as a filter, not an insult' if l['entropy_ratio'] > 0.85 else 'a smooth, patterned name is easy to remember but also easy to gloss over — distinctiveness must come from content'}.

**How others likely perceive this identity.** First contact is phonetic (the {['consonant-armored', 'balanced', 'vowel-open'][0 if vr < 0.35 else 1 if vr < 0.45 else 2]} sound envelope), second contact is the personality number's surface, and only sustained contact reveals the soul urge. The practical move: make sure the channels agree — when name-sound, presented surface, and actual motivation align, others experience congruence, and congruence is trust.
"""


def _sec10_methodology():
    return """## 10. Methodology & Caveats

**How the encoders work.** Pythagorean numerology maps A–Z to 1–9 cyclically and reads totals over the whole name, its vowels, and its consonants. Chaldean numerology uses the older Babylonian sound-value table (no letter maps to 9) and preserves the unreduced compound number. The ordinal ciphers are raw alphabet arithmetic (A1Z26, its reverse, and per-letter digital roots). The linguistic encoder computes Shannon entropy, syllable estimates, phoneme-class counts, and vowel/consonant statistics — measurable properties only. The binary/prime encoder writes the name as a vowel/consonant bit-string and weighs letters by primes (A=2 … Z=101). Gematria and Isopsephy transliterate into the Hebrew and Greek number-alphabets and reduce. Astrology uses the Swiss Ephemeris for tropical positions, houses, aspects, and lunar phase. Human Design combines birth and 88-days-prior ephemeris positions into gates, channels, type, and profile. The psychology layer is entirely user-supplied assessment data.

**What this analysis IS:** a reproducible, deterministic computation over a name (and optional birth data) through nine formal symbolic systems, plus honest measurements of the name as a signal. Run it twice, get the identical result. It is a structured mirror — useful for reflection, naming decisions, brand work, and pattern exploration.

**What this analysis IS NOT:** empirical psychology, prediction, or medical/financial/legal guidance. The symbolic systems (numerology, gematria, astrology, Human Design) are interpretive traditions, not validated instruments; their claims should be held as *lenses*, not facts. Only the linguistic measurements and any self-reported psychology carry empirical weight, and self-report has well-known limits.

**Limitations.** Transliteration into Hebrew and Greek involves convention choices; birth-time uncertainty degrades astrological precision (confidence is reported); the Human Design implementation is a simplified model of the full bodygraph; and all interpretive text is generated from fixed scholarly-tradition templates. Appropriate use: curiosity, self-reflection, and creative decision support — never gatekeeping, hiring, or judgments about other people.

---

*Generated by the Human Metadata Engine. Deterministic build — identical inputs always yield identical output.*
"""


# =====================================================================
# Public API
# =====================================================================

def generate_report(sig: dict,
                    psychology: dict | None = None,
                    comparisons: list[dict] | None = None) -> dict:
    """Generate the full ten-section report for a unified signature.

    comparisons: optional list of {"id","text","similarity"} against the
    reference population (already ranked descending).
    Returns {"markdown": str, "word_count": int, "sections": [names]}.
    """
    name = sig.get("text", "Unknown")
    resonance = sig.get("resonance") or composite_resonance(sig)
    fingerprint = sig.get("fingerprint") or identity_fingerprint(sig)

    p = sig["encoders"]["pythagorean"]
    findings = []
    digits = []
    for enc, field in DIGIT_FIELDS.values():
        v = _num(sig, enc, field)
        if isinstance(v, int) and v > 0:
            digits.append(_fold(v))
    counts = {}
    for d in digits:
        counts[d] = counts.get(d, 0) + 1
    if counts:
        md, mn = max(counts.items(), key=lambda kv: kv[1])
        if mn >= 3:
            findings.append(f"Strong cross-system convergence: {mn} of {len(digits)} independent systems reduce this name to {md} ({_meaning(md)[0]}).")
        elif mn == 2:
            findings.append(f"Partial convergence: two systems agree on the root {md} ({_meaning(md)[0]}), the rest diverge — a layered signature.")
        else:
            findings.append("A prismatic signature: all five digit systems disagree, which is the rarest configuration in the reference population.")
    if p.get("master_preserved"):
        findings.append(f"The name carries master number {p['master_preserved']} — high-voltage potential that most names do not have.")
    l = sig["encoders"]["linguistic"]
    findings.append(f"Linguistically, the name runs at {l['entropy_ratio']:.0%} of maximum entropy with a {l['vowel_ratio']:.0%} vowel share — "
                    + ("a distinctive, high-information signal." if l['entropy_ratio'] > 0.8 else "a rhythmic, pattern-forward signal."))
    astro = sig["encoders"].get("astrology")
    if astro and not astro.get("error") and astro.get("sun_sign"):
        findings.append(f"Birth data unlocked the celestial layer: {astro['sun_sign']} Sun, {astro['moon_sign']} Moon, {astro['ascendant']} rising, dominant element {astro.get('dominant_element')}.")

    sections = [
        _sec1_executive(name, sig, resonance, findings),
        _sec2_numerology(name, sig),
        _sec3_linguistic(name, sig),
        _sec4_symbolic(name, sig),
        _sec5_celestial(name, sig),
        _sec6_psychology(name, sig, psychology),
        _sec7_graph(name, sig, comparisons),
        _sec8_synthesis(name, sig, resonance, fingerprint),
        _sec9_practical(name, sig, resonance),
        _sec10_methodology(),
    ]
    body = "\n".join(s for s in sections if s)
    header = f"# Identity Resonance Report — {name}\n\n"
    markdown = header + body
    return {
        "markdown": markdown,
        "word_count": _wc(markdown),
        "sections": [i + 1 for i, s in enumerate(sections) if s],
    }
