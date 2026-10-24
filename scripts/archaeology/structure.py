"""Structure of the legacy code: hotspots, import graph, layer violations, dead code, Rust.

Run from the repo root (legacy is read through ``git`` and static tools with their caches off):
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.structure \
        --out docs/evidence/stage-1/structure

Tools (ADR-0007): ruff C901 for cyclomatic complexity, own ``ast`` extractor plus grimp for the
import graph, import-linter ``layers`` as an independent count of upward edges, vulture for dead
code. Nothing here runs, imports or writes under ``.legacy/``.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import tokenize
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Final

import grimp

from scripts import legacy
from scripts._json import Json, as_int, as_str, parse_json
from scripts.archaeology import tool_bench as tb
from scripts.archaeology.common import (
    PYSPORT,
    Commit,
    Loc,
    UnparsedError,
    assert_tree_clean,
    git_log,
    git_raw,
    iter_imports,
    layer_of,
    module_name,
    module_of,
    parse_source,
    physical_lines,
    pin_short,
    repo_root,
    tracked_files,
    write_outputs,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

ROOT: Final = legacy.ROOT
LEGACY_REL: Final = ".legacy/pysport"
TOP_HOTSPOTS: Final = 30
TOP_MODULES: Final = 20
ROOT_PACKAGE: Final = "sportorg"
VIOLATION_KINDS: Final = ("V1", "V2", "V3")
_CORE_MAX_RANK: Final = 2
_WARNING_RE: Final = re.compile(r"^(?P<path>.+?):(?P<line>\d+): (?P<message>.*)$", re.DOTALL)
_WORD_RE: Final = re.compile(r"\w+")
_DIGITS_RE: Final = re.compile(r"\d+")
_LINTER_HOP_RE: Final = re.compile(
    r"(?P<a>[\w.]+)\s*->\s*(?P<b>[\w.]+)\s*\(l\.(?P<lines>\d+(?:\s*,\s*l\.\d+)*)\)"
)
_LINTER_SIZE_RE: Final = re.compile(r"Analyzed (?P<files>\d+) files, (?P<deps>\d+) dependencies")
_NOT_CODE_TOKENS: Final = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
    }
)
# vulture findings whose "name" is a keyword or empty, not a defined name: no string check
NAMELESS_KINDS: Final = frozenset({"unreachable code", "redundant if-condition"})
# Contract layers, highest first; siblings of one layer share a tuple. Must agree with
# ``common.layer_of`` (checked in the tests): rank = 5 - index.
CONTRACT_LAYERS: Final = (
    ("sportorg.startup",),
    ("sportorg.gui",),
    ("sportorg.modules", "sportorg.rust_example"),
    ("sportorg.models",),
    (
        "sportorg.common",
        "sportorg.utils",
        "sportorg.config",
        "sportorg.settings",
        "sportorg.language",
        "sportorg.paths",
    ),
    ("sportorg.libs",),
)


# ---------------------------------------------------------------- GUI and I/O libraries (V3)


@dataclass(frozen=True, slots=True)
class IoLib:
    pattern: str  # a module root; a trailing ``*`` matches every root with that prefix
    category: str
    reason: str


IO_LIBS: Final = (
    IoLib("PySide6", "gui", "Qt 6 GUI toolkit"),
    IoLib("PySide2", "gui", "Qt 5 GUI toolkit (fallback binding of the Windows 7 build)"),
    IoLib("PyQt5", "gui", "Qt 5 GUI toolkit, alternative binding"),
    IoLib("PyQt6", "gui", "Qt 6 GUI toolkit, alternative binding"),
    IoLib("serial", "device", "pySerial: COM ports of SPORTident and other stations"),
    IoLib("pywinusb", "device", "USB HID devices on Windows (card readers)"),
    IoLib("pyImpinj", "device", "client of Impinj RFID readers"),
    IoLib("sportident", "device", "SPORTident reader library, talks to stations over serial"),
    IoLib("requests", "network", "HTTP client"),
    IoLib("aiohttp", "network", "asynchronous HTTP client and server"),
    IoLib("socket", "network", "raw sockets (TCP/UDP exchange with devices and clients)"),
    IoLib("win32*", "os-api", "pywin32 modules (win32api, win32print, win32ui, ...): Windows API"),
    IoLib("pywintypes", "os-api", "pywin32 support module"),
    IoLib("winreg", "os-api", "Windows registry"),
    IoLib("psutil", "os-api", "process and system information"),
    IoLib("webbrowser", "os-api", "starts the system browser"),
    IoLib("playsound3", "audio", "plays sound files through the OS audio system"),
)


def io_library(module: str) -> IoLib | None:
    """The GUI or I/O library entry that an imported module belongs to, if any."""
    root = module.split(".", maxsplit=1)[0]
    for lib in IO_LIBS:
        if lib.pattern.endswith("*"):
            if root.startswith(lib.pattern[:-1]):
                return lib
        elif root == lib.pattern:
            return lib
    return None


# ---------------------------------------------------------------- SLOC


def sloc(source: str) -> int:
    """Lines that carry at least one token other than a comment or a line break.

    Docstring and other multi-line string lines count; on a tokenizer error (a source that does
    not tokenize) the fallback counts lines that are neither blank nor start with ``#``.
    """
    covered: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type not in _NOT_CODE_TOKENS:
                covered.update(range(token.start[0], token.end[0] + 1))
    except tokenize.TokenError, SyntaxError:
        return sum(
            1
            for line in physical_lines(source)
            if line.strip() and not line.lstrip().startswith("#")
        )
    return len(covered)


# ---------------------------------------------------------------- hotspots


@dataclass(frozen=True, slots=True)
class Hotspot:
    path: str
    commits: int
    functions: int
    total_cc: int
    max_cc: int
    max_func: str
    max_line: int
    sloc: int
    lines: int
    score: int
    rank: int = 0

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.max_line).tag() if self.lines else ""


def commit_counts(log: Iterable[Commit]) -> Counter[str]:
    """Non-merge commits that touch each path."""
    counts: Counter[str] = Counter()
    for commit in log:
        if not commit.is_merge:
            counts.update({change.path for change in commit.files})
    return counts


def hotspot_rows(
    py: Mapping[str, str], log: Iterable[Commit], complexity: tb.Complexity
) -> list[Hotspot]:
    """Per ``.py`` file: commits x total complexity, ranked (ties: more commits, then path)."""
    commits = commit_counts(log)
    functions: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for (path, line), (name, cc) in complexity.items():
        functions[path].append((cc, line, name))
    rows: list[Hotspot] = []
    for path, source in py.items():
        found = functions.get(path, [])
        total = sum(cc for cc, _, _ in found)
        top = min(found, key=lambda f: (-f[0], f[1]), default=(0, 1, ""))
        rows.append(
            Hotspot(
                path=path,
                commits=commits[path],
                functions=len(found),
                total_cc=total,
                max_cc=top[0],
                max_func=top[2],
                max_line=top[1],
                sloc=sloc(source),
                lines=len(physical_lines(source)),
                score=commits[path] * total,
            )
        )
    rows.sort(key=lambda r: (-r.score, -r.commits, r.path))
    return [replace(row, rank=i) for i, row in enumerate(rows, start=1)]


def commits_complexity_spearman(rows: Sequence[Hotspot]) -> dict[str, float | None]:
    """Spearman correlation of commits and total complexity: all files, files with functions."""

    def rho(subset: Sequence[Hotspot]) -> float | None:
        if len(subset) < 2:  # noqa: PLR2004 - a correlation needs two points
            return None
        return round(tb.spearman([r.commits for r in subset], [r.total_cc for r in subset]), 4)

    return {
        "all_files": rho(rows),
        "files_with_functions": rho([r for r in rows if r.functions]),
    }


# ---------------------------------------------------------------- import extraction


@dataclass(frozen=True, slots=True)
class Edge:
    src: str
    dst: str
    path: str
    line: int
    local: bool

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.line).tag()


@dataclass(frozen=True, slots=True)
class External:
    src: str
    root: str
    module: str
    path: str
    line: int
    local: bool

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.line).tag()


@dataclass(frozen=True, slots=True)
class Warn:
    path: str
    line: int
    message: str

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.line).tag()


@dataclass(frozen=True, slots=True)
class Unparsed:
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class Extraction:
    modules: frozenset[str]
    edges: tuple[Edge, ...]
    externals: tuple[External, ...]
    warnings: tuple[Warn, ...]
    unparsed: tuple[Unparsed, ...]


def extract(py: Mapping[str, str]) -> Extraction:
    """Imports of the ``sportorg/`` modules (graph, violations) and parse problems of all files."""
    modules = {module_name(p)[0] for p in py if p.startswith(f"{ROOT_PACKAGE}/")}
    edges: list[Edge] = []
    externals: list[External] = []
    warnings: list[Warn] = []
    unparsed: list[Unparsed] = []
    for path in sorted(py):
        try:
            _, found = parse_source(py[path], path)
        except UnparsedError as exc:
            unparsed.append(Unparsed(path, exc.reason))
            continue
        for text in found:
            match = _WARNING_RE.match(text)
            if match is not None:
                warnings.append(Warn(path, int(match["line"]), match["message"]))
        if not path.startswith(f"{ROOT_PACKAGE}/"):
            continue
        name, is_package = module_name(path)
        for ref in iter_imports(py[path], name, is_package=is_package, path=path):
            if ref.module == ROOT_PACKAGE or ref.module.startswith(f"{ROOT_PACKAGE}."):
                edges.extend(
                    Edge(name, target, path, ref.line, ref.local)
                    for target in sorted(tb.import_targets(ref, modules))
                    if target != name
                )
            elif ref.module:
                root = ref.module.split(".")[0]
                externals.append(External(name, root, ref.module, path, ref.line, ref.local))
    return Extraction(
        modules=frozenset(modules),
        edges=tuple(sorted(edges, key=lambda e: (e.src, e.dst, e.line))),
        externals=tuple(sorted(externals, key=lambda e: (e.src, e.module, e.line))),
        warnings=tuple(sorted(warnings, key=lambda w: (w.path, w.line, w.message))),
        unparsed=tuple(unparsed),
    )


def module_summary(ex: Extraction) -> list[dict[str, Json]]:
    """Per module: distinct importers (fan-in) and distinct imported modules (fan-out)."""
    out: dict[str, set[str]] = defaultdict(set)
    into: dict[str, set[str]] = defaultdict(set)
    statements: Counter[str] = Counter()
    local: Counter[str] = Counter()
    for edge in ex.edges:
        out[edge.src].add(edge.dst)
        into[edge.dst].add(edge.src)
        statements[edge.src] += 1
        local[edge.src] += edge.local
    rows: list[dict[str, Json]] = []
    for module in sorted(ex.modules):
        rank, layer = layer_of(module)
        rows.append(
            {
                "module": module,
                "layer": layer,
                "rank": rank,
                "fan_in": len(into[module]),
                "fan_out": len(out[module]),
                "import_statements": statements[module],
                "local_import_statements": local[module],
            }
        )
    return rows


# ---------------------------------------------------------------- layer violations


@dataclass(frozen=True, slots=True)
class Violation:
    kind: str
    src: str
    src_layer: str
    dst: str
    dst_layer: str
    path: str
    line: int
    local: bool

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.line).tag()


def _lib_of(module: str) -> str | None:
    parts = module.split(".")
    if parts[:2] == [ROOT_PACKAGE, "libs"] and len(parts) > 2:  # noqa: PLR2004 - sportorg.libs.<lib>
        return parts[2]
    return None


def _same_lib(module: str, lib: str) -> bool:
    prefix = f"{ROOT_PACKAGE}.libs.{lib}"
    return module == prefix or module.startswith(f"{prefix}.")


def find_violations(ex: Extraction) -> list[Violation]:
    """V1 upward edge, V2 vendored lib importing another ``sportorg.*``, V3 GUI/I/O in the core."""
    found: list[Violation] = []
    for edge in ex.edges:
        (src_rank, src_layer), (dst_rank, dst_layer) = layer_of(edge.src), layer_of(edge.dst)
        row = (edge.src, src_layer, edge.dst, dst_layer, edge.path, edge.line, edge.local)
        if 0 <= src_rank < dst_rank:
            found.append(Violation("V1", *row))
        lib = _lib_of(edge.src)
        if lib is not None and not _same_lib(edge.dst, lib):
            found.append(Violation("V2", *row))
    for ext in ex.externals:
        src_rank, src_layer = layer_of(ext.src)
        lib = io_library(ext.module)
        if lib is not None and 0 <= src_rank <= _CORE_MAX_RANK:
            found.append(
                Violation(
                    "V3",
                    ext.src,
                    src_layer,
                    ext.module,
                    f"external {lib.category}",
                    ext.path,
                    ext.line,
                    ext.local,
                )
            )
    return sorted(found, key=lambda v: (v.kind, v.src, v.dst, v.line))


def violation_counts(found: Iterable[Violation]) -> dict[str, dict[str, int]]:
    counts = {kind: {"module_level": 0, "local": 0} for kind in VIOLATION_KINDS}
    for violation in found:
        counts[violation.kind]["local" if violation.local else "module_level"] += 1
    return counts


# ---------------------------------------------------------------- import-linter


def layers_contract(modules: Iterable[str]) -> str:
    """An import-linter config with the layer model; layers without any module are left out."""
    existing = set(modules)

    def present(prefix: str) -> bool:
        return any(m == prefix or m.startswith(f"{prefix}.") for m in existing)

    lines = [
        "[importlinter]",
        f"root_package = {ROOT_PACKAGE}",
        "",
        "[importlinter:contract:layers]",
        "name = legacy layer model",
        "type = layers",
        "layers =",
    ]
    for layer in CONTRACT_LAYERS:
        members = [m for m in layer if present(m)]
        if members:
            lines.append(f"    {' : '.join(members)}")
    return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class LinterDep:
    importer: str
    imported: str
    hops: int
    lines: tuple[int, ...]


def parse_lint_imports(text: str) -> list[LinterDep]:
    """Entries ``- a -> b (l.N)`` of a broken ``layers`` contract (wrapped lines are joined)."""
    deps: list[LinterDep] = []
    current: list[str] | None = None

    def flush() -> None:
        if current is None:
            return
        hops = list(_LINTER_HOP_RE.finditer(" ".join(current)))
        if hops:
            numbers = tuple(
                int(n.group()) for hop in hops for n in _DIGITS_RE.finditer(hop["lines"])
            )
            deps.append(LinterDep(hops[0]["a"], hops[-1]["b"], len(hops), numbers))

    for line in text.splitlines():
        if line.startswith("- "):
            flush()
            current = [line[2:]]
        elif not line.strip():
            flush()
            current = None
        elif current is not None:
            current.append(line)
    flush()
    return deps


def compare_v1(found: Iterable[Violation], deps: Sequence[LinterDep]) -> dict[str, Json]:
    """V1 module pairs against the direct pairs of the layers contract."""
    mine = {(v.src, v.dst) for v in found if v.kind == "V1" and ROOT_PACKAGE not in {v.src, v.dst}}
    direct = {(d.importer, d.imported) for d in deps if d.hops == 1}
    return {
        "v1_pairs": len(mine),
        "linter_direct_pairs": len(direct),
        "linter_indirect_entries": sum(d.hops > 1 for d in deps),
        "both": len(mine & direct),
        "only_v1": [list(p) for p in sorted(mine - direct)],
        "only_linter": [list(p) for p in sorted(direct - mine)],
    }


# ---------------------------------------------------------------- dead code


@dataclass(frozen=True, slots=True)
class StringIndex:
    exact: frozenset[str]  # whole string literals
    words: frozenset[str]  # words (``\w+``) inside string literals

    def is_string(self, name: str) -> bool:
        return name in self.exact

    def in_string(self, name: str) -> bool:
        return name in self.words


def _docstring_ids(tree: ast.Module) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                ids.add(id(first.value))
    return ids


def string_index(sources: Iterable[str]) -> StringIndex:
    """String literals of the sources, docstrings excluded; unparsable sources are skipped."""
    exact: set[str] = set()
    words: set[str] = set()
    for source in sources:
        try:
            tree, _ = parse_source(source, "<string>")
        except UnparsedError:
            continue
        docstrings = _docstring_ids(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in docstrings
            ):
                exact.add(node.value)
                words.update(_WORD_RE.findall(node.value))
    return StringIndex(frozenset(exact), frozenset(words))


@dataclass(frozen=True, slots=True)
class DeadRow:
    path: str
    line: int
    kind: str
    name: str
    confidence: int
    name_in_string: bool  # the name is a word of a (non-docstring) string literal somewhere
    name_is_string: bool  # the name is a whole string literal somewhere

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, self.line).tag()


def dead_code_rows(findings: Iterable[Mapping[str, Json]], index: StringIndex) -> list[DeadRow]:
    """Rows sorted by place; the string flags are False for findings that name no definition."""
    rows: list[DeadRow] = []
    for f in findings:
        kind, name = as_str(f.get("kind")), as_str(f.get("name"))
        named = kind not in NAMELESS_KINDS
        rows.append(
            DeadRow(
                path=as_str(f.get("path")),
                line=as_int(f.get("line")),
                kind=kind,
                name=name,
                confidence=as_int(f.get("confidence")),
                name_in_string=named and index.in_string(name),
                name_is_string=named and index.is_string(name),
            )
        )
    return sorted(rows, key=lambda r: (r.path, r.line, r.kind, r.name))


# ---------------------------------------------------------------- Rust


@dataclass(frozen=True, slots=True)
class RustFile:
    path: str
    kind: str  # rust | cargo-toml | cargo-lock
    crate: str
    lines: int
    commits: int

    @property
    def tag(self) -> str:
        return Loc(PYSPORT, self.path, 1).tag() if self.lines else ""


@dataclass(frozen=True, slots=True)
class RustCrate:
    crate: str
    files: int
    rust_lines: int
    cargo_lines: int
    commits: int


def _rust_kind(path: str) -> str | None:
    name = path.rsplit("/", 1)[-1]
    if path.endswith(".rs"):
        return "rust"
    return {"Cargo.toml": "cargo-toml", "Cargo.lock": "cargo-lock"}.get(name)


def rust_rows(
    tracked: Iterable[str], texts: Mapping[str, str], log: Iterable[Commit]
) -> tuple[list[RustFile], list[RustCrate]]:
    """Tracked ``*.rs``, ``Cargo.toml`` and ``Cargo.lock``: lines and non-merge commits."""
    paths = sorted(p for p in tracked if _rust_kind(p) is not None)
    wanted = set(paths)
    touching: dict[str, set[str]] = defaultdict(set)
    crate_commits: dict[str, set[str]] = defaultdict(set)
    for commit in log:
        if commit.is_merge:
            continue
        for change in commit.files:
            if change.path in wanted:
                touching[change.path].add(commit.sha)
                crate_commits[_crate_of(change.path)].add(commit.sha)
    files = [
        RustFile(
            path=path,
            kind=_rust_kind(path) or "",
            crate=_crate_of(path),
            lines=len(physical_lines(texts.get(path, ""))),
            commits=len(touching[path]),
        )
        for path in paths
    ]
    crates = [
        RustCrate(
            crate=crate,
            files=sum(f.crate == crate for f in files),
            rust_lines=sum(f.lines for f in files if f.crate == crate and f.kind == "rust"),
            cargo_lines=sum(f.lines for f in files if f.crate == crate and f.kind != "rust"),
            commits=len(crate_commits[crate]),
        )
        for crate in sorted({f.crate for f in files})
    ]
    return files, crates


def _crate_of(path: str) -> str:
    bucket = module_of(path)
    return bucket if bucket.startswith("crates.") else "workspace"


# ---------------------------------------------------------------- tool runners


def _env() -> dict[str, str]:
    return {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _venv_bin(name: str) -> str:
    return str(Path(sys.executable).parent / name)


def run_ruff_c901() -> tb.Complexity:
    result = subprocess.run(
        [
            _venv_bin("ruff"), "check", "--no-cache", "--isolated", "--select", "C901",
            "--config", "lint.mccabe.max-complexity=0", "--output-format", "json", LEGACY_REL,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=_env(),
    )  # fmt: skip
    return tb.parse_ruff_c901(parse_json(result.stdout), str(repo_root(PYSPORT)))


def run_vulture() -> list[dict[str, Json]]:
    result = subprocess.run(
        [_venv_bin("vulture"), f"{LEGACY_REL}/{ROOT_PACKAGE}", "--min-confidence", "0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=_env(),
    )
    return tb.parse_vulture(result.stdout, LEGACY_REL)


def grimp_edges(repo: Path) -> set[tuple[str, str]]:
    sys.path.insert(0, str(repo))
    try:
        graph = grimp.build_graph(ROOT_PACKAGE, cache_dir=None)
    finally:
        sys.path.remove(str(repo))
    return {(m, i) for m in graph.modules for i in graph.find_modules_directly_imported_by(m)}


def run_lint_imports(modules: Iterable[str], repo: Path) -> tuple[int, str]:
    """Run the layers contract from a config in ``$TMPDIR`` (never in the repository)."""
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "layers.ini"
        config.write_text(layers_contract(modules), encoding="utf-8", newline="\n")
        result = subprocess.run(
            [_venv_bin("lint-imports"), "--config", str(config), "--no-cache", "--no-logo"],
            cwd=tmp,
            capture_output=True,
            text=True,
            check=False,
            env={**_env(), "PYTHONPATH": str(repo)},
        )
    return result.returncode, result.stdout


# ---------------------------------------------------------------- output


def md_table(columns: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    return "\n".join(
        [
            "| " + " | ".join(columns) + " |",
            "|" + "---|" * len(columns),
            *("| " + " | ".join(cell(v) for v in row) + " |" for row in rows),
        ]
    )


def _header(title: str, note: str) -> str:
    return (
        f"# {title}\n\nLegacy pin: pysport@{pin_short(PYSPORT)}. Produced by "
        f"`scripts/archaeology/structure.py` (command in `commands.txt`). {note}"
    )


def _yes(flag: bool) -> str:  # noqa: FBT001 - a plain predicate formatter
    return "yes" if flag else "no"


def _hotspot_json(row: Hotspot) -> dict[str, Json]:
    return {
        "rank": row.rank,
        "path": row.path,
        "commits": row.commits,
        "functions": row.functions,
        "total_cc": row.total_cc,
        "max_cc": row.max_cc,
        "max_func": row.max_func,
        "max_line": row.max_line,
        "sloc": row.sloc,
        "lines": row.lines,
        "score": row.score,
        "tag": row.tag,
    }


def write_hotspots(out: Path, rows: Sequence[Hotspot]) -> dict[str, Json]:
    rho = commits_complexity_spearman(rows)
    summary: dict[str, Json] = {
        "py_files": len(rows),
        "files_with_functions": sum(1 for r in rows if r.functions),
        "functions": sum(r.functions for r in rows),
        "total_cc": sum(r.total_cc for r in rows),
        "sloc": sum(r.sloc for r in rows),
        "spearman_commits_vs_total_cc": dict(rho),
        "top10": [r.path for r in rows[:10]],
    }
    table = md_table(
        ("rank", "file", "commits", "total CC", "max CC (function)", "SLOC", "score", "[код]"),
        (
            (r.rank, f"`{r.path}`", r.commits, r.total_cc, f"{r.max_cc} (`{r.max_func}`)",
             r.sloc, r.score, r.tag)
            for r in rows[:TOP_HOTSPOTS]
        ),
    )  # fmt: skip
    text = (
        f"Spearman correlation of non-merge commits and total complexity: "
        f"{rho['all_files']} over all {len(rows)} `.py` files, "
        f"{rho['files_with_functions']} over the {summary['files_with_functions']} files "
        f"that contain functions.\n\nTop {TOP_HOTSPOTS} of {len(rows)} files (all in the JSON):\n\n"
        f"{table}"
    )
    header = _header(
        "Hotspots",
        "score = non-merge commits touching the file x total cyclomatic complexity (ruff C901, "
        "one value per function and method); SLOC = lines with a token other than a comment. "
        "The `[код]` tag points at the most complex function of the file.",
    )
    data: Json = {"summary": summary, "files": [_hotspot_json(r) for r in rows]}
    write_outputs(out, "hotspots", data, text, header)
    return summary


def write_imports(out: Path, ex: Extraction, grimp_set: set[tuple[str, str]]) -> dict[str, Json]:
    own = {(e.src, e.dst) for e in ex.edges}
    only_own, only_grimp = sorted(own - grimp_set), sorted(grimp_set - own)
    by_edge: dict[tuple[str, str], Edge] = {}
    for edge in ex.edges:
        by_edge.setdefault((edge.src, edge.dst), edge)
    modules = module_summary(ex)
    summary: dict[str, Json] = {
        "modules": len(ex.modules),
        "statements": len(ex.edges),
        "statements_module_level": sum(not e.local for e in ex.edges),
        "statements_local": sum(e.local for e in ex.edges),
        "edges_own": len(own),
        "edges_grimp": len(grimp_set),
        "edges_both": len(own & grimp_set),
        "edges_only_own": len(only_own),
        "edges_only_grimp": len(only_grimp),
        "syntax_warnings": len(ex.warnings),
        "unparsed": len(ex.unparsed),
    }
    edges_json: list[Json] = [
        {
            "src": e.src,
            "dst": e.dst,
            "path": e.path,
            "line": e.line,
            "local": e.local,
            "tag": e.tag,
        }
        for e in ex.edges
    ]
    diff_own: list[Json] = [{"src": a, "dst": b, "tag": by_edge[a, b].tag} for a, b in only_own]
    diff_grimp: list[Json] = [{"src": a, "dst": b} for a, b in only_grimp]
    warnings_json: list[Json] = [
        {"path": w.path, "line": w.line, "message": w.message, "tag": w.tag} for w in ex.warnings
    ]
    unparsed_json: list[Json] = [{"path": u.path, "reason": u.reason} for u in ex.unparsed]
    modules_json: list[Json] = [dict(m) for m in modules]
    data: Json = {
        "summary": summary,
        "modules": modules_json,
        "edges": edges_json,
        "only_own": diff_own,
        "only_grimp": diff_grimp,
        "syntax_warnings": warnings_json,
        "unparsed": unparsed_json,
    }

    def ranked(key: str) -> list[dict[str, Json]]:
        return sorted(modules, key=lambda m: (-as_int(m[key]), as_str(m["module"])))[:TOP_MODULES]

    def top(key: str) -> str:
        return md_table(
            ("module", "layer", "fan-in", "fan-out"),
            ((f"`{m['module']}`", m["layer"], m["fan_in"], m["fan_out"]) for m in ranked(key)),
        )

    text = "\n\n".join(
        [
            md_table(
                ("measure", "value"),
                [
                    ("modules (`sportorg/**.py`)", summary["modules"]),
                    ("import statements resolved to an internal module", summary["statements"]),
                    (
                        "...of them module level / function-local",
                        f"{summary['statements_module_level']} / {summary['statements_local']}",
                    ),
                    ("distinct module pairs, own extractor", summary["edges_own"]),
                    ("distinct module pairs, grimp", summary["edges_grimp"]),
                    ("in both", summary["edges_both"]),
                    ("only own", summary["edges_only_own"]),
                    ("only grimp", summary["edges_only_grimp"]),
                ],
            ),
            f"## Top {TOP_MODULES} by fan-in\n\n{top('fan_in')}",
            f"## Top {TOP_MODULES} by fan-out\n\n{top('fan_out')}",
            "## Edges only in the own extractor\n\n"
            + md_table(
                ("importer", "imported", "[код]"),
                ((f"`{a}`", f"`{b}`", by_edge[a, b].tag) for a, b in only_own),
            ),
            "## Edges only in grimp\n\n"
            + md_table(("importer", "imported"), ((f"`{a}`", f"`{b}`") for a, b in only_grimp)),
            f"## SyntaxWarnings ({len(ex.warnings)})\n\n"
            + md_table(
                ("message", "[код]"),
                ((f"`` {w.message} ``", w.tag) for w in ex.warnings),
            ),
            f"## Files that `ast` cannot parse ({len(ex.unparsed)})\n\n"
            + md_table(("file", "reason"), ((f"`{u.path}`", u.reason) for u in ex.unparsed)),
        ]
    )
    header = _header(
        "Import graph",
        "Own edges: `ast` imports of every tracked `sportorg/**.py`, relative imports resolved, "
        "`from m import x` counted as an edge to `m.x` when that is a module. Full edge list "
        "(file:line, local flag) in `imports.json`.",
    )
    write_outputs(out, "imports", data, text, header)
    return summary


def _violation_json(v: Violation) -> dict[str, Json]:
    return {
        "kind": v.kind, "src": v.src, "src_layer": v.src_layer, "dst": v.dst,
        "dst_layer": v.dst_layer, "path": v.path, "line": v.line, "local": v.local, "tag": v.tag,
    }  # fmt: skip


def write_violations(
    out: Path,
    ex: Extraction,
    found: Sequence[Violation],
    linter: Mapping[str, Json],
) -> dict[str, Json]:
    counts = violation_counts(found)
    layer_pairs = Counter(f"{v.src_layer} -> {v.dst_layer}" for v in found if v.kind == "V1")
    core_third_party = Counter(
        e.root
        for e in ex.externals
        if 0 <= layer_of(e.src)[0] <= _CORE_MAX_RANK
        and io_library(e.module) is None
        and e.root not in sys.stdlib_module_names
    )
    outside = sorted(m for m in ex.modules if layer_of(m)[0] < 0)
    summary: dict[str, Json] = {
        "counts": {k: dict(v) for k, v in counts.items()},
        "v1_by_layer_pair": dict(sorted(layer_pairs.items())),
        "v1_excluding_vendored": {
            "module_level": sum(
                v.kind == "V1" and v.src_layer != "vendored" and not v.local for v in found
            ),
            "local": sum(v.kind == "V1" and v.src_layer != "vendored" and v.local for v in found),
        },
        "linter": dict(linter),
        "core_third_party_not_listed": dict(sorted(core_third_party.items())),
        "modules_outside_model": list[Json](outside),
    }
    data: Json = {
        "summary": summary,
        "libraries": [
            {"pattern": lib.pattern, "category": lib.category, "reason": lib.reason}
            for lib in IO_LIBS
        ],
        "violations": [_violation_json(v) for v in found],
    }
    sections = [
        md_table(
            ("kind", "module level", "function-local"),
            ((k, counts[k]["module_level"], counts[k]["local"]) for k in VIOLATION_KINDS),
        ),
        (
            "V1 = upward edge (rank r to rank > r), V2 = `sportorg.libs.<a>` importing another "
            "`sportorg.*`, V3 = ranks 0-2 importing a GUI or I/O library (list in "
            "`violations.json`, `libraries`). One edge can be both V1 and V2."
        ),
        "## import-linter `layers` contract\n\n```json\n" + _dumps(dict(linter)) + "\n```",
    ]
    for kind in VIOLATION_KINDS:
        rows = [v for v in found if v.kind == kind]
        sections.append(
            f"## {kind} ({len(rows)})\n\n"
            + md_table(
                ("source", "layer", "target", "layer", "local", "[код]"),
                (
                    (f"`{v.src}`", v.src_layer, f"`{v.dst}`", v.dst_layer, _yes(v.local), v.tag)
                    for v in rows
                ),
            )
        )
    header = _header(
        "Layer violations",
        "Layer model from the plan (approved 2026-10-25), ranks from `common.layer_of`.",
    )
    write_outputs(out, "violations", data, "\n\n".join(sections), header)
    return summary


def _dumps(value: Mapping[str, Json]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True)


def write_dead_code(out: Path, rows: Sequence[DeadRow]) -> dict[str, Json]:
    by_kind = Counter(r.kind for r in rows)
    flagged = Counter(r.kind for r in rows if r.name_in_string)
    exact = Counter(r.kind for r in rows if r.name_is_string)
    summary: dict[str, Json] = {
        "findings": len(rows),
        "by_kind": dict(sorted(by_kind.items())),
        "name_in_string": sum(flagged.values()),
        "name_in_string_by_kind": dict(sorted(flagged.items())),
        "name_is_string": sum(exact.values()),
        "by_confidence": dict(sorted(Counter(str(r.confidence) for r in rows).items())),
    }
    data: Json = {
        "summary": summary,
        "findings": [
            {
                "kind": r.kind,
                "name": r.name,
                "confidence": r.confidence,
                "path": r.path,
                "line": r.line,
                "name_in_string": r.name_in_string,
                "name_is_string": r.name_is_string,
                "tag": r.tag,
            }
            for r in rows
        ],
    }
    kinds = md_table(
        ("kind", "findings", "name_in_string", "name_is_string"),
        ((k, by_kind[k], flagged[k], exact[k]) for k in sorted(by_kind)),
    )
    table = md_table(
        ("kind", "name", "confidence", "name_in_string", "name_is_string", "[код]"),
        (
            (r.kind, f"`{r.name}`", r.confidence, _yes(r.name_in_string), _yes(r.name_is_string),
             r.tag)
            for r in rows
        ),
    )  # fmt: skip
    header = _header(
        "Dead code (vulture, min confidence 0)",
        "`name_in_string`: the name is a word of a string literal (docstrings excluded) in a "
        "tracked legacy `.py` file, a likely false positive through string dispatch. "
        "`name_is_string`: the name is a whole string literal. No finding is judged here.",
    )
    write_outputs(out, "dead-code", data, f"{kinds}\n\n{table}", header)
    return summary


def write_rust(
    out: Path, files: Sequence[RustFile], crates: Sequence[RustCrate]
) -> dict[str, Json]:
    summary: dict[str, Json] = {
        "rust_files": sum(f.kind == "rust" for f in files),
        "rust_lines": sum(f.lines for f in files if f.kind == "rust"),
        "cargo_lines": sum(f.lines for f in files if f.kind != "rust"),
        "crates": {c.crate: c.rust_lines for c in crates},
    }
    data: Json = {
        "summary": summary,
        "files": [
            {
                "path": f.path,
                "kind": f.kind,
                "crate": f.crate,
                "lines": f.lines,
                "commits": f.commits,
                "tag": f.tag,
            }
            for f in files
        ],
        "crates": [
            {
                "crate": c.crate,
                "files": c.files,
                "rust_lines": c.rust_lines,
                "cargo_lines": c.cargo_lines,
                "commits": c.commits,
            }
            for c in crates
        ],
    }
    text = "\n\n".join(
        [
            md_table(
                ("crate", "files", "Rust lines", "Cargo lines", "commits"),
                ((c.crate, c.files, c.rust_lines, c.cargo_lines, c.commits) for c in crates),
            ),
            md_table(
                ("file", "kind", "lines", "commits", "[код]"),
                ((f"`{f.path}`", f.kind, f.lines, f.commits, f.tag) for f in files),
            ),
        ]
    )
    header = _header(
        "Rust",
        "Tracked `*.rs`, `Cargo.toml`, `Cargo.lock`; lines are physical lines, commits are "
        "non-merge commits touching the file (a crate: distinct commits touching any of its "
        "files).",
    )
    write_outputs(out, "rust", data, text, header)
    return summary


def write_summary(out: Path, parts: Mapping[str, Json]) -> None:
    data: Json = dict(parts)
    text = "```json\n" + _dumps(data) + "\n```"
    write_outputs(out, "summary", data, text, _header("Key numbers", "Collected from the files."))


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    repo, commit = repo_root(PYSPORT), legacy.find_pin(PYSPORT).commit
    if git_raw(repo, "rev-parse", "HEAD").strip() != commit:
        msg = f"{repo} is not at the pin {commit}; run `python -m scripts.legacy fetch`"
        raise legacy.LegacyError(msg)
    tracked = tracked_files(repo)
    py: dict[str, str] = {}
    texts: dict[str, str] = {}
    for path in tracked:
        if path.endswith((".py", ".rs")) or _rust_kind(path) is not None:
            try:
                text = git_raw(repo, "show", f"{commit}:{path}")
            except legacy.LegacyError, UnicodeDecodeError:
                continue
            (py if path.endswith(".py") else texts)[path] = text
    log = git_log(repo, commit)

    hotspots = hotspot_rows(py, log, run_ruff_c901())
    ex = extract(py)
    found = find_violations(ex)
    code, linter_text = run_lint_imports(ex.modules, repo)
    deps = parse_lint_imports(linter_text)
    size = _LINTER_SIZE_RE.search(linter_text)
    linter: dict[str, Json] = {
        "exit": code,
        "files_analysed": int(size["files"]) if size else 0,
        "dependencies_analysed": int(size["deps"]) if size else 0,
        "entries": len(deps),
        **compare_v1(found, deps),
    }
    index = string_index(py.values())
    dead = dead_code_rows(run_vulture(), index)
    rust_files, rust_crates = rust_rows(tracked, texts, log)

    summary = {
        "hotspots": write_hotspots(args.out, hotspots),
        "imports": write_imports(args.out, ex, grimp_edges(repo)),
        "violations": write_violations(args.out, ex, found, linter),
        "dead_code": write_dead_code(args.out, dead),
        "rust": write_rust(args.out, rust_files, rust_crates),
    }
    write_summary(args.out, summary)
    assert_tree_clean(repo)
    print(_dumps(summary))
    return 0


class Options(argparse.Namespace):
    out: Path = Path()


if __name__ == "__main__":
    sys.exit(main())
