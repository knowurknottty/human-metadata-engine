# v1.0 release-candidate QA evidence

Date: 2026-07-18 (America/Chicago)

## Physical-device matrix

| Target | Detection evidence | Result |
| --- | --- | --- |
| Android / Moto G Power (2022) | `adb devices -l` returned authorized serial `ZY22FSQQKZ`, model `moto_g_power_2022`; Android 12 / SDK 31 / build `S3RQS32.20-42-10-9-12`; Chrome `150.0.7871.124`. | **PARTIAL PASS.** Exact birth, name-only, unknown-time, ambiguity, all six surfaces, portrait/landscape, Explorer/Research, selection/cross-highlighting, fallback/native fullscreen entry/exit, unavailable states, reset, 44px controls, Living Pattern interactions, and Android print preview passed. A real saved/opened Markdown file and the share flow remain open. |
| TalkBack | TalkBack was briefly enabled only to inspect device state, then disabled at the user's direction. Final settings: `enabled_accessibility_services=null`, `accessibility_enabled=0`, no bound service. | **UNVERIFIED.** No TalkBack completion is claimed; it must not be re-enabled without explicit user approval. |
| iPhone Safari | `devicectl` restored the paired physical iPhone 17 Pro `WiFightIt`, iOS 26.5.2 build `23F84`; tunnel connected, developer mode enabled, and Safari launched the LAN test URL. | **PARTIAL.** Connection/launch only. The required Safari flows were not completed. |
| VoiceOver | VoiceOver was not enabled. | **UNVERIFIED.** No VoiceOver completion is claimed; it must not be enabled without explicit user approval. |

Physical connections now exist, but neither platform completed the entire
mandatory matrix and neither screen reader was tested. Browser automation below
does not substitute for the remaining physical flows.

### Final automated release-gate rerun

After the last provenance, verifier, narrative wording, and stale-highlight
patches, the exact candidate checkout produced:

- `.venv/bin/python -m pytest -q` — **294 passed, 95 subtests passed**.
- `.venv/bin/python -m pytest --collect-only -q` — **294 tests collected**.
- `.venv/bin/python tools/run_tests.py --quiet` — **42 test files; 0 failures;
  `ALL_TESTS_PASS`**.
- `.venv/bin/python tools/validate_contracts.py` —
  **`PUBLIC_CONTRACTS_VALID`**.
- `.venv/bin/python -m compileall -q src webapp` — exit 0, no output.
- `node --check webapp/static/app.js` and `node --check
  webapp/static/atlas.js` — exit 0, no output.
- `git diff --check` — exit 0, no output.
- Dedicated synthesis/narrative suite — **32 passed**.

### Physical Android defect evidence

- The user-provided `1982-2-4` value was reproducibly collapsed to `1982-24` by
  input normalization. The client now preserves typed separators, accepts one-
  or two-digit month/day input, and canonicalizes to `1982-02-04` on blur.
- Several mode/panel/fingerprint controls measured 33–40 CSS pixels. The focused
  CSS patch raises these interactive targets to at least 44 CSS pixels; physical
  retest measured a 44-pixel minimum.
- Blob, direct attachment POST, and asynchronous token handoff paths were not
  reliable in Android Chrome when “Ask where to save files” was enabled. The
  current user-initiated form POST → `303` → short-lived GET attachment path
  preserves the tap activation and is covered by HTTP tests. The physical
  save/open retest was interrupted when the USB/ADB connection dropped, so it
  remains an open release defect until a real `.md` file is saved and opened.
- Android portrait viewport was 411×766 CSS pixels with no document overflow;
  landscape was 822×331 with no document overflow. All six panels remained
  available in the exact-birth fixture.

### Physical Living Pattern evidence

- Exact fixture: `1982-02-04`, `01:42`, Evanston, Wyoming. The six Atlas
  surfaces and the central **Initiation–Analysis Pattern** rendered without
  document overflow in portrait or landscape.
- Plain, Mythic, and Research modes retained the same sentence, claim, and
  evidence identifiers. Only wording and disclosure changed.
