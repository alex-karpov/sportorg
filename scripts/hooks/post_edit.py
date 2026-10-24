"""PostToolUse hook: after Edit/Write of a Python file, run format, lint and type checks on it.

Exit 2 with the diagnostics on stderr so the agent sees them immediately; exit 0 otherwise.
Runs exactly the file-level steps of ``scripts/check.py``.
"""

from __future__ import annotations

import subprocess
import sys

from scripts._json import as_dict, as_str
from scripts.check import FILE_LEVEL_STEPS, step_command
from scripts.hooks._common import ROOT, read_payload, relative_to_root

CHECKED_PREFIXES = ("src/", "tests/", "scripts/")


def main() -> int:
    payload = read_payload()
    path = as_str(as_dict(payload.get("tool_input")).get("file_path"))
    if not path.endswith(".py"):
        return 0
    rel = relative_to_root(path)
    if rel is None or not rel.startswith(CHECKED_PREFIXES):
        return 0

    failures: list[str] = []
    for step in FILE_LEVEL_STEPS:
        cmd = step_command(step, files=[rel])
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode:
            failures.append(f"[{step}] {' '.join(cmd)}\n{result.stdout}{result.stderr}".rstrip())
    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
