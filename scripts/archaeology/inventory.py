"""Inventory of user-facing features of the legacy (Stage 1, TASK-7 criterion 1).

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.inventory \
        --out docs/evidence/stage-1/inventory

Static only: the menu literal is parsed with ``ast`` (never imported), legacy files are read with
``git show`` at the pin. Menu items added at run time (plugins) and imports under an alias are not
seen; the README of the evidence directory states these limits.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts import legacy
from scripts.archaeology.common import (
    PYSPORT,
    TEMPLATES,
    Loc,
    UnparsedError,
    git_raw,
    iter_imports,
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

MENU_PATH: Final = "sportorg/gui/menu/menu.py"
ACTIONS_PATH: Final = "sportorg/gui/menu/actions.py"
ACTIONS_MODULE: Final = "sportorg.gui.menu.actions"
FACTORY: Final = "ActionFactory"
MENU_KEYS: Final = frozenset({"title", "shortcut", "action", "actions"})
TEMPLATE_EXTENSIONS: Final = frozenset(
    {"html", "htm", "docx", "xlsx", "xls", "odt", "ods", "j2", "jinja", "jinja2", "tpl", "mustache"}
)
BINARY_EXTENSIONS: Final = frozenset({"docx", "xlsx", "xls", "odt", "ods"})
DOC_EXTENSIONS: Final = frozenset({"md", "rst"})
FILTER_RE: Final = re.compile(r"\*\.[A-Za-z0-9]+")
EXTENSION_RE: Final = re.compile(r"\.[A-Za-z0-9]{2,6}")
LOADER_PATTERNS: Final = (
    ("jinja2", re.compile(r"\bjinja2\b|\bFileSystemLoader\b|\bEnvironment\(")),
    ("docxtpl", re.compile(r"\bdocxtpl\b|\bDocxTemplate\b")),
    ("env_config", re.compile(r"TEMPLATES_PATH")),
    ("list_templates", re.compile(r"\bget_templates\(")),
    ("template_dir", re.compile(r"\btemplate_dir\(")),
    ("render_text", re.compile(r"\bget_text_from_(?:template|file)\(")),
    ("setting", re.compile(r"\btemplates_path\b|\bsplit_template\b")),
)
# [допущение]: module prefix -> format label, from the directory names of sportorg/modules and
# sportorg/libs; the longest matching prefix wins.
FORMAT_MODULES: Final = (
    ("sportorg.modules.iof", "IOF XML"),
    ("sportorg.libs.iof", "IOF XML"),
    ("sportorg.modules.winorient", "WinOrient (CSV, WDB)"),
    ("sportorg.libs.winorient", "WinOrient (CSV, WDB)"),
    ("sportorg.modules.ocad", "OCAD"),
    ("sportorg.libs.ocad", "OCAD"),
    ("sportorg.modules.sfr", "SFRx"),
    ("sportorg.libs.sfr", "SFRx"),
    ("sportorg.modules.backup", "SportOrg JSON (.json, gzip)"),
    ("sportorg.modules.recovery", "Recovery import (CSV, HTML, SI log)"),
    ("sportorg.gui.dialogs.report_dialog", "Report output (HTML, DOCX, CSV)"),
    ("sportorg.gui.dialogs.print_properties", "Report templates (HTML)"),
    ("sportorg.modules.printing", "Printing"),
)
READ_RE: Final = re.compile(r"^(?:read|import|parse|load|open|get_races)", re.IGNORECASE)
WRITE_RE: Final = re.compile(r"^(?:write|export|save|dump|create|build|make|send)", re.IGNORECASE)


class InventoryError(ValueError):
    """The legacy source does not have the expected shape."""


# ---------------------------------------------------------------- menu


@dataclass(frozen=True, slots=True)
class MenuItem:
    path: tuple[str, ...]
    title: str
    kind: str  # "action", "submenu" or "separator"
    shortcut: str
    action: str | None
    extra: dict[str, str]
    line: int


@dataclass(frozen=True, slots=True)
class ActionClass:
    name: str
    line: int
    end: int


@dataclass(frozen=True, slots=True)
class Resolution:
    resolved: dict[str, ActionClass]
    unresolved: list[str]
    unused: list[str]
    duplicates: list[str]


def _text(node: ast.expr) -> str:
    """Menu value: ``translate("X")`` gives ``X``, a string itself, anything else its source."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "translate"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        return node.args[0].value
    return ast.unparse(node)


