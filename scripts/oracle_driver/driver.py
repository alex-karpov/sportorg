"""Oracle driver: open a race file in legacy SportOrg, recalculate it, write a raw snapshot.

Runs under the legacy interpreter (``.legacy-run/pysport/.venv``, Python 3.8 first line, ADR-0009
T1), started by ``scripts/oracle_cli.py`` in a hermetic environment with
``QT_QPA_PLATFORM=offscreen`` and no display. Standard library and legacy only; it never writes
into the legacy copy.

Steps, each as the legacy program does it:

1. The clock is an input: ``OTime.now()`` returns ``--now`` (a result without a stored finish
   takes the clock [код: pysport@b548c35 sportorg/models/memory.py:499,878-882]).
2. Startup tables that change the recalculation: status comments and ranking tables from the
   shipped configs [код: pysport@b548c35 sportorg/gui/main.py:47-56,62-75,124-137].
   ``settings.json`` is not read: the defaults apply.
3. ``stored``: the file's own JSON, read the way legacy opens it: gzip, else UTF-8, else the
   locale's encoding, which on Russian Windows is cp1251
   [код: pysport@b548c35 sportorg/modules/backup/file.py:28-51]
   [код: pysport@b548c35 sportorg/modules/backup/json.py:50-54]. The oracle runs in C.UTF-8, so
   it tries cp1251 itself (Q3 (b) [мейнтейнер: 2026-11-01]) and hands legacy's ``json.load`` the
   decoded text, as ``File.open`` would there
   [код: pysport@b548c35 sportorg/modules/backup/file.py:77-83].
4. ``recalculated`` (``--state recalculated``): ``File.open`` (load, which recalculates), then for
   each race: set it current, rebuild indexes, recalculate, as the GUI does for a multi-day event
   [код: pysport@b548c35 sportorg/gui/main_window.py:678-686]; then each race is serialized with
   ``Race.to_dict()`` while it is current (``to_dict`` reads the current race).
   ``--state after-open``: ``File.open`` and what the GUI does next, ``init_model``: a multi-day
   event recalculates every race, any other file only rebuilds indexes; a switch to a race runs
   ``init_model`` again [код: pysport@b548c35 sportorg/gui/main_window.py:951-961,659-687,
   sportorg/gui/dialogs/settings.py:317-329]. Each race is serialized while it is current.

Usage (by ``scripts/oracle_cli.py``, with the repository root on ``PYTHONPATH``)::

    python -m scripts.oracle_driver.driver RACE_FILE RAW_OUT [--now HH:MM:SS] [--state STATE]
"""

from __future__ import annotations

import argparse
import gzip
import io
import platform
import sys
from pathlib import Path

import orjson
from sportorg import config, settings
from sportorg.common import otime
from sportorg.models.constant import RankingTable, StatusComments
from sportorg.models.memory import (
    Qualification,
    RaceType,
    RelayTeam,
    ResultStatus,
    SystemType,
    get_current_race_index,
    race,
    races,
    set_current_race_index,
)
from sportorg.models.result.result_tools import recalculate_results
from sportorg.modules.backup import json as legacy_json
from sportorg.modules.backup.file import File, is_gzip_file

from scripts.oracle_driver import snapshot


def fix_clock(now_ms: int) -> str:
    """Make ``OTime.now()`` return ``now_ms``; the name of the OTime implementation in use."""
    if otime.OTime is not otime.PythonOTime:
        msg = "the Rust OTime is in use: its clock cannot be fixed"
        raise RuntimeError(msg)

    def fixed_now(cls: type[otime.PythonOTime]) -> otime.PythonOTime:
        return cls(msec=now_ms)

    # A classmethod replaces a classmethod; the type checker refuses the plain assignment.
    setattr(otime.PythonOTime, "now", classmethod(fixed_now))  # noqa: B010 - see the line above
    return otime.PythonOTime.__name__


def _lines(path: str) -> list[str]:
    with Path(path).open(encoding="utf-8") as file:
        return file.readlines()


def load_startup_tables() -> None:
    """The non-GUI part of the startup that the recalculation reads."""
    StatusComments().set([line.strip() for line in _lines(settings.status_comments_path())])
    StatusComments().set_default_statuses(_lines(settings.status_default_comments_path()))
    RankingTable().set_table(
        [line.strip().split(";") for line in _lines(settings.ranking_score_path())]
    )
    RankingTable().set_table(
        [line.strip().split(";") for line in _lines(settings.ranking_ardf_score_path())], "ardf"
    )


class UndecodableRaceFile(Exception):  # noqa: N818 - the name is the message: reports drop messages
    """The race file is not gzip, UTF-8 or cp1251 text; legacy on Russian Windows fails too."""


