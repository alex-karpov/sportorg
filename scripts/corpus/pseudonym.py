"""Keyed pseudonyms, card numbers and birth dates for the corpus anonymization (Д1, S3).

Every output is a function of the key and the value only: no table of names already given out,
no dependence on the order of calls or on other files (locality, ``[мейнтейнер: 2026-11-01]``).

- ``pseudonym(key, kind, value)``: a base from HMAC of the normalized value (case, ё/е and
  whitespace folded, ``normalize``), so one person or club written alike gets one base across
  races. Legacy compares names as exact strings, for example in ``multi_day_id``
  [код: pysport@b548c35 sportorg/models/memory.py:1401-1422], so a value that is not in the plain
  form (``is_plain``) gets a suffix from HMAC of the exact value: variants share the base and stay
  apart, as they do in legacy.
- ``card_number(key, n)``: a keyed permutation inside the card-type range of ``n`` (one cycle, so
  no number maps to itself), ranges of the ``sportident`` package that legacy locks
  [код: sportident 1.2.8 sportident.py:755-778].
- ``birth_date(key, text)``: the same year, another day of it, by a keyed permutation of the days.

The key comes from ``SPORTORG_ANONYMIZATION_KEY`` and is never printed.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import re
import unicodedata
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping

KEY_ENV: Final = "SPORTORG_ANONYMIZATION_KEY"
MIN_KEY_LENGTH: Final = 16
type Kind = Literal["person", "org", "place", "contact", "code", "text"]
PREFIX: Final[dict[Kind, str]] = {
    "person": "P",
    "org": "O",
    "place": "L",
    "contact": "C",
    "code": "K",
    "text": "T",
}
_ALPHABET: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32
_BASE_CHARS: Final = 9
_SUFFIX_CHARS: Final = 4
_ROUNDS: Final = 8
SI6_STAR_MAX: Final = 16_777_215
# [код: sportident 1.2.8 sportident.py:755-778]; "gap" ranges are numbers no card type documents.
CARD_CLASSES: Final[tuple[tuple[int, int, str], ...]] = (
    (1, 65_000, "SI5"),
    (65_001, 200_000, "gap"),
    (200_001, 265_000, "SI5 series 2"),
    (265_001, 300_000, "gap"),
    (300_001, 365_000, "SI5 series 3"),
    (365_001, 400_000, "gap"),
    (400_001, 465_000, "SI5 series 4"),
    (465_001, 499_999, "gap"),
    (500_000, 999_999, "SI6"),
    (1_000_000, 1_999_999, "SI9"),
    (2_000_000, 2_002_999, "SI8"),
    (2_003_000, 2_003_400, "SI6 WM2003"),
    (2_003_401, 2_999_999, "SI8"),
    (3_000_000, 3_999_999, "gap"),
    (4_000_000, 4_999_999, "pCard"),
    (5_000_000, 5_999_999, "gap"),
    (6_000_000, 6_999_999, "tCard"),
    (7_000_000, 7_999_999, "SI10"),
    (8_000_000, 8_999_999, "SIAC1"),
    (9_000_000, 9_999_999, "SI11"),
    (10_000_000, 13_999_999, "gap"),
    (14_000_000, 14_999_999, "fCard"),
    (15_000_000, 16_711_679, "gap"),
    (16_711_680, SI6_STAR_MAX, "SI6*"),
)
_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})(.*)", re.DOTALL)
_DMY = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})(.*)", re.DOTALL)
_WORD_SEPARATORS = re.compile(r"([ -])")


class MissingKeyError(RuntimeError):
    """No usable anonymization key; the message never quotes the value."""


def load_key(environ: Mapping[str, str]) -> bytes:
    value = environ.get(KEY_ENV, "")
    if len(value) < MIN_KEY_LENGTH:
        msg = f"{KEY_ENV} is not set or shorter than {MIN_KEY_LENGTH} characters"
        raise MissingKeyError(msg)
    return value.encode("utf-8")


def _mac(key: bytes, *parts: str) -> bytes:
    return hmac.new(key, "\0".join(parts).encode("utf-8"), hashlib.sha256).digest()


def keyed_hash(key: bytes, label: str, value: str) -> str:
    """12 hex digits of HMAC: a neutral id that cannot be reversed by guessing the value."""
    return _mac(key, "keyed-hash", label, value).hex()[:12]


def key_id(key: bytes) -> str:
    """Tells keys apart in the manifest without revealing them."""
    return _mac(key, "key-id").hex()[:12]


# ---------------------------------------------------------------- strings


def normalize(value: str) -> str:
    """NFC, case folded, ё → е, whitespace runs to one space, no leading or trailing space."""
    folded = unicodedata.normalize("NFC", unicodedata.normalize("NFC", value).casefold())
    return " ".join(folded.replace("ё", "е").split())


def _display(normalized: str) -> str:
    parts = _WORD_SEPARATORS.split(normalized)
    return "".join(part[:1].upper() + part[1:] for part in parts)


def is_plain(value: str) -> bool:
    """Title-case words, single spaces, no ё: the one spelling that needs no variant suffix."""
    return value == _display(normalize(value))


def _encode(digest: bytes, chars: int) -> str:
    number = int.from_bytes(digest[:8], "big")
    out: list[str] = []
    for _ in range(chars):
        number, digit = divmod(number, len(_ALPHABET))
        out.append(_ALPHABET[digit])
    return "".join(out)


def pseudonym(key: bytes, kind: Kind, value: str) -> str:
    """One ASCII token for a non-empty value; the empty value stays empty."""
    if not value:
        return ""
    digest = _mac(key, "pseudonym", kind, normalize(value))
    base = f"{PREFIX[kind]}{digest[-1] % 10}{_encode(digest, _BASE_CHARS)}"
    if is_plain(value):
        return base
    return f"{base}-{_encode(_mac(key, 'variant', kind, value), _SUFFIX_CHARS)}"


# ---------------------------------------------------------------- numbers


class Permutation:
    """Keyed permutation of ``range(size)``: a Feistel network with cycle walking."""

    def __init__(self, key: bytes, label: str, size: int) -> None:
        if size < 1:
            msg = f"size must be positive, got {size}"
            raise ValueError(msg)
        bits = max(2, (size - 1).bit_length())
        bits += bits % 2
        self._key: bytes = key
        self._label: str = f"{label}\0{size}"
        self._half: int = bits // 2
        self._mask: int = (1 << self._half) - 1
        self.size: int = size

    def _round(self, value: int, index: int) -> int:
        digest = _mac(self._key, "permutation", self._label, str(index), str(value))
        return int.from_bytes(digest[:8], "big") & self._mask

    def _encrypt(self, x: int) -> int:
        left, right = x >> self._half, x & self._mask
        for index in range(_ROUNDS):
            left, right = right, left ^ self._round(right, index)
        return (left << self._half) | right

    def _decrypt(self, y: int) -> int:
        left, right = y >> self._half, y & self._mask
        for index in reversed(range(_ROUNDS)):
            left, right = right ^ self._round(left, index), left
        return (left << self._half) | right

    def forward(self, x: int) -> int:
        y = self._encrypt(x)
        while y >= self.size:
            y = self._encrypt(y)
        return y

    def inverse(self, y: int) -> int:
        x = self._decrypt(y)
        while x >= self.size:
            x = self._decrypt(x)
        return x

    def cycle(self, x: int) -> int:
        """The next element on one cycle through the whole range: never ``x`` itself."""
        if self.size == 1:
            return x
        return self.forward((self.inverse(x) + 1) % self.size)


def card_class(number: int) -> tuple[int, int, str]:
    """``(low, high, label)`` of the card-type range of a positive card number."""
    if number < 1:
        msg = f"card numbers start at 1, got {number}"
        raise ValueError(msg)
    for low, high, label in CARD_CLASSES:
        if low <= number <= high:
            return low, high, label
    digits = len(str(number))
    return max(SI6_STAR_MAX + 1, _pow10(digits - 1)), _pow10(digits) - 1, f"{digits} digits"


def _pow10(exponent: int) -> int:
    """``10 ** exponent`` typed as ``int`` (a negative exponent would give a float)."""
    return int("1".ljust(exponent + 1, "0"))


def _in_range(key: bytes, label: str, low: int, high: int, value: int) -> int:
    return low + Permutation(key, f"{label}/{low}", high - low + 1).cycle(value - low)


def card_number(key: bytes, number: int) -> int:
    """Another number of the same card type; 0 (no card) and negative numbers stay."""
    if number < 1:
        return number
    low, high, label = card_class(number)
    return _in_range(key, f"card/{label}", low, high, number)


def number_code(key: bytes, number: int) -> int:
    """A numeric identifier (``national_code``) as another number with as many digits."""
    if number < 1:
        return number
    digits = len(str(number))
    low = _pow10(digits - 1) if digits > 1 else 1
    return _in_range(key, "number-code", low, _pow10(digits) - 1, number)


def _parse_date(text: str) -> tuple[dt.date, str, bool] | None:
    """The date, the text after it, and whether it was written day first."""
    if match := _ISO.fullmatch(text):
        year, month, day, tail = match.groups()
        day_first = False
    elif match := _DMY.fullmatch(text):
        day, month, year, tail = match.groups()
        day_first = True
    else:
        return None
    try:
        return dt.date(int(year), int(month), int(day)), tail, day_first
    except ValueError:
        return None


def birth_date(key: bytes, text: str) -> str | None:
    """Another day of the same year, written as the input was; ``None`` if not a date."""
    parsed = _parse_date(text)
    if parsed is None:
        return None
    date, tail, day_first = parsed
    first = dt.date(date.year, 1, 1)
    days = (dt.date(date.year + 1, 1, 1) - first).days
    index = Permutation(key, f"birth-date/{date.year}", days).cycle((date - first).days)
    new = first + dt.timedelta(days=index)
    if day_first:
        return f"{new.day:02}.{new.month:02}.{new.year:04}{tail}"
    return f"{new.year:04}-{new.month:02}-{new.day:02}{tail}"
