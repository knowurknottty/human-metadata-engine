# The Human Manual Card-Launch Design

**Date:** 2026-09-17

## Product identity

The public product is **The Human Manual, for and by Humans**, an Inversion Labs project. “Human Metadata” remains an internal engineering/repository term only and must not appear in public navigation, hero copy, forms, report headings, downloadable filenames, SEO metadata, or user-facing status text.

The visible brand uses the canonical Inversion Labs gold infinite-key artwork supplied by the project owner. The existing Identity Resonance visual grammar remains the calculation/workspace shell; branding is layered over it rather than replacing the proven Atlas interactions.

## Public promise

The first viewport must answer, before requesting personal details: what the tool does, why a person might care, what kind of inputs unlock which calculations, and what happens to those inputs. The language must work for skeptical, technical, spiritual, privacy-sensitive, and casual visitors without requiring any one worldview.

Primary framing: humans have invented many systems for compressing aspects of identity and experience into symbols, numbers, maps, cycles, archetypes, and narratives. The Human Manual computes those systems separately, preserves provenance and limitations, then converges them without pretending symbolic interpretation is scientific fact.

## Privacy and agency

Privacy copy must be concrete rather than philosophical. The interface must distinguish browser-only state, server calculations, optional fields, downloaded artifacts, and any network-dependent feature. No field may imply that omission is suspicious or that maximum disclosure is required for every result.

The public experience must not make the “privacy is already gone” argument. The product should demonstrate the inversion instead: ask only for data needed for requested calculations, make optionality explicit, expose provenance, avoid hidden enrichment, and let users download/delete/reset their local session state.

## Deterministic storytelling

The public report must not require an LLM to feel authored. Remote Mythic narration is removed from the public path. The deterministic narrative system gains an extensible vocabulary/composition layer with:

- domain-specific phrase banks keyed by evidence/system/epistemic layer;
- multiple clause and paragraph grammars rather than synonym swapping;
- anti-repetition and recent-phrase suppression;
- controlled tone registers (plain, lyrical, research) that preserve the same underlying claims;
- deterministic seeded selection so identical validated inputs + versions yield identical prose;
- evidence-aware qualifiers and uncertainty language;
- collision tests preventing contradictory or inflated claims;
- stable extension points so each model cohort can add vocabulary without modifying calculation code.

## Export contract

The primary downloadable artifact is an agent-ready Markdown Human Manual. It must contain structured source data, calculated outputs, provenance, epistemic labels, deterministic narrative sections, limitations, and a short handoff prompt telling a user how to ask any preferred model to reinterpret the file without treating symbolic claims as facts.

The site may use playful copy around this export, including the project voice (“cool fucking story bro”) in a clearly optional/secondary place, but first-run trust and privacy language must remain plain and respectful.

## Release convergence

The release branch starts from `feature/sumerian-me-reflection-r1` and merges current `origin/main`, preserving the richer timing/Sumerian backend plus the newer Identity Resonance shell. The merge must keep both `tarot-radio-fix.css` and `identity-resonance-shell.css` unless tests prove one obsolete.

PR #9 merges to its intended `design/true-human-design-engine` base. PR #11 remains unmerged unless rebased/current-main tests pass; a failing draft is not a launch dependency.

## Release gates

Required before Netlify publication: full pytest/canonical runner, contract validators, JS syntax, browser desktop/mobile captures, first-run/privacy copy assertions, Markdown export verification, no public “Human Metadata” strings, no public remote-Mythic controls, no horizontal overflow, and live verification of `https://inversionlabs-hmd.netlify.app` after deploy.

After live verification, run the first critique cohort only: DeepSeek v4 Flash 0713 under CAPT, 11 vessels in one cohort. Stop after producing its review so the owner can critique and decide which changes to apply before the next model.
