"""Pure half of the oracle driver: whitelists, raw snapshot shape, sanitized errors.

Python 3.8 and the standard library only (the driver runs under legacy's interpreter, ADR-0009 T1).
Nothing here imports ``sportorg``, so the project tests import this module directly.

The whitelists keep the keys of legacy ``to_dict`` output that the recalculation produces or reads
[код: pysport@b548c35 sportorg/models/memory.py:363-388,453-470,601-648,1424-1450,1615-1628]
[код: pysport@b548c35 sportorg/models/memory.py:1720-1731].
Names, birth dates, chip numbers, organizations, comments, ``status_comment`` (free text, Д1) and
clock-dependent fields (``created_at``, ``can_win_count``, ``final_result_time``) are not in them:
they never leave the legacy process.
"""

from __future__ import annotations

import json
import re
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from typing_extensions import TypeGuard  # typing.TypeGuard is 3.10+; never imported at run time

PROTOCOL = 2
# The clock of a run: the last second of the day is never the falsy zero OTime and does not wrap
# a time without a finish over midnight [мейнтейнер: 2026-11-01] (ADR-0009 T5).
DEFAULT_NOW = "23:59:59"
# What the oracle reproduces: every race recalculated in its own context, or what the GUI shows
# after File > Open and a switch to each race (ADR-0009 T5, finding F6).
STATES = ("recalculated", "after-open")
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_LEGACY_ERROR = 3

DATA_KEYS = ("race_type", "relay_leg_count")
SETTING_KEYS = ("result_processing_mode", "time_accuracy", "time_rounding")
GROUP_KEYS = ("id", "name")
PERSON_KEYS = ("id", "bib", "group_id", "is_out_of_competition")
RESULT_KEYS = (
    "object",
    "id",
    "person_id",
    "bib",
    "system_type",
    "status",
    "place",
    "start_msec",
    "finish_msec",
    "result_msec",
    "penalty_time",
    "credit_time",
    "penalty_laps",
    "diff",
    "scores",
    "rogaine_score",
    "rogaine_penalty",
    "scores_ardf",
    "diff_scores",
    "assigned_rank",
    "order",
)
SPLIT_KEYS = (
    "code",
    "time",
    "leg_time",
    "relative_time",
    "leg_place",
    "relative_place",
    "is_correct",
    "course_index",
)
_NOW = re.compile(r"(\d{2}):(\d{2}):(\d{2})")
_HOUR, _MINUTE = 24, 60


def is_dict(value: object) -> TypeGuard[dict[str, object]]:
    """JSON objects (and legacy ``to_dict`` output) have ``str`` keys."""
    return isinstance(value, dict)


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _items(value: object) -> list[object]:
    return value if is_list(value) else []


def pick(item: object, keys: Iterable[str]) -> dict[str, object]:
    """The listed keys of a dict that it has; anything else is dropped."""
    if not is_dict(item):
        return {}
    return {key: item[key] for key in keys if key in item}


def _result(item: object) -> dict[str, object]:
    result = pick(item, RESULT_KEYS)
    if is_dict(item) and "splits" in item:
        result["splits"] = [pick(split, SPLIT_KEYS) for split in _items(item["splits"])]
    return result


def filter_race(race: object, index: int) -> dict[str, object]:
    """Whitelisted copy of one legacy race dict (from the file or from ``Race.to_dict()``)."""
    source = race if is_dict(race) else {}
    return {
        "index": index,
        "id": source.get("id"),
        "data": pick(source.get("data"), DATA_KEYS),
        "settings": pick(source.get("settings"), SETTING_KEYS),
        "groups": [pick(g, GROUP_KEYS) for g in _items(source.get("groups"))],
        "persons": [pick(p, PERSON_KEYS) for p in _items(source.get("persons"))],
        "results": [_result(r) for r in _items(source.get("results"))],
    }


def stored_races(data: object) -> list[object]:
    """Race dicts of a parsed file, accepting the shapes legacy accepts.

    [код: pysport@b548c35 sportorg/modules/backup/json.py:55-60]: a dict with ``races``, a single
    race dict, or a list of race dicts.
    """
    if is_dict(data) and "races" in data:
        return _items(data["races"])
    if is_list(data):
        return data
    return [data]


def clock_dependent(races: Iterable[object]) -> int:
    """Results without a stored finish time: legacy gives them the clock as finish.

    [код: pysport@b548c35 sportorg/models/memory.py:499,665-666,878-882]
    """
    return sum(
        1
        for race in races
        for result in _items(race.get("results") if is_dict(race) else None)
        if not is_dict(result) or result.get("finish_time") is None
    )


def parse_now(text: str) -> int:
    """``HH:MM:SS`` → milliseconds since midnight."""
    match = _NOW.fullmatch(text)
    if match is None:
        msg = f"expected HH:MM:SS, got {text!r}"
        raise ValueError(msg)
    hour, minute, sec = (int(g) for g in match.groups())
    if hour >= _HOUR or minute >= _MINUTE or sec >= _MINUTE:
        msg = f"expected HH:MM:SS within a day, got {text!r}"
        raise ValueError(msg)
    return ((hour * 60 + minute) * 60 + sec) * 1000


def short_path(path: str) -> str:
    """``sportorg/…`` part of a legacy path; the file name for anything else."""
    parts = re.split(r"[\\/]", path)
    if "sportorg" in parts[:-1]:
        start = len(parts) - 1 - parts[::-1].index("sportorg")
        return "/".join(parts[start:])
    return parts[-1]


def error_report(exc: BaseException) -> dict[str, object]:
    """Exception type and stack frames, without the message: it may quote the race file."""
    frames: list[object] = [
        [short_path(frame.filename), frame.lineno, frame.name]
        for frame in traceback.extract_tb(exc.__traceback__)
    ]
    return {"type": type(exc).__name__, "frames": frames}


def write_raw(path: str, payload: dict[str, object]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="\n") as file:
        json.dump(payload, file, ensure_ascii=False, sort_keys=True)


def guarded(raw_out: str, work: Callable[[], dict[str, object]]) -> int:
    """Run ``work`` and write its payload, or a sanitized error report, to ``raw_out``."""
    try:
        payload = work()
    except Exception as exc:  # noqa: BLE001 - every legacy failure becomes a report without its message
        write_raw(raw_out, {"protocol": PROTOCOL, "error": error_report(exc)})
        return EXIT_LEGACY_ERROR
    write_raw(raw_out, {"protocol": PROTOCOL, **payload})
    return EXIT_OK
