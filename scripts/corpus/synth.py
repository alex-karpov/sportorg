"""Synthetic race files in the legacy SportOrg JSON format, for the oracle and golden tests.

Three races, each built so that the legacy recalculation has something to decide (S2 of the
Stage 2 plan): an individual race (places, a tie, a missing punch, an extra punch, out of
competition, DNS, time rounding, overtime), a two-leg relay, and a rogaine by score. Three more
files isolate one finding each, for the maintainer to open in legacy's GUI: ``f3_rogaine_tie``,
``f4_slow_leader`` and ``f6_two_races`` (``docs/evidence/stage-2/oracle/findings.agent.md``). The
file format follows legacy ``to_dict``/``update_data``
[код: pysport@b548c35 sportorg/models/memory.py] and ``_race_migrate``
[код: pysport@b548c35 sportorg/modules/backup/json.py:84-104].

No personal data: every person is "Synthetic Runner NNN", chip numbers are 0, birth dates are
absent. Ids are UUID5 of fixed names, so a rerun writes the same bytes.

Usage::

    uv run python -m scripts.corpus.synth --out DIR    # DIR/<race>.json for each race
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import as_dict, as_list

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from scripts._json import Json

NAMESPACE: Final = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/alex-karpov/sportorg/synth")
LEGACY_VERSION: Final = "v1.8.0b2"  # [код: pysport@b548c35 sportorg/config.py:10]
SEC: Final = 1000
MIN: Final = 60 * SEC
HOUR: Final = 60 * MIN
START: Final = 10 * HOUR
# Legacy enum values [код: pysport@b548c35 sportorg/models/memory.py:67-93]
INDIVIDUAL, RELAY = 0, 3
OK, DID_NOT_START = 1, 13


class RaceBuilder:
    """Collects the objects of one race and writes them in legacy's shape."""

    def __init__(self, name: str, race_type: int, settings: dict[str, Json]) -> None:
        self.name: str = name
        self.race_type: int = race_type
        self.settings: dict[str, Json] = settings
        self.relay_leg_count: int = 3
        self.short_title: str = ""
        self.organizations: list[Json] = []
        self.courses: list[Json] = []
        self.groups: list[Json] = []
        self.persons: list[Json] = []
        self.results: list[Json] = []

    def id(self, kind: str, key: str) -> str:
        return str(uuid.uuid5(NAMESPACE, f"{self.name}/{kind}/{key}"))

    def organization(self, name: str) -> str:
        oid = self.id("organization", name)
        self.organizations.append(
            {"object": "Organization", "id": oid, "name": name, "country": "", "region": ""}
        )
        return oid

    def course(self, name: str, codes: Sequence[str], length: int = 0) -> str:
        cid = self.id("course", name)
        controls: list[Json] = [
            {"object": "CourseControl", "code": code, "length": 0} for code in codes
        ]
        self.courses.append(
            {
                "object": "Course",
                "id": cid,
                "name": name,
                "bib": 0,
                "length": length,
                "climb": 0,
                "corridor": 0,
                "controls": controls,
            }
        )
        return cid

    def group(self, name: str, course_id: str | None, max_time: int = 0) -> str:
        gid = self.id("group", name)
        self.groups.append(
            {
                "object": "Group",
                "id": gid,
                "name": name,
                "course_id": course_id,
                "is_any_course": False,
                "long_name": "",
                "price": 0,
                "min_year": 0,
                "max_year": 0,
                "min_age": 0,
                "max_age": 0,
                "max_time": max_time,
                "start_interval": 0,
                "start_corridor": 0,
                "order_in_corridor": 0,
                "first_number": 0,
                "relay_legs": 0,
                "ranking": None,
                "__type": None,
            }
        )
        return gid

    def person(
        self,
        bib: int,
        group_id: str,
        *,
        start: int,
        out_of_competition: bool = False,
        organization_id: str | None = None,
    ) -> str:
        pid = self.id("person", str(bib))
        self.persons.append(
            {
                "object": "Person",
                "id": pid,
                "name": "Synthetic",
                "surname": f"Runner {bib:03}",
                "middle_name": "",
                "card_number": 0,
                "bib": bib,
                "birth_date": None,
                "year": 0,
                "group_id": group_id,
                "organization_id": organization_id,
                "world_code": "",
                "national_code": 0,
                "qual": 0,
                "is_out_of_competition": out_of_competition,
                "is_paid": False,
                "is_rented_card": False,
                "is_personal": False,
                "comment": "",
                "start_time": start or None,
                "start_group": 0,
            }
        )
        return pid

    def result(
        self,
        person_id: str,
        *,
        finish: int | None,
        punches: Sequence[tuple[str, int]] = (),
        status: int = OK,
    ) -> str:
        rid = self.id("result", person_id)
        splits: list[Json] = [{"code": code, "time": time} for code, time in punches]
        self.results.append(
            {
                "object": "ResultSportident",
                "id": rid,
                "person_id": person_id,
                "bib": 0,
                "days": 0,
                "card_number": 0,
                "status": status,
                "status_comment": "",
                "penalty_laps": 0,
                "penalty_time": None,
                "credit_time": None,
                "scores": 0,
                "place": 0,
                "assigned_rank": 0,
                "start_time": None,
                "finish_time": finish,
                "splits": splits,
            }
        )
        return rid

    def document(self) -> Json:
        race: dict[str, Json] = {
            "object": "Race",
            "id": self.id("race", self.name),
            "data": {
                "title": f"Synthetic {self.name}",
                "description": "",
                "short_title": self.short_title,
                "location": "",
                "chief_referee": "",
                "secretary": "",
                "url": "",
                "race_type": self.race_type,
                "start_datetime": None,
                "end_datetime": None,
                "relay_leg_count": self.relay_leg_count,
            },
            "settings": self.settings,
            "organizations": self.organizations,
            "courses": self.courses,
            "groups": self.groups,
            "persons": self.persons,
            "results": self.results,
        }
        return {"version": LEGACY_VERSION, "current_race": 0, "races": [race]}


