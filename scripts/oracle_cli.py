"""Headless oracle: recalculate a race file in pinned legacy SportOrg, export normalized results.

TASK-8 AC #1. Legacy runs as a separate process in its own environment (Stage 2 rule 1):
``python -m scripts.oracle_driver.driver`` under ``.legacy-run/pysport/.venv`` (CPython 3.8.20,
ADR-0009 T1), with the hermetic environment of ``scripts.legacy_env``, ``QT_QPA_PLATFORM=offscreen``
and no display. The project never imports ``sportorg``: it normalizes the driver's raw snapshot
(``scripts/oracle_normalize.py``) and compares it with the values stored in the file
(``scripts/oracle_compare.py``).

Usage::

    uv run python scripts/oracle.py RACE_FILE              # normalized results on stdout
    uv run python scripts/oracle.py RACE_FILE --out DIR    # results, stored, comparison, run
    uv run python scripts/oracle.py RACE_FILE --venv .legacy-run/pysport/.venv-3.13   # second lane
    uv run python scripts/oracle.py RACE_FILE --now 12:00:00   # the clock legacy reads

Exit 0 ok; 1 the oracle failed (no legacy runtime, legacy error, crash); 2 usage error. A legacy
error is shown as its type and stack frames, never with its message, and the driver's stderr is
hidden unless ``--show-stderr``: both may quote the race file, which may hold personal data.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_list, as_str, parse_json
from scripts.legacy import ROOT, find_pin
from scripts.legacy_env import clone_path, env_python, hermetic_env, templates_ru
from scripts.oracle_compare import compare
from scripts.oracle_driver.snapshot import PROTOCOL, parse_now
from scripts.oracle_normalize import SCHEMA_VERSION, dumps, normalize

if TYPE_CHECKING:
    from collections.abc import Sequence

DRIVER_MODULE = "scripts.oracle_driver.driver"
DRIVER_TIMEOUT: Final = 600
OUTPUT_FILES: Final = ("results.json", "stored.json", "comparison.json", "run.json")
DEFAULT_NOW: Final = "00:00:00"


class OracleError(RuntimeError):
    """The driver did not produce a snapshot; the message holds no data from the race file."""


@dataclass(frozen=True, slots=True)
class OracleRun:
    results: Json
    stored: Json
    comparison: Json
    run: Json


def default_venv() -> Path:
    return clone_path() / ".venv"


def _format_error(error: Json) -> str:
    report = as_dict(error)
    frames = [
        ":".join(str(part) for part in as_list(frame)) for frame in as_list(report.get("frames"))
    ]
    where = "\n  ".join(frames[-8:])
    kind = as_str(report.get("type"), "?")
    return f"the driver or legacy raised {kind} (message hidden), at:\n  {where}"


def driver_command(
    python_exe: Path, race_file: Path, raw: Path, *, now: str, module: str
) -> list[str]:
    """Driver command line with absolute paths: the driver runs in a temporary directory.

    Links are kept: a virtual environment's interpreter is a link that must not be resolved.
    """
    return [
        str(python_exe.absolute()),
        "-m",
        module,
        str(race_file.absolute()),
        str(raw),
        "--now",
        now,
    ]


def run_driver(
    race_file: Path,
    *,
    python_exe: Path,
    now: str = DEFAULT_NOW,
    module: str = DRIVER_MODULE,
    show_stderr: bool = False,
) -> dict[str, Json]:
    """Run the driver on ``race_file`` and return its raw payload."""
    with tempfile.TemporaryDirectory(prefix="oracle-") as tmp:
        home = Path(tmp) / "home"
        (home / ".runtime").mkdir(parents=True, mode=0o700)
        env = hermetic_env(os.environ, home=home, qt_platform="offscreen", templates=templates_ru())
        env["PYTHONPATH"] = str(ROOT)
        raw = Path(tmp) / "raw.json"
        cmd = driver_command(python_exe, race_file, raw, now=now, module=module)
        done = subprocess.run(
            cmd,
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DRIVER_TIMEOUT,
            check=False,
        )
        data = as_dict(parse_json(raw.read_text(encoding="utf-8"))) if raw.exists() else {}
    if show_stderr and done.stderr:
        sys.stderr.write(done.stderr)
    if "error" in data:
        raise OracleError(_format_error(data["error"]))
    if done.returncode != 0 or not data:
        msg = (
            f"driver exit {done.returncode} without a snapshot; its stderr is hidden because it may"
            " quote the race file: rerun with --show-stderr on data without personal data"
        )
        raise OracleError(msg)
    if data.get("protocol") != PROTOCOL:
        msg = f"driver protocol {data.get('protocol')!r}, expected {PROTOCOL}"
        raise OracleError(msg)
    return data


def oracle(
    race_file: Path,
    *,
    python_exe: Path,
    now: str = DEFAULT_NOW,
    module: str = DRIVER_MODULE,
    show_stderr: bool = False,
) -> OracleRun:
    """Recalculate ``race_file`` in legacy and normalize what the driver returned."""
    raw = run_driver(
        race_file, python_exe=python_exe, now=now, module=module, show_stderr=show_stderr
    )
    enums = as_dict(raw.get("enums"))
    results = normalize(raw.get("recalculated"), enums)
    stored = normalize(raw.get("stored"), enums)
    run: dict[str, Json] = {
        "schema_version": SCHEMA_VERSION,
        "driver_protocol": PROTOCOL,
        "legacy_pin": find_pin("pysport").commit,
        "input_sha256": hashlib.sha256(race_file.read_bytes()).hexdigest(),
    }
    run |= as_dict(raw.get("meta"))
    return OracleRun(results, stored, compare(stored, results), run)


def write_run(run: OracleRun, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    docs = dict(zip(OUTPUT_FILES, (run.results, run.stored, run.comparison, run.run), strict=True))
    for name, doc in docs.items():
        (out / name).write_text(dumps(doc), encoding="utf-8", newline="\n")


def _now(text: str) -> str:
    try:
        parse_now(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return text


class Options(argparse.Namespace):
    race_file: Path = Path()
    out: Path | None = None
    venv: Path | None = None
    now: str = DEFAULT_NOW
    show_stderr: bool = False


def parse_args(argv: Sequence[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        prog="scripts/oracle.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("race_file", type=Path, metavar="RACE_FILE")
    parser.add_argument("--out", type=Path, help="write results/stored/comparison/run .json here")
    parser.add_argument("--venv", type=Path, help="legacy environment (default: .venv of the copy)")
    parser.add_argument("--now", type=_now, default=DEFAULT_NOW, help="clock HH:MM:SS")
    parser.add_argument("--show-stderr", action="store_true", help="pass the driver's stderr on")
    return parser.parse_args(argv, namespace=Options())


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    python_exe = env_python(args.venv or default_venv())
    if not python_exe.exists():
        sys.stderr.write(
            f"{python_exe} missing: run `uv run python -m scripts.legacy_env sync --python 3.8`\n"
        )
        return 1
    if not args.race_file.is_file():
        sys.stderr.write(f"{args.race_file}: no such file\n")
        return 1
    try:
        run = oracle(
            args.race_file,
            python_exe=python_exe,
            now=args.now,
            module=DRIVER_MODULE,
            show_stderr=args.show_stderr,
        )
    except OracleError as exc:
        sys.stderr.write(f"oracle: {exc}\n")
        return 1
    if args.out is None:
        # bytes: a redirected stdout on Windows would add the locale encoding and CRLF
        sys.stdout.flush()
        sys.stdout.buffer.write(dumps(run.results).encode("utf-8"))
        sys.stdout.buffer.flush()
        return 0
    write_run(run, args.out)
    races = as_list(as_dict(run.results).get("races"))
    count = sum(len(as_list(as_dict(r).get("results"))) for r in races)
    different = as_dict(run.comparison).get("different")
    print(f"{args.out}: {count} results in {len(races)} races, {different} stored values differ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
