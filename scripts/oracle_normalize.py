"""Normalize raw legacy snapshots from the oracle driver into the oracle schema (version 2).

The driver (``scripts/oracle_driver/driver.py``) runs under the legacy interpreter and emits a
whitelisted subset of legacy ``to_dict`` output per race, with legacy's own enum tables. This
module turns one snapshot (``stored`` or ``recalculated``) into the normalized document: stable
identifiers, enum names, integer milliseconds, canonical order. It only copies the keys it knows,
so a name, birth date or chip number in the raw input never reaches the output.

The ``stored`` side leaves out every field whose raw key the file does not have, so ``null`` there
means the file holds ``null`` (legacy writes a zero time behind, penalty or credit so
[код: pysport@b548c35 sportorg/models/memory.py:612,614,615]); the recalculated side has every
field. Version 2 added that distinction; the schema is described in
``docs/evidence/stage-2/oracle/README.md``.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_list

if TYPE_CHECKING:
    from collections.abc import Mapping

SCHEMA: Final = "sportorg-ng/oracle-results"
SCHEMA_VERSION: Final = 2
UNPLACED: Final = sys.maxsize

# normalized key → raw key of legacy ``Result.to_dict``
# [код: pysport@b548c35 sportorg/models/memory.py:601-648]
RESULT_NUMBERS: Final = (
    ("place", "place"),
    ("time_ms", "result_msec"),
    ("start_ms", "start_msec"),
    ("finish_ms", "finish_msec"),
    ("penalty_ms", "penalty_time"),
    ("credit_ms", "credit_time"),
    ("penalty_laps", "penalty_laps"),
    ("diff_ms", "diff"),
    ("scores", "scores"),
    ("rogaine_score", "rogaine_score"),
    ("rogaine_penalty", "rogaine_penalty"),
    ("scores_ardf", "scores_ardf"),
    ("diff_scores", "diff_scores"),
    ("order", "order"),
)
# normalized key → raw key of legacy ``Split.to_dict``
# [код: pysport@b548c35 sportorg/models/memory.py:453-470]
SPLIT_NUMBERS: Final = (
    ("time_ms", "time"),
    ("leg_ms", "leg_time"),
    ("relative_ms", "relative_time"),
    ("leg_place", "leg_place"),
    ("relative_place", "relative_place"),
    ("course_index", "course_index"),
)
# normalized key → legacy enum table → raw key
ENUM_FIELDS: Final = (
    ("system", "SystemType", "system_type"),
    ("status", "ResultStatus", "status"),
    ("rank", "Qualification", "assigned_rank"),
)
TEAM_NUMBERS: Final = (
    ("place", "place"),
    ("order", "order"),
    ("time_ms", "time_ms"),
    ("correct_legs", "correct_legs"),
)


def _number(value: Json | None) -> int | float | None:
    """An int or float as it is; anything else (bool, string, null) is ``None``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _integer(value: Json | None) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _text(value: Json | None) -> str | None:
    return value if isinstance(value, str) else None


def _flag(value: Json | None) -> bool | None:
    return value if isinstance(value, bool) else None


def _enum(enums: Mapping[str, Json], table: str, value: Json | None) -> str | None:
    """Legacy enum name of ``value``; an unknown value stays visible as ``<value>``."""
    code = _integer(value)
    if code is None:
        return None
    name = as_dict(enums.get(table)).get(str(code))
    return name if isinstance(name, str) else f"<{code}>"


def _place_key(place: Json | None) -> int:
    number = _integer(place)
    return number if number is not None and number > 0 else UNPLACED


def _present(raw: Mapping[str, Json], src: str, *, stored: bool) -> bool:
    return not stored or src in raw


def _split(raw: Mapping[str, Json], *, stored: bool) -> dict[str, Json]:
    split: dict[str, Json] = {}
    if _present(raw, "code", stored=stored):
        split["code"] = _text(raw.get("code"))
    split |= {
        key: _number(raw.get(src))
        for key, src in SPLIT_NUMBERS
        if _present(raw, src, stored=stored)
    }
    if _present(raw, "is_correct", stored=stored):
        split["is_correct"] = _flag(raw.get("is_correct"))
    return split


