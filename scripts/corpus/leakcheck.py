"""Leak check (Stage 2 S3): no original name, card number or birth date in what leaves the corpus.

Two uses:

- ``check_pair(original, anonymized)``: one race file against its anonymized copy. Every string
  of the original is classed by its field (Д1): sensitive (``person`` words of names and referees;
  whole values of ``org``, ``place``, ``contact``, ``code``, ``race``, ``text``, ``secret``) or
  kept (groups, courses, settings legacy reads, and every key of the file: keys are the schema;
  old files hold schema words such as ``address`` as values). Whole values shorter than three
  letters or digits are not searched (a thread id ``17`` matches by chance). A sensitive value
  found in the copy is a
  ``leak:<category>``, unless it also stands in a kept field of the original (a group named like a
  person): then it is ``residual:<category>``, a risk for the maintainer, not a fault of the
  anonymizer. Cards, numeric codes and birth dates are compared record by record (by object id):
  a permutation of all numbers of a card type maps some card onto another person's number, so a
  global search would report coincidences.
- ``scan``: text files (evidence, the repository) and commit messages against the sensitive
  values of every race file in the corpus and of legacy's ``tests/data/test.json``, which holds
  personal data ``[мейнтейнер: 2026-10-31]``: surnames (words of four letters or more,
  referees' too), organization names and places (five or more), contacts and codes (whole
  values), card numbers and numeric codes of six digits or more anywhere, shorter card numbers
  (SI5) only as the value of a card field (``"card_number": 12345``), birth dates other than
  1 January (the date legacy stores for a year only
  [код: pysport@b548c35 sportorg/models/memory.py:1379-1399]). Given names and middle names
  (formed from given names) are not searched: too common to tell a leak from a word.
  Five-digit numbers in free text are not searched either: with thousands of SI5 cards in the
  corpus most such numbers would match by chance ``[мейнтейнер: 2026-11-01]``.
  A value that also stands in a kept field of its file (a key of the schema, a group name) or in
  legacy's own texts (status titles, the hints of rule clauses) is not searched: its presence
  in the repository says nothing about the corpus.

Output is counts, categories, file names and line numbers, never the value found: a leak check
that printed its findings would itself send them to the model (``docs/data-request.md``, «Д3 на
практике»).

Files that scripts make only from synthetic inputs (``--synthetic``; their reruns reproduce them
byte for byte without the corpus) can hold a number equal to a card by chance: such hits are
counted apart and do not fail the check.

``--words-out FILE`` writes the matched words themselves, for the maintainer to read locally: the
file must lie outside the repository, and the console still shows only counts and its path.

Usage::

    uv run python -m scripts.corpus.leakcheck scan docs/evidence/stage-2 --commits main..HEAD
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import as_dict, as_list, as_str, parse_json
from scripts.corpus import anonymize, racefile
from scripts.corpus.pseudonym import normalize
from scripts.legacy import ROOT, legacy_dir

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

    from scripts._json import Json

CORPUS_ENV: Final = "SPORTORG_CORPUS"
_TOKEN = re.compile(r"\w+")
_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,40}")
_SPACED_DIGITS = re.compile(r"[0-9]+(?: [0-9]+)*")
_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{2})\.(\d{2})\.(\d{4})")
MIN_TOKEN: Final = 2
MIN_VALUE: Final = 3  # letters and digits; shorter values (a thread id "17") match by chance
MIN_SURNAME: Final = 4
MIN_ORG: Final = 5
MIN_CARD: Final = 100_000
DATE_NUMBERS: Final = range(10_000_000, 100_000_000)  # YYYYMMDD
JAN_FIRST: Final = 101  # MMDD of 1 January
SECRET_SETTINGS: Final = anonymize.CLEARED_SETTINGS | anonymize.TEXT_SETTINGS
PERSON_WORDS: Final = frozenset({"name", "surname", "middle_name"})
ORG_FIELDS: Final[dict[str, str]] = {
    "name": "org",
    "country": "place",
    "region": "place",
    "address": "place",
    "contact": "contact",
    "code": "code",
}
TEXT_CATEGORIES: Final = ("person", "org", "place", "contact", "code", "race", "text", "secret")


@dataclass
class Sensitive:
    """Sensitive values of one race file, and the strings of its kept fields."""

    tokens: set[str] = field(default_factory=set[str])
    values: dict[str, set[str]] = field(default_factory=dict[str, set[str]])
    kept: list[str] = field(default_factory=list[str])
    numbers: dict[str, tuple[str, int]] = field(default_factory=dict[str, tuple[str, int]])
    dates: dict[str, str] = field(default_factory=dict[str, str])
    surnames: set[str] = field(default_factory=set[str])


def _strings(value: Json) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)


def _searched(key: str, value: str) -> str:
    """The text searched for one value: ``multi_day_results`` is one field of 14 characters per day.

    The next day's time follows a cut text with no separator, so the fields are searched apart,
    and the whole string too (a text that does not start on a field boundary).
    """
    if key != anonymize.MULTI_DAY:
        return value
    size = anonymize.DAY_FIELD
    return "\n".join([value, *(value[i : i + size] for i in range(0, len(value), size))])


def _copy_strings(value: Json, key: str = "") -> Iterator[str]:
    """Like ``_strings``, with day fields apart: the strings searched in an anonymized copy."""
    if isinstance(value, str):
        yield _searched(key, value)
    elif isinstance(value, list):
        for item in value:
            yield from _copy_strings(item, key)
    elif isinstance(value, dict):
        for name, item in value.items():
            yield name
            yield from _copy_strings(item, name)


def _values(value: Json) -> Iterator[str]:
    """Strings inside ``value``, without the keys of nested objects."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _values(item)


