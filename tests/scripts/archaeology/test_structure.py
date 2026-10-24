"""Tests for scripts/archaeology/structure.py on synthetic sources (no legacy data, no network)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.archaeology import structure as s
from scripts.archaeology.common import Commit, FileChange, layer_of

if TYPE_CHECKING:
    from scripts._json import Json


def _commit(sha: str, *paths: str, merge: bool = False) -> Commit:
    parents = ("p1", "p2") if merge else ("p1",)
    return Commit(sha, parents, "2026-01-01", "s", tuple(FileChange(p, 1, 1) for p in paths))


def test_sloc_ignores_comments_and_blank_lines() -> None:
    source = (
        "# header comment\n"
        "\n"
        "import os  # trailing comment\n"
        "def f(a,\n"
        "      b):\n"
        '    """Doc\n'
        "    string.\n"
        '    """\n'
        "    # inner comment\n"
        "    return a\n"
        "\n"
    )
    assert s.sloc(source) == 7


def test_sloc_falls_back_on_tokenize_error() -> None:
    assert s.sloc("x = (1,\n# c\n\ny = 2\n") == 2


def test_hotspot_score_and_ranking() -> None:
    py = {
        "sportorg/a.py": "def f(x):\n    if x:\n        return 1\n    return 2\n",
        "sportorg/b.py": "def g():\n    return 1\n",
        "sportorg/c.py": "X = 1\n",
    }
    log = [
        _commit("1", "sportorg/a.py", "sportorg/b.py"),
        _commit("2", "sportorg/a.py", "sportorg/c.py"),
        _commit("3", "sportorg/b.py", "README.md"),
        _commit("4", "sportorg/a.py", "sportorg/b.py", merge=True),
    ]
    complexity = {
        ("sportorg/a.py", 1): ("f", 2),
        ("sportorg/b.py", 1): ("g", 1),
        ("sportorg/b.py", 9): ("h", 4),
    }
    rows = s.hotspot_rows(py, log, complexity)
    assert [r.path for r in rows] == ["sportorg/b.py", "sportorg/a.py", "sportorg/c.py"]
    b, a, c = rows
    assert (b.commits, b.total_cc, b.max_cc, b.max_func, b.max_line, b.score) == (
        2, 5, 4, "h", 9, 10,
    )  # fmt: skip
    assert (a.commits, a.total_cc, a.score, a.sloc, a.functions) == (2, 2, 4, 4, 1)
    assert (c.commits, c.total_cc, c.score, c.max_line) == (1, 0, 0, 1)
    assert [r.rank for r in rows] == [1, 2, 3]


def test_hotspot_ties_break_by_commits_then_path() -> None:
    py = {"sportorg/z.py": "def f(): ...\n", "sportorg/y.py": "def g(): ...\n"}
    log = [_commit("1", "sportorg/z.py", "sportorg/y.py")]
    complexity = {("sportorg/z.py", 1): ("f", 1), ("sportorg/y.py", 1): ("g", 1)}
    assert [r.path for r in s.hotspot_rows(py, log, complexity)] == [
        "sportorg/y.py",
        "sportorg/z.py",
    ]


def test_extract_edges_flag_local_and_resolve_relative() -> None:
    py = {
        "sportorg/__init__.py": "",
        "sportorg/models/__init__.py": "",
        "sportorg/models/memory.py": "X = 1\n",
        "sportorg/gui/__init__.py": "",
        "sportorg/gui/main.py": (
            "from ..models import memory\n"
            "import os\n"
            "def f():\n"
            "    from sportorg.models.memory import X\n"
        ),
    }
    ex = s.extract(py)
    edges = sorted((e.src, e.dst, e.line, e.local) for e in ex.edges)
    assert edges == [
        ("sportorg.gui.main", "sportorg.models.memory", 1, False),
        ("sportorg.gui.main", "sportorg.models.memory", 4, True),
    ]
    assert [(x.root, x.line) for x in ex.externals] == [("os", 2)]


def test_extract_reports_unparsed_and_syntax_warnings() -> None:
    py = {
        "sportorg/ok.py": 's = "\\d"\n',
        "sportorg/bad.py": "def (:\n",
    }
    ex = s.extract(py)
    assert [(w.path, w.line) for w in ex.warnings] == [("sportorg/ok.py", 1)]
    assert "escape sequence" in ex.warnings[0].message
    assert [u.path for u in ex.unparsed] == ["sportorg/bad.py"]


