"""Race files of the corpus: bytes to text by the oracle's rule, and the kind of a file by content.

A race file is gzip, UTF-8 or cp1251 text, in that order: legacy tries UTF-8 and then the locale's
encoding, cp1251 on Russian Windows [код: pysport@b548c35 sportorg/modules/backup/file.py:28-51],
and the oracle reads files the same way (ADR-0009 T6). Kinds are told by content, never by the
file name: the names in the corpus are not to be trusted or printed (R21).
"""

from __future__ import annotations

import gzip
import json
import re
import zlib
from collections import Counter
from typing import Final

from scripts._json import Json, as_dict, as_list, parse_json

FORMATS: Final = ("gzip", "utf-8", "cp1251")
KINDS: Final = (
    "race",
    "json",
    "pdf",
    "html",
    "zip",
    "image",
    "readout-log",
    "sportorg-log",
    "text",
    "binary",
)
GZIP_MAGIC: Final = b"\x1f\x8b"
_HTML_MARKS: Final = (b"<!doctype html", b"<html")
_PROBE: Final = 1024
_MAGIC: Final = (
    (b"%PDF", "pdf"),
    (b"PK\x03\x04", "zip"),
    (b"\x89PNG", "image"),
    (b"\xff\xd8\xff", "image"),
    (b"GIF8", "image"),
)
_TEXT_CONTROLS: Final = frozenset("\t\n\r\f")
# legacy's own log [код: pysport@b548c35 sportorg/config.py:114,130]
# level, asctime, threadName (may hold spaces), filename, lineno
_SPORTORG_LOG_LINE = re.compile(
    r"(DEBUG|INFO|WARNING|ERROR|CRITICAL) \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} "
    r".*?@(\S+):(\d+) "
)
_MODULE_FILE = re.compile(r"[A-Za-z0-9_]+\.py")
_LOG_PROBE_LINES: Final = 20


class UndecodableError(ValueError):
    """Not gzip, UTF-8 or cp1251 text; legacy on Russian Windows cannot open it either."""


def decode(raw: bytes) -> tuple[str, str]:
    """``(text, format)`` of a race file's bytes."""
    if raw.startswith(GZIP_MAGIC):
        try:
            return gzip.decompress(raw).decode("utf-8"), "gzip"
        except OSError, EOFError, zlib.error, UnicodeDecodeError:
            raise UndecodableError from None
    for encoding in FORMATS[1:]:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise UndecodableError


def encode(text: str, fmt: str) -> bytes:
    """Bytes in ``fmt``; gzip without a timestamp, so the output is reproducible."""
    if fmt == "gzip":
        return gzip.compress(text.encode("utf-8"), mtime=0)
    if fmt in FORMATS:
        return text.encode(fmt)
    msg = f"unknown format {fmt!r}"
    raise ValueError(msg)


def dumps(doc: Json) -> str:
    """JSON as legacy writes it: two-space indent, keys in their order, non-ASCII kept.

    [код: pysport@b548c35 sportorg/modules/backup/json.py:19-31]
    """
    return json.dumps(doc, ensure_ascii=False, indent=2)


def races_of(doc: Json) -> list[Json]:
    """Race dicts of a parsed file, in the shapes legacy accepts.

    [код: pysport@b548c35 sportorg/modules/backup/json.py:55-60]: a dict with ``races``, a list of
    race dicts, or a single race dict.
    """
    if isinstance(doc, dict) and "races" in doc:
        return as_list(doc["races"])
    if isinstance(doc, list):
        return doc
    return [doc]


def is_race(item: Json) -> bool:
    race = as_dict(item)
    return race.get("object") == "Race" or ("persons" in race and "results" in race)


def _is_race_file(doc: Json) -> bool:
    races = races_of(doc)
    return bool(races) and all(is_race(race) for race in races)


def _is_text(text: str) -> bool:
    return all(char.isprintable() or char in _TEXT_CONTROLS for char in text)


def _is_readout_log(text: str) -> bool:
    """The readout backup ``si<date>.log``: blocks ``start … split_start … split_end end``.

    [код: pysport@b548c35 sportorg/modules/sportident/backup.py:29-46]; SFR, Sportiduino, SRPID
    and Huichang readers write it too.
    """
    lines = text.lstrip().splitlines()
    return bool(lines) and lines[0].strip() == "start" and "split_start" in text


def _is_sportorg_log(text: str) -> bool:
    lines = text.splitlines()[:_LOG_PROBE_LINES]
    return any(_SPORTORG_LOG_LINE.match(line) for line in lines)


def sportorg_log_stats(text: str) -> dict[str, Json]:
    """Lines of legacy's log by level and by the code location that wrote them, never a message.

    ``%(filename)s:%(lineno)d`` names legacy's code [код: pysport@b548c35 sportorg/config.py:114];
    a line that does not start a record (a traceback, a multi-line message) is a continuation.
    """
    lines = text.splitlines()
    levels: Counter[str] = Counter()
    locations: Counter[str] = Counter()
    for line in lines:
        match = _SPORTORG_LOG_LINE.match(line)
        if match is None:
            continue
        levels[match[1]] += 1
        module = match[2]
        locations[f"{module}:{match[3]}" if _MODULE_FILE.fullmatch(module) else "(other)"] += 1
    return {
        "lines": len(lines),
        "continuation_lines": len(lines) - sum(levels.values()),
        "levels": dict[str, Json](sorted(levels.items())),
        "locations": dict[str, Json](sorted(locations.items())),
    }


def readout_log_stats(text: str) -> dict[str, int]:
    """Counts of a readout backup log; card numbers and times are read, never returned."""
    stats = {"readouts": 0, "punches": 0, "without_start": 0, "unparsed_lines": 0}
    lines = iter(text.splitlines())
    for line in lines:
        if line.strip() != "start":
            stats["unparsed_lines"] += 1 if line.strip() else 0
            continue
        header = [next(lines, "") for _ in range(4)]  # card, start, finish, split_start
        if not header[1].strip():
            stats["without_start"] += 1
        for punch in lines:
            if punch.strip() == "split_end":
                break
            stats["punches"] += 1
        if next(lines, "").strip() == "end":
            stats["readouts"] += 1
    return stats


def _magic_kind(raw: bytes) -> str | None:
    head = raw[:_PROBE].lstrip().lower()
    for magic, name in _MAGIC:
        if raw.startswith(magic):
            return name
    return "html" if any(mark in head for mark in _HTML_MARKS) else None


def kind(raw: bytes) -> str:
    """The kind of a file by its content (``KINDS``)."""
    if (by_magic := _magic_kind(raw)) is not None:
        return by_magic
    try:
        text, _ = decode(raw)
    except UndecodableError:
        return "binary"
    try:
        doc = parse_json(text)
    except ValueError:
        if _is_readout_log(text):
            return "readout-log"
        if _is_sportorg_log(text):
            return "sportorg-log"
        return "text" if _is_text(text) else "binary"
    return "race" if _is_race_file(doc) else "json"
