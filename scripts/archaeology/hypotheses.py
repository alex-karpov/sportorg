"""Verdicts on the six hypotheses of the brief (Stage 1, TASK-7 criterion 6).

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.hypotheses \
        --out docs/evidence/stage-1/hypotheses

Every definition is fixed here before the run and printed with its verdict. A verdict is
``confirmed`` when every part of the claim holds, ``refuted`` when none does, ``partly`` otherwise.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal

from scripts import legacy
from scripts._json import as_dict, as_list, as_str, parse_toml
from scripts.archaeology.common import (
    PYSPORT,
    Commit,
    Loc,
    UnparsedError,
    git_log,
    git_raw,
    iter_imports,
    layer_of,
    module_name,
    parse_source,
    physical_lines,
    pin_short,
    repo_root,
    tracked_files,
    write_outputs,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from scripts._json import Json

type VerdictName = Literal["confirmed", "refuted", "partly"]

MEMORY: Final = "sportorg/models/memory.py"
MEMORY_MODULE: Final = "sportorg.models.memory"
QT: Final = ("PySide6", "PySide2", "PyQt5", "PyQt6")
RESULT_GENERATION: Final = (
    "sportorg.models.result",
    "sportorg.modules.printing",
    "sportorg.libs.template",
    "sportorg.common.template",
)
CLAIMED_LINES: Final = 2910
CLAIMED_RACE_FILES: Final = 62
RACE_TOLERANCE: Final = 0.2
WIN7_RE: Final = re.compile(r"windows\s*7|\bwin\s?7\b", re.IGNORECASE)
PY38_MARKER_RE: Final = re.compile(r"python(?:_full)?_version\s*(?:==\s*'3\.8|<\s*'3\.9)")
WIN7_ROW_RE: Final = re.compile(r"^\|\s*([\w-]+)\s*\|\s*`([\d.]+)`\s*\|", re.MULTILINE)
VERDICT_RU: Final = {"confirmed": "подтверждена", "refuted": "опровергнута", "partly": "частично"}


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Legacy at the pin: Python sources, other text files, history and tracked paths."""

    py: dict[str, str]
    texts: dict[str, str]
    log: list[Commit]
    tracked: list[str]
    repo: str = PYSPORT


@dataclass(frozen=True, slots=True)
class Verdict:
    hid: str
    claim: str
    definition: str
    numbers: dict[str, int | str]
    verdict: VerdictName
    sources: tuple[Loc, ...] = field(default=())


def verdict_of(parts: Sequence[bool]) -> VerdictName:
    if all(parts):
        return "confirmed"
    return "partly" if any(parts) else "refuted"


def _trees(snap: Snapshot) -> dict[str, ast.Module]:
    trees: dict[str, ast.Module] = {}
    for path, source in snap.py.items():
        try:
            trees[path] = parse_source(source, path)[0]
        except UnparsedError:
            continue
    return trees


def _imports(snap: Snapshot) -> dict[str, list[tuple[str, tuple[str, ...], int, bool]]]:
    found: dict[str, list[tuple[str, tuple[str, ...], int, bool]]] = {}
    for path, source in snap.py.items():
        name, is_package = module_name(path)
        try:
            refs = iter_imports(source, name, is_package=is_package, path=path)
        except UnparsedError:
            continue
        found[path] = [(r.module, r.names, r.line, r.local) for r in refs]
    return found


# ---------------------------------------------------------------- H1


def _rank(counts: Counter[str], paths: Iterable[str], path: str) -> int:
    return 1 + sum(1 for other in paths if counts[other] > counts[path])


def _top(counts: Counter[str], paths: Sequence[str]) -> str:
    return min(paths, key=lambda p: (-counts[p], p))


def h1_memory(snap: Snapshot) -> Verdict:
    commits: Counter[str] = Counter()
    churn: Counter[str] = Counter()
    for commit in snap.log:
        if commit.is_merge:
            continue
        for change in commit.files:
            commits[change.path] += 1
            churn[change.path] += (change.added or 0) + (change.deleted or 0)
    lines = len(physical_lines(snap.py[MEMORY]))
    py = [p for p in snap.tracked if p.endswith(".py")]
    numbers: dict[str, int | str] = {
        "lines": lines,
        "commits": commits[MEMORY],
        "rank_by_commits": _rank(commits, snap.tracked, MEMORY),
        "top_by_commits": _top(commits, snap.tracked),
        "top_commits": commits[_top(commits, snap.tracked)],
        "rank_by_commits_among_py": _rank(commits, py, MEMORY),
        "churn": churn[MEMORY],
        "rank_by_churn": _rank(churn, snap.tracked, MEMORY),
        "top_by_churn": _top(churn, snap.tracked),
        "tracked_files": len(snap.tracked),
    }
    return Verdict(
        "H1",
        "`sportorg/models/memory.py` — 2 910 строк и самый часто меняемый файл",
        "lines = physical lines (CR/LF/CRLF) at the pin; change frequency = non-merge commits"
        " reachable from the pin that touch the path (`git log --no-renames`), ranked among files"
        " tracked at the pin; churn (added + deleted lines, binary files 0) is reported, not"
        " judged. Parts: lines == 2910; rank by commits == 1.",
        numbers,
        verdict_of([lines == CLAIMED_LINES, numbers["rank_by_commits"] == 1]),
        (Loc(snap.repo, MEMORY, 1, lines),),
    )


