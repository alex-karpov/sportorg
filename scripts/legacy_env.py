"""Legacy runtime in ``.legacy-run/pysport``: Python probe, sync, headless tests, clone status.

Stage 2 rule 1: legacy runs only from the writable copy made by ``scripts.legacy_clone``, in its own
environment (``uv sync --frozen`` on the legacy lock file), never in the project environment.
Managed Pythons go to ``.legacy-run/python`` (``UV_PYTHON_INSTALL_DIR``) so the runtime does not
depend on the interpreters of the machine.

Legacy tests run hermetically: temporary HOME and XDG directories, ``TZ=UTC``, ``C.UTF-8``,
``PYTHONHASHSEED=0``, no ``DISPLAY``/``WAYLAND_DISPLAY``, templates from
``.legacy-run/templates/ru``.
Before pytest, ``python -m sportorg.language`` compiles the translations, as legacy's own
``poe test`` does. Legacy pytest runs with ``--showlocals`` over data with personal data, so its
console output is discarded: only test ids and outcomes (from JUnit XML) reach the evidence.

Usage::

    uv run python -m scripts.legacy_env probe --out DIR --python 3.14 --python 3.13 ...
    uv run python -m scripts.legacy_env sync --python 3.13
    uv run python -m scripts.legacy_env tests --out DIR --name NAME --qt-platform offscreen|none
    uv run python -m scripts.legacy_env status    # copies at their pin, nothing left behind
    uv run python -m scripts.legacy_env restore   # clean the copies back to HEAD, keep .venv*
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts._json import as_dict, as_str, parse_toml
from scripts.archaeology.common import write_outputs
from scripts.legacy import ROOT, Pin, checkout_dir, load_manifest, run_dir

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from scripts._json import Json

type Outcome = Literal["passed", "failed", "error", "skipped"]

OUTCOMES: tuple[Outcome, ...] = ("error", "failed", "passed", "skipped")
CLONE_NAME = "pysport"
TEMPLATES_NAME = "templates"
RECALC_MARKERS = ("recalculate_results", "ResultCalculation")
REMOVED_VARIABLES = (
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "VIRTUAL_ENV",
    "PYTHONPATH",
    "PYTHONHOME",
    "QT_QPA_PLATFORM",
    "UV_PROJECT_ENVIRONMENT",
)
ENV_EXCLUDES = ("/.venv", "/.venv-*")
SYNC_ARGS = ("sync", "--frozen", "--extra", "gui", "--python-preference", "only-managed")
TEST_TIMEOUT = 1800
# Legacy tests whose outcome changes between identical runs; deselected in every evidence run and
# listed in its output. Two of these were seen flipping; all five share the same construction
# (docs/evidence/stage-2/legacy-env/unstable-tests.agent.md).
TEAMWORK_REASON = "timing: real TCP server and client threads on 127.0.0.1 with wait/queue timeouts"
UNSTABLE_TESTS: dict[str, str] = {
    f"tests/test_teamwork.py::{name}": TEAMWORK_REASON
    for name in (
        "test_teamwork",
        "test_teamwork_keepalive_and_server_disconnect",
        "test_teamwork_with_encryption",
        "test_teamwork_disconnect_on_encryption_mismatch",
        "test_teamwork_race_id_mismatch_requires_confirmation",
    )
}
SETUP_TIMEOUT = 300


@dataclass(frozen=True, slots=True)
class CaseOutcome:
    test_id: str
    outcome: Outcome


@dataclass(frozen=True, slots=True)
class LegacyRun:
    python: str
    qt_platform: str
    exit_code: int
    outcomes: list[CaseOutcome] | None
    setup_exit: int = 0
    deselected: tuple[str, ...] = ()


def clone_path() -> Path:
    return run_dir() / CLONE_NAME


def python_dir() -> Path:
    return run_dir() / "python"


def templates_ru() -> Path:
    return run_dir() / TEMPLATES_NAME / "ru"


def env_python(env_dir: Path) -> Path:
    if sys.platform == "win32":
        return env_dir / "Scripts" / "python.exe"
    return env_dir / "bin" / "python"


# ---------------------------------------------------------------- pure helpers


def parse_junit(xml_text: str) -> list[CaseOutcome]:
    """Test id (``classname::name``) and outcome of each test case, sorted by id."""
    root = ET.fromstring(xml_text)  # noqa: S314 - JUnit XML written by our own pytest run
    cases: list[CaseOutcome] = []
    for case in root.iter("testcase"):
        test_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("error") is not None:
            outcome: Outcome = "error"
        elif case.find("failure") is not None:
            outcome = "failed"
        elif case.find("skipped") is not None:
            outcome = "skipped"
        else:
            outcome = "passed"
        cases.append(CaseOutcome(test_id, outcome))
    return sorted(cases, key=lambda c: c.test_id)


def _counts(cases: Sequence[CaseOutcome]) -> dict[str, Json]:
    counts: dict[str, Json] = {o: sum(1 for c in cases if c.outcome == o) for o in OUTCOMES}
    counts["total"] = len(cases)
    return counts


def _in_module(test_id: str, module_path: str) -> bool:
    dotted = module_path.removesuffix(".py").replace("/", ".")
    return test_id.startswith((f"{dotted}.", f"{dotted}::"))


def summarize(run: LegacyRun, recalc_modules: Sequence[str]) -> dict[str, Json]:
    """Evidence summary of one legacy test run: ids and outcomes only, never messages."""
    cases = run.outcomes or []
    recalc = [c for c in cases if any(_in_module(c.test_id, m) for m in recalc_modules)]
    return {
        "python": run.python,
        "qt_platform": run.qt_platform,
        "setup_exit": run.setup_exit,
        "exit_code": run.exit_code,
        "crashed": run.outcomes is None,
        "deselected": [*run.deselected],
        "counts": _counts(cases),
        "recalc_modules": list(recalc_modules),
        "recalc_counts": _counts(recalc),
        "tests": [{"id": c.test_id, "outcome": c.outcome} for c in cases],
    }


def hermetic_env(
    base: Mapping[str, str], *, home: Path, qt_platform: str | None, templates: Path
) -> dict[str, str]:
    """Environment for running legacy code: no display, no project venv, fixed TZ and locale."""
    env = {k: v for k, v in base.items() if k not in REMOVED_VARIABLES}
    env |= {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "APPDATA": str(home / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home / "AppData" / "Local"),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_STATE_HOME": str(home / ".local" / "state"),
        "XDG_RUNTIME_DIR": str(home / ".runtime"),
        "TZ": "UTC",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "SPORTORG_TEMPLATES_PATH": str(templates),
    }
    if qt_platform is not None:
        env["QT_QPA_PLATFORM"] = qt_platform
    return env


def recalc_test_modules(clone: Path) -> list[str]:
    """Legacy test modules that call the recalculation directly."""
    tests = clone / "tests"
    found = [
        p.relative_to(clone).as_posix()
        for p in tests.rglob("test_*.py")
        if any(m in p.read_text(encoding="utf-8") for m in RECALC_MARKERS)
    ]
    return sorted(found)


def sanitize(text: str, replacements: Mapping[str, str]) -> str:
    for old in sorted(replacements, key=len, reverse=True):
        text = text.replace(old, replacements[old])
    return text


def clone_problems(pin: Pin, *, base: Path | None = None) -> list[str]:
    """Why ``.legacy-run/<name>`` is not a clean copy at its pin (empty list = clean)."""
    path = checkout_dir(pin.name, base if base is not None else run_dir())
    if not (path / ".git").exists():
        return [
            f"{pin.name}: missing (run `uv run python -m scripts.legacy_clone --name {pin.name}`)"
        ]
    head = _run(["git", "rev-parse", "HEAD"], cwd=path).stdout.strip()
    if head != pin.commit:
        return [f"{pin.name}: HEAD is not the pin {pin.commit[:12]}"]
    status = _run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored"], cwd=path
    )
    return [
        f"{pin.name}: {entry}"
        for entry in status.stdout.split("\0")
        if entry and not _is_environment(entry[3:])
    ]


def _is_environment(path: str) -> bool:
    """Legacy environments (``.venv``, ``.venv-probe-*``) are kept by design (Stage 2 rule 1)."""
    return path.split("/", maxsplit=1)[0].startswith(".venv")


def clean_clone(clone: Path) -> None:
    """Back to HEAD: tracked files restored, untracked and ignored files removed, envs kept."""
    _run(["git", "reset", "--quiet", "--hard", "HEAD"], cwd=clone)
    _run(["git", "clean", "-ffdxq", *(f"--exclude={p}" for p in ENV_EXCLUDES)], cwd=clone)


# ---------------------------------------------------------------- processes


def _run(
    cmd: Sequence[str | Path],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    timeout: float = SETUP_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(c) for c in cmd],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def pytest_command(python_exe: Path, junit: Path, deselect: Iterable[str]) -> list[str]:
    deselected = [arg for test in deselect for arg in ("--deselect", test)]
    return [
        str(python_exe),
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit}",
        *deselected,
    ]


def _uv_env(env_dir: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["UV_PROJECT_ENVIRONMENT"] = str(env_dir)
    env["UV_PYTHON_INSTALL_DIR"] = str(python_dir())
    return env


def sync(clone: Path, env_dir: Path, python: str) -> subprocess.CompletedProcess[str]:
    uv = shutil.which("uv") or "uv"
    return _run([uv, *SYNC_ARGS, "--python", python], cwd=clone, env=_uv_env(env_dir))


def python_version(python_exe: Path) -> str:
    code = "import platform; print(platform.python_version())"
    return _run([python_exe, "-c", code], cwd=ROOT).stdout.strip()


def resolved_python(request: str, clone: Path) -> str | None:
    uv = shutil.which("uv") or "uv"
    found = _run(
        [uv, "python", "find", "--python-preference", "only-managed", request],
        cwd=clone,
        env=_uv_env(clone / ".venv-unused"),
    )
    path = found.stdout.strip()
    return python_version(Path(path)) if found.returncode == 0 and path else None


def run_legacy_tests(clone: Path, python_exe: Path, *, qt_platform: str | None) -> LegacyRun:
    """Run legacy's tests from a clean copy and clean it again afterwards."""
    clean_clone(clone)
    try:
        return _run_legacy_tests(clone, python_exe, qt_platform=qt_platform)
    finally:
        clean_clone(clone)


