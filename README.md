# Human Metadata Engine

A provenance-aware identity metadata architecture that encodes humans, aliases, projects, personas, and symbolic identities into a structured graph.

**v0.6.0** — Core encoder suite plus 25 provenance-aware symbolic extensions across four phases, explicit Data/Magic reading modes, strict public contracts, redacted responses, cross-encoder analytics, graph algorithms, Knowledge Bubble export, and the **Identity Resonance web app**. The payment flow remains a demo stub by design.

## Quick Start — Web App

```bash
./deploy.sh                 # installs Swiss Ephemeris, runs the canonical test runner, serves :8000
# or directly:
python3 -m pip install --require-hashes -r requirements.txt && python3 webapp/server.py
```

Open http://localhost:8000 — choose Data or Magic mode, enter a name, and optionally add birth or self-reported assessment data. Data mode stays measurement/provenance-first; Magic mode adds a clearly labeled symbolic reflection layer. Historical public-reference input can use `subject_type: "reference"`.

**Deploying anywhere:** the app is a single Python process with one mandatory native dependency: the pinned `pyswisseph` Swiss Ephemeris extension for exact natal calculations. Use the repository Dockerfile or run `python3 -m pip install -r requirements.txt` before starting `python3 webapp/server.py`.

```bash
# The repository Dockerfile builds pyswisseph in a GCC-enabled builder stage
# and copies only the resulting wheel into the Python 3.12 runtime image.
docker build -t identity-resonance .
docker run --rm -p 127.0.0.1:8000:8080 identity-resonance
```

## Architecture

```
human-metadata-engine/
├── webapp/
│   ├── server.py                    # Stdlib HTTP server (API + static)
│   └── static/                      # Single-page dark-theme app (vendored Tailwind)
├── src/
│   ├── engine.py                    # Master orchestrator (signature-v2)
│   ├── analytics.py                 # Resonance score, fingerprints, correlations, feature agreement
│   ├── snapshot.py                  # Personality snapshot narratives
│   ├── report.py                    # Magic-mode long-form report generator
│   ├── public_contract.py            # Strict public validation and two-mode contract
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
│   │   ├── pipeline.py               # 25-system provenance-aware expansion pipeline
│   │   ├── kabbalah.py               # Tree of Life source module
│   │   └── apollonius.py             # Apollonius source module, unified by pipeline
│   ├── graph/
│   │   ├── analysis.py              # Centrality, communities, resonance
│   │   └── algorithms.py            # PageRank, spectral clustering, HITS
│   └── knowledge_bubble.py          # Knowledge Bubble export format
├── tests/
│   ├── test_pythagorean.py          # 17 tests
│   ├── test_extended.py             # 24 tests
│   ├── test_final.py                # 34 tests
│   └── test_analytics.py            # 46 tests (v0.4.0 analytics)
├── output/
│   ├── unified_signatures.json      # generated signatures + analytics
│   ├── encoder_correlations.json    # Pearson + digit-agreement matrices
│   ├── comparative_report.{json,md} # Batch ranking + feature-agreement report
│   ├── identity_graph.json          # 19 nodes, 25 edges
│   └── graph_analysis.json          # PageRank, spectral, HITS
└── schemas/
    ├── identity-signature.schema.json
    └── identity-graph.schema.json
```

## Core Encoder Suite

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
    "id": "human:john_michael_smith",
    "text": "John Michael Smith",
    "birth": {
        "year": 1985, "month": 6, "day": 15,
        "hour": 10, "minute": 30,
        "timezone_offset": -7,
        "location": "Portland, Oregon, USA",
        "lat": 45.5152, "lon": -122.6765,
    },
}

