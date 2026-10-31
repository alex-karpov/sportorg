"""Tests for scripts/legacy_env.py: hermetic legacy runs, JUnit summaries, clone status.

Synthetic inputs only: no legacy environment, no network.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scripts import legacy, legacy_env
from scripts.legacy import Pin
from scripts.legacy_env import CaseOutcome, LegacyRun

if TYPE_CHECKING:
    from pathlib import Path

IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="5">
<testcase classname="tests.test_b" name="test_ok" time="0.1"/>
<testcase classname="tests.test_a.TestX" name="test_fail" time="0.1">
  <failure message="assert 'Ivanov Ivan' == 'Petrov'">locals: name = 'Ivanov Ivan'</failure>
</testcase>
<testcase classname="tests.test_a" name="test_error" time="0.1"><error message="boom"/></testcase>
<testcase classname="tests.test_a" name="test_skip[p1]" time="0"><skipped message="why"/></testcase>
<testcase classname="tests.test_c" name="test_teardown" time="0.1">
  <failure message="f"/><error message="teardown"/>
</testcase>
</testsuite></testsuites>
"""


def test_parse_junit_outcomes_sorted_by_id() -> None:
    assert legacy_env.parse_junit(JUNIT) == [
        CaseOutcome("tests.test_a.TestX::test_fail", "failed"),
        CaseOutcome("tests.test_a::test_error", "error"),
        CaseOutcome("tests.test_a::test_skip[p1]", "skipped"),
        CaseOutcome("tests.test_b::test_ok", "passed"),
        CaseOutcome("tests.test_c::test_teardown", "error"),
    ]


def test_junit_summary_keeps_ids_and_outcomes_only() -> None:
    run = LegacyRun("3.13.17", "offscreen", 1, legacy_env.parse_junit(JUNIT))

    text = json.dumps(legacy_env.summarize(run, ["tests/test_a.py"]))

    assert "Ivanov" not in text
    assert "boom" not in text
    assert "teardown" in text  # the test id, not the message


def test_summary_counts_and_recalc_subset() -> None:
    run = LegacyRun("3.13.17", "offscreen", 1, legacy_env.parse_junit(JUNIT))

    summary = legacy_env.summarize(run, ["tests/test_a.py"])

    assert summary["crashed"] is False
    assert summary["counts"] == {"error": 2, "failed": 1, "passed": 1, "skipped": 1, "total": 5}
    assert summary["recalc_counts"] == {
        "error": 1,
        "failed": 1,
        "passed": 0,
        "skipped": 1,
        "total": 3,
    }


def test_missing_junit_is_reported_as_crash() -> None:
    summary = legacy_env.summarize(LegacyRun("3.13.17", "none", -6, None), [])

    assert summary["crashed"] is True
    assert summary["exit_code"] == -6
    assert summary["counts"] == {"error": 0, "failed": 0, "passed": 0, "skipped": 0, "total": 0}


def test_hermetic_env(tmp_path: Path) -> None:
    base = {
        "PATH": "/usr/bin",
        "HOME": "/home/real",
        "DISPLAY": ":0",
        "WAYLAND_DISPLAY": "wayland-0",
        "VIRTUAL_ENV": "/project/.venv",
        "PYTHONPATH": "/project",
        "QT_QPA_PLATFORM": "xcb",
        "TZ": "Europe/Moscow",
    }
    home = tmp_path / "home"
    templates = tmp_path / "templates" / "ru"

    env = legacy_env.hermetic_env(base, home=home, qt_platform="offscreen", templates=templates)

    assert env["PATH"] == "/usr/bin"
    for name in ("DISPLAY", "WAYLAND_DISPLAY", "VIRTUAL_ENV", "PYTHONPATH"):
        assert name not in env
    assert env["HOME"] == str(home)
    assert env["XDG_CONFIG_HOME"] == str(home / ".config")
    assert env["TZ"] == "UTC"
    assert env["LC_ALL"] == "C.UTF-8"
    assert env["PYTHONHASHSEED"] == "0"
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert env["QT_QPA_PLATFORM"] == "offscreen"
    assert env["SPORTORG_TEMPLATES_PATH"] == str(templates)


def test_hermetic_env_without_platform_drops_qt_variable(tmp_path: Path) -> None:
    base = {"QT_QPA_PLATFORM": "xcb"}

    env = legacy_env.hermetic_env(base, home=tmp_path, qt_platform=None, templates=tmp_path)

    assert "QT_QPA_PLATFORM" not in env