def _result(
    raw: Mapping[str, Json],
    persons: Mapping[str, Mapping[str, Json]],
    groups: Mapping[str, str],
    enums: Mapping[str, Json],
    *,
    stored: bool,
) -> dict[str, Json]:
    person_id = _text(raw.get("person_id"))
    person = persons.get(person_id) if person_id is not None else None
    if person is None:
        group = None
        bib = _integer(raw.get("bib"))
    else:
        group = groups.get(_text(person.get("group_id")) or "")
        bib = _integer(person.get("bib"))
    result: dict[str, Json] = {
        "result_id": _text(raw.get("id")),
        "person_id": person_id,
        "group": group,
        "bib": bib,
    }
    for key, table, src in ENUM_FIELDS:
        if _present(raw, src, stored=stored):
            result[key] = _enum(enums, table, raw.get(src))
    result |= {
        key: _number(raw.get(src))
        for key, src in RESULT_NUMBERS
        if _present(raw, src, stored=stored)
    }
    splits = as_list(raw.get("splits"))
    result["splits"] = [_split(as_dict(s), stored=stored) for s in splits]
    return result


def _result_key(result: Mapping[str, Json]) -> tuple[bool, str, int, str, str]:
    group = _text(result.get("group"))
    return (
        group is None,
        group or "",
        _place_key(result.get("place")),
        _text(result.get("person_id")) or "",
        _text(result.get("result_id")) or "",
    )


def _team(raw: Mapping[str, Json], groups: Mapping[str, str]) -> dict[str, Json]:
    team: dict[str, Json] = {
        "group": groups.get(_text(raw.get("group_id")) or ""),
        "bib": _integer(raw.get("bib_number")),
        "status_ok": _flag(raw.get("status_ok")),
    }
    team |= {key: _number(raw.get(src)) for key, src in TEAM_NUMBERS}
    legs = [as_dict(leg) for leg in as_list(raw.get("legs"))]
    legs.sort(key=lambda leg: (_integer(leg.get("leg")) or 0, _text(leg.get("result_id")) or ""))
    team["legs"] = [
        {"leg": _integer(leg.get("leg")), "result_id": _text(leg.get("result_id"))} for leg in legs
    ]
    return team


def _team_key(team: Mapping[str, Json]) -> tuple[bool, str, int, int]:
    group = _text(team.get("group"))
    return (
        group is None,
        group or "",
        _place_key(team.get("place")),
        _integer(team.get("bib")) or 0,
    )


def _race(raw: Mapping[str, Json], enums: Mapping[str, Json], *, stored: bool) -> dict[str, Json]:
    groups = {
        gid: _text(g.get("name")) or ""
        for g in map(as_dict, as_list(raw.get("groups")))
        if (gid := _text(g.get("id"))) is not None
    }
    persons = {
        pid: p
        for p in map(as_dict, as_list(raw.get("persons")))
        if (pid := _text(p.get("id"))) is not None
    }
    settings = as_dict(raw.get("settings"))
    results = [
        _result(as_dict(r), persons, groups, enums, stored=stored)
        for r in as_list(raw.get("results"))
    ]
    results.sort(key=_result_key)
    teams = [_team(as_dict(t), groups) for t in as_list(raw.get("relay_teams"))]
    teams.sort(key=_team_key)
    return {
        "race_id": _text(raw.get("id")),
        "race_index": _integer(raw.get("index")),
        "race_type": _enum(enums, "RaceType", as_dict(raw.get("data")).get("race_type")),
        "processing_mode": _text(settings.get("result_processing_mode")),
        "time_accuracy": _integer(settings.get("time_accuracy")),
        "time_rounding": _text(settings.get("time_rounding")),
        "results": list[Json](results),
        "relay_teams": list[Json](teams),
    }


def normalize(snapshot: Json, enums: Mapping[str, Json], *, stored: bool = False) -> Json:
    """Normalized document of one raw snapshot ``{"races": [...]}``.

    ``stored``: the snapshot is the file's own JSON; fields it does not hold are left out.
    """
    races = [
        _race(as_dict(r), enums, stored=stored) for r in as_list(as_dict(snapshot).get("races"))
    ]
    return {"schema": SCHEMA, "schema_version": SCHEMA_VERSION, "races": list[Json](races)}


def dumps(doc: Json) -> str:
    """Canonical text: sorted keys, one-space indent, UTF-8 as is, final newline."""
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
