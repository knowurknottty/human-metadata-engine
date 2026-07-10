"""Provenance-aware symbolic encoder pipeline.

The legacy encoders retain their public APIs.  This module adds a stable
envelope for the expanded systems: every result identifies its convention,
source set, input treatment, and epistemic level.  The values are deterministic
transformations of supplied text and birth data; they are not empirical traits
or predictions.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date
import re
import unicodedata
from typing import Any, Callable


MANIFEST_VERSION = "symbolic-systems-v1"

# In insertion order, grouped by the user's four delivery phases followed by
# the named structural integrations.
ROADMAP_SYSTEMS: dict[str, str] = {
    "kabbalah_tree_of_life": "phase_1",
    "sacred_geometry": "phase_1",
    "alchemical_transformation": "phase_1",
    "sumerian_sexagesimal": "phase_1",
    "hermetic_principles": "phase_1",
    "tarot": "phase_2",
    "babylonian_planetary": "phase_2",
    "hermes_thoth_nabu": "phase_2",
    "solomonic": "phase_2",
    "arabic_abjad": "phase_2",
    "chinese": "phase_3",
    "egyptian": "phase_3",
    "vedic_jyotish": "phase_3",
    "mayan_tzolkin": "phase_3",
    "cuneiform_magic": "phase_3",
    "elder_futhark": "phase_4",
    "ogham": "phase_4",
    "egyptian_maat": "phase_4",
    "mandaean_duodecimal": "phase_4",
    "tartaria_architecture": "phase_4",
    "indus_valley": "phase_4",
    "unicode_codepoint": "phase_4",
    "apollonius": "structural",
    "temporal_numerology": "structural",
    "esoteric_bridge": "structural",
}

# Source IDs refer to the repository's provenance document.  Some traditions
# have multiple internally divergent lineages; the convention field names the
# selected computational convention rather than silently blending them.
SYSTEM_PROVENANCE: dict[str, dict[str, Any]] = {
    "kabbalah_tree_of_life": {"convention": "ten-sephirot-and-22-paths-v1", "source_ids": ["SRC-KABBALAH-TREE", "SRC-HEBREW-NUMERALS"]},
    "sacred_geometry": {"convention": "integer-patterns-tetractys-polygon-v1", "source_ids": ["SRC-PYTHAGOREAN-TETRACTYS"]},
    "alchemical_transformation": {"convention": "four-color-work-v1", "source_ids": ["SRC-ALCHEMY-FOUR-STAGES"]},
    "sumerian_sexagesimal": {"convention": "base-60-place-value-v1", "source_ids": ["SRC-MESOPOTAMIAN-SEXAGESIMAL"]},
    "hermetic_principles": {"convention": "seven-principles-modern-hermetic-v1", "source_ids": ["SRC-HERMETIC-SEVEN-PRINCIPLES"]},
    "tarot": {"convention": "rider-waite-smith-major-arcana-v1", "source_ids": ["SRC-TAROT-RWS"]},
    "babylonian_planetary": {"convention": "chaldean-planetary-order-v1", "source_ids": ["SRC-CHALDEAN-ORDER"]},
    "hermes_thoth_nabu": {"convention": "comparative-deity-lineage-v1", "source_ids": ["SRC-HERMES-THOTH-NABU"]},
    "solomonic": {"convention": "planetary-and-shem-index-v1", "source_ids": ["SRC-KEY-OF-SOLOMON", "SRC-SHEM-72"]},
    "arabic_abjad": {"convention": "abjad-kabir-eastern-order-v1", "source_ids": ["SRC-ARABIC-ABJAD"]},
    "chinese": {"convention": "king-wen-wu-xing-year-pillar-v1", "source_ids": ["SRC-YIJING-KING-WEN", "SRC-WU-XING", "SRC-SEXAGENARY-CYCLE"]},
    "egyptian": {"convention": "uniliteral-transliteration-and-36-decans-v1", "source_ids": ["SRC-EGYPTIAN-UNILITERALS", "SRC-EGYPTIAN-DECANS"]},
    "vedic_jyotish": {"convention": "birth-requirements-and-nakshatra-index-v1", "source_ids": ["SRC-JYOTISH-NAKSHATRA"]},
    "mayan_tzolkin": {"convention": "gmt-correlation-tzolkin-v1", "source_ids": ["SRC-MAYAN-TZOLKIN"]},
    "cuneiform_magic": {"convention": "unicode-sign-structural-analysis-v1", "source_ids": ["SRC-CUNEIFORM-UNICODE"]},
    "elder_futhark": {"convention": "24-rune-futhark-order-v1", "source_ids": ["SRC-ELDER-FUTHARK"]},
    "ogham": {"convention": "medieval-ogham-letter-tree-v1", "source_ids": ["SRC-OGHAM-TREES"]},
    "egyptian_maat": {"convention": "symbolic-balance-index-v1", "source_ids": ["SRC-MAAT"]},
    "mandaean_duodecimal": {"convention": "base-12-representation-v1", "source_ids": ["SRC-MANDAEAN-TRADITION"]},
    "tartaria_architecture": {"convention": "architectural-proportion-only-v1", "source_ids": ["SRC-ARCHITECTURAL-PROPORTION"]},
    "indus_valley": {"convention": "undeciphered-sign-structure-v1", "source_ids": ["SRC-INDUS-UNDECIPHERED"]},
    "unicode_codepoint": {"convention": "unicode-scalar-value-v1", "source_ids": ["SRC-UNICODE-STANDARD"]},
    "apollonius": {"convention": "existing-apollonius-module-v1", "source_ids": ["SRC-APOLLONIUS-PHILOSTRATUS"]},
    "temporal_numerology": {"convention": "pythagorean-life-path-personal-year-v1", "source_ids": ["SRC-PYTHAGOREAN-NUMEROLOGY"]},
    "esoteric_bridge": {"convention": "explicit-number-correspondence-v1", "source_ids": ["SRC-TAROT-KABBALAH-CORRESPONDENCE", "SRC-CHALDEAN-ORDER"]},
}


# The built-in profile is intentionally finite.  Unknown code points remain in
# original_text and are surfaced through Unicode analysis instead of being
# silently converted into a made-up Latin spelling.
TRANSLITERATION_PROFILE = "builtin-v1"
TRANSLITERATION: dict[str, str] = {
    # Greek
    "Α": "A", "Β": "B", "Γ": "G", "Δ": "D", "Ε": "E", "Ζ": "Z", "Η": "E", "Θ": "TH", "Ι": "I", "Κ": "K", "Λ": "L", "Μ": "M", "Ν": "N", "Ξ": "X", "Ο": "O", "Π": "P", "Ρ": "R", "Σ": "S", "Τ": "T", "Υ": "Y", "Φ": "PH", "Χ": "CH", "Ψ": "PS", "Ω": "O",
    # Hebrew (consonantal transliteration, including finals)
    "א": "A", "ב": "B", "ג": "G", "ד": "D", "ה": "H", "ו": "V", "ז": "Z", "ח": "CH", "ט": "T", "י": "Y", "כ": "K", "ך": "K", "ל": "L", "מ": "M", "ם": "M", "נ": "N", "ן": "N", "ס": "S", "ע": "O", "פ": "P", "ף": "P", "צ": "TS", "ץ": "TS", "ק": "Q", "ר": "R", "ש": "SH", "ת": "TH",
    # Arabic (letters used in Arabic Abjad; diacritics normalize away)
    "ا": "A", "أ": "A", "إ": "A", "آ": "A", "ب": "B", "ج": "J", "د": "D", "ه": "H", "ة": "H", "و": "W", "ز": "Z", "ح": "H", "ط": "T", "ي": "Y", "ى": "Y", "ك": "K", "ل": "L", "م": "M", "ن": "N", "س": "S", "ع": "A", "ف": "F", "ص": "S", "ق": "Q", "ر": "R", "ش": "SH", "ت": "T", "ث": "TH", "خ": "KH", "ذ": "DH", "ض": "D", "ظ": "Z", "غ": "GH", "پ": "P", "چ": "CH", "ژ": "ZH", "گ": "G",
    # Cyrillic (common Russian transliteration)
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "E", "Ж": "ZH", "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M", "Н": "N", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "KH", "Ц": "TS", "Ч": "CH", "Ш": "SH", "Щ": "SHCH", "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E", "Ю": "YU", "Я": "YA",
    # A bounded Devanagari profile.  Vowel marks are deliberately omitted from
    # Latin-only encoders until a full Indic transliteration package is added.
    "अ": "A", "आ": "A", "इ": "I", "ई": "I", "उ": "U", "ऊ": "U", "ए": "E", "ओ": "O", "क": "K", "ख": "KH", "ग": "G", "घ": "GH", "च": "CH", "ज": "J", "ट": "T", "ड": "D", "त": "T", "द": "D", "न": "N", "प": "P", "ब": "B", "म": "M", "य": "Y", "र": "R", "ल": "L", "व": "V", "श": "SH", "स": "S", "ह": "H",
}

ARABIC_ABJAD = {
    "ا": 1, "أ": 1, "إ": 1, "آ": 1, "ب": 2, "ج": 3, "د": 4,
    "ه": 5, "ة": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9, "ي": 10,
    "ى": 10, "ك": 20, "ل": 30, "م": 40, "ن": 50, "س": 60,
    "ع": 70, "ف": 80, "ص": 90, "ق": 100, "ر": 200, "ش": 300,
    "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900,
    "غ": 1000,
}

TAROT_MAJOR = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower",
    "The Star", "The Moon", "The Sun", "Judgement", "The World",
]
HERMETIC_PRINCIPLES = [
    "Mentalism", "Correspondence", "Vibration", "Polarity", "Rhythm",
    "Cause and Effect", "Gender",
]
ALCHEMICAL_STAGES = ["Nigredo", "Albedo", "Citrinitas", "Rubedo"]
CHALDEAN_PLANETS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
HERMES_THOTH_NABU = [
    {"name": "Hermes", "culture": "Greek"},
    {"name": "Thoth", "culture": "Egyptian"},
    {"name": "Nabu", "culture": "Mesopotamian"},
]
WU_XING = ["Wood", "Fire", "Earth", "Metal", "Water"]
TRIGRAMS = ["Qian", "Dui", "Li", "Zhen", "Xun", "Kan", "Gen", "Kun"]
TZOLKIN_NAMES = [
    "Imix", "Ik'", "Ak'b'al", "K'an", "Chikchan", "Kimi", "Manik'",
    "Lamat", "Muluk", "Ok", "Chuwen", "Eb'", "B'en", "Ix", "Men",
    "K'ib'", "Kab'an", "Etz'nab'", "Kawak", "Ajaw",
]
FUTHARK = [
    ("F", "Fehu"), ("U", "Uruz"), ("TH", "Thurisaz"), ("A", "Ansuz"),
    ("R", "Raidho"), ("K", "Kenaz"), ("G", "Gebo"), ("W", "Wunjo"),
    ("H", "Hagalaz"), ("N", "Nauthiz"), ("I", "Isa"), ("J", "Jera"),
    ("EI", "Eihwaz"), ("P", "Perthro"), ("Z", "Algiz"), ("S", "Sowilo"),
    ("T", "Tiwaz"), ("B", "Berkano"), ("E", "Ehwaz"), ("M", "Mannaz"),
    ("L", "Laguz"), ("NG", "Ingwaz"), ("D", "Dagaz"), ("O", "Othala"),
]
OGHAM_TREES = {
    "B": "Birch", "L": "Rowan", "F": "Alder", "S": "Willow", "N": "Ash",
    "H": "Hawthorn", "D": "Oak", "T": "Holly", "C": "Hazel", "Q": "Apple",
    "M": "Vine", "G": "Ivy", "NG": "Reed", "Z": "Blackthorn", "R": "Elder",
    "A": "Pine", "O": "Furze", "U": "Heather", "E": "Aspen", "I": "Yew",
}


def _script_for_char(char: str) -> str | None:
    value = ord(char)
    if 0x0590 <= value <= 0x05FF:
        return "Hebrew"
    if 0x0600 <= value <= 0x06FF or 0x0750 <= value <= 0x077F:
        return "Arabic"
    if 0x0370 <= value <= 0x03FF or 0x1F00 <= value <= 0x1FFF:
        return "Greek"
    if 0x0400 <= value <= 0x052F:
        return "Cyrillic"
    if 0x0900 <= value <= 0x097F:
        return "Devanagari"
    if 0x4E00 <= value <= 0x9FFF or 0x3400 <= value <= 0x4DBF:
        return "Han"
    if 0x12000 <= value <= 0x123FF:
        return "Cuneiform"
    if 0x13000 <= value <= 0x1342F:
        return "Egyptian_Hieroglyphs"
    if 0x16A0 <= value <= 0x16FF:
        return "Runic"
    if 0x1680 <= value <= 0x169F:
        return "Ogham"
    if 0x0840 <= value <= 0x085F:
        return "Mandaic"
    if char.isalpha() and char.isascii():
        return "Latin"
    return None


def prepare_encoding_input(text: str) -> dict[str, Any]:
    """Preserve source Unicode while making a named transliteration available."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = unicodedata.normalize("NFKC", text)
    scripts: list[str] = []
    pieces: list[str] = []
    for char in normalized:
        script = _script_for_char(char)
        if script and script != "Latin" and script not in scripts:
            scripts.append(script)
        if char.isspace() or char in "-_":
            pieces.append(" ")
            continue
        upper = char.upper()
        if upper in TRANSLITERATION:
            pieces.append(TRANSLITERATION[upper])
        elif upper.isascii() and upper.isalpha():
            pieces.append(upper)
        else:
            decomposed = unicodedata.normalize("NFKD", upper)
            ascii_piece = "".join(c for c in decomposed if c.isascii() and c.isalpha())
            pieces.append(ascii_piece)
    latin = re.sub(r"\s+", " ", "".join(pieces)).strip()
    return {
        "original_text": text,
        "normalized_text": normalized,
        "scripts": scripts,
        "latin_transliteration": latin,
        "transliteration_profile": TRANSLITERATION_PROFILE,
    }