def read_file(path: str) -> tuple[object, str, str | None]:
    """Parsed JSON of a race file, its format (``gzip``, ``utf-8``, ``cp1251``), its cp1251 text."""
    if is_gzip_file(path):
        return orjson.loads(gzip.decompress(Path(path).read_bytes())), "gzip", None
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        return orjson.loads(text), "utf-8", None
    try:
        text = raw.decode("cp1251")
    except UnicodeDecodeError:
        raise UndecodableRaceFile from None
    return orjson.loads(text), "cp1251", text


def open_race_file(path: str, cp1251_text: str | None) -> None:
    """``File.open``; a cp1251 file goes to the same ``json.load`` as decoded text."""
    if cp1251_text is None:
        File(path).open()
    else:
        legacy_json.load(io.StringIO(cp1251_text))


def team_dict(team: RelayTeam) -> dict[str, object]:
    legs: list[object] = [
        {"leg": leg.leg, "result_id": str(leg.result.id) if leg.result else None}
        for leg in team.legs
    ]
    return {
        "group_id": str(team.group.id) if team.group else None,
        "bib_number": team.bib_number,
        "place": team.place,
        "order": team.order,
        "time_ms": team.get_time().to_msec(),
        "correct_legs": team.get_correct_lap_count(),
        "status_ok": team.get_is_status_ok(),
        "legs": legs,
    }


def _recalculate_every_race() -> None:
    current = get_current_race_index()
    for index in range(len(races())):
        set_current_race_index(index)
        race().rebuild_indexes()
        recalculate_results(race_object=race())
    set_current_race_index(current)


def _serialize_every_race(*, rebuild: bool) -> list[object]:
    """Each race while it is current; ``rebuild``: as a GUI switch to it does first."""
    current = get_current_race_index()
    snapshots: list[object] = []
    for index in range(len(races())):
        set_current_race_index(index)
        if rebuild:
            race().rebuild_indexes(rebuild_person=True, rebuild_course=True)
        data = snapshot.filter_race(race().to_dict(), index)
        data["relay_teams"] = [team_dict(team) for team in race().relay_teams]
        snapshots.append(data)
    set_current_race_index(current)
    return snapshots


def recalculated_races() -> list[object]:
    """Recalculate every race as the current one, then serialize each while it is current."""
    _recalculate_every_race()
    return _serialize_every_race(rebuild=False)


def after_open_races() -> list[object]:
    """What the GUI shows for each race after File > Open and a switch to it (``init_model``)."""
    if race().data.race_type == RaceType.MULTI_DAY_RACE:
        _recalculate_every_race()
    return _serialize_every_race(rebuild=True)


def enums() -> dict[str, object]:
    tables: dict[str, object] = {}
    for enum in (ResultStatus, SystemType, RaceType, Qualification):
        tables[enum.__name__] = {str(member.value): member.name for member in enum}
    return tables


def run(race_file: str, now_ms: int, state: str = "recalculated") -> dict[str, object]:
    otime_name = fix_clock(now_ms)
    load_startup_tables()
    data, file_format, cp1251_text = read_file(race_file)
    stored = snapshot.stored_races(data)
    open_race_file(race_file, cp1251_text)
    recalculated = after_open_races() if state == "after-open" else recalculated_races()
    meta: dict[str, object] = {
        "python": platform.python_version(),
        "otime": otime_name,
        "now_ms": now_ms,
        "legacy_version": config.VERSION,
        "file_version": data.get("version") if snapshot.is_dict(data) else None,
        "file_format": file_format,
        "current_race": get_current_race_index(),
        "clock_dependent_results": snapshot.clock_dependent(stored),
    }
    return {
        "meta": meta,
        "enums": enums(),
        "stored": {"races": [snapshot.filter_race(r, i) for i, r in enumerate(stored)]},
        "recalculated": {"races": recalculated},
    }


class Options(argparse.Namespace):
    race_file: str = ""
    raw_out: str = ""
    now: int = 0
    state: str = snapshot.STATES[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("race_file")
    parser.add_argument("raw_out")
    parser.add_argument(
        "--now",
        type=snapshot.parse_now,
        default=snapshot.parse_now(snapshot.DEFAULT_NOW),
        help="clock, HH:MM:SS",
    )
    parser.add_argument("--state", choices=snapshot.STATES, default=snapshot.STATES[0])
    args = parser.parse_args(argv, namespace=Options())
    return snapshot.guarded(args.raw_out, lambda: run(args.race_file, args.now, args.state))


if __name__ == "__main__":
    sys.exit(main())
