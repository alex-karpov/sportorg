"""Tests for scripts/corpus/leakcheck.py: no original name, card or birth date in the output.

The check prints counts, categories and line numbers, never the value it found (Д3 on practice).
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_list
from scripts.corpus import anonymize, leakcheck, racefile, synth

if TYPE_CHECKING:
    from pathlib import Path

    from scripts._json import Json

KEY = b"synthetic test key, not the corpus key"


def _anonymized(doc: Json) -> Json:
    return anonymize.anonymize(doc, key=KEY, neutral_id="S00-test").doc


def _leaks(counts: dict[str, int]) -> dict[str, int]:
    return {k: v for k, v in counts.items() if k.startswith("leak:") and v}


def _persons(doc: Json) -> list[dict[str, Json]]:
    return [as_dict(p) for p in as_list(as_dict(racefile.races_of(doc)[0])["persons"])]


def _results(doc: Json) -> list[dict[str, Json]]:
    return [as_dict(p) for p in as_list(as_dict(racefile.races_of(doc)[0])["results"])]


@pytest.mark.parametrize("name", list(synth.PERSONAL))
def test_anonymized_synthetic_races_leak_nothing(name: str) -> None:
    original = synth.PERSONAL[name]()
    assert _leaks(leakcheck.check_pair(original, _anonymized(original))) == {}


def test_the_original_against_itself_leaks_every_category() -> None:
    original = synth.personal_individual()
    leaks = _leaks(leakcheck.check_pair(original, original))
    for category in ("person", "org", "place", "contact", "race", "text", "card", "birth_date"):
        assert leaks.get(f"leak:{category}", 0) > 0, category


def test_one_restored_surname_is_found() -> None:
    original = synth.personal_individual()
    leaked = _anonymized(original)
    _persons(leaked)[8]["surname"] = _persons(original)[8]["surname"]
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:person": 1}


def test_one_restored_card_is_found() -> None:
    original = synth.personal_individual()
    leaked = _anonymized(original)
    _results(leaked)[2]["card_number"] = _results(original)[2]["card_number"]
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:card": 1}


def test_one_restored_birth_date_is_found() -> None:
    original = synth.personal_individual()
    leaked = _anonymized(original)
    _persons(leaked)[0]["birth_date"] = _persons(original)[0]["birth_date"]
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:birth_date": 1}


def test_a_surname_in_a_kept_field_is_residual_not_a_leak() -> None:
    original = copy.deepcopy(synth.personal_individual())
    group = as_dict(as_list(as_dict(racefile.races_of(original)[0])["groups"])[0])
    group["name"] = "Придумкин"
    counts = leakcheck.check_pair(original, _anonymized(original))
    assert _leaks(counts) == {}
    assert counts["residual:person"] == 1


# ---------------------------------------------------------------- scanning text


SCANNED_LINES = (
    "nothing here",
    "a row about Придумкин",
    "card 8123456 was read",
    "born 1990-05-17",
    "born 17.05.2010",
    "only the given name Пётр",
    "a year-only date 2005-01-01",
    "short card 12345",
)


@pytest.fixture
def scan_set() -> leakcheck.ScanSet:
    return leakcheck.scan_set([synth.personal_individual(), synth.personal_multi_day()])


def test_scan_finds_surnames_cards_and_birth_dates_by_line(scan_set: leakcheck.ScanSet) -> None:
    text = "\n".join(SCANNED_LINES)
    assert leakcheck.scan_text(text, scan_set) == [
        (2, "surname"),
        (3, "card"),
        (4, "birth_date"),
        (5, "birth_date"),
    ]


def test_scan_finds_an_organization_name(scan_set: leakcheck.ScanSet) -> None:
    assert leakcheck.scan_text("results of клуб  небыль here", scan_set) == [(1, "org")]


def test_scan_cli_prints_places_not_values(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    clean, dirty = tmp_path / "clean.md", tmp_path / "dirty.md"
    clean.write_text("counts only: 10 results\n", encoding="utf-8")
    dirty.write_text("line one\nВыдумщиков was here\n", encoding="utf-8")
    assert leakcheck.main(["scan", str(clean), "--source", str(source), "--no-corpus"]) == 0
    assert leakcheck.main(["scan", str(dirty), "--source", str(source), "--no-corpus"]) == 1
    out = capsys.readouterr().out
    assert "dirty.md:2: surname" in out
    assert "Выдумщиков" not in out


def test_leak_paths_name_where_a_leak_stands_never_what() -> None:
    original = synth.personal_individual()
    leaked = _anonymized(original)
    _persons(leaked)[8]["comment"] = f"note {_persons(original)[8]['surname']}"
    paths = leakcheck.leak_paths(original, leaked)
    assert paths == {"person in races[].persons[].comment": 1}


def test_a_value_that_is_also_a_key_name_is_residual() -> None:
    """Old files hold schema words as values (contact type ``address``): keys are not data."""
    original = synth.personal_old_format()
    org = as_dict(as_list(as_dict(original)["organizations"])[0])
    org["contact"] = {"type": "address", "value": "+7 000 000-00-03"}
    counts = leakcheck.check_pair(original, _anonymized(original))
    assert _leaks(counts) == {}
    assert counts["residual:contact"] == 1


def test_hits_in_synthetic_outputs_are_counted_apart(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file made only from synthetic inputs holds no corpus value: a hit there is chance."""
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    generated = tmp_path / "synthetic" / "results.json"
    generated.parent.mkdir()
    generated.write_text('{"time_ms": 8123456}\n', encoding="utf-8")
    args = ["scan", str(generated), "--source", str(source), "--no-corpus"]
    assert leakcheck.main([*args, "--synthetic", str(tmp_path / "synthetic")]) == 0
    out = capsys.readouterr().out
    assert "results.json:1" not in out
    assert "findings: 0" in out
    assert "in synthetic outputs: 1" in out


def test_a_path_that_is_gone_is_skipped(tmp_path: Path) -> None:
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    gone = tmp_path / "deleted.md"
    assert leakcheck.main(["scan", str(gone), "--source", str(source), "--no-corpus"]) == 0
