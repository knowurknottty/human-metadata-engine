"""
Cross-Encoder Analytics
=======================

Second-order analysis computed ON TOP of the unified signatures:

1. Composite Resonance Score (0-100) — a single comparable metric per identity
2. Identity Fingerprint — deterministic visual-hash parameters per identity
3. Feature vectors + cosine similarity between identities
4. Cross-encoder correlation matrix (Pearson on raw magnitudes +
   reduced-digit agreement rates)
5. Batch comparative report (markdown + JSON)

Composite Resonance Score — formula and justification
------------------------------------------------------

    resonance = 100 * ( 0.35 * numerological_convergence
                      + 0.25 * linguistic_harmony
                      + 0.20 * polarity_balance
                      + 0.20 * symbolic_depth )

* numerological_convergence (0.35): the five independent digit systems
  (Pythagorean expression, Chaldean name number, Ordinal reduced,
  Gematria absolute reduced, Isopsephy reduced) use different letter
  mappings, so agreement between them is non-trivial. We measure the
  concentration of the five reduced digits: if m is the multiplicity of
  the most common digit, convergence = (m - 1) / 4. A master number
  (11/22/33) in the Pythagorean expression adds +0.15 (capped at 1.0).
  This is the heaviest weight because inter-system agreement is the
  core "resonance" concept.

* linguistic_harmony (0.25): measurable euphony. Two sub-signals,
  averaged: (a) entropy_ratio proximity to 0.85 — names that are rich
  but still structured (natural English names cluster near 0.8-0.9);
  (b) vowel_ratio proximity to 0.40 — the vowel share of typical
  pronounceable English words.

* polarity_balance (0.20): from the binary/prime encoder. 70% the
  Shannon entropy of the vowel/consonant binary string (1.0 = perfectly
  balanced pattern) and 30% one minus the normalized prime-power
  polarity |vowel_power - consonant_power| / (vowel_power + consonant_power).

* symbolic_depth (0.20): alphabet completeness (few karmic lessons =
  many of the 9 digit classes present, weight 60%) plus the length of
  the isopsephy digital-root chain normalized over 3 steps (a longer
  reduction cascade means the name reaches deeper into the number space,
  weight 40%).

All inputs are deterministic functions of the name string, so the score
is reproducible. It is an interpretive index, not an empirical measure.
"""

from __future__ import annotations
import hashlib
import json
import math

RESONANCE_WEIGHTS = {
    "numerological_convergence": 0.35,
    "linguistic_harmony": 0.25,
    "polarity_balance": 0.20,
    "symbolic_depth": 0.20,
}

# Encoders that produce a comparable single reduced digit (1-9)
DIGIT_FIELDS = {
    "pythagorean": ("pythagorean", "expression"),
    "chaldean": ("chaldean", "name_number"),
    "ordinal": ("ordinal", "ordinal_reduced"),
    "gematria": ("gematria", "absolute_reduced"),
    "isopsephy": ("isopsephy", "reduced"),
}

# Primary raw magnitude per core encoder, for Pearson correlation
MAGNITUDE_FIELDS = {
    "pythagorean": ("pythagorean", "total"),
    "chaldean": ("chaldean", "compound_number"),
    "ordinal": ("ordinal", "ordinal_total"),
    "linguistic": ("linguistic", "shannon_entropy"),
    "binary_prime": ("binary_prime", "prime_total"),
    "gematria": ("gematria", "absolute_total"),
    "isopsephy": ("isopsephy", "total"),
}

ENCODER_HUES = {
    "pythagorean": 45,    # gold
    "chaldean": 30,       # amber
    "ordinal": 200,       # steel blue
    "linguistic": 220,    # blue
    "binary_prime": 160,  # teal
    "gematria": 280,      # purple
    "isopsephy": 260,     # violet
    "astrology": 300,     # magenta-purple
    "human_design": 130,  # green
}


def _get(sig: dict, encoder: str, field: str, default=None):
    enc = sig.get("encoders", {}).get(encoder, {})
    if isinstance(enc, dict):
        return enc.get(field, default)
    return default


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


