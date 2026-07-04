"""
Linguistic Encoder
==================

Computes measurable linguistic properties of identity strings:
- Letter frequency distribution
- Bigram and trigram frequencies
- Shannon entropy
- Vowel/consonant ratio
- Syllable estimate
- Palindrome detection
- Symmetry measures
- Uniqueness score
- Phonetic notes (approximate)

No symbolic claims — only measurable properties.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import Counter
import math
import re


STRICT_VOWELS = {"A", "E", "I", "O", "U"}
VOWEL_SET = {"A", "E", "I", "O", "U", "Y"}

# Approximate phonetic groupings (IPA-inspired, simplified)
PLOSIVES = {"B", "D", "G", "K", "P", "T"}
FRICATIVES = {"F", "H", "V", "Z", "S", "SH", "ZH"}
NASALS = {"M", "N"}
LIQUIDS = {"L", "R"}
GLIDES = {"W", "Y"}


@dataclass(frozen=True)
class BigramStats:
    bigram: str
    count: int
    frequency: float


@dataclass(frozen=True)
class LinguisticSignature:
    original_text: str
    normalized_text: str
    letter_count: int
    token_count: int

    # Vowel/consonant analysis
    vowel_count: int
    consonant_count: int
    vowel_ratio: float
    y_count: int
    y_as_vowel_count: int

    # Frequency distribution
    letter_frequency: dict[str, float]
    bigrams: list[BigramStats]
    trigrams: list[BigramStats]

    # Entropy
    shannon_entropy: float
    max_possible_entropy: float
    entropy_ratio: float

    # Symmetry
    is_palindrome: bool
    palindrome_length: int
    longest_palindrome_fragment: str
    forward_reverse_match: float

    # Syllable estimate
    syllable_estimate: int

    # Phonetic profile
    plosive_count: int
    fricative_count: int
    nasal_count: int
    liquid_count: int
    glide_count: int
    consonant_cluster_count: int

    # Uniqueness
    unique_letters: int
    letter_repetition_ratio: float
    repeated_letter_patterns: list[str]

    # Name structure
    has_prefix: bool
    has_suffix: bool
    common_prefixes: list[str]
    common_suffixes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


COMMON_PREFIXES = {"MC", "MAC", "DE", "VAN", "VON", "EL", "AL", "BIN", "IBN"}
COMMON_SUFFIXES = {"SON", "SEN", "MAN", "TON", "FIELD", "BURG", "BERG", "STEIN"}


def estimate_syllables(text: str) -> int:
    """Rough syllable count based on vowel groups."""
    text = text.upper()
    count = 0
    prev_vowel = False
    for ch in text:
        is_vowel = ch in VOWEL_SET
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Handle silent e
    if text.endswith("E") and count > 1:
        count -= 1
    return max(1, count)


def shannon_entropy(text: str) -> float:
    """Shannon entropy of character distribution."""
    if not text:
        return 0.0
    freq = Counter(text)
    total = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def longest_palindrome(text: str) -> str:
    """Find the longest palindromic substring."""
    if not text:
        return ""
    best = text[0]
    for i in range(len(text)):
        # Odd length
        l, r = i, i
        while l >= 0 and r < len(text) and text[l] == text[r]:
            if r - l + 1 > len(best):
                best = text[l:r+1]
            l -= 1
            r += 1
        # Even length
        l, r = i, i + 1
        while l >= 0 and r < len(text) and text[l] == text[r]:
            if r - l + 1 > len(best):
                best = text[l:r+1]
            l -= 1
            r += 1
    return best


def phonetic_class(ch: str) -> str:
    """Classify a letter by its phonetic properties."""
    if ch in PLOSIVES:
        return "plosive"
    if ch in FRICATIVES:
        return "fricative"
    if ch in NASALS:
        return "nasal"
    if ch in LIQUIDS:
        return "liquid"
    if ch in GLIDES:
        return "glide"
    if ch in STRICT_VOWELS:
        return "vowel"
    return "unknown"


def linguistic_signature(text: str) -> LinguisticSignature:
    """Compute full linguistic signature."""
    normalized = "".join(ch for ch in text.upper() if ch.isalpha())
    tokens = [t for t in re.split(r"[\s\-_]+", text.upper()) if t]

    # Letter classification
    vowels = [ch for ch in normalized if ch in STRICT_VOWELS]
    consonants = [ch for ch in normalized if ch not in STRICT_VOWELS]
    y_chars = [ch for ch in normalized if ch == "Y"]

    # Bigrams and trigrams
    bigrams = [normalized[i:i+2] for i in range(len(normalized)-1)]
    trigrams = [normalized[i:i+3] for i in range(len(normalized)-2)]

    bigram_freq = Counter(bigrams)
    trigram_freq = Counter(trigrams)
    total_bigrams = len(bigrams) if bigrams else 1
    total_trigrams = len(trigrams) if trigrams else 1

    bigram_stats = sorted(
        [BigramStats(b, c, c/total_bigrams) for b, c in bigram_freq.most_common(10)],
        key=lambda x: -x.count,
    )
    trigram_stats = sorted(
        [BigramStats(t, c, c/total_trigrams) for t, c in trigram_freq.most_common(10)],
        key=lambda x: -x.count,
    )

    # Letter frequency
    letter_count = Counter(normalized)
    total_letters = len(normalized) if normalized else 1
    letter_frequency = {ch: count/total_letters for ch, count in letter_count.most_common()}

    # Entropy
    entropy = shannon_entropy(normalized)
    max_entropy = math.log2(26) if normalized else 0

    # Palindrome
    rev = normalized[::-1]
    forward_match = sum(1 for a, b in zip(normalized, rev) if a == b)
    match_ratio = forward_match / len(normalized) if normalized else 0
    pal = longest_palindrome(normalized)

    # Syllables
    syllables = estimate_syllables(normalized)

    # Phonetic classes
    plosive_count = sum(1 for ch in normalized if ch in PLOSIVES)
    fricative_count = sum(1 for ch in normalized if ch in FRICATIVES)
    nasal_count = sum(1 for ch in normalized if ch in NASALS)
    liquid_count = sum(1 for ch in normalized if ch in LIQUIDS)
    glide_count = sum(1 for ch in normalized if ch in GLIDES)

    # Consonant clusters
    clusters = 0
    in_cluster = False
    for ch in normalized:
        if ch not in STRICT_VOWELS:
            if in_cluster:
                clusters += 1
            in_cluster = True
        else:
            in_cluster = False

    # Uniqueness
    unique = len(set(normalized))
    rep_ratio = 1 - (unique / len(normalized)) if normalized else 0

    # Repeated patterns
    repeated = []
    for ch, count in letter_count.items():
        if count > 1:
            repeated.append(f"{ch}x{count}")
    repeated.sort(key=lambda x: -int(x[2:]))

    # Prefixes and suffixes
    prefix_hits = [p for p in COMMON_PREFIXES if normalized.startswith(p)]
    suffix_hits = [s for s in COMMON_SUFFIXES if normalized.endswith(s)]

    return LinguisticSignature(
        original_text=text,
        normalized_text=normalized,
        letter_count=len(normalized),
        token_count=len(tokens),
        vowel_count=len(vowels),
        consonant_count=len(consonants),
        vowel_ratio=len(vowels) / len(normalized) if normalized else 0,
        y_count=len(y_chars),
        y_as_vowel_count=0,
        letter_frequency=letter_frequency,
        bigrams=bigram_stats,
        trigrams=trigram_stats,
        shannon_entropy=round(entropy, 4),
        max_possible_entropy=round(max_entropy, 4),
        entropy_ratio=round(entropy / max_entropy, 4) if max_entropy > 0 else 0,
        is_palindrome=normalized == rev,
        palindrome_length=len(pal),
        longest_palindrome_fragment=pal,
        forward_reverse_match=round(match_ratio, 4),
        syllable_estimate=syllables,
        plosive_count=plosive_count,
        fricative_count=fricative_count,
        nasal_count=nasal_count,
        liquid_count=liquid_count,
        glide_count=glide_count,
        consonant_cluster_count=clusters,
        unique_letters=unique,
        letter_repetition_ratio=round(rep_ratio, 4),
        repeated_letter_patterns=repeated,
        has_prefix=len(prefix_hits) > 0,
        has_suffix=len(suffix_hits) > 0,
        common_prefixes=prefix_hits,
        common_suffixes=suffix_hits,
    )


if __name__ == "__main__":
    names = [
        "John Michael Smith", "Capt", "CAPT", "testuser42", "bioCAPT",
        "Inversion Labs", "Jenn", "FrankenCAPT",
    ]
    for name in names:
        sig = linguistic_signature(name)
        print(f"{name:<25} Letters={sig.letter_count}  "
              f"V/C={sig.vowel_ratio:.2f}  "
              f"Entropy={sig.shannon_entropy:.2f}  "
              f"Syllables={sig.syllable_estimate}  "
              f"Unique={sig.unique_letters}")