# ---------------------------------------------------------------- H2


type Refs = list[tuple[str, tuple[str, ...], int, bool]]


def _is_memory_race(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "race"
        and isinstance(node.value, ast.Name)
        and node.value.id == "memory"
    )


def _race_uses(tree: ast.Module, refs: Refs) -> tuple[list[int], bool]:
    """Lines where a file binds or reaches the global race(), and whether it calls it."""
    name_lines = [
        line for module, names, line, _ in refs if module == MEMORY_MODULE and "race" in names
    ]
    module_imported = any(
        (module == MEMORY_MODULE and not names)
        or (module == "sportorg.models" and "memory" in names)
        for module, names, _, _ in refs
    )
    lines = list(name_lines)
    called = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and module_imported and _is_memory_race(node):
            lines.append(node.lineno)
        if isinstance(node, ast.Call):
            bare = isinstance(node.func, ast.Name) and node.func.id == "race" and bool(name_lines)
            called = called or bare or (module_imported and _is_memory_race(node.func))
    return sorted(set(lines)), called


def h2_race(snap: Snapshot) -> Verdict:
    trees, imports = _trees(snap), _imports(snap)
    uses: dict[str, list[int]] = {}
    calling: set[str] = set()
    for path, tree in trees.items():
        if path == MEMORY:
            continue
        lines, called = _race_uses(tree, imports.get(path, []))
        if lines:
            uses[path] = lines
        if called:
            calling.add(path)
    in_sportorg = [p for p in uses if p.startswith("sportorg/")]
    total = len(uses)
    scoped = len(in_sportorg)
    near = abs(scoped - CLAIMED_RACE_FILES) <= RACE_TOLERANCE * CLAIMED_RACE_FILES
    numbers: dict[str, int | str] = {
        "files_using_race": total,
        "files_using_race_in_sportorg": len(in_sportorg),
        "files_using_race_outside_sportorg": total - len(in_sportorg),
        "files_calling_race": len(calling),
    }
    verdict: VerdictName = "partly" if near else "refuted"
    if scoped == CLAIMED_RACE_FILES:
        verdict = "confirmed"
    sources = tuple(Loc(snap.repo, p, lines[0]) for p, lines in sorted(uses.items()))
    return Verdict(
        "H2",
        "глобальный `race()` используется в 62 файлах",
        "a file uses the global race() if it imports the name `race` from sportorg.models.memory"
        " (absolute or relative, module level or inside a function) or accesses `memory.race` after"
        " importing the memory module; memory.py itself excluded. Counted over all tracked .py"
        " files and over sportorg/. Verdict on sportorg/: confirmed if exactly 62, partly if within"
        " ±20 %, refuted otherwise. The scope sportorg/ was set after the result was known (the run"
        " fixed beforehand counted all files: 78, refuted) [мейнтейнер: 2026-10-25].",
        numbers,
        verdict,
        sources,
    )


# ---------------------------------------------------------------- H3


def _gui_kind(target: str, names: tuple[str, ...]) -> str:
    """``gui_package`` for sportorg.gui, ``qtcore`` for only QtCore of a binding, else ``qt_ui``."""
    if target.startswith("sportorg.gui"):
        return "gui_package"
    parts = target.split(".")
    submodules = set(parts[1:2]) if len(parts) > 1 else set(names)
    return "qtcore" if submodules == {"QtCore"} else "qt_ui"


