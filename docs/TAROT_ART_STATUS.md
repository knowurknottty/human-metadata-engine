# Inversion Tarot Art Status

Updated: 2026-09-24

All 78 runtime cards now have local Inversion Tarot artwork: 22 Major Arcana and all 56 Minor Arcana. The 13 Major assets already published by R4 retain their existing public paths; the remaining 65 assets were added from the completed 2026-09-24 Library intake.

`webapp/static/assets/tarot/manifest.json` binds every runtime card ID to source filename/SHA-256 and served asset/SHA-256. Artwork titles remain provenance unless separately frozen as interpretive canon; the authored reading semantics are unchanged.

`webapp/static/tarot-art.js` resolves local artwork by runtime card ID and falls back to the deterministic local SVG renderer if an image is missing or fails to load. No remote image host or image-generation API is called by the public site.
