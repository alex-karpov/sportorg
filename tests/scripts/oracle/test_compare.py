"""Tests for scripts/oracle_compare.py: stored results vs legacy recalculation, field by field."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts import oracle_compare
from scripts._json import as_dict, as_list

if TYPE_CHECKING:
    from scripts._json import Json


def _result(rid: str, **fields: Json) -> dict[str, Json]:
    result: dict[str, Json] = {
        "result_id": rid,
        "person_id": f"p-{rid}",
        "group": "M21",
        "status": "OK",
        "place": 1,
        "time_ms": 1000,
        "splits": [],
    }
    result.update(fields)
    return result


def _doc(*results: Json, race_id: str = "race-1") -> Json:
    return {"races": [{"race_id": race_id, "race_index": 0, "results": list(results)}]}


def _race(report: Json) -> dict[str, Json]:
    (race,) = as_list(as_dict(report).get("races"))
    return as_dict(race)


def _field(report: Json, name: str) -> dict[str, Json]:
    return as_dict(as_dict(_race(report).get("fields")).get(name))


def test_identical_documents_have_no_differences() -> None:
    doc = _doc(_result("r1"), _result("r2", place=2, time_ms=2000))

    report = oracle_compare.compare(doc, doc)

    assert as_dict(report)["different"] == 0
    assert _race(report)["differences"] == []
    assert _field(report, "place") == {"same": 2, "different": 0, "not_stored": 0}


def test_changed_field_is_counted_and_listed() -> None:
    stored = _doc(_result("r1", place=1), _result("r2", place=2))
    recalculated = _doc(_result("r1", place=2), _result("r2", place=2))

    report = oracle_compare.compare(stored, recalculated)

    assert as_dict(report)["different"] == 1
    assert _field(report, "place") == {"same": 1, "different": 1, "not_stored": 0}
    assert _race(report)["differences"] == [
        {"result_id": "r1", "field": "place", "stored": 1, "recalculated": 2}
    ]


def test_value_missing_in_file_is_not_stored_not_different() -> None:
    stored = _doc({k: v for k, v in _result("r1").items() if k != "time_ms"})
    recalculated = _doc(_result("r1", time_ms=1000))

    report = oracle_compare.compare(stored, recalculated)

    assert _field(report, "time_ms") == {"same": 0, "different": 0, "not_stored": 1}
    assert as_dict(report)["different"] == 0


def test_integer_and_float_of_the_same_value_are_equal() -> None:
    report = oracle_compare.compare(
        _doc(_result("r1", rogaine_score=5)), _doc(_result("r1", rogaine_score=5.0))
    )

    assert _field(report, "rogaine_score")["different"] == 0


def test_split_fields_compared_per_index() -> None:
    split: dict[str, Json] = {"code": "31", "leg_ms": 300, "is_correct": True}
    stored = _doc(_result("r1", splits=[split, split]))
    recalculated = _doc(_result("r1", splits=[split, split | {"leg_ms": 400}]))

    report = oracle_compare.compare(stored, recalculated)

    assert _field(report, "splits.leg_ms") == {"same": 0, "different": 1, "not_stored": 0}
    assert _race(report)["differences"] == [
        {"result_id": "r1", "field": "splits[1].leg_ms", "stored": 300, "recalculated": 400}
    ]


def test_split_count_mismatch_is_one_difference() -> None:
    split: dict[str, Json] = {"code": "31", "leg_ms": 300}
    report = oracle_compare.compare(
        _doc(_result("r1", splits=[split])), _doc(_result("r1", splits=[split, split]))
    )

    assert _field(report, "splits.count") == {"same": 0, "different": 1, "not_stored": 0}


def test_results_only_on_one_side_are_counted() -> None:
    report = oracle_compare.compare(_doc(_result("r1")), _doc(_result("r2")))

    assert as_dict(_race(report)["results"]) == {
        "stored": 1,
        "recalculated": 1,
        "only_stored": 1,
        "only_recalculated": 1,
    }


def test_counts_only_drops_values_and_ids() -> None:
    stored = _doc(_result("r1", place=1))
    recalculated = _doc(_result("r1", place=2))

    text = repr(oracle_compare.counts_only(oracle_compare.compare(stored, recalculated)))

    assert "r1" not in text
    assert "race-1" not in text
    assert "differences" not in text
    assert "'different': 1" in text


def test_stored_null_differs_from_a_recalculated_value() -> None:
    """Legacy writes a zero time behind, penalty or credit as null; a file that holds null held 0.

    [код: pysport@b548c35 sportorg/models/memory.py:612,614,615]
    """
    stored = _doc(_result("r1", penalty_ms=None, credit_ms=None, diff_ms=None))
    recalculated = _doc(_result("r1", penalty_ms=60000, credit_ms=None, diff_ms=0))

    report = oracle_compare.compare(stored, recalculated)

    assert _field(report, "penalty_ms") == {"same": 0, "different": 1, "not_stored": 0}
    assert _field(report, "credit_ms") == {"same": 1, "different": 0, "not_stored": 0}
    assert _field(report, "diff_ms") == {"same": 0, "different": 1, "not_stored": 0}


def test_split_value_missing_in_file_is_not_stored() -> None:
    stored = _doc(_result("r1", splits=[{"code": "31"}]))
    recalculated = _doc(_result("r1", splits=[{"code": "31", "leg_ms": 300}]))

    report = oracle_compare.compare(stored, recalculated)

    assert _field(report, "splits.leg_ms") == {"same": 0, "different": 0, "not_stored": 1}
