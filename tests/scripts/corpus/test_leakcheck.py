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


# ---------------------------------------------------------------- fix pass after the re-review


def _set_comment(doc: Json, index: int, which: int, comment: Json, multi_day: str) -> None:
    result = _shape_results(doc, index)[which]
    result["status_comment"] = comment
    result["multi_day_results"] = multi_day


def test_a_status_comment_cut_in_an_earlier_day_field_is_a_leak() -> None:
    """The next day's time follows the cut text without a separator."""
    original = synth.personal_legacy_shape()
    leaked = _anonymized(original)
    target = _shape_results(leaked, 0)[1]
    target["multi_day_results"] = FREE[: synth.DAY_FIELD] + "0:32:00       "
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}
    assert leakcheck.leak_paths(original, leaked) == {
        "text in races[].results[].multi_day_results": 1
    }


def test_a_cut_free_hint_after_a_rule_clause_is_a_leak() -> None:
    original = synth.personal_legacy_shape()
    comment = "пп1 # Придумкин Пётр"
    _set_comment(original, 0, 1, comment, f"{comment[: synth.DAY_FIELD]}0:32:00       ")
    leaked = _anonymized(original)
    _shape_results(leaked, 0)[1]["multi_day_results"] = f"{comment[: synth.DAY_FIELD]}0:32:00"
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_a_non_string_status_comment_left_in_the_copy_is_a_leak() -> None:
    original = synth.personal_legacy_shape()
    listed: list[Json] = ["Снят по протесту Небылицкого"]
    _set_comment(original, 0, 1, listed, "0:31:00       ")
    leaked = _anonymized(original)
    assert _leaks(leakcheck.check_pair(original, leaked)) == {}
    _shape_results(leaked, 0)[1]["status_comment"] = listed
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_an_unknown_race_level_key_is_sensitive_text() -> None:
    """The anonymizer masks it, so a copy that keeps it leaks."""
    original = copy.deepcopy(synth.personal_individual())
    as_dict(racefile.races_of(original)[0])["notes"] = "Заметка про Небылицкого"
    leaked = _anonymized(original)
    assert _leaks(leakcheck.check_pair(original, leaked)) == {}
    as_dict(racefile.races_of(leaked)[0])["notes"] = "Заметка про Небылицкого"
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_scan_finds_the_surname_of_a_referee(scan_set: leakcheck.ScanSet) -> None:
    assert leakcheck.scan_text("главный судья Придумов П. П.", scan_set) == [(1, "surname")]


def test_scan_finds_a_birth_date_written_as_a_number() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0]["birth_date"] = 19_900_517
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("born 19900517", scan) == [(1, "birth_date")]
    assert leakcheck.scan_text("born 19900518", scan) == []


def test_scan_finds_a_card_written_in_groups(scan_set: leakcheck.ScanSet) -> None:
    text = "card 8 123 456 read\ncard 8'123'456\ncard 8 123 456\nnot 8 123 4567"
    assert leakcheck.scan_text(text, scan_set) == [(1, "card"), (2, "card"), (3, "card")]


# ---------------------------------------------------------------- fix pass after the Opus review


@pytest.mark.parametrize(
    "comment",
    [
        "пп6.6.4 # не стартовал",
        "пп1 # не прошел КП 5",
        "пп6.6.4 # спортсмен сошел с трассы на КП 5",
    ],
)
def test_a_cut_hint_the_anonymizer_keeps_is_not_a_leak(comment: str) -> None:
    """The cut of a legacy hint is legacy's own text: the anonymizer keeps it, so must the check."""
    cut = comment[: synth.DAY_FIELD]
    assert anonymize.status_comment(KEY, cut, cut=True)[1] == "kept"
    original = synth.personal_legacy_shape()
    _set_comment(original, 0, 1, comment, f"{cut}0:32:00       ")
    assert _leaks(leakcheck.check_pair(original, _anonymized(original))) == {}


def test_a_comment_in_a_day_field_not_on_a_field_boundary_is_a_leak() -> None:
    original = synth.personal_legacy_shape()
    comment = "Заметка про Небылицкого"
    _set_comment(original, 0, 1, comment, "0:31:00       ")
    leaked = _anonymized(original)
    _shape_results(leaked, 0)[1]["multi_day_results"] = f"0:31:00 {comment}"
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_an_unknown_file_level_key_is_sensitive_text() -> None:
    original = copy.deepcopy(synth.personal_individual())
    wrapped: dict[str, Json] = {"version": 1, "races": [original], "notes": "Заметка о Небылицком"}
    leaked = _anonymized(wrapped)
    assert _leaks(leakcheck.check_pair(wrapped, leaked)) == {}
    as_dict(leaked)["notes"] = "Заметка о Небылицком"
    assert _leaks(leakcheck.check_pair(wrapped, leaked)) == {"leak:text": 1}


@pytest.mark.parametrize("birth_date", [19_900_517, 19_900_517.0, "19900517"])
def test_scan_finds_a_birth_date_written_as_eight_digits(birth_date: Json) -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0]["birth_date"] = birth_date
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("born 19900517", scan) == [(1, "birth_date")]


@pytest.mark.parametrize("birth_date", [1990, 0, 123_456_789])
def test_scan_ignores_a_number_that_is_not_a_date_of_eight_digits(birth_date: int) -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0]["birth_date"] = birth_date
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("in 1990, 0 errors, 123456789", scan) == []