def _letters(context: dict[str, Any]) -> list[str]:
    return [char for char in context["latin_transliteration"] if "A" <= char <= "Z"]


def _letter_total(context: dict[str, Any]) -> int:
    return sum(ord(char) - ord("A") + 1 for char in _letters(context))


def _reduce(number: int) -> int:
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number


def _base(number: int, base: int) -> list[int]:
    if number == 0:
        return [0]
    result: list[int] = []
    while number:
        result.append(number % base)
        number //= base
    return list(reversed(result))


def _birth_date(birth: dict[str, Any] | None) -> date | None:
    if not birth:
        return None
    try:
        return date(int(birth["year"]), int(birth["month"]), int(birth["day"]))
    except (KeyError, TypeError, ValueError):
        return None


def _as_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def _kabbalah(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    from .kabbalah import kabbalah_signature

    signature = _as_plain(kabbalah_signature(context["latin_transliteration"]))
    return {
        "total_value": signature["total_value"],
        "reduced_value": signature["reduced_value"],
        "dominant_sephirah": signature["dominant_sephirah_name"],
        "tree_depth": signature["tree_depth"],
        "unique_paths": signature["unique_paths"],
    }


def _sacred_geometry(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    sides = 3 + (total % 6)
    return {
        "letter_total": total,
        "digital_root": _reduce(total),
        "polygon_sides": sides,
        "tetractys_layer": (total - 1) % 10 + 1 if total else 0,
        "geometric_operation": "integer-indexed symbolic correspondence",
    }


def _alchemy(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {
        "letter_total": total,
        "stage_index": total % 4 if total else 0,
        "stage": ALCHEMICAL_STAGES[total % 4] if total else None,
        "operation": "symbolic four-stage index",
    }


def _sexagesimal(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {"decimal_total": total, "base_60_digits": _base(total, 60), "place_value_base": 60}


def _hermetic(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {
        "letter_total": total,
        "principle_index": (total - 1) % 7 + 1 if total else 0,
        "principle": HERMETIC_PRINCIPLES[(total - 1) % 7] if total else None,
    }


def _tarot(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    index = total % 22
    suits = ["Wands", "Cups", "Swords", "Pentacles"]
    return {
        "letter_total": total,
        "major_arcana_index": index,
        "major_arcana": TAROT_MAJOR[index],
        "minor_arcana_suit": suits[total % 4],
        "minor_arcana_rank": (total - 1) % 14 + 1 if total else 0,
    }


def _babylonian_planetary(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    index = (total - 1) % 7 if total else 0
    return {"letter_total": total, "chaldean_order_index": index + 1 if total else 0, "planet": CHALDEAN_PLANETS[index] if total else None}


def _lineage(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    correspondence = HERMES_THOTH_NABU[(total - 1) % 3] if total else None
    return {"letter_total": total, "correspondence": correspondence, "scope": "comparative symbolic lineage; not historical identity"}


def _solomonic(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {
        "letter_total": total,
        "planet": CHALDEAN_PLANETS[(total - 1) % 7] if total else None,
        "shem_index": (total - 1) % 72 + 1 if total else 0,
        "entity_name_included": False,
        "scope": "indexing only; no invocation or ritual instruction",
    }


def _abjad(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    native = [char for char in context["normalized_text"] if char in ARABIC_ABJAD]
    if native:
        values = [{"char": char, "value": ARABIC_ABJAD[char]} for char in native]
        mode = "native-arabic-abjad"
    else:
        values = [{"char": char, "value": ord(char) - ord("A") + 1} for char in _letters(context)]
        mode = "latin-transliteration-proxy"
    total = sum(item["value"] for item in values)
    return {"abjad_total": total, "reduced": _reduce(total), "letter_values": values, "input_mode": mode}


def _chinese(context: dict[str, Any], birth: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    han = [char for char in context["normalized_text"] if _script_for_char(char) == "Han"]
    total = sum(ord(char) for char in han) if han else _letter_total(context)
    birth_day = _birth_date(birth)
    year_pillar = None
    if birth_day:
        stem = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"][(birth_day.year - 4) % 10]
        branch = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"][(birth_day.year - 4) % 12]
        year_pillar = f"{stem}-{branch}"
    return {
        "iching_hexagram_index": (total - 1) % 64 + 1 if total else 0,
        "trigram": TRIGRAMS[total % 8] if total else None,
        "wu_xing_element": WU_XING[total % 5] if total else None,
        "year_pillar": year_pillar,
        "bazi_scope": "year pillar only; full Four Pillars requires solar-term-aware birth time and location",
        "stroke_count": None,
        "stroke_count_scope": "requires a supplied or licensed character-stroke dictionary",
        "han_characters": han,
    }


def _egyptian(context: dict[str, Any], birth: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    letters = _letters(context)
    birth_day = _birth_date(birth)
    return {
        "uniliteral_transliteration": "".join(letters),
        "hieroglyphic_unicode_count": sum(1 for char in context["normalized_text"] if _script_for_char(char) == "Egyptian_Hieroglyphs"),
        "decan_index": ((birth_day.timetuple().tm_yday - 1) // 10) + 1 if birth_day else None,
        "decan_scope": "civil-calendar tenth only; not an astronomical reconstruction",
    }


def _vedic(context: dict[str, Any], birth: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    birth_day = _birth_date(birth)
    return {
        "birth_data_available": bool(birth_day),
        "nakshatra": None,
        "calculation_status": "requires ephemeris, precise time, timezone, and location",
        "required_fields": ["year", "month", "day", "hour", "minute", "timezone_offset", "lat", "lon"],
        "scope": "no inferred sidereal placement is emitted from incomplete data",
    }


def _mayan(context: dict[str, Any], birth: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    birth_day = _birth_date(birth)
    if not birth_day:
        return {"available": False, "calculation_status": "requires Gregorian birth date"}
    # 2012-12-21 is 4 Ajaw in the common GMT correlation.
    delta = (birth_day - date(2012, 12, 21)).days
    return {
        "available": True,
        "correlation": "GMT",
        "tzolkin_number": ((3 + delta) % 13) + 1,
        "tzolkin_day": TZOLKIN_NAMES[(19 + delta) % 20],
    }


def _cuneiform(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    signs = [char for char in context["normalized_text"] if _script_for_char(char) == "Cuneiform"]
    return {
        "sign_count": len(signs),
        "codepoints": [f"U+{ord(char):04X}" for char in signs],
        "lexical_decoding": "not attempted",
        "scope": "structural Unicode-sign analysis only",
    }


def _futhark(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    remaining = "".join(_letters(context))
    matched: list[str] = []
    value = 0
    # Digraphs are resolved before their single-letter overlap.
    for token, rune in sorted(FUTHARK, key=lambda item: len(item[0]), reverse=True):
        count = remaining.count(token)
        if count:
            matched.extend([rune] * count)
            value += (FUTHARK.index((token, rune)) + 1) * count
            remaining = remaining.replace(token, "")
    return {"runes": matched, "rune_total": value, "unmapped_latin": remaining}


def _ogham(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    name = "".join(_letters(context))
    matches: list[dict[str, str]] = []
    cursor = 0
    while cursor < len(name):
        token = name[cursor:cursor + 2] if name[cursor:cursor + 2] in OGHAM_TREES else name[cursor]
        if token in OGHAM_TREES:
            matches.append({"letter": token, "tree": OGHAM_TREES[token]})
        cursor += len(token)
    return {"tree_letters": matches, "tree_count": len(matches)}


def _maat(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    letters = _letters(context)
    vowels = sum(char in "AEIOU" for char in letters)
    consonants = len(letters) - vowels
    balance = 1.0 - abs(vowels - consonants) / len(letters) if letters else 0.0
    return {"vowels": vowels, "consonants": consonants, "symbolic_balance": round(balance, 4), "scope": "formal letter balance, not a moral assessment"}


def _mandaean(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {"decimal_total": total, "base_12_digits": _base(total, 12), "scope": "duodecimal representation; no lexical Mandaic reading is inferred"}


def _tartaria(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    return {
        "polygon_sides": 3 + total % 6 if total else 0,
        "proportion_index": total % 144 if total else 0,
        "historical_claim_status": "Tartaria is not treated as an established historical polity or architectural tradition",
        "scope": "architectural-proportion symbolism only",
    }


def _indus(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    # Unicode does not encode Indus signs as a named block; preserve and
    # characterize the supplied symbols without assigning readings.
    symbols = [char for char in context["normalized_text"] if not char.isspace()]
    return {"undeciphered": True, "symbol_count": len(symbols), "codepoints": [f"U+{ord(char):04X}" for char in symbols], "lexical_reading": None}


def _unicode(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    codepoints = [ord(char) for char in context["normalized_text"]]
    return {
        "codepoints": [f"U+{point:04X}" for point in codepoints],
        "codepoint_sum": sum(codepoints),
        "utf8_byte_length": len(context["normalized_text"].encode("utf-8")),
        "scripts": context["scripts"],
    }


def _apollonius(context: dict[str, Any], **_: Any) -> dict[str, Any]:
    from .apollonius import apollonius_signature

    if not _letters(context):
        return {
            "available": False,
            "calculation_status": "requires Latin text or a supported transliteration",
            "scope": "original input remains available to native-script encoders",
        }
    signature = _as_plain(apollonius_signature(context["latin_transliteration"]))
    return {
        "total_value": signature["total_value"],
        "reduced_total": signature["reduced_total"],
        "dominant_planet": signature["dominant_planet"],
        "primary_virtue": signature["primary_virtue"],
        "divine_contemplation": round(signature["divine_contemplation"], 4),
    }


def _temporal(context: dict[str, Any], birth: dict[str, Any] | None = None, as_of_year: int | None = None, **_: Any) -> dict[str, Any]:
    birth_day = _birth_date(birth)
    if not birth_day:
        return {"available": False, "calculation_status": "requires year, month, and day"}
    life_path = _reduce(sum(int(digit) for digit in birth_day.strftime("%Y%m%d")))
    year = int(as_of_year) if as_of_year is not None else birth_day.year
    personal_year = _reduce(_reduce(birth_day.month) + _reduce(birth_day.day) + _reduce(year))
    return {"available": True, "life_path": life_path, "birthday_number": _reduce(birth_day.day), "personal_year": personal_year, "as_of_year": year}


def _bridge(context: dict[str, Any], birth: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    total = _letter_total(context)
    tarot_index = total % 22
    planet = CHALDEAN_PLANETS[(total - 1) % 7] if total else None
    # Keep the bridge explicit: each link reports the upstream convention and
    # value, never a claim that one tradition historically proves another.
    return {
        "bridge_type": "Tarot-Kabbalah-Astrology-Numerology",
        "links": {
            "tarot": {"major_arcana_index": tarot_index, "major_arcana": TAROT_MAJOR[tarot_index]},
            "kabbalah": {"number": _reduce(total), "mapping": "sephirot-number index"},
            "astrology": {"planet": planet, "mapping": "Chaldean planetary order"},
            "numerology": {"reduced_number": _reduce(total), "source": "Latin transliteration A1Z26"},
        },
        "birth_data_used": bool(_birth_date(birth)),
        "scope": "explicit convention bridge; comparative, not empirical validation",
    }


BUILDERS: dict[str, Callable[..., dict[str, Any]]] = {
    "kabbalah_tree_of_life": _kabbalah, "sacred_geometry": _sacred_geometry,
    "alchemical_transformation": _alchemy, "sumerian_sexagesimal": _sexagesimal,
    "hermetic_principles": _hermetic, "tarot": _tarot,
    "babylonian_planetary": _babylonian_planetary, "hermes_thoth_nabu": _lineage,
    "solomonic": _solomonic, "arabic_abjad": _abjad, "chinese": _chinese,
    "egyptian": _egyptian, "vedic_jyotish": _vedic, "mayan_tzolkin": _mayan,
    "cuneiform_magic": _cuneiform, "elder_futhark": _futhark, "ogham": _ogham,
    "egyptian_maat": _maat, "mandaean_duodecimal": _mandaean,
    "tartaria_architecture": _tartaria, "indus_valley": _indus,
    "unicode_codepoint": _unicode, "apollonius": _apollonius,
    "temporal_numerology": _temporal, "esoteric_bridge": _bridge,
}


def encode_symbolic_systems(
    text: str,
    *,
    birth: dict[str, Any] | None = None,
    as_of_year: int | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute all roadmap systems through one provenance-aware pipeline."""
    context = prepare_encoding_input(text)
    input_mode = "native-and-transliterated" if context["scripts"] else "latin-native"
    results: dict[str, dict[str, Any]] = {}
    for system in ROADMAP_SYSTEMS:
        data = BUILDERS[system](context, birth=birth, as_of_year=as_of_year)
        provenance = dict(SYSTEM_PROVENANCE[system])
        provenance.update({
            "manifest_version": MANIFEST_VERSION,
            "input_mode": input_mode,
            "transliteration_profile": context["transliteration_profile"],
        })
        interpretation = "symbolic"
        if system == "unicode_codepoint":
            interpretation = "computed"
        results[system] = {
            "system": system,
            "phase": ROADMAP_SYSTEMS[system],
            "status": "computed",
            "interpretation_level": interpretation,
            "provenance": provenance,
            "data": data,
        }
    return results
