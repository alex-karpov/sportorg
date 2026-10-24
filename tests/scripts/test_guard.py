"""The PreToolUse guard: legacy is read-only, golden files ask, everything else passes."""

import pytest

from scripts._json import as_dict, parse_json
from scripts.hooks import guard
from scripts.hooks._common import ROOT

LEGACY_FILE = r"C:\Users\ank\Prog\Orient\_other\pysport-legacy\sportorg\models\memory.py"
GOLDEN_FILE = str(ROOT / "tests" / "golden" / "race-2024-01.json")
ORDINARY_FILE = str(ROOT / "src" / "sportorg_ng" / "core" / "version.py")


@pytest.mark.parametrize("tool", ["Edit", "Write", "MultiEdit"])
def test_file_tools_are_denied_on_legacy(tool: str) -> None:
    decision = guard.evaluate(tool, {"file_path": LEGACY_FILE})
    assert decision is not None
    assert decision.permission == "deny"


def test_notebook_edit_uses_notebook_path() -> None:
    decision = guard.evaluate("NotebookEdit", {"notebook_path": LEGACY_FILE})
    assert decision is not None
    assert decision.permission == "deny"


def test_golden_files_ask_for_confirmation() -> None:
    decision = guard.evaluate("Write", {"file_path": GOLDEN_FILE})
    assert decision is not None
    assert decision.permission == "ask"
    assert "tests/golden/race-2024-01.json" in decision.reason


def test_ordinary_project_file_passes() -> None:
    assert guard.evaluate("Edit", {"file_path": ORDINARY_FILE}) is None


@pytest.mark.parametrize(
    "command",
    [
        "git -C ../_other/pysport-legacy log --oneline -5",
        "grep -rn 'def check_overtime' ../_other/pysport-legacy/sportorg",
        "git -C /c/Users/ank/Prog/Orient/_other/pysport-legacy show HEAD --stat",
    ],
)
def test_read_only_shell_commands_on_legacy_pass(command: str) -> None:
    assert guard.evaluate("Bash", {"command": command}) is None


@pytest.mark.parametrize(
    "command",
    [
        "echo x > ../_other/pysport-legacy/README.md",
        "rm -rf ../_other/pysport-legacy/.venv",
        "cd ../_other/pysport-legacy && uv sync",
        "git -C ../_other/pysport-legacy checkout main",
        "sed -i 's/a/b/' ../_other/pysport-legacy/sportorg/config.py",
        "Set-Content -Path C:\\Users\\ank\\Prog\\Orient\\_other\\pysport-legacy\\x.txt -Value 1",
    ],
)
def test_mutating_shell_commands_on_legacy_are_denied(command: str) -> None:
    decision = guard.evaluate("Bash", {"command": command})
    assert decision is not None
    assert decision.permission == "deny"


def test_commands_outside_legacy_are_not_touched() -> None:
    assert guard.evaluate("Bash", {"command": "rm -rf build && uv sync"}) is None


def test_unknown_tools_pass() -> None:
    assert guard.evaluate("WebFetch", {"url": "https://example.org"}) is None


def test_decision_json_matches_hook_schema() -> None:
    payload = as_dict(parse_json(guard.Decision("ask", "why").to_json()))
    output = as_dict(payload["hookSpecificOutput"])
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "ask"
    assert output["permissionDecisionReason"] == "why"