@pytest.mark.parametrize(
    "line",
    [
        "8,123,456",
        "8.123.456",
        "8 123 456",
        "card 08 123 456",
        "КП 31 212 345",  # a number before the card is not part of it
    ],
)
def test_scan_finds_a_card_in_more_groupings(scan_set: leakcheck.ScanSet, line: str) -> None:
    assert leakcheck.scan_text(line, scan_set) == [(1, "card")]


REFEREE_FORMATS = (
    "Придумов П. П.",
    "Придумов П.",
    "П. П. Придумов",
    "П. Придумов",
    "Придумов П.П.",
    "П.П. Придумов",
)


@pytest.mark.parametrize("referee", REFEREE_FORMATS)
def test_a_referee_is_searched_by_the_surname_not_by_the_initials(referee: str) -> None:
    """The initials are single letters: only the surname is a word of four letters or more."""
    original = copy.deepcopy(synth.personal_individual())
    as_dict(as_dict(racefile.races_of(original)[0])["data"])["chief_referee"] = referee
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("главный судья Придумов", scan) == [(1, "surname")]
    assert leakcheck.scan_text("П. П. судья", scan) == []


# ---------------------------------------------------------------- second Opus review


@pytest.mark.parametrize("stem", ["пп1 # не прошел КП 5", "пп6.6.4 # спортсмен сошел с трассы"])
@pytest.mark.parametrize("length", range(7, 21))
def test_a_correct_copy_never_leaks_whatever_the_length_of_the_hint(stem: str, length: int) -> None:
    """Short, exactly 14 and longer comments: the check mirrors what the anonymizer keeps."""
    comment = stem[:length]
    original = synth.personal_legacy_shape()
    _set_comment(original, 0, 1, comment, f"0:31:00       {comment[: synth.DAY_FIELD]:<14}")
    assert _leaks(leakcheck.check_pair(original, _anonymized(original))) == {}


def test_the_cut_of_a_comment_with_leading_spaces_is_searched() -> None:
    comment = "   Небылицкий П"  # 15 characters, 12 without the spaces
    original = synth.personal_legacy_shape()
    _set_comment(original, 0, 1, comment, "0:31:00       ")
    leaked = _anonymized(original)
    _shape_results(leaked, 0)[1]["multi_day_results"] = "0:31:00       " + comment[:14]
    assert _leaks(leakcheck.check_pair(original, leaked)) == {"leak:text": 1}


def test_scan_ignores_one_january_as_a_number() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0]["birth_date"] = 19_900_101
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("born 19900101", scan) == []


@pytest.mark.parametrize(
    "line",
    [
        "[код: pysport@b548c35 sportorg/models/memory.py:96-137,601-700]",
        "see file.py:120,135 and file.py:120.135",
        "took 123.456 s",
        "rgba(255,255,255,0.5)",
        "sizes 255, 255 and 137.601",
    ],
)
def test_scan_does_not_read_a_pair_of_groups_with_a_comma_or_a_dot_as_a_card(line: str) -> None:
    original = copy.deepcopy(synth.personal_individual())
    for person, card in zip(_persons(original), (137_601, 120_135, 123_456, 255_255), strict=False):
        person["card_number"] = card
    assert leakcheck.scan_text(line, leakcheck.scan_set([original])) == []


def test_scan_survives_a_very_long_run_of_digit_groups(scan_set: leakcheck.ScanSet) -> None:
    assert leakcheck.scan_text(" ".join(["123"] * 2000), scan_set) == []


def test_a_huge_number_as_a_birth_date_does_not_crash_the_extraction() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0]["birth_date"] = "9" * 5000
    assert leakcheck.scan_text("born 19900517", leakcheck.scan_set([original])) == []


# ---------------------------------------------------------------- third Opus review


@pytest.mark.parametrize(
    "comment",
    [
        "пп1 # не сдал\t",
        "пп1 # не сдал\xa0",
        "пп1 # не сдал\n",
        "пп1 # не про\t\t",
        "пп1 # не про\xa0\xa0",
    ],
)
def test_a_comment_ending_in_other_whitespace_than_spaces_is_measured_like_the_anonymizer(
    comment: str,
) -> None:
    """Legacy pads with spaces: the anonymizer measures a day field without spaces only."""
    original = synth.personal_legacy_shape()
    _set_comment(original, 0, 1, comment, f"0:31:00       {comment[: synth.DAY_FIELD]:<14}")
    assert _leaks(leakcheck.check_pair(original, _anonymized(original))) == {}


def test_a_card_after_a_long_run_of_groups_is_found() -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[1]["card_number"] = 212_345
    scan = leakcheck.scan_set([original])
    assert leakcheck.scan_text("100 200 300 400 212 345", scan) == [(1, "card")]
    assert leakcheck.scan_text("1 " + "100 " * 40 + "212 345", scan) == [(1, "card")]


@pytest.mark.parametrize("key", ["card_number", "national_code"])
@pytest.mark.parametrize("digits", ["1" * 5000, " ".join(["1" * 10] * 500)])
def test_a_huge_number_in_a_card_or_code_does_not_crash_extraction_or_scan(
    key: str, digits: str
) -> None:
    original = copy.deepcopy(synth.personal_individual())
    _persons(original)[0][key] = digits
    leakcheck.check_pair(original, original)
    assert leakcheck.scan_text("born 19900517", leakcheck.scan_set([original])) == []
