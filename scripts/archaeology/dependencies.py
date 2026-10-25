"""Dependencies, licences and vulnerabilities of legacy (Stage 1, TASK-7 criterion 2, direction W3).

Run from the repo root (offline: reads the legacy lock files through git and the network cache):
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.dependencies \
        --out docs/evidence/stage-1/dependencies [--cache-dir DIR]

Inputs: ``uv.lock``, ``pyproject.toml`` and ``Cargo.lock`` of ``pysport`` at the pin; cached PyPI,
crates.io and OSV responses (``scripts.archaeology.fetch``); the cross-check outputs of
``uv audit`` and ``osv-scanner`` in ``<cache>/tools/``. Licence names and the GPL-3.0-or-later
allowlist are those of ``scripts/check_licenses.py`` (imported, not copied). Nothing here decides
anything: differences between sources are listed, not classified.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import textwrap
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal

from scripts import legacy
from scripts._json import as_dict, as_list, as_str, parse_json, parse_toml
from scripts.archaeology import fetch
from scripts.archaeology.common import (
    PYSPORT,
    Loc,
    assert_tree_clean,
    git_raw,
    physical_lines,
    pin_short,
    repo_root,
    write_outputs,
)
from scripts.check_licenses import (
    ALIASES,
    expression_verdict,
    metadata_verdict,
    normalize_name,
    split_packages,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from scripts._json import Json

type Verdict = Literal["ok", "problem", "unknown"]
type Status = Literal["both", "only_own", "only_other"]
type PkgKey = tuple[str, str, str]  # (ecosystem, normalised name, version)

LOCKS: Final = ("uv.lock", "pyproject.toml", "Cargo.lock")
KLASSES: Final = ("runtime", "extra", "dev")
STATUSES: Final = ("both", "only_own", "only_other")
TOP = 10
SPDX_MAX = 80
DATE_PARTS = 3  # date, name, version
WRAP = 96
UV_AUDIT_FILE: Final = "uv-audit-legacy.json"
OSV_SCANNER_FILE: Final = "osv-scanner-legacy.json"
PY38_RE: Final = re.compile(r"python_(?:full_)?version\s*(?:<\s*'3\.9'|==\s*'3\.8(?:\.\*)?')")
_REQ_RE: Final = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*([^;]*?)\s*(?:;\s*(.*?))?\s*$"
)
_TABLE_RE: Final = re.compile(r"^\[([^\[\]]+)\]\s*$")
_KEY_RE: Final = re.compile(r"^([A-Za-z0-9_-]+)\s*=\s*\[")


# ---------------------------------------------------------------- uv.lock


@dataclass(frozen=True, slots=True)
class Edge:
    name: str
    version: str | None
    marker: str | None


@dataclass(frozen=True, slots=True)
class LockPackage:
    name: str
    version: str
    source: str
    markers: tuple[str, ...]
    line: int  # of the ``name = "…"`` entry
    runtime: tuple[Edge, ...]
    extras: Mapping[str, tuple[Edge, ...]]
    groups: Mapping[str, tuple[Edge, ...]]


@dataclass(frozen=True, slots=True)
class Lock:
    packages: tuple[LockPackage, ...]
    root: LockPackage


@dataclass(frozen=True, slots=True)
class Reach:
    groups: tuple[str, ...]  # "runtime", "extra:<name>", "dev:<group>"
    py38_only: bool  # reachable only through edges whose marker confines them to Python 3.8

    @property
    def klass(self) -> str:
        if "runtime" in self.groups:
            return "runtime"
        if any(g.startswith("extra:") for g in self.groups):
            return "extra"
        return "dev"  # like check_licenses: everything not reachable from the project is dev


def is_py38_marker(marker: str | None) -> bool:
    """True when the marker confines a requirement to Python 3.8 (an ``or`` makes it false)."""
    return marker is not None and " or " not in marker and PY38_RE.search(marker) is not None


def _edges(value: object) -> tuple[Edge, ...]:
    edges: list[Edge] = []
    for item in as_list(value):
        table = as_dict(item)
        version = as_str(table.get("version")) or None
        marker = as_str(table.get("marker")) or None
        edges.append(Edge(normalize_name(as_str(table.get("name"))), version, marker))
    return tuple(edges)


def _edge_tables(value: object) -> dict[str, tuple[Edge, ...]]:
    return {key: _edges(edges) for key, edges in as_dict(value).items()}


def _source(value: object) -> str:
    table = as_dict(value)
    for kind in ("registry", "editable", "virtual", "git", "path", "url", "directory"):
        if kind in table:
            return f"{kind}:{as_str(table[kind])}" if kind != "registry" else as_str(table[kind])
    return "unknown"


def package_lines(text: str) -> list[int]:
    """Line of the ``name = "…"`` entry of each ``[[package]]`` table, in file order."""
    lines: list[int] = []
    waiting = False
    for number, line in enumerate(physical_lines(text), start=1):
        if line.strip() == "[[package]]":
            waiting = True
        elif waiting and line.startswith("name ="):
            lines.append(number)
            waiting = False
    return lines


def parse_uv_lock(text: str) -> Lock:
    """Packages of a ``uv.lock`` with edges per group; the root is the editable/virtual project."""
    tables = [as_dict(item) for item in as_list(as_dict(parse_toml(text)).get("package"))]
    lines = package_lines(text)
    packages = tuple(
        LockPackage(
            name=normalize_name(as_str(table.get("name"))),
            version=as_str(table.get("version")),
            source=_source(table.get("source")),
            markers=tuple(as_str(m) for m in as_list(table.get("resolution-markers"))),
            line=lines[index],
            runtime=_edges(table.get("dependencies")),
            extras=_edge_tables(table.get("optional-dependencies")),
            groups=_edge_tables(table.get("dev-dependencies")),
        )
        for index, table in enumerate(tables)
    )
    roots = [p for p in packages if p.source.startswith(("editable:", "virtual:"))]
    if not roots:
        msg = "uv.lock has no editable or virtual root package"
        raise ValueError(msg)
    return Lock(tuple(p for p in packages if p is not roots[0]), roots[0])


def _resolve(lock: Lock, edge: Edge) -> list[tuple[str, str]]:
    return [
        (p.name, p.version)
        for p in lock.packages
        if p.name == edge.name and (edge.version is None or p.version == edge.version)
    ]


def _walk(lock: Lock, start: Sequence[Edge], *, skip_py38: bool) -> set[tuple[str, str]]:
    by_key = {(p.name, p.version): p for p in lock.packages}
    seen: set[tuple[str, str]] = set()
    queue: deque[Edge] = deque(start)
    while queue:
        edge = queue.popleft()
        if skip_py38 and is_py38_marker(edge.marker):
            continue
        for key in _resolve(lock, edge):
            if key not in seen:
                seen.add(key)
                queue.extend(by_key[key].runtime)
    return seen


def classify(lock: Lock) -> dict[tuple[str, str], Reach]:
    """Groups and Python-3.8-only flag of every locked package, keyed by (name, version)."""
    roots: dict[str, tuple[Edge, ...]] = {"runtime": lock.root.runtime}
    roots |= {f"extra:{k}": v for k, v in lock.root.extras.items()}
    roots |= {f"dev:{k}": v for k, v in lock.root.groups.items()}
    in_group: dict[tuple[str, str], set[str]] = {(p.name, p.version): set() for p in lock.packages}
    general: set[tuple[str, str]] = set()
    for group, edges in roots.items():
        for key in _walk(lock, edges, skip_py38=False):
            in_group[key].add(group)
        general |= _walk(lock, edges, skip_py38=True)
    return {
        key: Reach(tuple(sorted(groups)), key not in general and bool(groups))
        for key, groups in in_group.items()
    }


def split_by_name(text: str, project: str) -> tuple[list[str], list[str]]:
    """Runtime and dev names exactly as ``scripts.check_licenses`` computes them."""
    return split_packages(text, project)


def runtime_names(reach: Mapping[tuple[str, str], Reach]) -> list[str]:
    return sorted({name for (name, _), r in reach.items() if r.klass == "runtime"})


# ---------------------------------------------------------------- pyproject.toml


@dataclass(frozen=True, slots=True)
class Requirement:
    name: str  # normalised
    spec: str
    marker: str | None


@dataclass(frozen=True, slots=True)
class DirectDep:
    section: str  # "dependencies", "extra:<name>", "dev:<group>"
    raw: str
    name: str
    spec: str
    marker: str | None
    py38_only: bool
    line: int


def parse_requirement(text: str) -> Requirement:
    match = _REQ_RE.match(text)
    if match is None:
        msg = f"cannot parse requirement {text!r}"
        raise ValueError(msg)
    name, spec, marker = match.groups()
    return Requirement(normalize_name(name), spec, marker or None)


def _pyproject_blocks(text: str) -> dict[str, list[tuple[int, str]]]:
    """Lines of each array of requirements, keyed by section label."""
    blocks: dict[str, list[tuple[int, str]]] = {}
    table = ""
    current: str | None = None
    for number, line in enumerate(physical_lines(text), start=1):
        header = _TABLE_RE.match(line.strip())
        key = _KEY_RE.match(line.strip())
        if header is not None:
            table, current = header.group(1), None
        if key is not None:
            label = _section_label(table, key.group(1))
            current = label
            blocks.setdefault(label, [])
        if current is not None:
            blocks[current].append((number, line))
    return blocks


def _section_label(table: str, key: str) -> str:
    if table == "project" and key == "dependencies":
        return "dependencies"
    if table == "project.optional-dependencies":
        return f"extra:{key}"
    if table == "dependency-groups":
        return f"dev:{key}"
    return f"other:{table}:{key}"


def direct_dependencies(pyproject_text: str) -> list[DirectDep]:
    """Requirement strings of ``[project]`` and ``[dependency-groups]`` with their lines."""
    data = as_dict(parse_toml(pyproject_text))
    project = as_dict(data.get("project"))
    sections: dict[str, list[Json]] = {"dependencies": as_list(project.get("dependencies"))}
    for key, items in as_dict(project.get("optional-dependencies")).items():
        sections[f"extra:{key}"] = as_list(items)
    for key, items in as_dict(data.get("dependency-groups")).items():
        sections[f"dev:{key}"] = as_list(items)
    blocks = _pyproject_blocks(pyproject_text)
    rows: list[DirectDep] = []
    for section, items in sections.items():
        block = blocks.get(section, [])
        for item in items:
            raw = as_str(item)
            if not raw:
                continue  # e.g. ``{include-group = …}``: not a requirement string
            line = next((n for n, text in block if f'"{raw}"' in text), block[0][0] if block else 0)
            req = parse_requirement(raw)
            rows.append(
                DirectDep(
                    section, raw, req.name, req.spec, req.marker, is_py38_marker(req.marker), line
                )
            )
    return rows


# ---------------------------------------------------------------- Cargo.lock


@dataclass(frozen=True, slots=True)
class CargoPackage:
    name: str
    version: str
    source: str | None
    dependencies: tuple[str, ...]
    line: int

    @property
    def is_registry(self) -> bool:
        return self.source is not None and self.source.startswith("registry+")


def parse_cargo_lock(text: str) -> list[CargoPackage]:
    tables = [as_dict(item) for item in as_list(as_dict(parse_toml(text)).get("package"))]
    lines = package_lines(text)
    return [
        CargoPackage(
            name=as_str(table.get("name")),
            version=as_str(table.get("version")),
            source=as_str(table.get("source")) or None,
            dependencies=tuple(as_str(dep) for dep in as_list(table.get("dependencies"))),
            line=lines[index],
        )
        for index, table in enumerate(tables)
    ]


# ---------------------------------------------------------------- licences


@dataclass(frozen=True, slots=True)
class Licence:
    source: str  # expression | classifier | free text | not declared
    spdx: str
    verdict: Verdict


def _spdx(text: str) -> str:
    stripped = text.strip()
    return ALIASES.get(stripped.lower(), stripped)


def _verdict(raw: str) -> Verdict:
    return "problem" if raw == "denied" else ("ok" if raw == "ok" else "unknown")


def licence_of(expression: str | None, classifiers: Sequence[str], field_: str | None) -> Licence:
    """Licence by the priority of ``check_licenses``: expression, classifiers, free text."""
    raw, _ = metadata_verdict(expression, list(classifiers), field_)
    verdict = _verdict(raw)
    if expression and expression.strip():
        return Licence("expression", expression.strip(), verdict)
    names = list(dict.fromkeys(_spdx(c) for c in classifiers if c.startswith("License ::")))
    if names:
        return Licence("classifier", " OR ".join(names), verdict)
    if field_ and field_.strip() and field_.strip().upper() != "UNKNOWN":
        first = field_.strip().splitlines()[0].strip()
        return Licence("free text", _spdx(first)[:SPDX_MAX], verdict)
    return Licence("not declared", "", "unknown")


def crate_licence(text: str | None) -> Licence:
    """crates.io writes alternatives as ``A/B``; read as ``A OR B``."""
    if not text or not text.strip():
        return Licence("not declared", "", "unknown")
    spdx = text.strip().replace("/", " OR ")
    return Licence("crates.io", spdx, _verdict(expression_verdict(spdx)))


# ---------------------------------------------------------------- OSV and cross-checks


@dataclass(frozen=True, slots=True)
class Finding:
    id: str
    aliases: tuple[str, ...]
    withdrawn: bool = False

    @property
    def ids(self) -> frozenset[str]:
        return frozenset((self.id, *self.aliases))


@dataclass(frozen=True, slots=True)
class OsvVuln:
    id: str
    aliases: tuple[str, ...]
    summary: str
    severity: tuple[tuple[str, str], ...]
    label: str
    fixed: tuple[str, ...]
    withdrawn: bool

    @property
    def finding(self) -> Finding:
        return Finding(self.id, self.aliases, self.withdrawn)


def _fixed_versions(record: Mapping[str, Json], name: str) -> tuple[str, ...]:
    fixed: list[str] = []
    for affected in as_list(record.get("affected")):
        entry = as_dict(affected)
        package = as_dict(entry.get("package"))
        if normalize_name(as_str(package.get("name"))) != normalize_name(name):
            continue
        for range_ in as_list(entry.get("ranges")):
            for event in as_list(as_dict(range_).get("events")):
                version = as_str(as_dict(event).get("fixed"))
                if version and version not in fixed:
                    fixed.append(version)
    return tuple(fixed)


def parse_osv(response: Json, name: str) -> list[OsvVuln]:
    """Records of one ``/v1/query`` response, sorted by id; fixed versions for package ``name``."""
    vulns: list[OsvVuln] = []
    for item in as_list(as_dict(response).get("vulns")):
        record = as_dict(item)
        severity = tuple(
            (as_str(as_dict(s).get("type")), as_str(as_dict(s).get("score")))
            for s in as_list(record.get("severity"))
        )
        vulns.append(
            OsvVuln(
                id=as_str(record.get("id")),
                aliases=tuple(as_str(a) for a in as_list(record.get("aliases"))),
                summary=as_str(record.get("summary")),
                severity=severity,
                label=as_str(as_dict(record.get("database_specific")).get("severity")),
                fixed=_fixed_versions(record, name),
                withdrawn=bool(as_str(record.get("withdrawn"))),
            )
        )
    return sorted(vulns, key=lambda v: v.id)


@dataclass(frozen=True, slots=True)
class CrossRow:
    status: Status
    ecosystem: str
    name: str
    version: str
    id: str
    matched: tuple[str, ...]  # ids of the other side's records that matched
    reason: str


def _overlap(one: Finding, two: Finding) -> bool:
    return bool(one.ids & two.ids)


def _elsewhere(
    finding: Finding, side: Mapping[PkgKey, Sequence[Finding]], key: PkgKey
) -> str | None:
    """Another version of the same package where ``side`` has a matching record."""
    versions = sorted(
        k[2]
        for k, found in side.items()
        if k[:2] == key[:2] and k != key and any(_overlap(finding, f) for f in found)
    )
    return versions[0] if versions else None


def _reason_own(finding: Finding, other: Mapping[PkgKey, Sequence[Finding]], key: PkgKey) -> str:
    if finding.withdrawn:
        return "withdrawn in own record"
    version = _elsewhere(finding, other, key)
    if version is not None:
        return f"the other side reports it for version {version} of the same package"
    if not other.get(key):
        return "the other side has no record for this version"
    return "the other side has records for this version, none sharing an id or alias"


def _reason_other(finding: Finding, own: Mapping[PkgKey, Sequence[Finding]], key: PkgKey) -> str:
    version = _elsewhere(finding, own, key)
    if version is not None:
        return f"own lists it for version {version} of the same package"
    if not own.get(key):
        return "own response for this version has no records"
    return "own response for this version has records, none sharing an id or alias"


def crosscheck(
    own: Mapping[PkgKey, Sequence[Finding]], other: Mapping[PkgKey, Sequence[Finding]]
) -> list[CrossRow]:
    """Per (package, version, record) overlap of own findings with another tool's, by id or alias.

    ``both`` rows come from the own side (one per own record with at least one match).
    """
    rows: list[CrossRow] = []
    for key in sorted(set(own) | set(other)):
        mine, theirs = own.get(key, []), other.get(key, [])
        for finding in mine:
            matched = tuple(sorted(t.id for t in theirs if _overlap(finding, t)))
            if matched:
                rows.append(CrossRow("both", *key, finding.id, matched, ""))
            else:
                rows.append(
                    CrossRow("only_own", *key, finding.id, (), _reason_own(finding, other, key))
                )
        rows.extend(
            CrossRow("only_other", *key, t.id, (), _reason_other(t, own, key))
            for t in theirs
            if not any(_overlap(m, t) for m in mine)
        )
    return sorted(rows, key=lambda r: (r.ecosystem, r.name, r.version, r.id, r.status))


def count_status(rows: Iterable[CrossRow]) -> dict[str, int]:
    counts = Counter(r.status for r in rows)
    return {status: counts[status] for status in STATUSES}


def _finding(record: Mapping[str, Json]) -> Finding:
    return Finding(
        as_str(record.get("id")), tuple(as_str(a) for a in as_list(record.get("aliases")))
    )


def uv_audit_findings(data: Json) -> dict[PkgKey, list[Finding]]:
    found: dict[PkgKey, list[Finding]] = {}
    for item in as_list(as_dict(data).get("vulnerabilities")):
        record = as_dict(item)
        dep = as_dict(record.get("dependency"))
        key = ("PyPI", normalize_name(as_str(dep.get("name"))), as_str(dep.get("version")))
        found.setdefault(key, []).append(_finding(record))
    return found


def osv_scanner_findings(data: Json) -> dict[str, dict[PkgKey, list[Finding]]]:
    """Findings of an osv-scanner JSON by lock file name (temporary directories stripped)."""
    found: dict[str, dict[PkgKey, list[Finding]]] = {}
    for result in as_list(as_dict(data).get("results")):
        table = as_dict(result)
        file_name = Path(as_str(as_dict(table.get("source")).get("path"))).name
        per_file = found.setdefault(file_name, {})
        for package in as_list(table.get("packages")):
            entry = as_dict(package)
            info = as_dict(entry.get("package"))
            ecosystem = as_str(info.get("ecosystem"))
            name = as_str(info.get("name"))
            key = (ecosystem, normalize_name(name) if ecosystem == "PyPI" else name)
            full = (*key, as_str(info.get("version")))
            per_file.setdefault(full, []).extend(
                _finding(as_dict(v)) for v in as_list(entry.get("vulnerabilities"))
            )
    return found


# ---------------------------------------------------------------- the cache


class Cache:
    """Read-only view of the fetch cache that records the SHA-256 of every file it used."""

    def __init__(self, directory: Path) -> None:
        self.directory: Path = directory
        self.digests: dict[str, str] = {}
        self.missing: list[str] = []

    def load(self, kind: str, key: str) -> Json | None:
        label = f"{kind}/{key}"
        if not fetch.cache_path(self.directory, kind, key).exists():
            if label not in self.missing:
                self.missing.append(label)
            return None
        self.digests[label] = fetch.cached_sha256(kind, key, self.directory)
        return fetch.load_cached(kind, key, self.directory)

    def of_kind(self, kind: str) -> dict[str, str]:
        return {k: v for k, v in sorted(self.digests.items()) if k.startswith(f"{kind}/")}

    def combined(self, kind: str) -> str:
        shas = sorted(self.of_kind(kind).values())
        return hashlib.sha256("\n".join(shas).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class ToolFile:
    name: str
    sha256: str
    data: Json


@dataclass(frozen=True, slots=True)
class ToolOutputs:
    uv_audit: ToolFile
    osv_scanner: ToolFile


@dataclass(frozen=True, slots=True)
class Inputs:
    uv_lock: str
    pyproject: str
    cargo_lock: str
    tools: ToolOutputs


# ---------------------------------------------------------------- rows


@dataclass(frozen=True, slots=True)
class PackageRow:
    package: LockPackage
    reach: Reach
    licence: Licence
    requires_python: str
    released: str
    vulns: tuple[OsvVuln, ...]


@dataclass(frozen=True, slots=True)
class CrateRow:
    package: CargoPackage
    licence: Licence
    released: str
    vulns: tuple[OsvVuln, ...]
    looked_up: bool = field(default=True)


def _release_date(response: Json) -> str:
    dates = [
        as_str(as_dict(u).get("upload_time_iso_8601") or as_dict(u).get("upload_time"))[:10]
        for u in as_list(as_dict(response).get("urls"))
    ]
    return min((d for d in dates if d), default="")


def python_rows(
    lock: Lock, reach: Mapping[tuple[str, str], Reach], cache: Cache
) -> list[PackageRow]:
    rows: list[PackageRow] = []
    for package in sorted(lock.packages, key=lambda p: (p.name, p.version)):
        if not package.source.startswith("http"):
            continue  # not a registry package: nothing in PyPI/OSV to look up
        response = cache.load("pypi", f"{package.name}=={package.version}")
        info = as_dict(as_dict(response).get("info"))
        licence = (
            licence_of(
                as_str(info.get("license_expression")) or None,
                [as_str(c) for c in as_list(info.get("classifiers"))],
                as_str(info.get("license")) or None,
            )
            if response is not None
            else Licence("not declared", "", "unknown")
        )
        osv = cache.load("osv", f"PyPI:{package.name}=={package.version}")
        rows.append(
            PackageRow(
                package,
                reach[package.name, package.version],
                licence,
                as_str(info.get("requires_python")),
                _release_date(response) if response is not None else "",
                tuple(parse_osv(osv, package.name)) if osv is not None else (),
            )
        )
    return rows


def crate_rows(packages: Sequence[CargoPackage], cache: Cache) -> list[CrateRow]:
    rows: list[CrateRow] = []
    for package in sorted(packages, key=lambda p: (p.name, p.version)):
        if not package.is_registry:
            local = Licence("local crate", "", "unknown")
            rows.append(CrateRow(package, local, "", (), looked_up=False))
            continue
        meta = as_dict(
            as_dict(cache.load("crates", f"{package.name}=={package.version}")).get("version")
        )
        osv = cache.load("osv", f"crates.io:{package.name}=={package.version}")
        rows.append(
            CrateRow(
                package,
                crate_licence(as_str(meta.get("license")) or None),
                as_str(meta.get("created_at"))[:10],
                tuple(parse_osv(osv, package.name)) if osv is not None else (),
            )
        )
    return rows


def _findings(rows: Sequence[PackageRow]) -> dict[PkgKey, list[Finding]]:
    return {
        ("PyPI", r.package.name, r.package.version): [v.finding for v in r.vulns]
        for r in rows
        if r.vulns
    }


def _crate_findings(rows: Sequence[CrateRow]) -> dict[PkgKey, list[Finding]]:
    return {
        ("crates.io", r.package.name, r.package.version): [v.finding for v in r.vulns]
        for r in rows
        if r.vulns
    }


# ---------------------------------------------------------------- output


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _tag(path: str, line: int) -> str:
    return Loc(PYSPORT, path, line).tag()


def _strs(values: Iterable[str]) -> list[Json]:
    return list(values)


def _ints(values: Mapping[str, int]) -> dict[str, Json]:
    return dict(values)


def _strmap(values: Mapping[str, str]) -> dict[str, Json]:
    return dict(values)


def _yes(flag: bool) -> str:  # noqa: FBT001 - a one-argument formatting helper
    return "yes" if flag else "no"


@dataclass(frozen=True, slots=True)
class Analysis:
    inputs: Inputs
    lock: Lock
    rows: Sequence[PackageRow]
    crates: Sequence[CrateRow]
    cache: Cache
    cross: Mapping[str, Sequence[CrossRow]]
    runtime_only_here: Sequence[str]
    runtime_only_check_licenses: Sequence[str]


def _header(title: str, analysis: Analysis) -> str:
    pin = f"{PYSPORT}@{pin_short(PYSPORT)}"
    cache = analysis.cache
    lines = [
        f"# {title}: {pin}",
        "",
        "Produced by `scripts/archaeology/dependencies.py` (command in `commands.txt`). Sources:",
        f"- `uv.lock`, `pyproject.toml`, `Cargo.lock` of {pin}, read through git.",
    ]
    for kind, label in (("pypi", "PyPI JSON"), ("osv", "OSV query"), ("crates", "crates.io JSON")):
        lines.append(
            f"- {label} cache `{kind}/`: {len(cache.of_kind(kind))} files,"
            f" combined SHA-256 `{cache.combined(kind)}` (per-file values in `summary.json`)."
        )
    tools = (analysis.inputs.tools.uv_audit, analysis.inputs.tools.osv_scanner)
    lines.extend(f"- `tools/{t.name}`: SHA-256 `{t.sha256}`." for t in tools)
    return "\n".join(lines)


def _vuln_counts(rows: Sequence[PackageRow]) -> list[tuple[PackageRow, int]]:
    return [(r, len(r.vulns)) for r in rows if r.vulns]


def build_summary(analysis: Analysis) -> dict[str, Json]:
    rows, crates, cache = analysis.rows, analysis.crates, analysis.cache
    by_klass = Counter(r.reach.klass for r in rows)
    names = {k: len({r.package.name for r in rows if r.reach.klass == k}) for k in KLASSES}
    verdicts: dict[str, Json] = {}
    for klass in KLASSES:
        counts = Counter(r.licence.verdict for r in rows if r.reach.klass == klass)
        verdicts[klass] = {v: counts[v] for v in ("ok", "problem", "unknown")}
    vulnerable = _vuln_counts(rows)
    runtime_vuln = [(r, n) for r, n in vulnerable if r.reach.klass == "runtime"]
    top = sorted(vulnerable, key=lambda t: (-t[1], t[0].package.name, t[0].package.version))[:TOP]
    labels = Counter(v.label or "(none)" for r in rows for v in r.vulns)
    runtime_dates = sorted(
        (r.released, r.package.name, r.package.version)
        for r in rows
        if r.reach.klass == "runtime" and r.released
    )
    multi = sorted({name for name, n in Counter(r.package.name for r in rows).items() if n > 1})
    crate_vulns = [(r, len(r.vulns)) for r in crates if r.vulns]
    tools = (analysis.inputs.tools.uv_audit, analysis.inputs.tools.osv_scanner)
    return {
        "pins": {PYSPORT: legacy.find_pin(PYSPORT).commit},
        "inputs": {
            "cache_files": {
                kind: {
                    "count": len(cache.of_kind(kind)),
                    "combined_sha256": cache.combined(kind),
                    "files": _strmap(cache.of_kind(kind)),
                }
                for kind in ("pypi", "osv", "crates")
            },
            "missing_cache_files": _strs(sorted(cache.missing)),
            "tools": {t.name: {"sha256": t.sha256} for t in tools},
        },
        "python": {
            "locked_registry_packages": len(rows),
            "packages": _ints({k: by_klass[k] for k in KLASSES}),
            "distinct_names": _ints(names),
            "names_with_several_versions": _strs(multi),
            "py38_only_package_versions": sum(1 for r in rows if r.reach.py38_only),
            "runtime_names_only_in_this_script": _strs(analysis.runtime_only_here),
            "runtime_names_only_in_check_licenses": _strs(analysis.runtime_only_check_licenses),
            "licence_verdicts": verdicts,
            "licence_sources": _ints(Counter(r.licence.source for r in rows)),
            "licence_attention": [
                {
                    "name": r.package.name,
                    "version": r.package.version,
                    "class": r.reach.klass,
                    "verdict": r.licence.verdict,
                    "spdx": r.licence.spdx,
                }
                for r in rows
                if r.licence.verdict != "ok"
            ],
            "vulnerabilities": {
                "records": sum(n for _, n in vulnerable),
                "package_versions": len(vulnerable),
                "runtime_package_versions": len(runtime_vuln),
                "runtime_names": len({r.package.name for r, _ in runtime_vuln}),
                "runtime_package_versions_not_py38_only": sum(
                    1 for r, _ in runtime_vuln if not r.reach.py38_only
                ),
                "by_class": _ints(
                    {k: sum(n for r, n in vulnerable if r.reach.klass == k) for k in KLASSES}
                ),
                "by_label": _ints(labels),
                "top": [
                    {
                        "package": r.package.name,
                        "version": r.package.version,
                        "class": r.reach.klass,
                        "records": n,
                    }
                    for r, n in top
                ],
            },
            "release_dates_runtime": {
                "oldest": _strs(runtime_dates[0]) if runtime_dates else [],
                "newest": _strs(runtime_dates[-1]) if runtime_dates else [],
                "with_date": len(runtime_dates),
            },
        },
        "rust": {
            "packages": len(crates),
            "registry": sum(1 for r in crates if r.package.is_registry),
            "local": sum(1 for r in crates if not r.package.is_registry),
            "licence_verdicts": {
                v: sum(1 for r in crates if r.licence.verdict == v and r.looked_up)
                for v in ("ok", "problem", "unknown")
            },
            "vulnerable_package_versions": len(crate_vulns),
            "vulnerabilities": sum(n for _, n in crate_vulns),
        },
        "crosscheck": {
            name: _ints(count_status(rs)) for name, rs in sorted(analysis.cross.items())
        },
        "lock_root": analysis.lock.root.name,
    }


def _licence_json(licence: Licence) -> Json:
    return {"source": licence.source, "spdx": licence.spdx, "verdict": licence.verdict}


def _md_packages(rows: Sequence[PackageRow]) -> str:
    cols = ["package", "version", "class", "groups", "py3.8-only", "licence", "source"]
    cols += ["verdict", "vulns", "released", "lock"]
    head = [f"| {' | '.join(cols)} |", f"|{'---|' * len(cols)}"]
    body = [
        f"| {r.package.name} | {r.package.version} | {r.reach.klass}"
        f" | {cell(', '.join(r.reach.groups))} | {_yes(r.reach.py38_only)}"
        f" | {cell(r.licence.spdx or '-')} | {r.licence.source} | {r.licence.verdict}"
        f" | {len(r.vulns)} | {r.released or '-'} | {_tag('uv.lock', r.package.line)} |"
        for r in rows
    ]
    return "\n".join([*head, *body])


def _json_packages(rows: Sequence[PackageRow]) -> Json:
    return [
        {
            "name": r.package.name,
            "version": r.package.version,
            "source": r.package.source,
            "resolution_markers": _strs(r.package.markers),
            "class": r.reach.klass,
            "groups": _strs(r.reach.groups),
            "py38_only": r.reach.py38_only,
            "licence": _licence_json(r.licence),
            "requires_python": r.requires_python,
            "released": r.released,
            "vulnerability_ids": _strs(v.id for v in r.vulns),
            "lock": _tag("uv.lock", r.package.line),
        }
        for r in rows
    ]


def _md_vulns(rows: Sequence[PackageRow]) -> str:
    head = [
        "| package | version | class | py3.8-only | id | aliases | label | CVSS | fixed |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    body = [
        f"| {r.package.name} | {r.package.version} | {r.reach.klass}"
        f" | {_yes(r.reach.py38_only)} | {v.id} | {cell(', '.join(v.aliases) or '-')}"
        f" | {v.label or '-'} | {cell('; '.join(f'{t}: {s}' for t, s in v.severity) or '-')}"
        f" | {cell(', '.join(v.fixed) or '-')} |"
        for r in rows
        for v in r.vulns
    ]
    return "\n".join([*head, *body])


def _vuln_json(v: OsvVuln) -> dict[str, Json]:
    return {
        "id": v.id,
        "aliases": _strs(v.aliases),
        "summary": v.summary,
        "label": v.label,
        "severity": [{"type": t, "score": s} for t, s in v.severity],
        "fixed": _strs(v.fixed),
        "withdrawn": v.withdrawn,
    }


def _json_vulns(rows: Sequence[PackageRow]) -> Json:
    return [
        {
            "package": r.package.name,
            "version": r.package.version,
            "class": r.reach.klass,
            "py38_only": r.reach.py38_only,
            "lock": _tag("uv.lock", r.package.line),
            **_vuln_json(v),
        }
        for r in rows
        for v in r.vulns
    ]


def _md_direct(rows: Sequence[DirectDep], locked: Mapping[tuple[str, str], list[str]]) -> str:
    head = [
        "| section | requirement | marker | py3.8-only | locked versions | pyproject |",
        "|---|---|---|---|---|---|",
    ]
    body = [
        f"| {r.section} | `{cell(r.raw)}` | {cell(r.marker or '-')} | {_yes(r.py38_only)}"
        f" | {', '.join(locked.get((r.section, r.name), [])) or '-'}"
        f" | {_tag('pyproject.toml', r.line)} |"
        for r in rows
    ]
    return "\n".join([*head, *body])


def _json_direct(rows: Sequence[DirectDep], locked: Mapping[tuple[str, str], list[str]]) -> Json:
    return [
        {
            "section": r.section,
            "requirement": r.raw,
            "name": r.name,
            "marker": r.marker or "",
            "py38_only": r.py38_only,
            "locked_versions": _strs(locked.get((r.section, r.name), [])),
            "pyproject": _tag("pyproject.toml", r.line),
        }
        for r in rows
    ]


def _md_rust(rows: Sequence[CrateRow]) -> str:
    head = [
        "| crate | version | source | licence | verdict | released | vulns | Cargo.lock |",
        "|---|---|---|---|---|---|---|---|",
    ]
    body = [
        f"| {r.package.name} | {r.package.version}"
        f" | {'registry' if r.package.is_registry else 'local'}"
        f" | {cell(r.licence.spdx or r.licence.source)} | {r.licence.verdict}"
        f" | {r.released or '-'} | {len(r.vulns) if r.looked_up else '-'}"
        f" | {_tag('Cargo.lock', r.package.line)} |"
        for r in rows
    ]
    return "\n".join([*head, *body])


def _json_rust(rows: Sequence[CrateRow]) -> Json:
    return [
        {
            "name": r.package.name,
            "version": r.package.version,
            "source": r.package.source or "local",
            "dependencies": _strs(r.package.dependencies),
            "licence": _licence_json(r.licence),
            "released": r.released,
            "vulnerabilities": [_vuln_json(v) for v in r.vulns],
            "lock": _tag("Cargo.lock", r.package.line),
        }
        for r in rows
    ]


def _cross_json(rows: Sequence[CrossRow]) -> Json:
    return [
        {
            "status": r.status,
            "ecosystem": r.ecosystem,
            "package": r.name,
            "version": r.version,
            "id": r.id,
            "matched": _strs(r.matched),
            "reason": r.reason,
        }
        for r in rows
    ]


def _md_cross(cross: Mapping[str, Sequence[CrossRow]]) -> str:
    out = ["| comparison | both | only own | only other |", "|---|---|---|---|"]
    for name, rows in sorted(cross.items()):
        c = count_status(rows)
        out.append(f"| {name} | {c['both']} | {c['only_own']} | {c['only_other']} |")
    for name, rows in sorted(cross.items()):
        differing = [r for r in rows if r.status != "both"]
        out += ["", f"## {name}: records present on one side only ({len(differing)})", ""]
        if not differing:
            out.append("None.")
            continue
        out += ["| status | package | version | id | reason |", "|---|---|---|---|---|"]
        out += [
            f"| {r.status} | {r.name} | {r.version} | {r.id} | {cell(r.reason)} |"
            for r in differing
        ]
    return "\n".join(out)


def _reason_counts(rows: Sequence[CrossRow]) -> dict[str, int]:
    counts = Counter(f"{r.status}: {r.reason}" for r in rows if r.status != "both")
    return dict(sorted(counts.items()))


def _triple(counts: Json) -> str:
    table = as_dict(counts)
    return "/".join(str(table[v]) for v in ("ok", "problem", "unknown"))


def _date(value: Json) -> str:
    parts = [str(x) for x in as_list(value)]
    return f"{parts[0]} ({parts[1]} {parts[2]})" if len(parts) == DATE_PARTS else "n/a"


def _summary_md(summary: Mapping[str, Json]) -> str:
    py = as_dict(summary["python"])
    vulns = as_dict(py["vulnerabilities"])
    packages = as_dict(py["packages"])
    verdicts = as_dict(py["licence_verdicts"])
    out = ["| item | value |", "|---|---|"]
    out += [f"| package versions, {k} | {packages[k]} |" for k in KLASSES]
    out += [f"| licence ok/problem/unknown, {k} | {_triple(verdicts[k])} |" for k in KLASSES]
    out += [
        f"| OSV records (Python) | {vulns['records']} |",
        f"| vulnerable runtime package versions | {vulns['runtime_package_versions']} |",
        f"| vulnerable runtime names | {vulns['runtime_names']} |",
        "",
        "## Top packages by OSV records",
        "",
        "| package | version | class | records |",
        "|---|---|---|---|",
    ]
    out += [
        f"| {as_str(as_dict(t)['package'])} | {as_str(as_dict(t)['version'])}"
        f" | {as_str(as_dict(t)['class'])} | {as_dict(t)['records']} |"
        for t in as_list(vulns["top"])
    ]
    return "\n".join(out)


def _bullet(text: str) -> str:
    return textwrap.fill(text, width=WRAP, initial_indent="- ", subsequent_indent="  ")


def _attention(py: Mapping[str, Json]) -> str:
    rows = [as_dict(r) for r in as_list(py["licence_attention"])]
    return "; ".join(
        f"{as_str(r['name'])} {as_str(r['version'])} ({as_str(r['class'])}, {as_str(r['verdict'])}:"
        f" {as_str(r['spdx']) or 'not declared'})"
        for r in rows
    )


def readme(summary: Mapping[str, Json], cross: Mapping[str, Sequence[CrossRow]]) -> str:
    py = as_dict(summary["python"])
    vulns = as_dict(py["vulnerabilities"])
    packages = as_dict(py["packages"])
    verdicts = as_dict(py["licence_verdicts"])
    rust = as_dict(summary["rust"])
    crate_verdicts = as_dict(rust["licence_verdicts"])
    dates = as_dict(py["release_dates_runtime"])
    top = ", ".join(
        f"{as_str(as_dict(t)['package'])} {as_str(as_dict(t)['version'])} ({as_dict(t)['records']})"
        for t in as_list(vulns["top"])
    )
    cross_lines = [
        f"| {name} | {c['both']} | {c['only_own']} | {c['only_other']} |"
        for name, rows in sorted(cross.items())
        for c in (count_status(rows),)
    ]
    reason_lines = [
        _bullet(f"{name}: {reason} = {count}")
        for name, rows in sorted(cross.items())
        for reason, count in _reason_counts(rows).items()
    ]
    here = [str(n) for n in as_list(py["runtime_names_only_in_this_script"])]
    theirs = [str(n) for n in as_list(py["runtime_names_only_in_check_licenses"])]
    pin = f"{PYSPORT}@{pin_short(PYSPORT)}"
    head = [
        "# Dependencies, licences and vulnerabilities (TASK-7 criterion 2)",
        "",
        textwrap.fill(
            f"What: Python and Rust dependencies of `{pin}`, their licences and known"
            " vulnerabilities, from the lock files at the pin and the network cache. Generated by"
            " `scripts/archaeology/dependencies.py`; every number below comes from it.",
            width=WRAP,
        ),
        "",
        "Files (`.json` is the machine output, `.md` the table):",
        _bullet("`summary`: counts, input digests (per-file SHA-256 of the cache), top lists."),
        _bullet(
            "`direct-dependencies`: requirement strings of `pyproject.toml` with marker, line and"
            " the versions `uv.lock` resolves them to."
        ),
        _bullet(
            "`python-packages`: every registry package of `uv.lock` (one row per version) with"
            " class, groups, Python 3.8 flag, licence, verdict, vulnerability count."
        ),
        _bullet("`vulnerabilities-python`: own OSV records per package version."),
        _bullet("`rust-packages`: `Cargo.lock` packages, crates.io licence, OSV records."),
        _bullet("`crosscheck`: own OSV against `uv audit` and against osv-scanner, per record."),
        "",
        "Definitions:",
        _bullet(
            "Class `runtime`: reachable from `[project].dependencies` in `uv.lock`, environment"
            " markers ignored (the superset), as in `scripts/check_licenses.py`. Class `extra`:"
            " reachable only from `[project.optional-dependencies]` (`gui`, `win`). Class `dev`:"
            " every other package (dependency groups, anything unreachable). `groups` lists the"
            " groups that reach a package. The walk is per (name, version)."
        ),
        _bullet(
            "Python 3.8 only: no path from any group to the package avoids an edge whose marker"
            " confines it to Python 3.8 (`python_full_version < '3.9'`, `== '3.8.*'`); a marker"
            " with `or` is not counted as confined."
        ),
        _bullet(
            "Licence: PyPI `license_expression`, else `License ::` classifiers, else the free-text"
            " `license` field (first line), else not declared; names and allowlist of"
            " `scripts/check_licenses.py` (target GPL-3.0-or-later). Verdict `ok` = allowlisted;"
            " `problem` = denied there; `unknown` = neither. Crates: the crates.io `license`"
            " string, `/` read as `OR`."
        ),
        _bullet(
            "Vulnerability: an OSV record returned by `POST /v1/query` for the exact package"
            " version. Fixed versions are the `fixed` events of the `affected[]` entries of that"
            " package. Labels are the record's `database_specific.severity`; CVSS strings are"
            " copied, not scored."
        ),
        _bullet(
            "Cross-check: records match when their ids and aliases share a value. `both` is counted"
            " once per own record; `only other` counts the other tool's records with no own match."
        ),
        "",
        "Key numbers:",
    ]
    numbers = [
        _bullet(
            f"Registry packages in `uv.lock`: {py['locked_registry_packages']} package versions:"
            f" runtime {packages['runtime']}, extra {packages['extra']}, dev {packages['dev']};"
            f" {len(as_list(py['names_with_several_versions']))} names have several versions."
        ),
        _bullet(f"Python 3.8-only package versions: {py['py38_only_package_versions']}."),
        _bullet(
            f"Licence verdicts (ok/problem/unknown): runtime {_triple(verdicts['runtime'])},"
            f" extra {_triple(verdicts['extra'])}, dev {_triple(verdicts['dev'])}; crates"
            f" {_triple(crate_verdicts)} (local crates are counted in none)."
        ),
        _bullet(f"Not ok: {_attention(py)}."),
        _bullet(
            f"Own OSV: {vulns['records']} records on {vulns['package_versions']} package versions;"
            f" runtime package versions affected: {vulns['runtime_package_versions']}"
            f" ({vulns['runtime_names']} names; {vulns['runtime_package_versions_not_py38_only']}"
            f" of the versions are not Python-3.8-only). Top 10 by records: {top}."
        ),
        _bullet(
            f"Runtime release dates (PyPI upload): oldest {_date(dates['oldest'])},"
            f" newest {_date(dates['newest'])}."
        ),
        _bullet(
            f"Rust: {rust['packages']} packages ({rust['registry']} registry, {rust['local']}"
            f" local); crate versions with OSV records: {rust['vulnerable_package_versions']}"
            f" ({rust['vulnerabilities']} records)."
        ),
        _bullet(
            "Runtime names that `check_licenses.split_packages` and this walk place differently:"
            f" {len(here)} only here, {len(theirs)} only there"
            f" ({', '.join([*here, *theirs]) or 'none'}). `check_licenses.lock_graph` keeps one"
            " dependency list per name (the last version's); this walk keeps every version."
        ),
        "",
        "| cross-check | both | only own | only other |",
        "|---|---|---|---|",
        *cross_lines,
        "",
        "Differences by reason:",
        *(reason_lines or ["- none"]),
        "",
        "Limits:",
    ]
    limits = [
        _bullet(
            "OSV is queried per exact version; whether legacy uses the vulnerable code path is not"
            " assessed. The data are the responses cached on the fetch date, not today's."
        ),
        _bullet(
            "`Cargo.lock` has no runtime/dev split; crates are not classed. Local crates have no"
            " registry licence or OSV lookup."
        ),
        _bullet(
            "Packages without a cache file are listed in `summary.json` (`missing_cache_files`)."
        ),
        _bullet(
            "`uv audit` and osv-scanner results are cached runs on temporary copies of the lock"
            " files; paths are reduced to the file name."
        ),
        _bullet(
            "Author and maintainer fields of PyPI/crates metadata are not read (personal data)."
        ),
        "",
        "Checks: see `commands.txt`.",
    ]
    return "\n".join([*head, *numbers, *limits])


COMMANDS: Final = """\
# Run from the repository root; offline (lock files through git, network data from the cache).
PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.dependencies \\
    --out docs/evidence/stage-1/dependencies
PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.verify_locs \\
    --evidence docs/evidence/stage-1/dependencies --sample 10 --seed 1
uv run python -m scripts.legacy verify
"""


def _locked_versions(lock: Lock) -> dict[tuple[str, str], list[str]]:
    groups = {"dependencies": lock.root.runtime}
    groups |= {f"extra:{k}": v for k, v in lock.root.extras.items()}
    groups |= {f"dev:{k}": v for k, v in lock.root.groups.items()}
    locked: dict[tuple[str, str], list[str]] = {}
    for section, edges in groups.items():
        for edge in edges:
            for _, version in _resolve(lock, edge):
                bucket = locked.setdefault((section, edge.name), [])
                if version not in bucket:
                    bucket.append(version)
    return locked


def analyse(inputs: Inputs, cache_dir: Path) -> Analysis:
    cache = Cache(cache_dir)
    lock = parse_uv_lock(inputs.uv_lock)
    reach = classify(lock)
    theirs, _ = split_by_name(inputs.uv_lock, lock.root.name)
    ours = runtime_names(reach)
    rows = python_rows(lock, reach, cache)
    crates = crate_rows(parse_cargo_lock(inputs.cargo_lock), cache)
    scanner = osv_scanner_findings(inputs.tools.osv_scanner.data)
    cross = {
        "own vs uv audit (Python)": crosscheck(
            _findings(rows), uv_audit_findings(inputs.tools.uv_audit.data)
        ),
        "own vs osv-scanner (uv.lock)": crosscheck(_findings(rows), scanner.get("uv.lock", {})),
        "own vs osv-scanner (Cargo.lock)": crosscheck(
            _crate_findings(crates), scanner.get("Cargo.lock", {})
        ),
    }
    return Analysis(
        inputs,
        lock,
        rows,
        crates,
        cache,
        cross,
        sorted(set(ours) - set(theirs)),
        sorted(set(theirs) - set(ours)),
    )


def run(inputs: Inputs, cache_dir: Path, out: Path) -> dict[str, Json]:
    """Build every output from ``inputs`` and the cache; returns the summary."""
    analysis = analyse(inputs, cache_dir)
    summary = build_summary(analysis)
    direct = direct_dependencies(inputs.pyproject)
    locked = _locked_versions(analysis.lock)
    rows, crates, cross = analysis.rows, analysis.crates, analysis.cross
    outputs: list[tuple[str, str, Json, str]] = [
        ("summary", "Summary", summary, _summary_md(summary)),
        (
            "direct-dependencies",
            "Direct dependencies",
            _json_direct(direct, locked),
            _md_direct(direct, locked),
        ),
        ("python-packages", "Python packages", _json_packages(rows), _md_packages(rows)),
        (
            "vulnerabilities-python",
            "Python vulnerabilities",
            _json_vulns(rows),
            _md_vulns(rows),
        ),
        ("rust-packages", "Rust packages", _json_rust(crates), _md_rust(crates)),
        (
            "crosscheck",
            "Cross-check of vulnerability sources",
            {name: _cross_json(rs) for name, rs in sorted(cross.items())},
            _md_cross(cross),
        ),
    ]
    for stem, title, data, table in outputs:
        write_outputs(out, stem, data, table, _header(title, analysis))
    (out / "README.md").write_text(readme(summary, cross) + "\n", encoding="utf-8", newline="\n")
    (out / "commands.txt").write_text(COMMANDS, encoding="utf-8", newline="\n")
    return summary


def load_inputs(cache_dir: Path) -> Inputs:
    repo, commit = repo_root(PYSPORT), legacy.find_pin(PYSPORT).commit
    texts = [git_raw(repo, "show", f"{commit}:{name}") for name in LOCKS]
    tools: list[ToolFile] = []
    for name in (UV_AUDIT_FILE, OSV_SCANNER_FILE):
        body = (cache_dir / "tools" / name).read_bytes()
        tools.append(ToolFile(name, hashlib.sha256(body).hexdigest(), parse_json(body)))
    return Inputs(texts[0], texts[1], texts[2], ToolOutputs(tools[0], tools[1]))


class Options(argparse.Namespace):
    out: Path = Path()
    cache_dir: Path = fetch.DEFAULT_CACHE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=fetch.DEFAULT_CACHE)
    args = parser.parse_args(argv, namespace=Options())
    summary = run(load_inputs(args.cache_dir), args.cache_dir, args.out)
    assert_tree_clean(repo_root(PYSPORT))
    py = as_dict(summary["python"])
    print(
        f"packages: {py['packages']}; vulnerabilities: {as_dict(py['vulnerabilities'])['records']}"
    )
    print(f"crosscheck: {summary['crosscheck']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
