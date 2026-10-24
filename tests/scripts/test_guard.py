"""The PreToolUse guard: legacy is read-only, golden files ask, everything else passes."""

import io
import sys
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, parse_json
from scripts.hooks import guard
from scripts.hooks._common import ROOT

if TYPE_CHECKING:
    from pathlib import Path

LEGACY_FILE = str(ROOT / ".legacy" / "pysport" / "sportorg" / "models" / "memory.py")
GOLDEN_FILE = str(ROOT / "tests" / "golden" / "race-2024-01.json")
ORDINARY_FILE = str(ROOT / "src" / "sportorg_ng" / "core" / "version.py")


def deny(tool: str, tool_input: dict[str, str]) -> bool:
    decision = guard.evaluate(tool, dict(tool_input))
    return decision is not None and decision.permission == "deny"


# ---------------------------------------------------------------- file tools


@pytest.mark.parametrize("tool", ["Edit", "Write", "MultiEdit"])
def test_file_tools_are_denied_on_legacy(tool: str) -> None:
    assert deny(tool, {"file_path": LEGACY_FILE})


def test_notebook_edit_uses_notebook_path() -> None:
    assert deny("NotebookEdit", {"notebook_path": LEGACY_FILE})


@pytest.mark.parametrize(
    "path",
    [
        ".legacy/pysport/README.md",
        "src/../.legacy/pysport/README.md",
        str(ROOT / ".LEGACY" / "PYSPORT" / "README.md"),
        "legacy/sportorg/sportorg/config.py",
        r"C:\Users\someone\Prog\Orient\_other\pysport-legacy\sportorg\config.py",
    ],
)
def test_file_tools_are_denied_on_every_spelling_of_legacy(path: str) -> None:
    assert deny("Edit", {"file_path": path})


def test_file_tools_follow_directory_links_into_legacy(tmp_path: Path) -> None:
    target = tmp_path / ".legacy" / "pysport"
    target.mkdir(parents=True)
    link = tmp_path / "innocent"
    if sys.platform == "win32":
        import _winapi  # noqa: PLC0415 -- Windows-only stdlib module; junctions need no privileges

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)
    assert deny("Write", {"file_path": str(link / "new.py")})


def test_legacy_run_clone_is_writable() -> None:
    assert (
        guard.evaluate("Edit", {"file_path": str(ROOT / ".legacy-run" / "pysport" / "x.py")})
        is None
    )


def test_golden_files_ask_for_confirmation() -> None:
    decision = guard.evaluate("Write", {"file_path": GOLDEN_FILE})
    assert decision is not None
    assert decision.permission == "ask"
    assert "tests/golden/race-2024-01.json" in decision.reason


def test_ordinary_project_file_passes() -> None:
    assert guard.evaluate("Edit", {"file_path": ORDINARY_FILE}) is None


def test_reading_legacy_passes() -> None:
    assert guard.evaluate("Read", {"file_path": LEGACY_FILE}) is None


# ---------------------------------------------------------------- shell commands


@pytest.mark.parametrize(
    "command",
    [
        "git -C .legacy/pysport log --oneline -5",
        "git -C .legacy/pysport merge-base HEAD origin/master",
        "git -C .legacy/pysport log --format='%an <%ae>' -1",
        "git -C .legacy/pysport log --grep move --oneline",
        "git -C .legacy/pysport branch -a --contains 30d849d",
        "git -C .legacy/pysport show HEAD:LICENSE 2>/dev/null | head -5",
        "grep -rn 'def check_overtime' .legacy/pysport/sportorg > /tmp/hits.txt",
        "git -C .legacy/pysport ls-tree -r HEAD | tee /tmp/tree.txt",
        "cp .legacy/pysport/README.md /tmp/readme.md",
        "cd .legacy/pysport && git log -1",
        "git -C .legacy/pysport status && rm -rf build",
        "uv run python -m scripts.bench_typecheckers --legacy-path .legacy/pysport/sportorg",
        "python -I scan.py .legacy/pysport/sportorg/data",
        "ls .legacy-run/pysport && rm -rf .legacy-run/pysport",
    ],
)
def test_read_only_shell_commands_on_legacy_pass(command: str) -> None:
    assert guard.evaluate("Bash", {"command": command}) is None


