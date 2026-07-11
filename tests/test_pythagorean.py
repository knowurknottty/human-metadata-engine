"""
Tests for Pythagorean Numerology Encoder
========================================

Verifies the standard Pythagorean mapping and derived calculations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encoders.pythagorean import (
    pythagorean_signature,
    life_path_number,
    normalize_identity,
    reduce_number,
    PYTHAGOREAN_MAP,
    MASTER_NUMBERS,
)


def test_letter_mapping():
    assert PYTHAGOREAN_MAP == {
        "A": 1, "J": 1, "S": 1,
        "B": 2, "K": 2, "T": 2,
        "C": 3, "L": 3, "U": 3,
        "D": 4, "M": 4, "V": 4,
        "E": 5, "N": 5, "W": 5,
        "F": 6, "O": 6, "X": 6,
        "G": 7, "P": 7, "Y": 7,
        "H": 8, "Q": 8, "Z": 8,
        "I": 9, "R": 9,
    }
    print("✓ test_letter_mapping passed")


def test_capt():
    """CAPT: C=3, A=1, P=7, T=2 → 13 → 4."""
    sig = pythagorean_signature("CAPT")
    assert sig.total == 13, f"Expected 13, got {sig.total}"
    assert sig.reduced == 4, f"Expected 4, got {sig.reduced}"
    print("✓ test_capt passed")


def test_case_insensitive():
    sig1 = pythagorean_signature("CAPT")
    sig2 = pythagorean_signature("Capt")
    assert sig1.total == sig2.total
    print("✓ test_case_insensitive passed")


def test_testuser42():
    """TESTUSER: 2+5+1+2+3+1+5+9 = 28 → 10 → 1; digits are ignored."""
    sig = pythagorean_signature("testuser42")
    assert sig.total == 28, f"Expected 28, got {sig.total}"
    assert sig.reduced == 1, f"Expected 1, got {sig.reduced}"
    assert sig.ignored_characters == ["4", "2"]
    print("✓ test_testuser42 passed")


def test_john_michael_smith():
    """JOHN MICHAEL SMITH totals 77 and preserves no master number."""
    sig = pythagorean_signature("John Michael Smith")
    assert sig.total == 77, f"Expected 77, got {sig.total}"
    assert sig.reduced == 5, f"Expected 5, got {sig.reduced}"
    assert sig.master_preserved is None
    print("✓ test_john_michael_smith passed")


def test_life_path():
    """1985-06-15: 1+9+8+5+0+6+1+5 = 35 → 8."""
    lp = life_path_number(1985, 6, 15)
    assert lp.life_path_raw == 35, f"Expected 35, got {lp.life_path_raw}"
    assert lp.life_path_reduced == 8, f"Expected 8, got {lp.life_path_reduced}"
    print("✓ test_life_path passed")


def test_punctuation_ignored():
    sig = pythagorean_signature("Jenn-ai")
    assert sig.normalized_text == "JENNAI"
    assert sig.total == 26
    print("✓ test_punctuation_ignored passed")


def test_intensity_table():
    sig = pythagorean_signature("CAPT")
    assert sig.intensity_table[1] == 1
    assert sig.intensity_table[2] == 1
    assert sig.intensity_table[3] == 1
    assert sig.intensity_table[7] == 1
    assert sig.intensity_table[4] == 0
    assert sig.intensity_table[5] == 0
    print("✓ test_intensity_table passed")


def test_karmic_lessons():
    sig = pythagorean_signature("CAPT")
    assert set(sig.karmic_lessons) == {4, 5, 6, 8, 9}
    print("✓ test_karmic_lessons passed")


def test_vowel_consonant_split():
    sig = pythagorean_signature("CAPT")
    assert len(sig.vowels) == 1
    assert len(sig.consonants) == 3
    assert sig.vowels[0].char == "A"
    print("✓ test_vowel_consonant_split passed")


def test_soul_urge():
    sig = pythagorean_signature("CAPT")
    assert sig.soul_urge == 1
    print("✓ test_soul_urge passed")


def test_personality():
    sig = pythagorean_signature("CAPT")
    assert sig.personality == 3
    print("✓ test_personality passed")


def test_balance_number():
    """John Michael Smith initials: J=1, M=4, S=1 → 6."""
    sig = pythagorean_signature("John Michael Smith")
    assert sig.balance_number == 6, f"Expected balance 6, got {sig.balance_number}"
    print("✓ test_balance_number passed")


def test_master_number_preservation():
    for value in (11, 22, 33):
        reduced, master = reduce_number(value, preserve_master=True)
        assert reduced == value
        assert master == value
    print("✓ test_master_number_preservation passed")


def test_multi_token():
    sig = pythagorean_signature("John Michael Smith")
    assert sig.tokens == ["JOHN", "MICHAEL", "SMITH"]
    assert {lv.token_index for lv in sig.letter_values} == {0, 1, 2}
    print("✓ test_multi_token passed")


def test_hidden_passion():
    sig = pythagorean_signature("AABBCC")
    assert set(sig.hidden_passion) == {1, 2, 3}
    print("✓ test_hidden_passion passed")


def test_empty_string():
    sig = pythagorean_signature("")
    assert sig.total == 0
    assert sig.reduced == 0
    assert len(sig.letter_values) == 0
    print("✓ test_empty_string passed")


def test_normalization_contract():
    normalized, tokens, ignored = normalize_identity("  Capt-RYS_42! ")
    assert normalized == "CAPTRYS"
    # Tokens are produced from the sanitized Unicode/transliteration stream.
    # Discarded digits and punctuation remain auditable in `ignored` but are
    # not preserved as calculation tokens.
    assert tokens == ["CAPT", "RYS"]
    assert ignored == ["4", "2", "!"]
    print("✓ test_normalization_contract passed")


def test_all_tests():
    tests = [
        test_letter_mapping,
        test_capt,
        test_case_insensitive,
        test_testuser42,
        test_john_michael_smith,
        test_life_path,
        test_punctuation_ignored,
        test_intensity_table,
        test_karmic_lessons,
        test_vowel_consonant_split,
        test_soul_urge,
        test_personality,
        test_balance_number,
        test_master_number_preservation,
        test_multi_token,
        test_hidden_passion,
        test_empty_string,
        test_normalization_contract,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as exc:
            print(f"✗ {test.__name__} failed: {exc}")
            failed += 1
        except Exception as exc:
            print(f"✗ {test.__name__} error: {exc}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*60}")
    return failed == 0


if __name__ == "__main__":
    success = test_all_tests()
    sys.exit(0 if success else 1)
