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

Only the first two are implemented in this tranche.

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
- `maya-classical-gmt-v1` — Long Count, Tzolk'in, Haab', Calendar Round, and Lord of Night under GMT 584283.

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