def _at(start: int, *legs: tuple[str, int]) -> list[tuple[str, int]]:
    """Punches given as (code, minutes after start)."""
    return [(code, start + minutes * MIN) for code, minutes in legs]


def individual() -> Json:
    """Individual race, time mode.

    M21 course 31-32-33: 30:00 (1st), 32:00 and 32:00 (tie), a missing 32, out of competition
    faster than all, DNS without finish (the clock), an extra punch 99. W21 course 41-42: 31:00.4
    and 31:00.6 with whole seconds and math rounding. M60 with a 30:00 limit: 31:00 and 28:00.
    """
    race = RaceBuilder("individual", INDIVIDUAL, {"time_accuracy": 0, "time_rounding": "math"})
    a = race.course("A", ["31", "32", "33"], length=3000)
    b = race.course("B", ["41", "42"], length=2000)
    m21 = race.group("M21", a)
    w21 = race.group("W21", b)
    m60 = race.group("M60", b, max_time=30 * MIN)
    full = (("31", 5), ("32", 15), ("33", 25))
    for bib, offset, finish in ((101, 0, 30), (102, 1, 32), (103, 2, 32)):
        start = START + offset * MIN
        pid = race.person(bib, m21, start=start)
        race.result(pid, finish=start + finish * MIN, punches=_at(start, *full))
    start = START + 3 * MIN
    pid = race.person(104, m21, start=start)
    race.result(pid, finish=start + 31 * MIN, punches=_at(start, ("31", 5), ("33", 25)))
    start = START + 4 * MIN
    pid = race.person(105, m21, start=start, out_of_competition=True)
    race.result(pid, finish=start + 29 * MIN, punches=_at(start, *full))
    start = START + 5 * MIN
    pid = race.person(106, m21, start=start)
    race.result(pid, finish=None, status=DID_NOT_START)
    start = START + 6 * MIN
    pid = race.person(107, m21, start=start)
    extra = (("31", 5), ("99", 10), ("32", 15), ("33", 25))
    race.result(pid, finish=start + 35 * MIN, punches=_at(start, *extra))
    for bib, extra_ms in ((201, 400), (202, 600)):
        pid = race.person(bib, w21, start=START)
        punches = _at(START, ("41", 10), ("42", 20))
        race.result(pid, finish=START + 31 * MIN + extra_ms, punches=punches)
    for bib, offset, finish in ((301, 10, 31), (302, 11, 28)):
        start = START + offset * MIN
        pid = race.person(bib, m60, start=start)
        race.result(pid, finish=start + finish * MIN, punches=_at(start, ("41", 10), ("42", 20)))
    return race.document()


def relay() -> Json:
    """Two-leg relay, bibs 1000 * leg + team.

    [код: pysport@b548c35 sportorg/models/memory.py:2571-2575]. Team 2 is fastest, team 1 second,
    team 3 mispunches on leg 2. Only the first leg has a start time; legacy sets the next leg's
    start from the previous finish
    [код: pysport@b548c35 sportorg/models/memory.py:2645-2652].
    """
    race = RaceBuilder("relay", RELAY, {"time_accuracy": 0, "time_rounding": "math"})
    race.relay_leg_count = 2
    course = race.course("R", ["31", "32"])
    group = race.group("Relay", course)
    for team, (leg1, leg2, leg2_codes) in {
        1: (20, 45, ("31", "32")),
        2: (22, 44, ("31", "32")),
        3: (18, 40, ("31",)),
    }.items():
        club = race.organization(f"Synthetic Club {team}")
        first = race.person(1000 + team, group, start=START, organization_id=club)
        race.result(first, finish=START + leg1 * MIN, punches=_at(START, ("31", 5), ("32", 10)))
        second = race.person(2000 + team, group, start=0, organization_id=club)
        punches = [(code, START + (leg1 + 5 * (i + 1)) * MIN) for i, code in enumerate(leg2_codes)]
        race.result(second, finish=START + leg2 * MIN, punches=punches)
    return race.document()


