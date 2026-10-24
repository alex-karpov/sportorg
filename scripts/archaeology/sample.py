"""Seeded samples of evidence rows for the manual checks of Phase D.

Run from the repo root:
    uv run python -m scripts.archaeology.sample \
        --json docs/evidence/stage-1/structure/dead-code.json \
        --key findings --n 30 --seed 20261025 --fields kind,name,confidence,name_in_string,tag

Prints a Markdown table of the chosen rows in their input order; the manual verdict columns are
added by hand in the ``*.manual.md`` file that records this command.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from scripts._json import Json, as_dict, as_list, parse_json


def sample(items: list[Json], n: int, *, seed: int, stratify: str | None = None) -> list[Json]:
    """``n`` items chosen with ``random.Random(seed)``, equal shares per ``stratify`` value."""
    rng = random.Random(seed)  # noqa: S311 - reproducible sample, not crypto
    if stratify is None:
        groups = [list(range(len(items)))]
    else:
        values = sorted({str(as_dict(item).get(stratify)) for item in items})
        groups = [
            [i for i, it in enumerate(items) if str(as_dict(it).get(stratify)) == v] for v in values
        ]
    chosen: list[int] = []
    for number, group in enumerate(groups):
        share = n // len(groups) + (1 if number < n % len(groups) else 0)
        chosen += rng.sample(group, min(share, len(group)))
    return [items[i] for i in sorted(chosen)]


def table(items: list[Json], fields: list[str]) -> str:
    rows = ["| # | " + " | ".join(fields) + " |", "|---|" + "---|" * len(fields)]
    for number, item in enumerate(items, start=1):
        row = as_dict(item)
        cells = [str(row.get(f, "")).replace("|", "\\|") for f in fields]
        rows.append(f"| {number} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


class Options(argparse.Namespace):
    json: Path = Path()
    key: str = ""
    n: int = 30
    seed: int = 0
    stratify: str | None = None
    fields: str = ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--key", default="", help="top-level key holding the rows; empty: the list")
    parser.add_argument("--n", type=int, default=30)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--stratify")
    parser.add_argument("--fields", required=True, help="comma-separated row fields to show")
    args = parser.parse_args(argv, namespace=Options())
    data = parse_json(args.json.read_text(encoding="utf-8"))
    items = as_list(as_dict(data).get(args.key) if args.key else data)
    print(
        table(sample(items, args.n, seed=args.seed, stratify=args.stratify), args.fields.split(","))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
