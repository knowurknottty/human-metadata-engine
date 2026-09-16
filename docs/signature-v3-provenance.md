# Signature v3 provenance register

This register covers source IDs introduced by the opt-in `signature-v3` static
and timing artifacts. It supplements `symbolic-systems-provenance.md`.

The register records computational conventions. It does not assert that
astrological timing systems are empirically predictive.

## Swiss Ephemeris references

- `SRC-SWISSEPH-SIDEREAL` — Swiss Ephemeris 2.10 sidereal-mode functions. The predefined mode table identifies Lahiri as `SE_SIDM_LAHIRI = 1` and Raman as `SE_SIDM_RAMAN = 3`; sidereal positions are calculated with the sidereal flag after selecting a mode.
- `SRC-SWISSEPH-PLANETS` — `swe_calc_ut()` geocentric planetary positions with explicit `SEFLG_SPEED` when speed/retrograde state is emitted.
- `SRC-SWISSEPH-SOLCROSS` — `swe_solcross_ut()` forward UT search for the Sun crossing a specified ecliptic longitude.
- `SRC-SWISSEPH-RISE-SET` — `swe_rise_trans()` sunrise/set computation from explicit geographic coordinates.

Primary implementation reference: Astrodienst, *Swiss Ephemeris 2.10 — Programming Interface*.

## Civil-time / timezone reference

- `SRC-IANA-TZDB` — Python `zoneinfo` (PEP 615) using the IANA Time Zone Database. Runtime requirements pin `tzdata==2026.4` as the cross-platform fallback when the host OS does not provide zone files.
- `timezone_id` is preferred when supplied. A numeric `timezone_offset` remains an explicit fixed-offset fallback for compatibility.
- Ambiguous local times require `timezone_fold=0` or `timezone_fold=1`; nonexistent local times in a forward clock transition fail closed.
- When both `timezone_id` and `timezone_offset` are supplied, `timezone_id` is authoritative for v2 timing and any mismatch is retained in timezone provenance.

## Jyotish conventions

- `SRC-JYOTISH-LAHIRI` — Lahiri ayanamsa as a named Swiss Ephemeris predefined sidereal mode.
- `SRC-JYOTISH-RAMAN` — B. V. Raman ayanamsa as a separate named Swiss Ephemeris predefined sidereal mode. It is never averaged with Lahiri.
- `SRC-JYOTISH-LUNAR-NODES` — Swiss Ephemeris distinguishes mean node (`SE_MEAN_NODE = 10`) and true node (`SE_TRUE_NODE = 11`). `jyotish-v2` records the selected convention and emits Ketu exactly 180 degrees opposite the selected ascending node.
- `SRC-JYOTISH-NAKSHATRA` — 27 equal nakshatra divisions of the selected sidereal zodiac, each divided into four padas.
- `SRC-JYOTISH-NAVAMSHA` — D9/Navamsha deterministic ninefold sign projection.
- `SRC-JYOTISH-DASAMSA` — D10/Dasamsa deterministic tenfold sign projection.
- `SRC-JYOTISH-VIMSHOTTARI` — fixed Ketu-through-Mercury 120-year Mahadasha sequence; birth balance is proportional to the unelapsed fraction of the Moon's selected-ayanamsa nakshatra.

## Western timing conventions

- `SRC-TIMING-TRANSITS` — project-authored v1 convention: tropical geocentric longitudes at explicit `as_of`, with conjunction, sextile, square, trine, and opposition contacts inside a fixed one-degree computational orb.
- `SRC-TIMING-SECONDARY-PROGRESSIONS` — project-authored day-for-year convention: elapsed days divided by 365.2425 produce symbolic ephemeris days after birth. v1 progresses planets only.
- `SRC-TIMING-SOLAR-ARC` — project-authored v1 convention: secondary-progressed Sun minus natal Sun is the arc; the same arc is added to natal planets, Ascendant, and Midheaven.
- `SRC-TIMING-SOLAR-RETURN` — exact tropical natal-Sun-longitude crossing with `swe_solcross_ut()`. v1 erects the return chart at stored birth coordinates; relocation is not silently assumed.
- `SRC-PROFECTIONS-WHOLE-SIGN` — Hellenistic annual-profection count: age zero begins in the rising sign/first place, then advances one whole sign per completed civil year; the traditional domicile ruler becomes Lord of the Year. v2 resolves the civil birthday through `timezone_id` when available and otherwise uses the explicit fixed offset.

## Zodiacal Releasing convention

- `SRC-ZODIACAL-RELEASING-VALENS` — Fortune/Spirit lot formulas reverse by sect. If Fortune and Spirit occupy the same sign, the Spirit *releasing start* advances one sign; the natal Spirit Lot coordinate is not rewritten.
- `SRC-ZODIACAL-RELEASING-360DAY` — the v2 reconstruction uses idealized 360-day L1 years and 30-day L2 months. L3 uses 2.5-day units and L4 uses 5-hour units, each exactly 1/12 of the corresponding unit above it.
- `SRC-ZODIACAL-RELEASING-LB` — after the first complete 12-sign circuit within an L2/L3/L4 parent, the next subperiod jumps to the sign opposite the parent sign, is flagged `loosing_of_bond`, and zodiacal sequence continues from there. The jump is not repeated a second time inside the same parent.
- v2 emits the full L1 and L2 schedule. L3 and L4 sibling schedules are emitted for the active parent chain at explicit `as_of`, preventing an unnecessarily huge all-life tree.

The period-number table remains: Aries 15, Taurus 8, Gemini 20, Cancer 25, Leo 19, Virgo 20, Libra 8, Scorpio 15, Sagittarius 12, Capricorn 27, Aquarius 30, Pisces 12.

## Planetary-hours convention

- `SRC-PLANETARY-HOURS-CHALDEAN` — seven-planet Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon. The first hour after sunrise is ruled by the weekday ruler; daylight and night are each divided into twelve equal temporal hours.
- v2 resolves the local civil date with IANA `timezone_id` when supplied before calculating the weekday ruler and local sunrise/sunset labels.

## Boundary policy

1. Alternative ayanamsas and node models are separate named conventions.
2. Dynamic artifacts require explicit `as_of`; the engine does not silently read the wall clock.
3. Planetary hours require separate environment/time context; birth place is not assumed to be current location.
4. Timing artifacts remain outside static-signature convergence.
5. Calendar normalizations are emitted per artifact. Vimshottari/secondary progressions retain their disclosed 365.2425-day normalization; Zodiacal Releasing v2 uses the distinct 360/30/2.5-day/5-hour reconstruction.
6. Calculated periods, contacts, or returns are coordinates in a symbolic system, not predictions of concrete events.
7. IANA zone rules are used only when an explicit `timezone_id` is supplied; the engine does not guess a zone name from coordinates.