def _rogaine_race(name: str, plans: Mapping[int, tuple[tuple[str, ...], int]]) -> RaceBuilder:
    """Rogaine by score, 60:00 limit, one point per minute over it, score = code // 10.

    [код: pysport@b548c35 sportorg/models/result/result_checker.py:36-47,458-527]. ``plans``:
    bib → (codes punched, one every 5 minutes; finish after the start).
    """
    settings: dict[str, Json] = {
        "result_processing_mode": "scores",
        "result_processing_score_mode": "rogain",
        "result_processing_scores_minute_penalty": 1,
        "time_accuracy": 0,
        "time_rounding": "math",
    }
    race = RaceBuilder(name, INDIVIDUAL, settings)
    group = race.group("Open", None, max_time=60 * MIN)
    for bib, (codes, finish) in plans.items():
        pid = race.person(bib, group, start=START)
        punches = [(code, START + (i + 1) * 5 * MIN) for i, code in enumerate(codes)]
        race.result(pid, finish=START + finish, punches=punches)
    return race


def rogaine() -> Json:
    """Rogaine with ties, penalty points and a duplicate punch.

    A 12 points in 55:00; B 7 in 50:00; C 18 in 62:30 (3 penalty points); D 31-31-41 (the
    duplicate counts once) in 50:00, as B; E 5 points in 50:00, as B and D.
    """
    return _rogaine_race(
        "rogaine",
        {
            1: (("31", "41", "52"), 55 * MIN),
            2: (("31", "41"), 50 * MIN),
            3: (("31", "41", "52", "61"), 62 * MIN + 30 * SEC),
            4: (("31", "31", "41"), 50 * MIN),
            5: (("52",), 50 * MIN),
        },
    ).document()


# Points 10, 7, 5: codes 41+61, 31+41, 52 (score = code // 10).
TEN, SEVEN, FIVE = ("41", "61"), ("31", "41"), ("52",)


def f3_rogaine_tie() -> Json:
    """Finding F3: 10 points in 40:00, 7 in 45:00, 5 in 45:00.

    Legacy gives 5 points the same place as 7, because a shared place compares the time only
    [код: pysport@b548c35 sportorg/models/result/result_calculation.py:156,169-174]. The leader
    is the fastest, so the time behind stays positive (no F4 here).
    """
    plans = {1: (TEN, 40 * MIN), 2: (SEVEN, 45 * MIN), 3: (FIVE, 45 * MIN)}
    return _rogaine_race("f3_rogaine_tie", plans).document()


def f4_slow_leader() -> Json:
    """Finding F4: 10 points in 55:00, 7 in 50:00, 5 in 58:00; no shared time (no F3 here).

    The 7-point runner is 5:00 faster than the leader: legacy's time behind is -5:00 plus a day
    [код: pysport@b548c35 sportorg/common/otime.py:150-155,
    sportorg/models/result/result_calculation.py:157].
    """
    plans = {1: (TEN, 55 * MIN), 2: (SEVEN, 50 * MIN), 3: (FIVE, 58 * MIN)}
    return _rogaine_race("f4_slow_leader", plans).document()


def f6_two_races() -> Json:
    """Finding F6: one file, two races, not a multi-day event; the first race is current.

    Race 1 is ``individual``; race 2 a rogaine where the order by points (10 in 50:00, 7 in
    45:00, 5 in 40:00) is the reverse of the order by time. On open, legacy recalculates race 2
    while race 1 is current, so race 2 is not checked (no points)
    [код: pysport@b548c35 sportorg/modules/backup/json.py:42-44,
    sportorg/models/result/result_tools.py:106, sportorg/models/result/result_checker.py:98-99];
    a switch to race 2 does not recalculate it outside a multi-day event
    [код: pysport@b548c35 sportorg/gui/dialogs/settings.py:317-329,
    sportorg/gui/main_window.py:678-687].
    """
    first = as_dict(as_list(as_dict(individual())["races"])[0])
    as_dict(first["data"])["short_title"] = "Race 1 individual"
    second = _rogaine_race(
        "f6_rogaine", {1: (TEN, 50 * MIN), 2: (SEVEN, 45 * MIN), 3: (FIVE, 40 * MIN)}
    )
    second.short_title = "Race 2 rogaine"
    races: list[Json] = [first, as_list(as_dict(second.document())["races"])[0]]
    return {"version": LEGACY_VERSION, "current_race": 0, "races": races}


RACES: Final[dict[str, Callable[[], Json]]] = {
    "individual": individual,
    "relay": relay,
    "rogaine": rogaine,
    "f3_rogaine_tie": f3_rogaine_tie,
    "f4_slow_leader": f4_slow_leader,
    "f6_two_races": f6_two_races,
}


def dumps(doc: Json) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


class Options(argparse.Namespace):
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    args.out.mkdir(parents=True, exist_ok=True)
    for name, build in RACES.items():
        (args.out / f"{name}.json").write_text(dumps(build()), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
