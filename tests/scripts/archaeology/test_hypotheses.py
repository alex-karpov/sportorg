"""Tests for scripts/archaeology/hypotheses.py on synthetic snapshots (no legacy data)."""

from __future__ import annotations

from scripts.archaeology import hypotheses as h
from scripts.archaeology.common import Commit, FileChange

MEMORY = "sportorg/models/memory.py"


def _commit(sha: str, *paths: str, merge: bool = False) -> Commit:
    parents = ("p1", "p2") if merge else ("p1",)
    return Commit(sha, parents, "2026-01-01", "s", tuple(FileChange(p, 1, 1) for p in paths))


def _snapshot(
    py: dict[str, str], log: list[Commit] | None = None, extra: tuple[str, ...] = ()
) -> h.Snapshot:
    return h.Snapshot(py=py, texts={}, log=log or [], tracked=sorted([*py, *extra]))


def test_verdict_partly_when_one_part_fails() -> None:
    memory = "\n".join(f"x{i} = {i}" for i in range(2910)) + "\n"
    log = [
        _commit("a", "README.md"),
        _commit("b", "README.md"),
        _commit("c", MEMORY),
        _commit("d", MEMORY, "README.md", merge=True),
    ]
    snap = _snapshot({MEMORY: memory}, log, ("README.md",))
    verdict = h.h1_memory(snap)
    assert verdict.numbers["lines"] == 2910
    assert verdict.numbers["commits"] == 1
    assert verdict.numbers["rank_by_commits"] == 2
    assert verdict.numbers["top_by_commits"] == "README.md"
    assert verdict.verdict == "partly"


def test_h2_counts_local_and_module_imports() -> None:
    py = {
        MEMORY: "def race(): ...\n",
        "sportorg/a.py": "from sportorg.models.memory import race\nrace()\n",
        "sportorg/gui/b.py": "def f():\n    from ..models.memory import race, Person\n",
        "sportorg/c.py": "from sportorg.models import memory\nmemory.race()\n",
        "sportorg/d.py": "from sportorg.models.memory import Person\n",
        "tests/t.py": "from sportorg.models.memory import race\n",
    }
    verdict = h.h2_race(_snapshot(py))
    assert verdict.numbers["files_using_race"] == 4
    assert verdict.numbers["files_using_race_in_sportorg"] == 3
    assert verdict.numbers["files_calling_race"] == 2
    assert verdict.verdict == "refuted"


def test_h3_flags_qt_import_outside_gui() -> None:
    py = {
        "sportorg/gui/main.py": "from PySide6.QtWidgets import QWidget\n",
        "sportorg/models/result/score.py": "def f():\n    from sportorg.gui.main import App\n",
        "sportorg/modules/x.py": "from PySide6.QtCore import QThread\n",
        "sportorg/startup.py": "from sportorg.gui.main import Application\n",
    }
    verdict = h.h3_gui(_snapshot(py))
    assert verdict.numbers["modules_outside_gui"] == 2
    assert verdict.numbers["result_generation_modules"] == 1
    assert verdict.numbers["local_edges"] == 1
    assert verdict.verdict == "confirmed"


def test_h3_separates_qtcore_from_widgets_and_gui_package() -> None:
    py = {
        "sportorg/modules/reader.py": "from PySide6.QtCore import QThread, Signal\n",
        "sportorg/utils/time.py": "from PySide6 import QtCore\nfrom PySide6.QtCore import QDate\n",
        "sportorg/modules/printing.py": (
            "from PySide6.QtCore import QSizeF\nfrom PySide6.QtGui import QTextDocument\n"
        ),
        "sportorg/modules/wdb.py": "from PySide6 import QtCore, QtWidgets\n",
        "sportorg/modules/result.py": "from sportorg.gui.global_access import GlobalAccess\n",
    }
    numbers = h.h3_gui(_snapshot(py)).numbers
    assert numbers["edges"] == 7
    assert numbers["modules_qtcore_only"] == 2
    assert numbers["edges_qtcore_only"] == 4
    assert numbers["modules_ui"] == 3
    assert numbers["edges_ui"] == 3
    assert numbers["modules_gui_package"] == 1
    assert numbers["edges_gui_package"] == 1


