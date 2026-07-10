# Symbolic Systems Provenance Catalog

**Manifest version:** `symbolic-systems-v1`
**Policy:** each runtime result names one computational convention and its source
IDs. The catalog records the source tradition or reference used to choose that
convention; it does not turn symbolic correspondences into empirical claims.
Where scholarship or practice diverges, the encoder returns its named variant
rather than blending alternatives.

## Core and historical systems

- `SRC-KABBALAH-TREE` — *Sefer Yetzirah* tradition; ten-sephirot / 22-path tree convention.
- `SRC-HEBREW-NUMERALS` — standard *mispar hechrachi* Hebrew-letter values; final letters use ordinary values.
- `SRC-PYTHAGOREAN-TETRACTYS` — Pythagorean tetractys number symbolism.
- `SRC-ALCHEMY-FOUR-STAGES` — four-color work convention: nigredo, albedo, citrinitas, rubedo.
- `SRC-MESOPOTAMIAN-SEXAGESIMAL` — Mesopotamian base-60 place-value convention.
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
- `SRC-EGYPTIAN-UNILITERALS` — conventional Egyptological uniliteral transliteration.
- `SRC-EGYPTIAN-DECANS` — 36-decan division; this implementation exposes a civil-calendar index, not reconstructed astronomy.
- `SRC-JYOTISH-NAKSHATRA` — 27-nakshatra framework. Exact placements require complete birth data and an ephemeris.
- `SRC-MAYAN-TZOLKIN` — 260-day Tzolk'in with the GMT correlation anchored at 2012-12-21 = 4 Ajaw.
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
2. A missing script dictionary, ephemeris, or complete birth time produces an explicit limitation rather than a substituted reading.
3. Indus, cuneiform, and hieroglyphic data are never assigned invented lexical meanings.
4. The source catalog supports reproducibility and review; it is not a claim of historical certainty or predictive validity.
