"""
Extended Encoder Tests
=====================

Tests for Chaldean, Ordinal, Linguistic, and Binary/Prime encoders.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encoders.pythagorean import pythagorean_signature
from encoders.chaldean import chaldean_signature
from encoders.ordinal import ordinal_signature
from encoders.linguistic import linguistic_signature
from encoders.binary_prime import binary_prime_signature


# ===================== CHALDEAN TESTS =====================

def test_chaldean_mapping():
    """Chaldean mapping: A=1, I=1, J=1, Q=1, Y=1, B=2, etc."""
    sig = chaldean_signature("A")
    assert sig.total == 1
    sig = chaldean_signature("B")
    assert sig.total == 2
    sig = chaldean_signature("F")
    assert sig.total == 8
    print("✓ test_chaldean_mapping passed")


def test_chaldean_capt():
    """CAPT in Chaldean: C=3, A=1, P=8, T=4 = 16 → 7"""
    sig = chaldean_signature("CAPT")
    assert sig.compound_number == 16, f"Expected 16, got {sig.compound_number}"
    assert sig.reduced == 7, f"Expected 7, got {sig.reduced}"
    print("✓ test_chaldean_capt passed")


def test_chaldean_no_master():
    """Chaldean does NOT preserve master numbers."""
    sig = chaldean_signature("AJS")  # 1+1+3 = 5
    assert sig.reduced <= 9
    print("✓ test_chaldean_no_master passed")


def test_chaldean_case_insensitive():
    sig1 = chaldean_signature("CAPT")
    sig2 = chaldean_signature("Capt")
    assert sig1.total == sig2.total
    print("✓ test_chaldean_case_insensitive passed")


# ===================== ORDINAL TESTS =====================

def test_ordinal_standard():
    """A=1, B=2, ..., Z=26. 'AB' = 1+2 = 3"""
    sig = ordinal_signature("AB")
    assert sig.ordinal_total == 3
    print("✓ test_ordinal_standard passed")


def test_ordinal_reverse():
    """A=26, B=25, ..., Z=1. 'AB' = 26+25 = 51"""
    sig = ordinal_signature("AB")
    assert sig.reverse_total == 51
    print("✓ test_ordinal_reverse passed")


def test_ordinal_reduced():
    """Digital root of each letter. 'A' → 1, 'J' → 1 (10→1)"""
    sig = ordinal_signature("J")
    assert sig.reduced_total == 1  # J=10, digital_root(10)=1
    print("✓ test_ordinal_reduced passed")


def test_ordinal_capt():
    """CAPT: C=3, A=1, P=16, T=20 → ordinal=40, reverse=24+26+11+7=68"""
    sig = ordinal_signature("CAPT")
    assert sig.ordinal_total == 40
    assert sig.reverse_total == 68
    print("✓ test_ordinal_capt passed")


def test_ordinal_palindrome():
    """Ordinal should compute without error for various inputs."""
    sig = ordinal_signature("HELLO")
    assert sig.ordinal_total > 0
    print("✓ test_ordinal_palindrome passed")


# ===================== LINGUISTIC TESTS =====================

def test_linguistic_entropy():
    """Shannon entropy should be positive for non-empty strings."""
    sig = linguistic_signature("CAPT")
    assert sig.shannon_entropy > 0
    assert sig.entropy_ratio > 0
    print("✓ test_linguistic_entropy passed")


def test_linguistic_vowel_ratio():
    """CAPT: A is 1 of 4 letters → 0.25"""
    sig = linguistic_signature("CAPT")
    assert abs(sig.vowel_ratio - 0.25) < 0.01
    print("✓ test_linguistic_vowel_ratio passed")


def test_linguistic_bigrams():
    """CAPT bigrams: CA, AP, PT"""
    sig = linguistic_signature("CAPT")
    assert len(sig.bigrams) == 3
    print("✓ test_linguistic_bigrams passed")


def test_linguistic_syllables():
    """CAPT has ~1 syllable."""
    sig = linguistic_signature("CAPT")
    assert sig.syllable_estimate >= 1
    print("✓ test_linguistic_syllables passed")


def test_linguistic_plosives():
    """CAPT has P(plosive), T(plosive) = 2 plosives. C is NOT a plosive."""
    sig = linguistic_signature("CAPT")
    assert sig.plosive_count == 2
    print("✓ test_linguistic_plosives passed")


def test_linguistic_unique_letters():
    """CAPT has 4 unique letters."""
    sig = linguistic_signature("CAPT")
    assert sig.unique_letters == 4
    print("✓ test_linguistic_unique_letters passed")


def test_linguistic_repetition():
    """AAA has letter_repetition_ratio close to 0.67."""
    sig = linguistic_signature("AAA")
    assert sig.letter_repetition_ratio > 0.5
    print("✓ test_linguistic_repetition passed")


# ===================== BINARY/PRIME TESTS =====================

def test_binary_string():
    """CAPT: C=C(consonant=1), A=V(vowel=0), P=C(1), T=C(1) → 1011"""
    sig = binary_prime_signature("CAPT")
    assert sig.binary_string == "1011"
    print("✓ test_binary_string passed")


def test_binary_as_int():
    """1011 in binary = 11 in decimal."""
    sig = binary_prime_signature("CAPT")
    assert sig.binary_as_int == 11
    print("✓ test_binary_as_int passed")


def test_binary_weight():
    """CAPT has 3 consonants → weight=3."""
    sig = binary_prime_signature("CAPT")
    assert sig.binary_weight == 3
    print("✓ test_binary_weight passed")


def test_prime_values():
    """CAPT primes: C=5, A=2, P=8... wait, P=16th letter=53?"""
    sig = binary_prime_signature("CAPT")
    # C is 3rd letter → prime index 2 → PRIMES[2]=5
    # A is 1st letter → prime index 0 → PRIMES[0]=2
    # P is 16th letter → prime index 15 → PRIMES[15]=53
    # T is 20th letter → prime index 19 → PRIMES[19]=71
    assert sig.prime_values == [5, 2, 53, 71]
    assert sig.prime_total == 131
    print("✓ test_prime_values passed")


def test_polarity():
    """CAPT vowel_power=A(2), consonant_power=C(5)+P(53)+T(71)=129 → polarity negative."""
    sig = binary_prime_signature("CAPT")
    assert sig.polarity_score < 0  # consonant-dominant
    print("✓ test_polarity passed")


def test_binary_entropy():
    """Binary entropy of 1011 (3 ones, 1 zero) should be < 1.0."""
    sig = binary_prime_signature("CAPT")
    assert 0 < sig.binary_entropy < 1.0
    print("✓ test_binary_entropy passed")


# ===================== CROSS-ENCODER TESTS =====================

def test_cross_encoder_consistency():
    """All encoders should handle empty string."""
    for fn in [pythagorean_signature, chaldean_signature, ordinal_signature,
               linguistic_signature, binary_prime_signature]:
        sig = fn("")
        assert sig is not None
    print("✓ test_cross_encoder_consistency passed")


def test_cross_encoder_capt():
    """CAPT should produce consistent results across encoders."""
    pyth = pythagorean_signature("CAPT")
    chald = chaldean_signature("CAPT")
    ordi = ordinal_signature("CAPT")
    ling = linguistic_signature("CAPT")
    bp = binary_prime_signature("CAPT")

    # All should have normalized_text = "CAPT"
    assert pyth.normalized_text == "CAPT"
    assert chald.normalized_text == "CAPT"
    assert ordi.normalized_text == "CAPT"
    assert ling.normalized_text == "CAPT"
    assert bp.normalized_text == "CAPT"

    # All should have 4 letters
    assert pyth.total > 0
    assert chald.total > 0
    assert ordi.ordinal_total > 0
    assert ling.letter_count == 4
    assert bp.binary_weight == 3
    print("✓ test_cross_encoder_capt passed")


# ===================== RUN ALL =====================

def run_all():
    tests = [
        # Chaldean
        test_chaldean_mapping,
        test_chaldean_capt,
        test_chaldean_no_master,
        test_chaldean_case_insensitive,
        # Ordinal
        test_ordinal_standard,
        test_ordinal_reverse,
        test_ordinal_reduced,
        test_ordinal_capt,
        test_ordinal_palindrome,
        # Linguistic
        test_linguistic_entropy,
        test_linguistic_vowel_ratio,
        test_linguistic_bigrams,
        test_linguistic_syllables,
        test_linguistic_plosives,
        test_linguistic_unique_letters,
        test_linguistic_repetition,
        # Binary/Prime
        test_binary_string,
        test_binary_as_int,
        test_binary_weight,
        test_prime_values,
        test_polarity,
        test_binary_entropy,
        # Cross-encoder
        test_cross_encoder_consistency,
        test_cross_encoder_capt,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Extended Tests: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*60}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
