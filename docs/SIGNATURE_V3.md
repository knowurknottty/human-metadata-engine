# Signature v3 research contract

`signature-v3` is an opt-in research composition layer. The public API remains
`analysis-v1`, the compatibility engine remains `signature-v2`, and the report
contract remains `report-v1` until a separate public migration is reviewed.

## Why v3 exists

The older encoder map mixes static calculations, symbolic correspondences,
assessments, and time-varying work in one flat namespace. v3 instead emits
versioned `system-result-v2` artifacts with explicit provenance and dependency
semantics.

Each system result names its system/version, tradition, computational
convention, artifact class, epistemic class, input dependencies, dependency
roots, sensitivity, status, calculation payload, interpretation payload, source
IDs, licensing/dependency notes, and limitations.

## Artifact classes

- `static_signature` — stable calculations from a frozen subject input.
- `timing` — time-varying calculations derived from a frozen natal signature or from an explicit environment/time context.
- `divination_session` — session/event artifacts with explicit casting entropy.
- `assessment` — user-supplied or instrument-derived assessment data.
- `environment` — place/orientation/context traditions.
- `biometric` — explicitly supplied physiological or genetic observations.

Of these artifact classes, only `static_signature` and `timing` are implemented in this tranche. The number of implemented systems inside those classes is independent of that statement.

## Independence policy

A system count is a lens count, not an evidence count. Raw dependency roots are
preserved for provenance, then collapsed into independence families. `birth_date`
and `birth_instant` both belong to the `birth` family, so natal and timing systems
do not become independent confirmations merely because multiple traditions use
the same birth data.

Timing artifacts are excluded from static-signature convergence entirely.
Planetary hours use `environment_context`, but that still does not make them
empirical evidence about a person.

## Implemented v3 static systems

- `bazi-v2` — Four Pillars, Day Master, hidden stems, Ten Gods, and structural Five-Phase distribution under disclosed Li Chun/Jie/civil-time conventions. An explicit IANA `timezone_id` is authoritative when supplied; date-only partial results evaluate local-day boundaries with the zone's historical offsets.
- `jyotish-v3` — explicit Lahiri **or** Raman sidereal projection; mean **or** true Rahu/Ketu convention; 27 nakshatras/padas; D9/Navamsha; D10/Dasamsa; sidereal Placidus houses; explicit speed requests for retrograde state; and IANA-aware conversion of civil birth time to one UTC instant.
- `maya-classical-gmt-v1` — Long Count, Tzolk'in, Haab', Calendar Round, and Lord of Night under GMT 584283. The emitted correlation metadata identifies 584285 and 584289 as alternative published constants; this result does not silently treat GMT 584283 as the only scholarly convention.

## R3 live-calculator promotion

The legacy `signature-v2` result now exposes the three richer calculator envelopes additively at `signature.systems`: `jyotish`, `bazi`, and `maya_classical`. This is an inspectable contract surface, not a migration of the compatibility encoder map. Existing `vedic_jyotish` and `mayan_tzolkin` encoders remain unchanged for backward compatibility; the richer Maya result is the canonical detailed calendar contract.

Each calculator remains a named adapter with its own convention: Jyotish records its Lahiri/Raman ayanamsa and node mode; BaZi records Li Chun/Jie, zone resolution, civil-midnight policy, and its explicit absence of true-solar-time correction; Classical Maya records GMT 584283 and alternatives. Only validated Gregorian/JDN primitives may be shared. No generic calendar policy can substitute one tradition's epoch or day boundary for another.

The synthesis layer emits selected richer fields as deterministic, provenance-bound `reading_only` records. They have no ontology mapping, share the `birth_calculator` dependence family, and cannot add motif votes, convergence, or empirical support. Handoff v2 preserves such selected contract values only through reviewed `signature.systems.*` paths and continues to redact raw location, coordinate, and timezone fields.

Golden tests lock representative inputs, convention/version strings, withholding behavior, boundary behavior, and deterministic replay. They are the code/document drift gate for the conventions listed above.

## R4 governance, disclosure, and deliberate re-baseline

### Convention governance protocol

Scholar-facing conventions carried by the calculators (Jyotish ayanamsa, the
Classical Maya correlation constant, and the BaZi Jieqi/solar-term algorithm)
change only through this recorded procedure. It operationalises migration rules
2 and 5 and the golden-quarantine rule; it is **not** a mechanism for moving
constants quietly.

1. **Propose** — an issue describes the convention, its current value, the
   scholarly or in-repo source, and the expected effect on returned coordinates.
