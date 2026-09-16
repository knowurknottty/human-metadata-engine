# Symbolic Systems Provenance Catalog

**Manifest version:** `symbolic-systems-v1`
**Policy:** each runtime result names one computational convention and its source
IDs. The catalog records the source tradition or reference used to choose that
convention; it does not turn symbolic correspondences into empirical claims.
Where scholarship or practice diverges, the encoder returns its named variant
rather than blending alternatives. `signature-v3` artifacts reuse this catalog
through the stricter `system-result-v2` provenance envelope.

## Core and historical systems

- `SRC-KABBALAH-TREE` — *Sefer Yetzirah* tradition; ten-sephirot / 22-path tree convention.
- `SRC-HEBREW-NUMERALS` — standard *mispar hechrachi* Hebrew-letter values; final letters use ordinary values.
- `SRC-PYTHAGOREAN-TETRACTYS` — Pythagorean tetractys number symbolism.
- `SRC-ALCHEMY-FOUR-STAGES` — four-color work convention: nigredo, albedo, citrinitas, rubedo.
- `SRC-MESOPOTAMIAN-SEXAGESIMAL` — Mesopotamian base-60 place-value convention.
- `SRC-ETCSL-INANA-ENKI` — ETCSL 1.3.1, *Inana and Enki*; composite Sumerian text/translation used for the visible *me* inventory. The current bounded inventory contains the 81 legible named items in the surviving final recitation; damaged placeholders are excluded rather than reconstructed. This is not asserted to be a complete ancient canonical total.
- `SRC-FARBER-ME-LIST` — Gertrud Farber, *Der Mythos ‘Inanna und Enki’ unter besonderer Berücksichtigung der Liste der me* (Studia Pohl 10, 1973); specialist study of the *me* list and its textual tradition.
- `SRC-ORACC-ENKI` — ORACC Ancient Mesopotamian Gods and Goddesses, Enki/Ea overview; contextual secondary reference for the narrative transfer of the powers of civilization, not a source for filling textual lacunae.
- `SRC-HERMETIC-SEVEN-PRINCIPLES` — *The Kybalion* seven-principles convention; modern Hermetic text, not an ancient corpus claim.
- `SRC-TAROT-RWS` — Rider-Waite-Smith major-arcana ordering.
- `SRC-CHALDEAN-ORDER` — Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon order.
- `SRC-HERMES-THOTH-NABU` — comparative Greek, Egyptian, and Mesopotamian writing/knowledge-deity framing.
- `SRC-KEY-OF-SOLOMON` — *Key of Solomon* planetary tradition; indexing only, no ritual instructions.
- `SRC-SHEM-72` — 72-name / 72-fold indexing convention; the encoder does not emit entity names.
- `SRC-ARABIC-ABJAD` — eastern-order *abjad kabir* letter values.

## Cross-cultural systems

- `SRC-YIJING-KING-WEN` — *Zhou Yi* 64-hexagram King Wen sequence.
- `SRC-WU-XING` — five-phase sequence: Wood, Fire, Earth, Metal, Water.
- `SRC-SEXAGENARY-CYCLE` — ten heavenly stems and twelve earthly branches year-cycle convention.
- `SRC-BAZI-SEXAGENARY` — Four-Pillars use of the sexagenary stem/branch cycle for year, month, day, and hour pillars.
- `SRC-BAZI-JIEQI` — 24-solar-term astronomy; `bazi-v1` uses Li Chun for the year boundary and 30-degree Jie month boundaries.
- `SRC-EGYPTIAN-UNILITERALS` — conventional Egyptological uniliteral transliteration.
- `SRC-EGYPTIAN-DECANS` — 36-decan division; this implementation exposes a civil-calendar index, not reconstructed astronomy.
- `SRC-JYOTISH-LAHIRI` — Lahiri sidereal ayanamsa as implemented by Swiss Ephemeris.
- `SRC-JYOTISH-NAKSHATRA` — 27-nakshatra framework. Exact placements require complete birth data and an ephemeris.
- `SRC-JYOTISH-NAVAMSHA` — D9/Navamsha ninefold sign division with modality-based starting signs.
- `SRC-JYOTISH-DASAMSA` — D10/Dasamsa tenfold sign division; odd signs start from themselves and even signs from the ninth sign.
- `SRC-JYOTISH-VIMSHOTTARI` — fixed Ketu-through-Mercury 120-year Vimshottari sequence; birth balance derives from the unelapsed Moon-nakshatra fraction.
- `SRC-MAYAN-GMT` — Goodman-Martinez-Thompson 584283 correlation used by the Classical Maya calendar artifact.
- `SRC-MAYAN-TZOLKIN` — 260-day Tzolk'in with the GMT correlation anchored at 2012-12-21 = 4 Ajaw.
- `SRC-MAYAN-HAAB` — 365-day Haab' calendar used in the Classical Maya Calendar Round.
- `SRC-MAYAN-G-SERIES` — ninefold Lord-of-Night cycle; the 2012-12-21 anchor resolves to G9 under this convention.
- `SRC-CUNEIFORM-UNICODE` — Unicode Cuneiform block identifiers; no lexical decipherment is claimed.

## Specialized systems and constraints

- `SRC-ELDER-FUTHARK` — 24-rune Elder Futhark ordering.
- `SRC-OGHAM-TREES` — medieval Ogham letter/tree associations; later tree correspondences are not presented as Iron Age fact.
- `SRC-MAAT` — Ma'at as a symbolic balance framework, not a moral score.
- `SRC-MANDAEAN-TRADITION` — Mandaean context for duodecimal representation; no Mandaic lexical reading is inferred.
- `SRC-ARCHITECTURAL-PROPORTION` — geometric proportion vocabulary. “Tartaria” is not treated as an established historical polity or architectural tradition.
- `SRC-INDUS-UNDECIPHERED` — scholarly consensus that Indus signs remain undeciphered; output is structural only.
- `SRC-UNICODE-STANDARD` — Unicode scalar values and UTF-8 encoding rules.

## Structural integrations

- `SRC-APOLLONIUS-PHILOSTRATUS` — Philostratus, *Life of Apollonius of Tyana*; existing module is treated as symbolic synthesis.
- `SRC-PYTHAGOREAN-NUMEROLOGY` — modern Pythagorean life-path and personal-year arithmetic convention.
- `SRC-TAROT-KABBALAH-CORRESPONDENCE` — explicit comparative bridge convention. Links are displayed as mappings, not proof that traditions validate one another.

## Source-boundary rules

1. Native scripts are retained in the input; transliteration uses `builtin-v1` and is named in each result.
2. A missing script dictionary, ephemeris, complete birth time, or required location produces an explicit limitation rather than a substituted reading.
3. Indus, cuneiform, and hieroglyphic data are never assigned invented lexical meanings.
4. Source recurrence is not evidence independence. `birth_date` and `birth_instant` belong to one `birth` dependency family in `signature-v3`.
5. Timing artifacts are derived from frozen natal inputs and are excluded from static-signature convergence.
6. The source catalog supports reproducibility and review; it is not a claim of historical certainty or predictive validity.
7. The Sumerian *me* ontology is a corpus-level historical/textual reference. No modern name, birth datum, numerological result, or other identity feature is treated as evidence that a person possesses or corresponds to a particular *me*. Any future personal correspondence layer must use a separately versioned modern convention and remain explicitly interpretive.
8. The nine thematic *me* categories and the Human Capacity crosswalk are Inversion Labs analytical structures, not classifications stated by ETCSL or claimed as ancient Sumerian doctrine. They are versioned separately from the historical inventory and may not be cited as source-text evidence.
