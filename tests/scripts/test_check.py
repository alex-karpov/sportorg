"""Tests for scripts/check.py: the step list that defines "green"."""

from __future__ import annotations

import sys

from scripts import check


def test_golden_step_runs_the_guard_on_the_committed_range() -> None:
    assert check.step_command("golden") == [sys.executable, "-m", "scripts.golden_guard", "range"]


def test_golden_step_runs_before_tests() -> None:
    assert check.STEP_ORDER.index("golden") < check.STEP_ORDER.index("tests")