def test_violation_kinds_v1_v2_v3() -> None:
    py = {
        "sportorg/__init__.py": "",
        "sportorg/startup.py": "from sportorg.gui import main\n",
        "sportorg/gui/__init__.py": "",
        "sportorg/gui/main.py": "X = 1\n",
        "sportorg/modules/__init__.py": "",
        "sportorg/modules/run.py": "def f():\n    from sportorg.gui import main\n",
        "sportorg/models/__init__.py": "",
        "sportorg/models/memory.py": "import serial.tools\nfrom PySide6 import QtCore\n",
        "sportorg/common/__init__.py": "",
        "sportorg/common/otime.py": (
            "import win32api\nimport os\nfrom sportorg.models import memory\n"
        ),
        "sportorg/libs/__init__.py": "",
        "sportorg/libs/a/__init__.py": "",
        "sportorg/libs/a/x.py": "from sportorg.libs.a import y\nfrom sportorg.libs.b import z\n",
        "sportorg/libs/a/y.py": "from sportorg.common import otime\nimport requests\n",
        "sportorg/libs/b/__init__.py": "",
        "sportorg/libs/b/z.py": "X = 1\n",
        "sportorg/gui/other.py": "import requests\n",
    }
    found = s.find_violations(s.extract(py))
    got = sorted((v.kind, v.src, v.dst, v.line, v.local) for v in found)
    assert got == [
        ("V1", "sportorg.common.otime", "sportorg.models.memory", 3, False),
        ("V1", "sportorg.libs.a.y", "sportorg.common.otime", 1, False),
        ("V1", "sportorg.modules.run", "sportorg.gui.main", 2, True),
        ("V2", "sportorg.libs.a.x", "sportorg.libs.b.z", 2, False),
        ("V2", "sportorg.libs.a.y", "sportorg.common.otime", 1, False),
        ("V3", "sportorg.common.otime", "win32api", 1, False),
        ("V3", "sportorg.libs.a.y", "requests", 2, False),
        ("V3", "sportorg.models.memory", "PySide6", 2, False),
        ("V3", "sportorg.models.memory", "serial.tools", 1, False),
    ]
    layers = {(v.kind, v.src_layer, v.dst_layer) for v in found if v.src == "sportorg.modules.run"}
    assert layers == {("V1", "application", "ui")}
    counts = s.violation_counts(found)
    assert counts["V1"] == {"module_level": 2, "local": 1}
    assert counts["V2"] == {"module_level": 2, "local": 0}
    assert counts["V3"] == {"module_level": 4, "local": 0}


def test_v3_matches_win32_prefix_but_not_stdlib() -> None:
    assert s.io_library("win32com.client") is not None
    assert s.io_library("pywintypes") is not None
    assert s.io_library("PySide6.QtWidgets") is not None
    assert s.io_library("socket") is not None
    assert s.io_library("os") is None
    assert s.io_library("win32") is not None
    assert s.io_library("win32extra") is not None
    assert s.io_library("winreg") is not None
    assert s.io_library("sportorg.x") is None


def test_layers_contract_lists_only_existing_modules() -> None:
    modules = {
        "sportorg",
        "sportorg.startup",
        "sportorg.gui.main",
        "sportorg.modules.x",
        "sportorg.models.memory",
        "sportorg.common.otime",
        "sportorg.config",
        "sportorg.libs.a.x",
    }
    text = s.layers_contract(modules)
    assert "root_package = sportorg\n" in text
    lines = [line.strip() for line in text.splitlines()]
    layer_lines = lines[lines.index("layers =") + 1 :]
    assert layer_lines == [
        "sportorg.startup",
        "sportorg.gui",
        "sportorg.modules",
        "sportorg.models",
        "sportorg.common : sportorg.config",
        "sportorg.libs",
    ]


def test_parse_lint_imports_output_joins_wrapped_lines() -> None:
    text = (
        "sportorg.modules is not allowed to import sportorg.gui:\n\n"
        "- sportorg.modules.sportident.result_generation -> \n"
        "sportorg.gui.dialogs.bib_dialog (l.7)\n\n"
        "- sportorg.libs.sfr.sfrximporter -> sportorg.models.memory (l.6, l.7)\n\n"
        "- sportorg.models.a -> sportorg.models.b (l.1) sportorg.models.b -> sportorg.gui.c (l.2)\n"
    )
    deps = s.parse_lint_imports(text)
    assert [(d.importer, d.imported, d.hops, d.lines) for d in deps] == [
        (
            "sportorg.modules.sportident.result_generation",
            "sportorg.gui.dialogs.bib_dialog",
            1,
            (7,),
        ),
        ("sportorg.libs.sfr.sfrximporter", "sportorg.models.memory", 1, (6, 7)),
        ("sportorg.models.a", "sportorg.gui.c", 2, (1, 2)),
    ]