def tokens(text: str) -> list[str]:
    """Words (runs of letters, digits and ``_``) of a text."""
    return [text[m.start() : m.end()] for m in _TOKEN.finditer(text)]


def iso_date(text: str) -> str | None:
    """``YYYY-MM-DD`` of a date written ISO or day first; ``None`` if it is not one."""
    match = _DATE.match(text)
    if match is None:
        return None
    if match[1]:
        return f"{match[1]}-{match[2]}-{match[3]}"
    return f"{match[6]}-{match[5]}-{match[4]}"


def _whole_number(value: Json) -> int | None:
    """An int, a whole float, or ASCII digits as an int; ``None`` for anything else."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isascii() and value.isdigit():
        return int(value)
    return None


class _Extractor:
    def __init__(self) -> None:
        self.found: Sensitive = Sensitive()

    def value(self, category: str, value: Json) -> None:
        for text in _values(value):
            normalized = normalize(text)
            if sum(c.isalnum() for c in normalized) >= MIN_VALUE:
                self.found.values.setdefault(category, set()).add(normalized)

    def words(self, value: Json) -> None:
        for text in _values(value):
            self.found.tokens.update(t for t in tokens(normalize(text)) if len(t) >= MIN_TOKEN)

    def kept(self, name: str, value: Json) -> None:
        self.found.kept.append(name)
        self.found.kept.extend(_strings(value))

    def number(self, record: str, category: str, value: Json) -> None:
        """A number in any shape: an int, a whole float, digits with spaces (``212 345``)."""
        if isinstance(value, bool):
            return
        number = 0
        if isinstance(value, int):
            number = value
        elif isinstance(value, float) and value.is_integer():
            number = int(value)
        elif isinstance(value, str) and _SPACED_DIGITS.fullmatch(value.strip()):
            number = int("".join(value.split()))
        if number > 0:
            self.found.numbers[record] = (category, number)
        elif category == "code":
            self.value("code", value)

    def name_words(self, name: str, value: Json) -> None:
        self.words(value)
        if name == "surname":
            self.found.surnames.add(normalize(as_str(value)))

    def birth(self, record: str, value: Json) -> None:
        """A date by record; a date written as a number (``19900517``) too."""
        if isinstance(value, str) and (date := iso_date(value)):
            self.found.dates[record] = date
        elif (number := _whole_number(value)) is not None:
            self.found.numbers[record] = ("birth_date", number)

    def person(self, item: Json) -> None:
        person = as_dict(item)
        pid = as_str(person.get("id"))
        for name, value in person.items():
            if name in PERSON_WORDS:
                self.name_words(name, value)
            elif name in anonymize.CARD_KEYS:
                self.number(f"person:{pid}:{name}", "card", value)
            elif name in anonymize.CODE_KEYS:
                self.number(f"person:{pid}:{name}", "code", value)
            elif name in {"birth_date", "birthday"}:
                self.birth(f"person:{pid}:{name}", value)
            elif name in anonymize.PERSON_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)

    def status_comment(self, value: Json) -> None:
        """A rule clause is kept; the free part is sensitive, and as cut into a day field."""
        if not isinstance(value, str):
            self.value("text", value)  # the anonymizer masks every string of it
            return
        free = anonymize.status_comment_free_text(value)
        if free is None:
            self.kept("status_comment", value)
            return
        self.value("text", free)
        if len(value.strip()) > anonymize.DAY_FIELD:  # as cut into a day field
            cut = anonymize.status_comment_free_text(value[: anonymize.DAY_FIELD], cut=True)
            if cut is not None:  # None: a clause, or a start of legacy's hint, which stays
                self.value("text", cut.rstrip(" "))

    def result(self, item: Json) -> None:
        result = as_dict(item)
        rid = as_str(result.get("id"))
        for name, value in result.items():
            if name in anonymize.CARD_KEYS:
                self.number(f"result:{rid}:{name}", "card", value)
            elif name == "status_comment":
                self.status_comment(value)
            elif name in anonymize.RESULT_DERIVED:
                pass  # legacy's copies of the comment and the times: neither kept nor a source
            elif name in anonymize.RESULT_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)

    def organization(self, item: Json) -> None:
        for name, value in as_dict(item).items():
            if name in ORG_FIELDS:
                self.value(ORG_FIELDS[name], value)
            elif name in anonymize.ORG_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)

    def data(self, item: Json) -> None:
        for name, value in as_dict(item).items():
            if name in anonymize.DATA_NEUTRAL:
                self.value("race", value)
            elif name in anonymize.DATA_PERSON:
                self.words(value)
                for text in _values(value):
                    self.found.surnames.add(normalize(text))
            elif name in anonymize.DATA_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)

    def settings(self, item: Json) -> None:
        for name, value in as_dict(item).items():
            if name in SECRET_SETTINGS:
                self.value("secret", value)
            elif name in anonymize.LEGACY_SETTINGS:
                self.kept(name, value)
            else:
                self.value("text", value)

    def race(self, item: Json) -> None:
        handlers = {
            "persons": self.person,
            "results": self.result,
            "organizations": self.organization,
        }
        for name, value in as_dict(item).items():
            if name in handlers:
                for entry in as_list(value):
                    handlers[name](entry)
            elif name == "data":
                self.data(value)
            elif name == "settings":
                self.settings(value)
            elif name in anonymize.RACE_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)  # the anonymizer masks an unknown key as text


def _keys(value: Json) -> Iterator[str]:
    if isinstance(value, list):
        for item in value:
            yield from _keys(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _keys(item)


def extract(doc: Json) -> Sensitive:
    """Every key of the file counts as kept text: keys are the schema, not data.

    So do legacy's status titles, which it writes into the derived result strings.
    """
    extractor = _Extractor()
    for race in racefile.races_of(doc):
        extractor.race(race)
    if isinstance(doc, dict) and "races" in doc:  # the anonymizer masks other keys as text
        for name, value in doc.items():
            if name not in anonymize.FILE_KEPT and name != "races":
                extractor.value("text", value)
    extractor.found.kept.extend(sorted(set(_keys(doc))))
    extractor.found.kept.extend(anonymize.LEGACY_STATUS_TITLES)
    return extractor.found


def _bounded(text: str, value: str) -> bool:
    """``value`` occurs in ``text`` between non-word characters."""
    start = text.find(value)
    while start >= 0:
        end = start + len(value)
        before = text[start - 1] if start else " "
        after = text[end] if end < len(text) else " "
        if not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_"):
            return True
        start = text.find(value, start + 1)
    return False


def _records(doc: Json) -> tuple[dict[str, tuple[str, int]], dict[str, str]]:
    found = extract(doc)
    return found.numbers, found.dates


@dataclass
class _Hits:
    counts: Counter[str]
    tokens: set[str]
    values: dict[str, set[str]]
    residual_tokens: set[str] = field(default_factory=set[str])
    residual_values: dict[str, set[str]] = field(default_factory=dict[str, set[str]])


def _text_hits(sensitive: Sensitive, anonymized: Json) -> _Hits:
    out_text = "\n".join(normalize(s) for s in _copy_strings(anonymized))
    out_tokens = set(tokens(out_text))
    kept_text = "\n".join(normalize(s) for s in sensitive.kept)
    kept_tokens = set(tokens(kept_text))
    hits = _Hits(Counter(), set(), {})
    hits.counts["values:person"] = len(sensitive.tokens)
    for token in sensitive.tokens & out_tokens:
        if token in kept_tokens:
            hits.counts["residual:person"] += 1
            hits.residual_tokens.add(token)
        else:
            hits.counts["leak:person"] += 1
            hits.tokens.add(token)
    for category, values in sorted(sensitive.values.items()):
        hits.counts[f"values:{category}"] = len(values)
        for value in values:
            if not set(tokens(value)) <= out_tokens or not _bounded(out_text, value):
                continue
            if _bounded(kept_text, value):
                hits.counts[f"residual:{category}"] += 1
                hits.residual_values.setdefault(category, set()).add(value)
            else:
                hits.counts[f"leak:{category}"] += 1
                hits.values.setdefault(category, set()).add(value)
    return hits


def check_pair(original: Json, anonymized: Json) -> dict[str, int]:
    """``leak:``/``residual:`` counts per category, and ``values:`` counts of what was checked."""
    sensitive = extract(original)
    counts = _text_hits(sensitive, anonymized).counts
    numbers, dates = _records(anonymized)
    for record, (category, number) in sensitive.numbers.items():
        counts[f"values:{category}_number"] += 1
        if numbers.get(record, ("", 0))[1] == number:
            counts[f"leak:{category}"] += 1
    for record, date in sensitive.dates.items():
        counts["values:birth_date"] += 1
        if dates.get(record) == date:
            counts["leak:birth_date"] += 1
    return dict(sorted(counts.items()))


def _nodes(value: Json, path: str, key: str = "") -> Iterator[tuple[str, str]]:
    """``(path, string)`` of every string and key; list indexes folded to ``[]``."""
    if isinstance(value, str):
        yield path, _searched(key, value)
    elif isinstance(value, list):
        for item in value:
            yield from _nodes(item, f"{path}[]", key)
    elif isinstance(value, dict):
        for name, item in value.items():
            label = name if _KEY.fullmatch(name) else "(other)"
            child = f"{path}.{label}" if path else label
            yield f"{child} (key)", name
            yield from _nodes(item, child, name)


def leak_paths(original: Json, anonymized: Json) -> dict[str, int]:
    """Where in the copy each text leak stands: ``<category> in <JSON path>``; never the value.

    A residual is reported as ``residual <category> in <JSON path>``.
    """
    hits = _text_hits(extract(original), anonymized)
    found: Counter[str] = Counter()
    kinds = (
        ("", hits.tokens, hits.values),
        ("residual ", hits.residual_tokens, hits.residual_values),
    )
    for path, text in _nodes(anonymized, "races[]" if not isinstance(anonymized, dict) else ""):
        normalized = normalize(text)
        words = set(tokens(normalized))
        for prefix, person, values in kinds:
            if person & words:
                found[f"{prefix}person in {path}"] += 1
            for category, texts in values.items():
                if any(_bounded(normalized, value) for value in texts):
                    found[f"{prefix}{category} in {path}"] += 1
    return dict(sorted(found.items()))


# ---------------------------------------------------------------- scanning text


@dataclass
class ScanSet:
    surnames: set[str] = field(default_factory=set[str])
    orgs: set[str] = field(default_factory=set[str])
    places: set[str] = field(default_factory=set[str])
    contacts: set[str] = field(default_factory=set[str])
    codes: set[str] = field(default_factory=set[str])
    cards: set[str] = field(default_factory=set[str])
    short_cards: set[str] = field(default_factory=set[str])
    dates: set[str] = field(default_factory=set[str])
    birth_numbers: set[str] = field(default_factory=set[str])


SCAN_CATEGORIES: Final = ("surname", "org", "place", "contact", "code", "card", "birth_date")
# the value of a card field: ``"card_number": 12345``, ``card_number=12345``; not a counter name
# such as ``"values:card_number": 844`` or ``"mask:person.card_number": 291``
_CARD_VALUE = re.compile(
    r"(?<![\w:.])[\"']?(?:card_number|sportident_card)[\"']?\s*[:=]\s*[\"']?([0-9]+)"
)
# digits in groups of three: ``8 123 456``, ``8'123'456``, with no-break spaces too
_GROUPED_DIGITS = re.compile(r"(?<!\w)[0-9]{1,3}(?:[ '.,\u00a0\u2009\u202f][0-9]{3})+(?!\w)")
_LEGACY_TEXT: Final = "\n".join(
    [normalize(t) for t in anonymize.LEGACY_STATUS_TITLES] + sorted(anonymize.LEGACY_HINTS)
)


def _group_numbers(grouped: str) -> set[str]:
    """What digits in groups can be: all of them, or all but the leading groups (``КП 31 212 345``).

    Without leading zeros, as card numbers are written.
    """
    groups = re.split(r"[^0-9]", grouped)
    return {str(int("".join(groups[i:]))) for i in range(len(groups) - 1)}


def _is_date_number(number: int) -> bool:
    """``YYYYMMDD`` other than 1 January: a shorter or longer number is no date to search."""
    return DATE_NUMBERS.start <= number < DATE_NUMBERS.stop and number % 10_000 != JAN_FIRST


def _date_forms(iso: str) -> list[str]:
    year, month, day = iso.split("-")
    return [iso, f"{day}.{month}.{year}"]


def _own_values(found: Sensitive, category: str, shortest: int) -> set[str]:
    """Values of ``category`` in no kept field of the file and not in legacy's own text."""
    kept = "\n".join(normalize(s) for s in found.kept)
    return {
        v
        for v in found.values.get(category, set())
        if len(v) >= shortest and not _bounded(kept, v) and not _bounded(_LEGACY_TEXT, v)
    }


