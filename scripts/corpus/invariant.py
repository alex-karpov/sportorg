"""The main test of the anonymization: the oracle gives the same output before and after it.

Plan S3: oracle(anonymized) == oracle(original) on statuses, times and places. The oracle's
normalized output holds ids, statuses, times, places, splits and points, but no names or cards
(``scripts/oracle_driver/snapshot.py`` whitelists), so the check compares whole files:
``results.json``, ``stored.json`` and ``comparison.json`` must be byte-identical. ``run.json``
differs by the input hash. A difference is reported as counts per JSON path, never as values.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import Json
from scripts.oracle_cli import OracleError, RunSettings, oracle
from scripts.oracle_normalize import dumps

if TYPE_CHECKING:
    from scripts.oracle_cli import OracleRun

COMPARED: Final = ("results.json", "stored.json", "comparison.json")
_ERROR_KIND = re.compile(r"raised (\w+)")


def _walk(before: Json, after: Json, path: str, out: dict[str, int]) -> None:
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            child = f"{path}.{key}" if path else key
            if key not in before or key not in after:
                out[child] = out.get(child, 0) + 1
            else:
                _walk(before[key], after[key], child, out)
        return
    if isinstance(before, list) and isinstance(after, list):
        if len(before) != len(after):
            out[f"{path}.length"] = out.get(f"{path}.length", 0) + 1
        for a, b in zip(before, after, strict=False):
            _walk(a, b, f"{path}[]", out)
        return
    if before != after or type(before) is not type(after):
        out[path] = out.get(path, 0) + 1


def diff_counts(before: Json, after: Json) -> dict[str, int]:
    """How many values differ at each JSON path (list indexes folded to ``[]``)."""
    out: dict[str, int] = {}
    _walk(before, after, "", out)
    return dict(sorted(out.items()))


def _docs(run: OracleRun) -> dict[str, Json]:
    return dict(zip(COMPARED, (run.results, run.stored, run.comparison), strict=True))


def compare_runs(original: OracleRun, anonymized: OracleRun) -> dict[str, Json]:
    before, after = _docs(original), _docs(anonymized)
    files: dict[str, Json] = {name: dumps(before[name]) == dumps(after[name]) for name in COMPARED}
    differences: dict[str, Json] = {
        name: dict[str, Json](diff_counts(before[name], after[name]))
        for name in COMPARED
        if not files[name]
    }
    return {"identical": all(files.values()), "files": files, "differences": differences}


def _run(path: Path, python_exe: Path, settings: RunSettings) -> OracleRun | str:
    """The oracle's run, or ``<kind> at <last legacy frame>``.

    The oracle's error holds the exception type and stack frames, never the message
    (``scripts/oracle_cli.py: _format_error``): code locations of legacy, no data of the file.
    """
    try:
        return oracle(path, python_exe=python_exe, settings=settings)
    except OracleError as exc:
        text = str(exc)
        kind = _ERROR_KIND.search(text)
        frames = [line.strip() for line in text.splitlines()[1:] if line.strip()]
        legacy = [f for f in frames if f.startswith("sportorg/")]
        where = f" at {legacy[-1]}" if legacy else ""
        return f"{kind[1] if kind else 'OracleError'}{where}"


def check(
    original: Path, anonymized: Path, *, python_exe: Path, settings: RunSettings | None = None
) -> dict[str, Json]:
    """Run the oracle on both files and compare the three data files of its output.

    Both files are copied into a temporary directory first: legacy opens a gzip race file for
    reading and writing [код: pysport@b548c35 sportorg/modules/backup/file.py:33-41], so it cannot
    open a read-only original, and the copy keeps the original out of a handle that could write.
    If legacy fails, ``identical`` is ``None`` and ``errors`` names the kind on each side.
    """
    settings = settings or RunSettings()
    with tempfile.TemporaryDirectory(prefix="invariant-") as tmp:
        runs: dict[str, OracleRun | str] = {}
        for side, path in (("original", original), ("anonymized", anonymized)):
            target = Path(tmp) / side
            shutil.copyfile(path, target)
            runs[side] = _run(target, python_exe, settings)
    first, second = runs["original"], runs["anonymized"]
    if isinstance(first, str) or isinstance(second, str):
        errors: dict[str, Json] = {
            side: run if isinstance(run, str) else None for side, run in runs.items()
        }
        return {"identical": None, "errors": errors, "same_error": first == second}
    return compare_runs(first, second)
