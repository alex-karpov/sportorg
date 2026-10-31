"""Compare two normalized oracle documents result by result: stored in the file vs recalculated.

A difference is reported, never resolved: stage rule 8 classifies it (legacy bug / local practice /
rule gap) for the maintainer. A value that the file does not hold (``null`` on the stored side) is
counted as ``not_stored``, not as a difference.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_list

if TYPE_CHECKING:
    from collections.abc import Mapping

RESULT_FIELDS: Final = (
    "status",
    "place",
    "time_ms",
    "start_ms",
    "finish_ms",
    "penalty_ms",
    "credit_ms",
    "penalty_laps",
    "diff_ms",
    "scores",
    "rogaine_score",
    "rogaine_penalty",
    "scores_ardf",
    "diff_scores",
    "rank",
    "order",
)
SPLIT_FIELDS: Final = (
    "code",
    "time_ms",
    "leg_ms",
    "relative_ms",
    "leg_place",
    "relative_place",
    "is_correct",
    "course_index",
)
SPLIT_COUNT: Final = "splits.count"


def _tally(fields: dict[str, dict[str, int]], name: str, outcome: str) -> None:
    counts = fields.setdefault(name, {"same": 0, "different": 0, "not_stored": 0})
    counts[outcome] += 1


def _outcome(stored: Json | None, recalculated: Json | None) -> str:
    if stored == recalculated:
        return "same"
    return "not_stored" if stored is None else "different"


def _by_id(items: Json | None, id_key: str) -> dict[str, dict[str, Json]]:
    found = (as_dict(item) for item in as_list(items))
    return {item_id: item for item in found if isinstance(item_id := item.get(id_key), str)}


def _diff(rid: str, field: str, stored: Json | None, recalculated: Json | None) -> Json:
    return {"result_id": rid, "field": field, "stored": stored, "recalculated": recalculated}


def _compare_splits(
    rid: str,
    stored: Mapping[str, Json],
    recalculated: Mapping[str, Json],
    fields: dict[str, dict[str, int]],
    differences: list[Json],
) -> None:
    old = [as_dict(s) for s in as_list(stored.get("splits"))]
    new = [as_dict(s) for s in as_list(recalculated.get("splits"))]
    if len(old) != len(new):
        _tally(fields, SPLIT_COUNT, "different")
        differences.append(_diff(rid, SPLIT_COUNT, len(old), len(new)))
        return
    _tally(fields, SPLIT_COUNT, "same")
    for name in SPLIT_FIELDS:
        found = [
            (index, a.get(name), b.get(name))
            for index, (a, b) in enumerate(zip(old, new, strict=True))
            if _outcome(a.get(name), b.get(name)) != "same"
        ]
        outcomes = {_outcome(a, b) for _, a, b in found}
        outcome = "different" if "different" in outcomes else (outcomes.pop() if found else "same")
        _tally(fields, f"splits.{name}", outcome)
        differences.extend(
            _diff(rid, f"splits[{index}].{name}", a, b)
            for index, a, b in found
            if _outcome(a, b) == "different"
        )


def _compare_race(stored: Mapping[str, Json], recalculated: Mapping[str, Json]) -> dict[str, Json]:
    old = _by_id(stored.get("results"), "result_id")
    new = _by_id(recalculated.get("results"), "result_id")
    fields: dict[str, dict[str, int]] = {}
    differences: list[Json] = []
    order = [as_dict(r).get("result_id") for r in as_list(recalculated.get("results"))]
    for rid in (r for r in order if isinstance(r, str) and r in old):
        a, b = old[rid], new[rid]
        for name in RESULT_FIELDS:
            outcome = _outcome(a.get(name), b.get(name))
            _tally(fields, name, outcome)
            if outcome == "different":
                differences.append(_diff(rid, name, a.get(name), b.get(name)))
        _compare_splits(rid, a, b, fields, differences)
    return {
        "race_id": recalculated.get("race_id"),
        "race_index": recalculated.get("race_index"),
        "results": {
            "stored": len(old),
            "recalculated": len(new),
            "only_stored": len(old.keys() - new.keys()),
            "only_recalculated": len(new.keys() - old.keys()),
        },
        "fields": {name: dict[str, Json](counts) for name, counts in sorted(fields.items())},
        "differences": differences,
    }


def compare(stored: Json, recalculated: Json) -> Json:
    """Field-by-field report of ``stored`` against ``recalculated`` (both schema v1), per race."""
    old_races = _by_id(as_dict(stored).get("races"), "race_id")
    races: list[Json] = []
    for race in (as_dict(r) for r in as_list(as_dict(recalculated).get("races"))):
        race_id = race.get("race_id")
        old = old_races.get(race_id, {}) if isinstance(race_id, str) else {}
        races.append(_compare_race(old, race))
    different = sum(len(as_list(as_dict(r).get("differences"))) for r in races)
    return {"different": different, "races": races}


def counts_only(report: Json) -> Json:
    """The report without the list of differences (ids and values): for data with personal data."""
    races: list[Json] = [
        {k: v for k, v in as_dict(race).items() if k != "differences"}
        for race in as_list(as_dict(report).get("races"))
    ]
    return {"different": as_dict(report).get("different"), "races": races}
