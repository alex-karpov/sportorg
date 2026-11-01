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
  personal data ``[мейнтейнер: 2026-10-31]``: surnames (words of four letters or more),
  organization names, card numbers of six digits or more, birth dates other than 1 January (the
  date legacy stores for a year only [код: pysport@b548c35 sportorg/models/memory.py:1379-1399]).
  Given names alone are not searched: too common to tell a leak from a word.

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
_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{2})\.(\d{2})\.(\d{4})")
MIN_TOKEN: Final = 2
MIN_VALUE: Final = 3  # letters and digits; shorter values (a thread id "17") match by chance
MIN_SURNAME: Final = 4
MIN_ORG: Final = 5
MIN_CARD: Final = 100_000
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
        if isinstance(value, bool):
            return
        if isinstance(value, int) and value > 0:
            self.found.numbers[record] = (category, value)
        elif isinstance(value, str) and value.strip().isdigit() and int(value) > 0:
            self.found.numbers[record] = (category, int(value))
        elif category == "code":
            self.value("code", value)

    def person(self, item: Json) -> None:
        person = as_dict(item)
        pid = as_str(person.get("id"))
        for name, value in person.items():
            if name in PERSON_WORDS:
                self.words(value)
                if name == "surname":
                    self.found.surnames.add(normalize(as_str(value)))
            elif name in anonymize.CARD_KEYS:
                self.number(f"person:{pid}:{name}", "card", value)
            elif name in anonymize.CODE_KEYS:
                self.number(f"person:{pid}:{name}", "code", value)
            elif name == "birth_date":
                if isinstance(value, str) and (date := iso_date(value)):
                    self.found.dates[f"person:{pid}"] = date
            elif name == "birthday":
                pass
            elif name in anonymize.PERSON_KEPT:
                self.kept(name, value)
            else:
                self.value("text", value)

    def result(self, item: Json) -> None:
        result = as_dict(item)
        rid = as_str(result.get("id"))
        for name, value in result.items():
            if name in anonymize.CARD_KEYS:
                self.number(f"result:{rid}:{name}", "card", value)
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
            else:
                self.kept(name, value)


def _keys(value: Json) -> Iterator[str]:
    if isinstance(value, list):
        for item in value:
            yield from _keys(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _keys(item)


def extract(doc: Json) -> Sensitive:
    """Every key of the file counts as kept text: keys are the schema, not data."""
    extractor = _Extractor()
    for race in racefile.races_of(doc):
        extractor.race(race)
    extractor.found.kept.extend(sorted(set(_keys(doc))))
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


def _text_hits(sensitive: Sensitive, anonymized: Json) -> _Hits:
    out_text = "\n".join(normalize(s) for s in _strings(anonymized))
    out_tokens = set(tokens(out_text))
    kept_text = "\n".join(normalize(s) for s in sensitive.kept)
    kept_tokens = set(tokens(kept_text))
    hits = _Hits(Counter(), set(), {})
    hits.counts["values:person"] = len(sensitive.tokens)
    for token in sensitive.tokens & out_tokens:
        if token in kept_tokens:
            hits.counts["residual:person"] += 1
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


def _nodes(value: Json, path: str) -> Iterator[tuple[str, str]]:
    """``(path, string)`` of every string and key; list indexes folded to ``[]``."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for item in value:
            yield from _nodes(item, f"{path}[]")
    elif isinstance(value, dict):
        for key, item in value.items():
            name = key if _KEY.fullmatch(key) else "(other)"
            child = f"{path}.{name}" if path else name
            yield f"{child} (key)", key
            yield from _nodes(item, child)


def leak_paths(original: Json, anonymized: Json) -> dict[str, int]:
    """Where in the copy each text leak stands: ``<category> in <JSON path>``; never the value."""
    hits = _text_hits(extract(original), anonymized)
    found: Counter[str] = Counter()
    for path, text in _nodes(anonymized, "races[]" if not isinstance(anonymized, dict) else ""):
        normalized = normalize(text)
        if hits.tokens & set(tokens(normalized)):
            found[f"person in {path}"] += 1
        for category, values in hits.values.items():
            if any(_bounded(normalized, value) for value in values):
                found[f"{category} in {path}"] += 1
    return dict(sorted(found.items()))


# ---------------------------------------------------------------- scanning text


@dataclass
class ScanSet:
    surnames: set[str] = field(default_factory=set[str])
    orgs: set[str] = field(default_factory=set[str])
    cards: set[str] = field(default_factory=set[str])
    dates: set[str] = field(default_factory=set[str])


def _date_forms(iso: str) -> list[str]:
    year, month, day = iso.split("-")
    return [iso, f"{day}.{month}.{year}"]


def scan_set(docs: Iterable[Json]) -> ScanSet:
    scan = ScanSet()
    for doc in docs:
        found = extract(doc)
        for surname in found.surnames:
            scan.surnames.update(t for t in tokens(surname) if len(t) >= MIN_SURNAME)
        scan.orgs.update(v for v in found.values.get("org", set()) if len(v) >= MIN_ORG)
        scan.cards.update(
            str(number)
            for category, number in found.numbers.values()
            if category == "card" and number >= MIN_CARD
        )
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
        orgs = sorted(o for o in scan.orgs if set(tokens(o)) <= words and _bounded(normalized, o))
        hits.extend((number, "org", o) for o in orgs)
        hits.extend((number, "card", c) for c in sorted(words & scan.cards))
        hits.extend((number, "birth_date", d) for d in sorted(d for d in scan.dates if d in line))
    return hits


def scan_text(text: str, scan: ScanSet) -> list[tuple[int, str]]:
    """``(line number, category)`` of each line holding a sensitive value; never the value."""
    order = ("surname", "org", "card", "birth_date")
    found = {(line, category) for line, category, _ in scan_words(text, scan)}
    return sorted(found, key=lambda hit: (hit[0], order.index(hit[1])))


# ---------------------------------------------------------------- sources and targets


def race_docs(paths: Iterable[Path]) -> Iterator[Json]:
    """Parsed race files among ``paths`` (directories walked), told by content."""
    for path in paths:
        files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
        for file in files:
            raw = file.read_bytes()
            if racefile.kind(raw) == "race":
                yield parse_json(racefile.decode(raw)[0])


def _text_files(paths: Iterable[Path]) -> Iterator[tuple[Path, str]]:
    """Text files among ``paths``; a path that does not exist (deleted on the branch) is skipped."""
    for path in (p for p in paths if p.exists()):
        files = sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
        for file in files:
            raw = file.read_bytes()
            if racefile.kind(raw) in {"text", "json", "html", "race"}:
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
    for path, text in _text_files(args.paths):
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
        f"{len(scan.orgs)} organizations, {len(scan.cards)} cards, {len(scan.dates)} dates); "
        f"scanned {files} files and {len(commits)} commit messages; findings: {findings}; "
        f"in synthetic outputs: {chance}"
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