def test_h4_finds_system_bound_result_classes_and_branches() -> None:
    memory = (
        "class SystemType(Enum):\n    NONE = 0\n    MANUAL = 1\n    SPORTIDENT = 2\n"
        "class Result(ABC):\n"
        "    def is_sportident(self):\n        return self.system_type == SystemType.SPORTIDENT\n"
        "class ResultManual(Result):\n    system_type = SystemType.MANUAL\n"
        "class ResultSportident(Result):\n    system_type = SystemType.SPORTIDENT\n"
        "class ResultSFR(ResultSportident):\n    pass\n"
    )
    other = (
        "def f(r):\n    if r.is_sportident():\n        pass\n"
        "    if isinstance(r, ResultManual):\n        pass\n"
        "    return r.system_type == SystemType.MANUAL\n"
    )
    verdict = h.h4_system_type(_snapshot({MEMORY: memory, "sportorg/gui/x.py": other}))
    assert verdict.numbers["result_subclasses"] == 3
    assert verdict.numbers["subclasses_with_system_type"] == 2
    assert verdict.numbers["branches_outside_memory"] == 3
    assert verdict.verdict == "confirmed"


def test_h5_reports_definition_layer() -> None:
    py = {
        MEMORY: "class Qualification(IntEnum):\n    NOT_QUALIFIED = 0\n    KMS = 7\n",
        "sportorg/gui/q.py": "from sportorg.models.memory import Qualification\n",
    }
    verdict = h.h5_qualification(_snapshot(py))
    assert verdict.numbers["defined_in"] == "sportorg.models.memory"
    assert verdict.numbers["layer"] == "domain"
    assert verdict.numbers["members"] == "NOT_QUALIFIED, KMS"
    assert verdict.numbers["referencing_files_ui"] == 1
    assert verdict.verdict == "confirmed"


PYPROJECT = """
[project]
requires-python = ">=3.8.1,<=3.14"
dependencies = ["orjson>=3.9.5,<4", "cryptography>=46", "x; python_version == '3.8'"]
[project.optional-dependencies]
gui = ["PySide6>=6,<7"]
"""
LOCK = """
version = 1
[[package]]
name = "orjson"
version = "3.10.15"
resolution-markers = ["python_full_version < '3.9'"]
[[package]]
name = "orjson"
version = "3.11.3"
[[package]]
name = "cryptography"
version = "46.0.6"
[[package]]
name = "pyside6"
version = "6.6.3.1"
"""
CONTRIBUTING = """
| Dependency   | Last version that runs on Windows 7 | First broken version |
|--------------|-------------------------------------|----------------------|
| orjson       | `3.10.13`                           | `3.10.14`            |
| cryptography | `42.0.8`                            | `43.0.3`             |
"""


def test_h6_reads_markers_and_lock_versions() -> None:
    fallback = "try:\n    import PySide6\nexcept ImportError:\n    import PySide2\n"
    py = {"sportorg/gui/a.py": fallback}
    snap = h.Snapshot(
        py=py,
        texts={"pyproject.toml": PYPROJECT, "uv.lock": LOCK, "CONTRIBUTING.md": CONTRIBUTING},
        log=[],
        tracked=sorted([*py, "pyproject.toml", "uv.lock", "CONTRIBUTING.md"]),
    )
    verdict = h.h6_windows7(snap)
    assert verdict.numbers["requires_python"] == ">=3.8.1,<=3.14"
    assert verdict.numbers["py38_markers"] == 1
    assert verdict.numbers["lock_orjson"] == "3.10.15, 3.11.3"
    assert verdict.numbers["lock_cryptography"] == "46.0.6"
    assert verdict.numbers["files_importing_pyside2"] == 1
    assert ("sportorg/gui/a.py", 4) in {(loc.path, loc.line) for loc in verdict.sources}
    assert verdict.numbers["lock_within_win7_limits"] == 0
    assert verdict.numbers["win7_mentions"] == 1
    assert verdict.verdict == "partly"


def test_h2_verdict_uses_the_sportorg_scope() -> None:
    py = {MEMORY: "def race(): ...\n"}
    py |= {f"sportorg/m{i}.py": "from sportorg.models.memory import race\n" for i in range(62)}
    py |= {f"tests/t{i}.py": "from sportorg.models.memory import race\n" for i in range(16)}
    verdict = h.h2_race(_snapshot(py))
    assert verdict.numbers["files_using_race"] == 78
    assert verdict.numbers["files_using_race_in_sportorg"] == 62
    assert verdict.verdict == "confirmed"
    assert "мейнтейнер: 2026-10-25" in verdict.definition