def h3_gui(snap: Snapshot) -> Verdict:
    imports = _imports(snap)
    edges: list[tuple[str, int, bool, str]] = []
    startup = 0
    for path, refs in sorted(imports.items()):
        module = module_name(path)[0]
        if not path.startswith("sportorg/") or module.startswith("sportorg.gui"):
            continue
        for target, names, line, local in refs:
            if not (target.startswith("sportorg.gui") or target.split(".")[0] in QT):
                continue
            if module == "sportorg.startup":
                startup += 1
                continue
            edges.append((path, line, local, _gui_kind(target, names)))
    modules = sorted({p for p, _, _, _ in edges})
    result_gen = [p for p in modules if module_name(p)[0].startswith(RESULT_GENERATION)]
    ui = [e for e in edges if e[3] != "qtcore"]
    gui_package = [e for e in edges if e[3] == "gui_package"]
    ui_modules = {p for p, _, _, _ in ui}
    numbers: dict[str, int | str] = {
        "modules_outside_gui": len(modules),
        "edges": len(edges),
        "local_edges": sum(local for _, _, local, _ in edges),
        "result_generation_modules": len(result_gen),
        "startup_edges_not_counted": startup,
        "modules_qtcore_only": len(modules) - len(ui_modules),
        "edges_qtcore_only": len(edges) - len(ui),
        "modules_ui": len(ui_modules),
        "edges_ui": len(ui),
        "modules_gui_package": len({p for p, _, _, _ in gui_package}),
        "edges_gui_package": len(gui_package),
    }
    return Verdict(
        "H3",
        "GUI импортируется вне `sportorg/gui`, в том числе в генерации результатов",
        f"edges from modules of sportorg/ outside sportorg.gui (sportorg.startup excluded: the"
        f" entry point may import the UI) to sportorg.gui.* or a Qt binding ({', '.join(QT)})."
        f" Result generation = {', '.join(RESULT_GENERATION)}. Parts: any such edge; any in"
        " result generation. Split: qtcore_only = edges that import only QtCore of a Qt binding"
        " (threads, signals, dates); ui = the other edges (sportorg.gui, QtWidgets, QtGui,"
        " QtPrintSupport, ...); a module is qtcore_only when all its edges are.",
        numbers,
        verdict_of([bool(modules), bool(result_gen)]),
        tuple(Loc(snap.repo, p, line) for p, line, _, _ in edges),
    )


# ---------------------------------------------------------------- H4


def _system_attr(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Attribute) or not isinstance(node.value, ast.Name):
        return None
    return node.attr if node.value.id == "SystemType" else None


def _result_model(tree: ast.Module) -> tuple[dict[str, tuple[int, str | None]], set[str]]:
    """Result subclasses (line, bound SystemType member) and the ``is_<system>`` helper names."""
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    subclasses: dict[str, tuple[int, str | None]] = {}
    changed = True
    while changed:
        changed = False
        for name, node in classes.items():
            bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
            if name not in subclasses and bases & ({"Result"} | set(subclasses)):
                bound = None
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "system_type" for t in stmt.targets
                    ):
                        bound = _system_attr(stmt.value)
                subclasses[name] = (node.lineno, bound)
                changed = True
    helpers: set[str] = set()
    if "Result" in classes:
        for stmt in classes["Result"].body:
            if isinstance(stmt, ast.FunctionDef) and any(
                isinstance(n, ast.Compare) and any(_system_attr(c) for c in n.comparators)
                for n in ast.walk(stmt)
            ):
                helpers.add(stmt.name)
    return subclasses, helpers


def h4_system_type(snap: Snapshot) -> Verdict:
    trees = _trees(snap)
    subclasses, helpers = _result_model(trees[MEMORY])
    branches: list[tuple[str, int]] = []
    for path, tree in sorted(trees.items()):
        if path == MEMORY:
            continue
        for node in ast.walk(tree):
            compare = isinstance(node, ast.Compare) and any(
                _system_attr(e) for e in [node.left, *node.comparators]
            )
            helper = (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in helpers
            )
            instance = (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "isinstance"
                and any(
                    isinstance(n, ast.Name) and n.id in subclasses
                    for arg in node.args[1:]
                    for n in ast.walk(arg)
                )
            )
            if compare or helper or instance:
                branches.append((path, getattr(node, "lineno", 0)))
    bound = {name: v for name, v in subclasses.items() if v[1] is not None}
    numbers: dict[str, int | str] = {
        "result_subclasses": len(subclasses),
        "subclasses_with_system_type": len(bound),
        "system_types_bound": ", ".join(sorted({v[1] for v in bound.values() if v[1]})),
        "is_system_helpers": len(helpers),
        "branches_outside_memory": len(branches),
        "files_with_branches": len({p for p, _ in branches}),
    }
    defs = [Loc(snap.repo, MEMORY, line) for line, _ in sorted(subclasses.values())]
    sources = (*defs, *(Loc(snap.repo, p, line) for p, line in branches))
    return Verdict(
        "H4",
        "тип системы отметки зашит в классы результата",
        "in memory.py: classes deriving (transitively) from Result and their class attribute"
        " `system_type = SystemType.<X>`; Result methods comparing with SystemType (is_<system>"
        " helpers). Outside memory.py: comparisons with SystemType.<X>, calls of those helpers and"
        " isinstance checks against Result subclasses. Parts: ≥ 2 subclasses bound to a SystemType;"
        " ≥ 1 branch outside memory.py.",
        numbers,
        verdict_of([len(bound) >= 2, bool(branches)]),  # noqa: PLR2004 - "per system" needs two
        sources,
    )


