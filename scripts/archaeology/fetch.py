"""Fetch raw network responses for Stage 1 into a cache outside the repository.

Run from the repo root (each host needs the maintainer's approval, AGENTS.md / Stage 1 rules):
    uv run python -m scripts.archaeology.fetch pypi ruff radon==6.0.1
    uv run python -m scripts.archaeology.fetch osv PyPI:orjson==3.9.5 crates.io:serde==1.0.0
    uv run python -m scripts.archaeology.fetch github "repos/sportorg/pysport/issues?page=1"
    uv run python -m scripts.archaeology.fetch pypi --keys-file keys.txt

Responses go to ``<cache>/<kind>/<key>.json`` and are never requested twice; ``MANIFEST.json``
records url, fetch date and SHA-256 of each file. Analyses read the cache only (``load_cached``).
GitHub goes through ``gh api`` so that the token stays with ``gh``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import as_dict, fetch_bytes, parse_json

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from scripts._json import Json

DEFAULT_CACHE: Final = Path.home() / ".cache" / "sportorg-stage1"
USER_AGENT: Final = "sportorg-stage1-archaeology"
MANIFEST: Final = "MANIFEST.json"
KINDS: Final = ("pypi", "crates", "osv", "github")
_SAFE_KEY: Final = re.compile(r"[A-Za-z0-9._=@+-]+")
_HASH_LEN: Final = 12


@dataclass(frozen=True, slots=True)
class Request:
    kind: str
    key: str
    url: str
    data: bytes | None = None
    headers: tuple[tuple[str, str], ...] = ()


type Opener = Callable[[Request], bytes]


def _name_version(key: str) -> tuple[str, str | None]:
    name, sep, version = key.partition("==")
    return name, version if sep else None


def request_for(kind: str, key: str) -> Request:
    """Request for a key: ``name[==version]``, ``Ecosystem:name==version`` or a gh api path."""
    if kind == "pypi":
        name, version = _name_version(key)
        path = f"{name}/{version}" if version else name
        return Request(kind, key, f"https://pypi.org/pypi/{path}/json")
    if kind == "crates":
        name, version = _name_version(key)
        path = f"{name}/{version}" if version else name
        url = f"https://crates.io/api/v1/crates/{path}"
        return Request(kind, key, url, headers=(("User-Agent", USER_AGENT),))
    if kind == "osv":
        ecosystem, _, package = key.partition(":")
        name, version = _name_version(package)
        query = {"package": {"ecosystem": ecosystem, "name": name}, "version": version}
        data = json.dumps(query, sort_keys=True).encode()
        return Request(kind, key, "https://api.osv.dev/v1/query", data=data)
    if kind == "github":
        return Request(kind, key, f"https://api.github.com/{key}")
    msg = f"unknown kind {kind!r}; known: {', '.join(KINDS)}"
    raise ValueError(msg)


def cache_path(cache_dir: Path, kind: str, key: str) -> Path:
    """``<cache>/<kind>/<key>.json``; a key with unsafe characters gets a cleaned name + hash."""
    if _SAFE_KEY.fullmatch(key):
        name = key
    else:
        digest = hashlib.sha256(key.encode()).hexdigest()[:_HASH_LEN]
        name = f"{re.sub(r'[^A-Za-z0-9._=@+-]', '_', key)[:80]}-{digest}"
    return cache_dir / kind / f"{name}.json"


def default_opener(request: Request) -> bytes:
    if request.kind == "github":
        return subprocess.run(
            ["gh", "api", request.key], capture_output=True, check=True, timeout=60
        ).stdout
    return fetch_bytes(request.url, headers=dict(request.headers), data=request.data, timeout=60)


def _load_manifest(cache_dir: Path) -> dict[str, Json]:
    path = cache_dir / MANIFEST
    return as_dict(parse_json(path.read_text(encoding="utf-8"))) if path.exists() else {}


def fetch(
    requests: Sequence[Request], cache_dir: Path, opener: Opener = default_opener
) -> tuple[int, int, list[str]]:
    """Fetch the requests not yet cached; returns (fetched, already cached, errors)."""
    manifest = _load_manifest(cache_dir)
    fetched = cached = 0
    errors: list[str] = []
    for request in requests:
        target = cache_path(cache_dir, request.kind, request.key)
        if target.exists():
            cached += 1
            continue
        try:
            body = opener(request)
            parse_json(body)
        except (OSError, ValueError, urllib.error.URLError, subprocess.SubprocessError) as exc:
            errors.append(f"{request.kind}/{request.key}: {exc}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        manifest[target.relative_to(cache_dir).as_posix()] = {
            "kind": request.kind,
            "key": request.key,
            "url": request.url,
            "date": dt.datetime.now(dt.UTC).date().isoformat(),
            "sha256": hashlib.sha256(body).hexdigest(),
        }
        fetched += 1
    if fetched:
        text = json.dumps(manifest, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        (cache_dir / MANIFEST).write_text(text, encoding="utf-8", newline="\n")
    return fetched, cached, errors


def load_cached(kind: str, key: str, cache_dir: Path = DEFAULT_CACHE) -> Json:
    return parse_json(cache_path(cache_dir, kind, key).read_bytes())


def cached_sha256(kind: str, key: str, cache_dir: Path = DEFAULT_CACHE) -> str:
    return hashlib.sha256(cache_path(cache_dir, kind, key).read_bytes()).hexdigest()


class Options(argparse.Namespace):
    kind: str = ""
    keys: list[str] | None = None
    keys_file: Path | None = None
    cache_dir: Path = DEFAULT_CACHE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("keys", nargs="*")
    parser.add_argument("--keys-file", type=Path, help="one key per line")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    args = parser.parse_args(argv, namespace=Options())
    keys = list(args.keys or [])
    if args.keys_file is not None:
        lines = args.keys_file.read_text(encoding="utf-8").splitlines()
        keys += [line.strip() for line in lines if line.strip()]
    fetched, cached, errors = fetch([request_for(args.kind, k) for k in keys], args.cache_dir)
    print(f"{args.kind}: fetched {fetched}, cached {cached}, errors {len(errors)}")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
