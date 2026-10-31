"""Tests for scripts/golden_probe.py: the scenario matrix behind ADR-0008 and its facts.

The trailer column is the canary of AC #7: it runs on every OS in CI. The signed-manifest columns
need ``ssh-keygen -Y`` and are measured only by the evidence command.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts import golden_probe, legacy
from scripts.golden_probe import Raw

if TYPE_CHECKING:
    from pathlib import Path

IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")


def test_trailer_column_matches_expected(tmp_path: Path) -> None:
    rows = golden_probe.run_scenarios(tmp_path, mechanisms=("a_trailer",))

    assert {row.scenario: row.results["a_trailer"] for row in rows} == {
        "add": "detected",
        "modify": "detected",
        "delete": "detected",
        "rename_out": "detected",
        "evil_merge": "detected",
        "approved": "passed",
        "non_golden": "passed",
        "text_in_body": "detected",
        "forged": "passed",
    }


def test_expected_outcome_detects_every_unapproved_change() -> None:
    passed = {name for name, outcome in golden_probe.EXPECTED.items() if outcome == "passed"}

    assert passed == {"approved", "non_golden"}


def test_github_facts_from_raw_responses() -> None:
    raw = {
        "repo": Raw(0, '{"visibility": "public", "owner": {"type": "User"}}'),
        "collaborators": Raw(0, '[{"login": "someone"}]'),
        "rulesets": Raw(0, "[]"),
        "protection": Raw(1, '{"message": "Branch not protected", "status": "404"}'),
    }

    assert golden_probe.github_facts(raw) == {
        "visibility": "public",
        "owner_type": "User",
        "collaborators": 1,
        "rulesets": 0,
        "main_protected": False,
    }


def test_git_facts_counts_agent_commits(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    legacy.git("init", "--quiet", str(repo))
    messages = ["one", "two\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", "three"]
    for message in messages:
        legacy.git(*IDENTITY, "commit", "--quiet", "--allow-empty", "-m", message, cwd=repo)

    facts = golden_probe.git_facts(repo, rev="HEAD")

    assert facts == {
        "commits": 3,
        "signed_commits": 0,
        "authors": 1,
        "agent_commits": 1,
        "agent_commit_authors": 1,
    }


def test_canary_on_a_clone_of_this_repository(tmp_path: Path) -> None:
    result = golden_probe.run_canary(golden_probe.ROOT, tmp_path)

    assert result == {"without_trailer": 1, "with_trailer": 0}