def test_name_in_string_flag() -> None:
    sources = [
        'MENU = [{"action": "NewAction"}]\nclass NewAction: ...\n',
        'def f():\n    """Mentions UsedOnlyInDocstring here."""\n    return "run_%s" % 1\n',
        "label = f'start {x} StartAction'\n",
    ]
    index = s.string_index(sources)
    assert index.is_string("NewAction")
    assert index.in_string("NewAction")
    assert not index.in_string("UsedOnlyInDocstring")
    assert index.in_string("StartAction")
    assert not index.is_string("StartAction")
    assert not index.in_string("Missing")
    findings: list[dict[str, Json]] = [
        {"path": "sportorg/a.py", "line": 2, "kind": "unused class", "name": "NewAction",
         "confidence": 60},
        {"path": "sportorg/a.py", "line": 5, "kind": "unused function", "name": "Missing",
         "confidence": 60},
    ]  # fmt: skip
    rows = s.dead_code_rows(findings, index)
    assert [(r.name, r.name_in_string, r.name_is_string) for r in rows] == [
        ("NewAction", True, True),
        ("Missing", False, False),
    ]
    assert rows[0].tag.startswith("[код: pysport@")


def test_name_flags_are_false_for_nameless_findings() -> None:
    index = s.string_index(['x = "if"\n'])
    findings: list[dict[str, Json]] = [
        {"path": "sportorg/a.py", "line": 1, "kind": "unreachable code", "name": "if",
         "confidence": 100},
    ]  # fmt: skip
    (row,) = s.dead_code_rows(findings, index)
    assert (row.name_in_string, row.name_is_string) == (False, False)


def test_rust_rows_per_file_and_crate() -> None:
    tracked = [
        "Cargo.lock",
        "Cargo.toml",
        "crates/core/Cargo.toml",
        "crates/core/src/lib.rs",
        "crates/core/src/time.rs",
        "sportorg/a.py",
    ]
    texts = {
        "Cargo.lock": "a\nb\n",
        "Cargo.toml": "[workspace]\n",
        "crates/core/Cargo.toml": "[package]\nname = 'core'\n",
        "crates/core/src/lib.rs": "mod time;\n\nfn f() {}\n",
        "crates/core/src/time.rs": "fn t() {}\n",
    }
    log = [
        _commit("1", "crates/core/src/lib.rs", "crates/core/src/time.rs", "sportorg/a.py"),
        _commit("2", "crates/core/src/lib.rs", "Cargo.lock"),
        _commit("3", "crates/core/src/lib.rs", merge=True),
    ]
    files, crates = s.rust_rows(tracked, texts, log)
    assert [(f.path, f.kind, f.lines, f.commits) for f in files] == [
        ("Cargo.lock", "cargo-lock", 2, 1),
        ("Cargo.toml", "cargo-toml", 1, 0),
        ("crates/core/Cargo.toml", "cargo-toml", 2, 0),
        ("crates/core/src/lib.rs", "rust", 3, 2),
        ("crates/core/src/time.rs", "rust", 1, 1),
    ]
    by_crate = {c.crate: c for c in crates}
    assert by_crate["crates.core"].rust_lines == 4
    assert by_crate["crates.core"].commits == 2  # distinct commits touching the crate
    assert by_crate["crates.core"].files == 3
    assert by_crate["workspace"].files == 2


def test_spearman_of_hotspots() -> None:
    py = {f"sportorg/f{i}.py": f"def f{i}():\n    pass\n" for i in range(3)}
    log = [_commit("1", "sportorg/f1.py"), _commit("2", "sportorg/f2.py", "sportorg/f1.py")]
    complexity = {(f"sportorg/f{i}.py", 1): (f"f{i}", i + 1) for i in range(3)}
    rows = s.hotspot_rows(py, log, complexity)
    rho = s.commits_complexity_spearman(rows)
    assert rho["all_files"] is not None
    assert -1.0 <= rho["all_files"] <= 1.0
    assert rho["files_with_functions"] is not None


def test_contract_layers_agree_with_layer_of() -> None:
    for index, layer in enumerate(s.CONTRACT_LAYERS):
        assert {layer_of(prefix)[0] for prefix in layer} == {5 - index}
