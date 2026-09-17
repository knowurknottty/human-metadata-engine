"""Deterministic vocabulary banks for evidence-bound Human Manual prose."""
from __future__ import annotations

import hashlib

LEXICON_VERSION = "deterministic-prose-lexicon-v1"

LEXICON_BANKS = {
    "story_openers": (
        "Begin with the pattern as a scene rather than a verdict.",
        "Read this next piece as one lantern among several, not the whole landscape.",
        "Set the calculation beside lived experience and let them question each other.",
        "Imagine the result as a margin note written beside a much larger human story.",
        "Take this symbol as a doorway into a question, not a label pinned to a person.",
        "The next thread is most useful when held lightly enough to be tested.",
        "Let the image arrive before deciding whether it belongs in your account of yourself.",
        "This part of the manual works best as a scene you can compare with memory.",
        "Treat the pattern as a hypothesis with texture, not a conclusion with authority.",
        "Here the calculation becomes narrative only after its boundary is kept visible.",
        "The page offers a lens; your actual experience decides whether it focuses anything.",
        "Start from what was calculated, then allow metaphor to add depth without adding facts.",
    ),
    "story_transitions": (
        "A second way to hold that image is to ask what changes when the setting changes.",
        "The useful turn comes when the symbol meets an ordinary, specific situation.",
        "From there, the story becomes less about naming and more about noticing conditions.",
        "The next movement is not certainty but comparison: where does this fit, and where does it fail?",
        "That theme gains dimension when its opposite is allowed to remain in the room.",
        "Now move from the abstract pattern to the smallest real example you can remember.",
        "The image becomes more honest when a counterexample is invited alongside the example.",
        "What matters next is not intensity of language but whether the description survives contact with detail.",
        "Let the thread continue only as far as observable experience gives it somewhere to go.",
        "The story deepens when the same pattern is viewed from another person's position.",
        "A useful bridge here is context: timing, relationship, task, and stakes can change the expression entirely.",
        "Carry the pattern forward as a question whose answer may differ across seasons of life.",
    ),
    "story_reflections": (
        "Which recent moment gives this image something concrete to describe?",
        "What example supports this reading, and what example makes it less convincing?",
        "Where would this pattern be useful, and where would a different response serve better?",
        "What changed the last time this theme appeared in a real conversation or decision?",
        "Which part feels recognizable because of evidence, and which part merely sounds elegant?",
        "If someone who knows you well disagreed with this passage, what detail might they point to?",
        "What condition seems to bring out the useful side of this pattern most reliably?",
        "Where does the metaphor clarify an experience without pretending to explain all of it?",
        "What would you need to observe before trusting this description more than you do now?",
        "Which ordinary behavior would count as evidence for this reading, and which would count against it?",
        "How does this theme change when the stakes are low enough to experiment safely?",
        "What is the smallest reversible experiment that could tell you whether this lens earns another look?",
    ),
    "story_counterpoints": (
        "Keep the opposite possibility visible; a human pattern can change with context without becoming false.",
        "Do not force the tension to resolve simply because a tidy paragraph would prefer it.",
        "The counterweight matters: a useful strength can become costly when the situation changes.",
        "Another reading may fit the same event, and the disagreement is information rather than a defect.",
        "Hold both poles long enough to notice which one the present situation actually calls for.",
        "A contradiction here is not noise to erase; it may mark the boundary of the comparison.",
        "Leave room for the possibility that neither pole describes the moment particularly well.",
        "The most revealing detail may be the point at which the apparent pattern stops applying.",
        "Let context choose between competing interpretations rather than making one permanent.",
        "The page can preserve ambiguity without asking you to live ambiguously everywhere.",
        "A second lens can challenge the first without invalidating the calculation that produced either symbol.",
        "Keep the disagreement intact until experience gives you a reason to weight one side differently.",
    ),
    "story_closings": (
        "Keep what clarifies; discard what does not; the manual remains yours to annotate.",
        "The symbol has done enough once it helps you ask a better question.",
        "No metaphor needs to survive a counterexample merely because it was beautifully phrased.",
        "The useful ending is not belief, but a more precise observation to carry forward.",
        "Let the passage remain provisional enough to be revised by tomorrow's evidence.",
        "The page closes here, while the actual experiment continues outside it.",
        "Take the question with you; leave the claim behind until experience earns it.",
        "A good reflection should increase your options, not narrow them.",
        "Use the image if it expands attention; retire it if it begins replacing attention.",
        "The calculation stays reproducible even if your interpretation changes completely.",
        "What matters is not whether the sentence sounds like you, but whether it helps you see more accurately.",
        "Nothing in this passage outranks direct knowledge of your own circumstances.",
    ),
    "plain_reflections": (
        "Test that description against one concrete example before generalizing it.",
        "A counterexample is as useful here as a confirming example.",
        "Context may change whether this pattern is useful or misleading.",
        "The next useful step is observation rather than stronger language.",
        "Treat recurrence as a prompt to inspect, not as independent confirmation.",
        "Keep the distinction between a returned symbol and a measured trait visible.",
        "Use a real situation to decide whether the interpretation adds anything.",
        "If the description does not improve a decision or observation, it can be ignored.",
        "The same output can support more than one reasonable interpretation.",
        "Missing or conflicting evidence should remain visible rather than being smoothed over.",
    ),
    "research_bridges": (
        "Read the linked evidence IDs before treating the synthesis as informative.",
        "The interpretation remains downstream of the returned values and their documented limits.",
        "Independence groups matter here because repeated encodings of one input are not separate observations.",
        "The claim is bounded by the exact source paths attached to this sentence.",
        "A stronger interpretation would require evidence beyond the symbolic calculation shown here.",
        "The source record remains authoritative over any rhetorical summary of it.",
        "Contradicting evidence is retained rather than averaged away.",
        "This synthesis is project-authored and does not upgrade a traditional symbol into empirical measurement.",
        "The returned value is reproducible; the meaning assigned to it remains interpretive.",
        "Any missing dimension remains missing and is not inferred from neighboring systems.",
    ),
    "cadence_lines": (
        "Pause on the detail rather than the label.",
        "Let the example do more work than the adjective.",
        "Specificity is more useful here than certainty.",
        "A pattern earns weight through fit, not repetition alone.",
        "The map is allowed to be incomplete.",
        "A useful lens should survive contact with ordinary life.",
        "Not every recurrence deserves a grand interpretation.",
        "The person remains larger than the vocabulary used to describe them.",
        "Precision and wonder do not have to compete.",
        "A good story can stay honest about where its evidence ends.",
    ),
}


