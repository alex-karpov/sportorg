"""Tests for scripts/archaeology/common.py on synthetic repositories and sources."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import legacy
from scripts.archaeology import common
from scripts.archaeology.common import FileChange, ImportRef, Loc, UnparsedError
from tests.scripts.archaeology.conftest import IDENTITY

if TYPE_CHECKING:
    from pathlib import Path

    from tests.scripts.archaeology.conftest import Commit


def test_loc_tag_single_and_range() -> None:
    assert Loc("pysport", "sportorg/x.py", 12).tag() == "[код: pysport@b548c35 sportorg/x.py:12]"
    tag = Loc("pysport", "sportorg/x.py", 12, 15).tag()
    assert tag == "[код: pysport@b548c35 sportorg/x.py:12-15]"
    assert Loc("templates", "ru/a b.html", 3).tag() == "[код: templates@cd95382 ru/a b.html:3]"


def test_parse_tags_roundtrip() -> None:
    locs = [Loc("pysport", "sportorg/x.py", 12), Loc("templates", "ru/a b.html", 3, 9)]
    text = f"see {locs[0].tag()} and {locs[1].tag()}; [допущение] [история: pysport@abc1234]"
    assert common.parse_tags(text) == locs


def test_parse_tags_rejects_a_foreign_pin() -> None:
    with pytest.raises(ValueError, match="1234567"):
        common.parse_tags("[код: pysport@1234567 sportorg/x.py:1]")


def test_parse_git_log_basic(repo: Path, commit: Commit) -> None:
    first = commit("feat: one", {"a.py": b"1\n2\n"})
    second = commit("fix: two", {"a.py": b"1\n3\n", "b.py": b"x\n"})
    log = common.git_log(repo)
    assert [c.sha for c in log] == [second, first]
    assert log[0].parents == (first,)
    assert log[1].parents == ()
    assert log[0].subject == "fix: two"
    assert log[0].files == (FileChange("a.py", 1, 1), FileChange("b.py", 1, 0))
    assert len(log[0].date) == len("2026-10-25")


def test_parse_git_log_cyrillic_path_and_subject(repo: Path, commit: Commit) -> None:
    commit("исправлена «ошибка» в протоколе", {"шаблоны/итог 1.html": b"<p>\n"})
    (only,) = common.git_log(repo)
    assert only.subject == "исправлена «ошибка» в протоколе"
    assert only.files == (FileChange("шаблоны/итог 1.html", 1, 0),)
    assert common.tracked_files(repo) == ["шаблоны/итог 1.html"]


def test_parse_git_log_binary_and_empty(repo: Path, commit: Commit) -> None:
    base = commit("binary", {"logo.png": b"\x00\x01\x02"})
    commit("empty", {})
    legacy.git("switch", "--quiet", "-c", "side", base, cwd=repo)
    commit("side", {"s.txt": b"s\n"})
    legacy.git("switch", "--quiet", "main", cwd=repo)
    legacy.git(*IDENTITY, "merge", "--quiet", "--no-ff", "--no-edit", "side", cwd=repo)
    by_subject = {c.subject: c for c in common.git_log(repo)}
    assert by_subject["binary"].files == (FileChange("logo.png", None, None),)
    assert by_subject["empty"].files == ()
    merge = by_subject["Merge branch 'side'"]
    assert merge.is_merge
    assert merge.files == ()
    assert not by_subject["side"].is_merge


def test_tracked_files_pattern_sorted(repo: Path, commit: Commit) -> None:
    commit("files", {"b.py": b"", "a.py": b"", "pkg/c.py": b"", "d.txt": b""})
    assert common.tracked_files(repo, "*.py") == ["a.py", "b.py", "pkg/c.py"]


@pytest.mark.parametrize(
    ("path", "module"),
    [
        ("sportorg/models/result/result_checker.py", "sportorg.models.result"),
        ("sportorg/models/memory.py", "sportorg.models"),
        ("sportorg/config.py", "sportorg"),
        ("sportorg/libs/iof/v3/parser.py", "sportorg.libs.iof"),
        ("crates/sportorg-core/src/lib.rs", "crates.sportorg-core"),
        ("tests/test_x.py", "tests"),
        ("README.md", "other"),
    ],
)
def test_module_of(path: str, module: str) -> None:
    assert common.module_of(path) == module


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("sportorg/models/memory.py", ("sportorg.models.memory", False)),
        ("sportorg/models/__init__.py", ("sportorg.models", True)),
        ("sportorg/__init__.py", ("sportorg", True)),
    ],
)
def test_module_name(path: str, expected: tuple[str, bool]) -> None:
    assert common.module_name(path) == expected


@pytest.mark.parametrize(
    ("module", "layer"),
    [
        ("sportorg.startup", (5, "entry")),
        ("sportorg.gui.main_window", (4, "ui")),
        ("sportorg.modules.iof.iof", (3, "application")),
        ("sportorg.rust_example", (3, "application")),
        ("sportorg.models.memory", (2, "domain")),
        ("sportorg", (1, "foundation")),
        ("sportorg.common.otime", (1, "foundation")),
        ("sportorg.config", (1, "foundation")),
        ("sportorg.libs.iof.parser", (0, "vendored")),
        ("sportorg.guinea", (-1, "outside")),
        ("PySide6.QtCore", (-1, "outside")),
    ],
)
def test_layer_of(module: str, layer: tuple[int, str]) -> None:
    assert common.layer_of(module) == layer


def test_iter_imports_relative_and_local() -> None:
    source = (
        "import os, sportorg.models.memory as mem\n"
        "from . import otime\n"
        "def f():\n"
        "    from ..models import memory, result\n"
        "class C:\n"
        "    from .x import y\n"
    )
    refs = common.iter_imports(source, "sportorg.common.broker")
    assert refs == [
        ImportRef("os", (), 1, local=False),
        ImportRef("sportorg.models.memory", (), 1, local=False),
        ImportRef("sportorg.common", ("otime",), 2, local=False),
        ImportRef("sportorg.models", ("memory", "result"), 4, local=True),
        ImportRef("sportorg.common.x", ("y",), 6, local=False),
    ]


def test_iter_imports_relative_in_package() -> None:
    refs = common.iter_imports("from .memory import race\n", "sportorg.models", is_package=True)
    assert refs == [ImportRef("sportorg.models.memory", ("race",), 1, local=False)]


def test_iter_imports_reports_syntax_error() -> None:
    with pytest.raises(UnparsedError) as caught:
        common.iter_imports("def broken(:\n", "m", path="sportorg/broken.py")
    assert caught.value.path == "sportorg/broken.py"
    assert "line 1" in caught.value.reason


def test_write_outputs_is_deterministic(tmp_path: Path) -> None:
    one, two = tmp_path / "one", tmp_path / "two"
    common.write_outputs(one, "x", {"b": 1, "a": {"d": "ёжик", "c": [2, 1]}}, "| a |\n", "# X")
    common.write_outputs(two, "x", {"a": {"c": [2, 1], "d": "ёжик"}, "b": 1}, "| a |\n", "# X")
    assert (one / "x.json").read_bytes() == (two / "x.json").read_bytes()
    assert (one / "x.md").read_bytes() == (two / "x.md").read_bytes()
    assert (one / "x.json").read_text(encoding="utf-8").startswith('{\n "a": {\n  "c": [\n')
    assert "ёжик" in (one / "x.json").read_text(encoding="utf-8")
    assert (one / "x.md").read_bytes() == b"# X\n\n| a |\n"


def test_run_leaves_tree_clean(repo: Path, commit: Commit) -> None:
    commit("one", {"a.py": b"x = 1\n", ".gitignore": b"__pycache__/\n"})
    common.assert_tree_clean(repo)
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "a.cpython-314.pyc").write_bytes(b"")
    with pytest.raises(common.TreeNotCleanError, match="__pycache__"):
        common.assert_tree_clean(repo)


def test_parse_source_records_syntax_warnings() -> None:
    source = 'x = "\\`"\nimport os\n'
    _, warnings = common.parse_source(source, "sportorg/w.py")
    assert len(warnings) == 1
    assert warnings[0].startswith("sportorg/w.py:1: ")
    assert "invalid escape sequence" in warnings[0]
    assert common.iter_imports(source, "m") == [ImportRef("os", (), 2, local=False)]