# =====================================================================
# 1. Composite Resonance Score
# =====================================================================

def numerological_convergence(sig: dict) -> float:
    """Concentration of the five independent reduced digits (0..1)."""
    digits = []
    for enc, field in DIGIT_FIELDS.values():
        v = _get(sig, enc, field)
        if isinstance(v, int) and v > 0:
            # Fold master numbers to their digit for agreement counting
            d = v
            while d > 9:
                d = sum(int(c) for c in str(d))
            digits.append(d)
    if len(digits) < 2:
        return 0.0
    counts = {}
    for d in digits:
        counts[d] = counts.get(d, 0) + 1
    m = max(counts.values())
    score = (m - 1) / (len(digits) - 1)
    master = _get(sig, "pythagorean", "master_preserved")
    if master in (11, 22, 33):
        score += 0.15
    return _clip01(score)


def linguistic_harmony(sig: dict) -> float:
    """Euphony proxy: entropy near 0.85, vowel ratio near 0.40 (0..1)."""
    er = _get(sig, "linguistic", "entropy_ratio", 0.0) or 0.0
    vr = _get(sig, "linguistic", "vowel_ratio", 0.0) or 0.0
    entropy_score = _clip01(1.0 - abs(er - 0.85) / 0.85)
    vowel_score = _clip01(1.0 - abs(vr - 0.40) / 0.40)
    return (entropy_score + vowel_score) / 2.0


def polarity_balance(sig: dict) -> float:
    """Vowel/consonant structural balance from binary/prime encoder (0..1)."""
    be = _get(sig, "binary_prime", "binary_entropy", 0.0) or 0.0
    vp = _get(sig, "binary_prime", "vowel_power", 0.0) or 0.0
    cp = _get(sig, "binary_prime", "consonant_power", 0.0) or 0.0
    total = vp + cp
    polarity_norm = abs(vp - cp) / total if total > 0 else 1.0
    return _clip01(0.7 * be + 0.3 * (1.0 - polarity_norm))


def symbolic_depth(sig: dict) -> float:
    """Alphabet completeness + digital-root cascade depth (0..1)."""
    karmic = _get(sig, "pythagorean", "karmic_lessons", []) or []
    completeness = 1.0 - len(karmic) / 9.0
    chain = _get(sig, "isopsephy", "digital_root_chain", []) or []
    chain_depth = _clip01((len(chain) - 1) / 3.0)
    return _clip01(0.6 * completeness + 0.4 * chain_depth)


def composite_resonance(sig: dict) -> dict:
    """Compute the 0-100 composite resonance score with components."""
    components = {
        "numerological_convergence": round(numerological_convergence(sig), 4),
        "linguistic_harmony": round(linguistic_harmony(sig), 4),
        "polarity_balance": round(polarity_balance(sig), 4),
        "symbolic_depth": round(symbolic_depth(sig), 4),
    }
    score = sum(RESONANCE_WEIGHTS[k] * v for k, v in components.items())
    return {
        "score": round(100.0 * score, 1),
        "components": components,
        "weights": RESONANCE_WEIGHTS,
    }


# =====================================================================
# 2. Identity Fingerprint
# =====================================================================

