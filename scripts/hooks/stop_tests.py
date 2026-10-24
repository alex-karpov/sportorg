"""Stop hook: run the fast tests of the packages touched in the working tree before the agent stops.

Affected package = the first directory under ``src/sportorg_ng/`` of each changed file; its tests
are ``tests/<package>/`` when that directory exists, otherwise the whole ``tests/`` tree. Changed
files under ``scripts/`` map to ``tests/scripts/``; changed test files are always included.
Exit 2 (block) with the pytest output on stderr when tests fail.
"""

from __future__ import annotations

import subprocess
import sys

from scripts.check import step_command
from scripts.hooks._common import ROOT, normalize, read_payload

PORCELAIN_PREFIX = 3  # "XY " before the path in `git status --porcelain`
SRC_PACKAGE_DEPTH = 3  # src/sportorg_ng/<package>/...


def changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return [
        normalize(line[PORCELAIN_PREFIX:].split(" -> ")[-1].strip('"'))
        for line in result.stdout.splitlines()
        if len(line) > PORCELAIN_PREFIX
    ]


def tests_for(path: str) -> str | None:
    """Test target for one changed file, or None when the file needs no tests."""
    if not path.endswith(".py"):
        return None
    if path.startswith("tests/"):
        return path
    if path.startswith("scripts/"):
        return "tests/scripts" if (ROOT / "tests" / "scripts").is_dir() else None
    if path.startswith("src/sportorg_ng/"):
        parts = path.split("/")
        if len(parts) > SRC_PACKAGE_DEPTH and (ROOT / "tests" / parts[2]).is_dir():
            return f"tests/{parts[2]}"
        return "tests"
    return None


def test_targets(files: list[str]) -> list[str]:
    targets = {target for path in files if (target := tests_for(path)) is not None}
    if "tests" in targets:
        return ["tests"]
    return sorted(targets)


def main() -> int:
    payload = read_payload()
    if payload.get("stop_hook_active") is True:
        return 0  # already continuing because of this hook; never loop
    targets = test_targets(changed_files())
    if not targets:
        return 0
    cmd = [*step_command("tests"), "-x", *targets]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        print(f"Tests failed ({' '.join(cmd)}):\n{result.stdout}{result.stderr}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