def _entries(node: ast.Dict) -> dict[str, ast.expr]:
    return {
        key.value: value
        for key, value in zip(node.keys, node.values, strict=True)
        if isinstance(key, ast.Constant) and isinstance(key.value, str)
    }


def _walk_menu(nodes: Iterable[ast.expr], parent: tuple[str, ...]) -> list[MenuItem]:
    found: list[MenuItem] = []
    for node in nodes:
        if not isinstance(node, ast.Dict):
            continue
        entries = _entries(node)
        title = _text(entries["title"]) if "title" in entries else ""
        action = _text(entries["action"]) if "action" in entries else None
        is_separator = "type" in entries and _text(entries["type"]) == "separator"
        label = title or ("<separator>" if is_separator else "<untitled>")
        children = entries.get("actions")
        kind = "separator" if is_separator else "submenu" if children else "action"
        extra = {k: ast.unparse(v) for k, v in entries.items() if k not in MENU_KEYS}
        if "type" in extra and is_separator:
            del extra["type"]
        found.append(
            MenuItem(
                (*parent, label),
                title,
                kind,
                _text(entries["shortcut"]) if "shortcut" in entries else "",
                action,
                dict(sorted(extra.items())),
                node.lineno,
            )
        )
        if isinstance(children, ast.List):
            found.extend(_walk_menu(children.elts, (*parent, label)))
    return found


def parse_menu(source: str, path: str) -> list[MenuItem]:
    """Every node of the ``menu_list()`` literal, in source order."""
    tree, _ = parse_source(source, path)
    for func in tree.body:
        if isinstance(func, ast.FunctionDef) and func.name == "menu_list":
            for stmt in func.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.List):
                    return _walk_menu(stmt.value.elts, ())
    msg = f"{path}: no menu_list() function that assigns a list literal"
    raise InventoryError(msg)


def action_classes(source: str, path: str) -> list[ActionClass]:
    """Module-level classes registered by the ``ActionFactory`` metaclass (or inheriting it)."""
    tree, _ = parse_source(source, path)
    registered: set[str] = set()
    found: list[ActionClass] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        direct = any(
            kw.arg == "metaclass" and isinstance(kw.value, ast.Name) and kw.value.id == FACTORY
            for kw in node.keywords
        )
        inherited = any(isinstance(b, ast.Name) and b.id in registered for b in node.bases)
        if direct or inherited:
            registered.add(node.name)
            found.append(ActionClass(node.name, node.lineno, node.end_lineno or node.lineno))
    return found


def resolve_actions(items: Sequence[MenuItem], classes: Sequence[ActionClass]) -> Resolution:
    resolved = {c.name: c for c in classes}  # the registry keeps the last definition of a name
    used = {i.action for i in items if i.action}
    names = [c.name for c in classes]
    return Resolution(
        resolved={n: resolved[n] for n in sorted(resolved) if n in used},
        unresolved=sorted(used - resolved.keys()),
        unused=sorted(resolved.keys() - used),
        duplicates=sorted({n for n in names if names.count(n) > 1}),
    )


def _bindings(source: str, module: str, path: str) -> dict[str, str]:
    """Module-level imported name -> source module (the first binding wins; aliases not seen)."""
    bound: dict[str, str] = {}
    for ref in iter_imports(source, module, path=path):
        if ref.local:
            continue
        if ref.names:
            for name in ref.names:
                if name != "*":
                    bound.setdefault(name, ref.module)
        else:
            bound.setdefault(ref.module.split(".")[0], ref.module)
    return bound


def class_imports(
    source: str, module: str, path: str, classes: Sequence[ActionClass]
) -> dict[tuple[str, int], dict[str, str]]:
    """Per class (name, line): module-level imported names its body uses -> source modules."""
    bound = _bindings(source, module, path)
    tree, _ = parse_source(source, path)
    nodes = {n.lineno: n for n in tree.body if isinstance(n, ast.ClassDef)}
    uses: dict[tuple[str, int], dict[str, str]] = {}
    for cls in classes:
        names = {
            n.id
            for stmt in nodes[cls.line].body
            for n in ast.walk(stmt)
            if isinstance(n, ast.Name) and n.id in bound
        }
        uses[cls.name, cls.line] = {n: bound[n] for n in sorted(names)}
    return uses