def identity_fingerprint(sig: dict) -> dict:
    """Deterministic visual-hash parameters for an identity.

    Returns a spec that any renderer can turn into a unique radial
    pattern: a stable hex hash, an n-fold rotational symmetry (from the
    Pythagorean expression), one spoke per encoder (magnitude + hue),
    and a binary ring pattern (the vowel/consonant string).
    """
    # Stable hash over the digit-level outputs
    core = {name: _get(sig, enc, field)
            for name, (enc, field) in sorted(DIGIT_FIELDS.items())}
    core["binary"] = _get(sig, "binary_prime", "binary_string", "")
    core["text"] = sig.get("text", "")
    digest = hashlib.sha256(
        json.dumps(core, sort_keys=True).encode()).hexdigest()

    expression = _get(sig, "pythagorean", "expression", 5) or 5
    symmetry = max(3, min(9, expression if expression <= 9 else
                          sum(int(c) for c in str(expression))))

    spokes = []
    for name, (enc, field) in MAGNITUDE_FIELDS.items():
        raw = _get(sig, enc, field, 0) or 0
        # Normalize each magnitude into 0..1 with encoder-appropriate scale
        scale = {"pythagorean": 120.0, "chaldean": 90.0, "ordinal": 300.0,
                 "linguistic": 4.2, "binary_prime": 900.0,
                 "gematria": 1500.0, "isopsephy": 3000.0}[name]
        spokes.append({
            "encoder": name,
            "value": round(_clip01(float(raw) / scale), 4),
            "hue": ENCODER_HUES[name],
        })

    return {
        "hash": digest[:16],
        "full_hash": digest,
        "symmetry": symmetry,
        "spokes": spokes,
        "ring_pattern": _get(sig, "binary_prime", "binary_string", ""),
        "seed": int(digest[:8], 16),
    }


# =====================================================================
# 3. Feature vectors + similarity
# =====================================================================

FEATURE_ORDER = [
    "pyth_expression", "pyth_soul_urge", "pyth_personality",
    "chaldean_name", "ordinal_reduced", "gematria_reduced",
    "isopsephy_reduced", "prime_reduced",
    "entropy_ratio", "vowel_ratio", "binary_entropy",
    "polarity_norm", "syllables", "chain_depth",
]


def feature_vector(sig: dict) -> list[float]:
    """Normalized (0..1) feature vector used for identity similarity."""
    def digit(enc, field):
        v = _get(sig, enc, field, 0) or 0
        while v > 9:
            v = sum(int(c) for c in str(v))
        return v / 9.0

    vp = _get(sig, "binary_prime", "vowel_power", 0) or 0
    cp = _get(sig, "binary_prime", "consonant_power", 0) or 0
    total_power = vp + cp
    polarity_norm = (vp - cp) / total_power if total_power > 0 else 0.0
    chain = _get(sig, "isopsephy", "digital_root_chain", []) or []

    return [
        digit("pythagorean", "expression"),
        digit("pythagorean", "soul_urge"),
        digit("pythagorean", "personality"),
        digit("chaldean", "name_number"),
        digit("ordinal", "ordinal_reduced"),
        digit("gematria", "absolute_reduced"),
        digit("isopsephy", "reduced"),
        digit("binary_prime", "prime_reduced"),
        _clip01(_get(sig, "linguistic", "entropy_ratio", 0) or 0),
        _clip01(_get(sig, "linguistic", "vowel_ratio", 0) or 0),
        _clip01(_get(sig, "binary_prime", "binary_entropy", 0) or 0),
        (polarity_norm + 1.0) / 2.0,
        _clip01((_get(sig, "linguistic", "syllable_estimate", 1) or 1) / 10.0),
        _clip01((len(chain) - 1) / 3.0),
    ]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def identity_similarity_matrix(sigs: list[dict]) -> dict:
    """Pairwise cosine similarity between all identities."""
    vectors = {s["id"]: feature_vector(s) for s in sigs}
    ids = [s["id"] for s in sigs]
    matrix = {}
    for i in ids:
        matrix[i] = {}
        for j in ids:
            matrix[i][j] = round(cosine_similarity(vectors[i], vectors[j]), 4)
    neighbors = {}
    for i in ids:
        ranked = sorted(((j, v) for j, v in matrix[i].items() if j != i),
                        key=lambda kv: -kv[1])
        neighbors[i] = [{"id": j, "similarity": v} for j, v in ranked[:3]]
    return {"ids": ids, "matrix": matrix, "nearest_neighbors": neighbors,
            "feature_order": FEATURE_ORDER}


# =====================================================================
# 4. Cross-encoder correlation matrix
# =====================================================================

