"""Tests for scripts/archaeology/defects.py on synthetic data (no legacy, no network)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scripts.archaeology import defects as d
from scripts.archaeology.common import Commit, FileChange, git_log

if TYPE_CHECKING:
    from pathlib import Path

    from scripts._json import Json
    from tests.scripts.archaeology.conftest import Commit as CommitFactory


def _commit(subject: str, *files: tuple[str, int], merge: bool = False) -> Commit:
    parents = ("p1", "p2") if merge else ("p1",)
    changes = tuple(FileChange(path, lines, 0) for path, lines in files)
    return Commit("a" * 40, parents, "2026-01-01", subject, changes)


def test_is_fix_conventional_and_keyword() -> None:
    assert d.is_fix(_commit("fix(gui): crash on open"))
    assert d.is_fix(_commit("hotfix!: x"))
    assert d.is_fix(_commit("Fixed wrong place calculation"))
    assert d.is_fix(_commit("исправление ошибки"))
    assert d.is_fix(_commit("ci: fix building rust code"))
    assert not d.is_fix(_commit("add new dialog"))
    assert not d.is_fix(_commit("fix(x): merge", merge=True))


def test_feat_with_fix_word_is_not_fix() -> None:
    assert not d.is_fix(_commit("feat: fix various qualification names"))
    assert not d.is_fix(_commit("refactor(gui): fix index key type"))
    assert not d.is_fix(_commit("docs: fix imgs path"))
    assert d.is_fix(_commit("update: fix crash"))


def test_classify_single_keyword_class() -> None:
    assert d.classify(_commit("fix: wrong penalty", ("sportorg/gui/x.py", 5))) == "calc"
    assert d.classify(_commit("fix: midnight overflow", ("sportorg/gui/x.py", 5))) == "time"
    assert d.classify(_commit("fix: импорт файла", ("sportorg/gui/x.py", 5))) == "import-export"


def test_classify_falls_back_to_most_changed_module() -> None:
    # No keyword at all.
    files = (("sportorg/models/result/a.py", 30), ("sportorg/gui/b.py", 5))
    assert d.classify(_commit("fix: stuff", *files)) == "calc"
    # Two classes match the keywords (time and calc): fall back to the paths.
    commit = _commit("fix: time of result", ("sportorg/gui/dialogs/x.py", 9), ("tests/t.py", 1))
    assert d.classify(commit) == "ui"
    # Nothing maps.
    assert d.classify(_commit("fix: stuff", ("scripts/x.py", 3))) == "other"


def test_docs_only_is_not_product_defect() -> None:
    commit = _commit("fix: typo in readme", ("docs/a.md", 2), ("img/x.png", 0), ("README.md", 1))
    assert d.is_fix(commit)
    assert d.classify(commit) == d.DOCS_ONLY
    assert not d.is_product_defect(commit)
    assert d.is_product_defect(_commit("fix: crash", ("sportorg/gui/x.py", 2), ("README.md", 1)))


def test_ci_fix_is_platform_build() -> None:
    commit = _commit("ci: fix building rust code", (".github/workflows/x.yml", 4))
    assert d.classify(commit) == "platform-build"
    assert not d.is_product_defect(commit)
    assert d.classify(_commit("build: fix printing", ("pyproject.toml", 1))) == "platform-build"


def test_keyword_stems_are_word_starts() -> None:
    assert d.keyword_classes("thread already") == set()
    assert d.keyword_classes("reading cards") == {"device"}
    assert d.keyword_classes("circle") == set()
    assert d.keyword_classes("fix ci") == {"platform-build"}


def test_issue_rows_never_contain_titles() -> None:
    items: list[Json] = [
        {
            "number": 7,
            "state": "closed",
            "labels": [{"name": "bug"}, {"name": "github_actions"}],
            "title": "SECRET printing title",
            "body": "SECRET body",
            "user": {"login": "someone"},
            "created_at": "2024-03-01T10:00:00Z",
            "closed_at": "2025-01-01T00:00:00Z",
            "pull_request": {"merged_at": "2025-01-01T00:00:00Z"},
        },
        {
            "number": 8,
            "state": "open",
            "labels": [],
            "title": "SECRET wrong penalty",
            "created_at": "2023-03-01T10:00:00Z",
            "closed_at": None,
        },
        {
            "number": 9,
            "state": "open",
            "labels": [],
            "title": "hello",
            "created_at": "2022-01-01T00:00:00Z",
        },
    ]
    rows = d.issue_rows(items)
    text = json.dumps([r.as_json() for r in rows], ensure_ascii=False)
    assert "SECRET" not in text
    assert "someone" not in text
    assert [(r.number, r.is_pr, r.cls, r.source, r.merged) for r in rows] == [
        (7, True, "platform-build", "label", True),
        (8, False, "calc", "keyword", False),
        (9, False, "unclassified", "none", False),
    ]
    assert rows[0].created_year == 2024
    assert rows[0].closed_year == 2025


def test_old_app_layout_maps_to_current_modules() -> None:
    cases = {
        "sportorg/app/gui/dialogs/a.py": "sportorg/gui/dialogs/a.py",
        "sportorg/app/models/memory.py": "sportorg/models/memory.py",
        "sportorg/app/modules/backup/b.py": "sportorg/modules/backup/b.py",
        "sportorg/app/plugins/sportident/c.py": "sportorg/modules/sportident/c.py",
        "sportorg/app/controllers/dialogs/d.py": "sportorg/gui/dialogs/d.py",
        "sportorg/lib/ocad/e.py": "sportorg/libs/ocad/e.py",
        "sportorg/core/otime.py": "sportorg/common/otime.py",
        "sportorg/gui/menu/f.py": "sportorg/gui/menu/f.py",
        "app.py": "app.py",
    }
    for old, new in cases.items():
        assert d.normalise_path(old) == new
    commit = _commit("fix: stuff", ("sportorg/app/models/result/a.py", 5))
    assert d.classify(commit) == "calc"
    row = d.commit_row(commit)
    assert row.modules == ("sportorg.models.result",)
    assert row.files == (("sportorg/app/models/result/a.py", "sportorg.models.result"),)
    assert d.module_of_path("sportorg/app/gui/dialogs/x.py") == "sportorg.gui.dialogs"


def test_memory_functions_decide_class() -> None:
    diff = (
        "@@ -10,0 +11,2 @@ class Foo:\n"
        "@@ -40 +41 @@ def get_split_places(self, x):\n"
        "@@ -50 +51 @@ def helper(self):\n"
    )
    assert d.hunk_words(diff) == "foo get split places helper"
    assert d.memory_class(diff) == "calc"
    assert d.memory_class("@@ -1 +1 @@ class PersonRecovery(Model):\n") == "persistence"


def test_memory_functions_ambiguous_keeps_fallback() -> None:
    # "result" is calc, "save" is persistence: two classes, no decision.
    assert d.memory_class("@@ -1 +1 @@ def save_result(self):\n") is None
    assert d.memory_class("@@ -1 +1 @@ def helper(self):\n") is None
    assert d.memory_class("") is None


def test_memory_rule_reads_git_hunks(repo: Path, commit: CommitFactory) -> None:
    body = "x = 1\n\n\ndef helper():\n    return 1\n\n\ndef load_backup():\n    return 2\n"
    commit("init", {"sportorg/models/memory.py": body.encode()})
    commit(
        "fix: stuff", {"sportorg/models/memory.py": body.replace("return 2", "return 3").encode()}
    )
    fixes = git_log(repo, "HEAD~1..HEAD")
    assert d.decide(fixes[0], repo) == ("persistence", "memory-functions")
    assert d.decide(fixes[0], None) == (d.OTHER, "other")
    keyword = _commit("fix: wrong penalty", ("sportorg/models/memory.py", 1))
    assert d.decide(keyword, repo) == ("calc", "keyword")
    paths = _commit("fix: stuff", ("sportorg/gui/x.py", 1))
    assert d.decide(paths, repo) == ("ui", "path")
