"""Tests for scripts/corpus/pseudonym.py: keyed pseudonyms, card numbers and birth dates (Д1).

Locality [мейнтейнер: 2026-11-01]: every output is a function of the key and the value only, so
these tests need no file, no table and no order of calls.
"""

from __future__ import annotations

import datetime as dt
import unicodedata

import pytest

from scripts.corpus import pseudonym as ps

KEY = b"synthetic test key, not the corpus key"
OTHER_KEY = b"another synthetic test key, not used"


# ---------------------------------------------------------------- key


def test_no_key_is_an_error() -> None:
    with pytest.raises(ps.MissingKeyError):
        ps.load_key({})


def test_a_short_key_is_an_error_that_does_not_quote_it() -> None:
    with pytest.raises(ps.MissingKeyError) as error:
        ps.load_key({ps.KEY_ENV: "short-secret"})
    assert "short-secret" not in str(error.value)


def test_the_key_comes_from_the_environment() -> None:
    assert ps.load_key({ps.KEY_ENV: KEY.decode()}) == KEY


def test_key_id_tells_keys_apart_without_showing_them() -> None:
    assert ps.key_id(KEY) == ps.key_id(KEY)
    assert ps.key_id(KEY) != ps.key_id(OTHER_KEY)
    assert KEY.decode() not in ps.key_id(KEY)


# ---------------------------------------------------------------- normalization


@pytest.mark.parametrize(
    ("raw", "normalized"),
    [
        ("Ёлкина", "елкина"),
        ("ЁЛКИНА", "елкина"),
        ("  Ёлкина \t Анна\u00a0", "елкина анна"),
        (unicodedata.normalize("NFD", "Йошкина"), "йошкина"),
        ("Straße", "strasse"),
    ],
)
def test_normalize_case_yo_and_spaces(raw: str, normalized: str) -> None:
    assert ps.normalize(raw) == normalized


@pytest.mark.parametrize(
    ("raw", "plain"),
    [
        ("Выдумкина", True),
        ("Выдумкина-Придумова", True),
        ("Анна Мария", True),
        ("ВЫДУМКИНА", False),
        ("выдумкина", False),
        ("Ёлкина", False),
        (" Выдумкина", False),
        ("Анна  Мария", False),
        ("де ла Крус", False),
    ],
)
def test_plain_form_is_title_case_with_single_spaces_and_no_yo(raw: str, *, plain: bool) -> None:
    assert ps.is_plain(raw) is plain


# ---------------------------------------------------------------- pseudonyms


def test_pseudonym_is_deterministic_and_keyed() -> None:
    first = ps.pseudonym(KEY, "person", "Синтетикова")
    assert first == ps.pseudonym(KEY, "person", "Синтетикова")
    assert first != ps.pseudonym(OTHER_KEY, "person", "Синтетикова")


def test_empty_stays_empty() -> None:
    assert not ps.pseudonym(KEY, "person", "")


def test_kinds_do_not_share_pseudonyms() -> None:
    assert ps.pseudonym(KEY, "person", "Роза") != ps.pseudonym(KEY, "org", "Роза")


def test_variants_share_the_base_and_stay_distinct() -> None:
    """One person, one base; legacy compares exact strings, so variants stay apart.

    [код: pysport@b548c35 sportorg/models/memory.py:1401-1422] (``multi_day_id``).
    """
    plain = ps.pseudonym(KEY, "person", "Елкина")
    variants = [ps.pseudonym(KEY, "person", v) for v in ("Ёлкина", "ЕЛКИНА", "Елкина ")]
    assert all(v.split("-")[0] == plain for v in variants)
    assert len({plain, *variants}) == 1 + len(variants)


def test_pseudonym_is_one_ascii_token_without_the_original() -> None:
    value = ps.pseudonym(KEY, "person", "Анна Мария")
    assert value.isascii()
    assert " " not in value
    assert "Анна" not in value
    assert any(c.isdigit() for c in value)


def test_different_values_get_different_pseudonyms() -> None:
    values = [f"Синтетик{i}" for i in range(2000)]
    assert len({ps.pseudonym(KEY, "person", v) for v in values}) == len(values)


# ---------------------------------------------------------------- permutation


