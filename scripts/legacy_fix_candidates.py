"""Find bug-fix-like commits touching both tests/ and sportorg/ (read-only git use).

Run from the repo root:
    uv run --no-sync python -m scripts.legacy_fix_candidates --legacy-path PATH --out FILE
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from scripts._json import Json

PAT = re.compile(r"fix|bug|исправ|correct|wrong|error|crash|не ", re.IGNORECASE)
CC = re.compile(r"^fix(\(.*?\))?!?:", re.IGNORECASE)
MIN_NUMSTAT_FIELDS = 2

type Commit = dict[str, Json]


class Options(argparse.Namespace):
    """Typed command line options."""

    legacy_path: Path = Path()
    out: Path = Path()


def git(path: Path, *args: str) -> str:
    """Run a read-only git command in ``path`` and return its stdout."""
    return subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout


def changed_lines(path: Path, commit_hash: str) -> int:
    """Count added plus deleted lines under sportorg/ in one commit."""
    numstat = git(path, "show", "--numstat", "--format=", commit_hash, "--", "sportorg/")
    total = 0
    for line in numstat.splitlines():
        fields = line.split("\t")
        if len(fields) >= MIN_NUMSTAT_FIELDS and fields[0].isdigit() and fields[1].isdigit():
            total += int(fields[0]) + int(fields[1])
    return total


def parse_block(path: Path, block: str) -> Commit | None:
    """Turn one ``git log`` block into a candidate record, or ``None``."""
    lines = block.splitlines()
    h, d, *s = lines[0].split(" ", 2)
    msg = s[0] if s else ""
    files = [name for name in lines[1:] if name.strip()]
    if not (PAT.search(msg) or CC.match(msg)):
        return None
    tests = [f for f in files if f.startswith("tests/")]
    src = [f for f in files if f.startswith("sportorg/")]
    if not (tests and src):
        return None
    return {
        "hash": h,
        "date": d,
        "msg": msg,
        "tests": list(tests),
        "src": list(src),
        "src_lines": changed_lines(path, h),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy-path", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv, namespace=Options())
    out = git(a.legacy_path, "log", "--format=@@%H %ad %s", "--date=short", "--name-only")
    commits: list[Commit] = []
    for block in out.split("@@")[1:]:
        commit = parse_block(a.legacy_path, block)
        if commit is not None:
            commits.append(commit)
    with a.out.open("w", encoding="utf-8") as f:
        json.dump(commits, f, ensure_ascii=False, indent=1)
    print(len(commits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
