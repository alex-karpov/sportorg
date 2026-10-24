"""Shared helpers for agent hooks (Claude Code today; any agent that pipes JSON on stdin).

Only the standard library and ``scripts._json`` are used, so the guard hook can run with
``uv run --no-project`` and keeps working when the project environment is broken.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts._json import Json, as_dict, parse_json

HOOKS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = HOOKS_DIR.parent
ROOT = SCRIPTS_DIR.parent

# Markers of the read-only legacy checkout (AGENTS.md rule 1), matched on normalized paths/commands.
LEGACY_MARKERS = ("pysport-legacy",)
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


def is_legacy(path_or_command: str) -> bool:
    text = normalize(path_or_command)
    return any(marker in text for marker in LEGACY_MARKERS)
