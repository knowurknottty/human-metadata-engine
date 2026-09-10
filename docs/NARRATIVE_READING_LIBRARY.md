# Rich local readings and tarot

The expanded reading is entirely local: no API key, language model, provider call,
or per-reading AI cost. Python hosting and any geocoding remain separate services.
The UI visual redesign is not part of this change.

## Architecture

`extractors.py` now exposes returned planetary signs, houses and retrograde flags,
Human Design authority/profile/definition and all returned center states, plus the
name-derived tarot index. Time-withheld charts do not contribute houses or a
new ascendant. New reading-only records have no motif tags and do not boost
cross-system confidence. Tarot stays in the shared name-number independence group.

`reading_library.py` contains original editorial material for 12 signs, ten planets,
12 houses, five aspect types, 12 number values, five HD types, eight authorities,
six profile lines, nine centers, 64 gate prompts and 22 major archetypes.
`readings.py` applies that vocabulary only to supported returned values. Unknown
symbols receive no invented detail reading. Gate prompts are project-authored;
they are not official gate interpretations. No legacy gate/center topology is used.

The plan retains up to four gift/shadow themes, three tensions and three agreements,
and adds distinct system chapters. Plain/Mythic/Research share claim and evidence
IDs while changing prose. Reading claims carry exact planned texts and their
library version; the verifier rejects altered prose or dropped evidence.
Confidence on these authored readings is tentative, not empirical certainty.

Template version is `narrative-templates-v2`; library version is
`reflective-reading-library-v1`. Existing schema envelopes stay v1 because their
shape is compatible. Chapters and sentence records remain dynamic collections.
A sentence record is an evidence-linked passage and can contain multiple prose
sentences, as it already could in the original template engine.

The existing frontend exposes a chapter contents list and native expandable
chapters. All passages remain selectable and evidence-linked. Print expands the
chapters temporarily and restores their prior state afterward. Markdown includes
all chapters; the download endpoint alone accepts up to 1 MiB for longer encoded
reports. Analysis requests retain the existing 64 KiB cap.

## Independent tarot draw

Three reading types:

- `focus`: one-card focus.
- `situation`: situation, challenge, guidance.
- `crossroads`: where you stand, Path A, Path B, what to consider, a next step.

`POST /api/tarot` accepts exactly `{"spread":"focus"}` (or the other IDs).
`GET /api/tarot/spreads` returns the three supported choices.
The 78-card deck has 22 Major Arcana and four suits of 14 cards. Every minor
card has its own authored theme, image and prompt in `tarot_minor_library.py`.
Readings are upright only; there is no implied reversed-card interpretation.
Card XIII retains its name in the standalone draw and is discussed as symbolic
transition, never as a forecast. In name synthesis it is titled Transformation
(XIII), with the exact index and source available in the ledger.

The server uses operating-system randomness and samples without replacement.
The **draw** is intentionally nondeterministic; `realize_reading(spread, card_ids)`
is deterministic. The reading ID hashes the interpretation version, spread,
and ordered cards. It identifies content, not a unique draw event. Markdown
exports contain those fields for replay. Readings are not persisted server-side.
The optional question stays in the browser and is included in the local download;
it is neither transmitted nor used to select cards or customize prose.

The API uses the existing request validation, rate limiter and concurrency gate.
The client prevents concurrent draws, has a timeout, renders through textContent,
and keeps the preceding reading on failure. It does not auto-redraw or call AI.
The generic Netlify `/api/*` proxy already forwards these routes; the Python
backend must be updated together with the frontend before production use.

## Editorial source boundaries

The prose is original and intentionally framed as reflection. It is not a
translation or reproduction of a divination manual and makes no claim that
symbolic readings are measured personality traits.

- Existing normalized sign/number themes: `src/synthesis/data/motif_ontology_v1.json`.
- Existing computational conventions: `docs/symbolic-systems-provenance.md`.
- RWS historical context: A. E. Waite, *The Pictorial Key to the Tarot*,
  https://en.wikisource.org/wiki/Pictorial_Key_to_the_Tarot .
- Human Design terminology context: https://jovianarchive.com/pages/what-is-human-design
  and https://jovianarchive.com/pages/what-is-inner-authority-in-human-design .
- Returned HD topology authority: `src/true_human_design`; the approximate legacy
  drawing and legacy gate center mappings do not authorize new calculations.

These sources establish terminology and context, not validation of the authored
interpretations. New library material must be reviewed for unsupported claims,
misleading certainty and duplication before changing the version.
