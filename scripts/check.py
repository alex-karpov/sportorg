"""Run every quality check the project defines.

Usage::

    uv run python scripts/check.py                # all steps, fail-fast
    uv run python scripts/check.py --fix          # ruff format + autofix, then all steps
    uv run python scripts/check.py --only lint,tests
    uv run python scripts/check.py --keep-going   # run every step even after a failure
    uv run python scripts/check.py --files src/sportorg_ng/core/version.py   # file-level steps

This script is the single definition of "green". pre-commit, CI and agent hooks call the same
steps. It runs inside the project environment, so tools are resolved from the virtualenv on PATH.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED_DIRS = ("src", "tests", "scripts")
STEP_ORDER = ("format", "lint", "types", "imports", "golden", "tests")
FILE_LEVEL_STEPS = ("format", "lint", "types")


class Options(argparse.Namespace):
    fix: bool = False
    only: str | None = None
    keep_going: bool = False
    files: list[str] | None = None


def _tool(name: str) -> str:
    exe = shutil.which(name)
    if exe is None:
        msg = f"{name} not found on PATH: run `uv sync`, then `uv run python scripts/check.py`"
        raise SystemExit(msg)
    return exe


def step_command(step: str, *, fix: bool = False, files: list[str] | None = None) -> list[str]:
    """Return the command line for one step, optionally restricted to given files."""
    targets = files or list(CHECKED_DIRS)
    if step == "format":
        return [_tool("ruff"), "format", *([] if fix else ["--check"]), *targets]
    if step == "lint":
        return [_tool("ruff"), "check", *(["--fix"] if fix else []), *targets]
    if step == "types":
        return [_tool("basedpyright"), *targets]
    if step == "imports":
        return [_tool("lint-imports")]
    if step == "golden":
        # Committed history against main (+ $GOLDEN_BASE in CI): AGENTS.md rule 5, ADR-0008.
        return [sys.executable, "-m", "scripts.golden_guard", "range"]
    if step == "tests":
        return [_tool("pytest"), "-q", *(files or [])]
    msg = f"unknown step {step!r}; known: {', '.join(STEP_ORDER)}"
    raise SystemExit(msg)


def run_step(step: str, *, fix: bool, files: list[str] | None) -> tuple[int, float]:
    cmd = step_command(step, fix=fix, files=files)
    print(f"\n== {step}: {' '.join(cmd)}", flush=True)
    started = time.perf_counter()
    code = subprocess.run(cmd, cwd=ROOT, check=False).returncode
    return code, time.perf_counter() - started


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--fix", action="store_true", help="apply ruff format and safe autofixes")
    parser.add_argument("--only", help="comma-separated subset of steps")
    parser.add_argument("--keep-going", action="store_true", help="do not stop at first failure")
    parser.add_argument("--files", nargs="+", help="restrict file-level steps to these files")
    return parser.parse_args(argv, namespace=Options())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    steps = list(STEP_ORDER)
    if args.only:
        steps = [s.strip() for s in args.only.split(",") if s.strip()]
    if args.files:
        steps = [s for s in steps if s in FILE_LEVEL_STEPS]

    results: list[tuple[str, int, float]] = []
    for step in steps:
        code, seconds = run_step(step, fix=args.fix, files=args.files)
        results.append((step, code, seconds))
        if code and not args.keep_going:
            break

    print("\n== summary")
    for step, code, seconds in results:
        print(f"{'ok  ' if code == 0 else 'FAIL'} {step:<8} {seconds:6.2f}s")
    done = {step for step, _, _ in results}
    skipped = [s for s in steps if s not in done]
    if skipped:
        print(f"skipped (fail-fast): {', '.join(skipped)}")
    return 1 if any(code for _, code, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
