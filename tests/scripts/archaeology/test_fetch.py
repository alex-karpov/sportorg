"""Tests for scripts/archaeology/fetch.py with a fake opener (no network)."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, parse_json
from scripts.archaeology import fetch

if TYPE_CHECKING:
    from pathlib import Path

    from scripts.archaeology.fetch import Request


class FakeOpener:
    def __init__(self, bodies: dict[str, bytes]) -> None:
        self.bodies: dict[str, bytes] = bodies
        self.calls: list[Request] = []

    def __call__(self, request: Request) -> bytes:
        self.calls.append(request)
        return self.bodies[request.url]


def test_request_for_pypi_and_crates() -> None:
    assert fetch.request_for("pypi", "ruff").url == "https://pypi.org/pypi/ruff/json"
    assert fetch.request_for("pypi", "Ruff==0.17.2").url == "https://pypi.org/pypi/Ruff/0.17.2/json"
    crate = fetch.request_for("crates", "serde==1.0.0")
    assert crate.url == "https://crates.io/api/v1/crates/serde/1.0.0"
    assert ("User-Agent", fetch.USER_AGENT) in crate.headers


def test_request_for_osv_posts_a_query() -> None:
    request = fetch.request_for("osv", "PyPI:orjson==3.9.5")
    assert request.url == "https://api.osv.dev/v1/query"
    assert request.data is not None
    assert parse_json(request.data) == {
        "package": {"ecosystem": "PyPI", "name": "orjson"},
        "version": "3.9.5",
    }


def test_request_for_github_uses_the_api_path() -> None:
    key = "repos/sportorg/pysport/issues?state=all&per_page=100&page=2"
    assert fetch.request_for("github", key).url == f"https://api.github.com/{key}"


def test_request_for_unknown_kind() -> None:
    with pytest.raises(ValueError, match="unknown kind"):
        fetch.request_for("ftp", "x")


def test_cache_path_keeps_safe_keys_and_hashes_others(tmp_path: Path) -> None:
    expected = tmp_path / "pypi" / "ruff==0.17.2.json"
    assert fetch.cache_path(tmp_path, "pypi", "ruff==0.17.2") == expected
    one = fetch.cache_path(tmp_path, "github", "repos/a/b?page=1")
    two = fetch.cache_path(tmp_path, "github", "repos/a_b?page=1")
    assert one.parent == tmp_path / "github"
    assert one != two
    assert "/" not in one.name


def test_fetch_skips_existing_and_records_sha(tmp_path: Path) -> None:
    body = b'{"info": {"version": "1"}}'
    opener = FakeOpener({"https://pypi.org/pypi/ruff/json": body})
    requests = [fetch.request_for("pypi", "ruff")]
    assert fetch.fetch(requests, tmp_path, opener) == (1, 0, [])
    assert fetch.fetch(requests, tmp_path, opener) == (0, 1, [])
    assert len(opener.calls) == 1
    manifest = as_dict(parse_json((tmp_path / "MANIFEST.json").read_text(encoding="utf-8")))
    entry = as_dict(manifest["pypi/ruff.json"])
    assert entry["url"] == "https://pypi.org/pypi/ruff/json"
    assert entry["sha256"] == hashlib.sha256(body).hexdigest()
    assert fetch.load_cached("pypi", "ruff", tmp_path) == {"info": {"version": "1"}}


def test_fetch_does_not_store_a_non_json_body(tmp_path: Path) -> None:
    opener = FakeOpener({"https://pypi.org/pypi/ruff/json": b"<html>rate limited</html>"})
    fetched, cached, errors = fetch.fetch([fetch.request_for("pypi", "ruff")], tmp_path, opener)
    assert (fetched, cached) == (0, 0)
    assert len(errors) == 1
    assert errors[0].startswith("pypi/ruff:")
    assert not fetch.cache_path(tmp_path, "pypi", "ruff").exists()
