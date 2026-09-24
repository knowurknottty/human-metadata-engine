# Inversion Tarot Art Status

Updated: 2026-09-23

The public Tarot reader remains a local, no-AI runtime. Card selection uses operating-system randomness and interpretation is project-authored. Visual artwork is a separate layer bound by the stable Major Arcana numeric index.

## Finished Library artwork

Major indices 0–12 have finished Inversion Tarot artwork sourced from the Human Meta Data Project Library and downloaded as original PNGs. The served site uses locally generated WebP derivatives. webapp/static/assets/tarot/manifest.json records the original filename and SHA-256 digest for every source.

The artwork series has evolving custom visual titles. Those titles are currently treated as artwork provenance, not as a rewrite of the reading engine archetype names. This prevents an intermediate naming draft from silently changing the interpretive contract.

## Remaining production

- Major Arcana XIII–XXI: 9 artworks
- Minor Arcana: 56 artworks
- Total remaining: 65 artworks

Until an artwork exists, the site uses the deterministic local SVG renderer. No remote image host or image-generation API is called by the public site.

## Completion rule

A card moves from fallback to finished art only when its source artwork is accepted, its source filename and SHA-256 are recorded, a local web derivative is checked in, the numeric binding is verified, and browser/fallback tests pass.