- On the physically tested build, sentence → Atlas exposed five evidence
  references, six target identifiers, and 44 linked marks; Atlas → sentence
  highlighted 21 narrative sentences for the astrology surface. Review then
  found that the two-part central title cited only the primary motif. The claim
  now cites both named motifs (10 evidence and 10 target identifiers in the exact
  fixture), and automated provenance tests pass. That expanded physical
  cross-highlight count remains pending because the USB/ADB connection dropped.
- The Android accessibility tree exposed 18 narrative buttons with meaningful
  sentence, confidence, and evidence names. This verifies platform semantics,
  not TalkBack speech or focus behavior.
- Name-only produced an explicitly partial 15-sentence narrative; unknown-time
  produced an explicitly partial 16-sentence narrative with Human Design
  unavailable. Both retained 44px-or-larger visible controls and zero document
  overflow.
- `Start a new analysis` removed the prior dashboard DOM rather than leaving
  stale narrative or Atlas marks.
- Physical screenshots were captured only as local QA artifacts because the
  exact fixture contains user-supplied personal data; they are intentionally not
  included in the repository's sanitized public screenshot set.

## Automated browser matrix

Command:

```bash
HME_RUN_NETWORK_QA=1 node tools/capture_atlas_baselines.mjs
```

Environment: Headless Chrome 150.0.0.0 on macOS, device scale factor 1. The
390 × 844 and other narrow-width checks use Chrome mobile metrics emulation.

| Flow/check | Result |
| --- | --- |
| Exact birth via real form/API with explicit IANA zone and coordinates | PASS |
| Name-only via real form/API | PASS |
| Unknown exact time | PASS — astrology remains, Human Design is explicitly unavailable, summary says Date only |
| Live ambiguous location (`Springfield`, Open-Meteo) | PASS — multiple keyboard-operable choices rendered |
| Hostile HTML-like name | PASS — rejected; no inserted element |
| Six surface count | PASS |
| Duplicate element IDs | PASS — none in the rendered exact-birth Atlas/report DOM |
| Constellation, astrology, center/gate, Tree, numerology, fingerprint selection | PASS — one current selection and inspector detail each |
| Chrome accessibility tree | PASS — 169 named buttons; calculated root, planets, centers, and gates exposed by name |
| Repeated Explorer/Research switching | PASS — presentation changes with zero fetch calls |
| Fullscreen fallback | PASS — opens, Escape closes, focus returns to the control |
| Horizontal overflow at 320/360/390/412/768 CSS px | PASS |
| Print media | PASS — gate index and Research text/provenance visible; inspector hidden |
| Print action | PASS |
| Markdown download | PASS — one `.md` file with expected report heading |
| Repeated exact fixture | PASS — Atlas DOM is byte-identical |
| Exact-birth → name-only replacement | PASS — planet/center marks removed; at least two unavailable panels |
| Start new analysis | PASS — prior dashboard becomes hidden |

The machine-readable capture hashes, widths, scroll positions, and individual
selection results are in `docs/assets/ui-v10/manifest.json`.

## Manual screenshot inspection

The nine committed sanitized PNGs were inspected for visible clipping, missing
glyph boxes, misleading stale data, and unavailable-state clarity. The focused
desktop and 390-pixel captures show the constellation, astrology symbols,
center/channel diagram, gate index, Research mode, and name-only unavailable
state. No user or personal-report fixture is present.

This inspection is evidence for the captured Chrome/font environment only. It
does not prove zodiac, planetary, I Ching, or Tree-of-Life font coverage on the
unavailable physical Android/iPhone targets.

## Release implication

Automated and static evidence is green, but the explicit physical Android,
TalkBack, iPhone Safari, and VoiceOver release gates in `RELEASE_GATES.md` are
open. The defensible public-release status is **NOT READY** until those required
device gates pass. The deterministic Narrative Synthesis layer also requires
its live physical/mobile interaction rerun. The local implementation remains a
release candidate with the documented v1.1 topology boundary.