def scan_set(docs: Iterable[Json]) -> ScanSet:
    scan = ScanSet()
    for doc in docs:
        found = extract(doc)
        for surname in found.surnames:
            scan.surnames.update(t for t in tokens(surname) if len(t) >= MIN_SURNAME)
        scan.orgs.update(_own_values(found, "org", MIN_ORG))
        scan.places.update(_own_values(found, "place", MIN_ORG))
        scan.contacts.update(_own_values(found, "contact", MIN_VALUE))
        scan.codes.update(_own_values(found, "code", MIN_VALUE))
        for category, number in found.numbers.values():
            if category == "code" and number >= MIN_CARD:
                scan.codes.add(str(number))
            elif category == "card":
                (scan.cards if number >= MIN_CARD else scan.short_cards).add(str(number))
            elif category == "birth_date" and _is_date_number(number):
                scan.birth_numbers.add(str(number))
        for date in found.dates.values():
            if not date.endswith("-01-01"):
                scan.dates.update(_date_forms(date))
    return scan


def scan_words(text: str, scan: ScanSet) -> list[tuple[int, str, str]]:
    """``(line number, category, matched word)``: for the maintainer's local file only."""
    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        normalized = normalize(line)
        words = set(tokens(normalized))
        hits.extend((number, "surname", w) for w in sorted(words & scan.surnames))
        for category, values in (
            ("org", scan.orgs),
            ("place", scan.places),
            ("contact", scan.contacts),
            ("code", scan.codes),
        ):
            found = sorted(v for v in values if set(tokens(v)) <= words and _bounded(normalized, v))
            hits.extend((number, category, v) for v in found)
        grouped = {n for m in _GROUPED_DIGITS.finditer(line) for n in _group_numbers(m[0])}
        cards = (
            (words & scan.cards)
            | (grouped & scan.cards)
            | ({m[1] for m in _CARD_VALUE.finditer(line)} & scan.short_cards)
        )
        hits.extend((number, "card", c) for c in sorted(cards))
        hits.extend((number, "birth_date", d) for d in sorted(d for d in scan.dates if d in line))
        hits.extend((number, "birth_date", n) for n in sorted(words & scan.birth_numbers))
    return hits


