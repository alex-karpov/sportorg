"""Create a fresh clone of the pinned legacy commit for execution (AGENTS.md rule 1).

The read-only checkout in ``../_other/pysport-legacy`` is never executed or modified. Anything
that runs legacy code (oracle, smoke tests, benchmarks) works on the clone this script produces
and records the commit hash it verified.

Usage::

    uv run python scripts/legacy_clone.py [--dest .legacy-run/pysport]
                                          [--source ../_other/pysport-legacy]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_COMMIT = "30d849dde1f7ebe04599098b3344b72fdb1210fe"
DEFAULT_SOURCE = ROOT.parent / "_other" / "pysport-legacy"
DEFAULT_DEST = ROOT / ".legacy-run" / "pysport"


class Options(argparse.Namespace):
    source: Path = DEFAULT_SOURCE
    dest: Path = DEFAULT_DEST
    force: bool = False


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--force", action="store_true", help="replace an existing destination")
    return parser.parse_args(argv, namespace=Options())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not (args.source / ".git").exists():
        print(f"legacy source not found: {args.source}", file=sys.stderr)
        return 1
    if args.dest.exists():
        if not args.force:
            head = git("rev-parse", "HEAD", cwd=args.dest)
            if head == PINNED_COMMIT:
                print(f"{args.dest} already at {PINNED_COMMIT}")
                return 0
            msg = f"{args.dest} exists at {head}, not the pinned commit; use --force"
            print(msg, file=sys.stderr)
            return 1
        shutil.rmtree(args.dest)
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--no-checkout", str(args.source), str(args.dest)],
        check=True,
    )
    git("checkout", "--quiet", "--detach", PINNED_COMMIT, cwd=args.dest)
    head = git("rev-parse", "HEAD", cwd=args.dest)
    if head != PINNED_COMMIT:
        print(f"clone is at {head}, expected {PINNED_COMMIT}", file=sys.stderr)
        return 1
    print(f"{args.dest} at {head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