def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def cross_encoder_correlations(sigs: list[dict]) -> dict:
    """How well do the encoders agree with each other across identities?

    Two views:
    * pearson: correlation of raw magnitudes (totals/entropy) — captures
      shared sensitivity to name length and letter composition.
    * digit_agreement: fraction of identities where two digit-producing
      encoders reduce to the SAME final digit — captures deep symbolic
      agreement that is independent of magnitude.
    """
    encoders = list(MAGNITUDE_FIELDS.keys())
    series = {}
    for name, (enc, field) in MAGNITUDE_FIELDS.items():
        series[name] = [float(_get(s, enc, field, 0) or 0) for s in sigs]

    pearson = {}
    for a in encoders:
        pearson[a] = {}
        for b in encoders:
            pearson[a][b] = round(_pearson(series[a], series[b]), 4)

    digit_encoders = list(DIGIT_FIELDS.keys())
    digits = {}
    for name, (enc, field) in DIGIT_FIELDS.items():
        vals = []
        for s in sigs:
            v = _get(s, enc, field, 0) or 0
            while v > 9:
                v = sum(int(c) for c in str(v))
            vals.append(v)
        digits[name] = vals

    agreement = {}
    n = len(sigs)
    for a in digit_encoders:
        agreement[a] = {}
        for b in digit_encoders:
            if n == 0:
                agreement[a][b] = 0.0
            else:
                same = sum(1 for x, y in zip(digits[a], digits[b]) if x == y)
                agreement[a][b] = round(same / n, 4)

    return {
        "n_identities": n,
        "magnitude_encoders": encoders,
        "pearson": pearson,
        "digit_encoders": digit_encoders,
        "digit_agreement": agreement,
    }


# =====================================================================
# 5. Batch comparative report
# =====================================================================

def batch_report(sigs: list[dict]) -> tuple[dict, str]:
    """Process a batch of signatures into a comparative report.

    Returns (report_json, report_markdown).
    """
    enriched = []
    for s in sigs:
        res = s.get("resonance") or composite_resonance(s)
        enriched.append({
            "id": s["id"],
            "text": s["text"],
            "resonance": res["score"],
            "components": res["components"],
            "expression": _get(s, "pythagorean", "expression"),
            "chaldean": _get(s, "chaldean", "name_number"),
            "entropy_ratio": _get(s, "linguistic", "entropy_ratio"),
        })
    ranked = sorted(enriched, key=lambda e: -e["resonance"])
    sim = identity_similarity_matrix(sigs)
    corr = cross_encoder_correlations(sigs)

    lines = ["# Comparative Identity Report", ""]
    lines.append(f"Batch of **{len(sigs)}** identities, ranked by "
                 "composite resonance score (0-100).")
    lines.append("")
    lines.append("| Rank | Identity | Resonance | Expression | Chaldean | Entropy |")
    lines.append("|-----:|----------|----------:|-----------:|---------:|--------:|")
    for i, e in enumerate(ranked, 1):
        lines.append(f"| {i} | {e['text']} (`{e['id']}`) | {e['resonance']} "
                     f"| {e['expression']} | {e['chaldean']} "
                     f"| {e['entropy_ratio']} |")
    lines.append("")
    lines.append("## Nearest Neighbors (cosine similarity over 14 features)")
    lines.append("")
    for ident, nbrs in sim["nearest_neighbors"].items():
        nbr_txt = ", ".join(f"{n['id']} ({n['similarity']:.2f})" for n in nbrs)
        lines.append(f"- **{ident}** → {nbr_txt}")
    lines.append("")
    lines.append("## Cross-Encoder Digit Agreement")
    lines.append("")
    des = corr["digit_encoders"]
    lines.append("| | " + " | ".join(des) + " |")
    lines.append("|---" * (len(des) + 1) + "|")
    for a in des:
        row = [f"{corr['digit_agreement'][a][b]:.2f}" for b in des]
        lines.append(f"| **{a}** | " + " | ".join(row) + " |")
    lines.append("")

    report = {
        "n_identities": len(sigs),
        "ranking": ranked,
        "similarity": sim,
        "correlations": corr,
    }
    return report, "\n".join(lines)
