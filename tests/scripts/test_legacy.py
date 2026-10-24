"""Tests for scripts/legacy.py: the manifest and fetch, including pin updates (ADR-0006).

File-mode and ACL locking are measured by scripts/probe_legacy_protection.py; here the lock is a
set of paths, so the git logic runs the same on every OS and as root in the CI container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import legacy
from scripts.legacy import LegacyError, Pin

if TYPE_CHECKING:
    from pathlib import Path

IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")


@pytest.fixture
def source(tmp_path: Path) -> tuple[Path, list[str]]:
    """A repository with two commits; returns its path and the commit ids, oldest first."""
    repo = tmp_path / "source"
    legacy.git("init", "--quiet", str(repo))
    commits: list[str] = []
    for text in ("one", "two"):
        (repo / "file.txt").write_text(text, encoding="utf-8")
        legacy.git("add", "file.txt", cwd=repo)
        legacy.git(*IDENTITY, "commit", "--quiet", "-m", text, cwd=repo)
        commits.append(legacy.git("rev-parse", "HEAD", cwd=repo))
    return repo, commits


@pytest.fixture
def locked(monkeypatch: pytest.MonkeyPatch) -> set[Path]:
    paths: set[Path] = set()

    def lock(path: Path) -> None:
        paths.add(path)

    def unlock(path: Path) -> None:
        paths.discard(path)

    def is_locked(path: Path) -> bool:
        return path in paths

    monkeypatch.setattr(legacy, "lock", lock)
    monkeypatch.setattr(legacy, "unlock", unlock)
    monkeypatch.setattr(legacy, "is_locked", is_locked)
    return paths


def test_fetch_clones_the_pinned_commit_and_locks_it(
    tmp_path: Path, source: tuple[Path, list[str]], locked: set[Path]
) -> None:
    repo, commits = source
    base = tmp_path / ".legacy"
    pin = Pin("demo", "unused", commits[0])

    legacy.fetch(pin, str(repo), base)

    checkout = base / "demo"
    assert legacy.git("rev-parse", "HEAD", cwd=checkout) == commits[0]
    assert checkout in locked
    assert legacy.problems(pin, base) == []


def test_fetch_leaves_a_checkout_at_the_pin_alone(
    tmp_path: Path, source: tuple[Path, list[str]], locked: set[Path]
) -> None:
    repo, commits = source
    base = tmp_path / ".legacy"
    pin = Pin("demo", "unused", commits[0])
    legacy.fetch(pin, str(repo), base)

    assert "already at" in legacy.fetch(pin, str(repo), base)
    assert base / "demo" in locked


def test_fetch_replaces_a_clean_checkout_when_the_pin_changes(
    tmp_path: Path, source: tuple[Path, list[str]], locked: set[Path]
) -> None:
    repo, commits = source
    base = tmp_path / ".legacy"
    legacy.fetch(Pin("demo", "unused", commits[0]), str(repo), base)

    message = legacy.fetch(Pin("demo", "unused", commits[1]), str(repo), base)

    checkout = base / "demo"
    assert legacy.git("rev-parse", "HEAD", cwd=checkout) == commits[1]
    assert f"replaced {commits[0][:12]}" in message
    assert checkout in locked
    assert not (base / "demo.partial").exists()


def test_fetch_refuses_to_replace_a_changed_working_tree(
    tmp_path: Path, source: tuple[Path, list[str]], locked: set[Path]
) -> None:
    repo, commits = source
    base = tmp_path / ".legacy"
    legacy.fetch(Pin("demo", "unused", commits[0]), str(repo), base)
    (base / "demo" / "file.txt").write_text("edited", encoding="utf-8")

    with pytest.raises(LegacyError, match="working tree changed"):
        legacy.fetch(Pin("demo", "unused", commits[1]), str(repo), base)

    assert legacy.git("rev-parse", "HEAD", cwd=base / "demo") == commits[0]
    assert base / "demo" in locked


def test_fetch_names_the_note_when_the_commit_is_missing(
    tmp_path: Path, source: tuple[Path, list[str]], locked: set[Path]
) -> None:
    repo, _ = source
    base = tmp_path / ".legacy"
    pin = Pin("demo", "unused", "0" * 40, note="fetch it from elsewhere")

    with pytest.raises(LegacyError, match="fetch it from elsewhere"):
        legacy.fetch(pin, str(repo), base)

    assert not (base / "demo").exists()
    assert not locked


def test_manifest_pins_pysport_and_templates() -> None:
    pins = legacy.load_manifest()

    assert [pin.name for pin in pins] == ["pysport", "templates"]
    assert all(len(pin.commit) == 40 and pin.url.startswith("https://") for pin in pins)


def test_manifest_rejects_a_short_commit(tmp_path: Path) -> None:
    manifest = tmp_path / "legacy.toml"
    manifest.write_text('[[repo]]\nname = "x"\nurl = "u"\ncommit = "abc"\n', encoding="utf-8")

    with pytest.raises(LegacyError, match="40-character commit"):
        legacy.load_manifest(manifest)