def _run_legacy_tests(clone: Path, python_exe: Path, *, qt_platform: str | None) -> LegacyRun:
    with tempfile.TemporaryDirectory(prefix="legacy-tests-") as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        (home / ".runtime").mkdir(mode=0o700)
        env = hermetic_env(os.environ, home=home, qt_platform=qt_platform, templates=templates_ru())
        setup = _run([python_exe, "-m", "sportorg.language"], cwd=clone, env=env)
        junit = Path(tmp) / "junit.xml"
        result = _run(
            pytest_command(python_exe, junit, UNSTABLE_TESTS),
            cwd=clone,
            env=env,
            timeout=TEST_TIMEOUT,
        )
        text = junit.read_text(encoding="utf-8") if junit.exists() else ""
        outcomes = parse_junit(text) if text.strip() else None
    return LegacyRun(
        python_version(python_exe),
        qt_platform or "none",
        result.returncode,
        outcomes,
        setup.returncode,
        tuple(UNSTABLE_TESTS),
    )


# ---------------------------------------------------------------- commands


def _requires_python(clone: Path) -> str:
    data = as_dict(parse_toml((clone / "pyproject.toml").read_text(encoding="utf-8")))
    return as_str(as_dict(data.get("project")).get("requires-python"))


def _error_line(output: str) -> str:
    lines = [line for line in output.splitlines() if line.startswith("error:")]
    replacements = {str(ROOT): "<repo>", str(Path.home()): "~"}
    return sanitize(lines[0], replacements) if lines else ""