def class_local_imports(
    source: str, module: str, path: str, classes: Sequence[ActionClass]
) -> dict[tuple[str, int], dict[str, str]]:
    """Per class (name, line): names imported inside functions of its body -> source modules."""
    refs = [r for r in iter_imports(source, module, path=path) if r.local]
    found: dict[tuple[str, int], dict[str, str]] = {}
    for cls in classes:
        bound: dict[str, str] = {}
        for ref in refs:
            if cls.line <= ref.line <= cls.end:
                for name in ref.names or (ref.module.split(".")[0],):
                    bound.setdefault(name, ref.module)
        found[cls.name, cls.line] = dict(sorted(bound.items()))
    return found


# ---------------------------------------------------------------- file formats


@dataclass(frozen=True, slots=True)
class FilterRef:
    label: str
    extensions: tuple[str, ...]
    path: str
    line: int


@dataclass(frozen=True, slots=True)
class ExtensionRef:
    text: str
    path: str
    line: int


@dataclass(frozen=True, slots=True)
class FormatChain:
    menu_path: tuple[str, ...]
    action: str
    class_line: int
    formats: tuple[str, ...]
    modules: tuple[str, ...]
    calls: tuple[str, ...]
    filters: tuple[FilterRef, ...]
    menu_line: int = 0


@dataclass(frozen=True, slots=True)
class FormatFunction:
    format: str
    path: str
    qualname: str
    line: int
    direction: str


