# Human Metadata Engine

A provenance-aware identity metadata architecture that encodes humans, aliases, projects, personas, and symbolic identities into a structured graph.

**v0.3.0** — Complete encoder suite with 9 symbolic systems, graph algorithms, and Knowledge Bubble export.

## Architecture

```
human-metadata-engine/
├── src/
│   ├── engine.py                    # Master orchestrator (v0.3.0)
│   ├── encoders/
│   │   ├── pythagorean.py           # Pythagorean numerology (expression, soul urge, personality)
│   │   ├── chaldean.py              # Chaldean numerology (ancient Babylonian, no master numbers)
│   │   ├── ordinal.py               # A1Z26, reverse ordinal, reduced ordinal
│   │   ├── linguistic.py            # Shannon entropy, bigrams, syllables, phonetics
│   │   ├── binary_prime.py          # Vowel/consonant binary, prime-index encoding
│   │   ├── gematria.py              # Hebrew Gematria (absolute + ordinal)
│   │   ├── isopsephy.py             # Greek Isopsephy (digital root chain)
│   │   ├── astrology.py             # Tropical astrology (Swiss Ephemeris)
│   │   ├── human_design.py          # Human Design / Gene Keys (64 gates)
│   │   └── psychology.py            # Big Five, MBTI, Enneagram (user-supplied)
│   ├── graph/
│   │   ├── analysis.py              # Centrality, communities, resonance
│   │   └── algorithms.py            # PageRank, spectral clustering, HITS
│   └── knowledge_bubble.py          # Knowledge Bubble export format
├── tests/
│   ├── test_pythagorean.py          # 17 tests
│   ├── test_extended.py             # 24 tests
│   └── test_final.py                # 31 tests
├── output/
│   ├── unified_signatures.json      # 19 identities × 9 encoders
│   ├── identity_graph.json          # 19 nodes, 25 edges
│   └── graph_analysis.json          # PageRank, spectral, HITS
└── schemas/
    ├── identity-signature.schema.json
    └── identity-graph.schema.json
```

## Encoder Suite (9 Systems)

| Encoder | Type | Dimensions | Description |
|---------|------|------------|-------------|
| **Pythagorean** | Numerology | 12 | Expression, soul urge, personality, hidden passion, karmic lessons |
| **Chaldean** | Numerology | 5 | Name number, compound number, vibration-based mapping |
| **Ordinal** | Numerology | 5 | A1Z26, reverse, reduced — pure alphabetical encoding |
| **Linguistic** | Analysis | 14 | Shannon entropy, syllables, plosives, fricatives, bigrams |
| **Binary/Prime** | Encoding | 9 | Vowel/consonant binary string, prime-index mapping |
| **Gematria** | Hebrew | 7 | Absolute + ordinal totals, Latin-to-Hebrew mapping |
| **Isopsephy** | Greek | 5 | Digital root chain, Latin-to-Greek correspondence |
| **Astrology** | Tropical | 20+ | Sun/Moon/Ascendant, 10 planets, aspects, houses |
| **Human Design** | Gene Keys | 15+ | Type, strategy, 64 gates, channels, centers, profile |
| **Psychology** | User-supplied | 20+ | Big Five, MBTI, Enneagram, attachment style |

## Quick Start

```python
from src.engine import compute_unified_signature

identity = {
    "id": "human:kirk_evan_brown",
    "text": "Kirk Evan Brown",
    "birth": {
        "year": 1982, "month": 2, "day": 4,
        "hour": 1, "minute": 42,
        "timezone_offset": -7,
        "location": "Evanston, Wyoming, USA",
        "lat": 41.2633, "lon": -110.9631,
    },
}

sig = compute_unified_signature(identity)
print(f"Dimensions: {sig['dimensions']}")
print(f"Encoders: {list(sig['encoders'].keys())}")
```

## Graph Algorithms

| Algorithm | Purpose |
|-----------|---------|
| **PageRank** | Importance ranking based on incoming links |
| **Spectral Clustering** | Community detection via Laplacian eigenvectors |
| **HITS** | Hub/authority scoring for network analysis |
| **Betweenness Centrality** | Bridge node identification |
| **Clustering Coefficient** | Local density measurement |
| **Shortest Paths** | Distance between any two nodes |
| **Connected Components** | Isolated subgraph detection |

## Knowledge Bubble Format

Exports identity analysis as self-contained, verifiable Knowledge Bubbles:

```python
from src.knowledge_bubble import create_identity_bubble

bubble = create_identity_bubble(
    identity_text="CAPT",
    pythagorean_data=sig["encoders"]["pythagorean"],
    chaldean_data=sig["encoders"]["chaldean"],
    ordinal_data=sig["encoders"]["ordinal"],
    linguistic_data=sig["encoders"]["linguistic"],
    binary_prime_data=sig["encoders"]["binary_prime"],
)
```

Each bubble contains:
- **Claims** (with confidence levels and evidence)
- **Computations** (reproducible formulas)
- **Procedures** (step-by-step reproduction)
- **Risks** (limitations and caveats)
- **Open Questions** (unresolved issues)

## Identity Graph

19 nodes, 25 edges representing relationships between:
- Humans (Kirk, Jenn)
- Aliases (Captain, CAPT, Capt Cortex)
- Handles (Knowurknot)
- Projects (CAPT, FrankenCAPT, bioCAPT, Inversion Labs, JennAI, SynSync)
- Collaborators (Ornith)
- Platforms (Hermes, OpenRouter)

### Graph Metrics
- **Diameter:** 4 (longest shortest path)
- **Radius:** 1 (minimum eccentricity)
- **Avg Clustering Coefficient:** 0.414
- **Connected Components:** 3

## Test Coverage

```
test_pythagorean.py:  17 tests (Pythagorean numerology)
test_extended.py:     24 tests (Chaldean, Ordinal, Linguistic, Binary/Prime)
test_final.py:        31 tests (Gematria, Isopsephy, Astrology, HD, Psychology, Graph)
─────────────────────────────────────────────────────────────────
Total:                72 tests, 100% passing
```

## Dependencies

- Python 3.9+
- `pyswisseph` — Swiss Ephemeris for astrological calculations

## Usage

```bash
# Run the engine
python3 src/engine.py

# Run all tests
python3 tests/test_pythagorean.py
python3 tests/test_extended.py
python3 tests/test_final.py

# Run graph algorithms
python3 src/graph/algorithms.py output/identity_graph.json

# Generate Knowledge Bubble
python3 src/knowledge_bubble.py
```

## Disclaimer

This system uses symbolic numerological and astrological systems as **interpretive lenses**, not empirical proof. Claims derived from these systems should be treated as symbolic analysis, not factual assertions.

## License

Private — Inversion Labs
