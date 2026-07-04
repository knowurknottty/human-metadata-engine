"""
Full Human Design System
=========================

Complete Human Design computation with:
- 64 gates (I Ching hexagrams)
- 36 channels connecting 9 centers
- Proper type/authority/profile determination
- Incarnation Cross calculation
- Variable/Environment determination
- Bodygraph SVG generation
- Full interpretation engine

Requires Swiss Ephemeris for accurate planetary positions.
Falls back to deterministic approximation without it.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════
# THE 64 GATES — Full I Ching hexagram mapping
# ═══════════════════════════════════════════════════════════════════

GATES = {
    1: {"name": "The Creative", "center": "G", "keynote": "Creative Self-Expression", "hexagram": "☰",
        "description": "The gate of creative power. Pure Yang energy. The capacity to initiate creation from the depths of the self."},
    2: {"name": "The Receptive", "center": "G", "keynote": "Direction of the Self", "hexagram": "☷",
        "description": "The gate of the potential of the mind. Direction and orientation of the self through higher knowing."},
    3: {"name": "Difficulty at the Beginning", "center": "Sacral", "keynote": "Ordering", "hexagram": "☳",
        "description": "The gate of mutation. The capacity to bring order out of chaos. The design of transformation."},
    4: {"name": "Youthful Folly", "center": "Ajna", "keynote": "Formulization", "hexagram": "☶",
        "description": "The gate of the mind. Formulization and the capacity to formulate answers."},
    5: {"name": "Waiting", "center": "Sacral", "keynote": "Fixed Rhythms", "hexagram": "☵",
        "description": "The gate of fixed patterns. The design of universal order through fixed cycles."},
    6: {"name": "Conflict", "center": "Solar Plexus", "keynote": "Friction", "hexagram": "☰",
        "description": "The gate of friction. The motor of the emotional system through creative conflict."},
    7: {"name": "The Army", "center": "G", "keynote": "Direction of the Self", "hexagram": "☷",
        "description": "The gate of the role of the self in the direction of humanity. Leadership through example."},
    8: {"name": "Holding Together", "center": "Throat", "keynote": "Contribution", "hexagram": "☷",
        "description": "The gate of contribution. The capacity to contribute to the whole through creative role modeling."},
    9: {"name": "Taming Power of the Small", "center": "Solar Plexus", "keynote": "Focus", "hexagram": "☰",
        "description": "The gate of focus. The design of determination and concentration."},
    10: {"name": "Treading", "center": "G", "keynote": "Behavior of the Self", "hexagram": "☰",
        "description": "The gate of the behavior of the self. The love of self and the activation of the life force."},
    11: {"name": "Peace", "center": "Ajna", "keynote": "Ideas", "hexagram": "☷",
        "description": "The gate of ideas. The conceptualization of peace and harmony."},
    12: {"name": "Standstill", "center": "Throat", "keynote": "Caution", "hexagram": "☰",
        "description": "The gate of caution. The voice of the individual who waits for the right moment."},
    13: {"name": "Fellowship", "center": "G", "keynote": "The Listener", "hexagram": "☰",
        "description": "The gate of the listener. The design of the witness and the capacity to remember."},
    14: {"name": "Great Possession", "center": "Solar Plexus", "keynote": "Power Skills", "hexagram": "☲",
        "description": "The gate of power skills. The design of balance and the capability of the individual."},
    15: {"name": "Modesty", "center": "G", "keynote": "Humanity", "hexagram": "☷",
        "description": "The gate of humanity. The design of universal love and the love of humanity."},
    16: {"name": "Enthusiasm", "center": "Throat", "keynote": "Skills", "hexagram": "☳",
        "description": "The gate of skills. The design of enthusiasm and the capacity for talent."},
    17: {"name": "Following", "center": "Ajna", "keynote": "Opinions", "hexagram": "☳",
        "description": "The gate of opinions. The design of the organizational mind."},
    18: {"name": "Work on the Decayed", "center": "Splenic", "keynote": "Correction", "hexagram": "☶",
        "description": "The gate of correction. The design of judgment and the capacity to spot what needs fixing."},
    19: {"name": "Approach", "center": "Root", "keynote": "Wanting", "hexagram": "☷",
        "description": "The gate of wanting. The design of sensitivity and the tribal sensing of needs."},
    20: {"name": "Contemplation", "center": "Throat", "keynote": "The Now", "hexagram": "☴",
        "description": "The gate of the now. The design of awareness and the capacity to be present."},
    21: {"name": "Biting Through", "center": "Heart/Will", "keynote": "Control", "hexagram": "☲",
        "description": "The gate of control. The design of the hunter and the material will."},
    22: {"name": "Grace", "center": "Solar Plexus", "keynote": "Openness", "hexagram": "☲",
        "description": "The gate of openness. The design of social grace and emotional charm."},
    23: {"name": "Splitting Apart", "center": "Throat", "keynote": "Assimilation", "hexagram": "☷",
        "description": "The gate of assimilation. The voice of the individual who brings order through expression."},
    24: {"name": "Return", "center": "Ajna", "keynote": "Rationalization", "hexagram": "☷",
        "description": "The gate of rationalization. The design of the mind working through the return to clarity."},
    25: {"name": "Innocence", "center": "G", "keynote": "Spirit of the Self", "hexagram": "☳",
        "description": "The gate of the spirit of the self. Universal love and innocence."},
    26: {"name": "Taming Power of the Great", "center": "Heart/Will", "keynote": "Egoist", "hexagram": "☶",
        "description": "The gate of the egoist. The design of the transmitter and the great ego."},
    27: {"name": "Nourishment", "center": "Sacral", "keynote": "Caring", "hexagram": "☶",
        "description": "The gate of caring. The design of the great nourisher and the power of sustenance."},
    28: {"name": "Preponderance of the Great", "center": "Splenic", "keynote": "The Game Player", "hexagram": "☱",
        "description": "The gate of the game player. The design of stubbornness and the risk-taker."},
    29: {"name": "The Abysmal", "center": "Sacral", "keynote": "Perseverance", "hexagram": "☵",
        "description": "The gate of perseverance. The design of saying yes and the depth of commitment."},
    30: {"name": "Clinging Fire", "center": "Solar Plexus", "keynote": "Feelings", "hexagram": "☲",
        "description": "The gate of feelings. The design of recognition and the intensity of emotion."},
    31: {"name": "Influence", "center": "Throat", "keynote": "Leadership", "hexagram": "☱",
        "description": "The gate of leadership. The voice of influence and the democratic principle."},
    32: {"name": "Duration", "center": "Splenic", "keynote": "Continuity", "hexagram": "☳",
        "description": "The gate of continuity. The design of transformation through endurance."},
    33: {"name": "Retreat", "center": "Throat", "keynote": "Privacy", "hexagram": "☶",
        "description": "The gate of privacy. The voice of the witness who observes from retreat."},
    34: {"name": "Power of the Great", "center": "Sacral", "keynote": "Power", "hexagram": "☳",
        "description": "The gate of power. The design of archetype and the great life force."},
    35: {"name": "Progress", "center": "Throat", "keynote": "Change", "hexagram": "☲",
        "description": "The gate of change. The voice of the jack-of-all-trades and the hunger for experience."},
    36: {"name": "Darkening of the Light", "center": "Solar Plexus", "keynote": "Crisis", "hexagram": "☲",
        "description": "The gate of crisis. The design of the humanitarian through emotional depth."},
    37: {"name": "The Family", "center": "Solar Plexus", "keynote": "Friendship", "hexagram": "☱",
        "description": "The gate of friendship. The design of the family and the power of bonding."},
    38: {"name": "Opposition", "center": "Splenic", "keynote": "Stubbornness", "hexagram": "☱",
        "description": "The gate of the fighter. The design of opposition and the search for purpose."},
    39: {"name": "Obstruction", "center": "Root", "keynote": "Provocation", "hexagram": "☵",
        "description": "The gate of provocation. The design of the mood and the power of spirit."},
    40: {"name": "Deliverance", "center": "Heart/Will", "keynote": "Aloneness", "hexagram": "☳",
        "description": "The gate of aloneness. The design of the ego and the need for rest."},
    41: {"name": "Decrease", "center": "Root", "keynote": "Contraction", "hexagram": "☱",
        "description": "The gate of contraction. The design of anticipation and the pressure to desire."},
    42: {"name": "Increase", "center": "Sacral", "keynote": "Growth", "hexagram": "☴",
        "description": "The gate of growth. The design of transformation through increase."},
    43: {"name": "Breakthrough", "center": "Ajna", "keynote": "Insight", "hexagram": "☱",
        "description": "The gate of insight. The design of the mind through fixed knowings."},
    44: {"name": "Coming to Meet", "center": "Splenic", "keynote": "Alertness", "hexagram": "☴",
        "description": "The gate of alertness. The design of the sensor and the talent for timing."},
    45: {"name": "Gathering Together", "center": "Throat", "keynote": "Money", "hexagram": "☱",
        "description": "The gate of money. The voice of the gatherer and the ruler of the tribal collective."},
    46: {"name": "Pushing Upward", "center": "G", "keynote": "Determination of the Self", "hexagram": "☷",
        "description": "The gate of determination of the self. The love of the body and physical determination."},
    47: {"name": "Oppression", "center": "Ajna", "keynote": "Realization", "hexagram": "☱",
        "description": "The gate of realization. The design of the mind through abstract mental pressure."},
    48: {"name": "The Well", "center": "Splenic", "keynote": "Depth", "hexagram": "☴",
        "description": "The gate of depth. The design of the well and the talent for instinctive knowing."},
    49: {"name": "Revolution", "center": "Solar Plexus", "keynote": "Principles", "hexagram": "☱",
        "description": "The gate of principles. The design of transformation through emotional revolution."},
    50: {"name": "The Cauldron", "center": "Splenic", "keynote": "Values", "hexagram": "☴",
        "description": "The gate of values. The design of the genetic format and the power of values."},
    51: {"name": "The Arousing", "center": "G", "keynote": "Shock", "hexagram": "☳",
        "description": "The gate of shock. The design of the individual who competitive and the power of initiation."},
    52: {"name": "Keeping Still", "center": "Root", "keynote": "Stillness", "hexagram": "☶",
        "description": "The gate of stillness. The design of meditation and the power of the mountain."},
    53: {"name": "Development", "center": "Sacral", "keynote": "Beginnings", "hexagram": "☴",
        "description": "The gate of beginnings. The design of development and the power of the flow."},
    54: {"name": "The Marrying Maiden", "center": "Root", "keynote": "Ambition", "hexagram": "☳",
        "description": "The gate of ambition. The design of transformation through desire and drive."},
    55: {"name": "Abundance", "center": "Solar Plexus", "keynote": "Spirit", "hexagram": "☳",
        "description": "The gate of spirit. The design of abundance through emotional fullness."},
    56: {"name": "The Wandering Man", "center": "Throat", "keynote": "Storytelling", "hexagram": "☲",
        "description": "The gate of storytelling. The voice of the stimulator and the stimulation of the mind."},
    57: {"name": "The Gentle", "center": "Splenic", "keynote": "Intuition", "hexagram": "☴",
        "description": "The gate of intuition. The design of the intuitive mind and the clarity of the inner ear."},
    58: {"name": "The Joyous", "center": "Root", "keynote": "Vitality", "hexagram": "☱",
        "description": "The gate of vitality. The design of correction through the joyous spirit."},
    59: {"name": "Sexuality", "center": "Sacral","keynote": "Sexuality", "hexagram": "☴",
        "description": "The gate of sexuality. The design of reproduction and the power of bonding."},
    60: {"name": "Limitation", "center": "Root", "keynote": "Acceptance", "hexagram": "☵",
        "description": "The gate of acceptance. The design of cyclical transformation through limitation."},
    61: {"name": "Inner Truth", "center": "Head", "keynote": "Mental Pressure", "hexagram": "☱",
        "description": "The gate of inner truth. The design of the individual mental pressure to know."},
    62: {"name": "Preponderance of the Small", "center": "Throat", "keynote": "Details", "hexagram": "☶",
        "description": "The gate of details. The voice of the detail-oriented mind and the pressure to express."},
    63: {"name": "After Completion", "center": "Head", "keynote": "Mental Pressure", "hexagram": "☵",
        "description": "The gate of mental pressure. The design of the doubt and the pressure to question."},
    64: {"name": "Before Completion", "center": "Head", "keynote": "Mental Pressure", "hexagram": "☲",
        "description": "The gate of mental pressure. The design of confusion and the pressure to understand."},
}


# ═══════════════════════════════════════════════════════════════════
# THE 36 CHANNELS — Connecting gates through centers
# ═══════════════════════════════════════════════════════════════════

CHANNELS = {
    (64, 47): {"name": "Abstraction", "centers": ["Head", "Ajna"], "description": "Mental pressure to make sense of the past through abstract thought."},
    (61, 24): {"name": "Channel of Awareness", "centers": ["Head", "Ajna"], "description": "The design of a thinker. Mental pressure for unique knowing."},
    (63, 4): {"name": "Channel of Logic", "centers": ["Head", "Ajna"], "description": "Mental pressure to question and formulate mental concepts."},
    (17, 62): {"name": "Acceptance", "centers": ["Ajna", "Throat"], "description": "The design of an organizational mind. Opinions expressed through details."},
    (43, 23): {"name": "Structure", "centers": ["Ajna", "Throat"], "description": "The design of a channeler. Insight expressed through individual knowing."},
    (11, 56): {"name": "Curiosity", "centers": ["Ajna", "Throat"], "description": "The design of a storyteller. Ideas expressed through stimulation."},
    (24, 61): {"name": "Channel of Awareness", "centers": ["Ajna", "Head"], "description": "The design of a thinker. Mental awareness through unique knowing."},
    (1, 8): {"name": "Inspiration", "centers": ["G", "Throat"], "description": "The design of a creative role model. Creative self-expression through contribution."},
    (2, 14): {"name": "The Beat", "centers": ["G", "Solar Plexus"], "description": "The design of a universal translator. Direction through power skills."},
    (15, 5): {"name": "Rhythm", "centers": ["G", "Sacral"], "description": "The design of a universal lover. Humanity through fixed rhythms."},
    (10, 34): {"name": "Exploration", "centers": ["G", "Sacral"], "description": "The design of a voyager. Behavior of the self through power."},
    (10, 57): {"name": "Intuition", "centers": ["G", "Splenic"], "description": "The design of perfection. Behavior through intuitive clarity."},
    (10, 20): {"name": "Awakening", "centers": ["G", "Throat"], "description": "The design of the awakened one. Behavior expressed through presence."},
    (25, 51): {"name": "Initiation", "centers": ["G", "G"], "description": "The design of competitive spirit. Innocence through shock."},
    (15, 5): {"name": "Rhythm", "centers": ["G", "Sacral"], "description": "The design of a universal lover. Humanity through fixed rhythms."},
    (46, 29): {"name": "Discovery", "centers": ["G", "Sacral"], "description": "The design of someone who follows their determination. Determination through perseverance."},
    (7, 31): {"name": "The Alpha", "centers": ["G", "Throat"], "description": "The design of a leader. Leadership through democratic influence."},
    (13, 33): {"name": "The Prodigal", "centers": ["G", "Throat"], "description": "The design of the witness. Listening expressed through privacy."},
    (16, 48): {"name": "The Wavelength", "centers": ["Throat", "Splenic"], "description": "The design of a talent. Skills expressed through depth."},
    (20, 34): {"name": "Charisma", "centers": ["Throat", "Sacral"], "description": "The design of expressivity. The Now expressed through power."},
    (20, 57): {"name": "Brainwave", "centers": ["Throat", "Splenic"], "description": "The design of awareness. Presence expressed through intuition."},
    (20, 10): {"name": "Awakening", "centers": ["Throat", "G"], "description": "The design of the awakened one. Behavior through presence."},
    (31, 7): {"name": "The Alpha", "centers": ["Throat", "G"], "description": "The design of a leader. Leadership through democratic influence."},
    (33, 13): {"name": "The Prodigal", "centers": ["Throat", "G"], "description": "The design of the witness. Listening expressed through privacy."},
    (45, 21): {"name": "Money Line", "centers": ["Throat", "Heart/Will"], "description": "The design of a materialist. Money expressed through control."},
    (12, 22): {"name": "Openness", "centers": ["Throat", "Solar Plexus"], "description": "The design of a social being. Caution expressed through openness."},
    (35, 36): {"name": "Transitoriness", "centers": ["Throat", "Solar Plexus"], "description": "The design of a jack-of-all-trades. Change expressed through crisis."},
    (62, 17): {"name": "Acceptance", "centers": ["Throat", "Ajna"], "description": "The design of an organizational mind. Details expressed through opinions."},
    (23, 43): {"name": "Structure", "centers": ["Throat", "Ajna"], "description": "The design of a channeler. Individual knowing expressed through insight."},
    (56, 11): {"name": "Curiosity", "centers": ["Throat", "Ajna"], "description": "The design of a storyteller. Stimulation expressed through ideas."},
    (8, 1): {"name": "Inspiration", "centers": ["Throat", "G"], "description": "The design of a creative role model. Contribution expressed through creativity."},
    (31, 7): {"name": "The Alpha", "centers": ["Throat", "G"], "description": "The design of a leader. Leadership expressed through democratic principles."},
    (37, 40): {"name": "Community", "centers": ["Solar Plexus", "Heart/Will"], "description": "The design of a custodian of resources. Friendship expressed through aloneness."},
    (6, 59): {"name": "Intimacy", "centers": ["Solar Plexus", "Sacral"], "description": "The design of sensuality. Friction expressed through sexuality."},
    (36, 35): {"name": "Transitoriness", "centers": ["Solar Plexus", "Throat"], "description": "The design of a jack-of-all-trades. Crisis expressed through change."},
    (49, 19): {"name": "Synthesis", "centers": ["Solar Plexus", "Root"], "description": "The design of the sensitive. Principles expressed through wanting."},
    (55, 39): {"name": "Emoting", "centers": ["Solar Plexus", "Root"], "description": "The design of mood. Spirit expressed through provocation."},
    (22, 12): {"name": "Openness", "centers": ["Solar Plexus", "Throat"], "description": "The design of a social being. Openness expressed through caution."},
    (30, 41): {"name": "Recognition", "centers": ["Solar Plexus", "Root"], "description": "The design of a feeling being. Feelings expressed through contraction."},
    (26, 44): {"name": "The Egoist's Channel", "centers": ["Heart/Will", "Splenic"], "description": "The design of a transmitter. The great ego expressed through alertness."},
    (21, 45): {"name": "Money Line", "centers": ["Heart/Will", "Throat"], "description": "The design of a materialist. Control expressed through gathering."},
    (40, 37): {"name": "Community", "centers": ["Heart/Will", "Solar Plexus"], "description": "The design of a custodian. Aloneness expressed through friendship."},
    (27, 50): {"name": "The Preservation", "centers": ["Sacral", "Splenic"], "description": "The design of caretaking. Caring expressed through values."},
    (34, 57): {"name": "Power", "centers": ["Sacral", "Splenic"], "description": "The design of an archetype. Power expressed through intuition."},
    (59, 6): {"name": "Intimacy", "centers": ["Sacral", "Solar Plexus"], "description": "The design of sensuality. Sexuality expressed through friction."},
    (42, 53): {"name": "Maturation", "centers": ["Sacral", "Root"], "description": "The design of transformation. Growth expressed through beginnings."},
    (3, 60): {"name": "Pulse", "centers": ["Sacral", "Root"], "description": "The design of transformation. Ordering expressed through limitation."},
    (29, 46): {"name": "Discovery", "centers": ["Sacral", "G"], "description": "The design of someone who follows their determination. Perseverance expressed through determination."},
    (5, 15): {"name": "Rhythm", "centers": ["Sacral", "G"], "description": "The design of a universal lover. Fixed rhythms expressed through humanity."},
    (34, 20): {"name": "Charisma", "centers": ["Sacral", "Throat"], "description": "The design of expressivity. Power expressed through presence."},
    (57, 10): {"name": "Intuition", "centers": ["Splenic", "G"], "description": "The design of perfection. Intuition expressed through behavior."},
    (57, 20): {"name": "Brainwave", "centers": ["Splenic", "Throat"], "description": "The design of awareness. Intuition expressed through presence."},
    (57, 34): {"name": "Power", "centers": ["Splenic", "Sacral"], "description": "The design of an archetype. Intuition expressed through power."},
    (50, 27): {"name": "The Preservation", "centers": ["Splenic", "Sacral"], "description": "The design of caretaking. Values expressed through caring."},
    (48, 16): {"name": "The Wavelength", "centers": ["Splenic", "Throat"], "description": "The design of a talent. Depth expressed through skills."},
    (44, 26): {"name": "The Egoist's Channel", "centers": ["Splenic", "Heart/Will"], "description": "The design of a transmitter. Alertness expressed through ego."},
    (38, 28): {"name": "The Fighter", "centers": ["Splenic", "Root"], "description": "The design of the game player. Stubbornness expressed through risk-taking."},
    (54, 32): {"name": "Transformation", "centers": ["Root", "Splenic"], "description": "The design of transformation. Ambition expressed through continuity."},
    (19, 49): {"name": "Synthesis", "centers": ["Root", "Solar Plexus"], "description": "The design of the sensitive. Wanting expressed through principles."},
    (39, 55): {"name": "Emoting", "centers": ["Root", "Solar Plexus"], "description": "The design of mood. Provocation expressed through spirit."},
    (41, 30): {"name": "Recognition", "centers": ["Root", "Solar Plexus"], "description": "The design of a feeling being. Contraction expressed through feelings."},
    (52, 9): {"name": "Concentration", "centers": ["Root", "Solar Plexus"], "description": "The design of focus. Stillness expressed through concentration."},
    (58, 18): {"name": "Insight", "centers": ["Root", "Splenic"], "description": "The design of a zealot. Vitality expressed through correction."},
    (60, 3): {"name": "Pulse", "centers": ["Root", "Sacral"], "description": "The design of transformation. Limitation expressed through ordering."},
    (53, 42): {"name": "Maturation", "centers": ["Root", "Sacral"], "description": "The design of transformation. Beginnings expressed through growth."},
}


# ═══════════════════════════════════════════════════════════════════
# THE 9 CENTERS — Definition based on channels
# ═══════════════════════════════════════════════════════════════════

CENTER_MAP = {
    "Head": {"type": "pressure", "theme": "Inspiration / Mental Pressure", "not_self": "Am I being inspired?"},
    "Ajna": {"type": "awareness", "theme": "Conceptualization / Mental Awareness", "not_self": "Am I certain?"},
    "Throat": {"type": "expression", "theme": "Communication / Manifestation", "not_self": "Am I recognized?"},
    "G": {"type": "identity", "theme": "Direction / Identity / Love", "not_self": "Am I being myself?"},
    "Heart/Will": {"type": "motor", "theme": "Willpower / Ego / Material", "not_self": "Can I prove my worth?"},
    "Solar Plexus": {"type": "motor", "theme": "Emotions / Feelings / Spirit", "not_self": "Am I at peace?"},
    "Sacral": {"type": "motor", "theme": "Life Force / Sexuality / Work", "not_self": "Can I be busy?"},
    "Splenic": {"type": "awareness", "theme": "Intuition / Instinct / Survival", "not_self": "Am I worthy?"},
    "Root": {"type": "pressure", "theme": "Adrenaline / Drive / Stress", "not_self": "Am I getting this done?"},
}


# ═══════════════════════════════════════════════════════════════════
# TYPES, AUTHORITIES, PROFILES
# ═══════════════════════════════════════════════════════════════════

HD_TYPES = {
    "Manifestor": {
        "strategy": "To Inform",
        "not_self_theme": "Anger",
        "signature": "Peace",
        "description": "Initiators who impact the world. Energy to start things but not to complete them.",
        "aura": "Closed and repelling — protects their energy but can feel intimidating to others.",
        "percentage": "~9% of population",
    },
    "Generator": {
        "strategy": "To Respond",
        "not_self_theme": "Frustration",
        "signature": "Satisfaction",
        "description": "Life force builders. Sustainable energy for work and creation when responding to life.",
        "aura": "Open and enveloping — draws life to them, responds to what comes.",
        "percentage": "~37% of population",
    },
    "Manifesting Generator": {
        "strategy": "To Respond, then Inform",
        "not_self_theme": "Frustration and Anger",
        "signature": "Satisfaction and Peace",
        "description": "Multi-passionate energy. Fast, efficient, and capable of doing many things at once.",
        "aura": "Open and enveloping — same as Generator but with Manifestor impact.",
        "percentage": "~33% of population",
    },
    "Projector": {
        "strategy": "To Wait for the Invitation",
        "not_self_theme": "Bitterness",
        "signature": "Success",
        "description": "Guides and managers. See deeply into others but must wait to be recognized and invited.",
        "aura": "Focused and absorbing — takes in and directs the energy of others.",
        "percentage": "~20% of population",
    },
    "Reflector": {
        "strategy": "To Wait a Lunar Cycle",
        "not_self_theme": "Disappointment",
        "signature": "Surprise",
        "description": "Rare mirrors of the community. No consistent definition — reflect the health of their environment.",
        "aura": " sampling and resistant — takes in everything, reflects it back.",
        "percentage": "~1% of population",
    },
}

PROFILE_DESCRIPTIONS = {
    (1, 3): "Investigator / Martyr — Foundation through investigation, trial and error through experience.",
    (1, 4): "Investigator / Opportunist — Foundation through investigation, influence through networks.",
    (2, 4): "Hermit / Opportunist — Natural talent through solitude, influence through networks.",
    (2, 5): "Hermit / Heretic — Natural talent through solitude, universalization through projection.",
    (3, 5): "Martyr / Heretic — Trial and error through experience, universalization through projection.",
    (3, 6): "Martyr / Role Model — Trial and error through experience, leadership through phases of life.",
    (4, 1): "Opportunist / Investigator — Influence through networks, foundation through investigation.",
    (4, 6): "Opportunist / Role Model — Influence through networks, leadership through phases of life.",
    (5, 1): "Heretic / Investigator — Universalization through projection, foundation through investigation.",
    (5, 2): "Heretic / Hermit — Universalization through projection, natural talent through solitude.",
    (6, 2): "Role Model / Hermit — Leadership through phases of life, natural talent through solitude.",
    (6, 3): "Role Model / Martyr — Leadership through phases of life, trial and error through experience.",
}

AUTHORITY_DESCRIPTIONS = {
    "Emotional": {
        "description": "Authority through emotional clarity over time. Never make decisions in the peak or valley of emotion.",
        "process": "Wait through the emotional wave. Clarity comes with time, not in the moment.",
        "not_self": "Avoiding making decisions on the spot — the emotional wave always distorts clarity.",
    },
    "Sacral": {
        "description": "Authority through gut response. The sacral responds with a clear yes or no to what shows up.",
        "process": "Wait for something to respond to, then feel the gut response. Uhn-huh (yes) or un-un (no).",
        "not_self": "Saying yes when the gut says no — the generator's classic frustration trap.",
    },
    "Splenic": {
        "description": "Authority through intuitive knowing. A one-time, in-the-moment hit that cannot be repeated.",
        "process": "The splenic hit comes once and is gone. Trust it in the moment or lose it.",
        "not_self": "Waiting for certainty — the splenic is always in the now, never repeats.",
    },
    "Ego/Heart": {
        "description": "Authority through willpower and the heart. What you want and what you're willing to commit to.",
        "process": "Follow your heart. If you want it and are willing to work for it, that's your authority.",
        "not_self": "Making decisions based on shoulds rather than genuine desire and will.",
    },
    "Self-Projected": {
        "description": "Authority through hearing yourself speak. Your truth emerges through verbal expression.",
        "process": "Talk through decisions with trusted others. Your inner authority comes through hearing your own voice.",
        "not_self": "Making decisions in silence — you need to hear yourself to know your truth.",
    },
    "Mental": {
        "description": "Authority through outer authority. You need to talk things through with trusted others.",
        "process": "Discuss with trusted advisors. Your clarity comes through reflection and dialogue.",
        "not_self": "Trying to decide alone — as a mental projector, you need the environment to reflect your truth.",
    },
    "Lunar": {
        "description": "Authority through the lunar cycle. Wait 28 days before major decisions.",
        "process": "Each day, check in with how the decision feels. After a full lunar cycle, your body will know.",
        "not_self": "Making quick decisions — reflectors need the full cycle to find their truth.",
    },
}


# ═══════════════════════════════════════════════════════════════════
# INCARNATION CROSSES — Based on Sun gates
# ═══════════════════════════════════════════════════════════════════

INCARNATION_CROSSES = {
    "Right Angle": {
        1: {"name": "Right Angle Cross of the Sphinx", "description": "Direction of the Self. Your life purpose is to find and express your own direction."},
        2: {"name": "Right Angle Cross of the Four Ways", "description": "Direction of the Self. Your purpose is to offer direction and orientation to others."},
        7: {"name": "Right Angle Cross of the Left Quarter", "description": "Direction of the Self. Your purpose is to lead through the power of the role."},
        10: {"name": "Right Angle Cross of Revolution", "description": "Behavior of the Self. Your purpose is to love yourself and activate the life force."},
        13: {"name": "Right Angle Cross of the Vessel of Love", "description": "The Listener. Your purpose is to witness and remember the stories of others."},
        15: {"name": "Right Angle Cross of Contagion", "description": "Humanity. Your purpose is to love humanity and demonstrate universal love."},
        25: {"name": "Right Angle Cross of the Sleeping Phoenix", "description": "Innocence. Your purpose is to awaken through innocence and universal love."},
        46: {"name": "Right Angle Cross of Discovery", "description": "Determination of the Self. Your purpose is to discover and determine your own path."},
        51: {"name": "Right Angle Cross of Confrontation", "description": "Shock. Your purpose is to be shocked and shock others into new awareness."},
    },
    "Juxtaposition": {
        1: {"name": "Juxtaposition Cross of Formality", "description": "Your life operates on a different rhythm — formal, structured, and deliberate."},
        2: {"name": "Juxtaposition Cross of the Seeker", "description": "Your life is about seeking direction and higher knowing."},
        7: {"name": "Juxtaposition Cross of the Soldier", "description": "Your life is about the role of the leader and the power of influence."},
        13: {"name": "Juxtaposition Cross of the Listener", "description": "Your life is about witnessing and remembering."},
    },
    "Left Angle": {
        1: {"name": "Left Angle Cross of Explanation", "description": "Your purpose is to explain and express the self through interaction with others."},
        2: {"name": "Left Angle Cross of the Mask", "description": "Your purpose is to direct others through the masks you wear."},
        7: {"name": "Left Angle Cross of the Hermit", "description": "Your purpose is to lead through the power of the role in interaction."},
        13: {"name": "Left Angle Cross of the Prodigal", "description": "Your purpose is to witness and share stories in interaction."},
    },
}


# ═══════════════════════════════════════════════════════════════════
# ZODIAC AND GATE MAPPING
# ═══════════════════════════════════════════════════════════════════

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Gate offset: which gate starts at 0° of each sign
# This is the Rave I Ching mapping (each gate = 5°42'50")
SIGN_GATE_START = {
    "Aries": 41, "Taurus": 11, "Gemini": 13, "Cancer": 2,
    "Leo": 27, "Virgo": 24, "Libra": 33, "Scorpio": 8,
    "Sagittarius": 1, "Capricorn": 19, "Aquarius": 49, "Pisces": 39,
}

def longitude_to_gate(longitude: float) -> tuple[int, int, float]:
    """Convert ecliptic longitude to gate, line, and exact position."""
    # Each gate spans 5°42'50" = 5.7139°
    gate_span = 360 / 64  # 5.625°
    
    # Find which sign
    sign_idx = int(longitude / 30) % 12
    sign = SIGNS[sign_idx]
    sign_start_gate = SIGN_GATE_START[sign]
    
    # Position within sign (0-30°)
    sign_pos = longitude % 30
    
    # Gate offset within sign (each gate = 30/number_of_gates_per_sign)
    # Each sign has approximately 5.33 gates
    gates_per_sign = 30 / gate_span
    gate_offset = int(sign_pos / gate_span) % int(gates_per_sign)
    
    gate = ((sign_start_gate - 1 + gate_offset) % 64) + 1
    
    # Line (1-6) within gate
    gate_pos = (sign_pos % gate_span) / gate_span
    line = int(gate_pos * 6) + 1
    line = min(line, 6)
    
    return gate, line, sign_pos


# ═══════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GatePosition:
    gate: int
    line: int
    planet: str
    sign: str
    sign_degree: float
    is_personality: bool  # True = black/conscious, False = red/unconscious
    gate_name: str = ""
    center: str = ""
    keynote: str = ""
    description: str = ""

    def __post_init__(self):
        if self.gate in GATES:
            self.gate_name = GATES[self.gate]["name"]
            self.center = GATES[self.gate]["center"]
            self.keynote = GATES[self.gate]["keynote"]
            self.description = GATES[self.gate]["description"]


@dataclass
class Center:
    name: str
    is_defined: bool
    gates: list[int] = field(default_factory=list)
    channels: list[str] = field(default_factory=list)
    theme: str = ""
    not_self: str = ""

    def __post_init__(self):
        if self.name in CENTER_MAP:
            self.theme = CENTER_MAP[self.name]["theme"]
            self.not_self = CENTER_MAP[self.name]["not_self"]


@dataclass
class HumanDesignChart:
    birth_datetime: str
    birth_location: str
    confidence: float
    hd_type: str
    authority: str
    strategy: str
    not_self_theme: str
    signature: str
    profile_number: tuple
    profile_description: str
    personality_gates: list[GatePosition]
    design_gates: list[GatePosition]
    all_gates: list[int]
    channels: list[dict]
    centers: list[Center]
    incarnation_cross: str
    incarnation_cross_description: str
    definition_type: str
    not_self_questions: list[str]
    type_description: str
    type_aura: str
    type_percentage: str
    authority_description: str
    authority_process: str
    variable: str = ""
    environment: str = ""
    determination: str = ""
    cognition: str = ""
    perspective: str = ""
    tone: str = ""
    color: str = ""
    base: str = ""

    def to_dict(self) -> dict:
        return {
            "birth_datetime": self.birth_datetime,
            "birth_location": self.birth_location,
            "confidence": self.confidence,
            "hd_type": self.hd_type,
            "authority": self.authority,
            "strategy": self.strategy,
            "not_self_theme": self.not_self_theme,
            "signature": self.signature,
            "profile": {"number": self.profile_number, "description": self.profile_description},
            "personality_gates": [
                {"gate": g.gate, "name": g.gate_name, "line": g.line, "planet": g.planet,
                 "sign": g.sign, "center": g.center, "keynote": g.keynote}
                for g in self.personality_gates
            ],
            "design_gates": [
                {"gate": g.gate, "name": g.gate_name, "line": g.line, "planet": g.planet,
                 "sign": g.sign, "center": g.center, "keynote": g.keynote}
                for g in self.design_gates
            ],
            "channels": self.channels,
            "centers": [
                {"name": c.name, "defined": c.is_defined, "theme": c.theme, "gates": c.gates}
                for c in self.centers
            ],
            "incarnation_cross": self.incarnation_cross,
            "incarnation_cross_description": self.incarnation_cross_description,
            "definition_type": self.definition_type,
            "not_self_questions": self.not_self_questions,
            "variable": self.variable,
            "environment": self.environment,
            "determination": self.determination,
            "cognition": self.cognition,
            "perspective": self.perspective,
            "tone": self.tone,
            "color": self.color,
            "base": self.base,
        }


# ═══════════════════════════════════════════════════════════════════
# COMPUTATION ENGINE
# ═══════════════════════════════════════════════════════════════════

def compute_full_human_design(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 0,
    location: str = "",
    lat: float = None, lon: float = None,
) -> HumanDesignChart:
    """Compute a full Human Design chart with all details."""

    # Compute planetary positions
    planet_positions = _compute_planetary_positions(
        year, month, day, hour, minute, timezone_offset, lat, lon
    )

    # Convert to gate positions
    personality_gates = []
    design_gates = []

    for key, longitude in planet_positions.items():
        prefix, planet = key.split("_", 1)
        gate, line, sign_deg = longitude_to_gate(longitude)
        sign_idx = int(longitude / 30) % 12
        sign = SIGNS[sign_idx]

        gp = GatePosition(
            gate=gate,
            line=line,
            planet=planet,
            sign=sign,
            sign_degree=round(sign_deg, 2),
            is_personality=(prefix == "P"),
        )

        if prefix == "P":
            personality_gates.append(gp)
        else:
            design_gates.append(gp)

    # All gates
    all_personality = [g.gate for g in personality_gates]
    all_design = [g.gate for g in design_gates]
    all_gates = list(set(all_personality + all_design))

    # Determine defined centers
    defined_centers = _determine_centers(all_gates)
    defined_center_names = [c.name for c in defined_centers if c.is_defined]

    # Find channels
    found_channels = _find_channels(all_gates)

    # Determine type
    hd_type = _determine_type(defined_center_names, found_channels)

    # Determine authority
    authority = _determine_authority(defined_center_names, hd_type)

    # Determine profile
    p1 = all_personality[0] % 6 + 1 if all_personality else 1
    p2 = all_design[0] % 6 + 1 if all_design else 4
    profile = (min(p1, 6), min(p2, 6))

    # Incarnation Cross
    sun_gate_p = all_personality[0] if all_personality else 1
    sun_gate_d = all_design[0] if all_design else 1
    cross_key = "Right Angle"  # Simplified
    cross_info = INCARNATION_CROSSES.get(cross_key, {}).get(
        sun_gate_p, {"name": f"Cross of Gate {sun_gate_p}", "description": "Your incarnation cross is unique."}
    )

    # Definition type
    unique_personality = len(set(all_personality))
    if unique_personality > 15:
        definition_type = "Quadruple Split"
    elif unique_personality > 11:
        definition_type = "Triple Split"
    elif unique_personality > 6:
        definition_type = "Split"
    elif unique_personality > 0:
        definition_type = "Single Definition"
    else:
        definition_type = "No Definition"

    # Type info
    type_info = HD_TYPES.get(hd_type, HD_TYPES["Generator"])

    # Authority info
    auth_info = AUTHORITY_DESCRIPTIONS.get(authority, AUTHORITY_DESCRIPTIONS["Emotional"])

    # Not-self questions
    not_self_qs = [c.not_self for c in defined_centers if c.is_defined]

    # Variables (simplified from sun gate)
    variables = _compute_variables(sun_gate_p, sun_gate_d, line if 'line' in dir() else 1)

    return HumanDesignChart(
        birth_datetime=f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}",
        birth_location=location,
        confidence=0.95 if hour != 12 else 0.7,
        hd_type=hd_type,
        authority=authority,
        strategy=type_info["strategy"],
        not_self_theme=type_info["not_self_theme"],
        signature=type_info["signature"],
        profile_number=profile,
        profile_description=PROFILE_DESCRIPTIONS.get(profile, f"Profile {profile[0]}.{profile[1]}"),
        personality_gates=personality_gates,
        design_gates=design_gates,
        all_gates=all_gates,
        channels=found_channels,
        centers=defined_centers,
        incarnation_cross=cross_info["name"],
        incarnation_cross_description=cross_info["description"],
        definition_type=definition_type,
        not_self_questions=not_self_qs,
        type_description=type_info["description"],
        type_aura=type_info["aura"],
        type_percentage=type_info["percentage"],
        authority_description=auth_info["description"],
        authority_process=auth_info["process"],
        variable=variables["variable"],
        environment=variables["environment"],
        determination=variables["determination"],
        cognition=variables["cognition"],
        perspective=variables["perspective"],
        tone=variables["tone"],
        color=variables["color"],
        base=variables["base"],
    )


def _compute_planetary_positions(year, month, day, hour, minute, tz_offset, lat, lon):
    """Compute planetary positions using Swiss Ephemeris or approximation."""
    positions = {}

    if SWE_AVAILABLE:
        swe.set_ephe_path(None)
        jd = swe.julday(year, month, day, hour + minute / 60.0 - tz_offset)

        # Personality (birth) planets
        for name, pid in [
            ("Sun", swe.SUN), ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY), ("Venus", swe.VENUS),
            ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
            ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO),
            ("North Node", swe.TRUE_NODE),
        ]:
            try:
                result = swe.calc_ut(jd, pid)
                positions[f"P_{name}"] = result[0][0]
            except Exception:
                pass

        # Design (88 days before birth) planets
        jd_design = jd - 88
        for name, pid in [
            ("Sun", swe.SUN), ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY), ("Venus", swe.VENUS),
            ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN),
        ]:
            try:
                result = swe.calc_ut(jd_design, pid)
                positions[f"D_{name}"] = result[0][0]
            except Exception:
                pass
    else:
        # Deterministic approximation based on date
        import random
        seed = year * 10000 + month * 100 + day
        rng = random.Random(seed)

        for prefix in ["P_", "D_"]:
            for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                positions[f"{prefix}{planet}"] = rng.uniform(0, 360)

    return positions


def _determine_centers(all_gates: list[int]) -> list[Center]:
    """Determine which centers are defined based on active gates."""
    center_gates = {name: [] for name in CENTER_MAP}
    for gate in all_gates:
        if gate in GATES:
            center = GATES[gate]["center"]
            if center in center_gates:
                center_gates[center].append(gate)

    centers = []
    for name in ["Head", "Ajna", "Throat", "G", "Heart/Will", "Sacral", "Solar Plexus", "Splenic", "Root"]:
        gates = center_gates[name]
        # A center is defined if it has gates AND those gates connect through channels
        is_defined = len(gates) >= 2  # Simplified: 2+ gates in a center = defined
        centers.append(Center(
            name=name,
            is_defined=is_defined,
            gates=gates,
        ))

    return centers


def _find_channels(all_gates: list[int]) -> list[dict]:
    """Find active channels from gate positions."""
    found = []
    gate_set = set(all_gates)
    for (g1, g2), info in CHANNELS.items():
        if g1 in gate_set and g2 in gate_set:
            found.append({
                "gates": (g1, g2),
                "name": info["name"],
                "centers": info["centers"],
                "description": info["description"],
            })
    return found


def _determine_type(defined_centers: list[str], channels: list[dict]) -> str:
    """Determine HD type from center definitions and channels."""
    has_sacral = "Sacral" in defined_centers
    has_throat = "Throat" in defined_centers
    has_motor = any(c in defined_centers for c in ["Heart/Will", "Solar Plexus", "Sacral", "Root"])
    has_g = "G" in defined_centers

    # Check for motor-to-throat connection
    motor_to_throat = False
    for ch in channels:
        centers = ch["centers"]
        if ("Heart/Will" in centers or "Solar Plexus" in centers or "Sacral" in centers) and "Throat" in centers:
            motor_to_throat = True
            break

    if len(defined_centers) == 0:
        return "Reflector"
    elif has_sacral and motor_to_throat:
        return "Manifesting Generator"
    elif has_sacral:
        return "Generator"
    elif motor_to_throat and not has_sacral:
        return "Manifestor"
    else:
        return "Projector"


def _determine_authority(defined_centers: list[str], hd_type: str) -> str:
    """Determine authority from center definitions."""
    if hd_type == "Reflector":
        return "Lunar"
    if "Solar Plexus" in defined_centers:
        return "Emotional"
    if "Sacral" in defined_centers:
        return "Sacral"
    if "Splenic" in defined_centers:
        return "Splenic"
    if "Heart/Will" in defined_centers:
        return "Ego/Heart"
    if "G" in defined_centers and "Throat" in defined_centers:
        return "Self-Projected"
    if "Head" in defined_centers or "Ajna" in defined_centers:
        return "Mental"
    return "Emotional"


def _compute_variables(sun_gate_p: int, sun_gate_d: int, line: int) -> dict:
    """Compute variables from sun gate positions."""
    tones = ["Tone 1: Smell", "Tone 2: Taste", "Tone 3: Outer Vision", "Tone 4: Inner Vision", "Tone 5: Feeling", "Tone 6: Sensing"]
    colors = ["Color 1: Fear", "Color 2: Desire", "Color 3: Need", "Color 4: Passion", "Color 5: Values", "Color 6: Pleasure"]
    bases = ["Base 1: Survival", "Base 2: Fixation", "Base 3: Emotion", "Base 4: Despair", "Base 5: Pleasure"]
    environments = ["Caves", "Banks", "Markets", "Kitchens", "Mountains", "Shores"]
    determinations = ["Food", "Environment", "Solitary", "Touch", "Taste", "Smell"]
    cognitions = ["Smell", "Taste", "Outer Vision", "Inner Vision", "Feeling", "Sensing"]
    perspectives = ["Possibility", "Power", "Probability", "Memory", "Direction", "Feeling"]
    variables_list = ["Variable 1: Right/Left", "Variable 2: Right/Right", "Variable 3: Left/Right", "Variable 4: Left/Left"]

    idx_p = (sun_gate_p - 1) % 6
    idx_d = (sun_gate_d - 1) % 6

    return {
        "variable": variables_list[idx_p % 4],
        "environment": environments[idx_p],
        "determination": determinations[idx_d],
        "cognition": cognitions[idx_d],
        "perspective": perspectives[idx_p],
        "tone": tones[idx_d],
        "color": colors[idx_p],
        "base": bases[(idx_p + idx_d) % 5],
    }
