# v1.0 release-candidate QA evidence

> **Scope note (2026-09-17):** the current Human Manual card-release candidate has fresh automated code, browser, download, privacy, Story-mode, and Sumerian-reflection evidence in Headless Chrome 153. The older physical-device evidence below remains useful but predates parts of this release; physical Android/iPhone and TalkBack/VoiceOver completion remains a separate open gate.

Original physical-device date: 2026-07-18 (America/Chicago)

Current automated release-candidate update: 2026-09-17

## Physical-device matrix

| Target | Detection evidence | Result |
| --- | --- | --- |
| Android / Moto G Power (2022) | `adb devices -l` returned authorized serial `ZY22FSQQKZ`, model `moto_g_power_2022`; Android 12 / SDK 31 / build `S3RQS32.20-42-10-9-12`; Chrome `150.0.7871.124`. | **PARTIAL PASS.** Exact birth, name-only, unknown-time, ambiguity, all six surfaces, portrait/landscape, Explorer/Research, selection/cross-highlighting, fallback/native fullscreen entry/exit, unavailable states, reset, 44px controls, Living Pattern interactions, and Android print preview passed. A real saved/opened Markdown file and the share flow remain open. |
| TalkBack | TalkBack was briefly enabled only to inspect device state, then disabled at the user's direction. Final settings: `enabled_accessibility_services=null`, `accessibility_enabled=0`, no bound service. | **UNVERIFIED.** No TalkBack completion is claimed; it must not be re-enabled without explicit user approval. |
| iPhone Safari | `devicectl` restored the paired physical iPhone 17 Pro `WiFightIt`, iOS 26.5.2 build `23F84`; tunnel connected, developer mode enabled, and Safari launched the LAN test URL. | **PARTIAL.** Connection/launch only. The required Safari flows were not completed. |
| VoiceOver | VoiceOver was not enabled. | **UNVERIFIED.** No VoiceOver completion is claimed; it must not be enabled without explicit user approval. |

Both physical connections were established during this QA run, but neither
platform completed the entire mandatory matrix and neither screen reader was
tested. Browser automation below does not substitute for the remaining physical
flows. The Android USB/ADB connection was absent at the end of the run.

### Final automated release-gate rerun

On the final Human Manual release-candidate tree, the verification gate produced:

- `.venv/bin/python -m pytest -q` — **383 passed, 100 subtests passed**.
- `.venv/bin/python tools/run_tests.py --quiet` — **57 test files; 0 failures; `ALL_TESTS_PASS`**.
- `.venv/bin/python tools/validate_contracts.py` — **`PUBLIC_CONTRACTS_VALID`** and **`SYSTEM_RESULT_V2_SCHEMA_VALID`**.
- `.venv/bin/python -m compileall -q src webapp` — exit 0, no output.
- `node --check` over every `webapp/static/*.js` file and `tools/capture_atlas_baselines.mjs` — exit 0.
- `git diff --check` — exit 0, no output.
- Deterministic storytelling contracts cover the versioned prose lexicon, byte-stable replay, evidence-ID preservation, zero public remote-model path, richer Story prose, and Agent Handoff export.

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
  avoids the known asynchronous handoff and is covered by HTTP tests. Its
  physical result is not yet proven: the save/open retest was interrupted when
  the USB/ADB connection dropped, so it remains an open release defect until a
  real `.md` file is saved and opened.
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

