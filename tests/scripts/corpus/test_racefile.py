"""Tests for scripts/corpus/racefile.py: race files read by the oracle's rule, kinds by content."""

from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

import pytest

from scripts.corpus import racefile, synth

if TYPE_CHECKING:
    from scripts._json import Json

RACE_TEXT = synth.dumps(synth.individual())
# [код: pysport@b548c35 sportorg/modules/sportident/backup.py:29-46]; invented card numbers
READOUT_LOG = (
    "start\n8000001\n10:00:00\n10:30:00\nsplit_start\n31 10:05:00\n32 10:15:00\nsplit_end\nend\n"
    "start\n8000002\n\n10:31:00\nsplit_start\nsplit_end\nend\n"
)
# [код: pysport@b548c35 sportorg/config.py:114]
SPORTORG_LOG = (
    "INFO 2025-06-22 10:00:00,123 MainThread@main_window.py:267 Сохранение\n"
    "ERROR 2025-06-22 10:00:01,005 Thread-3@sireader.py:120 нет связи\n"
    "Traceback (most recent call last):\n"
)


@pytest.mark.parametrize("fmt", racefile.FORMATS)
def test_encode_then_decode_round_trips(fmt: str) -> None:
    text = RACE_TEXT.replace("Synthetic", "Синтетик")
    assert racefile.decode(racefile.encode(text, fmt)) == (text, fmt)


def test_utf8_comes_before_cp1251() -> None:
    """[код: pysport@b548c35 sportorg/modules/backup/file.py:28-51], ADR-0009 T6."""
    assert racefile.decode("Синтетик".encode())[1] == "utf-8"
    assert racefile.decode("Синтетик".encode("cp1251"))[1] == "cp1251"


def test_bytes_neither_utf8_nor_cp1251_are_refused() -> None:
    with pytest.raises(racefile.UndecodableError):
        racefile.decode(b"\x98\xff\xfe")


def test_gzip_output_is_reproducible() -> None:
    assert racefile.encode(RACE_TEXT, "gzip") == racefile.encode(RACE_TEXT, "gzip")


def test_gzip_is_found_by_content_not_by_name() -> None:
    assert racefile.decode(gzip.compress(RACE_TEXT.encode()))[1] == "gzip"


@pytest.mark.parametrize(
    ("raw", "kind"),
    [
        (RACE_TEXT.encode(), "race"),
        (gzip.compress(RACE_TEXT.encode()), "race"),
        (RACE_TEXT.encode("cp1251"), "race"),
        (b'{"object": "Race", "persons": [], "results": []}', "race"),
        (b'[{"object": "Race", "persons": [], "results": []}]', "race"),
        (b'{"version": "1", "items": []}', "json"),
        (b"%PDF-1.7\n...", "pdf"),
        (b"\n<!DOCTYPE html><html></html>", "html"),
        (b"<HTML><body>", "html"),
        (b"PK\x03\x04rest", "zip"),
        (b"\x89PNG\r\n\x1a\nrest", "image"),
        (b"\xff\xd8\xffrest", "image"),
        ("# Заметка\nтекст\n".encode(), "text"),
        (b"\x00\x01\x02\x98\xff", "binary"),
        (READOUT_LOG.encode(), "readout-log"),
        (SPORTORG_LOG.encode("cp1251"), "sportorg-log"),
    ],
)
def test_kind_by_content(raw: bytes, kind: str) -> None:
    assert racefile.kind(raw) == kind


def test_races_of_accepts_the_shapes_legacy_accepts() -> None:
    """[код: pysport@b548c35 sportorg/modules/backup/json.py:55-60]."""
    race: Json = {"object": "Race", "persons": [], "results": []}
    assert racefile.races_of({"races": [race]}) == [race]
    assert racefile.races_of(race) == [race]
    assert racefile.races_of([race, race]) == [race, race]


def test_dumps_writes_legacy_indent_and_keeps_key_order() -> None:
    text = racefile.dumps({"b": 1, "a": ["Ё"]})
    assert text == '{\n  "b": 1,\n  "a": [\n    "Ё"\n  ]\n}'


def test_readout_log_counts_blocks_and_punches_only() -> None:
    assert racefile.readout_log_stats(READOUT_LOG + "garbage\n") == {
        "readouts": 2,
        "punches": 2,
        "without_start": 1,
        "unparsed_lines": 1,
    }


def test_sportorg_log_counts_lines_by_level_and_code_location_only() -> None:
    """[код: pysport@b548c35 sportorg/config.py:114]: ``%(filename)s:%(lineno)d`` is code."""
    text = SPORTORG_LOG + "INFO 2025-06-22 10:00:02,000 Thread-2 (run)@../x.py:7 Выдумкин\n"
    assert racefile.sportorg_log_stats(text) == {
        "lines": 4,
        "continuation_lines": 1,
        "levels": {"ERROR": 1, "INFO": 2},
        "locations": {"(other)": 1, "main_window.py:267": 1, "sireader.py:120": 1},
    }


@pytest.mark.parametrize("char", ["\ufeff", "\u00a0", "\u200b", "\u00ad", "\u2028"])
def test_text_with_a_bom_or_an_invisible_space_is_text(char: str) -> None:
    assert racefile.kind(f"{char}a line{char}of text\n".encode()) == "text"
