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
- `SRC-PROFECTIONS-WHOLE-SIGN` — Hellenistic annual-profection count: age zero begins in the rising sign/first place, then advances one whole sign per completed year; the traditional domicile ruler becomes Lord of the Year. v1 uses the completed civil birthday under the supplied fixed UTC offset.
- `SRC-ZODIACAL-RELEASING-VALENS` — Level-1 releasing from Fortune or Spirit in zodiacal order. Sign periods: Aries 15, Taurus 8, Gemini 20, Cancer 25, Leo 19, Virgo 20, Libra 8, Scorpio 15, Sagittarius 12, Capricorn 27, Aquarius 30, Pisces 12 years. Day formula: Fortune = Asc + Moon - Sun, Spirit = Asc + Sun - Moon; formulas reverse by night. v1 determines sect from the Sun's true astronomical altitude and does not emit L2-L4 or loosing-of-the-bond. The period table/basic mechanics follow Vettius Valens as summarized in Chris Brennan's Astrodienst article “Annual Profections, Lots, and Zodiacal Releasing.”

## Planetary-hours convention

- `SRC-PLANETARY-HOURS-CHALDEAN` — seven-planet Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon. The first hour after sunrise is ruled by the weekday ruler; daylight and night are each divided into twelve equal temporal hours.

## Boundary policy

1. Alternative ayanamsas and node models are separate named conventions.
2. Dynamic artifacts require explicit `as_of`; the engine does not silently read the wall clock.
3. Planetary hours require separate environment/time context; birth place is not assumed to be current location.
4. Timing artifacts remain outside static-signature convergence.
5. Calendar normalizations such as 365.2425 days are emitted in results and are not described as universal historical consensus.
6. Calculated periods, contacts, or returns are coordinates in a symbolic system, not predictions of concrete events.
7. v1 timing contexts use the supplied numeric UTC offset as a fixed offset. IANA time-zone databases, historical offset changes, and daylight-saving transitions are not inferred or reconstructed.
