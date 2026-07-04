# Human Metadata Engine

A provenance-aware identity metadata architecture that encodes humans, aliases, projects, personas, and symbolic identities into a structured graph.

**v0.2.0** — Now with 5 encoders, graph analysis, and ~50 dimensions per identity.

## What This Is

This engine computes multiple symbolic, linguistic, semantic, temporal, and graph-based signatures for identity strings. It treats numerology as one encoder among many — not the authority.

## Core Principle

> "What lenses describe this identity?"  
> not:  
> "What is this person?"

## Encoder Suite

| Encoder | What It Computes | Dimensions |
|---------|------------------|------------|
| **Pythagorean** | Expression, Soul Urge, Personality, Balance, Hidden Passion, Karmic Lessons | ~15 |
| **Chaldean** | Name Number, Compound Number, Soul/Personality (ancient system, no master numbers) | ~10 |
| **Ordinal** | A1Z26 standard + reverse + digital root reduced, vowel/consonant totals | ~8 |
| **Linguistic** | Shannon entropy, bigrams, trigrams, syllables, phonetics, symmetry, uniqueness | ~20 |
| **Binary/Prime** | Vowel/consonant binary string, prime-index encoding, polarity score | ~10 |

**Total: ~50 dimensions per identity string.**

## Quick Start

```bash
# Run all tests (41 tests)
python3 tests/test_pythagorean.py    # 17 Pythagorean tests
python3 tests/test_extended.py       # 24 Chaldean/Ordinal/Linguistic/Binary tests

# Generate unified signatures (all encoders)
python3 src/engine.py

# Run graph analysis
python3 src/graph/analysis.py output/identity_graph.json
```

## Encoder Implementations

### Pythagorean (`src/encoders/pythagorean.py`)
Standard letter-to-number mapping:
```
1: A J S    4: D M V    7: G P Y
2: B K T    5: E N W    8: H Q Z
3: C L U    6: F O X    9: I R
```
Master numbers (11, 22, 33) preserved at intermediate reduction.

### Chaldean (`src/encoders/chaldean.py`)
Ancient Babylonian mapping (9 is sacred, excluded):
```
1: A I J Q Y    5: E H N X
2: B K R         6: U V W
3: C G L S       7: O Z
4: D M T         8: F P
```
No master numbers. Name numbers reduce to single digit.

### Ordinal (`src/encoders/ordinal.py`)
Three ordinal variants:
- **Standard**: A=1, B=2, ..., Z=26
- **Reverse**: A=26, B=25, ..., Z=1
- **Reduced**: Digital root of standard ordinal per letter

### Linguistic (`src/encoders/linguistic.py`)
Measurable text properties (no symbolic claims):
- Shannon entropy of character distribution
- Bigram/trigram frequency tables
- Syllable estimation
- Phon...[truncated]