2. **Adjudicate** — review confirms the source is verifiable. Fabricating an
   arcsecond figure or a citation is a no-fabrication violation, not a shortcut.
3. **Version bump** — the affected `system_version` and `convention` string are
   bumped together; metadata renames require the version signal or a documented
   compatibility break, never a silent in-place rename.
4. **Re-baseline** — goldens are re-computed deliberately and the change is
   recorded in the changelog entry referenced from the fixture header. Golden
   fixtures are never updated automatically on a `tzdata` bump; that friction is
   intended.
5. **Quarantine** — a stale golden may be quarantined only with a recorded
   changelog entry naming the convention change that invalidated it.

### R4 changelog

- **2026-09-23 — local-first Netlify ingress hardening.** Removed the SPA
  catch-all rewrite and wildcard `/api/*` proxy. The Netlify bridge now exposes
  only the six deterministic engine routes used by the public client and
  diagnostics. Unknown application/API paths fail closed, cross-origin response
  synthesis was removed, and a regression test locks the route allowlist.
  Intentional collection re-baseline: **490 pytest tests / 68 pytest files** and
  **67 canonical test files**.

### Per-system disclosure block

Each calculator emits an additive `interpretation.disclosure` block beside its
result. `approximation_precision` is either the literal `undisclosed`, when no
arcsecond figure is published in the implementation docs, or `exact_integer`
where the calculation is exact integer-day arithmetic. The block never claims
birth-time precision, true-solar correction, or a numeric truth-confidence
scalar. The value is traceable to this section:

| system | convention | approximation_precision | basis |
| --- | --- | --- | --- |
| `jyotish-v3` | `lahiri-mean-node-27-nakshatra-zone-aware-v3` | `undisclosed` | No published arcsecond figure for the sidereal projection. |
| `bazi-v2` | `li-chun-jie-civil-time-zone-aware-v2` | `undisclosed` | Solar-term placement uses an ephemeris solar longitude; no published arcsecond figure. |
| `maya-classical-gmt-v1` | `gmt-584283-v1` | `exact_integer` | Long Count, Tzolk'in, Haab', Calendar Round, and Lord of Night are exact integer-day arithmetic. |

### Unsupported-capability registry

`src/unsupported_capabilities.py` is the machine-readable negative-fact ledger.
It records, per system, the byte-stable disclosure fragment that must remain
present in that system's `limitations`. The registry pins the claim; the encoder
limitations remain the published wording. The no-fabrication suite asserts both
directions, so the two cannot drift.

Enforcement surfaces for this section: `src/unsupported_capabilities.py`,
`src/agent_handoff.py`, `src/system_contracts.py`, `src/time_context.py`, and
`src/synthesis/realize.py`. `src/synthesis/extractors.py` remains the
evidence-inventory owner whose `EXTRACTORS` tuple and `ROADMAP_EVIDENCE_CONFIG`
are reconciled against the documented families.

Recorded absences: BaZi true/apparent solar-time correction and alternate
late-Zi 23:00 rollover are **not applied**; Jyotish emits no Vimshottari dasha in
the static signature and does not substitute a noon chart; Classical Maya emits
non-negative Long Count dates only and keeps modern Dreamspell systems separate.
No Gene Keys backend exists or is planned in this contract, and `confidence_bound`
remains removed.

### Metadata rename compatibility note (CD-08)

Narrative metadata renamed `evidence_density` to `evidence_item_count` and
`total_evidence_density` to `total_evidence_item_count`. A repository-wide audit
found no in-repo, web, or front-end consumer of the old keys, so this is recorded
as a documented compatibility break rather than a dual-key window; no external
consumer was found to justify a one-release alias. `narrative-v1` remains the
schema identifier because the rename is metadata-only and does not alter the
narrative envelope.

### Handoff analysis-mode policy (CD-12)

`agent_handoff.build_handoff_v2` rejects an unknown `analysis_mode` instead of
echoing it. The accepted set mirrors `public_contract.MODES` and is asserted
equal in the handoff suite.

### Corpus asset id convention

Every `SYSTEM_VOCABULARY_ASSETS` id follows the pattern
`sys-<system-with-dashes>-<NNN>` for the first 12 × 10 block and
`sys-<system-with-dashes>-r2-<NNN>` for the 24 × 5 R2 block. The single
outlier `sys-human_design-007` (underscore in the system segment) is a
documented exemption preserved from the R1 asset set; no alias is introduced
and the id is stable.

The nine shared-source witnesses documented in this contract are:
`sys-gematria-007`, `sys-kabbalah-006`, `sys-pythagorean-007`,
`sys-chaldean-005`, `sys-ordinal-003`, `sys-isopsephy-007`,
`sys-linguistic-007`, `sys-chinese-006`, and `sys-human_design-008`.

