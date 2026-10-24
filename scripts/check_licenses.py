"""Fail when a runtime dependency's licence is not compatible with GPL-3.0.

The project licence is GPL-3.0-or-later (ADR-0004); the allowlist is the set of licences compatible
with distributing the project under it (the same set holds for GPL-3.0-only). Package sets come from
``uv.lock`` (parsed offline): *runtime* is everything reachable from the project's ``dependencies``
(environment markers ignored, i.e. the superset), *dev* is every other locked package. Licences come
from the installed metadata
(``License-Expression``, then ``License ::`` classifiers, then the ``License`` field), are
normalised to SPDX identifiers and evaluated as SPDX expressions (``OR`` any, ``AND`` all,
``WITH`` keeps the base licence verdict).

Exit code 1 when a runtime package is denied, unknown or not installed. Dev packages are only
reported, unless ``--strict-dev`` is given (then denied or unknown dev packages also fail).

Usage: ``uv run python -m scripts.check_licenses [--json] [--strict-dev]`` (module form: the script
imports ``scripts._json``, so it must run with the repository root on ``sys.path``).
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import sys
import tomllib
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeGuard, final

if TYPE_CHECKING:
    from collections.abc import Callable

type Verdict = Literal["ok", "denied", "unknown"]

PROJECT = "sportorg-ng"
LOCK_PATH = Path(__file__).resolve().parent.parent / "uv.lock"

ALLOWED = frozenset(
    {
        "0BSD",
        "MIT",
        "MIT-0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "ISC",
        "Apache-2.0",
        "PSF-2.0",
        "Python-2.0",
        "MPL-2.0",
        "LGPL-2.1-only",
        "LGPL-2.1-or-later",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "Unlicense",
        "Zlib",
        "CC0-1.0",
        "HPND",
        "BSL-1.0",
    }
)
DENIED = frozenset({"GPL-2.0-only", "SSPL-1.0"})
DENIED_PREFIXES = ("AGPL-",)
DENIED_WORDS = ("proprietary", "commercial")

# Free-text names and classifier tails -> SPDX (keys are lower case).
ALIASES: dict[str, str] = {
    "mit": "MIT",
    "mit license": "MIT",
    "license :: osi approved :: mit license": "MIT",
    "license :: osi approved :: mit no attribution license (mit-0)": "MIT-0",
    "license :: osi approved :: apache software license": "Apache-2.0",
    "apache software license": "Apache-2.0",
    "apache license 2.0": "Apache-2.0",
    "apache 2.0": "Apache-2.0",
    "license :: osi approved :: bsd license": "BSD-3-Clause",
    "bsd license": "BSD-3-Clause",
    "bsd": "BSD-3-Clause",
    "license :: osi approved :: isc license (iscl)": "ISC",
    "isc license": "ISC",
    "license :: osi approved :: mozilla public license 2.0 (mpl 2.0)": "MPL-2.0",
    "mozilla public license 2.0 (mpl 2.0)": "MPL-2.0",
    "license :: osi approved :: python software foundation license": "PSF-2.0",
    "python software foundation license": "PSF-2.0",
    "license :: osi approved :: zlib/libpng license": "Zlib",
    "license :: osi approved :: the unlicense (unlicense)": "Unlicense",
    "license :: cc0 1.0 universal (cc0 1.0) public domain dedication": "CC0-1.0",
    "license :: osi approved :: historical permission notice and disclaimer (hpnd)": "HPND",
    "license :: osi approved :: boost software license 1.0 (bsl-1.0)": "BSL-1.0",
    "license :: osi approved :: gnu general public license v2 (gplv2)": "GPL-2.0-only",
    "license :: osi approved :: gnu general public license v2 or later (gplv2+)": (
        "GPL-2.0-or-later"
    ),
    "license :: osi approved :: gnu general public license v3 (gplv3)": "GPL-3.0-only",
    "license :: osi approved :: gnu general public license v3 or later (gplv3+)": (
        "GPL-3.0-or-later"
    ),
    "license :: osi approved :: gnu general public license (gpl)": "GPL-UNSPECIFIED",
    "license :: osi approved :: gnu lesser general public license v2 (lgplv2)": "LGPL-2.0-only",
    "license :: osi approved :: gnu lesser general public license v2 or later (lgplv2+)": (
        "LGPL-2.1-or-later"
    ),
    "license :: osi approved :: gnu lesser general public license v3 (lgplv3)": "LGPL-3.0-only",
    "license :: osi approved :: gnu lesser general public license v3 or later (lgplv3+)": (
        "LGPL-3.0-or-later"
    ),
    "license :: osi approved :: gnu affero general public license v3": "AGPL-3.0-only",
    "license :: osi approved :: gnu affero general public license v3 or later (agplv3+)": (
        "AGPL-3.0-or-later"
    ),
    "gplv2": "GPL-2.0-only",
    "gplv2+": "GPL-2.0-or-later",
    "gplv3": "GPL-3.0-only",
    "gplv3+": "GPL-3.0-or-later",
    "gpl-2.0": "GPL-2.0-only",
    "gpl-2.0+": "GPL-2.0-or-later",
    "gpl-3.0": "GPL-3.0-only",
    "gpl-3.0+": "GPL-3.0-or-later",
    "lgpl-2.1": "LGPL-2.1-only",
    "lgpl-2.1+": "LGPL-2.1-or-later",
    "lgpl-3.0": "LGPL-3.0-only",
    "lgpl-3.0+": "LGPL-3.0-or-later",
    "license :: other/proprietary license": "LicenseRef-Proprietary",
}
_RANK: dict[Verdict, int] = {"denied": 0, "unknown": 1, "ok": 2}
_TOKEN = re.compile(r"\(|\)|[^\s()]+")
_SPDX_ID = re.compile(r"[A-Za-z0-9.+-]+")


def normalize_name(name: str) -> str:
    """PEP 503 normalisation of a distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def atom_verdict(text: str) -> Verdict:
    """Verdict for a single licence name (SPDX id, classifier or free text)."""
    key = text.strip()
    spdx = ALIASES.get(key.lower(), key)
    lowered = spdx.lower()
    verdict: Verdict = "unknown"
    if spdx in ALLOWED:
        verdict = "ok"
    elif (
        spdx in DENIED
        or spdx.startswith(DENIED_PREFIXES)
        or "affero" in lowered
        or any(word in lowered for word in DENIED_WORDS)
    ):
        verdict = "denied"
    return verdict


