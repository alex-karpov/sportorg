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
3. ``stored``: the file's own JSON, read the way legacy opens it
   [код: pysport@b548c35 sportorg/modules/backup/file.py:28-51]
   [код: pysport@b548c35 sportorg/modules/backup/json.py:50-54].
4. ``recalculated``: ``File(path).open()`` (load, which recalculates), then for each race: set it
   current, rebuild indexes, recalculate, as the GUI does for a multi-day event
   [код: pysport@b548c35 sportorg/gui/main_window.py:678-686]; then each race is serialized with
   ``Race.to_dict()`` while it is current (``to_dict`` reads the current race).

Usage (by ``scripts/oracle_cli.py``, with the repository root on ``PYTHONPATH``)::

    python -m scripts.oracle_driver.driver RACE_FILE RAW_OUT [--now HH:MM:SS]
"""

from __future__ import annotations

import argparse
import gzip
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


def read_file(path: str) -> tuple[object, str]:
    """Parsed JSON of a race file and its format (``gzip`` or ``text``)."""
    if is_gzip_file(path):
        return orjson.loads(gzip.decompress(Path(path).read_bytes())), "gzip"
    try:
        text = Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # legacy retries in the locale encoding (file.py:45-51); C.UTF-8 in the hermetic environment
        text = Path(path).read_text(encoding=None)
    return orjson.loads(text), "text"


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


def recalculated_races() -> list[object]:
    """Recalculate every race as the current one, then serialize each while it is current."""
    current = get_current_race_index()
    for index in range(len(races())):
        set_current_race_index(index)
        race().rebuild_indexes()
        recalculate_results(race_object=race())
    snapshots: list[object] = []
    for index in range(len(races())):
        set_current_race_index(index)
        data = snapshot.filter_race(race().to_dict(), index)
        data["relay_teams"] = [team_dict(team) for team in race().relay_teams]
        snapshots.append(data)
    set_current_race_index(current)
    return snapshots


def enums() -> dict[str, object]:
    tables: dict[str, object] = {}
    for enum in (ResultStatus, SystemType, RaceType, Qualification):
        tables[enum.__name__] = {str(member.value): member.name for member in enum}
    return tables


def run(race_file: str, now_ms: int) -> dict[str, object]:
    otime_name = fix_clock(now_ms)
    load_startup_tables()
    data, file_format = read_file(race_file)
    stored = snapshot.stored_races(data)
    File(race_file).open()
    recalculated = recalculated_races()
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("race_file")
    parser.add_argument("raw_out")
    parser.add_argument("--now", type=snapshot.parse_now, default=0, help="clock, HH:MM:SS")
    args = parser.parse_args(argv, namespace=Options())
    return snapshot.guarded(args.raw_out, lambda: run(args.race_file, args.now))


if __name__ == "__main__":
    sys.exit(main())
