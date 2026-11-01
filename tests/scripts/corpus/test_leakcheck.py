"""Tests for scripts/corpus/leakcheck.py: no original name, card or birth date in the output.

The check prints counts, categories and line numbers, never the value it found (Д3 on practice).
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_list
from scripts.corpus import anonymize, leakcheck, racefile, synth
from scripts.legacy import ROOT

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


def _shape_results(doc: Json, index: int) -> list[dict[str, Json]]:
    return [as_dict(r) for r in as_list(as_dict(racefile.races_of(doc)[index])["results"])]


FREE = synth.SHAPE_PEOPLE[1][3][1]  # day 2, free text


@pytest.mark.parametrize("key", ["result", "result_relay", "result_current"])
def test_a_status_comment_left_in_a_derived_string_is_a_leak(key: str) -> None:
    original = synth.personal_legacy_shape()
    leaked = _anonymized(original)
    target = next(r for r in _shape_results(leaked, 1) if r["status"] == synth.DISQUALIFIED)
    target[key] = FREE
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_a_status_comment_cut_in_multi_day_results_is_a_leak() -> None:
    original = synth.personal_legacy_shape()
    leaked = _anonymized(original)
    target = _shape_results(leaked, 0)[1]
    target["multi_day_results"] = "0:31:00       " + FREE[: synth.DAY_FIELD]
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_a_kept_rule_clause_is_not_a_sensitive_value() -> None:
    original = synth.personal_legacy_shape()
    counts = leakcheck.check_pair(original, _anonymized(original))
    assert counts.get("residual:text", 0) == 0
    assert counts["values:text"] == 3  # the free comment, its 14 characters, the free hint


def test_leak_paths_also_name_where_a_residual_stands() -> None:
    original = copy.deepcopy(synth.personal_individual())
    group = as_dict(as_list(as_dict(racefile.races_of(original)[0])["groups"])[0])
    group["name"] = "Придумкин"
    paths = leakcheck.leak_paths(original, _anonymized(original))
    assert paths == {"residual person in races[].groups[].name": 1}


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


def test_words_out_lists_matches_in_a_file_outside_the_repository(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The maintainer reads the matched words locally; the console shows counts and the path."""
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    doc = tmp_path / "old.md"
    doc.write_text("intro\nа Придумкин здесь\n", encoding="utf-8")
    words = tmp_path / "words.tsv"
    args = ["scan", str(doc), "--source", str(source), "--no-corpus", "--words-out", str(words)]
    assert leakcheck.main(args) == 1
    assert words.read_text(encoding="utf-8").splitlines() == [
        "path\tline\tcategory\tword",
        f"{doc.name}\t2\tsurname\tпридумкин",
    ]
    out = capsys.readouterr().out
    assert "Придумкин" not in out
    assert "придумкин" not in out
    assert str(words) in out


def test_words_out_refuses_a_path_inside_the_repository() -> None:
    target = ROOT / "words.tsv"
    args = ["scan", "--no-corpus", "--no-legacy-test-data", "--words-out", str(target)]
    assert leakcheck.main(args) == 2
    assert not target.exists()