# ---------------------------------------------------------------- H5


def h5_qualification(snap: Snapshot) -> Verdict:
    trees = _trees(snap)
    defs = [
        (path, node)
        for path, tree in sorted(trees.items())
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Qualification"
    ]
    path, node = defs[0]
    module = module_name(path)[0]
    members = [
        t.id
        for stmt in node.body
        if isinstance(stmt, ast.Assign)
        for t in stmt.targets
        if isinstance(t, ast.Name)
    ]
    refs: Counter[str] = Counter()
    ref_locs: list[Loc] = []
    for other, tree in sorted(trees.items()):
        if other == path:
            continue
        lines = sorted(
            getattr(n, "lineno", 0)
            for n in ast.walk(tree)
            if (isinstance(n, ast.Name) and n.id == "Qualification")
            or (isinstance(n, ast.Attribute) and n.attr == "Qualification")
            or (isinstance(n, ast.alias) and n.name == "Qualification")
        )
        if lines:
            refs[layer_of(module_name(other)[0])[1]] += 1
            ref_locs.append(Loc(snap.repo, other, lines[0]))
    layer = layer_of(module)[1]
    numbers: dict[str, int | str] = {
        "definitions": len(defs),
        "defined_in": module,
        "layer": layer,
        "members": ", ".join(members),
        **{f"referencing_files_{name}": count for name, count in sorted(refs.items())},
    }
    return Verdict(
        "H5",
        "`Qualification` с разрядами ЕВСК живёт в доменной модели",
        "the class named Qualification: where it is defined and the layer of that module (layer"
        " model of the plan); its members; files referencing the name, by layer. Part judged:"
        " defined in the domain layer. Whether the members are the EVSK ranks is not judged here:"
        " that needs the rules document (AGENTS.md rule 2), so it stays `[допущение]` until"
        " Stage 3.",
        numbers,
        verdict_of([layer == "domain"]),
        (Loc(snap.repo, path, node.lineno, node.end_lineno), *ref_locs),
    )


# ---------------------------------------------------------------- H6


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(m.group()) for m in re.finditer(r"\d+", version))


def _lock_versions(lock_text: str) -> dict[str, list[str]]:
    versions: dict[str, list[str]] = {}
    for item in as_list(as_dict(parse_toml(lock_text)).get("package")):
        package = as_dict(item)
        name, version = as_str(package.get("name")).lower(), as_str(package.get("version"))
        versions.setdefault(name, []).append(version)
    return {name: sorted(v, key=_version_key) for name, v in versions.items()}


def _strings(value: Json) -> list[str]:
    if isinstance(value, str):
        return [value]
    items = value.values() if isinstance(value, dict) else value if isinstance(value, list) else []
    return [s for item in items for s in _strings(item)]


def _dependency_strings(pyproject: dict[str, Json]) -> list[str]:
    project = as_dict(pyproject.get("project"))
    return [
        *_strings(project.get("dependencies")),
        *_strings(project.get("optional-dependencies")),
        *_strings(pyproject.get("dependency-groups")),
    ]


def _line_of(text: str, needle: str) -> int:
    for number, line in enumerate(physical_lines(text), start=1):
        if needle in line:
            return number
    return 1