@final
class _Parser:
    """Recursive-descent evaluator for SPDX expressions (OR, AND, WITH, parentheses)."""

    def __init__(self, text: str) -> None:
        self.tokens: list[str] = _TOKEN.findall(text)
        self.pos: int = 0

    def peek(self) -> str:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ""

    def take(self) -> str:
        token = self.peek()
        self.pos += 1
        return token

    def or_expr(self) -> Verdict:
        best = self.and_expr()
        while self.peek().upper() == "OR":
            self.take()
            other = self.and_expr()
            best = max(best, other, key=_RANK.__getitem__)
        return best

    def and_expr(self) -> Verdict:
        worst = self.term()
        while self.peek().upper() == "AND":
            self.take()
            other = self.term()
            worst = min(worst, other, key=_RANK.__getitem__)
        return worst

    def term(self) -> Verdict:
        piece = self.take()
        if piece == "(":
            inner = self.or_expr()
            if self.take() != ")":
                msg = "missing closing parenthesis"
                raise ValueError(msg)
            return inner
        if not _SPDX_ID.fullmatch(piece) or piece.upper() in {"OR", "AND", "WITH"}:
            msg = f"unexpected token {piece!r}"
            raise ValueError(msg)
        verdict = atom_verdict(piece)
        if self.peek().upper() == "WITH":
            self.take()
            self.take()  # the exception id never changes the base licence's verdict
        return verdict


def expression_verdict(text: str) -> Verdict:
    """Verdict for a licence string: a known name, else an SPDX expression, else unknown."""
    stripped = text.strip()
    if not stripped:
        return "unknown"
    if stripped.lower() in ALIASES:
        return atom_verdict(stripped)
    parser = _Parser(stripped)
    try:
        verdict = parser.or_expr()
    except ValueError:
        return atom_verdict(stripped)
    if parser.pos != len(parser.tokens):
        return atom_verdict(stripped)
    return verdict


def combine_any(verdicts: list[Verdict]) -> Verdict:
    """Several independent declarations (classifiers) are alternatives, as in a dual licence."""
    return max(verdicts, key=_RANK.__getitem__) if verdicts else "unknown"