@pytest.mark.parametrize("text", ["\ufeffВыдумщиков was here\n", "Выдумщиков\u00a0was here\n"])
def test_scan_reads_a_file_with_a_bom_or_a_no_break_space(
    tmp_path: Path, text: str, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    note = tmp_path / "note.md"
    note.write_text(text, encoding="utf-8")
    assert leakcheck.main(["scan", str(note), "--source", str(source), "--no-corpus"]) == 1
    assert "note.md:1: surname" in capsys.readouterr().out


def test_scan_says_how_many_files_it_could_not_read_as_text(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "race.json"
    source.write_text(synth.dumps(synth.personal_individual()), encoding="utf-8")
    scanned = tmp_path / "scanned"
    scanned.mkdir()
    (scanned / "blob.bin").write_bytes(b"\x00\x01\x02\xff\xfe")
    (scanned / "log.txt").write_text("start\ncard\n\n\nsplit_start\nsplit_end\nend\n")
    assert leakcheck.main(["scan", str(scanned), "--source", str(source), "--no-corpus"]) == 0
    out = capsys.readouterr().out
    assert "scanned 1 files" in out  # the readout log
    assert "not text: 1" in out


# ---------------------------------------------------------------- other shapes (I2)


@pytest.mark.parametrize("card", [212_345.0, "212 345", " 212345"])
def test_a_card_in_another_shape_left_in_the_copy_is_found(card: Json) -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[1]["card_number"] = card
    leaked = _anonymized(original)
    _persons(leaked)[1]["card_number"] = card
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:card": 1}


def test_a_birthday_left_in_the_copy_is_found() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[1].update({"birth_date": "", "birthday": "17.05.1990"})
    leaked = _anonymized(original)
    _persons(leaked)[1]["birthday"] = "17.05.1990"
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:birth_date": 1}


def test_a_birth_date_number_left_in_the_copy_is_found() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[1]["birth_date"] = 19_900_517
    leaked = _anonymized(original)
    _persons(leaked)[1]["birth_date"] = 19_900_517
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:birth_date": 1}


def test_a_digit_that_is_not_ascii_does_not_break_the_check() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[1]["card_number"] = "²"
    assert _leaks(leakcheck.check_pair(original, _anonymized(original))) == {}


# ---------------------------------------------------------------- what else the scan finds (I3)


@pytest.mark.parametrize(
    ("line", "category"),
    [
        ("phone +7 000 000-00-01 here", "contact"),
        ("code WRE-000001 here", "code"),
        ("code NC-77 here", "code"),
        ("place Небывальская область here", "place"),
        ('      "card_number": 12345,', "card"),
        ('      "sportident_card": 12345,', "card"),
    ],
)
def test_scan_finds_contacts_codes_places_and_short_cards_by_their_key(
    scan_set: leakcheck.ScanSet, line: str, category: str
) -> None:
    assert leakcheck.scan_text(line, scan_set) == [(1, category)]


def test_a_numeric_code_is_found_like_a_card(scan_set: leakcheck.ScanSet) -> None:
    """1234567 is a national code of one person and the card of another result."""
    assert leakcheck.scan_text("national 1234567 here", scan_set) == [(1, "code"), (1, "card")]


@pytest.mark.parametrize(
    "line",
    [
        "short card 12345",
        "took 12345 ms",
        '"time": 12345,',
        '"values:card_number": 12345,',
        '"mask:person.card_number": 12345,',
        "card_number counts 12345",
    ],
)
def test_a_short_card_number_outside_a_card_field_is_not_searched(
    scan_set: leakcheck.ScanSet, line: str
) -> None:
    assert leakcheck.scan_text(line, scan_set) == []


def test_a_status_title_legacy_writes_is_residual_even_if_a_club_has_that_name() -> None:
    """Without a comment legacy writes the status title (``Не заявлен``) into ``result``."""
    original = copy.deepcopy(synth.personal_individual())
    org = as_dict(as_list(as_dict(racefile.races_of(original)[0])["organizations"])[0])
    org["name"] = "Не заявлен"
    result = _results(original)[0]
    result.update({"status": 14, "result": "Не заявлен", "result_relay": "Не заявлен"})
    leaked = _anonymized(original)
    counts = leakcheck.check_pair(original, leaked)
    assert _leaks(counts) == {}
    assert counts["residual:org"] == 1


def test_middle_names_are_not_searched_in_text(scan_set: leakcheck.ScanSet) -> None:
    """Formed from given names, which are too common to search."""
    assert leakcheck.scan_text("patronymic Петрович here", scan_set) == []


def test_a_value_that_is_a_key_of_the_schema_is_not_searched() -> None:
    original = copy.deepcopy(synth.personal_old_format())
    org = as_dict(as_list(as_dict(original)["organizations"])[0])
    org["contact"] = {"type": "address", "value": "+7 000 000-00-03"}
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("the address of the club", scan) == []
    assert leakcheck.scan_text("phone +7 000 000-00-03", scan) == [(1, "contact")]


def test_a_value_that_is_legacys_own_text_is_not_searched() -> None:
    original = copy.deepcopy(synth.personal_individual())
    org = as_dict(as_list(as_dict(racefile.races_of(original)[0])["organizations"])[0])
    org["name"] = "Не заявлен"
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text('"Не заявлен",', scan) == []