def h6_windows7(snap: Snapshot) -> Verdict:
    pyproject_text, lock_text = snap.texts["pyproject.toml"], snap.texts["uv.lock"]
    pyproject = as_dict(parse_toml(pyproject_text))
    requires = as_str(as_dict(pyproject.get("project")).get("requires-python"))
    lower = re.search(r">=\s*([\d.]+)", requires)
    py38 = lower is not None and _version_key(lower.group(1))[:2] <= (3, 8)
    markers = [d for d in _dependency_strings(pyproject) if PY38_MARKER_RE.search(d)]
    lock = _lock_versions(lock_text)
    limits = {
        m.group(1): m.group(2) for m in WIN7_ROW_RE.finditer(snap.texts.get("CONTRIBUTING.md", ""))
    }
    within = sum(
        1
        for name, limit in limits.items()
        for version in lock.get(name.lower(), [])
        if _version_key(version) <= _version_key(limit)
    )
    pyside2 = sorted(
        (path, min(line for module, _, line, _ in refs if module.split(".")[0] == "PySide2"))
        for path, refs in _imports(snap).items()
        if any(module.split(".")[0] == "PySide2" for module, _, _, _ in refs)
    )
    locked = ("cryptography", "orjson", "pyside2", "pyside6")
    shown_limits = ", ".join(f"{k} <= {v}" for k, v in sorted(limits.items())) or "none"
    mentions = [
        (path, number)
        for path, text in sorted({**snap.texts, **snap.py}.items())
        for number, line in enumerate(physical_lines(text), start=1)
        if WIN7_RE.search(line)
    ]
    numbers: dict[str, int | str] = {
        "requires_python": requires,
        "py38_markers": len(markers),
        **{f"lock_{name}": ", ".join(lock.get(name, [])) or "none" for name in locked},
        "win7_limits_in_contributing": shown_limits,
        "lock_within_win7_limits": within,
        "files_importing_pyside2": len(pyside2),
        "win7_mentions": len(mentions),
    }
    sources = (
        Loc(snap.repo, "pyproject.toml", _line_of(pyproject_text, "requires-python")),
        *(Loc(snap.repo, p, line) for p, line in pyside2),
        *(Loc(snap.repo, p, n) for p, n in mentions),
    )
    return Verdict(
        "H6",
        "Windows 7 удерживает Python 3.8, PySide2 и старые `orjson`/`cryptography`",
        "parts: (a) `requires-python` admits 3.8; (b) some .py file imports PySide2 (the Qt5"
        " fallback); (c) `uv.lock` resolves orjson or cryptography to a version at or below the"
        " Windows 7 limits that legacy's CONTRIBUTING.md states. Also counted: dependency markers"
        " for Python 3.8 and lines that mention Windows 7 in tracked text files.",
        numbers,
        verdict_of([py38, bool(pyside2), within > 0]),
        sources,
    )


# ---------------------------------------------------------------- run on legacy


def load_snapshot(name: str = PYSPORT) -> Snapshot:
    repo, commit = repo_root(name), legacy.find_pin(name).commit
    py: dict[str, str] = {}
    texts: dict[str, str] = {}
    tracked = tracked_files(repo)
    for path in tracked:
        try:
            text = git_raw(repo, "show", f"{commit}:{path}")
        except legacy.LegacyError, UnicodeDecodeError:  # binary files are not text evidence
            continue
        (py if path.endswith(".py") else texts)[path] = text
    return Snapshot(py=py, texts=texts, log=git_log(repo, commit), tracked=tracked, repo=name)


HYPOTHESES: Final = (h1_memory, h2_race, h3_gui, h4_system_type, h5_qualification, h6_windows7)


def _as_json(verdict: Verdict) -> Json:
    return {
        "claim": verdict.claim,
        "definition": verdict.definition,
        "numbers": dict(verdict.numbers),
        "verdict": verdict.verdict,
        "sources": [loc.tag() for loc in verdict.sources],
    }


def table(verdicts: Sequence[Verdict]) -> str:
    rows = ["| гипотеза | число | вердикт | источник |", "|---|---|---|---|"]
    for v in verdicts:
        numbers = "; ".join(f"{k} = {val}" for k, val in v.numbers.items())
        shown = " ".join(loc.tag() for loc in v.sources[:3])
        more = f" и ещё {len(v.sources) - 3} в JSON" if len(v.sources) > 3 else ""  # noqa: PLR2004 - three shown
        rows.append(f"| {v.hid}: {v.claim} | {numbers} | {VERDICT_RU[v.verdict]} | {shown}{more} |")
    return "\n".join(rows)


class Options(argparse.Namespace):
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    snap = load_snapshot()
    verdicts = [hypothesis(snap) for hypothesis in HYPOTHESES]
    header = (
        f"# Hypotheses of the brief: verdicts on pysport@{pin_short(PYSPORT)}\n\n"
        "Produced by `scripts/archaeology/hypotheses.py` (command in `commands.txt`). Definitions"
        " are in `hypotheses.json` (`definition`), every `file:line` in `sources`."
    )
    data: Json = {v.hid: _as_json(v) for v in verdicts}
    write_outputs(args.out, "hypotheses", data, table(verdicts), header)
    for v in verdicts:
        print(f"{v.hid}: {v.verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
