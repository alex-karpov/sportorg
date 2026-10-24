"""Copy an installed Claude Code plugin into ``tools/plugins/<name>`` for ``claude plugin eval``.

``claude plugin eval`` only loads plugins that live under the directory it is run against; it
refuses junctions that resolve outside it and plugin directories placed inside the eval directory
(verified 2026-10-24). So the plugin under test is copied from the local plugin cache into a
git-ignored directory, and cases reference it with ``plugins: ["../../../tools/plugins/<name>"]``.

Usage::

    uv run python scripts/pilot_setup.py code-modernization [--marketplace claude-plugins-official]
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST_DIR = ROOT / "tools" / "plugins"


class Options(argparse.Namespace):
    name: str = ""
    marketplace: str = "claude-plugins-official"


def plugin_cache() -> Path:
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config_dir) if config_dir else Path.home() / ".claude"
    return base / "plugins" / "cache"


def version_key(path: Path) -> list[int | str]:
    return [int(part) if part.isdigit() else part for part in path.name.split(".")]


def latest_version_dir(plugin_dir: Path) -> Path | None:
    versions = [p for p in plugin_dir.iterdir() if p.is_dir()]
    return max(versions, key=version_key) if versions else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("name", help="plugin name, e.g. code-modernization")
    parser.add_argument("--marketplace", default="claude-plugins-official")
    args = parser.parse_args(argv, namespace=Options())

    source_root = plugin_cache() / args.marketplace / args.name
    if not source_root.is_dir():
        print(f"plugin not found in cache: {source_root}", file=sys.stderr)
        return 1
    source = latest_version_dir(source_root)
    if source is None:
        print(f"no version directories under {source_root}", file=sys.stderr)
        return 1
    dest = DEST_DIR / args.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    print(f"{source} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