def scan_text(text: str, scan: ScanSet) -> list[tuple[int, str]]:
    """``(line number, category)`` of each line holding a sensitive value; never the value."""
    found = {(line, category) for line, category, _ in scan_words(text, scan)}
    return sorted(found, key=lambda hit: (hit[0], SCAN_CATEGORIES.index(hit[1])))


# ---------------------------------------------------------------- sources and targets


def race_docs(paths: Iterable[Path]) -> Iterator[Json]:
    """Parsed race files among ``paths`` (directories walked), told by content."""
    for path in paths:
        files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
        for file in files:
            raw = file.read_bytes()
            if racefile.kind(raw) == "race":
                yield parse_json(racefile.decode(raw)[0])


def _text_files(paths: Iterable[Path], skipped: Counter[str]) -> Iterator[tuple[Path, str]]:
    """Text files among ``paths`` (logs included); the others are counted in ``skipped``.

    A path that does not exist (deleted on the branch) is skipped.
    """
    for path in (p for p in paths if p.exists()):
        files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
        for file in files:
            raw = file.read_bytes()
            if racefile.kind(raw) in racefile.NOT_TEXT:
                skipped["not text"] += 1
                continue
            yield file, racefile.decode(raw)[0]


def _commits(revisions: str) -> list[tuple[str, str]]:
    done = subprocess.run(
        ["git", "log", "-z", "--format=%h%n%B", revisions],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    commits: list[tuple[str, str]] = []
    for entry in done.stdout.split("\0"):
        sha, _, message = entry.lstrip("\n").partition("\n")
        if sha:
            commits.append((sha, message))
    return commits


class Options(argparse.Namespace):
    command: str = ""
    paths: tuple[Path, ...] = ()
    source: tuple[Path, ...] = ()
    no_corpus: bool = False
    no_legacy_test_data: bool = False
    commits: str | None = None
    synthetic: tuple[Path, ...] = ()
    words_out: Path | None = None


def _sources(args: Options) -> tuple[list[Path], str | None]:
    sources = list(args.source)
    if not args.no_corpus:
        corpus = os.environ.get(CORPUS_ENV)
        if not corpus:
            return [], f"{CORPUS_ENV} is not set (or pass --no-corpus)"
        sources.append(Path(corpus) / "raw")
    if not args.no_legacy_test_data:
        sources.append(legacy_dir() / "pysport" / "tests" / "data" / "test.json")
    return sources, None


def _show(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _inside_repository(path: Path) -> bool:
    return path.resolve().is_relative_to(ROOT.resolve())


def scan_command(args: Options) -> int:
    if args.words_out is not None and _inside_repository(args.words_out):
        print("leakcheck: --words-out must be outside the repository (it lists corpus values)")
        return 2
    sources, error = _sources(args)
    if error:
        print(f"leakcheck: {error}")
        return 2
    docs = list(race_docs(sources))
    scan = scan_set(docs)
    findings = chance = files = 0
    synthetic = [p.resolve() for p in args.synthetic]
    words: list[str] = []
    skipped: Counter[str] = Counter()
    for path, text in _text_files(args.paths, skipped):
        files += 1
        hits = scan_text(text, scan)
        if args.words_out is not None:
            words.extend(f"{_show(path)}\t{n}\t{c}\t{w}" for n, c, w in scan_words(text, scan))
        if any(path.resolve().is_relative_to(s) for s in synthetic):
            chance += len(hits)
            continue
        for line, category in hits:
            findings += 1
            print(f"{_show(path)}:{line}: {category}")
    commits = _commits(args.commits) if args.commits else []
    for sha, message in commits:
        for line, category in scan_text(message, scan):
            findings += 1
            print(f"commit {sha}:{line}: {category}")
    print(
        f"leakcheck: {len(docs)} source race files ({len(scan.surnames)} surnames, "
        f"{len(scan.orgs)} organizations, "
        f"{len(scan.places)} places, {len(scan.contacts)} contacts, {len(scan.codes)} codes, "
        f"{len(scan.cards)} cards, {len(scan.short_cards)} short cards, "
        f"{len(scan.dates) + len(scan.birth_numbers)} dates); "
        f"scanned {files} files and {len(commits)} commit messages; findings: {findings}; "
        f"in synthetic outputs: {chance}; not text: {skipped['not text']}"
    )
    if args.words_out is not None:
        args.words_out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["path\tline\tcategory\tword", *words]
        args.words_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(
            f"leakcheck: {len(words)} matched words written to {args.words_out} (open it locally)"
        )
    return 1 if findings else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="text files and commit messages")
    scan.add_argument("paths", nargs="*", type=Path, help="files or directories to scan")
    scan.add_argument("--source", action="append", type=Path, default=[], help="race file or dir")
    scan.add_argument("--no-corpus", action="store_true", help=f"do not read ${CORPUS_ENV}/raw")
    scan.add_argument("--no-legacy-test-data", action="store_true", help="skip legacy test.json")
    scan.add_argument("--commits", help="also scan the messages of this git revision range")
    scan.add_argument(
        "--synthetic",
        action="append",
        type=Path,
        default=[],
        help="outputs made only from synthetic inputs: hits there are counted apart, as chance",
    )
    scan.add_argument(
        "--words-out",
        type=Path,
        help="write the matched words (corpus values) to this file outside the repository",
    )
    args = parser.parse_args(argv, namespace=Options())
    return scan_command(args)


if __name__ == "__main__":
    sys.exit(main())