def counts_text(counts: Mapping[str, Json]) -> str:
    """Counts on one line without ``|``, so they fit in a markdown table cell."""
    return ", ".join(f"{k} {counts[k]}" for k in (*OUTCOMES, "total"))


def not_passed(summary: Mapping[str, Json]) -> list[str]:
    """``<test id>: <outcome>`` for every test of a summary that did not pass."""
    tests = summary.get("tests")
    return [
        f"{as_str(t.get('id'))}: {as_str(t.get('outcome'))}"
        for t in (tests if isinstance(tests, list) else [])
        if isinstance(t, dict) and t.get("outcome") != "passed"
    ]


def probe_command(out: Path, pythons: Sequence[str]) -> int:
    clone = clone_path()
    recalc = recalc_test_modules(clone)
    uv = shutil.which("uv") or "uv"
    candidates: list[Json] = []
    details: list[str] = []
    rows = ["| request | resolved | uv sync | legacy tests (offscreen) |", "|---|---|---|---|"]
    for request in pythons:
        env_dir = clone / f".venv-probe-{request}"
        synced = sync(clone, env_dir, request)
        entry: dict[str, Json] = {
            "request": request,
            "resolved": resolved_python(request, clone),
            "sync_exit": synced.returncode,
            "sync_error": _error_line(synced.stdout + synced.stderr),
            "tests": None,
        }
        cell = "not run"
        if synced.returncode == 0:
            summary = summarize(
                run_legacy_tests(clone, env_python(env_dir), qt_platform="offscreen"), recalc
            )
            entry["tests"] = {k: summary[k] for k in ("exit_code", "crashed", "counts")}
            failing = not_passed(summary)
            entry["not_passed"] = [*failing]
            if failing:
                details.append(f"- {request}: " + "; ".join(failing))
            counts = summary["counts"]
            cell = counts_text(counts) if isinstance(counts, dict) else ""
        shutil.rmtree(env_dir, ignore_errors=True)
        candidates.append(entry)
        sync_cell = (
            "ok" if synced.returncode == 0 else f"exit {synced.returncode}: {entry['sync_error']}"
        )
        rows.append(f"| {request} | {entry['resolved']} | {sync_cell} | {cell} |")
    data: Json = {
        "legacy_requires_python": _requires_python(clone),
        "uv": _run([uv, "--version"], cwd=ROOT).stdout.strip(),
        "candidates": candidates,
    }
    header = (
        "# Python for the legacy runtime (ADR-0009 T1)\n\n"
        f'Legacy `requires-python = "{_requires_python(clone)}"`. Each candidate: '
        "`uv sync --frozen --extra gui --python-preference only-managed` into a throwaway "
        "environment, then legacy's own tests headless (`QT_QPA_PLATFORM=offscreen`, no display)."
    )
    table = "\n".join([*rows, "", "Tests that did not pass, per candidate:", "", *details])
    write_outputs(out, "python-probe", data, table, header)
    return 0


