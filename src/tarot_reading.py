"""Local authored tarot readings: real shuffled draws, no AI provider.

The draw is intentionally nondeterministic. Realization from its recorded card
IDs and spread is deterministic and separately versioned for replay/export.
"""
from __future__ import annotations

import hashlib
import json
import secrets

from synthesis.reading_library import TAROT
from synthesis.tarot_minor_library import MINOR

VERSION = "tarot-reading-v1"
SPREADS = {
    "focus": {"title": "One-card focus", "description": "One clear theme and a practical reflection.", "positions": [
        ("Focus", "What deserves your attention?", "Name one situation in which this theme could be useful today.")]},
    "situation": {"title": "Situation / Challenge / Guidance", "description": "Explore a situation from three distinct angles.", "positions": [
        ("Situation", "What lens can clarify the situation?", "Describe the situation without assuming the card explains its cause."),
        ("Challenge", "What deserves a closer look?", "Look for a tradeoff or assumption you can examine, rather than an obstacle you are fated to face."),
        ("Guidance", "What response could you explore?", "Choose one reversible action and a sign that would tell you whether it helped.")]},
    "crossroads": {"title": "Five-card crossroads", "description": "Compare two paths without predicting the outcome.", "positions": [
        ("Where you stand", "What matters in this choice?", "Write down the actual choice and the information you already have."),
        ("Path A", "What could you learn by exploring the first path?", "Use this theme to question the first option, not to predict its result."),
        ("Path B", "What could you learn by exploring the second path?", "Apply the same care to the second option; this card does not rank it above or below the first."),
        ("What to consider", "What perspective might be missing?", "Name one question you could ask someone with relevant experience."),
        ("A next step", "What small experiment would make the choice clearer?", "Choose a low-stakes step that gathers information before committing further.")]},
}
SUITS = {
    "Wands": ("initiative and creative effort", "what you want to begin or sustain", "activity without a clear purpose"),
    "Cups": ("feelings and connection", "what makes an exchange meaningful", "assuming an unspoken feeling is understood"),
    "Swords": ("thought and communication", "what needs to be named or examined", "treating an explanation as the whole experience"),
    "Pentacles": ("practice and resources", "what can be supported in everyday life", "measuring value only by visible results"),
}
RANKS = [
    ("Ace", "an opening", "identify a possibility and give it a small first form"),
    ("Two", "a choice or balance", "compare two demands and make the tradeoff explicit"),
    ("Three", "development through exchange", "invite a useful contribution from another perspective"),
    ("Four", "a pause or foundation", "ask what structure supports you and what has become too fixed"),
    ("Five", "disruption", "name what changed and what remains available"),
    ("Six", "adjustment and exchange", "notice what can be restored, shared, or approached differently"),
    ("Seven", "discernment", "choose where your attention belongs instead of answering every demand"),
    ("Eight", "directed movement", "turn a broad intention into a repeatable practice"),
    ("Nine", "the edge of completion", "review what has accumulated and what still needs care"),
    ("Ten", "a full cycle", "decide what to carry forward and what to put down"),
    ("Page", "a learner's perspective", "ask a sincere question before performing expertise"),
    ("Knight", "pursuit", "compare the energy of pursuit with the direction it serves"),
    ("Queen", "attentive stewardship", "create conditions in which this theme can develop"),
    ("King", "responsible direction", "make the purpose and limits of your influence clear"),
]


def _deck() -> tuple[dict, ...]:
    deck = []
    for index, (name, theme, practice, image) in enumerate(TAROT):
        deck.append({"id": f"major-{index:02}", "name": "Death — Transformation" if index == 13 else name,
                     "arcana": "Major", "number": index, "theme": theme, "practice": practice, "image": image})
    for suit, (domain, concern, excess) in SUITS.items():
        for index, (rank, _, _) in enumerate(RANKS, 1):
            theme, practice, image = MINOR[suit][index - 1]
            deck.append({"id": f"{suit.lower()}-{index:02}", "name": f"{rank} of {suit}", "arcana": "Minor",
                         "suit": suit, "number": index, "theme": theme, "practice": practice,
                         "concern": concern, "excess": excess, "image": image})
    return tuple(deck)