sig = compute_unified_signature(identity)
print(f"Dimensions: {sig['dimensions']}")
print(f"Encoders: {list(sig['encoders'].keys())}")
```

## Cross-Encoder Analytics

Second-order analysis computed on top of the unified signatures:

| Feature | Description |
|---------|-------------|
| **Composite Resonance Score** | 0–100 metric: 35% numerological convergence + 25% linguistic harmony + 20% polarity balance + 20% symbolic depth (formula documented in `src/analytics.py`) |
| **Identity Fingerprint** | Deterministic visual hash: SHA-256-derived seed, n-fold symmetry from the expression number, one spoke per encoder, vowel/consonant binary ring |
| **Correlation Matrices** | Pearson over raw magnitudes + digit-agreement rates with the mathematically coupled ordinal root excluded |
| **Feature Agreement** | 14-feature comparison: eight independent reduced-digit categories match exactly and six continuous features use fixed tolerances; it is not person-level similarity |
| **Batch Reports** | Comparative ranking of any identity set (markdown + JSON) |
| **Personality Snapshots** | Deterministic narrative from astrology + Human Design + psychology layers |
| **Long-Form Reports** | 10-section, 3,000+ word written analysis per identity (`src/report.py`) |

Reference population outputs are generated from the current engine version; dimension counts intentionally are not fixed across encoder releases.

## Provenance-Aware Symbolic Extensions (25 Systems)

The expansion is available through `compute_unified_signature(...)["encoders"]` and is grouped into the four roadmap phases plus structural integrations:

- **Phase 1:** Kabbalistic Tree of Life, Sacred Geometry, Alchemical Transformation, Sumerian Sexagesimal, Hermetic Principles.
- **Phase 2:** Tarot, Babylonian Planetary Numbers, Hermes–Thoth–Nabu Lineage, Solomonic Indexing, Arabic Abjad.
- **Phase 3:** Chinese I Ching/Wu Xing/year-pillar context, Egyptian uniliteral/decans, Vedic Jyotish requirements, Mayan Tzolkin, Cuneiform structural analysis.
- **Phase 4:** Elder Futhark, Ogham, Egyptian Ma'at, Mandaean Duodecimal, architectural-proportion analysis, Indus structural analysis, Unicode codepoints.
- **Structural:** unified Apollonius, temporal numerology, and the explicit Tarot–Kabbalah–Astrology–Numerology bridge.

Every extension returns `system`, `phase`, `status`, `interpretation_level`, `provenance`, and `data`. Direct-script input is preserved, while Latin-only systems use the named `builtin-v1` transliteration profile. See [the provenance catalog](docs/symbolic-systems-provenance.md) for each convention, source ID, and limitation.

The extension results are intentionally excluded from the existing composite resonance formula and fingerprint spokes. They are symbolic or computed lenses, not empirical findings.

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
- Humans (John, Alice)
- Aliases (Captain, CAPT, Capt Cortex)
- Handles (testuser42)
- Projects (CAPT, FrankenCAPT, bioCAPT, Inversion Labs, JennAI, SynSync)
- Collaborators (Ornith)
- Platforms (Hermes, OpenRouter)

### Graph Metrics
- **Diameter:** 4 (longest shortest path)
- **Radius:** 1 (minimum eccentricity)
- **Avg Clustering Coefficient:** 0.414
- **Connected Components:** 3

## Invention Suite (20 Modules)

The engine ships with 20 self-contained invention modules:

### Core Encoders (9)
1. **Pythagorean** — Expression, Soul Urge, Personality, Karmic Lessons
2. **Chaldean** — Alternative numerology with occult letter values
3. **Ordinal (A1Z26)** — Simple letter-to-number mapping
4. **Linguistic** — Shannon entropy, bigrams, trigrams, syllable analysis
5. **Binary/Prime** — Vowel/consonant polarity, prime number mapping
6. **Gematria** — Hebrew alphabet numeric values
7. **Isopsephy** — Greek alphabet numeric values
8. **Astrology** — Birth chart computation (requires birth data)
9. **Human Design** — Type, strategy, authority (requires birth data)

### Analytics & Search (3)
10. **Identity Search** — Feature-agreement search across the declared 14-feature schema
11. **Signature Diff** — Dimension-by-dimension comparison of two identities
12. **Clustering** — Unsupervised hierarchical grouping of identities

### Generation (3)
13. **Personality Narrative** — Human-readable profile from numeric data
14. **SVG Fingerprint** — Deterministic visual identity fingerprint
15. **Name Generator** — Find names with target numerological properties

### Analysis (2)
16. **Knowledge Bubble Miner** — Extract novel cross-encoder insights
17. **Anomaly Detection** — Z-score outlier detection across dimensions

### Infrastructure (3)
18. **SQLite Persistence** — Historical tracking of signatures and drift
19. **Export System** — CSV, JSONL, webhook, and markdown export
20. **CLI Batch Tool** — Command-line interface for all operations

### APIs (2)
- **REST API** — `/encode`, `/compare`, `/search`, `/narrative`, `/fingerprint`
- **Web Dashboard** — Interactive comparison and graph visualization

```bash
# Run all 20 inventions
python3 -m src.run_all

# CLI usage
python3 -m src.cli add "Captain"
python3 -m src.cli compare "Captain" "Jenn"
python3 -m src.cli search "Captain"
python3 -m src.cli narrative "Captain"
python3 -m src.cli cluster
python3 -m src.cli anomaly
python3 -m src.cli export --format csv
python3 -m src.cli stats

# Start the legacy API only for loopback compatibility work; it is not the public surface.
python3 -m src.api
```

## Test Coverage

```
test_pythagorean.py:  17 tests (Pythagorean numerology)
test_extended.py:     24 tests (Chaldean, Ordinal, Linguistic, Binary/Prime)
test_final.py:        34 tests (Gematria, Isopsephy, exact astrology, HD, Psychology, Graph)
test_analytics.py:    46 tests (Resonance, fingerprints, correlations, reports)
test_symbolic_*.py:   16 tests (roadmap, Unicode, provenance, detail surface)
test_ephemeris_packaging.py: 1 test (Docker/deploy/CI contract)
─────────────────────────────────────────────────────────────────
The canonical runner discovers every `tests/test_*.py` file and reports its exact count; avoid hardcoding a stale total in product copy.
```

## Dependencies

- Python 3.9+
- `pyswisseph==2.10.3.2` *(mandatory)* — Swiss Ephemeris for exact astrology and Human Design; see [third-party notice](THIRD_PARTY_NOTICES.md)

## Usage

```bash
# Run the engine (writes output/*.json + comparative report)
python3 src/engine.py

# Run all tests
python3 tools/run_tests.py

# Run graph algorithms
python3 src/graph/algorithms.py output/identity_graph.json

# Generate Knowledge Bubble
python3 src/knowledge_bubble.py

# Serve the web app
python3 webapp/server.py       # or ./deploy.sh
```

## Disclaimer

This system uses symbolic numerological and astrological systems as **interpretive lenses**, not empirical proof. Claims derived from these systems should be treated as symbolic analysis, not factual assertions.

## License

Private — Inversion Labs
