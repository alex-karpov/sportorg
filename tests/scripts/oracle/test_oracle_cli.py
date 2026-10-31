"""Tests for scripts/oracle_cli.py and the entry point scripts/oracle.py (TASK-8 AC #1).

Unit tests replace the driver with tests/scripts/oracle/fake_driver.py and run everywhere.
Integration tests run the real driver in the legacy runtime (``.legacy-run/pysport/.venv``); they
are skipped where that runtime does not exist (CI has no legacy checkout).
"""

from __future__ import annotations

import gzip
import io
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from scripts import oracle_cli
from scripts._json import Json, as_dict, as_list, parse_json
from scripts.corpus import synth
from scripts.legacy import ROOT
from scripts.legacy_env import clone_path, env_python
from scripts.oracle_normalize import dumps

if TYPE_CHECKING:
    from collections.abc import Callable

FAKE = "tests.scripts.oracle.fake_driver"
ENUMS: dict[str, Json] = {"ResultStatus": {"1": "OK"}, "SystemType": {}, "RaceType": {"0": "X"}}
RAW_RACE: dict[str, Json] = {
    "index": 0,
    "id": "race-1",
    "data": {"race_type": 0},
    "settings": {},
    "groups": [{"id": "g1", "name": "M21"}],
    "persons": [{"id": "p1", "bib": 1, "group_id": "g1"}],
    "results": [{"id": "r1", "person_id": "p1", "status": 1, "place": 1, "result_msec": 1000}],
}
PAYLOAD: dict[str, Json] = {
    "meta": {"python": "3.14.x", "now_ms": 0},
    "enums": ENUMS,
    "stored": {"races": [RAW_RACE | {"results": []}]},
    "recalculated": {"races": [RAW_RACE]},
}


def _fake_file(tmp_path: Path, payload: Json) -> Path:
    path = tmp_path / "race.json"
    path.write_text(synth.dumps(payload), encoding="utf-8")
    return path


def _fake_oracle(race_file: Path, *, now: str = "00:00:00") -> oracle_cli.OracleRun:
    return oracle_cli.oracle(race_file, python_exe=Path(sys.executable), now=now, module=FAKE)


def test_oracle_normalizes_both_snapshots_and_compares_them(tmp_path: Path) -> None:
    run = _fake_oracle(_fake_file(tmp_path, PAYLOAD))

    (race,) = as_list(as_dict(run.results)["races"])
    (result,) = as_list(as_dict(race)["results"])
    assert as_dict(result)["status"] == "OK"
    assert as_list(as_dict(as_list(as_dict(run.stored)["races"])[0])["results"]) == []
    assert as_dict(as_dict(run.comparison)["races"]) is not None
    meta = as_dict(run.run)
    assert meta["python"] == "3.14.x"
    assert meta["schema_version"] == 1
    assert isinstance(meta["input_sha256"], str)
    assert len(meta["input_sha256"]) == 64


def test_oracle_passes_the_clock(tmp_path: Path) -> None:
    run = _fake_oracle(_fake_file(tmp_path, PAYLOAD), now="12:34:56")

    assert as_dict(run.run)["now_arg"] == "12:34:56"


def test_legacy_error_is_reported_without_its_message(tmp_path: Path) -> None:
    with pytest.raises(oracle_cli.OracleError) as info:
        _fake_oracle(_fake_file(tmp_path, {"raise": True}))

    text = str(info.value)
    assert "KeyError" in text
    assert "fake_driver.py" in text
    assert "Ivanov" not in text


def test_driver_crash_hides_stderr(tmp_path: Path) -> None:
    with pytest.raises(oracle_cli.OracleError) as info:
        _fake_oracle(_fake_file(tmp_path, {"crash": True}))

    text = str(info.value)
    assert "exit 1" in text
    assert "--show-stderr" in text
    assert "Ivanov" not in text


