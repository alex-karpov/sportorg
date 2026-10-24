"""Temporary git repositories for the archaeology tests: synthetic data, no legacy, no network."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import legacy

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")

type Commit = Callable[[str, dict[str, bytes]], str]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    legacy.git("init", "--quiet", "--initial-branch=main", str(path))
    return path


@pytest.fixture
def commit(repo: Path) -> Commit:
    """Write ``files`` (path -> bytes), commit them with ``message`` and return the commit id."""

    def make(message: str, files: dict[str, bytes]) -> str:
        for name, content in files.items():
            target = repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            legacy.git("add", "--", name, cwd=repo)
        legacy.git(*IDENTITY, "commit", "--quiet", "--allow-empty", "-m", message, cwd=repo)
        return legacy.git("rev-parse", "HEAD", cwd=repo)

    return make
