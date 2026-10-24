"""Check the ``[код: …]`` tags of an evidence directory against the legacy source at the pins.

Run from the repo root:
    uv run python -m scripts.archaeology.verify_locs --evidence docs/evidence/stage-1/<dir> \
        --sample 10 --seed 1

Prints every problem (file missing at the pin, line out of range) and a seeded random sample of tags
with their source lines for comparison by eye. Exit code 1 if there is any problem.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from scripts import legacy
from scripts.archaeology.common import Loc, git_raw, parse_tags, physical_lines, repo_root

if TYPE_CHECKING:
    from collections.abc import Mapping

type Pins = Mapping[str, tuple[Path, str]]

EVIDENCE_SUFFIXES = (".md", ".json", ".txt")


def default_pins() -> dict[str, tuple[Path, str]]:
    return {pin.name: (repo_root(pin.name), pin.commit) for pin in legacy.load_manifest()}


def _read_at_pin(
    loc: Loc, pins: Pins, cache: dict[tuple[str, str], list[str] | None]
) -> list[str] | None:
    key = (loc.repo, loc.path)
    if key not in cache:
        repo, commit = pins[loc.repo]
        try:
            cache[key] = physical_lines(git_raw(repo, "show", f"{commit}:{loc.path}"))
        except legacy.LegacyError:
            cache[key] = None
    return cache[key]


def check(locs: list[Loc], pins: Pins | None = None) -> list[str]:
    """Problems with ``locs``: file missing at the pin or a line outside the file."""
    pins = pins if pins is not None else default_pins()
    cache: dict[tuple[str, str], list[str] | None] = {}
    problems: list[str] = []
    for loc in locs:
        short = pins[loc.repo][1][:7]
        lines = _read_at_pin(loc, pins, cache)
        if lines is None:
            problems.append(f"{loc.tag()}: file not found at {short}")
            continue
        last = loc.end if loc.end is not None else loc.line
        if loc.line < 1 or last < loc.line or last > len(lines):
            problems.append(
                f"{loc.tag()}: line {last} out of range ({len(lines)} lines at {short})"
            )
    return problems


def source_lines(loc: Loc, pins: Pins | None = None) -> list[str]:
    lines = _read_at_pin(loc, pins if pins is not None else default_pins(), {}) or []
    return lines[loc.line - 1 : loc.end if loc.end is not None else loc.line]


def collect(evidence: Path) -> tuple[list[Loc], list[str]]:
    """Unique tags of the evidence files under ``evidence``; files with tags at a foreign pin."""
    found: set[Loc] = set()
    problems: list[str] = []
    for path in sorted(evidence.rglob("*")):
        if path.suffix not in EVIDENCE_SUFFIXES or not path.is_file():
            continue
        try:
            found.update(parse_tags(path.read_text(encoding="utf-8")))
        except ValueError as exc:
            problems.append(f"{path}: {exc}")
    return sorted(found, key=lambda loc: (loc.repo, loc.path, loc.line, loc.end or 0)), problems


class Options(argparse.Namespace):
    evidence: Path = Path()
    sample: int = 10
    seed: int = 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv, namespace=Options())
    locs, problems = collect(args.evidence)
    pins = default_pins()
    problems += check(locs, pins)
    print(f"tags: {len(locs)}; problems: {len(problems)}")
    for problem in problems:
        print(f"PROBLEM {problem}")
    chosen = random.Random(args.seed).sample(locs, min(args.sample, len(locs)))  # noqa: S311 - reproducible sample, not crypto
    for loc in sorted(chosen, key=lambda loc: (loc.repo, loc.path, loc.line)):
        print(loc.tag())
        for line in source_lines(loc, pins):
            print(f"    {line}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