def metadata_verdict(
    expression: str | None, classifiers: list[str], field: str | None
) -> tuple[Verdict, str]:
    """Verdict and the licence text used, by priority: expression, classifiers, ``License``."""
    if expression and expression.strip():
        return expression_verdict(expression), expression.strip()
    licences = [c for c in classifiers if c.startswith("License ::")]
    if licences:
        return combine_any([expression_verdict(c) for c in licences]), "; ".join(licences)
    if field and field.strip() and field.strip().upper() != "UNKNOWN":
        first_line = field.strip().splitlines()[0]
        return expression_verdict(field), first_line
    return "unknown", ""


# ------------------------------------------------------------------ uv.lock

_LOADS: Callable[[str], dict[str, object]] = tomllib.loads


def _is_table(value: object) -> TypeGuard[dict[str, object]]:
    """TOML tables always have ``str`` keys."""
    return isinstance(value, dict)


def _is_array(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _objects(value: object) -> list[dict[str, object]]:
    return [item for item in value if _is_table(item)] if _is_array(value) else []


def _str(value: object) -> str:
    return value if isinstance(value, str) else ""


def lock_graph(text: str) -> dict[str, list[str]]:
    """Map each locked package (normalised name) to its dependencies' names (all groups)."""
    graph: dict[str, list[str]] = {}
    for package in _objects(_LOADS(text).get("package")):
        name = normalize_name(_str(package.get("name")))
        deps = [normalize_name(_str(d.get("name"))) for d in _objects(package.get("dependencies"))]
        graph[name] = deps
    return graph


def split_packages(text: str, project: str = PROJECT) -> tuple[list[str], list[str]]:
    """Return (runtime, dev) package names: reachable from the project's dependencies, the rest."""
    graph = lock_graph(text)
    root = normalize_name(project)
    seen: set[str] = set()
    queue = deque(graph.get(root, []))
    while queue:
        name = queue.popleft()
        if name in seen or name == root:
            continue
        seen.add(name)
        queue.extend(graph.get(name, []))
    runtime = sorted(seen)
    dev = sorted(name for name in graph if name != root and name not in seen)
    return runtime, dev


# ------------------------------------------------------------------ report


def inspect_package(name: str) -> dict[str, str]:
    """One report row from the installed metadata of ``name``."""
    try:
        meta = importlib.metadata.metadata(name)
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return {"name": name, "version": "", "licence": "", "status": "not installed"}
    verdict, licence = metadata_verdict(
        meta.get("License-Expression"), meta.get_all("Classifier") or [], meta.get("License")
    )
    return {"name": name, "version": version, "licence": licence, "status": verdict}


def _format(row: dict[str, str]) -> str:
    licence = row["licence"] or "(no licence metadata)"
    return f"  {row['status']:<13} {row['name']} {row['version']}: {licence}"


class Options(argparse.Namespace):
    as_json: bool = False
    strict_dev: bool = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", dest="as_json", action="store_true", help="also print JSON")
    parser.add_argument(
        "--strict-dev", action="store_true", help="fail on denied or unknown dev packages too"
    )
    args = parser.parse_args(argv, namespace=Options())

    runtime_names, dev_names = split_packages(LOCK_PATH.read_text(encoding="utf-8"))
    runtime = [inspect_package(n) for n in runtime_names]
    dev = [inspect_package(n) for n in dev_names]
    runtime_problems = [r for r in runtime if r["status"] != "ok"]
    dev_problems = [r for r in dev if r["status"] in {"denied", "unknown"}]

    print(
        f"checked {len(runtime)} runtime and {len(dev)} dev packages; "
        f"runtime problems: {len(runtime_problems)}"
    )
    if not runtime:
        print("runtime dependencies: none (the project declares no dependencies in uv.lock)")
    else:
        print("runtime:")
        print("\n".join(_format(r) for r in runtime))
    print("dev (not distributed; informational unless --strict-dev):")
    print("\n".join(_format(r) for r in dev))
    if args.as_json:
        print(json.dumps({"runtime": runtime, "dev": dev}, indent=2))
    failed = bool(runtime_problems) or (args.strict_dev and bool(dev_problems))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
