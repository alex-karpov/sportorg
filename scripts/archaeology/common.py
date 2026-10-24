"""Shared helpers for the Stage 1 legacy archaeology (read-only, stdlib only).

Legacy is read through ``git`` at the pins of ``legacy.toml`` and parsed with ``ast``; nothing here
writes under ``.legacy/``. Commit records carry no author fields (personal data, AGENTS.md rule 8).
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, override

from scripts import legacy

if TYPE_CHECKING:
    from scripts._json import Json

PYSPORT: Final = "pysport"
TEMPLATES: Final = "templates"
PIN_SHORT_LEN: Final = 7
LEGACY_BASE_ENV: Final = "ARCHAEOLOGY_LEGACY_BASE"

GIT_LOG_FORMAT: Final = "%x1e%H%x1f%P%x1f%as%x1f%s"
_RECORD: Final = "\x1e"
_FIELD: Final = "\x1f"
_HEADER_FIELDS: Final = 4
_NUMSTAT_FIELDS: Final = 3

_EOL_RE: Final = re.compile(r"\r\n|\r|\n")
_TAG_RE: Final = re.compile(r"\[код: (\w+)@([0-9a-f]{7}) (.+?):(\d+)(?:-(\d+))?\]")


class UnparsedError(ValueError):
    """A source file that ``ast`` cannot parse; reported in outputs, never dropped silently."""

    def __init__(self, path: str, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path: str = path
        self.reason: str = reason


class TreeNotCleanError(RuntimeError):
    """A run left tracked changes or untracked/ignored files in a repository."""


# ---------------------------------------------------------------- pins and tags


def repo_root(name: str) -> Path:
    """``.legacy/<name>``; ``ARCHAEOLOGY_LEGACY_BASE`` points the scripts at a canary copy instead.

    Canaries of the verification prompt modify a writable copy (``.legacy-run/``, made by
    ``scripts.legacy_clone``) and replace the pinned commit there with ``git replace``. The scripts
    keep reading ``<pin>:<path>``, so only the base directory changes.
    """
    base = os.environ.get(LEGACY_BASE_ENV)
    return legacy.checkout_dir(name, Path(base) if base else None)


def pin_short(name: str) -> str:
    return legacy.find_pin(name).commit[:PIN_SHORT_LEN]


@dataclass(frozen=True, slots=True)
class Loc:
    repo: str
    path: str
    line: int
    end: int | None = None

    def tag(self) -> str:
        span = f"{self.line}-{self.end}" if self.end is not None else str(self.line)
        return f"[код: {self.repo}@{pin_short(self.repo)} {self.path}:{span}]"


def parse_tags(text: str) -> list[Loc]:
    """Every ``[код: …]`` tag in ``text``; a tag at a commit other than the pin is an error."""
    locs: list[Loc] = []
    for match in _TAG_RE.finditer(text):
        repo, sha, path, line, end = match.groups()
        if sha != pin_short(repo):
            msg = f"tag {match.group(0)} is not at the pin {repo}@{pin_short(repo)}"
            raise ValueError(msg)
        locs.append(Loc(repo, path, int(line), int(end) if end is not None else None))
    return locs


def physical_lines(text: str) -> list[str]:
    """Lines as ``ast`` and editors number them: only CR, LF and CRLF end a line.

    ``str.splitlines`` also breaks at form feed, U+2028 and other separators, which would shift
    every ``file:line`` after them.
    """
    lines = _EOL_RE.split(text)
    return lines[:-1] if lines and not lines[-1] else lines


# ---------------------------------------------------------------- git history


@dataclass(frozen=True, slots=True)
class FileChange:
    path: str
    added: int | None  # None: binary file
    deleted: int | None


@dataclass(frozen=True, slots=True)
class Commit:
    sha: str
    parents: tuple[str, ...]
    date: str
    subject: str
    files: tuple[FileChange, ...]

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1


def _count(field: str) -> int | None:
    return None if field == "-" else int(field)


def parse_git_log(text: str) -> list[Commit]:
    """Parse ``git log --format=GIT_LOG_FORMAT --numstat --no-renames -z`` output."""
    commits: list[Commit] = []
    for record in text.split(_RECORD)[1:]:
        header, _, body = record.partition("\0")
        sha, parents, date, subject = header.split(_FIELD, _HEADER_FIELDS - 1)
        files: list[FileChange] = []
        for entry in body.lstrip("\n").split("\0"):
            if not entry:
                continue
            added, deleted, path = entry.split("\t", _NUMSTAT_FIELDS - 1)
            files.append(FileChange(path, _count(added), _count(deleted)))
        commits.append(Commit(sha, tuple(parents.split()), date, subject, tuple(files)))
    return commits


def git_raw(repo: Path, *args: str) -> str:
    """Run a read-only git command; unlike ``legacy.git`` the output is not stripped."""
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.quotepath=off", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)}: {result.stderr.strip()}"
        raise legacy.LegacyError(msg)
    return result.stdout


def git_log(repo: Path, *rev: str) -> list[Commit]:
    """Commits reachable from ``rev`` (default ``HEAD``), newest first, with numstat."""
    return parse_git_log(
        git_raw(repo, "log", f"--format={GIT_LOG_FORMAT}", "--numstat", "--no-renames", "-z", *rev)
    )


def tracked_files(repo: Path, pattern: str = "*") -> list[str]:
    out = git_raw(repo, "ls-files", "-z", "--", pattern)
    return sorted(name for name in out.split("\0") if name)


def assert_tree_clean(repo: Path) -> None:
    status = git_raw(repo, "status", "--porcelain", "--ignored", "-z")
    if status:
        entries = ", ".join(sorted(e for e in status.split("\0") if e))
        msg = f"{repo} is not clean after the run: {entries}"
        raise TreeNotCleanError(msg)


# ---------------------------------------------------------------- modules and layers


def module_of(path: str) -> str:
    """Module bucket of a path for history counts (plan, "Defect rule and taxonomy")."""
    parts = path.split("/")
    match parts:
        case ["sportorg", pkg, sub, _, *_]:
            return f"sportorg.{pkg}.{sub}"
        case ["sportorg", pkg, _]:
            return f"sportorg.{pkg}"
        case ["sportorg", _]:
            return "sportorg"
        case ["crates", name, *_]:
            return f"crates.{name}"
        case ["tests", *_]:
            return "tests"
        case _:
            return "other"


def module_name(path: str) -> tuple[str, bool]:
    """Dotted module name of a ``.py`` path and whether it is a package ``__init__``."""
    parts = path.removesuffix(".py").split("/")
    if parts[-1] == "__init__":
        return ".".join(parts[:-1]), True
    return ".".join(parts), False


# (rank, layer, module prefixes); the legacy layer model of the plan, approved 2026-10-25.
_LAYERS: Final = (
    (5, "entry", ("sportorg.startup",)),
    (4, "ui", ("sportorg.gui",)),
    (3, "application", ("sportorg.modules", "sportorg.rust_example")),
    (2, "domain", ("sportorg.models",)),
    (0, "vendored", ("sportorg.libs",)),
    (
        1,
        "foundation",
        (
            "sportorg.common",
            "sportorg.utils",
            "sportorg.config",
            "sportorg.settings",
            "sportorg.language",
            "sportorg.paths",
        ),
    ),
)


def layer_of(module: str) -> tuple[int, str]:
    """Layer rank and name of a dotted module; anything outside the model is ``(-1, "outside")``."""
    if module == "sportorg":
        return 1, "foundation"
    for rank, name, prefixes in _LAYERS:
        if any(module == p or module.startswith(f"{p}.") for p in prefixes):
            return rank, name
    return -1, "outside"


# ---------------------------------------------------------------- import extraction


@dataclass(frozen=True, slots=True)
class ImportRef:
    module: str
    names: tuple[str, ...]
    line: int
    local: bool  # inside a function body


def _resolve(node: ast.ImportFrom, module: str, *, is_package: bool) -> str:
    if node.level == 0:
        return node.module or ""
    base = module.split(".") if is_package else module.split(".")[:-1]
    base = base[: len(base) - (node.level - 1)]
    return ".".join([*base, *([node.module] if node.module else [])])


class _Collector(ast.NodeVisitor):
    def __init__(self, module: str, *, is_package: bool) -> None:
        self.module: str = module
        self.is_package: bool = is_package
        self.depth: int = 0
        self.refs: list[ImportRef] = []

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function(node)

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function(node)

    @override
    def visit_Import(self, node: ast.Import) -> None:
        self.refs.extend(
            ImportRef(alias.name, (), node.lineno, local=self.depth > 0) for alias in node.names
        )

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        target = _resolve(node, self.module, is_package=self.is_package)
        names = tuple(alias.name for alias in node.names)
        self.refs.append(ImportRef(target, names, node.lineno, local=self.depth > 0))


def parse_source(source: str, path: str) -> tuple[ast.Module, list[str]]:
    """Parse one module; ``SyntaxWarning`` s are returned as ``path:line: message``, not printed."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", SyntaxWarning)
        try:
            tree = ast.parse(source, filename=path)
        except (SyntaxError, ValueError) as exc:
            raise UnparsedError(path, str(exc)) from exc
    found = [
        f"{path}:{w.lineno}: {w.message}" for w in caught if issubclass(w.category, SyntaxWarning)
    ]
    return tree, found


def iter_imports(
    source: str, module: str, *, is_package: bool = False, path: str = "<string>"
) -> list[ImportRef]:
    """Imports of one module in source order, relative imports resolved against ``module``."""
    tree, _ = parse_source(source, path)
    collector = _Collector(module, is_package=is_package)
    collector.visit(tree)
    return collector.refs


# ---------------------------------------------------------------- outputs


def write_outputs(out_dir: Path, stem: str, data: Json, table_md: str, header: str) -> None:
    """Write ``<stem>.json`` (sorted keys) and ``<stem>.md`` (header + table), LF, final newline."""
    out_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    (out_dir / f"{stem}.json").write_text(text, encoding="utf-8", newline="\n")
    md = f"{header.rstrip()}\n\n{table_md.rstrip()}\n"
    (out_dir / f"{stem}.md").write_text(md, encoding="utf-8", newline="\n")
