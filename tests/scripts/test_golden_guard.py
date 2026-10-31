"""Tests for scripts/golden_guard.py: a golden change needs the maintainer's trailer (ADR-0008).

Every test builds a temporary git repository: ``main`` has a base commit, work happens on ``work``
unless the test is about the default branch itself. No network, no legacy, no real golden files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import golden_guard, legacy
from scripts.golden_guard import GuardError, Violation

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

IDENTITY = (
    "-c",
    "user.name=test",
    "-c",
    "user.email=test@example.invalid",
    "-c",
    "commit.gpgsign=false",
)
APPROVED = "\n\nGolden-Approved-By: maintainer"

type Commit = Callable[..., str]


def git(repo: Path, *args: str) -> str:
    return legacy.git(*IDENTITY, *args, cwd=repo)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    git(path, "init", "--quiet", "--initial-branch=main")
    (path / "README").write_text("base\n", encoding="utf-8")
    git(path, "add", "README")
    git(path, "commit", "--quiet", "-m", "base")
    git(path, "switch", "--quiet", "-c", "work")
    return path


@pytest.fixture
def commit(repo: Path) -> Commit:
    """Write files (path -> text, None = delete), commit with ``message``, return the commit id."""

    def make(message: str, files: dict[str, str | None]) -> str:
        for name, text in files.items():
            target = repo / name
            if text is None:
                git(repo, "rm", "--quiet", "--", name)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            git(repo, "add", "--", name)
        git(repo, "commit", "--quiet", "--allow-empty", "-m", message)
        return git(repo, "rev-parse", "HEAD")

    return make


def test_commit_without_trailer_fails(repo: Path, commit: Commit) -> None:
    sha = commit("add golden", {"tests/golden/a.json": "{}"})

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert found == [Violation(sha, "add golden", ("tests/golden/a.json",))]


def test_commit_with_trailer_passes(repo: Path, commit: Commit) -> None:
    commit("add golden" + APPROVED, {"tests/golden/a.json": "{}"})

    assert golden_guard.check_range("HEAD", base=None, cwd=repo) == []


def test_non_golden_change_passes(repo: Path, commit: Commit) -> None:
    commit("code", {"tests/test_a.py": "x = 1\n", "tests/goldenish.txt": "no"})

    assert golden_guard.check_range("HEAD", base=None, cwd=repo) == []


def test_every_commit_needs_its_own_trailer(repo: Path, commit: Commit) -> None:
    first = commit("first", {"tests/golden/a.json": "{}"})
    commit("second" + APPROVED, {"tests/golden/b.json": "{}"})

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert [v.commit for v in found] == [first]


def test_deletion_needs_trailer(repo: Path, commit: Commit) -> None:
    commit("add" + APPROVED, {"tests/golden/a.json": "{}"})
    sha = commit("drop", {"tests/golden/a.json": None})

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert found == [Violation(sha, "drop", ("tests/golden/a.json",))]


def test_rename_out_of_golden_needs_trailer(repo: Path, commit: Commit) -> None:
    commit("add" + APPROVED, {"tests/golden/a.json": "{}"})
    git(repo, "mv", "tests/golden/a.json", "tests/a.json")
    git(repo, "commit", "--quiet", "-m", "move")

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert [v.paths for v in found] == [("tests/golden/a.json",)]


def test_evil_merge_needs_trailer(repo: Path, commit: Commit) -> None:
    commit("work side", {"work.txt": "w"})
    git(repo, "switch", "--quiet", "-c", "side", "main")
    commit("side", {"side.txt": "s"})
    git(repo, "switch", "--quiet", "work")
    git(repo, "merge", "--quiet", "--no-ff", "--no-commit", "side")
    (repo / "tests" / "golden").mkdir(parents=True)
    (repo / "tests" / "golden" / "m.json").write_text("{}", encoding="utf-8")
    git(repo, "add", "tests/golden/m.json")
    git(repo, "commit", "--quiet", "-m", "merge side")
    merge = git(repo, "rev-parse", "HEAD")

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert found == [Violation(merge, "merge side", ("tests/golden/m.json",))]


def test_clean_merge_of_approved_branch_passes(repo: Path, commit: Commit) -> None:
    git(repo, "switch", "--quiet", "-c", "side", "main")
    commit("side golden" + APPROVED, {"tests/golden/s.json": "{}"})
    git(repo, "switch", "--quiet", "work")
    commit("work", {"work.txt": "w"})
    git(repo, "merge", "--quiet", "--no-ff", "-m", "merge side", "side")

    assert golden_guard.check_range("HEAD", base=None, cwd=repo) == []


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("tests/golden/a.json", True),
        ("tests/golden", True),
        ("Tests/Golden/a.json", True),
        ("tests\\golden\\a.json", True),
        ("tests/golden/sub/dir/b.txt", True),
        ("tests/goldenfile", False),
        ("tests/test_golden.py", False),
        ("src/tests/golden/a.json", False),
    ],
)
def test_case_variant_path_is_golden(path: str, *, expected: bool) -> None:
    assert golden_guard.is_golden(path) is expected


def test_non_ascii_golden_path(repo: Path, commit: Commit) -> None:
    name = "tests/golden/протокол ü.json"
    sha = commit("non-ascii", {name: "{}"})

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert found == [Violation(sha, "non-ascii", (name,))]


def test_trailer_in_body_does_not_approve(repo: Path, commit: Commit) -> None:
    message = "subject\n\nGolden-Approved-By: maintainer\n\nA paragraph after it."
    commit(message, {"tests/golden/a.json": "{}"})

    assert len(golden_guard.check_range("HEAD", base=None, cwd=repo)) == 1


def test_empty_trailer_does_not_approve(repo: Path, commit: Commit) -> None:
    commit("subject\n\nGolden-Approved-By:", {"tests/golden/a.json": "{}"})

    assert len(golden_guard.check_range("HEAD", base=None, cwd=repo)) == 1


def test_trailer_key_is_case_insensitive(repo: Path, commit: Commit) -> None:
    commit("subject\n\ngolden-approved-by: maintainer", {"tests/golden/a.json": "{}"})

    assert golden_guard.check_range("HEAD", base=None, cwd=repo) == []


def test_zero_base_falls_back_to_merge_base(repo: Path, commit: Commit) -> None:
    commit("add golden", {"tests/golden/a.json": "{}"})

    found = golden_guard.check_range("HEAD", base="0" * 40, cwd=repo)

    assert len(found) == 1


def test_explicit_base_checks_commits_on_the_default_branch(repo: Path, commit: Commit) -> None:
    git(repo, "switch", "--quiet", "main")
    before = git(repo, "rev-parse", "HEAD")
    sha = commit("pushed to main", {"tests/golden/a.json": "{}"})

    assert golden_guard.check_range("HEAD", base=None, cwd=repo) == []
    assert [v.commit for v in golden_guard.check_range("HEAD", base=before, cwd=repo)] == [sha]


def test_unknown_base_on_default_branch_fails_closed(repo: Path, commit: Commit) -> None:
    git(repo, "switch", "--quiet", "main")
    commit("pushed to main", {"tests/golden/a.json": "{}"})

    with pytest.raises(GuardError, match="fetch-depth: 0"):
        golden_guard.check_range("HEAD", base="deadbeef" * 5, cwd=repo)


def test_unknown_base_on_branch_uses_merge_base(repo: Path, commit: Commit) -> None:
    commit("add golden", {"tests/golden/a.json": "{}"})

    found = golden_guard.check_range("HEAD", base="deadbeef" * 5, cwd=repo)

    assert len(found) == 1


def test_unpushed_commits_on_main_are_checked(repo: Path, commit: Commit) -> None:
    git(repo, "switch", "--quiet", "main")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    sha = commit("local only", {"tests/golden/a.json": "{}"})

    found = golden_guard.check_range("HEAD", base=None, cwd=repo)

    assert [v.commit for v in found] == [sha]


def test_no_default_branch_and_no_base_is_an_error(tmp_path: Path) -> None:
    repo = tmp_path / "lonely"
    repo.mkdir()
    git(repo, "init", "--quiet", "--initial-branch=trunk")
    git(repo, "commit", "--quiet", "--allow-empty", "-m", "root")

    with pytest.raises(GuardError, match="--base"):
        golden_guard.check_range("HEAD", base=None, cwd=repo)


def test_commit_message_without_trailer_fails(repo: Path) -> None:
    (repo / "tests" / "golden").mkdir(parents=True)
    (repo / "tests" / "golden" / "a.json").write_text("{}", encoding="utf-8")
    git(repo, "add", "tests/golden/a.json")
    message = repo / "MSG"
    message.write_text("add golden\n\n# Please enter the commit message\n", encoding="utf-8")

    found = golden_guard.check_commit_message(message, cwd=repo)

    assert found == Violation("(staged)", "add golden", ("tests/golden/a.json",))


def test_commit_message_with_trailer_and_comments_passes(repo: Path) -> None:
    (repo / "tests" / "golden").mkdir(parents=True)
    (repo / "tests" / "golden" / "a.json").write_text("{}", encoding="utf-8")
    git(repo, "add", "tests/golden/a.json")
    message = repo / "MSG"
    text = "add golden\n\nGolden-Approved-By: maintainer\n# Please enter the commit message\n#\n"
    message.write_text(text, encoding="utf-8")

    assert golden_guard.check_commit_message(message, cwd=repo) is None


def test_commit_message_without_golden_change_passes(repo: Path) -> None:
    (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "code.py")
    message = repo / "MSG"
    message.write_text("code\n", encoding="utf-8")

    assert golden_guard.check_commit_message(message, cwd=repo) is None


def test_cli_range_reports_violation(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    commit("add golden", {"tests/golden/a.json": "{}"})

    code = golden_guard.main(["range"])

    out = capsys.readouterr().out
    assert code == 1
    assert "add golden" in out
    assert "tests/golden/a.json" in out
    assert "Golden-Approved-By" in out


def test_cli_range_reads_base_from_environment(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repo, "switch", "--quiet", "main")
    monkeypatch.chdir(repo)
    monkeypatch.setenv("GOLDEN_BASE", git(repo, "rev-parse", "HEAD"))
    commit("pushed to main", {"tests/golden/a.json": "{}"})

    assert golden_guard.main(["range"]) == 1


def test_cli_range_lists_approved_commits(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    commit("add golden" + APPROVED, {"tests/golden/a.json": "{}"})

    code = golden_guard.main(["range"])

    out = capsys.readouterr().out
    assert code == 0
    assert "approved by maintainer: add golden" in out


def test_cli_range_notes_uncommitted_golden_changes(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    (repo / "tests" / "golden").mkdir(parents=True)
    (repo / "tests" / "golden" / "new.json").write_text("{}", encoding="utf-8")

    code = golden_guard.main(["range"])

    assert code == 0
    assert "uncommitted" in capsys.readouterr().out


def test_cli_history_error_exits_2(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repo, "switch", "--quiet", "main")
    monkeypatch.chdir(repo)
    commit("pushed to main", {"tests/golden/a.json": "{}"})

    assert golden_guard.main(["range", "--base", "deadbeef" * 5]) == 2


def test_cli_commit_msg(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(repo)
    (repo / "tests" / "golden").mkdir(parents=True)
    (repo / "tests" / "golden" / "a.json").write_text("{}", encoding="utf-8")
    git(repo, "add", "tests/golden/a.json")
    message = repo / "MSG"
    message.write_text("add golden\n", encoding="utf-8")

    assert golden_guard.main(["commit-msg", str(message)]) == 1


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (".github/workflows/ci.yml", True),
        (".pre-commit-config.yaml", True),
        (".claude/settings.json", True),
        ("AGENTS.md", True),
        ("pyproject.toml", True),
        ("scripts/check.py", True),
        ("Scripts/Check.py", True),
        ("scripts/golden_guard.py", True),
        ("scripts/golden_probe.py", True),
        ("scripts/hooks/guard.py", True),
        ("tests/golden/a.json", True),
        ("scripts/check_licenses.py", False),
        ("scripts/legacy_env.py", False),
        ("src/sportorg_ng/core/version.py", False),
        ("docs/AGENTS.md", False),
    ],
)
def test_is_protected(path: str, *, expected: bool) -> None:
    assert golden_guard.is_protected(path) is expected


def test_protected_changes_since_main(repo: Path, commit: Commit) -> None:
    commit("ci", {".github/workflows/ci.yml": "on: push\n", "src/a.py": "x = 1\n"})
    commit("config", {"pyproject.toml": "[project]\n"})

    assert golden_guard.protected_changes("HEAD", base=None, cwd=repo) == [
        ".github/workflows/ci.yml",
        "pyproject.toml",
    ]


def test_cli_protected_lists_files_and_review_command(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    monkeypatch.delenv("PRE_COMMIT_TO_REF", raising=False)
    commit("ci", {".github/workflows/ci.yml": "on: push\n"})

    code = golden_guard.main(["protected"])

    out = capsys.readouterr().out
    assert code == 0
    assert "  .github/workflows/ci.yml" in out
    assert "git diff " in out


def test_cli_protected_without_changes(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    monkeypatch.delenv("PRE_COMMIT_TO_REF", raising=False)
    commit("code", {"src/a.py": "x = 1\n"})

    assert golden_guard.main(["protected"]) == 0
    assert "no protected files changed" in capsys.readouterr().out


def test_cli_head_comes_from_the_pushed_ref(
    repo: Path, commit: Commit, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    git(repo, "switch", "--quiet", "-c", "other", "main")
    commit("ci", {".github/workflows/ci.yml": "on: push\n"})
    other = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "--quiet", "work")
    monkeypatch.chdir(repo)
    monkeypatch.delenv("GOLDEN_BASE", raising=False)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", other)

    assert golden_guard.main(["protected"]) == 0
    assert ".github/workflows/ci.yml" in capsys.readouterr().out


def test_cli_deleting_a_remote_ref_checks_nothing(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(repo)
    monkeypatch.setenv("PRE_COMMIT_TO_REF", "0" * 40)

    assert golden_guard.main(["protected"]) == 0
    assert golden_guard.main(["range"]) == 0
    assert "deleting" in capsys.readouterr().out
