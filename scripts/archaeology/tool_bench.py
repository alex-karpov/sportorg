"""Measurements behind ADR-0007 (Stage 1 analysis tools).

Run from the repo root:
    uv run python -m scripts.archaeology.tool_bench candidates --out docs/evidence/stage-1/tools

``candidates`` summarises the cached PyPI JSON of each candidate (fetched by
``scripts.archaeology.fetch pypi …``): latest version, release date, licence, development status
and wheel availability for CPython 3.14 and 3.15 on Linux x86_64, Windows amd64 and macOS.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import as_dict, as_list, as_str
from scripts.archaeology import fetch
from scripts.archaeology.common import PYSPORT, ImportRef, pin_short, write_outputs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from scripts._json import Json

PLATFORMS: Final = ("linux", "macos", "windows")
PYTHONS: Final = ("3.14", "3.15")
_WHEEL_RE: Final = re.compile(r"^(?P<py>[^-]+)-(?P<abi>[^-]+)-(?P<plat>[^-]+)\.whl$")
_SOURCE_KEYS: Final = ("Source", "Source Code", "Repository", "Code", "GitHub", "Homepage")
_LICENSE_TEXT_MAX: Final = 60
_LIZARD_FIELDS: Final = 11
CANDIDATES: Final = (
    "ruff",
    "grimp",
    "import-linter",
    "radon",
    "lizard",
    "complexipy",
    "vulture",
    "skylos",
    "deadcode",
    "pydeps",
    "pip-audit",
    "pydriller",
    "semgrep",
    "ast-grep-cli",
)


def _platform(tag: str) -> str | None:
    if tag == "any":
        return "*"
    if tag == "win_amd64":
        return "windows"
    if tag.startswith("macosx_"):
        return "macos"
    if tag.endswith("_x86_64") and (tag.startswith(("manylinux", "linux_"))):
        return "linux"
    return None


def _python_ok(py_tags: str, abi_tags: str, python: str) -> bool:
    minor = int(python.split(".")[1])
    abis = set(abi_tags.split("."))
    for tag in py_tags.split("."):
        if tag in {"py3", f"py3{minor}"}:
            return True
        cp = re.fullmatch(r"cp3(\d+)", tag)
        if cp is None:
            continue
        tag_minor = int(cp.group(1))
        if tag_minor == minor and (f"cp3{minor}" in abis or "none" in abis):
            return True
        if "abi3" in abis and tag_minor <= minor:
            return True
    return False


def wheel_platforms(filename: str, python: str) -> set[str]:
    """Target platforms on which CPython ``python`` (GIL build) can install this wheel."""
    match = _WHEEL_RE.search("-".join(filename.split("-")[-3:]))
    if match is None or not _python_ok(match["py"], match["abi"], python):
        return set()
    found = {_platform(tag) for tag in match["plat"].split(".")}
    return set(PLATFORMS) if "*" in found else {p for p in found if p is not None}


def _license(info: dict[str, Json]) -> str:
    expression = as_str(info.get("license_expression"))
    if expression:
        return expression
    text = as_str(info.get("license")).strip()
    if text and len(text) <= _LICENSE_TEXT_MAX and "\n" not in text:
        return text
    for classifier in as_list(info.get("classifiers")):
        value = as_str(classifier)
        if value.startswith("License :: "):
            return f"{value.rsplit(' :: ', 1)[-1]} (classifier)"
    return "not declared"


def _status(info: dict[str, Json]) -> str:
    for classifier in as_list(info.get("classifiers")):
        value = as_str(classifier)
        if value.startswith("Development Status :: "):
            return value.removeprefix("Development Status :: ")
    return "not declared"


def _source(info: dict[str, Json]) -> str:
    urls = as_dict(info.get("project_urls"))
    for key in _SOURCE_KEYS:
        if as_str(urls.get(key)):
            return as_str(urls.get(key))
    return as_str(info.get("home_page"))


def _wheels(files: list[str], python: str) -> str:
    wheels = [f for f in files if f.endswith(".whl")]
    if not wheels:
        return "none (sdist only)"
    platforms: set[str] = set()
    for wheel in wheels:
        platforms |= wheel_platforms(wheel, python)
    return ", ".join(sorted(platforms)) or "none"


def pypi_summary(data: Json) -> dict[str, str]:
    """Facts about the latest release from a PyPI ``/pypi/<name>/json`` document."""
    info = as_dict(as_dict(data).get("info"))
    urls = [as_dict(u) for u in as_list(as_dict(data).get("urls"))]
    files = [as_str(u.get("filename")) for u in urls]
    uploads = sorted(as_str(u.get("upload_time_iso_8601")) for u in urls)
    summary = {
        "name": as_str(info.get("name")),
        "version": as_str(info.get("version")),
        "released": uploads[0][:10] if uploads else "unknown",
        "license": _license(info),
        "requires_python": as_str(info.get("requires_python")) or "not declared",
        "status": _status(info),
        "source": _source(info),
    }
    for python in PYTHONS:
        summary[f"wheels_{python}"] = _wheels(files, python)
    return summary


# ---------------------------------------------------------------- tool output parsers

type FuncKey = tuple[str, int]  # (path relative to the legacy root, line of ``def``)
type Complexity = dict[FuncKey, tuple[str, int]]

_C901_RE: Final = re.compile(r"^`(?P<name>.+)` is too complex \((?P<n>\d+) > \d+\)$")
_VULTURE_RE: Final = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+): (?P<msg>.+) \((?P<conf>\d+)% confidence\)$"
)
_VULTURE_MSG_RE: Final = re.compile(r"^(?P<kind>.+?)(?: after)? '(?P<name>.+)'$")


def _relative(path: str, root: str) -> str:
    return path.removeprefix(root.rstrip("/") + "/")


def parse_ruff_c901(data: Json, root: str) -> Complexity:
    """``ruff check --select C901 --output-format json`` with ``max-complexity = 0``."""
    found: Complexity = {}
    for item in as_list(data):
        entry = as_dict(item)
        match = _C901_RE.match(as_str(entry.get("message")))
        if as_str(entry.get("code")) != "C901" or match is None:
            continue
        row = as_dict(entry.get("location")).get("row")
        if isinstance(row, int):
            path = _relative(as_str(entry.get("filename")), root)
            found[path, row] = (match["name"], int(match["n"]))
    return found


def _radon_blocks(blocks: list[Json], path: str, found: Complexity) -> None:
    for item in blocks:
        block = as_dict(item)
        line, complexity = block.get("lineno"), block.get("complexity")
        if as_str(block.get("type")) == "class":
            continue
        if isinstance(line, int) and isinstance(complexity, int):
            found[path, line] = (as_str(block.get("name")), complexity)
        _radon_blocks(as_list(block.get("closures")), path, found)


def parse_radon(data: Json, root: str) -> Complexity:
    """``radon cc -j``: functions, methods (listed at top level too) and closures; no classes."""
    found: Complexity = {}
    for path, blocks in as_dict(data).items():
        _radon_blocks(as_list(blocks), _relative(path, root), found)
    return found


def parse_lizard_csv(text: str, root: str) -> Complexity:
    """``lizard --csv`` columns: NLOC, CCN, …, file (6), function (7), …, start (9), end."""
    found: Complexity = {}
    for row in csv.reader(text.splitlines()):
        if len(row) >= _LIZARD_FIELDS and row[1].isdigit():
            found[_relative(row[6], root), int(row[9])] = (row[7], int(row[1]))
    return found


def parse_vulture(text: str, root: str) -> list[dict[str, Json]]:
    findings: list[dict[str, Json]] = []
    for line in text.splitlines():
        match = _VULTURE_RE.match(line)
        if match is None:
            continue
        msg = _VULTURE_MSG_RE.match(match["msg"])
        findings.append(
            {
                "path": _relative(match["path"], root),
                "line": int(match["line"]),
                "kind": msg["kind"] if msg else match["msg"],
                "name": msg["name"] if msg else "",
                "confidence": int(match["conf"]),
            }
        )
    return findings


def _nearest(module: str, modules: set[str]) -> str | None:
    parts = module.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in modules:
            return candidate
    return None


def import_targets(ref: ImportRef, modules: set[str]) -> set[str]:
    """Internal modules one import statement depends on (``from m import sub`` → ``m.sub``)."""
    if not ref.names:
        found = _nearest(ref.module, modules)
        return {found} if found else set()
    targets: set[str] = set()
    for name in ref.names:
        found = _nearest(f"{ref.module}.{name}", modules)
        if found:
            targets.add(found)
    return targets


# ---------------------------------------------------------------- agreement metrics


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(a: Sequence[float], b: Sequence[float]) -> float:
    """Spearman rank correlation (average ranks for ties)."""
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=True))
    var = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return cov / var if var else 0.0


def overlap(a: set[str], b: set[str]) -> dict[str, int | float]:
    union = a | b
    return {
        "only_a": len(a - b),
        "only_b": len(b - a),
        "both": len(a & b),
        "jaccard": round(len(a & b) / len(union), 4) if union else 1.0,
    }


# ---------------------------------------------------------------- CLI


def candidates(out: Path, cache_dir: Path) -> None:
    rows = [pypi_summary(fetch.load_cached("pypi", name, cache_dir)) for name in CANDIDATES]
    sources = {name: fetch.cached_sha256("pypi", name, cache_dir) for name in CANDIDATES}
    columns = (
        "name",
        "version",
        "released",
        "license",
        "status",
        "requires_python",
        "wheels_3.14",
        "wheels_3.15",
    )
    table = "\n".join(
        [
            "| " + " | ".join(columns) + " |",
            "|" + "---|" * len(columns),
            *("| " + " | ".join(row[c] for c in columns) + " |" for row in rows),
        ]
    )
    header = (
        "# Tool candidates: PyPI facts\n\n"
        f"Legacy pin: pysport@{pin_short(PYSPORT)}. "
        "Source: cached `https://pypi.org/pypi/<name>/json` "
        "(SHA-256 per file in `candidates.json`, cache `~/.cache/sportorg-stage1/pypi/`). "
        "`released` = first upload of the latest version; wheels = installable by CPython "
        "(GIL build) on Linux x86_64 (manylinux), macOS, Windows amd64."
    )
    data: Json = {"rows": [dict(r) for r in rows], "cache_sha256": dict(sources)}
    write_outputs(out, "candidates", data, table, header)


class Options(argparse.Namespace):
    command: str = ""
    out: Path = Path()
    cache_dir: Path = fetch.DEFAULT_CACHE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidates",))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=fetch.DEFAULT_CACHE)
    args = parser.parse_args(argv, namespace=Options())
    candidates(args.out, args.cache_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
