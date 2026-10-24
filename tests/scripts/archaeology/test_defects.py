"""Tests for scripts/archaeology/defects.py on synthetic data (no legacy, no network)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scripts.archaeology import defects as d
from scripts.archaeology.common import Commit, FileChange

if TYPE_CHECKING:
    from scripts._json import Json


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
