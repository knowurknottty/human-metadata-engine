# Signature v3 research contract

`signature-v3` is an opt-in research composition layer. The public API remains
`analysis-v1`, the compatibility engine remains `signature-v2`, and the report
contract remains `report-v1` until a separate public migration is reviewed.

## Why v3 exists

The older encoder map mixes static calculations, symbolic correspondences,
assessments, and future timing work in one flat namespace. v3 instead emits
versioned `system-result-v2` artifacts with explicit provenance and dependency
semantics.

Each system result names its system/version, tradition, computational
convention, artifact class, epistemic class, input dependencies, dependency
roots, sensitivity, status, calculation payload, interpretation payload, source
IDs, licensing/dependency notes, and limitations.

## Artifact classes

- `static_signature` — stable calculations from a frozen subject input.
- `timing` — time-varying calculations derived from a frozen natal signature.
- `divination_session` — session/event artifacts with explicit casting entropy.
- `assessment` — user-supplied or instrument-derived assessment data.
- `environment` — place/orientation/context traditions.
- `biometric` — explicitly supplied physiological or genetic observations.

Only the first two are implemented in this tranche.

## Independence policy

A system count is a lens count, not an evidence count. Raw dependency roots are
preserved for provenance, then collapsed into independence families. For
example, `birth_date` and `birth_instant` both belong to the `birth` family, so
BaZi, Jyotish, Classical Maya, and Vimshottari do not become four independent
confirmations merely because four traditions use the same birth data.

Timing artifacts are excluded from static-signature convergence entirely.
Repeated symbolic motifs may be reported as symbolic recurrence, but they must
not be relabeled as empirical support.

## Implemented v3 systems

- `bazi-v1` — Four Pillars, Day Master, hidden stems, Ten Gods, and structural
  Five-Phase distribution under disclosed Li Chun/Jie/civil-time conventions.
  With unknown birth time, it preserves date-derived pillars, leaves the hour
  pillar null, and withholds year/month only when that local date crosses a
  relevant solar-term boundary.
- `jyotish-v1` — Lahiri sidereal planets/houses, 27 nakshatras and padas,
  D9/Navamsha, and D10/Dasamsa. It requests Swiss Ephemeris speed explicitly so
  retrograde labels are calculated rather than defaulting false.
- `maya-classical-gmt-v1` — Long Count, Tzolk'in, Haab', Calendar Round, and
  Lord of Night under GMT 584283; modern Dreamspell remains separate.
- `vimshottari-v1` — separate timing artifact computing the birth balance and
  Mahadasha boundaries under a disclosed 365.2425-day year convention.

## Fail-closed rules

Unknown birth time is never replaced with an invented noon reading. BaZi v1 can
emit a partial date-derived result with an explicit null hour pillar and partial
Five-Phase basis. Jyotish v1 and Vimshottari v1 return `input_insufficient` when
exact-time-dependent coordinates are unavailable. Missing required inputs return
`input_insufficient`; unsupported calculation states return `unavailable`.

The implementation does not fabricate Day-Master strength percentages, event
predictions, or empirical personality validity. New artifacts remain outside the
legacy composite resonance score and identity-fingerprint spokes until an
explicit migration defines how those surfaces should consume dependency-aware
data.
