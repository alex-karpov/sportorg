"""Tests for scripts/corpus/synth.py: synthetic race files in the legacy JSON format.

Shape only (no legacy environment): the keys legacy's ``update_data`` reads unconditionally are
present, ids are valid and stable, nothing looks like personal data. What legacy computes from
these files is checked by the integration tests in test_oracle_cli.py.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_list, parse_json
from scripts.corpus import synth

if TYPE_CHECKING:
    from pathlib import Path

    from scripts._json import Json

# Keys read with data[...] (KeyError when absent) by legacy update_data / _race_migrate.
REQUIRED = {
    # [код: pysport@b548c35 sportorg/modules/backup/json.py:84-104]
    # [код: pysport@b548c35 sportorg/models/memory.py:1820-1832]
    "race": {
        "object",
        "id",
        "data",
        "settings",
        "organizations",
        "courses",
        "groups",
        "persons",
        "results",
    },
    # [код: pysport@b548c35 sportorg/models/memory.py:1630-1643]
    "data": {
        "title",
        "description",
        "location",
        "chief_referee",
        "secretary",
        "url",
        "race_type",
        "relay_leg_count",
        "start_datetime",
        "end_datetime",
    },
    # [код: pysport@b548c35 sportorg/models/memory.py:273-284]
    "course": {"object", "id", "name", "bib", "length", "climb", "corridor", "controls"},
    "control": {"code", "length"},
    # [код: pysport@b548c35 sportorg/models/memory.py:390-415, 1860-1862]
    "group": {
        "object",
        "id",
        "name",
        "course_id",
        "long_name",
        "price",
        "min_year",
        "max_year",
        "min_age",
        "max_age",
        "max_time",
        "start_interval",
        "start_corridor",
        "order_in_corridor",
        "first_number",
        "relay_legs",
        "__type",
    },
    # [код: pysport@b548c35 sportorg/models/memory.py:1453-1477, 1847-1849]
    "person": {
        "object",
        "id",
        "name",
        "surname",
        "card_number",
        "bib",
        "world_code",
        "national_code",
        "qual",
        "is_out_of_competition",
        "is_paid",
        "is_rented_card",
        "is_personal",
        "comment",
        "start_group",
        "start_time",
        "birth_date",
        "group_id",
        "organization_id",
    },
    # [код: pysport@b548c35 sportorg/models/memory.py:650-664, 1850-1859]
    "result": {
        "object",
        "id",
        "person_id",
        "status",
        "penalty_laps",
        "scores",
        "place",
        "assigned_rank",
        "start_time",
        "finish_time",
        "penalty_time",
    },
    # [код: pysport@b548c35 sportorg/models/memory.py:472-475]
    "split": {"code", "time"},
}


def _races() -> list[tuple[str, dict[str, Json]]]:
    return [(name, as_dict(build())) for name, build in synth.RACES.items()]


@pytest.mark.parametrize(("name", "doc"), _races())
def test_race_files_have_the_keys_legacy_requires(name: str, doc: dict[str, Json]) -> None:
    for race_dict in map(as_dict, as_list(doc["races"])):
        assert REQUIRED["race"] <= race_dict.keys(), name
        assert REQUIRED["data"] <= as_dict(race_dict["data"]).keys()
        for course in map(as_dict, as_list(race_dict["courses"])):
            assert REQUIRED["course"] <= course.keys()
            controls = as_list(course["controls"])
            assert all(REQUIRED["control"] <= as_dict(c).keys() for c in controls)
        for group in map(as_dict, as_list(race_dict["groups"])):
            assert REQUIRED["group"] <= group.keys()
        for person in map(as_dict, as_list(race_dict["persons"])):
            assert REQUIRED["person"] <= person.keys()
        for result in map(as_dict, as_list(race_dict["results"])):
            assert REQUIRED["result"] <= result.keys()
            assert all(REQUIRED["split"] <= as_dict(s).keys() for s in as_list(result["splits"]))


@pytest.mark.parametrize(("name", "doc"), _races())
def test_ids_are_uuids_and_references_resolve(name: str, doc: dict[str, Json]) -> None:
    for race in map(as_dict, as_list(doc["races"])):
        ids: dict[str, set[str]] = {}
        for key in ("courses", "groups", "persons", "results", "organizations"):
            items = map(as_dict, as_list(race[key]))
            ids[key] = {i for item in items if isinstance(i := item["id"], str)}
        for found in ids.values():
            for value in found:
                uuid.UUID(value)
        groups = map(as_dict, as_list(race["groups"]))
        assert all(g["course_id"] in ids["courses"] | {None} for g in groups), name
        persons = list(map(as_dict, as_list(race["persons"])))
        assert all(p["group_id"] in ids["groups"] for p in persons)
        assert all(p["organization_id"] in ids["organizations"] | {None} for p in persons)
        results = map(as_dict, as_list(race["results"]))
        assert all(r["person_id"] in ids["persons"] for r in results)


@pytest.mark.parametrize(("name", "doc"), _races())
def test_no_personal_data_shapes(name: str, doc: dict[str, Json]) -> None:
    for race in map(as_dict, as_list(doc["races"])):
        for person in map(as_dict, as_list(race["persons"])):
            assert person["card_number"] == 0, name
            assert person["birth_date"] is None
            assert person["name"] == "Synthetic"
        for result in map(as_dict, as_list(race["results"])):
            assert result.get("card_number", 0) == 0


def test_files_for_the_maintainer_check_of_f3_f4_f6() -> None:
    assert {"f3_rogaine_tie", "f4_slow_leader", "f6_two_races"} <= synth.RACES.keys()


def test_two_race_file_is_one_event_that_is_not_multi_day() -> None:
    doc = as_dict(synth.f6_two_races())
    first, second = map(as_dict, as_list(doc["races"]))

    assert doc["current_race"] == 0
    assert as_dict(first["data"])["race_type"] == synth.INDIVIDUAL
    assert as_dict(second["settings"])["result_processing_mode"] == "scores"
    assert first["id"] != second["id"]
    titles = [as_dict(r["data"])["short_title"] for r in (first, second)]
    assert all(titles), "the race list in the GUI shows short_title"
    assert len(set(titles)) == 2


def test_generation_is_deterministic() -> None:
    first = {name: synth.dumps(build()) for name, build in synth.RACES.items()}
    second = {name: synth.dumps(build()) for name, build in synth.RACES.items()}

    assert first == second


def test_cli_writes_one_file_per_race(tmp_path: Path) -> None:
    assert synth.main(["--out", str(tmp_path)]) == 0

    written = sorted(p.name for p in tmp_path.iterdir())
    assert written == sorted(f"{name}.json" for name in synth.RACES)
    for name, build in synth.RACES.items():
        text = (tmp_path / f"{name}.json").read_text(encoding="utf-8")
        assert parse_json(text) == build()