### Vocabulary eligibility declarations (CD-23)

`SYSTEM_VOCABULARY_ASSETS` declares `mode_eligibility` and
`identity_synthesis_eligible` on every asset. R4 keeps those as declarations:
`select_system_vocabulary` enforces `identity_synthesis_eligible`, while
`mode_eligibility` remains documentation of the register each asset was written
for. No `readings.py` mode guard is added in this tranche; cross-mode surfacing
is recorded as intentional for this release and the guard stays a deferred
item.

## Implemented timing systems

All dynamic artifacts require an explicit `as_of`; the engine never reads the wall clock silently.

- `vimshottari-v2` — birth balance and Mahadasha boundaries using the selected Jyotish ayanamsa and a disclosed 365.2425-day year normalization.
- `transits-v1` — tropical geocentric positions plus major natal/transit contacts inside a fixed one-degree computational orb.
- `secondary-progressions-v1` — day-for-year planetary progressions using `elapsed_days / 365.2425` symbolic days after birth.
- `solar-arc-v1` — the secondary-progressed Sun arc applied uniformly to natal planets, Ascendant, and Midheaven; coordinate output only.
- `solar-return-v1` — exact tropical Sun-longitude return bracketing `as_of` using Swiss Ephemeris solar-crossing search; the return chart is erected for stored birth coordinates.
- `annual-profection-v2` — one whole sign per completed civil year from the natal rising sign, with IANA-zone civil boundaries when `timezone_id` is supplied and fixed-offset fallback otherwise.
- `planetary-hours-v2` — twelve unequal daylight hours and twelve unequal night hours from explicit environment coordinates, using sunrise/sunset, local civil date, IANA-zone resolution when available, and the Chaldean order.
- `zodiacal-releasing-v2` — Fortune/Spirit releasing with the Valens same-sign Spirit start rule, idealized 360-day years / 30-day months, L1-L4 recursive units, and loosing-of-the-bond at L2-L4. Full L1/L2 schedules are emitted; L3/L4 are emitted for the active parent chain at `as_of`.

## Civil-time policy

`timezone_id` (for example `America/New_York`) is the preferred v3 civil-time input and is resolved with Python `zoneinfo`. The project pins `tzdata` as a fallback when a host does not provide system IANA data. A numeric `timezone_offset` remains supported as an explicit fixed-offset compatibility path.

The same precedence now applies to both static and timing artifacts. The engine does not infer a timezone name from latitude/longitude. Ambiguous local times during a backward clock transition require `timezone_fold=0` or `timezone_fold=1`; nonexistent local times during a forward transition fail closed. If both `timezone_id` and `timezone_offset` are supplied, the named IANA zone is authoritative and any supplied-offset mismatch is retained in provenance.

## Fail-closed rules

Unknown birth time is never replaced with an invented noon reading. BaZi can emit a partial date-derived result; exact-time-dependent Jyotish and natal timing artifacts return `input_insufficient` when required inputs are unavailable.

Dynamic timing requires explicit `as_of`; planetary hours additionally require a separate `timing_context` with latitude, longitude, and either `timezone_id` or `timezone_offset`. Unsupported, ambiguous, nonexistent, or geographically impossible states return an explicit failure status rather than fabricated coordinates.

The implementation does not fabricate event predictions, empirical personality validity, or claims that symbolic recurrence is independent evidence. New artifacts remain outside the legacy composite resonance score and identity-fingerprint spokes until an explicit migration defines how those surfaces should consume dependency-aware data.

## Adjacent historical/reflection boundary

The compatibility encoder map now includes `sumerian_me_ontology` as a historical/textual corpus reference, and `analysis-v1` can optionally return `sumerian-me-reflection-v1`. Neither is promoted into v3 static-signature convergence by this tranche. Historical attestation is not an independence family for personality evidence, and explicit reflection tags remain user-supplied/modern-interpretive context rather than a new v3 proof source.

### 2026-09-24 — R4 household/Atlas/Tarot integration

- Pytest collection baseline intentionally advanced from 490 tests / 68 files to **572 tests / 76 files** after merging the household composition contracts, expanded Atlas coverage, completed 78-card Tarot asset integrity checks, and associated regression suites.
- `esoteric_bridge` is explicitly classified as `project_authored_crosswalk`, remains in the `crosswalk_comparison` independence group, and is non-claim-eligible so project-authored correspondences cannot masquerade as independent evidence.
- The protected single-person calculation contract remains `analysis-v1`; household composition is additive and default-off for paid/public use.
