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
Research mode, name-only unavailable state, and 390 × 844 mobile overview,
astrology, and bodygraph. Desktop captures are 1440 × 1000 CSS pixels at device
scale factor 1.

SHA equality is useful only with the same committed browser build, OS font
stack, and rendering environment. CI should first regenerate in a pinned Chrome
container, compare per-image hashes or a small bounded pixel threshold, and
publish diff artifacts on failure. This release does not add pixel-diff CI
because the repository has no pinned browser/font image; treating cross-platform
antialiasing changes as product regressions would be unreliable.

Set `HME_RUN_NETWORK_QA=1` to add a live Open-Meteo ambiguous-location browser
check. It is intentionally optional for baseline regeneration because it depends
on an external provider; release verification runs it separately.
