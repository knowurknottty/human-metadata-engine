"""Original editorial prompts, not additional calculations or authoritative doctrine.

These entries interpret named symbols for reflection. They never participate in
motif scoring. See docs/NARRATIVE_READING_LIBRARY.md for sources and boundaries.
"""

LIBRARY_VERSION = "reflective-reading-library-v1"

# theme, useful expression, counterweight, image
NUMBERS = {
    1: ("initiative", "beginning something before consensus arrives", "asking for help without surrendering direction", "a first footprint on an unmarked path"),
    2: ("reciprocity", "listening for what a situation needs from both sides", "naming a preference even when agreement is uncertain", "two banks giving a river its shape"),
    3: ("expression", "giving an idea a voice, image, or playful form", "finishing a small piece instead of collecting possibilities", "a workshop with its windows open"),
    4: ("structure", "making a dependable rhythm for work that matters", "revising a rule when it no longer serves its purpose", "a foundation that leaves room for another doorway"),
    5: ("freedom", "learning through movement and unfamiliar perspectives", "staying long enough to discover what novelty conceals", "a road that branches beyond the familiar hills"),
    6: ("care", "creating conditions in which others can participate", "offering support without taking over responsibility", "a hearth with space for more than one voice"),
    7: ("inquiry", "following a question beyond its first easy answer", "letting an unfinished thought meet real feedback", "a lamp illuminating one page at a time"),
    8: ("stewardship", "turning intention into coordinated practical effort", "distinguishing influence from control", "a bridge maintained by many hands"),
    9: ("completion", "seeing what an experience can contribute to a larger whole", "ending a commitment without erasing what it taught", "a harvest gathered before a new season"),
    11: ("sensitivity and expression", "putting a subtle impression into words others can examine", "checking an impression against what actually happened", "a fine string that needs both tension and tuning"),
    22: ("vision and construction", "breaking a large possibility into workable stages", "choosing a human scale instead of an impossible standard", "a drawing slowly becoming a place to inhabit"),
    33: ("care and communication", "sharing understanding in a form someone else can use", "keeping room for your own limits and learning", "a teacher who leaves an empty chair for questions"),
}
SIGN_THEMES = {
    "Aries": ("initiative and directness", "starting a small experiment", "leaving room to listen", "a spark seeking useful tinder"),
    "Taurus": ("continuity and tangible experience", "building through steady repetition", "recognizing when stability becomes resistance", "roots deep enough to support new growth"),
    "Gemini": ("curiosity and exchange", "trying several ways to explain an idea", "pausing to integrate what you have gathered", "a conversation between open windows"),
    "Cancer": ("care and belonging", "noticing what creates a sense of welcome", "separating care from responsibility for every feeling", "a sheltered inlet with an opening to the sea"),
    "Leo": ("creative visibility", "sharing something that carries your own signature", "allowing feedback to matter more than applause", "a fire that illuminates more than its keeper"),
    "Virgo": ("discernment and craft", "making one concrete improvement", "letting usefulness outrank perfection", "a careful hand repairing a well-used object"),
    "Libra": ("relationship and proportion", "making room for another perspective", "making a choice before every disagreement disappears", "a balance adjusted through conversation"),
    "Scorpio": ("depth and change", "staying with a difficult but worthwhile question", "allowing an experience to remain ordinary", "a well whose depth does not require constant descent"),
    "Sagittarius": ("discovery and perspective", "placing an experience in a wider context", "testing a large claim against a small detail", "a horizon reached by walking rather than declaring"),
    "Capricorn": ("structure and sustained effort", "setting a sequence you can actually maintain", "revising success to include rest and support", "a staircase built one sound step at a time"),
    "Aquarius": ("independence and shared ideas", "questioning an inherited assumption", "staying connected while disagreeing", "a window opened in a familiar room"),
    "Pisces": ("imagination and receptivity", "letting different impressions coexist before deciding", "giving an intuition a practical boundary", "a shoreline where distinct waters meet"),
}
PLANETS = {
    "Sun": "expression and the direction of attention", "Moon": "familiarity, comfort, and changing responses",
    "Mercury": "learning, language, and exchange", "Venus": "appreciation, preferences, and relating",
    "Mars": "effort, assertion, and taking action", "Jupiter": "growth, perspective, and what feels worth exploring",
    "Saturn": "limits, commitments, and patient development", "Uranus": "experimentation and departures from habit",
    "Neptune": "imagination and the boundary between an ideal and experience", "Pluto": "change and the question of what to retain",
    "Ascendant": "first approaches and how an encounter begins",
}
HOUSES = {
    1: "first approaches and self-presentation", 2: "resources and what you value", 3: "everyday learning and communication",
    4: "home and foundations", 5: "creative play and personal expression", 6: "routines and practical contribution",
    7: "one-to-one cooperation", 8: "shared commitments and boundaries", 9: "study and wider perspectives",
    10: "public contribution and responsibility", 11: "groups and shared aspirations", 12: "solitude and behind-the-scenes reflection",
}
ASPECTS = {
    "Conjunction": ("concentration", "two symbolic functions occupy nearby positions", "tell the two needs apart before combining them"),
    "Sextile": ("cooperation", "two functions offer a possible route for collaboration", "notice an opportunity that still needs deliberate effort"),
    "Square": ("friction", "two functions can be read as competing demands", "give each need a specific place instead of treating one as a mistake"),
    "Trine": ("ease", "two functions can be read as supporting each other", "develop what comes easily rather than leaving it unexamined"),
    "Opposition": ("perspective", "two functions face each other across the chart", "try describing the same situation from both sides"),
}
HD_TYPES = {
    "Generator": ("response and sustained involvement", "compare a task you willingly return to with one you continue only from obligation", "a craftsperson learning which work invites another hour"),
    "Manifesting Generator": ("response, movement, and revision", "notice which changes improve a process and which merely restart it", "a maker testing more than one route through the workshop"),
    "Manifestor": ("initiation and communication", "consider who benefits from knowing what you intend before you begin", "a pathfinder leaving clear signs at the turning points"),
    "Projector": ("recognition and focused guidance", "compare advice that was requested with advice you felt compelled to give", "a guide choosing where a map would actually help"),
    "Reflector": ("observation across changing contexts", "revisit an impression in different surroundings before treating it as settled", "a traveler comparing the same landscape in different light"),
}
AUTHORITIES = {
    "Emotional": "compare how a low-stakes preference feels at different moments, rather than asking one intense moment to settle it",
    "Sacral": "notice your immediate willingness toward a specific, low-stakes option, then compare it with what you learn by trying it",
    "Splenic": "record a brief first impression and later check its fit with observable details",
    "Ego Manifested": "listen to the commitments you voice and ask which ones you have the resources to honor",
    "Ego Projected": "separate what you want to commit to from what would merely win approval",
    "Self-Projected": "say an option aloud and notice whether your description becomes clearer or more strained",
    "Mental/Environmental": "use a trusted listener and a comfortable setting to hear your own reasoning without handing the decision away",
    "Lunar": "return to a low-stakes question over time and record what changes with the context",
}
PROFILE_LINES = {
    1: ("investigation", "what information would provide a useful foundation"),
    2: ("natural practice and retreat", "which activity becomes clearer when given unpressured space"),
    3: ("experimentation", "what a small reversible attempt could teach"),
    4: ("connection", "which trusted relationship makes exchange more honest"),
    5: ("practical expectations", "which problem is actually yours to help solve"),
    6: ("perspective", "what changes when you step back from the immediate situation"),
}
CENTERS = {
    "Head": "questions and inspiration", "Ajna": "concepts and explanations", "Throat": "expression and being heard",
    "G/Identity": "direction and a sense of self", "Heart/Will": "promises and the use of effort",
    "Solar Plexus": "emotional timing", "Sacral": "involvement and sustainable effort",
    "Splenic": "immediate impressions", "Root": "pressure and pacing",
}
# Original prompts for all 64 gate indices; no topology or legacy center map is imported.
GATE_PROMPTS = {
1: "give an original idea a modest first form", 2: "notice what helps you choose a direction", 3: "allow a beginning to be untidy without abandoning it",
4: "hold an explanation lightly until it has been tested", 5: "find a rhythm that supports rather than restricts you", 6: "name a boundary before friction grows",
7: "ask what responsible direction would look like in a group", 8: "offer a contribution without requiring imitation", 9: "give one small detail your undivided attention",
10: "compare your actions with the values you describe", 11: "keep an idea available without making it an obligation", 12: "choose a moment when your words can be received",
13: "listen without making another person's story your own", 14: "direct practical effort toward something you value", 15: "make room for rhythms different from your own",
16: "practice a skill beyond its first exciting stage", 17: "state an opinion together with what might change it", 18: "offer a correction with a usable next step",
19: "distinguish a need from an unspoken expectation", 20: "notice what is actually happening before rehearsing a response", 21: "clarify the scope of a responsibility before managing it",
22: "allow openness to include the option of a pause", 23: "explain one complex idea in ordinary language", 24: "notice when revisiting a thought produces something new",
25: "meet an unfamiliar experience without deciding its meaning too early", 26: "describe an offering without exaggerating it", 27: "offer care at a scale you can sustain",
28: "ask which challenge is worth the effort it requires", 29: "check the scope of a yes before extending it", 30: "let a strong wish exist without making the outcome compulsory",
31: "invite feedback from the people affected by your direction", 32: "distinguish what deserves continuity from what merely persists", 33: "take time to digest an experience before retelling it",
34: "match the force of an action to the need in front of you", 35: "ask what a new experience would add to what you have learned", 36: "leave room for unfamiliarity while learning a new situation",
37: "make the terms of mutual support explicit", 38: "choose a disagreement that serves something you value", 39: "ask whether a challenge opens conversation or only provokes a reaction",
40: "balance a promise to others with time to recover your attention", 41: "choose one possibility from a crowded imagination", 42: "recognize when a cycle has reached a useful stopping point",
43: "give a fresh insight enough context to be understood", 44: "compare a familiar pattern with the details that are different this time", 45: "make shared resources and responsibilities visible",
46: "notice the practical conditions that help you participate", 47: "allow understanding to develop without forcing an immediate explanation", 48: "share a useful piece of knowledge before feeling completely prepared",
49: "name a principle together with the responsibilities it creates", 50: "ask who a shared rule protects and who it overlooks", 51: "try a manageable challenge without turning it into a contest",
52: "create a small interval of uninterrupted attention", 53: "give a beginning a realistic next step", 54: "describe ambition in terms of practice rather than status",
55: "notice how your sense of possibility changes with your mood", 56: "tell a story that leaves room for someone else's understanding", 57: "check a subtle impression against the present situation",
58: "improve something because it matters rather than because it is imperfect", 59: "build trust through a clear and welcome exchange", 60: "choose what can be done within the actual limits",
61: "stay curious about a question that has no immediate answer", 62: "use a precise detail to make an explanation clearer", 63: "turn doubt into a question that can be investigated",
64: "let fragments remain fragments until a pattern becomes useful",
}
# Project-authored reflective readings keyed to the engine's RWS indices.
# XIII is titled Transformation in prose so a card label is not a mortality claim.
TAROT = [
("The Fool", "beginning", "try a small unfamiliar step while noticing the ground beneath it", "a traveler at the edge of a new path"),
("The Magician", "application", "choose which available tool can turn an intention into a first action", "a table of tools waiting for a deliberate hand"),
("The High Priestess", "attention", "leave space for what is not yet clear without calling uncertainty an answer", "a quiet threshold between question and response"),
("The Empress", "cultivation", "give an idea the time and conditions it needs to take form", "a garden shaped by patient tending"),
("The Emperor", "structure", "build a boundary that supports participation rather than closing it down", "a seat of responsibility with room for counsel"),
("The Hierophant", "inheritance", "examine what a received practice teaches and where it needs questioning", "a doorway into a shared tradition"),
("The Lovers", "alignment", "compare a choice with the values you want it to express", "two paths asking for an honest choice"),
("The Chariot", "direction", "bring competing efforts toward one manageable objective", "a vehicle whose movement depends on coordinated reins"),
("Strength", "steadiness", "meet resistance with patient attention before adding force", "an open hand beside a powerful creature"),
("The Hermit", "discernment", "take enough space to hear your own question, then bring one insight back", "a lantern that reveals the next few steps"),
("Wheel of Fortune", "change", "separate what you can influence from the conditions you must respond to", "a turning wheel viewed from more than one position"),
("Justice", "accountability", "consider both the reasons for a choice and the effects it has on others", "a balance that asks for careful attention"),
("The Hanged Man", "perspective", "pause one habitual response and look at the situation from another angle", "a familiar landscape seen upside down"),
("Transformation (XIII)", "transition", "identify a habit or unfinished commitment you are ready to release", "a field being cleared for another season"),
("Temperance", "combination", "adjust the proportions of two competing needs instead of choosing an extreme", "water passing carefully between two vessels"),
("The Devil", "attachment", "examine a bargain or habit that narrows your sense of choice", "a loose chain noticed for the first time"),
("The Tower", "revision", "test a brittle assumption through a small change before relying on it further", "an old structure revealing where it needs repair"),
("The Star", "renewal", "choose a modest act that makes hope practical", "water returned to ground that can receive it"),
("The Moon", "uncertainty", "distinguish what you observed from the story you added to it", "a path whose edges emerge slowly in dim light"),
("The Sun", "openness", "share something clearly enough that another person can respond to it", "a courtyard becoming visible in morning light"),
("Judgement", "reassessment", "review an old decision using what you understand now", "a call to listen again rather than repeat an old answer"),
("The World", "integration", "name what has come together and what remains open", "a circle that marks completion without closing the horizon"),
]