def _strings(source: str, path: str) -> list[tuple[str, int]]:
    tree, _ = parse_source(source, path)
    found = [
        (node.value, node.lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    return sorted(found, key=lambda s: (s[1], s[0]))


def parse_filters(source: str, path: str) -> list[FilterRef]:
    """String literals that carry a ``*.ext`` pattern (Qt file-dialog filters)."""
    found: list[FilterRef] = []
    for value, line in _strings(source, path):
        patterns = [m.group(0) for m in FILTER_RE.finditer(value)]
        if patterns:
            extensions = tuple(dict.fromkeys(p[1:].lower() for p in patterns))
            found.append(FilterRef(value, extensions, path, line))
    return found


def parse_extension_strings(source: str, path: str) -> list[ExtensionRef]:
    """String literals that are exactly a file extension, e.g. ``".sfrx"``."""
    return [
        ExtensionRef(value, path, line)
        for value, line in _strings(source, path)
        if EXTENSION_RE.fullmatch(value)
    ]


def format_of(module: str) -> str | None:
    best = ""
    label: str | None = None
    for prefix, name in FORMAT_MODULES:
        if (module == prefix or module.startswith(prefix + ".")) and len(prefix) > len(best):
            best, label = prefix, name
    return label


def _dotted(node: ast.expr) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return ".".join([node.id, *reversed(parts)])
    return None


def format_chains(  # noqa: PLR0913 - one join over six inputs, all needed
    items: Sequence[MenuItem],
    resolution: Resolution,
    uses: dict[tuple[str, int], dict[str, str]],
    filters: Sequence[FilterRef],
    source: str,
    *,
    local: dict[tuple[str, int], dict[str, str]],
) -> list[FormatChain]:
    """Menu item -> action class -> format modules used, calls into them and dialog filters."""
    tree, _ = parse_source(source, ACTIONS_PATH)
    nodes = {n.lineno: n for n in tree.body if isinstance(n, ast.ClassDef)}
    chains: list[FormatChain] = []
    for item in items:
        cls = resolution.resolved.get(item.action or "")
        if cls is None:
            continue
        imported = {**uses[cls.name, cls.line], **local[cls.name, cls.line]}
        mapped = {name: mod for name, mod in imported.items() if format_of(mod)}
        formats = tuple(sorted({label for mod in mapped.values() if (label := format_of(mod))}))
        calls = tuple(
            sorted(
                {
                    dotted
                    for stmt in nodes[cls.line].body
                    for n in ast.walk(stmt)
                    if isinstance(n, ast.Call)
                    and (dotted := _dotted(n.func)) is not None
                    and dotted.split(".")[0] in mapped
                }
            )
        )
        inside = tuple(
            f for f in filters if f.path == ACTIONS_PATH and cls.line <= f.line <= cls.end
        )
        if formats or inside:
            chains.append(
                FormatChain(
                    item.path,
                    cls.name,
                    cls.line,
                    formats,
                    tuple(sorted(set(mapped.values()))),
                    calls,
                    inside,
                    item.line,
                )
            )
    return chains


def format_functions(source: str, module: str, path: str) -> list[FormatFunction]:
    """Reader/writer candidates (by name) defined in a format module."""
    label = format_of(module)
    if label is None:
        return []
    tree, _ = parse_source(source, path)
    found: list[FormatFunction] = []

    def visit(body: Sequence[ast.stmt], prefix: str) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit(node.body, f"{prefix}{node.name}.")
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                name = node.name.lstrip("_")
                direction = (
                    "read" if READ_RE.match(name) else "write" if WRITE_RE.match(name) else ""
                )
                if direction:
                    found.append(
                        FormatFunction(label, path, f"{prefix}{node.name}", node.lineno, direction)
                    )

    visit(tree.body, "")
    return found


# ---------------------------------------------------------------- templates and documents


@dataclass(frozen=True, slots=True)
class TemplateFile:
    path: str
    format: str
    lines: int | None
    size: int


@dataclass(frozen=True, slots=True)
class DocFile:
    path: str
    lines: int | None
    size: int


@dataclass(frozen=True, slots=True)
class LoaderRef:
    kind: str
    path: str
    line: int
    text: str


def _extension(path: str) -> str:
    return path.rsplit(".", 1)[1].lower() if "." in path.rsplit("/", 1)[-1] else ""


def _size(repo: Path, commit: str, path: str) -> int:
    return int(git_raw(repo, "cat-file", "-s", f"{commit}:{path}"))


def _line_count(repo: Path, commit: str, path: str) -> int | None:
    try:
        return len(physical_lines(git_raw(repo, "show", f"{commit}:{path}")))
    except UnicodeDecodeError:
        return None


def template_files(
    repo: Path, commit: str, tracked: Iterable[str], prefix: str = ""
) -> list[TemplateFile]:
    found: list[TemplateFile] = []
    for path in tracked:
        ext = _extension(path)
        if ext not in TEMPLATE_EXTENSIONS or not path.startswith(prefix):
            continue
        lines = None if ext in BINARY_EXTENSIONS else _line_count(repo, commit, path)
        found.append(TemplateFile(path, ext, lines, _size(repo, commit, path)))
    return sorted(found, key=lambda f: f.path)


def doc_files(repo: Path, commit: str, tracked: Iterable[str]) -> list[DocFile]:
    found: list[DocFile] = []
    for path in tracked:
        base = path.rsplit("/", 1)[-1].lower()
        if (
            path.startswith("docs/")
            or _extension(path) in DOC_EXTENSIONS
            or base.startswith("changelog")
        ):
            found.append(DocFile(path, _line_count(repo, commit, path), _size(repo, commit, path)))
    return sorted(found, key=lambda f: f.path)


def scan_template_loaders(source: str, path: str) -> list[LoaderRef]:
    """Lines of a Python file that locate, list or render templates (comments skipped)."""
    found: list[LoaderRef] = []
    for number, line in enumerate(physical_lines(source), start=1):
        if line.lstrip().startswith("#"):
            continue
        found.extend(
            LoaderRef(kind, path, number, line.strip())
            for kind, pattern in LOADER_PATTERNS
            if pattern.search(line)
        )
    return found


# ---------------------------------------------------------------- snapshot and rendering


@dataclass(frozen=True, slots=True)
class Snapshot:
    py: dict[str, str]
    pysport_tracked: list[str]
    templates_tracked: list[str]
    unparsed: list[str] = field(default_factory=list)


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _tag(repo: str, path: str, line: int) -> str:
    return Loc(repo, path, line).tag()


def _row(*cells: str) -> str:
    return "| " + " | ".join(_cell(c) for c in cells) + " |"


def _table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    head = [_row(*headers), _row(*("---" for _ in headers))]
    return "\n".join([*head, *(_row(*r) for r in rows)])


def _items_json(items: Sequence[MenuItem], resolution: Resolution) -> list[Json]:
    out: list[Json] = []
    for i in items:
        cls = resolution.resolved.get(i.action or "")
        extra: dict[str, Json] = dict(i.extra)
        out.append(
            {
                "path": list(i.path),
                "title_key": i.title,
                "kind": i.kind,
                "shortcut": i.shortcut,
                "action": i.action,
                "class_line": cls.line if cls else None,
                "extra": extra,
                "source": _tag(PYSPORT, MENU_PATH, i.line),
            }
        )
    return out


def _menu_table(items: Sequence[MenuItem], resolution: Resolution) -> str:
    rows: list[list[str]] = []
    for i in items:
        cls = resolution.resolved.get(i.action or "")
        extra = "; ".join(f"{k}={v}" for k, v in i.extra.items())
        rows.append(
            [
                " > ".join(i.path),
                i.kind,
                i.shortcut,
                i.action or "",
                _tag(PYSPORT, ACTIONS_PATH, cls.line) if cls else "",
                extra,
                _tag(PYSPORT, MENU_PATH, i.line),
            ]
        )
    return _table(
        [
            "menu path (translation keys)",
            "kind",
            "shortcut",
            "action",
            "class",
            "other keys",
            "item",
        ],
        rows,
    )


def _actions_table(
    resolution: Resolution, uses: dict[tuple[str, int], dict[str, str]]
) -> tuple[str, list[Json]]:
    rows: list[list[str]] = []
    data: list[Json] = []
    for name, cls in resolution.resolved.items():
        imported = uses[name, cls.line]
        rows.append(
            [
                name,
                _tag(PYSPORT, ACTIONS_PATH, cls.line),
                ", ".join(f"{n} ← {m}" for n, m in imported.items()),
            ]
        )
        data.append(
            {
                "class": name,
                "line": cls.line,
                "end": cls.end,
                "imports": dict(imported),
                "source": _tag(PYSPORT, ACTIONS_PATH, cls.line),
            }
        )
    return _table(["action class", "class", "module-level names used ← source module"], rows), data


def _chain_json(c: FormatChain) -> Json:
    return {
        "menu_path": list(c.menu_path),
        "action": c.action,
        "formats": list(c.formats),
        "modules": list(c.modules),
        "calls": list(c.calls),
        "filters": [
            {
                "label": f.label,
                "extensions": list(f.extensions),
                "source": _tag(PYSPORT, f.path, f.line),
            }
            for f in c.filters
        ],
        "class": _tag(PYSPORT, ACTIONS_PATH, c.class_line),
        "item": _tag(PYSPORT, MENU_PATH, c.menu_line),
    }


def _chains_table(chains: Sequence[FormatChain]) -> str:
    return _table(
        [
            "menu path",
            "action",
            "formats (by module)",
            "modules",
            "calls into them",
            "dialog filters",
            "class",
        ],
        [
            [
                " > ".join(c.menu_path),
                c.action,
                ", ".join(c.formats),
                ", ".join(c.modules),
                ", ".join(c.calls),
                "; ".join(f"{f.label} {_tag(PYSPORT, f.path, f.line)}" for f in c.filters),
                _tag(PYSPORT, ACTIONS_PATH, c.class_line),
            ]
            for c in chains
        ],
    )


@dataclass(frozen=True, slots=True)
class Collected:
    filters: list[FilterRef]
    extensions: list[ExtensionRef]
    functions: list[FormatFunction]
    loaders: list[LoaderRef]
    unparsed: list[str]


def collect(py: dict[str, str]) -> Collected:
    filters: list[FilterRef] = []
    extensions: list[ExtensionRef] = []
    functions: list[FormatFunction] = []
    loaders: list[LoaderRef] = []
    unparsed: list[str] = []
    for path, source in sorted(py.items()):
        try:
            if path.startswith("sportorg/"):
                filters.extend(parse_filters(source, path))
                extensions.extend(parse_extension_strings(source, path))
                functions.extend(format_functions(source, module_name(path)[0], path))
            loaders.extend(scan_template_loaders(source, path))
        except UnparsedError:
            unparsed.append(path)
    return Collected(filters, extensions, functions, loaders, unparsed)


def _json_files(files: Sequence[TemplateFile | DocFile], repo: str) -> list[Json]:
    return [
        {
            "path": f.path,
            "lines": f.lines,
            "size": f.size,
            "format": f.format if isinstance(f, TemplateFile) else _extension(f.path),
            "source": _tag(repo, f.path, 1) if f.lines else "",
        }
        for f in files
    ]


def _files_table(files: Sequence[TemplateFile | DocFile], repo: str) -> str:
    return _table(
        ["repo", "path", "format", "lines", "bytes", "source"],
        [
            [
                repo,
                f.path,
                f.format if isinstance(f, TemplateFile) else _extension(f.path),
                "" if f.lines is None else str(f.lines),
                str(f.size),
                _tag(repo, f.path, 1) if f.lines else "",
            ]
            for f in files
        ],
    )


def run(out: Path) -> None:
    py_repo, py_commit = repo_root(PYSPORT), legacy.find_pin(PYSPORT).commit
    tp_repo, tp_commit = repo_root(TEMPLATES), legacy.find_pin(TEMPLATES).commit
    py_tracked, tp_tracked = tracked_files(py_repo), tracked_files(tp_repo)
    py: dict[str, str] = {}
    for path in py_tracked:
        if path.endswith(".py"):
            py[path] = git_raw(py_repo, "show", f"{py_commit}:{path}")

    menu_source, actions_source = py[MENU_PATH], py[ACTIONS_PATH]
    items = parse_menu(menu_source, MENU_PATH)
    classes = action_classes(actions_source, ACTIONS_PATH)
    resolution = resolve_actions(items, classes)
    uses = class_imports(actions_source, ACTIONS_MODULE, ACTIONS_PATH, classes)
    local = class_local_imports(actions_source, ACTIONS_MODULE, ACTIONS_PATH, classes)
    seen = collect(py)
    chains = format_chains(items, resolution, uses, seen.filters, actions_source, local=local)
    pin = f"pysport@{pin_short(PYSPORT)}"

    kinds = [i.kind for i in items]
    menu_counts: dict[str, Json] = {
        "nodes": len(items),
        "actions": kinds.count("action"),
        "submenus": kinds.count("submenu"),
        "separators": kinds.count("separator"),
        "with_shortcut": sum(1 for i in items if i.shortcut),
        "with_feature": sum(1 for i in items if "feature" in i.extra),
        "distinct_action_names": len({i.action for i in items if i.action}),
        "resolved": len(resolution.resolved),
        "unresolved": len(resolution.unresolved),
        "unused_classes": len(resolution.unused),
        "duplicate_class_names": len(resolution.duplicates),
        "registered_classes": len(classes),
    }
    menu_data: dict[str, Json] = {
        "counts": menu_counts,
        "items": _items_json(items, resolution),
        "unresolved": list(resolution.unresolved),
        "unused_classes": [
            {"class": c.name, "source": _tag(PYSPORT, ACTIONS_PATH, c.line)}
            for c in classes
            if c.name in resolution.unused
        ],
        "duplicate_class_names": [
            {
                "class": n,
                "sources": [_tag(PYSPORT, ACTIONS_PATH, c.line) for c in classes if c.name == n],
            }
            for n in resolution.duplicates
        ],
    }
    extras = "\n".join(
        [
            f"Unresolved action names: {', '.join(resolution.unresolved) or 'none'}.",
            f"Unused action classes: {', '.join(resolution.unused) or 'none'}.",
            f"Class names defined twice: {', '.join(resolution.duplicates) or 'none'}.",
        ]
    )
    write_outputs(
        out,
        "menu",
        menu_data,
        _menu_table(items, resolution) + "\n\n" + extras,
        f"# Menu tree of {pin}\n\nParsed from the `menu_list()` literal "
        f"{_tag(PYSPORT, MENU_PATH, 1)} with `ast`; plugin items are added at run time"
        " and are not listed.",
    )

    actions_md, actions_data = _actions_table(resolution, uses)
    write_outputs(
        out,
        "actions",
        {"actions": actions_data},
        actions_md,
        f"# Action classes of {pin}\n\nResolved through the `ActionFactory` registry of "
        f"{_tag(PYSPORT, ACTIONS_PATH, 1)}; imports are the module-level names of actions.py"
        " used in the class body.",
    )

    tp_templates = template_files(tp_repo, tp_commit, tp_tracked)
    py_templates = template_files(py_repo, py_commit, py_tracked)
    loader_rows: list[Json] = [
        {"kind": r.kind, "text": r.text, "source": _tag(PYSPORT, r.path, r.line)}
        for r in seen.loaders
    ]
    write_outputs(
        out,
        "templates",
        {
            "templates_repo": _json_files(tp_templates, TEMPLATES),
            "pysport": _json_files(py_templates, PYSPORT),
            "loaders": loader_rows,
        },
        "\n\n".join(
            [
                "## Template files",
                _files_table(tp_templates, TEMPLATES),
                _files_table(py_templates, PYSPORT),
                "## Code that locates, lists or renders templates",
                _table(
                    ["kind", "code", "source"],
                    [[r.kind, r.text, _tag(PYSPORT, r.path, r.line)] for r in seen.loaders],
                ),
            ]
        ),
        f"# Report templates of templates@{pin_short(TEMPLATES)} and {pin}\n\n"
        "Format is the file extension; `lines` is empty for binary files.",
    )

    filter_rows: list[Json] = [
        {
            "label": f.label,
            "extensions": list(f.extensions),
            "source": _tag(PYSPORT, f.path, f.line),
        }
        for f in seen.filters
    ]
    ext_rows: list[Json] = [
        {"text": e.text, "source": _tag(PYSPORT, e.path, e.line)} for e in seen.extensions
    ]
    func_rows: list[Json] = [
        {
            "format": f.format,
            "function": f.qualname,
            "direction": f.direction,
            "source": _tag(PYSPORT, f.path, f.line),
        }
        for f in seen.functions
    ]
    chain_rows: list[Json] = [_chain_json(c) for c in chains]
    write_outputs(
        out,
        "formats",
        {
            "chains": chain_rows,
            "filters": filter_rows,
            "extension_strings": ext_rows,
            "functions": func_rows,
            "format_modules": [{"prefix": p, "format": n} for p, n in FORMAT_MODULES],
        },
        "\n\n".join(
            [
                "## Menu action to format chains",
                _chains_table(chains),
                "## Filters (`*.ext` string literals in sportorg/)",
                _table(
                    ["label", "extensions", "source"],
                    [
                        [f.label, " ".join(f.extensions), _tag(PYSPORT, f.path, f.line)]
                        for f in seen.filters
                    ],
                ),
                "## Extension strings",
                _table(
                    ["string", "source"],
                    [[e.text, _tag(PYSPORT, e.path, e.line)] for e in seen.extensions],
                ),
                "## Reader/writer candidates in format modules (by function name)",
                _table(
                    ["format", "function", "direction", "source"],
                    [
                        [f.format, f.qualname, f.direction, _tag(PYSPORT, f.path, f.line)]
                        for f in seen.functions
                    ],
                ),
            ]
        ),
        f"# Import/export formats of {pin}\n\nFormat labels come from the module table in "
        "`scripts/archaeology/inventory.py` (`FORMAT_MODULES`, an assumption)."
        " Protocol details are W5.",
    )

    py_docs = doc_files(py_repo, py_commit, py_tracked)
    tp_docs = doc_files(tp_repo, tp_commit, tp_tracked)
    write_outputs(
        out,
        "docs",
        {
            "pysport": _json_files(py_docs, PYSPORT),
            "templates_repo": _json_files(tp_docs, TEMPLATES),
        },
        _files_table(py_docs, PYSPORT)
        + "\n"
        + "\n".join(_files_table(tp_docs, TEMPLATES).splitlines()[2:]),
        f"# Documentation files of {pin} and templates@{pin_short(TEMPLATES)}\n\n"
        "`docs/`, `*.md`, `*.rst`, `changelog*`.",
    )

    print(
        f"menu: {menu_counts['actions']} actions, {menu_counts['submenus']} submenus, "
        f"{menu_counts['separators']} separators; unresolved {len(resolution.unresolved)}, "
        f"unused {len(resolution.unused)}"
    )
    print(
        f"templates: templates repo {len(tp_templates)}, pysport {len(py_templates)}; "
        f"loader lines {len(seen.loaders)}"
    )
    print(
        f"formats: chains {len(chains)}, filters {len(seen.filters)}, "
        f"extension strings {len(seen.extensions)}, functions {len(seen.functions)}"
    )
    print(f"docs: pysport {len(py_docs)}, templates repo {len(tp_docs)}")
    if seen.unparsed:
        print(f"unparsed: {', '.join(seen.unparsed)}")


class Options(argparse.Namespace):
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    run(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
