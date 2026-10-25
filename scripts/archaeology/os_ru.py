"""OS-specific code and Russian specifics of legacy (Stage 1, TASK-7 criterion 5).

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.os_ru \
        --out docs/evidence/stage-1/os-ru

A rule-based scanner (ADR-0007 N8): ``ast`` and ``tokenize`` for Python, so that code, strings,
docstrings and comments are told apart, and line regexes for the other files. The script lists hits
with ``file:line``; it classifies and decides nothing. Recall is measured against ``git grep``.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, override

from scripts import legacy
from scripts.archaeology.common import (
    PYSPORT,
    Loc,
    UnparsedError,
    git_raw,
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

CORE_RANKS: Final = frozenset({1, 2})
KINDS: Final = ("code", "string", "docstring", "comment", "config")
RULES: Final = (
    "OS01",
    "OS02",
    "OS03",
    "OS04",
    "OS05",
    "OS06",
    "RU01",
    "RU02",
    "RU03",
    "RU04",
    "RU05",
)
RULE_TITLE: Final = {
    "OS01": "platform branches",
    "OS02": "OS-only modules",
    "OS03": "OS-only calls",
    "OS04": "OS paths and devices",
    "OS05": "dependency markers",
    "OS06": "Rust cfg",
    "RU01": "Cyrillic in Python strings, docstrings and comments",
    "RU02": "EVSK ranks and Qualification",
    "RU03": "Russian services and domains",
    "RU04": "Cyrillic encodings",
    "RU05": "Russian locale defaults",
}
MAX_WORD: Final = 40
SNIPPET: Final = 100
MD_LIST_CAP: Final = 30

# Rule patterns; the README repeats them verbatim

OS_ONLY_MODULES: Final = frozenset(
    {
        "winreg",
        "_winreg",
        "msvcrt",
        "pywintypes",
        "pythoncom",
        "wmi",
        "fcntl",
        "termios",
        "pwd",
        "grp",
        "pywinusb",
        "winsound",
    }
)
OS_ONLY_PREFIX: Final = "win32"
CTYPES_WINDOWS: Final = frozenset({"windll", "WinDLL", "oledll", "OleDLL", "WinError"})
OS01_NAMES: Final = frozenset({"sys.platform", "os.name", "sys.getwindowsversion"})
OS01_PLATFORM_ROOT: Final = "platform"
OS03_NAMES: Final = frozenset({"os.startfile", "os.add_dll_directory"})
OS03_SHELL_PREFIX: Final = "ShellExecute"
OS03_CALLS: Final = frozenset(
    {
        "os.system",
        "os.popen",
        "subprocess.run",
        "subprocess.call",
        "subprocess.Popen",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.getoutput",
        "Popen",
        "check_call",
        "check_output",
    }
)
OS03_FIRST_WORDS: Final = frozenset(
    {"open", "start", "xdg-open", "explorer", "explorer.exe", "cmd"}
)
OS03_TEXT: Final = re.compile(
    r"\bxdg-open\b|ShellExecute\w*|\bexplorer(?:\.exe)?\b|\bcmd(?:\.exe)?\s+/[ck]\b|\bos\.startfile\b"
)
OS04_TEXT: Final = (
    ("com", re.compile(r"\bCOM\d+\b")),
    ("tty", re.compile(r"/dev/(?:tty|cu\.|serial)[\w./-]*")),
    ("drive", re.compile(r"[A-Z]:\\")),
    ("ext", re.compile(r"\.(?:exe|bat|dll)\b", re.IGNORECASE)),
    ("env", re.compile(r"\b(?:APPDATA|LOCALAPPDATA|USERPROFILE|HOME|XDG_[A-Z_]+)\b")),
    ("backslash", re.compile(r"\w\\(?![ux][0-9a-fA-F]{2}|U[0-9a-fA-F]{8})[A-Za-z_]\w+")),
)
OS05_MARKER: Final = re.compile(r"\b(?:sys_platform|platform_system|os_name)\b")
OS05_PACKAGE: Final = re.compile(
    r"\b(?:pywin32-ctypes|pypiwin32|pywin32|pywinusb|pyimpinj|comtypes|wmi)\b", re.IGNORECASE
)
OS06_CFG: Final = re.compile(
    r"\bcfg(?:_attr)?!?\s*\([^\n]*?\b(windows|unix|target_os(?:\s*=\s*\"\w+\")?"
    r"|target_family(?:\s*=\s*\"\w+\")?)"
)
FIXTURE_DIRS: Final = ("tests/", "benches/")
TITLE_CASE: Final = re.compile(r"(?<![А-Яа-яЁё])[А-ЯЁ][а-яё]+")
CYRILLIC: Final = re.compile(r"[\u0400-\u04ff]")
RU02_TEXT: Final = re.compile(
    r"МСМК|ЗМС|(?<!\w)МС(?!\w)|(?<!\w)КМС(?!\w)|[Рр]азряд\w*|[Мм]астер\w* спорта|\bQualification\b"
)
RU03_DOMAIN: Final = re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:ru|рф)\b", re.IGNORECASE)
RU03_KEYWORD: Final = re.compile(
    r"orgeo|sportident\.ru|yandex|vk\.com|telegram|\bt\.me/", re.IGNORECASE
)
RU04_TEXT: Final = re.compile(r"cp-?1251|windows-1251|cp-?866|koi8(?:-?[ru])?", re.IGNORECASE)
RU05_SUBSTRING: Final = re.compile(r"Europe/Moscow|ru_RU|ru-RU")
RU05_WHOLE: Final = re.compile(r"(?:ru|RU|RUS|ru_RU|ru-RU|Europe/Moscow)")
RU05_QUOTED: Final = re.compile(r"[\"'](?:ru|RU|RUS|ru_RU|ru-RU)[\"']")
LOG_NAMES: Final = frozenset(
    {"print", "debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
)
UI_PREFIXES: Final = ("set", "add", "insert", "Q")
UI_NAMES: Final = frozenset({"tr", "_", "translate"})
PARENT_CATEGORY: Final = (
    ((ast.Raise,), "exception"),
    ((ast.Dict, ast.List, ast.Tuple, ast.Set), "data-literal"),
    ((ast.Compare,), "comparison"),
    ((ast.Assign, ast.AnnAssign), "assignment"),
    ((ast.arguments,), "default-argument"),
    ((ast.Return,), "return-value"),
)
SCANNED_SUFFIXES: Final = (".py", ".rs", ".toml", ".iss", ".spec", ".bat", ".ps1", ".sh")
SCANNED_NAMES: Final = ("Makefile", "uv.lock")
LINE_COMMENT: Final = {
    ".rs": ("//",),
    ".iss": (";", "//"),
    ".bat": ("rem ", "::"),
}
DEFAULT_COMMENT: Final = ("#",)


# ---------------------------------------------------------------- data


@dataclass(frozen=True, slots=True)
class Hit:
    rule: str
    path: str
    line: int
    layer: str
    rank: int
    kind: str
    token: str
    detail: str = ""
    end: int | None = None

    @property
    def core(self) -> bool:
        return self.rank in CORE_RANKS

    @property
    def loc(self) -> Loc:
        return Loc(PYSPORT, self.path, self.line, self.end)


@dataclass(slots=True)
class ScanResult:
    hits: list[Hit] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)
    text_lines: dict[str, set[int]] = field(default_factory=dict)
    scanned: int = 0


def layer_info(path: str) -> tuple[int, str]:
    if not path.endswith(".py") or not path.startswith("sportorg"):
        return -1, "outside"
    return layer_of(module_name(path)[0])


def is_scannable(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return path.endswith(SCANNED_SUFFIXES) or name in SCANNED_NAMES or path.startswith(".github/")


# ---------------------------------------------------------------- text rules


@dataclass(frozen=True, slots=True)
class TextMatch:
    rule: str
    token: str
    detail: str
    offset: int


def text_matches(text: str, kind: str) -> list[TextMatch]:
    """Rules that look at the text of a string, docstring, comment or config line."""
    found: list[TextMatch] = []
    found.extend(TextMatch("OS03", m.group(0), "", m.start()) for m in OS03_TEXT.finditer(text))
    for detail, pattern in OS04_TEXT:
        found.extend(
            TextMatch("OS04", m.group(0), detail, m.start()) for m in pattern.finditer(text)
        )
    found.extend(TextMatch("RU02", m.group(0), "", m.start()) for m in RU02_TEXT.finditer(text))
    found.extend(TextMatch("RU03", m.group(0), "", m.start()) for m in RU03_DOMAIN.finditer(text))
    found.extend(TextMatch("RU03", m.group(0), "", m.start()) for m in RU03_KEYWORD.finditer(text))
    found.extend(TextMatch("RU04", m.group(0), "", m.start()) for m in RU04_TEXT.finditer(text))
    found.extend(
        TextMatch("RU05", m.group(0), "", m.start()) for m in RU05_SUBSTRING.finditer(text)
    )
    if kind in {"string", "docstring"} and RU05_WHOLE.fullmatch(text):
        if not RU05_SUBSTRING.search(text):
            found.append(TextMatch("RU05", text, "whole-string", 0))
    elif kind == "comment":
        found.extend(
            TextMatch("RU05", m.group(0), "quoted", m.start()) for m in RU05_QUOTED.finditer(text)
        )
    return found


def safe_text(text: str, path: str) -> str:
    """Echo Cyrillic text only if it cannot be a person's name (AGENTS.md rule 8).

    Shown: one word of at most 40 characters, with no Title-case Cyrillic word, outside
    ``tests/`` and ``benches/`` (fixture data). Text without Cyrillic is returned unchanged.
    """
    if not CYRILLIC.search(text):
        return text
    fixture = path.startswith(FIXTURE_DIRS)
    if (
        not fixture
        and len(text.split()) == 1
        and len(text) <= MAX_WORD
        and not TITLE_CASE.search(text)
    ):
        return text
    return f"<text omitted: {len(text)} chars>"


# ---------------------------------------------------------------- Python


def _dotted(node: ast.expr) -> str | None:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def _is_os01(dotted: str | None) -> bool:
    if dotted is None:
        return False
    if dotted in OS01_NAMES:
        return True
    parts = dotted.split(".")
    return len(parts) == 2 and parts[0] == OS01_PLATFORM_ROOT  # noqa: PLR2004 - platform.<name>


def _os01_root(node: ast.expr) -> ast.Attribute | None:
    cur: ast.expr = node
    while True:
        if isinstance(cur, ast.Call):
            cur = cur.func
        elif isinstance(cur, ast.Attribute):
            if _is_os01(_dotted(cur)):
                return cur
            cur = cur.value
        else:
            return None


def _literals(nodes: Iterable[ast.expr]) -> str:
    values: list[str] = []
    for node in nodes:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
        elif isinstance(node, ast.Tuple | ast.List | ast.Set):
            values.extend(
                e.value
                for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)
            )
    return ",".join(values)


def _first_string(node: ast.expr) -> str | None:
    match node:
        case ast.Constant(value=str() as value):
            return value
        case ast.List(elts=[first, *_]) | ast.Tuple(elts=[first, *_]):
            return _first_string(first)
        case ast.JoinedStr(values=[first, *_]):
            return _first_string(first)
        case ast.BinOp(left=left):
            return _first_string(left)
        case _:
            return None


def _call_category(call: ast.Call) -> str:
    short = (_dotted(call.func) or "").rsplit(".", 1)[-1]
    if short in LOG_NAMES:
        return "log"
    if short.startswith(UI_PREFIXES) or short in UI_NAMES:
        return "ui"
    return "call-argument"


def _category(node: ast.AST, parents: dict[int, ast.AST]) -> str:
    """Guess of what a string is used for, from its nearest meaningful parent (not a verdict)."""
    cur = node
    for _ in range(5):
        parent = parents.get(id(cur))
        if parent is None:
            break
        if isinstance(parent, ast.Call):
            return _call_category(parent)
        for types, label in PARENT_CATEGORY:
            if isinstance(parent, types):
                return label
        cur = parent
    return "other"


class _Scanner(ast.NodeVisitor):
    def __init__(self, path: str, tree: ast.Module) -> None:
        self.path: str = path
        self.rank: int
        self.layer: str
        self.rank, self.layer = layer_info(path)
        self.hits: list[Hit] = []
        self._seen: set[tuple[str, int, str, str, str]] = set()
        self.lits: dict[int, str] = {}
        self.docstrings: set[int] = set()
        self.skip: set[int] = set()
        self.parents: dict[int, ast.AST] = {}
        self.string_lines: set[int] = set()
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self.parents[id(child)] = node
            self._prepare(node)

    def _prepare(self, node: ast.AST) -> None:
        if isinstance(node, ast.Compare):
            for operand in (node.left, *node.comparators):
                root = _os01_root(operand)
                if root is not None:
                    rest = [o for o in (node.left, *node.comparators) if o is not operand]
                    self.lits[id(root)] = _literals(rest)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"startswith", "endswith"}
        ):
            root = _os01_root(node.func.value)
            if root is not None:
                self.lits[id(root)] = _literals(node.args)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                self.docstrings.add(id(first.value))

    def emit(  # noqa: PLR0913, PLR0917 - one hit record, all fields are needed
        self, rule: str, line: int, kind: str, token: str, detail: str = "", end: int | None = None
    ) -> None:
        token = safe_text(token, self.path)
        detail = safe_text(detail, self.path)
        key = (rule, line, kind, token, detail)
        if key in self._seen:
            return
        self._seen.add(key)
        self.hits.append(
            Hit(rule, self.path, line, self.layer, self.rank, kind, token, detail, end)
        )

    # --- code

    @override
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._module(alias.name, node.lineno)

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        if node.level == 0 and mod:
            self._module(mod, node.lineno)
            for alias in node.names:
                if mod == "ctypes" and alias.name in CTYPES_WINDOWS:
                    self.emit("OS02", node.lineno, "code", f"ctypes.{alias.name}")
                if (mod, alias.name) in {
                    ("sys", "platform"),
                    ("sys", "getwindowsversion"),
                    ("os", "name"),
                }:
                    self.emit("OS01", node.lineno, "code", f"{mod}.{alias.name}", "import")
                if mod == OS01_PLATFORM_ROOT:
                    self.emit("OS01", node.lineno, "code", f"platform.{alias.name}", "import")
                if mod == "os" and alias.name in {"startfile", "add_dll_directory"}:
                    self.emit("OS03", node.lineno, "code", f"os.{alias.name}", "import")
                if alias.name == "Qualification":
                    self.emit("RU02", node.lineno, "code", "Qualification", "import")
        self.generic_visit(node)

    def _module(self, name: str, line: int) -> None:
        root = name.split(".", maxsplit=1)[0]
        if root in OS_ONLY_MODULES or root.startswith(OS_ONLY_PREFIX):
            self.emit("OS02", line, "code", name)

    @override
    def visit_Attribute(self, node: ast.Attribute) -> None:
        dotted = _dotted(node)
        if _is_os01(dotted) and dotted is not None:
            self.emit("OS01", node.lineno, "code", dotted, self.lits.get(id(node), ""))
        elif dotted in OS03_NAMES:
            self.emit("OS03", node.lineno, "code", dotted)
        elif dotted is not None and dotted.startswith("ctypes.") and node.attr in CTYPES_WINDOWS:
            self.emit("OS02", node.lineno, "code", dotted)
        if node.attr.startswith(OS03_SHELL_PREFIX):
            self.emit("OS03", node.lineno, "code", node.attr)
        if isinstance(node.value, ast.Name) and node.value.id == "Qualification":
            self.skip.add(id(node.value))
            self.emit("RU02", node.lineno, "code", f"Qualification.{node.attr}")
        self.generic_visit(node)

    @override
    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "Qualification" and id(node) not in self.skip:
            self.emit("RU02", node.lineno, "code", "Qualification")
        if node.id.startswith(OS03_SHELL_PREFIX):
            self.emit("OS03", node.lineno, "code", node.id)

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.name == "Qualification":
            self.emit("RU02", node.lineno, "code", "class Qualification", "definition")
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            self.emit(
                                "RU02",
                                stmt.lineno,
                                "code",
                                f"Qualification.{target.id}",
                                "definition",
                            )
        self.generic_visit(node)

    @override
    def visit_Call(self, node: ast.Call) -> None:
        if _dotted(node.func) in OS03_CALLS and node.args:
            first = _first_string(node.args[0])
            word = first.split()[0] if first and first.split() else ""
            if word in OS03_FIRST_WORDS:
                self.emit("OS03", node.lineno, "code", word, "command")
        self.generic_visit(node)

    # --- strings

    @override
    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, str):
            return
        text = node.value
        end = node.end_lineno or node.lineno
        kind = "docstring" if id(node) in self.docstrings else "string"
        self.string_lines.update(range(node.lineno, end + 1))
        for m in text_matches(text, kind):
            line = min(node.lineno + text.count("\n", 0, m.offset), end)
            self.emit(m.rule, line, kind, m.token, m.detail)
        if CYRILLIC.search(text):
            category = "docstring" if kind == "docstring" else _category(node, self.parents)
            self.emit(
                "RU01",
                node.lineno,
                kind,
                text,
                category,
                end if end != node.lineno else None,
            )


def _comments(source: str) -> list[tuple[int, str]]:
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return [
        (tok.start[0], tok.string.removeprefix("#").strip())
        for tok in tokens
        if tok.type == tokenize.COMMENT
    ]


def scan_python(path: str, source: str) -> list[Hit]:
    return _scan_python(path, source)[0]


def _scan_python(path: str, source: str) -> tuple[list[Hit], set[int]]:
    tree, _ = parse_source(source, path)
    scanner = _Scanner(path, tree)
    scanner.visit(tree)
    text_lines = set(scanner.string_lines)
    for line, text in _comments(source):
        text_lines.add(line)
        for m in text_matches(text, "comment"):
            scanner.emit(m.rule, line, "comment", m.token, m.detail)
        if CYRILLIC.search(text):
            scanner.emit("RU01", line, "comment", text, "comment")
    return scanner.hits, text_lines


# ---------------------------------------------------------------- other files


def _line_kind(path: str, line: str) -> str:
    suffix = Path(path).suffix
    prefixes = LINE_COMMENT.get(suffix, DEFAULT_COMMENT)
    stripped = line.lstrip().lower() if suffix == ".bat" else line.lstrip()
    if stripped.startswith(prefixes):
        return "comment"
    return "code" if suffix == ".rs" else "config"


def scan_text_file(path: str, text: str) -> list[Hit]:
    """Line regexes over a non-Python file (config, installer, build script, Rust)."""
    hits: list[Hit] = []
    seen: set[tuple[str, int, str, str]] = set()
    name = path.rsplit("/", 1)[-1]
    markers = path.endswith(".toml") or name == "uv.lock"
    for number, line in enumerate(physical_lines(text), start=1):
        kind = _line_kind(path, line)
        found = [
            (m.rule, m.token, m.detail)
            for m in text_matches(line, kind)
            if m.rule in {"OS03", "OS04", "RU03", "RU04"}
        ]
        if markers:
            found += [("OS05", m.group(0), "marker") for m in OS05_MARKER.finditer(line)]
            found += [("OS05", m.group(0), "package") for m in OS05_PACKAGE.finditer(line)]
        if path.endswith((".rs", ".toml")):
            found += [("OS06", m.group(1), "") for m in OS06_CFG.finditer(line)]
        for rule, token, detail in found:
            if (rule, number, token, detail) not in seen:
                seen.add((rule, number, token, detail))
                hits.append(
                    Hit(rule, path, number, "outside", -1, kind, safe_text(token, path), detail)
                )
    return hits


def scan_files(files: dict[str, str]) -> ScanResult:
    result = ScanResult()
    for path in sorted(files):
        result.scanned += 1
        if path.endswith(".py"):
            try:
                hits, lines = _scan_python(path, files[path])
            except UnparsedError:
                result.unparsed.append(path)
                continue
            result.hits.extend(hits)
            result.text_lines[path] = lines
        else:
            result.hits.extend(scan_text_file(path, files[path]))
    result.hits.sort(key=lambda h: (h.rule, not h.core, h.path, h.line, h.kind, h.token, h.detail))
    return result


# ---------------------------------------------------------------- legacy snapshot


def load_files(name: str = PYSPORT) -> tuple[dict[str, str], list[str]]:
    repo, commit = repo_root(name), legacy.find_pin(name).commit
    files: dict[str, str] = {}
    skipped: list[str] = []
    for path in tracked_files(repo):
        if not is_scannable(path):
            continue
        try:
            files[path] = git_raw(repo, "show", f"{commit}:{path}")
        except legacy.LegacyError, UnicodeDecodeError:
            skipped.append(path)
    return files, skipped


# ---------------------------------------------------------------- recall against git grep


@dataclass(frozen=True, slots=True)
class RecallSpec:
    name: str
    pattern: str
    rule: str
    detail: str | None = None  # restrict scanner hits to this detail, if any
    ignore_case: bool = False
    code_rule: bool = False  # the scanner ignores comments and strings for this rule


RECALL_SPECS: Final = (
    RecallSpec(
        name="OS01",
        pattern=r"sys\.platform|\bos\.name\b|\bplatform\.[A-Za-z_]+|getwindowsversion",
        rule="OS01",
        code_rule=True,
    ),
    RecallSpec(
        name="OS02",
        pattern=(
            r"^[[:space:]]*(import|from)[[:space:]]+(winreg|_winreg|msvcrt|win32[A-Za-z_0-9]*"
            r"|pywintypes|pythoncom|wmi|fcntl|termios|pwd|grp|pywinusb|winsound)\b"
            r"|ctypes\.(windll|WinDLL)"
        ),
        rule="OS02",
        code_rule=True,
    ),
    RecallSpec(name="OS04-com", pattern=r"\bCOM[0-9]+\b", rule="OS04", detail="com"),
    RecallSpec(name="OS04-drive", pattern=r"[A-Z]:\\", rule="OS04", detail="drive"),
    RecallSpec(
        name="RU04",
        pattern=r"cp-?1251|windows-1251|cp-?866|koi8",
        rule="RU04",
        ignore_case=True,
    ),
    RecallSpec(
        name="RU05",
        pattern=r"[\"'](ru|RU|RUS|ru_RU|ru-RU)[\"']|Europe/Moscow|ru_RU|ru-RU",
        rule="RU05",
    ),
)
_GREP_LINE: Final = re.compile(r"^[0-9a-f]{40}:(.+?):(\d+):")


def compare_sets(
    grep: set[tuple[str, int]], ours: set[tuple[str, int]]
) -> tuple[list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]]]:
    return sorted(grep & ours), sorted(grep - ours), sorted(ours - grep)


def grep_lines(repo: Path, commit: str, spec: RecallSpec) -> set[tuple[str, int]]:
    flags = ["-n", "-I", "-E", *(["-i"] if spec.ignore_case else [])]
    try:
        out = git_raw(repo, "grep", *flags, spec.pattern, commit, "--", "*.py")
    except legacy.LegacyError as exc:
        if str(exc).endswith(": "):  # git grep exits 1 without output when nothing matches
            return set()
        raise
    found: set[tuple[str, int]] = set()
    for row in out.splitlines():
        m = _GREP_LINE.match(row)
        if m:
            found.add((m.group(1), int(m.group(2))))
    return found


def _snippet(files: dict[str, str], path: str, line: int) -> str:
    lines = physical_lines(files.get(path, ""))
    return lines[line - 1].strip()[:SNIPPET] if 0 < line <= len(lines) else ""


def recall(
    files: dict[str, str], result: ScanResult, repo: Path, commit: str
) -> dict[str, dict[str, Json]]:
    report: dict[str, dict[str, Json]] = {}
    for spec in RECALL_SPECS:
        grep = grep_lines(repo, commit, spec)
        ours = {
            (h.path, h.line)
            for h in result.hits
            if h.rule == spec.rule
            and h.path.endswith(".py")
            and (spec.detail is None or h.detail == spec.detail)
        }
        both, only_grep, only_ours = compare_sets(grep, ours)

        def reason_grep(path: str, line: int, spec: RecallSpec = spec) -> str:
            if path in result.unparsed:
                return "file not parsed by ast"
            if spec.code_rule and line in result.text_lines.get(path, set()):
                return "text mention (comment, docstring or string); the rule reads code only"
            return "different token (alias, multi-token import, escaped or split literal)"

        def entry(path: str, line: int, why: str) -> Json:
            return {
                "tag": Loc(PYSPORT, path, line).tag(),
                "reason": why,
                "snippet": _snippet(files, path, line),
            }

        report[spec.name] = {
            "pattern": spec.pattern + (" (-i)" if spec.ignore_case else ""),
            "grep": len(grep),
            "scanner": len(ours),
            "both": len(both),
            "only_grep": [entry(p, n, reason_grep(p, n)) for p, n in only_grep],
            "only_scanner": [
                entry(p, n, "scanner token or line offset not matched by the grep pattern")
                for p, n in only_ours
            ],
        }
    return report


# ---------------------------------------------------------------- outputs


def _as_json(hit: Hit) -> Json:
    return {
        "rule": hit.rule,
        "layer": hit.layer,
        "core": hit.core,
        "kind": hit.kind,
        "token": hit.token,
        "detail": hit.detail,
        "tag": hit.loc.tag(),
    }


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def hits_table(hits: Sequence[Hit]) -> str:
    rows: list[str] = []
    for rule in RULES:
        group = [h for h in hits if h.rule == rule]
        rows += [
            f"## {rule} {RULE_TITLE[rule]}: {len(group)} hits, {sum(h.core for h in group)} core",
            "",
            "| core | layer | kind | token | detail | location |",
            "|---|---|---|---|---|---|",
        ]
        ordered = sorted(group, key=lambda h: (not h.core, h.path, h.line, h.kind, h.token))
        rows += [
            f"| {'yes' if h.core else 'no'} | {h.layer} | {h.kind} | `{_cell(h.token)}` |"
            f" {_cell(h.detail)} | {h.loc.tag()} |"
            for h in ordered
        ]
        rows.append("")
    return "\n".join(rows)


def summary(result: ScanResult) -> dict[str, dict[str, dict[str, int]]]:
    table: dict[str, dict[str, dict[str, int]]] = {}
    for rule in RULES:
        table[rule] = {"core": dict.fromkeys(KINDS, 0), "outside": dict.fromkeys(KINDS, 0)}
    for hit in result.hits:
        table[hit.rule]["core" if hit.core else "outside"][hit.kind] += 1
    return table


def counts_json(table: dict[str, dict[str, dict[str, int]]]) -> Json:
    out: dict[str, Json] = {}
    for rule, scopes in table.items():
        out[rule] = {scope: dict(counts) for scope, counts in scopes.items()}
    return out


def summary_table(table: dict[str, dict[str, dict[str, int]]]) -> str:
    rows = [
        "| rule | scope | " + " | ".join(KINDS) + " | total |",
        "|---|---|" + "---|" * (len(KINDS) + 1),
    ]
    for rule in RULES:
        for scope in ("core", "outside"):
            counts = table[rule][scope]
            cells = " | ".join(str(counts[k]) for k in KINDS)
            rows.append(f"| {rule} | {scope} | {cells} | {sum(counts.values())} |")
    return "\n".join(rows)


def layer_counts(result: ScanResult) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {rule: {} for rule in RULES}
    for hit in result.hits:
        counts[hit.rule][hit.layer] = counts[hit.rule].get(hit.layer, 0) + 1
    return counts


def recall_table(report: dict[str, dict[str, Json]]) -> str:
    rows = [
        "| rule | grep lines | scanner lines | both | only grep | only scanner |",
        "|---|---|---|---|---|---|",
    ]
    for name, data in report.items():
        only_grep, only_scanner = data["only_grep"], data["only_scanner"]
        assert isinstance(only_grep, list)  # noqa: S101 - narrowing for the type checker
        assert isinstance(only_scanner, list)  # noqa: S101 - narrowing for the type checker
        rows.append(
            f"| {name} | {data['grep']} | {data['scanner']} | {data['both']} |"
            f" {len(only_grep)} | {len(only_scanner)} |"
        )
    for name, data in report.items():
        for key in ("only_grep", "only_scanner"):
            items = data[key]
            assert isinstance(items, list)  # noqa: S101 - narrowing for the type checker
            if not items:
                continue
            rows += ["", f"### {name}: {key.replace('_', ' ')} ({len(items)})", ""]
            for item in items[:MD_LIST_CAP]:
                assert isinstance(item, dict)  # noqa: S101 - narrowing for the type checker
                rows.append(f"- {item['tag']} {item['reason']}: `{_cell(str(item['snippet']))}`")
            if len(items) > MD_LIST_CAP:
                rows.append(f"- ... {len(items) - MD_LIST_CAP} more in recall.json")
    return "\n".join(rows)


def _p(*parts: str) -> str:
    return "".join(parts)


def _codes(items: Iterable[str]) -> str:
    return ", ".join(f"`{item}`" for item in items)


def _rule_rows() -> list[str]:
    ctypes_names = _codes(f"ctypes.{n}" for n in sorted(CTYPES_WINDOWS))
    return [
        _p(
            "| OS01 | platform branches | ast dotted names ",
            _codes(sorted(OS01_NAMES)),
            ", `platform.<name>`; `from sys import platform`, `from os import name`;",
            " compared literal in `detail` (`==`, `in`, `.startswith`) |",
        ),
        _p(
            "| OS02 | OS-only modules | imports of ",
            _codes(sorted(OS_ONLY_MODULES)),
            f", `{OS_ONLY_PREFIX}*`; ",
            ctypes_names,
            " (import and attribute) |",
        ),
        _p(
            "| OS03 | OS-only calls | ast ",
            _codes(sorted(OS03_NAMES)),
            f", names starting `{OS03_SHELL_PREFIX}`; first word ",
            _codes(sorted(OS03_FIRST_WORDS)),
            " of the first argument of ",
            _codes(sorted(OS03_CALLS)),
            f"; text regex `{OS03_TEXT.pattern}` |",
        ),
        _p(
            "| OS04 | OS paths and devices | text regexes ",
            "; ".join(f"{d}: `{p.pattern}`" for d, p in OS04_TEXT),
            " |",
        ),
        _p(
            f"| OS05 | dependency markers | `{OS05_MARKER.pattern}` and packages",
            f" `{OS05_PACKAGE.pattern}` (case-insensitive) in `*.toml`, `uv.lock` |",
        ),
        f"| OS06 | Rust cfg | `{OS06_CFG.pattern}` in `*.rs`, `*.toml` |",
        _p(
            f"| RU01 | Cyrillic | `{CYRILLIC.pattern}` in a string, docstring or comment; token",
            " shown only if one word of at most 40 characters, else `<text omitted: N chars>`;",
            " `detail` is a guess (log, exception, ui, data-literal, comparison, assignment, ...)",
            " from the parent node |",
        ),
        _p(
            "| RU02 | EVSK ranks | ast `Qualification`, `Qualification.<member>`, class",
            f" `Qualification` members; text `{RU02_TEXT.pattern}` |",
        ),
        _p(
            f"| RU03 | Russian services | domains `{RU03_DOMAIN.pattern}`, keywords",
            f" `{RU03_KEYWORD.pattern}` (case-insensitive; `telegram` is not checked for being",
            " bound to a Russian service) |",
        ),
        f"| RU04 | Cyrillic encodings | `{RU04_TEXT.pattern}` (case-insensitive) |",
        _p(
            f"| RU05 | Russian locale defaults | substrings `{RU05_SUBSTRING.pattern}`;",
            f" whole strings `{RU05_WHOLE.pattern}`; in comments quoted `{RU05_QUOTED.pattern}` |",
        ),
    ]


def readme(result: ScanResult, skipped: list[str], report: dict[str, dict[str, Json]]) -> str:
    pin = pin_short(PYSPORT)
    unparsed = ", ".join(result.unparsed) or "none"
    lines = [
        f"# os-ru: OS-specific code and Russian specifics of pysport@{pin}",
        "",
        _p(
            "Produced by `scripts/archaeology/os_ru.py` (commands in `commands.txt`). The script",
            " lists hits with `file:line`; it classifies nothing (the agent classifies them in",
            " `classification.agent.md`, TASK-7 criterion 5). Files: `hits.{json,md}` (all hits,",
            " core first), `summary.{json,md}` (rule x core/outside x kind), `recall.{json,md}`",
            " (against `git grep`).",
        ),
        "",
        "## Definitions",
        "",
        _p(
            "- core = layer rank 1 or 2 (`foundation`, `domain`) by `common.layer_of` on the",
            " module name; `sportorg.libs` (rank 0), gui, modules, startup and every file outside",
            " `sportorg/` are not core.",
        ),
        _p(
            "- kind: `code` (ast node), `string`, `docstring`, `comment` (tokenize), `config`",
            " (line of a non-Python file; Rust lines are `code`, comment lines `comment`).",
        ),
        _p(
            "- Python strings are scanned per constant (f-string parts separately); a match in a",
            " multi-line string is placed at its line inside the string, RU01 at the string start.",
        ),
        "",
        "## Rules and exact patterns",
        "",
        "| rule | what | patterns |",
        "|---|---|---|",
        *_rule_rows(),
        "",
        _p(
            "Scope: tracked `*.py`, `*.rs`, `*.toml`, `*.iss`, `*.spec`, `*.bat`, `*.ps1`, `*.sh`,",
            " `Makefile`, `uv.lock`, `.github/**`. Non-Python files get OS03, OS04, RU03, RU04",
            " (and OS05, OS06 where they apply); RU01, RU02, RU05 and ast rules are Python only.",
        ),
        "",
        "## Key numbers",
        "",
        _p(
            f"- files scanned: {result.scanned}; unparsed by ast: {len(result.unparsed)}",
            f" ({unparsed}); undecodable: {len(skipped)}; hits: {len(result.hits)}.",
        ),
        "",
        summary_table(summary(result)),
        "",
        "## Recall against git grep (line level, `*.py`)",
        "",
        recall_table(report),
        "",
        "## Limits",
        "",
        _p(
            "- Aliases (`import platform as p`, `from os import name as n` used later) are not",
            " followed; only the import line is a hit.",
        ),
        _p(
            "- Dynamic strings (concatenation, `format`, `chr`) are not evaluated; the backslash",
            " path join is a noisy regex (it also hits some regex-like strings).",
        ),
        _p(
            "- `HOME` in OS04 matches the word in any string or comment; line numbers inside",
            " multi-line strings count `\\n` in the decoded value (escapes in non-raw strings can",
            " shift them).",
        ),
        _p(
            "- A hit is a place to look at, not a verdict: nothing here says whether the code is",
            " reachable, guarded by a fallback, or a false positive.",
        ),
    ]
    return "\n".join(lines)


class Options(argparse.Namespace):
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    files, skipped = load_files()
    result = scan_files(files)
    repo, commit = repo_root(PYSPORT), legacy.find_pin(PYSPORT).commit
    report = recall(files, result, repo, commit)
    pin = pin_short(PYSPORT)
    intro = f"Produced by `scripts/archaeology/os_ru.py` on pysport@{pin}; see README.md."
    write_outputs(
        args.out,
        "hits",
        {"hits": [_as_json(h) for h in result.hits], "unparsed": list(result.unparsed)},
        hits_table(result.hits),
        f"# os-ru hits (core first)\n\n{intro}",
    )
    table = summary(result)
    summary_data: dict[str, Json] = {
        "counts": counts_json(table),
        "layers": {rule: dict(layers) for rule, layers in layer_counts(result).items()},
        "scanned": result.scanned,
        "unparsed": list(result.unparsed),
        "undecodable": list(skipped),
    }
    write_outputs(
        args.out,
        "summary",
        summary_data,
        summary_table(table),
        f"# os-ru summary: rule x core/outside x kind\n\n{intro}",
    )
    write_outputs(
        args.out,
        "recall",
        dict(report.items()),
        recall_table(report),
        f"# os-ru recall against git grep\n\n{intro}",
    )
    (args.out / "README.md").write_text(
        readme(result, skipped, report) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"hits: {len(result.hits)}; unparsed: {len(result.unparsed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
