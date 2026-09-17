# v1.0 visual regression baselines

The sanitized baseline set lives in `docs/assets/ui-v10/`. It contains no user
report or personal fixture. The exact-birth fixture is deliberately synthetic:
`Atlas Verification Fixture`, 1985-06-15 10:30, `America/Chicago`, 41.8781,
-87.6298. The name-only fixture is `Atlas Name-Only Fixture`.

Capture with:

```bash
node tools/capture_atlas_baselines.mjs
```

The dependency-free script starts the local application, launches the installed
Chrome in a temporary headless profile, submits both fixtures through the real
form/API path, and records browser identity, viewport, mobile emulation state,
and SHA-256 for every PNG in `manifest.json`. The temporary profile is removed.

The committed set contains 14 captures covering the Human Manual first run, the pre-input privacy boundary, desktop overview/astrology/bodygraph/constellation/Research mode, name-only unavailable state, the Sumerian me reflection result, and 390 × 844 mobile first-run/overview/astrology/bodygraph/reflection views. Desktop captures are 1440 × 1000 CSS pixels at device scale factor 1.

SHA equality is useful only with the same committed browser build, OS font
stack, and rendering environment. CI should first regenerate in a pinned Chrome
container, compare per-image hashes or a small bounded pixel threshold, and
publish diff artifacts on failure. This release does not add pixel-diff CI
because the repository has no pinned browser/font image; treating cross-platform
antialiasing changes as product regressions would be unreliable.

Set `HME_RUN_NETWORK_QA=1` to add a live Open-Meteo ambiguous-location browser
check. It is intentionally optional for baseline regeneration because it depends
on an external provider; release verification runs it separately.

## Reflection UI baseline evidence

The Human Capacity / Sumerian me Reflection is now covered by a sanitized synthetic observation/tag fixture in the baseline harness. The fixture explicitly selects `crafts_and_technical_practice` and `knowledge_and_judgment`; the browser verifies exactly two matches, the three epistemic-layer labels, the expanded modern/historical separation, the historical-personal boundary copy, and no horizontal overflow at 390 CSS pixels.

The current baseline was regenerated with Headless Chrome 153. The reflection hashes are `86b8945e1703439b0e97a17af323297a96194bd2bd92a312d451cb73688ea920` (desktop) and `7b0e5a6edc1f1fe092c7f93ee62bba2fa1f73928603c4a9a49b45140f3677e30` (390 × 844 mobile). The public label uses text-safe **Sumerian me** wording because the U+12228 cuneiform glyph is not reliably available in browser font stacks; `𒈨` remains preserved in the historical ontology/provenance data. Physical-device and screen-reader verification remains a separate gate.

The harness accepts `HME_QA_PORT` and `HME_QA_DEBUG_PORT` so baseline capture does not require ports reserved by other local CAPT services.

## Human Manual card-release baseline

The 2026-09-17 card-release candidate adds first-run baseline evidence for the canonical public identity and trust boundary. `desktop-first-run.png` is SHA-256 `b47e1fb36fce315e86ef332c07ef09063db22291417fa32cfc232432598c5b5a`; `mobile-first-run.png` is `0a1b968b14bdb1c3b97549b9bfda83410da145d70e77e0713a35ceafcb9b8b4d`; `mobile-privacy-before-input.png` is `c4fb08f5b7cb91a2c6e199a62a38d73184967fd4bde9f58e40d8c082440488e9`.

The same browser run verifies first-run and result-page horizontal overflow at 320/360/390/412/768 CSS pixels, privacy/trust disclosure before PII, deterministic Story mode with zero additional fetch calls, the visible post-report bring-your-own-agent prompt, and an actual Markdown download containing the Agent Handoff contract. Exact checks and all 14 capture hashes live in `manifest.json`.
