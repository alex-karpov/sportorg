"""Tests for scripts/oracle_driver/snapshot.py, the pure half of the oracle driver.

The driver runs under the legacy interpreter (Python 3.8). ``snapshot`` imports only the standard
library, so it is tested here in the project environment; ``driver.py`` (which imports ``sportorg``)
is covered by the integration tests in test_oracle_cli.py.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts._json import as_dict, as_list, parse_json
from scripts.oracle_driver import snapshot

DRIVER_DIR = Path(snapshot.__file__).parent

PERSON = {
    "object": "Person",
    "id": "p1",
    "name": "Ivan",
    "surname": "Ivanov",
    "middle_name": "Ivanovich",
    "card_number": 8001234,
    "bib": 7,
    "birth_date": "2010-05-17",
    "year": 2010,
    "birthday": "17.05.2010",
    "group_id": "g1",
    "organization_id": "o1",
    "world_code": "WRE1",
    "national_code": "NC1",
    "qual": 6,
    "is_out_of_competition": False,
    "comment": "phone 123",
    "start_time": 36000000,
}
RESULT = {
    "object": "ResultSportident",
    "id": "r1",
    "person_id": "p1",
    "card_number": 8001234,
    "status": 1,
    "status_comment": "Ivanov asked",
    "place": 1,
    "result_msec": 1000,
    "result": "00:00:01",
    "created_at": 1700000000.5,
    "can_win_count": 2,
    "final_result_time": "12:00:00",
    "splits": [{"code": "31", "time": 36300000, "leg_time": 300000, "days": 0, "speed": "5:00"}],
}
RACE = {
    "object": "Race",
    "id": "race-1",
    "data": {
        "title": "Cup of Ivanovo",
        "location": "Ivanovo",
        "chief_referee": "Petrov",
        "secretary": "Sidorova",
        "race_type": 0,
        "relay_leg_count": 3,
    },
    "settings": {
        "result_processing_mode": "time",
        "time_accuracy": 0,
        "live_urls": ["https://example.invalid/x"],
        "telegram_chat_id": "42",
    },
    "organizations": [{"object": "Organization", "id": "o1", "name": "Club Ivanov"}],
    "courses": [],
    "groups": [{"object": "Group", "id": "g1", "name": "M21", "long_name": "Men", "price": 100}],
    "persons": [PERSON],
    "results": [RESULT],
}


@pytest.mark.parametrize("name", ["driver.py", "snapshot.py"])
def test_driver_source_parses_as_python_3_8(name: str) -> None:
    ast.parse((DRIVER_DIR / name).read_text(encoding="utf-8"), feature_version=(3, 8))


def test_filter_race_keeps_whitelisted_keys_only() -> None:
    filtered = snapshot.filter_race(RACE, 0)

    assert filtered == {
        "index": 0,
        "id": "race-1",
        "data": {"race_type": 0, "relay_leg_count": 3},
        "settings": {"result_processing_mode": "time", "time_accuracy": 0},
        "groups": [{"id": "g1", "name": "M21"}],
        "persons": [{"id": "p1", "bib": 7, "group_id": "g1", "is_out_of_competition": False}],
        "results": [
            {
                "object": "ResultSportident",
                "id": "r1",
                "person_id": "p1",
                "status": 1,
                "place": 1,
                "result_msec": 1000,
                "splits": [{"code": "31", "time": 36300000, "leg_time": 300000}],
            }
        ],
    }


def test_filtered_race_holds_no_personal_data() -> None:
    text = json.dumps(snapshot.filter_race(RACE, 0), ensure_ascii=False)

    for secret in ("Ivan", "8001234", "2010", "WRE1", "NC1", "phone", "Petrov", "Sidorova", "42"):
        assert secret not in text


def test_stored_races_accepts_the_formats_legacy_accepts() -> None:
    # [код: pysport@b548c35 sportorg/modules/backup/json.py:55-60]
    assert snapshot.stored_races({"races": [RACE], "current_race": 0}) == [RACE]
    assert snapshot.stored_races(RACE) == [RACE]
    assert snapshot.stored_races([RACE, RACE]) == [RACE, RACE]


def test_clock_dependent_counts_results_without_finish() -> None:
    races: list[object] = [
        {"results": [{"finish_time": None}, {"finish_time": 1}, {}]},
        {"results": []},
    ]

    assert snapshot.clock_dependent(races) == 2


@pytest.mark.parametrize(
    ("text", "msec"), [("00:00:00", 0), ("10:00:00", 36000000), ("23:59:59", 86399000)]
)
def test_parse_now(text: str, msec: int) -> None:
    assert snapshot.parse_now(text) == msec


@pytest.mark.parametrize("text", ["24:00:00", "10:60:00", "10:00", "x"])
def test_parse_now_rejects_bad_times(text: str) -> None:
    with pytest.raises(ValueError, match="HH:MM:SS"):
        snapshot.parse_now(text)


def _raise_with_personal_data() -> None:
    msg = "Ivanov Ivan 8001234"
    raise KeyError(msg)


def test_error_report_has_type_and_frames_but_no_message() -> None:
    with pytest.raises(KeyError) as info:
        _raise_with_personal_data()
    report = snapshot.error_report(info.value)

    assert report["type"] == "KeyError"
    frames = as_list(report["frames"])
    assert frames
    assert all(len(as_list(f)) == 3 for f in frames)
    assert as_list(frames[-1])[2] == "_raise_with_personal_data"
    assert "Ivanov" not in json.dumps(report)


def test_short_path_keeps_the_package_part_only() -> None:
    legacy = "/home/u/src/sportorg/.legacy-run/pysport/sportorg/models/memory.py"

    assert snapshot.short_path(legacy) == "sportorg/models/memory.py"
    assert snapshot.short_path("/usr/lib/python3.8/uuid.py") == "uuid.py"
    assert snapshot.short_path("C:\\Users\\u\\pysport\\sportorg\\models\\memory.py") == (
        "sportorg/models/memory.py"
    )


def test_guarded_writes_the_payload_with_the_protocol(tmp_path: Path) -> None:
    raw = tmp_path / "raw.json"

    code = snapshot.guarded(str(raw), lambda: {"meta": {"python": "3.8.20"}})

    assert code == snapshot.EXIT_OK
    assert parse_json(raw.read_text(encoding="utf-8")) == {
        "protocol": snapshot.PROTOCOL,
        "meta": {"python": "3.8.20"},
    }


def test_guarded_turns_a_legacy_error_into_a_report_without_message(tmp_path: Path) -> None:
    raw = tmp_path / "raw.json"

    def work() -> dict[str, object]:
        _raise_with_personal_data()
        return {}

    code = snapshot.guarded(str(raw), work)

    assert code == snapshot.EXIT_LEGACY_ERROR
    text = raw.read_text(encoding="utf-8")
    assert "Ivanov" not in text
    report = as_dict(as_dict(parse_json(text)).get("error"))
    assert report["type"] == "KeyError"