def _pick(seed: str, bank: str, salt: str) -> str:
    items = LEXICON_BANKS[bank]
    digest = hashlib.sha256(f"{seed}|{bank}|{salt}".encode()).digest()
    return items[int.from_bytes(digest[:8], "big") % len(items)]


def enrich_synthesis_sentence(base: str, *, seed: str, mode: str, claim_type: str, contradiction: bool) -> str:
    """Add deterministic connective prose without changing the underlying claim."""
    if mode == "mythic":
        pieces = []
        if claim_type in {"descriptive", "agreement"}:
            pieces.append(_pick(seed, "story_openers", claim_type))
        pieces.append(base)
        pieces.append(_pick(seed, "story_transitions", "transition"))
        if contradiction or claim_type in {"tension", "shadow"}:
            pieces.append(_pick(seed, "story_counterpoints", "counterpoint"))
        pieces.append(_pick(seed, "story_reflections", "reflection"))
        pieces.append(_pick(seed, "story_closings", "closing"))
        return " ".join(pieces)
    if mode == "research" and claim_type != "reading":
        return f"{base} {_pick(seed, 'research_bridges', claim_type)}"
    if mode == "plain" and claim_type != "reading":
        return f"{base} {_pick(seed, 'plain_reflections', claim_type)}"
    return base
