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

The committed set covers desktop overview, astrology, bodygraph, constellation,
Research mode, name-only unavailable state, the Sumerian me reflection result,
and 390 × 844 mobile overview, astrology, bodygraph, and reflection result.
Desktop captures are 1440 × 1000 CSS pixels at device scale factor 1.

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

The current baseline was regenerated with Headless Chrome 153. The reflection hashes are `0c8251985a8bfb84ae85affabc3f99d63c8ad6c01d8af1e5bb5283270ef1b681` (desktop) and `e252b0d8b18940756cf6ced6f984661b9959ef867a57ca1585fea803d5431591` (390 × 844 mobile). The public label uses text-safe **Sumerian me** wording because the U+12228 cuneiform glyph is not reliably available in browser font stacks; `𒈨` remains preserved in the historical ontology/provenance data. Physical-device and screen-reader verification remains a separate gate.

The harness accepts `HME_QA_PORT` and `HME_QA_DEBUG_PORT` so baseline capture does not require ports reserved by other local CAPT services.