Final release command (with `HME_PYTHON_BIN` pointed at the repository's verified `.venv` interpreter):

```bash
HME_RUN_NETWORK_QA=1 HME_QA_PORT=8900 HME_QA_DEBUG_PORT=9440 node tools/capture_atlas_baselines.mjs
```

Environment: Headless Chrome 153.0.0.0 on macOS, device scale factor 1. Mobile checks use Chrome device-metrics emulation; they are browser evidence, not a substitute for physical-device QA.

| Flow/check | Result |
| --- | --- |
| Human Manual / Inversion Labs public identity | PASS |
| Privacy/trust disclosure before the first PII field | PASS |
| First-run horizontal overflow at 320/360/390/412/768 CSS px | PASS |
| Exact birth via real form/API with explicit IANA zone and coordinates | PASS |
| Name-only via real form/API | PASS |
| Unknown exact time | PASS — astrology remains, Human Design is explicitly unavailable, summary says Date only |
| Live ambiguous location (`Springfield`, Open-Meteo) | PASS — multiple keyboard-operable choices rendered |
| Hostile HTML-like name | PASS — rejected; no inserted element |
| Six surface count and unique element IDs | PASS |
| Constellation, astrology, center/gate, Tree, numerology, fingerprint selection | PASS — one current selection and inspector detail each |
| Chrome accessibility tree | PASS — 174 named buttons; calculated root, planets, centers, and gates exposed by name |
| Repeated Explorer/Research switching | PASS — presentation changes with zero fetch calls |
| Story mode | PASS — deterministic local Story renders with zero additional fetch calls |
| Post-report bring-your-own-agent handoff prompt | PASS |
| Fullscreen fallback | PASS — opens, Escape closes, focus returns to the control |
| Result horizontal overflow at 320/360/390/412/768 CSS px | PASS |
| Print media and print action | PASS |
| Markdown download | PASS — one Human Manual `.md` file containing `## Agent Handoff` and `human-manual-agent-handoff-v1` |
| Repeated exact fixture | PASS — Atlas DOM is byte-identical |
| Human Capacity / Sumerian me reflection | PASS — exact explicit tags, three-layer boundary, no score/rank, 390px no-overflow |
| Exact-birth → name-only replacement | PASS — planet/center marks removed; unavailable panels replace exact-birth surfaces |
| Start new analysis | PASS — prior dashboard becomes hidden |

The machine-readable hashes, widths, scroll positions, exact fixtures, and individual checks are in `docs/assets/ui-v10/manifest.json`.

## Manual screenshot inspection

The 14 sanitized PNGs in the final manifest were inspected for visible clipping, missing glyph boxes, misleading stale data, and unavailable-state clarity. They cover the Human Manual first run, pre-input privacy boundary, exact-birth workspace, focused astronomy/bodygraph/constellation surfaces, Research mode, name-only unavailable state, and the Sumerian reflection on desktop and 390-pixel mobile. Fixtures are synthetic; no real user report is committed.

This inspection is evidence for the captured Chrome/font environment only. It
does not prove zodiac, planetary, I Ching, or Tree-of-Life font coverage on the
unavailable physical Android/iPhone targets.

## Release implication

The automated public-demo/card-pilot gate is green for the current Human Manual candidate. Physical Android/iPhone and TalkBack/VoiceOver completion remains open and must not be described as verified. Therefore this evidence supports a bounded public demo/card rollout, not a claim that every general-consumer physical-device gate in `RELEASE_GATES.md` is closed.

## Post-v1.0 Sumerian reflection delta

The current release candidate includes an opt-in observation/tag interface and three-layer result view. Static/frontend/server contracts verify explicit opt-in, user-selected category tags, historical/modern boundaries, disabled-by-default behavior, raw-observation redaction, and absence of reflection scoring.

A sanitized synthetic browser fixture exercises the same public UI path with `crafts_and_technical_practice` and `knowledge_and_judgment`. Headless Chrome 153 rendered exactly two expandable matches, the labels **Personal evidence → Modern analytical bridge → Historical corpus**, the explicit historical-personal boundary statement, and no horizontal overflow at 390 CSS pixels. The mobile capture is fully readable. The desktop subsection capture is functionally complete but its heading is partially under the sticky report bars because the baseline helper scrolls the subsection flush to the viewport; this is capture framing, not hidden result content or horizontal overflow.

Final reflection capture hashes: `desktop-sumerian-reflection.png` = `86b8945e1703439b0e97a17af323297a96194bd2bd92a312d451cb73688ea920`; `mobile-sumerian-reflection.png` = `7b0e5a6edc1f1fe092c7f93ee62bba2fa1f73928603c4a9a49b45140f3677e30`. This browser evidence does **not** replace TalkBack/VoiceOver or physical Android/iPhone QA for the new controls.
