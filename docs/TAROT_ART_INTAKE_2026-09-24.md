# Tarot Art Intake — 2026-09-24

Status: **78/78 mapped and visually reviewed; versioned local deployment assets active with deterministic SVG fallback**

The Tarot feature now prefers the versioned local art deck in `webapp/static/assets/tarot/`. `webapp/static/tarot-art.js` retains the deterministic offline SVG renderer as the per-card error fallback. Draw mechanics and authored interpretations are unchanged.

## Candidate new art batch

The current Downloads inventory contains **78 recent PNG candidate card images** in the generation sequence beginning 2026-09-23 17:39 and ending 2026-09-24 01:42.

Observed dimensions:

- 74 images: 1024 × 1536
- 3 earlier images: 1086 × 1448

The sequential filename run previously had one confirmed hole, now recovered:

- recovered candidate slot: `image-gen-9(4).png`
- logical neighbors: `image-gen-8(4).png` → `image-gen-9(4).png` → `image-gen-10(4).png`
- recovered file dimensions: 1024 × 1536
- recovered SHA-256: `510ef44ba1d5d746f6341dd102b2a20b2f40810b78137ec2e4850ca0ab4af935`
- the full candidate set contains 78 unique file SHA-256 digests and all 78 files decode successfully

PNG/Spotlight metadata does not contain a reliable card title or generation prompt, so filenames alone are **not** sufficient to bind these images to the 78 canonical card IDs safely.

## Activation requirements

Do not replace the current Tarot art renderer until all of the following are true:

1. [x] exactly 78 candidate card assets are present and decode successfully;
2. [x] every asset is explicitly mapped to one canonical card ID from the current 78-card deck;
3. [x] the intake manifest contains a SHA-256 digest and dimensions for every file;
4. [x] duplicate-file and missing-asset-count checks pass;
5. [x] every mapped image is visually reviewed for the intended card;
6. [x] the application falls back to the deterministic SVG art if an asset is missing or fails validation.

Downloads remains an intake location, not a production asset path. Verified WebP derivatives are stored in `webapp/static/assets/tarot/`, named by canonical card ID, with the unified R4 `manifest.json` binding every deployed asset to its source PNG SHA-256 and deployed SHA-256.


Machine-readable intake manifest: `release/tarot-art-intake-2026-09-24.json`.

Focused regression: 83/83 passed after image-first integration. Isolated Headless Chrome 153 Atlas/browser QA also passed on the same worktree. Physical-device QA remains a separate release gate.