def test_write_run_writes_the_four_files(tmp_path: Path) -> None:
    run = _fake_oracle(_fake_file(tmp_path, PAYLOAD))
    out = tmp_path / "out"

    oracle_cli.write_run(run, out)

    assert sorted(p.name for p in out.iterdir()) == sorted(oracle_cli.OUTPUT_FILES)
    assert parse_json((out / "results.json").read_text(encoding="utf-8")) == run.results


def test_main_without_legacy_runtime_says_how_to_make_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = oracle_cli.main([str(_fake_file(tmp_path, PAYLOAD)), "--venv", str(tmp_path / "no")])

    assert code == 1
    assert "scripts.legacy_env sync" in capsys.readouterr().err


def test_main_rejects_a_bad_clock(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as info:
        oracle_cli.main([str(_fake_file(tmp_path, PAYLOAD)), "--now", "25:00:00"])

    assert info.value.code == 2  # argparse usage error


def test_main_prints_results_without_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(oracle_cli, "DRIVER_MODULE", FAKE)

    def this_python(_venv: Path) -> Path:
        return Path(sys.executable)

    monkeypatch.setattr(oracle_cli, "env_python", this_python)

    code = oracle_cli.main([str(_fake_file(tmp_path, PAYLOAD))])

    assert code == 0
    assert (
        parse_json(capsys.readouterr().out) == _fake_oracle(_fake_file(tmp_path, PAYLOAD)).results
    )


def test_entry_point_runs_as_a_file() -> None:
    done = subprocess.run(  # noqa: S603 - fixed argv: this interpreter and a repository script
        [sys.executable, str(ROOT / "scripts" / "oracle.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )

    assert done.returncode == 0, done.stderr
    assert "RACE_FILE" in done.stdout


# ---------------------------------------------------------------- integration (legacy runtime)

LEGACY_PYTHON = env_python(clone_path() / ".venv")
requires_legacy = pytest.mark.skipif(
    not LEGACY_PYTHON.exists(),
    reason="no legacy runtime: uv run python -m scripts.legacy_env sync --python 3.8 (ADR-0009 T1)",
)


@pytest.fixture(scope="module")
def synth_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("synth")
    assert synth.main(["--out", str(out)]) == 0
    return out


def _legacy(race_file: Path, *, now: str = "00:00:00") -> oracle_cli.OracleRun:
    return oracle_cli.oracle(race_file, python_exe=LEGACY_PYTHON, now=now)


def _by_bib(run: oracle_cli.OracleRun) -> dict[int, dict[str, Json]]:
    found: dict[int, dict[str, Json]] = {}
    for race in as_list(as_dict(run.results)["races"]):
        for result in map(as_dict, as_list(as_dict(race)["results"])):
            bib = result["bib"]
            assert isinstance(bib, int)
            found[bib] = result
    return found


@pytest.fixture(scope="module")
def individual(synth_dir: Path) -> oracle_cli.OracleRun:
    return _legacy(synth_dir / "individual.json")


def _outcome(result: dict[str, Json]) -> tuple[Json, Json, Json]:
    return result["status"], result["place"], result["time_ms"]


@requires_legacy
def test_ac1_command_runs_without_display(synth_dir: Path) -> None:
    env = {k: v for k, v in os.environ.items() if k not in {"DISPLAY", "WAYLAND_DISPLAY"}}
    done = subprocess.run(  # noqa: S603 - fixed argv: this interpreter and a repository script
        [sys.executable, "scripts/oracle.py", str(synth_dir / "individual.json")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
        env=env,
    )

    assert done.returncode == 0, done.stderr
    doc = as_dict(parse_json(done.stdout))
    assert doc["schema_version"] == 1
    assert len(as_list(as_dict(as_list(doc["races"])[0])["results"])) == 11


@requires_legacy
def test_individual_outcomes(individual: oracle_cli.OracleRun) -> None:
    minute = 60_000
    got = {bib: _outcome(r) for bib, r in _by_bib(individual).items()}
    # [код: pysport@b548c35 sportorg/models/result/result_calculation.py:155-191]: places by time,
    # equal times share a place and the next place is skipped; out of competition gets -1.
    assert got[101] == ("OK", 1, 30 * minute)
    assert got[102] == ("OK", 2, 32 * minute)
    assert got[103] == ("OK", 2, 32 * minute)
    assert got[107] == ("OK", 4, 35 * minute)  # extra punch 99 is ignored
    assert got[105][:2] == ("OK", -1)
    # [код: pysport@b548c35 sportorg/models/result/result_checker.py:68-85]
    assert got[104][:2] == ("MISSING_PUNCH", -1)
    assert got[106][0] == "DID_NOT_START"
    # whole seconds, math rounding [код: pysport@b548c35 sportorg/common/otime.py:175-191]
    assert got[201] == ("OK", 1, 31 * minute)
    assert got[202] == ("OK", 2, 31 * minute + 1000)
    # group limit 30:00
    # [код: pysport@b548c35 sportorg/models/result/result_checker.py:89-92,166-178]
    assert got[301][0] == "OVERTIME"
    assert got[302] == ("OK", 1, 28 * minute)


@requires_legacy
def test_splits_of_a_clean_run(individual: oracle_cli.OracleRun) -> None:
    splits = [as_dict(s) for s in as_list(_by_bib(individual)[101]["splits"])]

    assert [s["code"] for s in splits] == ["31", "32", "33"]
    assert [s["leg_ms"] for s in splits] == [300_000, 600_000, 600_000]
    assert all(s["is_correct"] is True for s in splits)


@requires_legacy
def test_two_runs_byte_identical(synth_dir: Path, tmp_path: Path) -> None:
    first, second = tmp_path / "1", tmp_path / "2"
    oracle_cli.write_run(_legacy(synth_dir / "individual.json"), first)
    oracle_cli.write_run(_legacy(synth_dir / "individual.json"), second)

    for name in oracle_cli.OUTPUT_FILES:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def _edited(source: Path, target: Path, edit: Callable[[dict[str, Json]], None]) -> Path:
    doc = as_dict(parse_json(source.read_text(encoding="utf-8")))
    edit(doc)
    target.write_text(synth.dumps(doc), encoding="utf-8")
    return target


@requires_legacy
def test_finish_change_moves_place(
    synth_dir: Path, tmp_path: Path, individual: oracle_cli.OracleRun
) -> None:
    """Canary: a later finish of bib 101 (30:00 → 33:00) moves it from 1st to 3rd."""
    minute = 60_000
    before = _by_bib(individual)[101]
    pid = before["person_id"]

    def later_finish(doc: dict[str, Json]) -> None:
        race = as_dict(as_list(doc["races"])[0])
        for result in map(as_dict, as_list(race["results"])):
            finish = result["finish_time"]
            if result["person_id"] == pid and isinstance(finish, int):
                result["finish_time"] = finish + 3 * minute

    changed = _legacy(_edited(synth_dir / "individual.json", tmp_path / "x.json", later_finish))

    assert _outcome(before) == ("OK", 1, 30 * minute)
    assert _outcome(_by_bib(changed)[101]) == ("OK", 3, 33 * minute)
    assert _by_bib(changed)[102]["place"] == 1


@requires_legacy
def test_clock_is_an_input(synth_dir: Path, individual: oracle_cli.OracleRun) -> None:
    later = _legacy(synth_dir / "individual.json", now="12:00:00")

    assert as_dict(individual.run)["now_ms"] == 0
    assert as_dict(later.run)["now_ms"] == 12 * 3_600_000
    assert as_dict(individual.run)["clock_dependent_results"] == 1
    # only the DNS result has no finish: only its time follows the clock
    changed = [
        bib
        for bib, r in _by_bib(individual).items()
        if r["time_ms"] != _by_bib(later)[bib]["time_ms"]
    ]
    assert changed == [106]


@requires_legacy
def test_relay_outcomes(synth_dir: Path) -> None:
    run = _legacy(synth_dir / "relay.json")
    teams = [
        as_dict(t)
        for t in as_list(as_dict(as_list(as_dict(run.results)["races"])[0])["relay_teams"])
    ]
    got = {t["bib"]: (t["place"], t["status_ok"]) for t in teams}

    # [код: pysport@b548c35 sportorg/models/result/result_calculation.py:193-226]
    assert got == {2: (1, True), 1: (2, True), 3: (-1, False)}
    results = _by_bib(run)
    assert results[2003]["status"] == "MISSING_PUNCH"
    assert results[1002]["place"] == results[2002]["place"] == 1


@requires_legacy
def test_rogaine_scores(synth_dir: Path) -> None:
    results = _by_bib(_legacy(synth_dir / "rogaine.json"))
    got = {bib: (r["rogaine_score"], r["rogaine_penalty"]) for bib, r in results.items()}

    # score = code // 10, a duplicate counts once, 1 point per started minute over 60:00
    # [код: pysport@b548c35 sportorg/models/result/result_checker.py:458-527]
    assert got == {1: (12, 0), 2: (7, 0), 3: (15, 3), 4: (7, 0), 5: (5, 0)}
    assert [results[b]["place"] for b in (3, 1, 2, 4)] == [1, 2, 3, 3]


def test_driver_command_uses_absolute_paths_without_resolving_links() -> None:
    cmd = oracle_cli.driver_command(
        Path(".legacy-run/pysport/.venv-3.13/bin/python"),
        Path("in/race.json"),
        Path("raw.json"),
        now="00:00:00",
        module=FAKE,
    )

    assert cmd[0] == str(Path.cwd() / ".legacy-run/pysport/.venv-3.13/bin/python")
    assert cmd[1:3] == ["-m", FAKE]
    assert cmd[3] == str(Path.cwd() / "in/race.json")
    assert cmd[4:] == ["raw.json", "--now", "00:00:00"]


def test_main_writes_utf8_with_lf_whatever_the_console(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A redirected stdout on Windows has the locale encoding and CRLF; the output must not."""
    groups: list[Json] = [{"id": "g1", "name": "\u0416" + "21"}]  # a Cyrillic group name
    race: dict[str, Json] = {**RAW_RACE, "groups": groups}
    payload: dict[str, Json] = {**PAYLOAD, "recalculated": {"races": [race]}}
    race_file = _fake_file(tmp_path, payload)
    raw = io.BytesIO()
    console = io.TextIOWrapper(raw, encoding="cp1251", newline="\r\n")
    monkeypatch.setattr(oracle_cli, "DRIVER_MODULE", FAKE)

    def this_python(_venv: Path) -> Path:
        return Path(sys.executable)

    monkeypatch.setattr(oracle_cli, "env_python", this_python)
    monkeypatch.setattr(sys, "stdout", console)

    code = oracle_cli.main([str(race_file)])
    console.flush()

    assert code == 0
    expected = dumps(_fake_oracle(race_file).results).encode("utf-8")
    assert raw.getvalue() == expected


# ---------------------------------------------------------------- integration: review fixes

SECRETS: dict[str, Json] = {
    "name": "Secretname",
    "surname": "Secretsurname",
    "middle_name": "Secretmiddle",
    "comment": "Secretcomment",
    "world_code": "SecretWRE",
    "birth_date": "2011-03-04",
    "card_number": 7654321,
}


def _with_secrets(doc: dict[str, Json]) -> None:
    race = as_dict(as_list(doc["races"])[0])
    as_dict(race["data"]).update(
        {"title": "Secrettitle", "location": "Secretplace", "chief_referee": "Secretjudge"}
    )
    club: dict[str, Json] = {
        "object": "Organization",
        "id": synth.RaceBuilder("x", 0, {}).id("organization", "secret"),
        "name": "Secretclub",
        "contact": "Secretcontact",
    }
    race["organizations"] = [club]
    for person in map(as_dict, as_list(race["persons"])):
        person.update(SECRETS)
        person["organization_id"] = club["id"]
    for result in map(as_dict, as_list(race["results"])):
        result.update({"card_number": 7654321, "status_comment": "Secretstatus"})


@requires_legacy
def test_no_personal_data_reaches_any_output(synth_dir: Path, tmp_path: Path) -> None:
    race_file = _edited(synth_dir / "individual.json", tmp_path / "s.json", _with_secrets)
    run = _legacy(race_file)

    texts = [dumps(doc) for doc in (run.results, run.stored, run.comparison, run.run)]
    secrets = ["Secret", "7654321", "2011"]
    assert [s for s in secrets for text in texts if s in text] == []
    assert _outcome(_by_bib(run)[101])[:2] == ("OK", 1)  # the race itself is unchanged


@requires_legacy
def test_a_legacy_error_is_sanitized_end_to_end(synth_dir: Path, tmp_path: Path) -> None:
    def bad_status(doc: dict[str, Json]) -> None:
        race = as_dict(as_list(doc["races"])[0])
        as_dict(as_list(race["results"])[0])["status"] = "Secretsurname-7654321"

    race_file = _edited(synth_dir / "individual.json", tmp_path / "bad.json", bad_status)
    with pytest.raises(oracle_cli.OracleError) as info:
        _legacy(race_file)

    text = str(info.value)
    assert "ValueError" in text
    assert "sportorg/models/memory.py" in text
    assert "Secret" not in text
    assert "7654321" not in text


@requires_legacy
def test_gzip_file_gives_the_same_results(synth_dir: Path, tmp_path: Path) -> None:
    source = synth_dir / "individual.json"
    packed = tmp_path / "individual.json"
    packed.write_bytes(gzip.compress(source.read_bytes(), mtime=0))

    plain, zipped = _legacy(source), _legacy(packed)

    assert dumps(zipped.results) == dumps(plain.results)
    assert as_dict(zipped.run)["file_format"] == "gzip"


@requires_legacy
def test_a_file_that_is_not_utf8_is_refused_by_name(synth_dir: Path, tmp_path: Path) -> None:
    """Legacy retries in the machine's locale (cp1251 on Russian Windows); the oracle won't guess.

    [код: pysport@b548c35 sportorg/modules/backup/file.py:45-51]
    """
    cyrillic = "\u041c21"  # M21 with a Cyrillic EM: not ASCII, so the encoding matters
    text = (synth_dir / "individual.json").read_text(encoding="utf-8").replace("M21", cyrillic)
    race_file = tmp_path / "cp1251.json"
    race_file.write_bytes(text.encode("cp1251"))

    with pytest.raises(oracle_cli.OracleError) as info:
        _legacy(race_file)

    message = str(info.value)
    assert "NotUtf8RaceFile" in message
    assert "driver or legacy raised" in message


@requires_legacy
def test_each_race_of_a_multi_race_file_in_its_own_context(synth_dir: Path, tmp_path: Path) -> None:
    """A rogaine as the second, non-current race is scored as when it is alone in a file.

    Legacy's load recalculates every race against the current one (``_check_all`` reads
    ``race()``) [код: pysport@b548c35 sportorg/models/result/result_tools.py:105]; the oracle then
    recalculates each race as the current one (ADR-0009 T5).
    """
    first = as_dict(parse_json((synth_dir / "individual.json").read_text(encoding="utf-8")))
    second = as_dict(parse_json((synth_dir / "rogaine.json").read_text(encoding="utf-8")))
    races: list[Json] = [*as_list(first["races"]), *as_list(second["races"])]
    both: dict[str, Json] = {**first, "races": races}
    race_file = tmp_path / "two.json"
    race_file.write_text(synth.dumps(both), encoding="utf-8")

    combined = as_list(as_dict(_legacy(race_file).results)["races"])
    alone = as_list(as_dict(_legacy(synth_dir / "rogaine.json").results)["races"])

    assert len(combined) == 2
    assert as_dict(combined[1])["results"] == as_dict(alone[0])["results"]
