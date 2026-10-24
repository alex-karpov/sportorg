"""Fail when an installed dependency's licence is not on the project allowlist.

The project licence is GPL-3.0-or-later (provisional, open question in ADR-0004); the allowlist
is the set of licences compatible with it. Data comes from the installed metadata via
pip-licenses, so the check covers what is really in the environment (runtime and dev groups).

Usage: ``uv run python -m scripts.check_licenses [--json]`` (module form: the script imports
``scripts._json``, so it must run with the repository root on ``sys.path``).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

from scripts._json import as_dict, as_list, as_str, parse_json

ALLOWED_FRAGMENTS = (
    "MIT",
    "BSD",
    "0BSD",
    "ISC",
    "Apache",
    "PSF",
    "Python Software Foundation",
    "MPL",
    "Mozilla",
    "LGPL",
    "GNU Lesser",
    "GPL",
    "Unlicense",
    "Zlib",
    "CC0",
    "HPND",
    "Historical Permission",
)
DENIED_FRAGMENTS = ("AGPL", "Affero", "Proprietary", "Commercial")
# Packages without licence metadata whose licence was checked by hand: name -> (licence, source)
MANUAL: dict[str, tuple[str, str]] = {}
PROJECT_NAMES = frozenset({"sportorg-ng", "sportorg_ng"})


class Options(argparse.Namespace):
    as_json: bool = False


def installed_licences() -> list[dict[str, str]]:
    exe = shutil.which("pip-licenses")
    if exe is None:
        msg = "pip-licenses not found: run `uv sync` and start via `uv run python scripts/...`"
        raise SystemExit(msg)
    result = subprocess.run(
        [exe, "--format=json", "--from=mixed", "--with-urls"],
        capture_output=True,
        text=True,
        check=True,
    )
    rows: list[dict[str, str]] = []
    for item in as_list(parse_json(result.stdout)):
        row = {key: as_str(value) for key, value in as_dict(item).items()}
        if row.get("Name", "").lower() not in PROJECT_NAMES:
            rows.append(row)
    return rows


def verdict(name: str, licence: str) -> str:
    text = MANUAL[name][0] if name in MANUAL else licence
    lowered = text.lower()
    if any(fragment.lower() in lowered for fragment in DENIED_FRAGMENTS):
        return "denied"
    if any(fragment.lower() in lowered for fragment in ALLOWED_FRAGMENTS):
        return "ok"
    return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="print the full table as JSON"
    )
    args = parser.parse_args(argv, namespace=Options())

    rows = installed_licences()
    problems: list[str] = []
    for row in rows:
        name, licence = row.get("Name", "?"), row.get("License", "")
        status = verdict(name, licence)
        if status != "ok":
            version = row.get("Version", "")
            problems.append(f"{status:<8} {name} {version}: {licence or '(no licence metadata)'}")
    if args.as_json:
        print(json.dumps(rows, indent=2))
    print(f"checked {len(rows)} packages; problems: {len(problems)}")
    for line in problems:
        print("  " + line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
