# The Human Manual Card-Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: execute sequentially through CAPT; do not parallelize release edits or model cohorts.

**Goal:** Ship a trustworthy, branded, deterministic-first Human Manual release at the existing Netlify URL.

**Architecture:** Converge the richer feature branch with current main, retain the Identity Resonance workspace, replace public Human Metadata naming with Human Manual/Inversion Labs identity, add an extensible deterministic prose layer, remove public remote-LLM narration, harden export/privacy UX, then verify and deploy.

**Tech Stack:** Python, static HTML/CSS/JS, pytest, headless Chrome, Netlify CLI, CAPT Node/harness.

**Spec:** `docs/superpowers/specs/2026-09-17-human-manual-card-launch-design.md`

## Global constraints

- Public name: **The Human Manual, for and by Humans**.
- Public brand: canonical Inversion Labs infinite-key identity.
- “Human Metadata” is internal-only.
- No public remote-LLM narration dependency.
- Deterministic output remains evidence/provenance bound.
- Identical validated input + version must produce identical narrative output.
- Cohorts run sequentially; first external review is DeepSeek v4 Flash 0713 with 11 vessels.

---
### Task 1: Converge branches and release docs

**Files:** merge conflicts in `README.md`, `webapp/static/index.html`; create spec/plan docs.

- [ ] Preserve current-main Identity Resonance shell and feature-branch timing/Sumerian functionality.
- [ ] Keep both relevant CSS layers unless tests show redundancy.
- [ ] Resolve README to current release truth.
- [ ] Run baseline tests after merge resolution.
- [ ] Commit the convergence/spec checkpoint.

### Task 2: Public identity, logo, and first-run trust

**Files:** `webapp/static/index.html`, `webapp/static/identity-resonance-shell.css`, brand assets, frontend contract tests.

- [ ] Add failing assertions for Human Manual title, Inversion Labs identity, privacy/trust disclosure, and absence of public “Human Metadata”.
- [ ] Copy canonical supplied brand assets into a public asset directory with stable filenames.
- [ ] Rewrite SEO/title/header/hero/form framing around The Human Manual.
- [ ] Add explicit plain-language local/server/optional-data disclosure before sensitive inputs.
- [ ] Verify desktop/mobile first viewport and accessibility labels.
### Task 3: Deterministic narrative vocabulary engine

**Files:** existing narrative modules plus a focused lexicon/composition module and narrative tests.

- [ ] Add failing tests for deterministic seeded prose, register selection, anti-repetition, evidence-bound qualifiers, and no remote-model requirement.
- [ ] Introduce a focused vocabulary/composition layer consumed by the existing synthesis pipeline.
- [ ] Seed substantial phrase banks across structure, agency, discernment, tension, transformation, relation, craft, knowledge, timing, uncertainty, and synthesis domains.
- [ ] Preserve provenance/epistemic labels and forbid new factual claims from vocabulary variation.
- [ ] Expose plain, lyrical, and research deterministic registers with identical underlying claims.
- [ ] Run focused and full narrative tests.

### Task 4: Agent-ready Markdown and public LLM removal

**Files:** report/export code, browser UI, tests, docs.

- [ ] Add failing tests for Human Manual Markdown filename/content and agent handoff block.
- [ ] Remove public Mythic/remote-model controls while retaining deterministic plain/lyrical/research presentation.
- [ ] Ensure exported Markdown contains structured inputs/results/provenance/limitations and a safe reinterpretation prompt.
- [ ] Verify no API key or remote-provider language appears in first-run/public report UI.

### Task 5: Browser/mobile dogfood and WebMCP surface

**Files:** browser harness, optional `webmcp.js`, QA docs/baselines.

- [ ] Extend browser automation around card-scan first-run flow, privacy disclosure, form progression, report, and Markdown download.
- [ ] Register read/navigate/download-oriented imperative WebMCP tools only where they map to real visible actions; feature-detect and fail silently when unsupported.
- [ ] Capture desktop and 390px mobile screenshots and inspect them visually.
- [ ] Record remaining physical-device/screen-reader risks without overstating coverage.

### Task 6: Release verification, merge, push, deploy

**Files:** release docs and deploy configuration only if evidence requires changes.

- [ ] Run full pytest, canonical test runner, contract validators, Python compile, JS syntax, and `git diff --check`.
- [ ] Audit public strings for internal “Human Metadata” naming and remote-model language.
- [ ] Commit exact intended file set and verify clean worktree.
- [ ] Push release branch, merge to `main` only after green verification, and independently verify remote SHA.
- [ ] Deploy the verified commit to the existing Netlify site and verify HTTP/security headers plus desktop/mobile live screenshots at `https://inversionlabs-hmd.netlify.app`.

### Task 7: First sequential CAPT critique cohort

- [ ] Resolve the actual CAPT provider identifier for DeepSeek v4 Flash 0713; do not invent it.
- [ ] Run one cohort with 11 vessels against the deployed site, source, test evidence, privacy/trust copy, deterministic narrative architecture, and release goals.
- [ ] Require each vessel to identify concrete defects, language gaps, storytelling/vocabulary expansion opportunities, and launch risks.
- [ ] Converge the 11 vessel outputs without applying their suggestions automatically.
- [ ] Stop and present the DeepSeek critique for owner review before any DeepSeek 4.1, Gemini, Union Alpha, GLM, or Qwen cohort runs.
