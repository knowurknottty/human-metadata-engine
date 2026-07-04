"""
Greek Isopsephy Encoder
=======================

Maps Latin letters to their Greek alphabet equivalents
and computes isopsephy (Greek numerology).

Greek alphabet numerical values:
α=1, β=2, γ=3, δ=4, ε=5, ϛ=6, ζ=7, η=8, θ=9,
ι=10, κ=20, λ=30, μ=40, ν=50, ξ=60, ο=70, π=80, ϟ=90,
ρ=100, σ=200, τ=300, υ=400, φ=500, χ=600, ψ=700, ω=800, ϡ=900

Latin-to-Greek transliteration mapping:
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import Counter
import re


# Latin letter → Greek isopsephy value
ISOPSEPHY_MAP: dict[str, int] = {
    "A": 1,    # α (alpha)
    "B": 2,    # β (beta)
    "G": 3,    # γ (gamma)
    "D": 4,    # δ (delta)
    "E": 5,    # ε (epsilon)
    "F": 6,    # ϛ (stigma/digamma)
    "Z": 7,    # ζ (zeta)
    "H": 8,    # η (eta)
    "I": 10,   # ι (iota) — skipping θ=9 (no Latin equivalent)
    "K": 20,   # κ (kappa)
    "L": 30,   # λ (lambda)
    "M": 40,   # μ (mu)
    "N": 50,   # ν (nu)
    "X": 60,   # ξ (xi)
    "O": 70,   # ο (omicron)
    "P": 80,   # π (pi)
    "Q": 80,   # π (pi, closest)
    "R": 100,  # ρ (rho)
    "S": 200,  # σ (sigma)
    "T": 300,  # τ (tau)
    "U": 400,  # υ (upsilon)
    "V": 400,  # υ (upsilon, Latin V)
    "W": 800,  # ω (omega, W as double-U)
    "Y": 400,  # υ (upsilon, closest)
    "C": 300,  # τ (tau, soft C closest)
    "J": 10,   # ι (iota, closest)
}

# Greek letter names for reference
GREEK_LETTERS = {
    1: ("α", "alpha"), 2: ("β", "beta"), 3: ("γ", "gamma"),
    4: ("δ", "delta"), 5: ("ε", "epsilon"), 6: ("ϛ", "stigma"),
    7: ("ζ", "zeta"), 8: ("η", "eta"), 9: ("θ", "theta"),
    10: ("ι", "iota"), 20: ("κ", "kappa"), 30: ("λ", "lambda"),
    40: ("μ", "mu"), 50: ("ν", "nu"), 60: ("ξ", "xi"),
    70: ("ο", "omicron"), 80: ("π", "pi"), 90: ("ϟ", "koppa"),
    100: ("ρ", "rho"), 200: ("σ", "sigma"), 300: ("τ", "tau"),
    400: ("υ", "upsilon"), 500: ("φ", "phi"), 600: ("χ", "chi"),
    700: ("ψ", "psi"), 800: ("ω", "omega"), 900: ("ϡ", "sampi"),
}


@dataclass(frozen=True)
class IsopsephySignature:
    original_text: str
    normalized_text: str

    # Total
    total: int
    reduced: int

    # Letter-by-letter
    letter_values: list[dict]

    # Greek letter correspondence
    greek_correspondence: list[dict]

    # Intensity
    intensity_table: dict[int, int]
    hidden_passion: list[int]

    # Digital root analysis
    digital_root_chain: list[int]

    def to_dict(self) -> dict:
        return asdict(self)


def normalize(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalpha())


def digital_root(n: int) -> int:
    if n <= 0:
        return 0
    current = n
    chain = [current]
    while current > 9:
        current = sum(int(d) for d in str(current))
        chain.append(current)
    return chain[-1]


def isopsephy_signature(text: str) -> IsopsephySignature:
    """Compute Greek Isopsephy signature."""
    normalized = normalize(text)

    letter_values = []
    greek_corr = []
    total = 0

    for i, ch in enumerate(normalized):
        val = ISOPSEPHY_MAP.get(ch, 0)
        total += val

        letter_values.append({
            "char": ch,
            "value": val,
            "index": i,
        })

        # Find Greek equivalent
        greek_char = "?"
        greek_name = "unknown"
        for v, (gc, gn) in GREEK_LETTERS.items():
            if v == val:
                greek_char = gc
                greek_name = gn
                break

        greek_corr.append({
            "latin": ch,
            "greek": greek_char,
            "greek_name": greek_name,
            "value": val,
        })

    reduced = digital_root(total)

    # Digital root chain
    chain = [total]
    current = total
    while current > 9:
        current = sum(int(d) for d in str(current))
        chain.append(current)

    # Intensity
    counts = Counter(lv["value"] for lv in letter_values if lv["value"] > 0)
    intensity_table = {i: counts.get(i, 0) for i in range(1, 10)}
    max_count = max(intensity_table.values(), default=0)
    hidden_passion = [n for n, c in intensity_table.items() if c == max_count and c > 0]

    return IsopsephySignature(
        original_text=text,
        normalized_text=normalized,
        total=total,
        reduced=reduced,
        letter_values=letter_values,
        greek_correspondence=greek_corr,
        intensity_table=intensity_table,
        hidden_passion=hidden_passion,
        digital_root_chain=chain,
    )


if __name__ == "__main__":
    names = ["CAPT", "Knowurknot", "Kirk Evan Brown", "Jenn", "Inversion Labs"]
    for name in names:
        sig = isopsephy_signature(name)
        print(f"{name:<25} Isopsephy={sig.total:>5}({sig.reduced})  "
              f"Chain={'→'.join(map(str, sig.digital_root_chain))}")