@pytest.mark.parametrize("size", [2, 3, 10, 365, 1000])
def test_permutation_is_a_bijection_with_an_inverse(size: int) -> None:
    perm = ps.Permutation(KEY, "test", size)
    images = [perm.forward(x) for x in range(size)]
    assert sorted(images) == list(range(size))
    assert all(perm.inverse(perm.forward(x)) == x for x in range(size))


@pytest.mark.parametrize("size", [2, 10, 366])
def test_cycle_is_one_cycle_without_fixed_points(size: int) -> None:
    perm = ps.Permutation(KEY, "test", size)
    seen: list[int] = []
    x = 0
    for _ in range(size):
        seen.append(x)
        x = perm.cycle(x)
    assert x == 0
    assert sorted(seen) == list(range(size))


# ---------------------------------------------------------------- card numbers


def test_card_classes_cover_one_to_si6_star_without_gaps() -> None:
    """[код: sportident 1.2.8 sportident.py:755-778] (the package in legacy's uv.lock)."""
    lows = [low for low, _, _ in ps.CARD_CLASSES]
    highs = [high for _, high, _ in ps.CARD_CLASSES]
    assert lows[0] == 1
    assert highs[-1] == 16_777_215
    assert all(low == high + 1 for low, high in zip(lows[1:], highs[:-1], strict=True))


@pytest.mark.parametrize(
    ("number", "label"),
    [
        (12_345, "SI5"),
        (212_345, "SI5 series 2"),
        (100_000, "gap"),
        (512_345, "SI6"),
        (1_234_567, "SI9"),
        (2_003_100, "SI6 WM2003"),
        (2_345_678, "SI8"),
        (4_123_456, "pCard"),
        (6_123_456, "tCard"),
        (7_123_456, "SI10"),
        (8_123_456, "SIAC1"),
        (9_123_456, "SI11"),
        (14_123_456, "fCard"),
        (16_711_700, "SI6*"),
        (123_456_789, "9 digits"),
    ],
)
def test_card_class(number: int, label: str) -> None:
    assert ps.card_class(number)[2] == label


def test_card_zero_and_negative_stay() -> None:
    assert ps.card_number(KEY, 0) == 0
    assert ps.card_number(KEY, -5) == -5


@pytest.mark.parametrize("number", [7, 212_345, 512_345, 2_003_100, 8_123_456, 123_456_789])
def test_card_stays_in_its_class_and_changes(number: int) -> None:
    new = ps.card_number(KEY, number)
    assert new != number
    assert ps.card_class(new) == ps.card_class(number)
    assert new == ps.card_number(KEY, number)


def test_cards_of_one_class_never_collide() -> None:
    numbers = range(8_000_000, 8_003_000)
    assert len({ps.card_number(KEY, n) for n in numbers}) == len(numbers)


# ---------------------------------------------------------------- birth dates


@pytest.mark.parametrize(
    "text", ["2010-05-17", "2010-01-01", "2012-02-29", "2010-05-17T00:00:00", "17.05.2010"]
)
def test_birth_date_keeps_year_and_format_and_moves_the_day(text: str) -> None:
    new = ps.birth_date(KEY, text)
    assert new is not None
    assert new != text
    assert len(new) == len(text)
    year = text[6:10] if "." in text[:3] else text[:4]
    assert (new[6:10] if "." in new[:3] else new[:4]) == year
    assert new[len("2010-05-17") :] == text[len("2010-05-17") :]  # the time part, if any
    assert new == ps.birth_date(KEY, text)


@pytest.mark.parametrize("text", ["1990-05-17 Выдумкин", "17.05.1990 (approx)", "1990-05-17T"])
def test_text_after_a_birth_date_makes_it_unparsed(text: str) -> None:
    assert ps.birth_date(KEY, text) is None


def test_birth_date_is_a_valid_date_of_the_same_year() -> None:
    new = ps.birth_date(KEY, "2012-02-29")
    assert new is not None
    assert dt.date.fromisoformat(new).year == 2012


def test_unparsed_birth_date_is_none() -> None:
    assert ps.birth_date(KEY, "sometime") is None


def test_national_code_number_keeps_its_digit_count() -> None:
    new = ps.number_code(KEY, 1_234_567)
    assert new != 1_234_567
    assert len(str(new)) == 7


def test_normalize_drops_invisible_format_characters() -> None:
    assert ps.normalize("\ufeffПриду\u00adмкин\u200b") == "придумкин"
