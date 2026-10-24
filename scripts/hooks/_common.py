"""Shared helpers for agent hooks (Claude Code today; any agent that pipes JSON on stdin).

Only the standard library, ``scripts._json`` and ``scripts.legacy`` are used, so the guard hook can
run with ``uv run --no-project`` and keeps working when the project environment is broken.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from scripts._json import Json, as_dict, parse_json
from scripts.legacy import LEGACY_DIRNAME

HOOKS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = HOOKS_DIR.parent
ROOT = SCRIPTS_DIR.parent

# Spellings of legacy (AGENTS.md rule 1, ADR-0006), matched on lower-case text with forward
# slashes: the pinned clones in .legacy/, the code-modernization junction legacy/sportorg that
# points into them, and the maintainer's sibling checkout that Stage 0 used.
_BEFORE = r"(?:^|[^\w.-])"
_AFTER = r"(?=/|$|[\s'\"`;|&)])"
LEGACY_PATTERNS = (
    re.compile(_BEFORE + re.escape(LEGACY_DIRNAME) + _AFTER),
    re.compile(_BEFORE + r"legacy/sportorg" + _AFTER),
    re.compile(r"pysport-legacy"),
)
# Protected golden files (AGENTS.md rule 5), relative to the repository root.
GOLDEN_PREFIXES = ("tests/golden/",)


def read_payload() -> dict[str, Json]:
    """Return the hook payload from stdin, or an empty dict when it is missing or malformed."""
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return as_dict(parse_json(raw))
    except ValueError:
        return {}


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def relative_to_root(path: str) -> str | None:
    """Path relative to the repository root with forward slashes, or None when outside it."""
    try:
        return normalize(str(Path(path).resolve().relative_to(ROOT)))
    except ValueError:
        return None


def mentions_legacy(text: str) -> bool:
    """True when ``text`` contains a path segment that names legacy (case-insensitive)."""
    lowered = normalize(text).lower()
    return any(pattern.search(lowered) for pattern in LEGACY_PATTERNS)


def is_legacy_path(path: str) -> bool:
    """True when ``path`` names legacy as written or after resolving links and junctions."""
    if mentions_legacy(path):
        return True
    try:
        resolved = Path(path).expanduser().resolve(strict=False)
    except OSError, RuntimeError, ValueError:
        return False
    return mentions_legacy(resolved.as_posix())