DECK = _deck()
BY_ID = {card["id"]: card for card in DECK}


def spread_catalog() -> list[dict]:
    return [{"id": key, "title": spec["title"], "description": spec["description"], "card_count": len(spec["positions"])} for key, spec in SPREADS.items()]


def realize_reading(spread: str, card_ids: list[str]) -> dict:
    if not isinstance(spread, str) or spread not in SPREADS:
        raise ValueError("Choose focus, situation, or crossroads.")
    positions = SPREADS[spread]["positions"]
    if not isinstance(card_ids, list) or len(card_ids) != len(positions) or any(not isinstance(c, str) or c not in BY_ID for c in card_ids) or len(set(card_ids)) != len(card_ids):
        raise ValueError("The recorded draw must contain the spread's exact number of distinct valid cards.")
    cards = []
    for card_id, (position, question, exercise) in zip(card_ids, positions):
        card = dict(BY_ID[card_id])
        paragraphs = [
            f"In the {position.lower()} position, {card['name']} offers {card['theme']} as a lens. {question} Start with what you actually know about the situation, then see whether the image brings a useful detail into focus.",
            f"Picture {card['image']}. The invitation is to {card['practice']}. Describe one moment where that invitation would help and another where a different approach would be wiser.",
        ]
        if card["arcana"] == "Minor":
            paragraphs.append(f"The suit asks about {card['concern']}. A useful counterweight is to watch for {card['excess']}. Read the rank as a stage of reflection, not a level of personal achievement; court cards describe approaches, not a person's age or gender.")
        paragraphs.append(exercise)
        card.update({"position": position, "question": question, "paragraphs": paragraphs, "orientation": "upright"})
        cards.append(card)
    if spread == "focus":
        synthesis = f"Keep this reading centered on {cards[0]['theme']}. Choose one phrase that helps you see a real situation more clearly, and one small action to test it. Revisit your notes after the action rather than drawing repeatedly until a preferred answer appears."
    elif spread == "situation":
        synthesis = f"Read the sequence as three questions: how does {cards[0]['theme']} frame the situation, what does {cards[1]['theme']} ask you to examine, and how could {cards[2]['theme']} inform a response? These are assigned positions in a shuffled spread, not evidence of a causal chain. Let conflicting invitations remain visible."
    else:
        synthesis = f"Begin with {cards[0]['theme']}, then compare Path A through {cards[1]['theme']} and Path B through {cards[2]['theme']}. Neither card is a predicted outcome or a recommendation to choose that path. Bring {cards[3]['theme']} into the comparison and use {cards[4]['theme']} to design a small next step. Write one benefit, one cost, and one unanswered question for each real option."
    canonical = json.dumps([VERSION, spread, card_ids], separators=(",", ":"))
    return {"schema_version": VERSION, "spread": spread, "title": SPREADS[spread]["title"], "cards": cards,
            "reading_id": hashlib.sha256(canonical.encode()).hexdigest()[:24], "synthesis": synthesis,
            "method": "78-card deck; operating-system randomness; sampling without replacement; upright cards only. Interpretation is authored locally and deterministic for the recorded draw.",
            "interpretation": "Project-authored reflective rank/suit and archetype readings, not a reproduction of a traditional divinatory manual.",
            "disclaimer": "A symbolic reflection, not a prediction or a substitute for informed decisions.",
            "ai_used": False}


def draw_reading(payload: dict) -> dict:
    if not isinstance(payload, dict) or set(payload) != {"spread"}:
        raise ValueError("A tarot draw accepts only a spread selection; no personal information is needed.")
    spread = payload["spread"]
    if not isinstance(spread, str) or spread not in SPREADS:
        raise ValueError("Choose focus, situation, or crossroads.")
    ids = secrets.SystemRandom().sample(list(BY_ID), len(SPREADS[spread]["positions"]))
    return realize_reading(spread, ids)
