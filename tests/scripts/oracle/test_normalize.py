"""Tests for scripts/oracle_normalize.py: raw legacy snapshots → normalized schema v1.

Synthetic raw dicts in the shape the driver emits (a whitelisted subset of legacy ``to_dict``);
no legacy environment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts import oracle_normalize as norm
from scripts._json import as_dict, as_list

if TYPE_CHECKING:
    from scripts._json import Json

ENUMS: dict[str, Json] = {
    "ResultStatus": {"1": "OK", "4": "MISSING_PUNCH", "13": "DID_NOT_START"},
    "SystemType": {"1": "MANUAL", "2": "SPORTIDENT"},
    "RaceType": {"0": "INDIVIDUAL_RACE", "3": "RELAY"},
    "Qualification": {"0": "NOT_QUALIFIED", "6": "III"},
}

G1 = "00000000-0000-4000-8000-0000000000a1"
G2 = "00000000-0000-4000-8000-0000000000a2"


def _person(pid: str, bib: int, group: str | None) -> dict[str, Json]:
    return {"id": pid, "bib": bib, "group_id": group, "is_out_of_competition": False}


def _result(rid: str, pid: str | None, **fields: Json) -> dict[str, Json]:
    base: dict[str, Json] = {
        "object": "ResultSportident",
        "id": rid,
        "person_id": pid,
        "bib": 0,
        "system_type": 2,
        "status": 1,
        "place": 0,
        "result_msec": 0,
        "splits": [],
    }
    base.update(fields)
    return base


def _race(results: list[Json], persons: list[Json], **extra: Json) -> dict[str, Json]:
    race: dict[str, Json] = {
        "index": 0,
        "id": "00000000-0000-4000-8000-000000000001",
        "data": {"race_type": 0, "relay_leg_count": 3},
        "settings": {"result_processing_mode": "time", "time_accuracy": 0, "time_rounding": "math"},
        "groups": [
            {"id": G1, "name": "M21", "__type": None, "course_id": None},
            {"id": G2, "name": "D21", "__type": None, "course_id": None},
        ],
        "persons": persons,
        "results": results,
    }
    race.update(extra)
    return race


def _only_race(doc: Json) -> dict[str, Json]:
    races = as_list(as_dict(doc).get("races"))
    assert len(races) == 1
    return as_dict(races[0])


def _results(doc: Json) -> list[dict[str, Json]]:
    return [as_dict(r) for r in as_list(_only_race(doc).get("results"))]


def test_document_header_and_race_fields() -> None:
    doc = norm.normalize({"races": [_race([], [])]}, ENUMS)

    assert as_dict(doc)["schema"] == norm.SCHEMA
    assert as_dict(doc)["schema_version"] == 1
    race = _only_race(doc)
    assert race["race_id"] == "00000000-0000-4000-8000-000000000001"
    assert race["race_index"] == 0
    assert race["race_type"] == "INDIVIDUAL_RACE"
    assert race["processing_mode"] == "time"
    assert race["time_accuracy"] == 0
    assert race["time_rounding"] == "math"
    assert race["relay_teams"] == []


def test_result_fields_mapped_with_legacy_enums() -> None:
    raw = _result(
        "r1",
        "p1",
        status=4,
        place=-1,
        result_msec=840000,
        start_msec=36060000,
        finish_msec=36900000,
        penalty_time=None,
        credit_time=60000,
        penalty_laps=2,
        diff=None,
        scores=0,
        rogaine_score=5.0,
        rogaine_penalty=1,
        scores_ardf=0,
        diff_scores=0,
        assigned_rank=6,
        order=3,
    )
    doc = norm.normalize({"races": [_race([raw], [_person("p1", 7, G1)])]}, ENUMS)

    (result,) = _results(doc)
    assert result == {
        "result_id": "r1",
        "person_id": "p1",
        "group": "M21",
        "bib": 7,
        "system": "SPORTIDENT",
        "status": "MISSING_PUNCH",
        "place": -1,
        "time_ms": 840000,
        "start_ms": 36060000,
        "finish_ms": 36900000,
        "penalty_ms": None,
        "credit_ms": 60000,
        "penalty_laps": 2,
        "diff_ms": None,
        "scores": 0,
        "rogaine_score": 5.0,
        "rogaine_penalty": 1,
        "scores_ardf": 0,
        "diff_scores": 0,
        "rank": "III",
        "order": 3,
        "splits": [],
    }


def test_missing_raw_keys_become_null() -> None:
    raw: dict[str, Json] = {"object": "ResultManual", "id": "r1", "person_id": None}
    doc = norm.normalize({"races": [_race([raw], [])]}, ENUMS)

    (result,) = _results(doc)
    assert result["group"] is None
    assert result["bib"] is None
    assert result["status"] is None
    assert result["time_ms"] is None
    assert result["splits"] == []


def test_result_without_person_keeps_its_own_bib() -> None:
    doc = norm.normalize({"races": [_race([_result("r1", None, bib=42)], [])]}, ENUMS)

    (result,) = _results(doc)
    assert result["bib"] == 42
    assert result["group"] is None


def test_unknown_enum_value_is_kept_visible() -> None:
    doc = norm.normalize({"races": [_race([_result("r1", None, status=99)], [])]}, ENUMS)

    (result,) = _results(doc)
    assert result["status"] == "<99>"


def test_splits_in_punch_order_with_integer_times() -> None:
    splits: list[Json] = [
        {
            "code": "31",
            "time": 36300000,
            "leg_time": 300000,
            "relative_time": 300000,
            "leg_place": 1,
            "relative_place": 1,
            "is_correct": True,
            "course_index": 1,
        },
        {"code": "99", "time": 36400000, "is_correct": False},
    ]
    doc = norm.normalize(
        {"races": [_race([_result("r1", "p1", splits=splits)], [_person("p1", 1, G1)])]}, ENUMS
    )

    (result,) = _results(doc)
    assert result["splits"] == [
        {
            "code": "31",
            "time_ms": 36300000,
            "leg_ms": 300000,
            "relative_ms": 300000,
            "leg_place": 1,
            "relative_place": 1,
            "is_correct": True,
            "course_index": 1,
        },
        {
            "code": "99",
            "time_ms": 36400000,
            "leg_ms": None,
            "relative_ms": None,
            "leg_place": None,
            "relative_place": None,
            "is_correct": False,
            "course_index": None,
        },
    ]


def test_canonical_order_group_then_place_then_person() -> None:
    persons: list[Json] = [
        _person("p1", 1, G1),
        _person("p2", 2, G1),
        _person("p3", 3, G2),
        _person("p4", 4, G1),
        _person("p5", 5, None),
    ]
    results: list[Json] = [
        _result("r5", "p5", place=0),
        _result("r1", "p1", place=-1),
        _result("r2", "p2", place=2),
        _result("r3", "p3", place=1),
        _result("r4", "p4", place=1),
        _result("r0", None, place=0),
    ]
    doc = norm.normalize({"races": [_race(results, persons)]}, ENUMS)

    order = [r["result_id"] for r in _results(doc)]
    # D21 < M21 by code point; places 1, 2, then unplaced; results without a group last
    assert order == ["r3", "r4", "r2", "r1", "r0", "r5"]


def test_order_does_not_depend_on_input_order() -> None:
    persons: list[Json] = [_person("p1", 1, G1), _person("p2", 2, G1)]
    results: list[Json] = [_result("r1", "p1", place=-1), _result("r2", "p2", place=-1)]
    forward = norm.normalize({"races": [_race(results, persons)]}, ENUMS)
    backward = norm.normalize(
        {"races": [_race(results[::-1], persons[::-1])]},
        ENUMS,
    )

    assert norm.dumps(forward) == norm.dumps(backward)


def test_relay_teams_normalized_and_sorted() -> None:
    teams: list[Json] = [
        {
            "group_id": G1,
            "bib_number": 2,
            "place": -1,
            "order": 2,
            "time_ms": 0,
            "correct_legs": 1,
            "status_ok": False,
            "legs": [{"leg": 2, "result_id": "r22"}, {"leg": 1, "result_id": "r21"}],
        },
        {
            "group_id": G1,
            "bib_number": 1,
            "place": 1,
            "order": 1,
            "time_ms": 5400000,
            "correct_legs": 3,
            "status_ok": True,
            "legs": [{"leg": 1, "result_id": "r11"}],
        },
    ]
    doc = norm.normalize({"races": [_race([], [], relay_teams=teams)]}, ENUMS)

    relay = as_list(_only_race(doc)["relay_teams"])
    assert relay == [
        {
            "group": "M21",
            "bib": 1,
            "place": 1,
            "order": 1,
            "time_ms": 5400000,
            "correct_legs": 3,
            "status_ok": True,
            "legs": [{"leg": 1, "result_id": "r11"}],
        },
        {
            "group": "M21",
            "bib": 2,
            "place": -1,
            "order": 2,
            "time_ms": 0,
            "correct_legs": 1,
            "status_ok": False,
            "legs": [{"leg": 1, "result_id": "r21"}, {"leg": 2, "result_id": "r22"}],
        },
    ]


def test_extra_raw_keys_never_reach_the_output() -> None:
    person = _person("p1", 1, G1) | {"name": "Ivan", "surname": "Ivanov", "card_number": 8001234}
    result = _result("r1", "p1", card_number=8001234, status_comment="Ivanov called")
    doc = norm.normalize({"races": [_race([result], [person])]}, ENUMS)

    text = norm.dumps(doc)
    assert "Ivan" not in text
    assert "8001234" not in text


def test_dumps_is_canonical_json_with_final_newline() -> None:
    text = norm.dumps({"b": 1, "a": [1, 2], "c": "ё"})

    assert text == '{\n "a": [\n  1,\n  2\n ],\n "b": 1,\n "c": "ё"\n}\n'
