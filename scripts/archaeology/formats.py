"""Readers and writers of files and devices in legacy, with their hard-coded values (Stage 1, W5).

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.formats \
        --out docs/evidence/stage-1/formats

An *I/O site* is a call that matches a rule of ``_API``/``_PREFIX``/``_METHODS`` below (or the
``open`` family), resolved through the import aliases of its module. One row is produced per
enclosing scope (function, class body or module level) that holds at least one site. Hard-coded
values are taken from the same scope only; nested functions are scopes of their own.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts import legacy
from scripts.archaeology.common import (
    PYSPORT,
    Loc,
    UnparsedError,
    git_raw,
    module_name,
    parse_source,
    physical_lines,
    pin_short,
    repo_root,
    tracked_files,
    write_outputs,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

    from scripts._json import Json

type Scope = ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
type ConstValue = str | bytes | int | float

VALUE_KINDS: Final = (
    "baudrate",
    "timeout",
    "encoding",
    "delimiter",
    "struct-format",
    "byte-constant",
    "offset-or-width",
    "url",
    "port",
    "extension",
    "other",
)
MODULE_SCOPE: Final = "<module>"
TEXT_LIMIT: Final = 80
EMAIL_RE: Final = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
URL_RE: Final = re.compile(r"^(?:https?|wss?|ftp)://|^\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?$")
PORT_RE: Final = re.compile(r"^(?:COM\d+|/dev/tty\S*|/dev/cu\.\S*)$")
BOT_TOKEN_RE: Final = re.compile(r"bot\d+:[\w-]+")
EXTENSIONS: Final = (
    "csv|xml|json|html?|txt|docx?|xlsx?|zip|gz|ini|cfg|log|xsd|xsl|po|mo|wav|mp3|"
    "sportorg|bak|tmp|dat|pdf|png|jpe?g|rtf|odt|ods|mdb|db"
)
EXT_RE: Final = re.compile(rf"^\*?\.[A-Za-z0-9]{{1,8}}$|\.(?:{EXTENSIONS})$|\*\.(?:{EXTENSIONS})\b")
ENCODINGS: Final = frozenset(
    {
        "utf-8",
        "utf8",
        "utf-8-sig",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "utf_8",
        "cp1251",
        "cp1252",
        "cp866",
        "cp1250",
        "windows-1251",
        "koi8-r",
        "ascii",
        "latin-1",
        "latin1",
        "iso-8859-1",
        "iso-8859-5",
        "mbcs",
        "gbk",
        "gb2312",
    }
)
# keyword -> value kind; ``host`` is reported as ``url``, ``newline`` as a delimiter
KEYWORD_KINDS: Final = {
    "baudrate": "baudrate",
    "baud": "baudrate",
    "timeout": "timeout",
    "read_timeout": "timeout",
    "write_timeout": "timeout",
    "inter_byte_timeout": "timeout",
    "connect_timeout": "timeout",
    "port": "port",
    "encoding": "encoding",
    "newline": "delimiter",
    "delimiter": "delimiter",
    "quotechar": "delimiter",
    "mode": "other",
    "url": "url",
    "host": "url",
}
NAME_TOKEN_KINDS: Final = {
    "BAUD": "baudrate",
    "BAUDRATE": "baudrate",
    "BAUDRATES": "baudrate",
    "TIMEOUT": "timeout",
    "ENCODING": "encoding",
    "CHARSET": "encoding",
    "PORT": "port",
    "URL": "url",
    "URI": "url",
    "HOST": "url",
    "ADDR": "url",
    "DELIMITER": "delimiter",
    "SEPARATOR": "delimiter",
    "SEP": "delimiter",
}
SIZE_TOKENS: Final = frozenset(
    {"SIZE", "LEN", "LENGTH", "WIDTH", "OFFSET", "COUNT", "MAX", "MIN", "SHIFT"}
)
WIDTH_CALLS: Final = frozenset(
    {"read", "readline", "recv", "to_bytes", "from_bytes", "ljust", "rjust", "zfill", "range"}
)
SOCKET_METHODS: Final = frozenset({"connect", "bind", "connect_ex", "sendto"})
HOST_PORT_LEN: Final = 2
SMALL_INTS: Final = frozenset({0, 1, -1})

# [допущение] receivers of device/stream method calls: the last part of a name or attribute chain,
# compared case-insensitively without leading underscores
DEVICE_VOCABULARY: Final = frozenset(
    {"serial", "ser", "port", "sock", "socket", "conn", "device", "dev", "reader", "station", "hid"}
)
SOCKET_VOCABULARY: Final = frozenset({"sock", "socket", "conn"})
# method of a device/stream object -> direction
DEVICE_METHODS: Final = {
    "read": "read",
    "readline": "read",
    "readlines": "read",
    "read_until": "read",
    "read_all": "read",
    "recv": "read",
    "recv_into": "read",
    "reset_input_buffer": "read",
    "set_raw_data_handler": "read",
    "write": "write",
    "flush": "write",
    "reset_output_buffer": "write",
    "send": "write",
    "sendall": "write",
    "send_output_report": "write",
    "send_feature_report": "write",
}
# path prefix -> device format of the protocol code under it (also the encoder/decoder contexts)
DEVICE_KINDS: Final = (
    ("sportorg/libs/sportiduino/", "Sportiduino serial"),
    ("sportorg/modules/sportiduino/", "Sportiduino serial"),
    ("sportorg/libs/sfr/", "SFR HID"),
    ("sportorg/modules/sfr/", "SFR HID"),
    ("sportorg/libs/srpid/", "SRPID serial"),
    ("sportorg/modules/srpid/", "SRPID serial"),
    ("sportorg/libs/huichang/", "Huichang serial"),
    ("sportorg/modules/huichang/", "Huichang serial"),
    ("sportorg/modules/sportident/", "SPORTident serial"),
    ("sportorg/modules/rfid_impinj/", "Impinj RFID"),
)
PROTOCOL_API: Final = "<protocol>"
# [допущение]: a function parameter with one of these names is a file object; its read/write
# methods are I/O sites of kind FILE_PARAMETER (e.g. ``dump(file)`` writing the .srb board)
FILE_VOCABULARY: Final = frozenset({"file", "f", "fp", "fh", "fd", "fobj", "stream"})
FILE_METHODS: Final = {
    "read": "read",
    "readline": "read",
    "readlines": "read",
    "write": "write",
    "writelines": "write",
}
FILE_PARAMETER: Final = "file object (parameter)"
BIT_OPS: Final = (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)
BYTE_OPS: Final = (*BIT_OPS, ast.Mult, ast.Add, ast.Sub, ast.FloorDiv, ast.Mod)

# (kind, direction) of exact resolved call names
_API: Final = {
    "csv.reader": ("CSV", "read"),
    "csv.DictReader": ("CSV", "read"),
    "csv.writer": ("CSV", "write"),
    "csv.DictWriter": ("CSV", "write"),
    "json.load": ("JSON", "read"),
    "json.loads": ("JSON", "read"),
    "json.dump": ("JSON", "write"),
    "json.dumps": ("JSON", "write"),
    "orjson.loads": ("JSON", "read"),
    "orjson.dumps": ("JSON", "write"),
    "xml.etree.ElementTree.parse": ("XML", "read"),
    "xml.etree.ElementTree.fromstring": ("XML", "read"),
    "xml.etree.ElementTree.XML": ("XML", "read"),
    "xml.etree.ElementTree.iterparse": ("XML", "read"),
    "xml.etree.ElementTree.tostring": ("XML", "write"),
    "xml.etree.ElementTree.dump": ("XML", "write"),
    "xml.etree.cElementTree.parse": ("XML", "read"),
    "xml.etree.cElementTree.fromstring": ("XML", "read"),
    "xml.etree.cElementTree.tostring": ("XML", "write"),
    "lxml.etree.parse": ("XML", "read"),
    "lxml.etree.fromstring": ("XML", "read"),
    "lxml.etree.XML": ("XML", "read"),
    "lxml.etree.XMLParser": ("XML", "read"),
    "lxml.etree.XMLSchema": ("XML", "read"),
    "lxml.etree.tostring": ("XML", "write"),
    "lxml.builder.ElementMaker": ("XML", "write"),
    "xml.dom.minidom.parse": ("XML", "read"),
    "xml.dom.minidom.parseString": ("XML", "read"),
    "serial.Serial": ("serial", "device"),
    "serial.serial_for_url": ("serial", "device"),
    "serial.tools.list_ports.comports": ("serial", "device"),
    "struct.pack": ("struct", "write"),
    "struct.pack_into": ("struct", "write"),
    "struct.unpack": ("struct", "read"),
    "struct.unpack_from": ("struct", "read"),
    "struct.iter_unpack": ("struct", "read"),
    "struct.calcsize": ("struct", "both"),
    "struct.Struct": ("struct", "both"),
    "docxtpl.DocxTemplate": ("docx", "read"),
    "docx.Document": ("docx", "read"),
    "jinja2.Environment": ("jinja2", "read"),
    "jinja2.FileSystemLoader": ("jinja2", "read"),
    "jinja2.Template": ("jinja2", "read"),
    "configparser.ConfigParser": ("INI", "both"),
    "configparser.RawConfigParser": ("INI", "both"),
    "polib.pofile": ("PO", "read"),
    "polib.mofile": ("PO", "read"),
    "playsound3.playsound": ("audio", "read"),
    "boltons.fileutils.atomic_save": ("binary file", "write"),
    "shutil.copy": ("file system", "write"),
    "shutil.copyfile": ("file system", "write"),
    "shutil.copy2": ("file system", "write"),
    "shutil.copytree": ("file system", "write"),
    "shutil.move": ("file system", "write"),
    "shutil.rmtree": ("file system", "write"),
    "requests.get": ("HTTP", "read"),
    "requests.head": ("HTTP", "read"),
    "requests.options": ("HTTP", "read"),
    "requests.post": ("HTTP", "write"),
    "requests.put": ("HTTP", "write"),
    "requests.patch": ("HTTP", "write"),
    "requests.delete": ("HTTP", "write"),
    "requests.request": ("HTTP", "both"),
    "requests.Session": ("HTTP", "both"),
}
# (prefix, kind, direction): any resolved call name below the prefix
_PREFIX: Final = (
    ("socket", "socket", "both"),
    ("aiohttp", "HTTP", "both"),
    ("sportident", "SPORTident lib", "device"),
    ("pywinusb.hid", "HID", "device"),
    ("pyImpinj", "Impinj RFID", "device"),
    ("win32print", "printer", "device"),
    ("win32ui", "printer", "device"),
    ("PySide6.QtPrintSupport", "printer", "device"),
    ("PySide2.QtPrintSupport", "printer", "device"),
)
# attribute calls recognised by name alone: name -> (kind, direction)
_METHODS: Final = {
    "read_text": ("text file", "read"),
    "read_bytes": ("binary file", "read"),
    "write_text": ("text file", "write"),
    "write_bytes": ("binary file", "write"),
    "toxml": ("XML", "write"),
    "toprettyxml": ("XML", "write"),
}
# kind present in the scope -> attribute calls that then count as I/O of that kind
_COMPANIONS: Final = {
    "docx": {"save": "write"},
    "jinja2": {"render": "write", "stream": "write", "dump": "write"},
    "INI": {"read": "read", "read_file": "read", "read_string": "read", "write": "write"},
}
_OPEN_MODE_ARG: Final = {
    "open": 1,
    "io.open": 1,
    "codecs.open": 1,
    "gzip.open": 1,
    "gzip.GzipFile": 1,
    "zipfile.ZipFile": 1,
}
_OPEN_KIND: Final = {"gzip.open": "gzip", "gzip.GzipFile": "gzip", "zipfile.ZipFile": "zip"}
_OPEN_DEFAULT_MODE: Final = {"gzip.open": "rb", "gzip.GzipFile": "rb"}
_CONTEXTS: Final = (
    ("sportorg/models/memory.py", "race file (JSON)"),
    ("sportorg/modules/iof/", "IOF XML"),
    ("sportorg/modules/ocad/", "OCAD"),
    ("sportorg/modules/winorient/", "WinOrient"),
    ("sportorg/modules/sfr/", "SFR"),
    ("sportorg/modules/sportident/", "SPORTident"),
    ("sportorg/modules/sportiduino/", "Sportiduino"),
    ("sportorg/modules/srpid/", "SRPID"),
    ("sportorg/modules/rfid_impinj/", "Impinj RFID"),
    ("sportorg/modules/huichang/", "Huichang"),
    ("sportorg/modules/live/", "live"),
    ("sportorg/modules/teamwork/", "teamwork"),
    ("sportorg/modules/backup/", "backup"),
    ("sportorg/modules/recovery/", "recovery"),
    ("sportorg/modules/printing/", "printing"),
    ("sportorg/modules/telegram/", "telegram"),
)


# ---------------------------------------------------------------- records


@dataclass(frozen=True, slots=True)
class Call:
    line: int
    api: str
    kind: str
    direction: str


@dataclass(frozen=True, slots=True)
class Value:
    kind: str
    text: str
    line: int  # where the value is written (the assignment line for a named constant)
    use_line: int  # where the function uses it
    origin: str


@dataclass(frozen=True, slots=True)
class FunctionRow:
    path: str
    module: str
    function: str
    line: int
    context: str
    calls: tuple[Call, ...]
    values: tuple[Value, ...]

    @property
    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({c.kind for c in self.calls}))

    @property
    def direction(self) -> str:
        return combine(c.direction for c in self.calls)

    def direction_of(self, kind: str) -> str:
        return combine(c.direction for c in self.calls if c.kind == kind)


@dataclass(frozen=True, slots=True)
class ConstDef:
    value: ConstValue
    text: str
    line: int


def combine(directions: Iterator[str] | Sequence[str]) -> str:
    """``read``/``write`` only; ``device`` only; ``unknown`` only; anything else ``both``."""
    found = set(directions)
    for single in ("read", "write", "device", "unknown", "decode", "encode"):
        if found == {single}:
            return single
    return "both"


def context_of(path: str) -> str:
    for prefix, label in _CONTEXTS:
        if path.startswith(prefix):
            return label
    if path.startswith("sportorg/libs/"):
        return f"lib:{path.split('/')[2]}"
    return "other"


def redact(text: str) -> str:
    """Personal data never enters the evidence: e-mail literals are replaced, bot tokens cut."""
    if EMAIL_RE.search(text):
        return "<redacted: e-mail>"
    return BOT_TOKEN_RE.sub("bot<redacted: token>", text)


# ---------------------------------------------------------------- module facts


class _Facts:
    """Aliases, constants and source segments of one module."""

    def __init__(self, tree: ast.Module, source: str, path: str) -> None:
        self.path: str = path
        self.lines: list[bytes] = [line.encode("utf-8") for line in physical_lines(source)]
        self.aliases: dict[str, str] = {}
        self.module_consts: dict[str, ConstDef] = {}
        self.class_consts: dict[str, dict[str, ConstDef]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = alias.name if alias.asname else alias.name.split(".")[0]
                    self.aliases[alias.asname or alias.name.split(".")[0]] = target
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for alias in node.names:
                    self.aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self._collect(tree.body, self.module_consts)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                found: dict[str, ConstDef] = {}
                self._collect(node.body, found)
                self.class_consts[node.name] = found

    def segment(self, node: ast.expr) -> str:
        if node.end_lineno is None or node.end_col_offset is None:
            return ""
        first, last = node.lineno - 1, node.end_lineno - 1
        if first == last:
            raw = self.lines[first][node.col_offset : node.end_col_offset]
        else:
            parts = [self.lines[first][node.col_offset :], *self.lines[first + 1 : last]]
            parts.append(self.lines[last][: node.end_col_offset])
            raw = b" ".join(parts)
        return " ".join(raw.decode("utf-8", errors="replace").split())

    def _collect(self, body: Sequence[ast.stmt], into: dict[str, ConstDef]) -> None:
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                targets, value = stmt.targets, stmt.value
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                targets, value = [stmt.target], stmt.value
            else:
                continue
            literal = _literal(value)
            if literal is None:
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in into:
                    into[target.id] = ConstDef(literal, self.segment(value), stmt.lineno)

    def dotted(self, node: ast.expr) -> str | None:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            return None
        parts.append(self.aliases.get(current.id, current.id))
        return ".".join(reversed(parts))


def _literal(node: ast.expr) -> ConstValue | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes, int, float)):
        return None if isinstance(node.value, bool) else node.value
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and isinstance(node.operand, ast.Constant)
        and isinstance(node.operand.value, (int, float))
        and not isinstance(node.operand.value, bool)
    ):
        return -node.operand.value
    return None


# ---------------------------------------------------------------- scopes


def _children(node: ast.AST) -> Iterator[ast.AST]:
    yield from ast.iter_child_nodes(node)


def _own_nodes(scope: Scope) -> Iterator[tuple[ast.AST, ast.AST]]:
    """``(node, parent)`` of a scope, not descending into nested functions and classes."""
    stack: list[tuple[ast.AST, ast.AST]] = [(child, scope) for child in reversed(scope.body)]
    while stack:
        node, parent = stack.pop()
        yield node, parent
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        stack.extend((child, node) for child in reversed(list(_children(node))))


def _scopes(tree: ast.Module) -> Iterator[tuple[str, str | None, Scope]]:
    """``(qualified name, enclosing class, node)`` of the module, classes and functions."""
    yield MODULE_SCOPE, None, tree

    def visit(
        body: Sequence[ast.stmt], prefix: str, owner: str | None
    ) -> Iterator[tuple[str, str | None, Scope]]:
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{stmt.name}"
                yield name, owner, stmt
                yield from visit(stmt.body, f"{name}.", owner)
            elif isinstance(stmt, ast.ClassDef):
                name = f"{prefix}{stmt.name}"
                yield f"{name}.<class>", stmt.name, stmt
                yield from visit(stmt.body, f"{name}.", stmt.name)
            else:
                for inner in _nested_bodies(stmt):
                    yield from visit(inner, prefix, owner)

    yield from visit(tree.body, "", None)


def _nested_bodies(stmt: ast.stmt) -> Iterator[Sequence[ast.stmt]]:
    if isinstance(
        stmt,
        ast.If
        | ast.For
        | ast.AsyncFor
        | ast.While
        | ast.With
        | ast.AsyncWith
        | ast.Try
        | ast.TryStar,
    ):
        yield stmt.body
        if not isinstance(stmt, ast.With | ast.AsyncWith):
            yield stmt.orelse
        if isinstance(stmt, ast.Try | ast.TryStar):
            yield stmt.finalbody
            for handler in stmt.handlers:
                yield handler.body
    elif isinstance(stmt, ast.Match):
        for case in stmt.cases:
            yield case.body


# ---------------------------------------------------------------- I/O sites


def _str_arg(call: ast.Call, index: int, keyword: str) -> str | None:
    node: ast.expr | None = None
    if len(call.args) > index:
        node = call.args[index]
    for kw in call.keywords:
        if kw.arg == keyword:
            node = kw.value
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _has_arg(call: ast.Call, index: int, keyword: str) -> bool:
    return len(call.args) > index or any(kw.arg == keyword for kw in call.keywords)


def _mode_direction(mode: str | None) -> str:
    if mode is None:
        return "unknown"
    if "+" in mode:
        return "both"
    return "write" if any(ch in mode for ch in "wax") else "read"


def _open_call(call: ast.Call, name: str) -> Call:
    index = _OPEN_MODE_ARG[name]
    mode = _str_arg(call, index, "mode")
    if mode is None and not _has_arg(call, index, "mode"):
        mode = _OPEN_DEFAULT_MODE.get(name, "r")
    kind = _OPEN_KIND.get(name) or ("binary file" if mode and "b" in mode else "text file")
    if name == "zipfile.ZipFile" and mode is not None:
        mode = mode[:1] + "+" * ("+" in mode)
    return Call(call.lineno, name, kind, _mode_direction(mode))


def _is_path_receiver(facts: _Facts, node: ast.expr) -> bool:
    if isinstance(node, ast.Call):
        root = facts.dotted(node.func)
        return root is not None and root.startswith("pathlib.")
    name = facts.dotted(node)
    return name is not None and ("path" in name.lower() or name.startswith("pathlib."))


def _is_element_tree(facts: _Facts, node: ast.expr) -> bool:
    """``ElementTree(...)`` of ``xml.etree`` or ``lxml.etree`` as the receiver of ``.write``."""
    if not isinstance(node, ast.Call):
        return False
    name = facts.dotted(node.func) or ""
    return name.endswith(".ElementTree") and name.startswith(("xml.", "lxml."))


def _named_site(call: ast.Call, name: str) -> Call | None:
    if name in _API:
        kind, direction = _API[name]
        return Call(call.lineno, name, kind, direction)
    for prefix, kind, direction in _PREFIX:
        if name == prefix or name.startswith(f"{prefix}."):
            return Call(call.lineno, name, kind, direction)
    return None


def _site(call: ast.Call, facts: _Facts) -> Call | None:
    func = call.func
    name = facts.dotted(func) or ""
    if name in _OPEN_MODE_ARG:
        return _open_call(call, name)
    found = _named_site(call, name)
    if found is None and any(kw.arg == "xml_declaration" for kw in call.keywords):
        found = Call(call.lineno, ".write", "XML", "write") if _call_name(call) == "write" else None
    if found is None and isinstance(func, ast.Attribute):
        found = _method_site(call, func, facts)
    return found


def _method_site(call: ast.Call, func: ast.Attribute, facts: _Facts) -> Call | None:
    attr = func.attr
    if attr in _METHODS:
        kind, direction = _METHODS[attr]
        return Call(call.lineno, f".{attr}", kind, direction)
    if attr == "open" and _is_path_receiver(facts, func.value):
        mode = _str_arg(call, 0, "mode")
        found = _open_call(call, "open") if mode is not None else None
        direction = found.direction if found else "read"
        return Call(call.lineno, ".open", found.kind if found else "text file", direction)
    if attr == "write" and _is_element_tree(facts, func.value):
        return Call(call.lineno, ".write", "XML", "write")
    if attr in SOCKET_METHODS and _is_host_port(call):
        return Call(call.lineno, f".{attr}", "socket", "both")
    return _device_method_site(call, func, facts.path)


def device_kind(path: str) -> str | None:
    for prefix, label in DEVICE_KINDS:
        if path.startswith(prefix):
            return label
    return None


def _receiver_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Attribute):
        return node.attr
    return node.id if isinstance(node, ast.Name) else None


def _device_method_site(call: ast.Call, func: ast.Attribute, path: str) -> Call | None:
    direction = DEVICE_METHODS.get(func.attr)
    receiver = _receiver_name(func.value)
    if direction is None or receiver is None:
        return None
    bare = receiver.lstrip("_").lower()
    if bare not in DEVICE_VOCABULARY:
        return None
    kind = "socket" if bare in SOCKET_VOCABULARY else device_kind(path) or "device stream"
    return Call(call.lineno, f"{receiver}.{func.attr}", kind, direction)


def _parameter_calls(
    nodes: Sequence[tuple[ast.AST, ast.AST]], scope: ast.FunctionDef | ast.AsyncFunctionDef
) -> list[Call]:
    """Read/write methods on a parameter named like a file object (FILE_VOCABULARY)."""
    args = scope.args
    params = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)} & FILE_VOCABULARY
    found: list[Call] = []
    for node, _parent in nodes:
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        receiver, method = node.func.value, node.func.attr
        if isinstance(receiver, ast.Name) and receiver.id in params and method in FILE_METHODS:
            api = f"{receiver.id}.{method}"
            found.append(Call(node.lineno, api, FILE_PARAMETER, FILE_METHODS[method]))
    return found


def _is_host_port(call: ast.Call) -> bool:
    first = call.args[0] if call.args else None
    return isinstance(first, ast.Tuple) and len(first.elts) == HOST_PORT_LEN


def _companions(calls: list[Call], scope_nodes: Sequence[ast.Call]) -> list[Call]:
    extra: list[Call] = []
    present = {c.kind for c in calls}
    for kind, methods in _COMPANIONS.items():
        if kind not in present:
            continue
        extra.extend(
            Call(call.lineno, f".{call.func.attr}", kind, methods[call.func.attr])
            for call in scope_nodes
            if isinstance(call.func, ast.Attribute) and call.func.attr in methods
        )
    return extra


# ---------------------------------------------------------------- hard-coded values


def kind_from_name(name: str, *, numeric: bool) -> str | None:
    tokens = name.upper().split("_")
    for token in tokens:
        if token in NAME_TOKEN_KINDS:
            return NAME_TOKEN_KINDS[token]
    if numeric and any(token in SIZE_TOKENS for token in tokens):
        return "offset-or-width"
    return None


def classify_str(text: str) -> str | None:
    if URL_RE.search(text):
        return "url"
    if PORT_RE.match(text):
        return "port"
    if text.lower() in ENCODINGS:
        return "encoding"
    if len(text) <= TEXT_LIMIT and EXT_RE.search(text):
        return "extension"
    return None


def _clip(text: str) -> str:
    text = redact(text)
    return text if len(text) <= TEXT_LIMIT else f"{text[:TEXT_LIMIT]}..."


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return func.id if isinstance(func, ast.Name) else ""


def _compare_kind(parent: ast.Compare) -> str:
    others = [parent.left, *parent.comparators]
    if any(isinstance(o, ast.Call) and _call_name(o) == "len" for o in others):
        return "offset-or-width"
    return "byte-constant"


def _int_kind(node: ast.expr, parent: ast.AST, text: str, api: str) -> str | None:
    kind: str | None = None
    if text.lower().startswith("0x"):
        kind = "byte-constant"
    elif isinstance(parent, ast.Compare):
        kind = _compare_kind(parent)
    elif isinstance(parent, ast.Subscript | ast.Slice):
        kind = "offset-or-width"
    elif isinstance(parent, ast.BinOp) and isinstance(parent.op, BIT_OPS):
        shift = isinstance(parent.op, ast.LShift | ast.RShift)
        kind = "offset-or-width" if shift else "byte-constant"
    elif isinstance(parent, ast.Call) and node is not parent.func:
        if api.startswith("struct."):
            kind = "byte-constant"
        elif _call_name(parent) in WIDTH_CALLS:
            kind = "offset-or-width"
    return kind


@dataclass(frozen=True, slots=True)
class _Ref:
    """A literal or a named constant, with where it is written and where it is used."""

    value: ConstValue
    text: str
    line: int
    use_line: int
    origin: str
    name: str = ""


class _ValueScan:
    """Collects the hard-coded values of one scope."""

    def __init__(
        self, facts: _Facts, owner: str | None, calls_api: Mapping[int, str], *, device: bool
    ) -> None:
        self.device: bool = device
        self.facts: _Facts = facts
        self.owner: str | None = owner
        self.calls_api: Mapping[int, str] = calls_api
        self.consumed: set[int] = set()
        self.found: set[Value] = set()

    def add(self, kind: str, text: str, line: int, use_line: int, origin: str) -> None:
        self.found.add(Value(kind, _clip(text), line, use_line, origin))

    def resolve(self, node: ast.expr) -> tuple[ConstDef | None, str]:
        """The constant a name or ``self.NAME`` refers to, and the name."""
        if isinstance(node, ast.Name):
            own = self.facts.class_consts.get(self.owner or "", {})
            return own.get(node.id) or self.facts.module_consts.get(node.id), node.id
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and self.owner is not None
        ):
            own = self.facts.class_consts.get(self.owner, {})
            if node.value.id in {"self", "cls", self.owner}:
                return own.get(node.attr), node.attr
        return None, ""

    def keyword_value(self, kind: str, value: ast.expr, label: str, use_line: int) -> None:
        literal = _literal(value)
        if kind == "struct-format" and not isinstance(literal, str):
            literal = None
        if literal is not None:
            self.consumed.add(id(value))
            self.add(kind, self.facts.segment(value), value.lineno, use_line, label)
            return
        const, name = self.resolve(value)
        if const is not None and (kind != "struct-format" or isinstance(const.value, str)):
            self.consumed.add(id(value))
            self.add(kind, const.text, const.line, use_line, f"constant {name} via {label}")

    def call(self, node: ast.Call, api: str) -> None:
        callee = api or self.facts.dotted(node.func) or _call_name(node)
        for kw in node.keywords:
            if kw.arg in KEYWORD_KINDS:
                label = f"keyword {kw.arg} of {callee}"
                self.keyword_value(KEYWORD_KINDS[kw.arg], kw.value, label, node.lineno)
        self._positional(node, api)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"encode", "decode"}:
            self._first("encoding", node, f"{node.func.attr} argument")
        if api.startswith(("requests.", "aiohttp")):
            self._first("url", node, f"first argument of {api}")

    def _first(self, kind: str, node: ast.Call, label: str) -> None:
        if node.args:
            self.keyword_value(kind, node.args[0], label, node.lineno)

    def _positional(self, node: ast.Call, api: str) -> None:
        if api in {"serial.Serial", "serial.serial_for_url"}:
            for index, kind in ((0, "port"), (1, "baudrate")):
                if len(node.args) > index:
                    label = f"positional {index + 1} of {api}"
                    self.keyword_value(kind, node.args[index], label, node.lineno)
        elif api.startswith("struct.") and node.args:
            self.keyword_value(
                "struct-format", node.args[0], f"first argument of {api}", node.lineno
            )
        elif api in _OPEN_MODE_ARG and len(node.args) > _OPEN_MODE_ARG[api]:
            mode = node.args[_OPEN_MODE_ARG[api]]
            self.keyword_value("other", mode, f"mode of {api}", node.lineno)
        elif api.startswith("."):
            self._network_tuple(node)

    def _network_tuple(self, node: ast.Call) -> None:
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Tuple) and len(first.elts) == HOST_PORT_LEN:
            label = f"address of .{_call_name(node)}"
            self.keyword_value("url", first.elts[0], label, node.lineno)
            self.keyword_value("port", first.elts[1], label, node.lineno)

    def constant(self, node: ast.expr, parent: ast.AST, api: str) -> None:
        literal = _literal(node)
        if literal is None or id(node) in self.consumed:
            return
        name = ""  # a non-empty string assigned to a local name is typed by that name
        if isinstance(parent, ast.Assign) and len(parent.targets) == 1 and isinstance(literal, str):
            target = parent.targets[0]
            name = target.id if isinstance(target, ast.Name) and literal else ""
        ref = _Ref(literal, self.facts.segment(node), node.lineno, node.lineno, "literal", name)
        self._typed(ref, node, parent, api)

    def named(self, node: ast.expr, parent: ast.AST, api: str) -> None:
        if id(node) in self.consumed:
            return
        const, name = self.resolve(node)
        if const is not None:
            ref = _Ref(const.value, const.text, const.line, node.lineno, f"constant {name}", name)
            self._typed(ref, node, parent, api)

    def _typed(self, ref: _Ref, node: ast.expr, parent: ast.AST, api: str) -> None:
        value, name = ref.value, ref.name
        kind: str | None = None
        if isinstance(value, bytes):
            kind = "byte-constant" if value else None
        elif isinstance(value, str):
            kind = (kind_from_name(name, numeric=False) if name else None) or classify_str(value)
        elif name and kind_from_name(name, numeric=True):
            kind = kind_from_name(name, numeric=True)
        elif isinstance(value, int):
            shift = isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.LShift | ast.RShift)
            if value not in SMALL_INTS or shift or ref.text.lower().startswith("0x"):
                kind = _int_kind(node, parent, ref.text, api)
            if kind is None and self.device and name.isupper():
                kind = "byte-constant"  # a named command code or protocol constant
            if kind is None and self.device and isinstance(parent, ast.BinOp):
                kind = "offset-or-width"  # weights and divisors of byte arithmetic
        if kind is not None:
            self.add(kind, ref.text, ref.line, ref.use_line, ref.origin)


def _find_calls(nodes: Sequence[tuple[ast.AST, ast.AST]], facts: _Facts) -> list[Call]:
    calls: list[Call] = []
    call_nodes: list[ast.Call] = []
    for node, _parent in nodes:
        if isinstance(node, ast.Call):
            call_nodes.append(node)
            site = _site(node, facts)
            if site is not None:
                calls.append(site)
    calls.extend(_companions(calls, call_nodes))
    return calls


def _is_reference(node: ast.AST, parent: ast.AST) -> bool:
    """A name or attribute that may stand for a constant (not a callee, not an inner attribute)."""
    if not isinstance(node, ast.Name | ast.Attribute) or not isinstance(node.ctx, ast.Load):
        return False
    is_callee = isinstance(parent, ast.Call) and node is parent.func
    is_inner = isinstance(parent, ast.Attribute) and node is parent.value
    return not (is_callee or is_inner)


def _collect_values(
    nodes: Sequence[tuple[ast.AST, ast.AST]], scan: _ValueScan, api_at: Mapping[int, str]
) -> None:
    for node, _parent in nodes:
        if isinstance(node, ast.Call):
            scan.call(node, api_at.get(node.lineno, ""))
    for node, parent in nodes:
        api = api_at.get(parent.lineno, "") if isinstance(parent, ast.Call) else ""
        if isinstance(node, ast.Constant | ast.UnaryOp):
            if not (isinstance(parent, ast.UnaryOp) and isinstance(node, ast.Constant)):
                scan.constant(node, parent, api)
        elif _is_reference(node, parent) and isinstance(node, ast.expr):
            scan.named(node, parent, api)


def _is_byte_arithmetic(node: ast.BinOp, facts: _Facts) -> bool:
    """Bit operation with a hex mask, or any byte operation on an indexed value with an int."""
    inner = list(ast.walk(node))
    ints = [n for n in inner if isinstance(n, ast.Constant) and isinstance(n.value, int)]
    indexed = any(isinstance(n, ast.Subscript) for n in inner)
    hex_mask = isinstance(node.op, BIT_OPS) and any(
        facts.segment(n).lower().startswith("0x") for n in ints
    )
    return hex_mask or (indexed and bool(ints))


def _protocol_features(
    nodes: Sequence[tuple[ast.AST, ast.AST]], facts: _Facts
) -> tuple[int, set[str]] | None:
    """First line and kinds of encoder/decoder evidence in a scope without I/O calls."""
    line = 0
    signals: set[str] = set()
    for node, parent in nodes:
        found: str | None = None
        if isinstance(node, ast.Constant) and isinstance(node.value, bytes) and node.value:
            found = "compare" if isinstance(parent, ast.Compare) else "literal"
        elif isinstance(node, ast.Call):
            name = facts.dotted(node.func) or ""
            if name == "int.from_bytes":
                found = "decode"
            elif _call_name(node) == "to_bytes":
                found = "encode"
        elif isinstance(node, ast.BinOp) and isinstance(node.op, BYTE_OPS):
            found = "decode" if _is_byte_arithmetic(node, facts) else None
        if found is not None and isinstance(node, ast.expr):
            signals.add(found)
            line = line or node.lineno
    return (line, signals) if signals else None


def _protocol_call(
    nodes: Sequence[tuple[ast.AST, ast.AST]], facts: _Facts, kind: str
) -> list[Call]:
    found = _protocol_features(nodes, facts)
    if found is None:
        return []
    line, signals = found
    decode, encode = "decode" in signals or "compare" in signals, "encode" in signals
    if decode and encode:
        direction = "both"
    elif encode or (signals == {"literal"} and not decode):
        direction = "encode"
    else:
        direction = "decode"
    return [Call(line, PROTOCOL_API, kind, direction)]


def _scan_scope(
    scope: Scope, owner: str | None, facts: _Facts, path: str
) -> tuple[list[Call], list[Value]]:
    nodes = list(_own_nodes(scope))
    calls = _find_calls(nodes, facts)
    if isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef):
        known = {(c.line, c.api) for c in calls}
        calls += [c for c in _parameter_calls(nodes, scope) if (c.line, c.api) not in known]
    kind = device_kind(path)
    if not calls and kind is not None and isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef):
        calls = _protocol_call(nodes, facts, kind)
    if not calls:
        return [], []
    api_at = {c.line: c.api for c in calls}
    scan = _ValueScan(facts, owner, api_at, device=kind is not None)
    _collect_values(nodes, scan, api_at)
    values = sorted(scan.found, key=lambda v: (v.use_line, v.line, v.kind, v.text, v.origin))
    return sorted(set(calls), key=lambda c: (c.line, c.api, c.kind, c.direction)), values


def scan_source(source: str, path: str) -> list[FunctionRow]:
    """One row per scope of ``source`` that holds an I/O site, in source order."""
    tree, _ = parse_source(source, path)
    facts = _Facts(tree, source, path)
    module = module_name(path)[0]
    rows: list[FunctionRow] = []
    for name, owner, scope in _scopes(tree):
        calls, values = _scan_scope(scope, owner, facts, path)
        if calls:
            line = 1 if isinstance(scope, ast.Module) else scope.lineno
            rows.append(
                FunctionRow(path, module, name, line, context_of(path), tuple(calls), tuple(values))
            )
    return rows


# ---------------------------------------------------------------- summary


def _directions_by(rows: Sequence[FunctionRow], key: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for row in rows:
        for call in row.calls:
            label = call.kind if key == "kind" else row.context
            found.setdefault(label, set()).add(call.direction)
    return found


def _strings(items: Sequence[str]) -> Json:
    out: list[Json] = list(items)
    return out


def _counts(data: Mapping[str, Mapping[str, int]]) -> Json:
    return {k: dict(sorted(v.items())) for k, v in sorted(data.items())}


def summarise(rows: Sequence[FunctionRow]) -> dict[str, Json]:
    by_kind: dict[str, Counter[str]] = {}
    by_context: dict[str, Counter[str]] = {}
    value_kinds: Counter[str] = Counter()
    for row in rows:
        for kind in row.kinds:
            by_kind.setdefault(kind, Counter())[row.direction_of(kind)] += 1
        by_context.setdefault(row.context, Counter())[row.direction] += 1
        value_kinds.update(v.kind for v in row.values)
    kinds = _directions_by(rows, "kind")
    contexts = _directions_by(rows, "context")
    return {
        "functions": len(rows),
        "io_calls": sum(len(r.calls) for r in rows),
        "values": sum(len(r.values) for r in rows),
        "by_kind_direction": _counts(by_kind),
        "by_context_direction": _counts(by_context),
        "by_value_kind": {k: value_kinds[k] for k in VALUE_KINDS if value_kinds[k]},
        "without_reader": _strings(_missing(kinds, {"read", "both"})),
        "without_writer": _strings(_missing(kinds, {"write", "both"})),
        "device_only_formats": _strings(sorted(k for k, d in kinds.items() if d == {"device"})),
        "contexts_without_reader": _strings(_missing(contexts, {"read", "both"})),
        "contexts_without_writer": _strings(_missing(contexts, {"write", "both"})),
        "device_only_contexts": _strings(sorted(k for k, d in contexts.items() if d == {"device"})),
    }


def _missing(found: Mapping[str, set[str]], wanted: set[str]) -> list[str]:
    return sorted(k for k, d in found.items() if d != {"device"} and not d & wanted)


# ---------------------------------------------------------------- run on legacy


def load_sources(name: str = PYSPORT) -> dict[str, str]:
    repo, commit = repo_root(name), legacy.find_pin(name).commit
    sources: dict[str, str] = {}
    for path in tracked_files(repo):
        if path.startswith("sportorg/") and path.endswith(".py"):
            sources[path] = git_raw(repo, "show", f"{commit}:{path}")
    return sources


def scan_all(sources: Mapping[str, str]) -> tuple[list[FunctionRow], list[str]]:
    rows: list[FunctionRow] = []
    unparsed: list[str] = []
    for path in sorted(sources):
        try:
            rows.extend(scan_source(sources[path], path))
        except UnparsedError as exc:
            unparsed.append(f"{exc.path}: {exc.reason}")
    return rows, unparsed


def _tag(path: str, line: int) -> str:
    return Loc(PYSPORT, path, line).tag()


def _row_json(row: FunctionRow) -> Json:
    return {
        "path": row.path,
        "module": row.module,
        "function": row.function,
        "context": row.context,
        "formats": list(row.kinds),
        "direction": row.direction,
        "tag": _tag(row.path, row.calls[0].line),
        "calls": [
            {
                "line": c.line,
                "api": c.api,
                "format": c.kind,
                "direction": c.direction,
                "tag": _tag(row.path, c.line),
            }
            for c in row.calls
        ],
        "values": [
            {
                "kind": v.kind,
                "text": v.text,
                "origin": v.origin,
                "tag": _tag(row.path, v.line),
                "use_tag": _tag(row.path, v.use_line),
            }
            for v in row.values
        ],
    }


DEFINITIONS: Final = {
    "io_site": "a call matching the API tables of formats.py (open family with the mode's"
    " direction; csv/json/orjson/xml/lxml/struct/zip/gzip/docx/jinja2/INI/PO; serial, socket,"
    " HTTP, SPORTident, HID, Impinj, printer; Path.read_*/write_*)",
    "row": "one per enclosing function, class body or module level with at least one I/O site;"
    " nested functions are rows of their own",
    "direction": "read, write, both (read and write, or both in one call), device (only device"
    " calls), unknown (open with a non-literal mode)",
    "values": "literals in the same scope: keyword/positional parameters, strings classified by"
    " content, bytes and hex constants, ints in comparisons, subscripts and packing, and module"
    " or class constants referenced by name (tag at the assignment line, use_tag at the use)",
    "device_methods": "[допущение] a call of one of DEVICE_METHODS (read, readline, write, flush,"
    " send, recv, reset_input_buffer, send_output_report, set_raw_data_handler, ...) on a name or"
    " attribute chain whose last part, case-insensitive and without leading underscores, is in"
    " DEVICE_VOCABULARY = {serial, ser, port, sock, socket, conn, device, dev, reader, station,"
    " hid}; direction comes from the method; format is the device format of the module path"
    " (e.g. Sportiduino serial, SFR HID), `socket` for sock/socket/conn, else `device stream`",
    "protocol_rows": "in the device paths of DEVICE_KINDS (libs/{sportiduino,sfr,srpid,huichang},"
    " modules/{sportident,sfr,sportiduino,srpid,rfid_impinj,huichang}) a function without I/O"
    " calls gets a row (call `<protocol>`, direction decode/encode/both) when it has a non-empty"
    " bytes literal, `int.from_bytes`, `.to_bytes`, or byte arithmetic: `& | ^ << >>` with a hex"
    " mask or on an indexed value with an int, and, beyond the original list, `+ - * // %` on an"
    " indexed value with an int. encode = `.to_bytes` or a bytes literal that is not compared;"
    " decode = the rest. Named upper-case int constants referenced there are byte-constants",
    "host": "a host or URL value is reported with kind url; newline and quotechar as delimiter",
    "file_parameter": "[допущение] a read/readline/readlines/write/writelines call on a"
    " parameter of the enclosing function named file, f, fp, fh, fd, fobj or stream"
    " (FILE_VOCABULARY) is an I/O site of kind `file object (parameter)` unless a device rule"
    " already matched it; its direction comes from the method",
    "local_names": "a non-empty string literal assigned to a local name is typed by that name"
    ' like a constant (e.g. `sep = "\\t"` is a delimiter)',
}


def table(rows: Sequence[FunctionRow], summary: Mapping[str, Json]) -> str:
    out = ["## Functions", "", "| format | direction | module | function | calls | values |"]
    out.append("|---|---|---|---|---|---|")
    for row in rows:
        calls = " ".join(f"`{c.api}` {_tag(row.path, c.line)}" for c in row.calls)
        values = ", ".join(f"{v.kind}={v.text}" for v in row.values) or "-"
        values = values.replace("|", "\\|")
        out.append(
            f"| {', '.join(row.kinds)} | {row.direction} | {row.module} | {row.function} |"
            f" {calls} | {values} |"
        )
    out += [
        "",
        "## Values",
        "",
        "| kind | value | origin | function | tag |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        for v in row.values:
            text = f"`{v.text}`".replace("|", "\\|")
            out.append(
                f"| {v.kind} | {text} | {v.origin} | {row.module}.{row.function} |"
                f" {_tag(row.path, v.line)} |"
            )
    out += ["", "## Summary", "", f"```\n{_dump(summary)}\n```"]
    return "\n".join(out)


def _dump(data: Mapping[str, Json]) -> str:
    import json  # noqa: PLC0415 - used only here

    return json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True)


def readme(summary: Mapping[str, Json], unparsed: Sequence[str]) -> str:
    return (
        "# Formats: readers and writers of files and devices (TASK-7 criterion 4)\n\n"
        f"What: every I/O site in tracked `sportorg/**/*.py` of `pysport@{pin_short(PYSPORT)}`,"
        " one row per function, with direction, format and the hard-coded values of the function.\n"
        "- `formats.json`: rows (calls and values, each with a `[код]` tag) and the summary.\n"
        "- `formats.md`: the function table, the value table and the summary.\n\n"
        "Definitions (`scripts/archaeology/formats.py`):\n"
        + "".join(f"- {k}: {v}.\n" for k, v in DEFINITIONS.items())
        + "\nKey numbers (from the script):\n"
        f"- functions with I/O: {summary['functions']}; I/O calls: {summary['io_calls']};"
        f" hard-coded values: {summary['values']}.\n"
        f"- per format and direction: `{_dump_line(summary['by_kind_direction'])}`.\n"
        f"- per value kind: `{_dump_line(summary['by_value_kind'])}`.\n"
        f"- formats without a reader: {summary['without_reader']}; without a writer:"
        f" {summary['without_writer']}; device-only: {summary['device_only_formats']}.\n"
        f"- contexts (modules) without a reader: {summary['contexts_without_reader']};"
        f" without a writer: {summary['contexts_without_writer']}.\n"
        f"- files that `ast` could not parse: {len(unparsed)}.\n\n"
        "Limits:\n"
        "- Static names only: methods of objects are found by receiver name (DEVICE_VOCABULARY),"
        " `tree.write` through the companion rules; other receivers are missed.\n"
        "- `.open` counts only on receivers named like a path; `json.loads`/`dumps` are counted"
        " although they work on strings.\n"
        "- Protocol rows are heuristics: a decoder that only slices (`data[5:9]`) and no I/O or"
        " arithmetic gets no row. Receivers outside DEVICE_VOCABULARY are missed.\n"
        "- A value is attributed to the function that contains it, not to the call it feeds.\n"
        "- File objects received as parameters count only under the names of FILE_VOCABULARY;"
        " the format of such a row is the caller's (e.g. `.srb` for"
        " `sfr_results_board.dump`), which the row does not name. Directory listing"
        " (`os.listdir`), file-choosing dialogs and `webbrowser` are not I/O sites.\n"
        "- An int compared with `==`/`<` is reported as `byte-constant` unless the other side is"
        " `len(...)`; plain index comparisons are therefore included.\n"
        "- Lists of formats without a reader or writer are not judgements: they only show that"
        " no site of that kind was found.\n"
    )


def _dump_line(data: Json) -> str:
    import json  # noqa: PLC0415 - used only here

    return json.dumps(data, ensure_ascii=False, sort_keys=True)


class Options(argparse.Namespace):
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    rows, unparsed = scan_all(load_sources())
    summary = summarise(rows)
    header = (
        f"# Formats: I/O of files and devices in pysport@{pin_short(PYSPORT)}\n\n"
        "Produced by `scripts/archaeology/formats.py` (command in `commands.txt`)."
    )
    data: Json = {
        "definitions": dict(DEFINITIONS),
        "rows": [_row_json(r) for r in rows],
        "summary": summary,
        "unparsed": list(unparsed),
    }
    write_outputs(args.out, "formats", data, table(rows, summary), header)
    (args.out / "README.md").write_text(readme(summary, unparsed), encoding="utf-8", newline="\n")
    print(
        f"functions: {summary['functions']}, calls: {summary['io_calls']},"
        f" values: {summary['values']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
