# Human Metadata Engine

A provenance-aware identity metadata architecture that encodes humans, aliases, projects, personas, and symbolic identities into a structured graph.

## What This Is

This engine computes multiple symbolic, linguistic, semantic, temporal, and graph-based signatures for identity strings. It treats numerology as one encoder among many — not the authority.

## Core Principle

> "What lenses describe this identity?"  
> not:  
> "What is this person?"

That distinction keeps the system powerful without becoming delusional, invasive, or overconfident.

## Components

### Pythagorean Encoder (`src/encoders/pythagorean.py`)

Implements the standard Pythagorean letter-to-number mapping:

```
1: A J S    4: D M V    7: G P Y
2: B K T    5: E N W    8: H Q Z
3: C L U    6: F O X    9: I R
```

Produces:
- Expression number (all letters)
- Soul Urge number (vowels only)
- Personality number (consonants only)
- Balance number (initials)
- Hidden Passion (most frequent value)
- Karmic Lessons (missing numbers 1-9)
- Intensity table
- Master number preservation (11, 22, 33)

### Identity Graph (`output/identity_graph.json`)

Nodes represent identities (human, alias, handle, project, persona).  
Edges represent relationships (created_by, uses_alias, symbolically_resonates_with).

Each edge includes:
- Confidence score (0.0 to 1.0)
- Interpretation level (factual, user_claimed, symbolic, inferred, speculative)

### Comparative Matrix (`output/comparative_matrix.json`)

Compares identity pairs across:
- Expression match
- Soul Urge match
- Personality match
- Shared active numbers

### Interpretation Report (`output/interpretation_report.md`)

Full analysis with strict sections:
1. Verified facts
2. Computed facts
3. Symbolic interpretations
4. Speculative synthesis
5. Risks
6. Naming recommendations
7. Integration recommendations
8. Safety & provenance policy

## Quick Start

```bash
# Run tests
python3 tests/test_pythagorean.py

# Generate signatures
python3 -c "
import sys
sys.path.insert(0, 'src')
from encoders.pythagorean import pythagorean_signature
sig = pythagorean_signature('Your Name')
print(f'Expression: {sig.reduced}')
print(f'Soul Urge: {sig.soul_urge}')
print(f'Personality: {sig.personality}')
"
```

## Human Seed

```yaml
birth_identity:
  full_birth_name: Kirk Evan Brown
  birth_date: 1982-02-04
  birth_time: 01:42
  birth_place: Evanston, Wyoming, USA

known_aliases:
  - Capt
  - Captain
  - Knowurknot
  - knowurknottty
  - Captain Knowurknot

project_entities:
  - CAPT
  - bioCAPT
  - FrankenCAPT
  - Jenn-ai
  - SynSync
  - Soul Fractal Engine
  - Knowledge Bubbles
  - Inversion Labs
  - CAPT-RYS
  - SYNCHEF
  - Wyrd
```

## Critical Rules

1. **Never say numerology proves anything.**
2. **Never conflate symbolic resonance with empirical validation.**
3. **Never infer sensitive personal traits as fact.**
4. **Every symbolic claim must be labeled symbolic, interpretive, or speculative.**
5. **Every computed value must be reproducible.**

## File Structure

```
human-metadata-engine/
├── README.md
├── src/
│   └── encoders/
│       └── pythagorean.py      # Pythagorean encoder
├── tests/
│   └── test_pythagorean.py     # 17 verification tests
├── output/
│   ├── identity_signatures.json  # 17 identity signatures
│   ├── identity_graph.json       # Graph with nodes and edges
│   ├── comparative_matrix.json   # Pair comparisons
│   └── interpretation_report.md  # Full analysis
├── schemas/                      # JSON schemas (future)
└── examples/                     # Usage examples (future)
```

## Integration with CAPT/bioCAPT

This engine is designed to integrate with:
- **CAPT**: Identity metadata as graph nodes
- **bioCAPT**: ECHO indexing by symbolic resonance
- **CSG**: Identity state transitions
- **PULSE**: Identity coherence monitoring
- **Knowledge Bubbles**: Exportable identity analysis

## Version History

- **0.1.0** (2026-07-04): Initial release with Pythagorean encoder, 17 identity signatures, graph model, comparative matrix, interpretation report.

---

*Part of the Inversion Labs ecosystem.*  
*Symbolic systems are interpretive lenses, not empirical proof.*
