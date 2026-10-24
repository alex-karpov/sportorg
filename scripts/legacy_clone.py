"""Create a fresh, writable clone of a pinned legacy repository for execution (AGENTS.md rule 1).

The read-only pinned clone in ``.legacy/<name>`` (``scripts/legacy.py``) is never executed or
modified. Anything that runs legacy code (oracle, smoke tests, benchmarks) works on the clone this
script produces, by default ``.legacy-run/<name>``, and records the commit it verified.

Usage::

    uv run python -m scripts.legacy_clone [--name pysport] [--dest DIR] [--force]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.legacy import LegacyError, checkout_dir, find_pin, remove_tree, run_dir


class Options(argparse.Namespace):
    name: str = "pysport"
    dest: Path | None = None
    force: bool = False


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--name", default="pysport", help="repository name from legacy.toml")
    parser.add_argument("--dest", type=Path, help="default: .legacy-run/<name>")
    parser.add_argument("--force", action="store_true", help="replace an existing destination")
    return parser.parse_args(argv, namespace=Options())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        pin = find_pin(args.name)
    except LegacyError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    source = checkout_dir(pin.name)
    dest = args.dest or run_dir() / pin.name
    if not (source / ".git").exists():
        print(f"{source} missing: run `uv run python -m scripts.legacy fetch`", file=sys.stderr)
        return 1
    if dest.exists():
        if not args.force:
            head = git("rev-parse", "HEAD", cwd=dest)
            if head == pin.commit:
                print(f"{dest} already at {pin.commit}")
                return 0
            print(f"{dest} exists at {head}, not the pinned commit; use --force", file=sys.stderr)
            return 1
        remove_tree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # --no-hardlinks: hard-linked objects would share the read-only lock of the source clone.
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout", str(source), str(dest)],
        check=True,
    )
    git("-c", "advice.detachedHead=false", "checkout", "--quiet", "--detach", pin.commit, cwd=dest)
    head = git("rev-parse", "HEAD", cwd=dest)
    if head != pin.commit:
        print(f"clone is at {head}, expected {pin.commit}", file=sys.stderr)
        return 1
    print(f"{dest} at {head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