def test_recalc_test_modules(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_a.py").write_text("recalculate_results(race)\n", encoding="utf-8")
    (tests / "test_b.py").write_text("x = 1\n", encoding="utf-8")
    (tests / "test_c.py").write_text("ResultCalculation(r).process_results()\n", encoding="utf-8")

    assert legacy_env.recalc_test_modules(tmp_path) == ["tests/test_a.py", "tests/test_c.py"]


def test_sanitize_replaces_local_paths() -> None:
    text = "error: failed at /home/u/repo/.legacy-run/pysport/.venv-probe-3.8/bin/python"

    clean = legacy_env.sanitize(text, {"/home/u/repo/.legacy-run": "<run>"})

    assert clean == "error: failed at <run>/pysport/.venv-probe-3.8/bin/python"


def test_clone_problems_reports_untracked_file(tmp_path: Path) -> None:
    clone = tmp_path / "demo"
    legacy.git("init", "--quiet", str(clone))
    legacy.git(*IDENTITY, "commit", "--quiet", "--allow-empty", "-m", "pin", cwd=clone)
    pin = Pin("demo", "unused", legacy.git("rev-parse", "HEAD", cwd=clone))

    assert legacy_env.clone_problems(pin, base=tmp_path) == []

    (clone / "left-behind.txt").write_text("x", encoding="utf-8")

    assert legacy_env.clone_problems(pin, base=tmp_path) == ["demo: ?? left-behind.txt"]


def test_clone_problems_reports_wrong_head(tmp_path: Path) -> None:
    clone = tmp_path / "demo"
    legacy.git("init", "--quiet", str(clone))
    legacy.git(*IDENTITY, "commit", "--quiet", "--allow-empty", "-m", "pin", cwd=clone)
    pin = Pin("demo", "unused", legacy.git("rev-parse", "HEAD", cwd=clone))
    legacy.git(*IDENTITY, "commit", "--quiet", "--allow-empty", "-m", "later", cwd=clone)

    problems = legacy_env.clone_problems(pin, base=tmp_path)

    assert problems == [f"demo: HEAD is not the pin {pin.commit[:12]}"]


def test_counts_text_fits_in_a_markdown_cell() -> None:
    counts = {"error": 0, "failed": 3, "passed": 288, "skipped": 10, "total": 301}

    assert legacy_env.counts_text(counts) == "error 0, failed 3, passed 288, skipped 10, total 301"


def test_not_passed_lists_ids_with_outcomes() -> None:
    run = LegacyRun("3.13.17", "offscreen", 1, legacy_env.parse_junit(JUNIT))

    assert legacy_env.not_passed(legacy_env.summarize(run, [])) == [
        "tests.test_a.TestX::test_fail: failed",
        "tests.test_a::test_error: error",
        "tests.test_a::test_skip[p1]: skipped",
        "tests.test_c::test_teardown: error",
    ]


def _demo_clone(tmp_path: Path) -> tuple[Path, Pin]:
    clone = tmp_path / "demo"
    legacy.git("init", "--quiet", str(clone))
    (clone / ".gitignore").write_text(".venv*\n*.tmp\n", encoding="utf-8")
    (clone / "tracked.txt").write_text("pinned\n", encoding="utf-8")
    legacy.git("add", ".gitignore", "tracked.txt", cwd=clone)
    legacy.git(*IDENTITY, "commit", "--quiet", "-m", "pin", cwd=clone)
    return clone, Pin("demo", "unused", legacy.git("rev-parse", "HEAD", cwd=clone))


def test_clean_clone_restores_the_pin_and_keeps_environments(tmp_path: Path) -> None:
    clone, pin = _demo_clone(tmp_path)
    (clone / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (clone / "untracked.txt").write_text("x", encoding="utf-8")
    (clone / "left.tmp").write_text("x", encoding="utf-8")
    (clone / ".venv" / "bin").mkdir(parents=True)
    (clone / ".venv" / "bin" / "python").write_text("", encoding="utf-8")

    legacy_env.clean_clone(clone)

    assert (clone / "tracked.txt").read_text(encoding="utf-8") == "pinned\n"
    assert not (clone / "untracked.txt").exists()
    assert not (clone / "left.tmp").exists()
    assert (clone / ".venv" / "bin" / "python").exists()
    assert legacy_env.clone_problems(pin, base=tmp_path) == []


def test_clone_problems_reports_ignored_leftovers_but_not_environments(tmp_path: Path) -> None:
    clone, pin = _demo_clone(tmp_path)
    (clone / "left.tmp").write_text("x", encoding="utf-8")
    (clone / ".venv").mkdir()
    (clone / ".venv" / "pyvenv.cfg").write_text("", encoding="utf-8")

    assert legacy_env.clone_problems(pin, base=tmp_path) == ["demo: !! left.tmp"]


def test_pytest_command_deselects_unstable_tests(tmp_path: Path) -> None:
    junit = tmp_path / "junit.xml"
    python = tmp_path / "python"

    command = legacy_env.pytest_command(python, junit, ["tests/test_x.py::test_flaky"])

    assert command == [
        str(python),
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit}",
        "--deselect",
        "tests/test_x.py::test_flaky",
    ]


def test_summary_lists_deselected_tests() -> None:
    run = LegacyRun("3.13.17", "offscreen", 0, [], deselected=("tests/test_x.py::test_flaky",))

    assert legacy_env.summarize(run, [])["deselected"] == ["tests/test_x.py::test_flaky"]


def test_unstable_tests_are_the_teamwork_server_client_tests() -> None:
    names = [
        "test_teamwork",
        "test_teamwork_keepalive_and_server_disconnect",
        "test_teamwork_with_encryption",
        "test_teamwork_disconnect_on_encryption_mismatch",
        "test_teamwork_race_id_mismatch_requires_confirmation",
    ]

    assert sorted(legacy_env.UNSTABLE_TESTS) == sorted(
        f"tests/test_teamwork.py::{name}" for name in names
    )
    assert set(legacy_env.UNSTABLE_TESTS.values()) == {legacy_env.TEAMWORK_REASON}