@pytest.mark.parametrize(
    "command",
    [
        "echo x > .legacy/pysport/README.md",
        "echo x >>.legacy/pysport/README.md",
        "echo ok; rm -rf .legacy/pysport/x",
        "true && rm -rf ./.legacy",
        "cd .legacy/pysport && uv sync",
        "cd .legacy/pysport; python SportOrg.pyw",
        "git -C .legacy/pysport checkout main",
        "git -C .legacy/pysport branch -D feature",
        "git -C .legacy/pysport fetch origin",
        "sed -i 's/a/b/' .legacy/pysport/sportorg/config.py",
        "cp README.md .legacy/pysport/README.md",
        "mv .legacy/pysport/a.py .legacy/pysport/b.py",
        "chmod -R u+w .legacy",
        "find .legacy -name '*.pyc' -delete",
        "ls .legacy/pysport | xargs rm",
        "echo x | tee -a .legacy/pysport/x.txt",
        "python .legacy/pysport/SportOrg.pyw",
        "pytest .legacy/pysport/tests",
        "uv run --directory .legacy/pysport pytest",
        "rm -rf legacy/sportorg/sportorg",
        "rm -rf ../_other/pysport-legacy/.venv",
        "git -C ../_other/pysport-legacy checkout main",
    ],
)
def test_mutating_shell_commands_on_legacy_are_denied(command: str) -> None:
    assert deny("Bash", {"command": command})


@pytest.mark.parametrize(
    "command",
    [
        r"Set-Content -Path .legacy\pysport\x.txt -Value 1",
        "Remove-Item -Recurse -Force .legacy",
        "Set-Location .legacy/pysport; Remove-Item x.txt",
        "Copy-Item README.md -Destination .legacy/pysport/README.md",
        r"attrib -R .legacy\pysport\x.txt",
        "icacls .legacy /remove:d someone",
    ],
)
def test_mutating_powershell_commands_on_legacy_are_denied(command: str) -> None:
    assert deny("PowerShell", {"command": command})


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content .legacy/pysport/README.md | Select-Object -First 5",
        "Copy-Item .legacy/pysport/README.md -Destination $env:TEMP/readme.md",
        "icacls .legacy/pysport",
        r"attrib .legacy\pysport\README.md",
    ],
)
def test_read_only_powershell_commands_on_legacy_pass(command: str) -> None:
    assert guard.evaluate("PowerShell", {"command": command}) is None


def test_commands_outside_legacy_are_not_touched() -> None:
    assert guard.evaluate("Bash", {"command": "rm -rf build && uv sync"}) is None


def test_unknown_tools_pass() -> None:
    assert guard.evaluate("WebFetch", {"url": "https://example.org"}) is None


# ---------------------------------------------------------------- the hook entry point


def run_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], stdin: str
) -> tuple[int, str]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    code = guard.main()
    return code, capsys.readouterr().out


def test_main_prints_the_decision(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin = '{"tool_name": "Bash", "tool_input": {"command": "rm -rf .legacy"}}'
    code, out = run_main(monkeypatch, capsys, stdin)
    assert code == 0
    output = as_dict(as_dict(parse_json(out))["hookSpecificOutput"])
    assert output["permissionDecision"] == "deny"


def test_main_is_silent_when_the_tool_may_run(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out = run_main(
        monkeypatch, capsys, '{"tool_name": "Bash", "tool_input": {"command": "ls"}}'
    )
    assert (code, out) == (0, "")


@pytest.mark.parametrize("stdin", ["", "not json", "[1, 2]", '{"tool_name": 5, "tool_input": "x"}'])
def test_main_never_fails_on_bad_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], stdin: str
) -> None:
    assert run_main(monkeypatch, capsys, stdin) == (0, "")


def test_main_asks_instead_of_crashing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def broken(_tool: str, _tool_input: dict[str, object]) -> guard.Decision | None:
        raise RuntimeError

    monkeypatch.setattr(guard, "evaluate", broken)
    stdin = '{"tool_name": "Bash", "tool_input": {"command": "rm -rf .legacy"}}'
    code, out = run_main(monkeypatch, capsys, stdin)
    assert code == 0
    output = as_dict(as_dict(parse_json(out))["hookSpecificOutput"])
    assert output["permissionDecision"] == "ask"


def test_decision_json_matches_hook_schema() -> None:
    payload = as_dict(parse_json(guard.Decision("ask", "why").to_json()))
    output = as_dict(payload["hookSpecificOutput"])
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "ask"
    assert output["permissionDecisionReason"] == "why"