def tests_command(out: Path, name: str, qt_platform: str | None) -> int:
    clone = clone_path()
    python_exe = env_python(clone / ".venv")
    if not python_exe.exists():
        print(
            f"{python_exe} missing: run `uv run python -m scripts.legacy_env sync`", file=sys.stderr
        )
        return 1
    recalc = recalc_test_modules(clone)
    summary = summarize(run_legacy_tests(clone, python_exe, qt_platform=qt_platform), recalc)
    counts = summary["counts"]
    recalc_counts = summary["recalc_counts"]
    others = [f"- `{line}`" for line in not_passed(summary)]
    lines = [
        (
            f"Python {summary['python']}, `QT_QPA_PLATFORM` = {summary['qt_platform']}, "
            f"no `DISPLAY`/`WAYLAND_DISPLAY`. Translation setup exit {summary['setup_exit']}, "
            f"pytest exit {summary['exit_code']}, crashed: {summary['crashed']}."
        ),
        "",
        f"- all tests: {counts_text(counts) if isinstance(counts, dict) else ''}",
        (
            f"- recalculation tests ({', '.join(f'`{m}`' for m in recalc)}): "
            f"{counts_text(recalc_counts) if isinstance(recalc_counts, dict) else ''}"
        ),
        "",
        "Not passed:" if others else "Not passed: none.",
        *others,
    ]
    header = f"# Legacy tests: {name}"
    write_outputs(out, name, summary, "\n".join(lines), header)
    return 0


def sync_command(python: str) -> int:
    clone = clone_path()
    result = sync(clone, clone / ".venv", python)
    print(f"uv sync --python {python}: exit {result.returncode}")
    if result.returncode:
        print(_error_line(result.stdout + result.stderr) or result.stderr[-2000:])
        return 1
    print(f"{env_python(clone / '.venv')}: Python {python_version(env_python(clone / '.venv'))}")
    return 0


def restore_command() -> int:
    for pin in load_manifest():
        path = checkout_dir(pin.name, run_dir())
        if (path / ".git").exists():
            clean_clone(path)
    return status_command()


def status_command() -> int:
    pins = load_manifest()
    problems = [p for pin in pins for p in clone_problems(pin)]
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("ok: " + ", ".join(f"{p.name}@{p.commit[:12]}" for p in pins) + " clean in .legacy-run")
    return 0


class Options(argparse.Namespace):
    command: str = ""
    out: Path = Path()
    python: list[str] | None = None
    name: str = ""
    qt_platform: str = "offscreen"


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    probe = sub.add_parser("probe", help="sync and test each candidate Python")
    probe.add_argument("--out", type=Path, required=True)
    probe.add_argument("--python", action="append", required=True)
    sync_p = sub.add_parser("sync", help="create .legacy-run/pysport/.venv")
    sync_p.add_argument("--python", action="append", required=True)
    tests = sub.add_parser("tests", help="run legacy tests in .legacy-run/pysport/.venv")
    tests.add_argument("--out", type=Path, required=True)
    tests.add_argument("--name", required=True)
    tests.add_argument("--qt-platform", choices=("offscreen", "none"), default="offscreen")
    sub.add_parser("status", help="both copies at their pin and clean")
    sub.add_parser("restore", help="clean both copies back to HEAD (environments kept)")
    return parser.parse_args(argv, namespace=Options())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    pythons = args.python or []
    if args.command == "probe":
        return probe_command(args.out, pythons)
    if args.command == "sync":
        return sync_command(pythons[-1])
    if args.command == "tests":
        platform = None if args.qt_platform == "none" else args.qt_platform
        return tests_command(args.out, args.name, platform)
    if args.command == "restore":
        return restore_command()
    return status_command()


if __name__ == "__main__":
    sys.exit(main())
