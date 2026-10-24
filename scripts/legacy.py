"""Pinned legacy repositories: where they live, how they are fetched, verified and locked.

AGENTS.md rule 1, ADR-0006. Each repository listed in ``legacy.toml`` is cloned into
``.legacy/<name>`` (git-ignored) at its pinned commit and then locked: write bits are removed and,
on Windows, an inherited deny ACE for the current user blocks writes, renames and deletions
(the read-only attribute alone does not; see ``docs/evidence/stage-0/legacy-layout/``).
Executable copies are made by ``scripts/legacy_clone.py`` into ``.legacy-run/<name>``.

This module is the single place that knows these paths. Standard library only: the guard hook
imports it under ``uv run --no-project``.

Usage::

    uv run python -m scripts.legacy fetch [--source NAME=PATH_OR_URL]   # also applies pin updates
    uv run python -m scripts.legacy verify
    uv run python -m scripts.legacy unlock [NAME ...]   # before maintenance
    uv run python -m scripts.legacy lock [NAME ...]
    uv run python -m scripts.legacy path NAME           # print the checkout directory
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIRNAME = ".legacy"
RUN_DIRNAME = ".legacy-run"
MANIFEST = ROOT / "legacy.toml"
IS_WINDOWS = sys.platform == "win32"
WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
LOCK_PROBE = ".write-probe"

# Narrows tomllib.loads' ``dict[str, Any]`` the same way scripts/_json.py narrows json.loads.
_TOML_LOADS: Callable[[str], dict[str, object]] = tomllib.loads

# Inherited deny ACE for the current user: write, append, attributes, delete, delete-child. icacls
# cannot express it (it widens the mask to "W", which includes SYNCHRONIZE and blocks reading too),
# so PowerShell 7 sets it through .NET with the exact mask.
DENY_ACE_RIGHTS = (
    "WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, "
    "DeleteSubdirectoriesAndFiles"
)
DENY_ACE_SCRIPT = (
    "$ErrorActionPreference = 'Stop'; "
    "$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User; "
    "$acl = Get-Acl -LiteralPath $env:LEGACY_ACE_PATH; "
    "$rights = [Security.AccessControl.FileSystemRights]$env:LEGACY_ACE_RIGHTS; "
    "$inherit = [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'; "
    "$rule = [Security.AccessControl.FileSystemAccessRule]::new("
    "$sid, $rights, $inherit, 'None', 'Deny'); "
    "if ($env:LEGACY_ACE_REMOVE) { [void]$acl.RemoveAccessRule($rule) } "
    "else { $acl.AddAccessRule($rule) }; "
    "Set-Acl -LiteralPath $env:LEGACY_ACE_PATH -AclObject $acl"
)


class LegacyError(RuntimeError):
    """A pinned repository cannot be fetched, verified, locked or unlocked."""


@dataclass(frozen=True, slots=True)
class Pin:
    name: str
    url: str
    commit: str
    note: str = ""


# ---------------------------------------------------------------- locations


def main_checkout_root() -> Path:
    """The main working tree; from a git worktree, legacy still lives in the main checkout."""
    result = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    common = Path(result.stdout.strip()) if result.returncode == 0 else None
    return common.parent if common is not None and common.name == ".git" else ROOT


def legacy_dir() -> Path:
    return main_checkout_root() / LEGACY_DIRNAME


def run_dir() -> Path:
    return ROOT / RUN_DIRNAME


def checkout_dir(name: str, base: Path | None = None) -> Path:
    return (base if base is not None else legacy_dir()) / name


# ---------------------------------------------------------------- manifest


def _is_table(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def _is_array(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def load_manifest(path: Path = MANIFEST) -> list[Pin]:
    data = _TOML_LOADS(path.read_text(encoding="utf-8"))
    repos = data.get("repo")
    pins: list[Pin] = []
    for entry in repos if _is_array(repos) else []:
        if not _is_table(entry):
            continue
        fields = {key: value for key, value in entry.items() if isinstance(value, str)}
        name, url, commit = fields.get("name", ""), fields.get("url", ""), fields.get("commit", "")
        if not (name and url and len(commit) == 40):  # noqa: PLR2004 -- a full SHA-1 commit id
            msg = f"{path}: every [[repo]] needs name, url and a 40-character commit"
            raise LegacyError(msg)
        pins.append(Pin(name, url, commit, fields.get("note", "")))
    if not pins:
        msg = f"{path}: no [[repo]] entries"
        raise LegacyError(msg)
    return pins


def find_pin(name: str, pins: Sequence[Pin] | None = None) -> Pin:
    for candidate in pins if pins is not None else load_manifest():
        if candidate.name == name:
            return candidate
    msg = f"no repository named {name!r} in {MANIFEST.name}"
    raise LegacyError(msg)


# ---------------------------------------------------------------- git


def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)}: {result.stderr.strip()}"
        raise LegacyError(msg)
    return result.stdout.strip()


# ---------------------------------------------------------------- lock


def _chmod_tree(root: Path, *, writable: bool) -> None:
    """Add or remove write bits; executable bits stay, so ``git status`` remains clean."""
    entries = [root, *root.rglob("*")] if writable else [*root.rglob("*"), root]
    for path in entries:
        if path.is_symlink():
            continue
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IWUSR if writable else mode & ~WRITE_BITS)


def _deny_ace(path: Path, *, remove: bool) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        msg = "PowerShell 7 (pwsh) is needed to set the deny ACE on Windows"
        raise LegacyError(msg)
    env = os.environ | {"LEGACY_ACE_PATH": str(path), "LEGACY_ACE_RIGHTS": DENY_ACE_RIGHTS}
    env["LEGACY_ACE_REMOVE"] = "1" if remove else ""
    argv = [pwsh, "-NoProfile", "-NonInteractive", "-Command", DENY_ACE_SCRIPT]
    result = subprocess.run(argv, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        msg = f"deny ACE on {path}: {result.stderr.strip()}"
        raise LegacyError(msg)


def lock(path: Path) -> None:
    _chmod_tree(path, writable=False)
    if IS_WINDOWS:
        _deny_ace(path, remove=False)


def unlock(path: Path) -> None:
    if IS_WINDOWS:
        _deny_ace(path, remove=True)
    _chmod_tree(path, writable=True)


def is_locked(path: Path) -> bool:
    """True when a new file cannot be created at the top of ``path``."""
    probe = path / LOCK_PROBE
    try:
        probe.touch(exist_ok=False)
    except OSError:
        return True
    probe.unlink()
    return False


def _make_writable_and_retry(func: Callable[[str], object], path: str, _exc: BaseException) -> None:
    Path(path).chmod(stat.S_IWRITE | stat.S_IREAD)
    func(path)


def remove_tree(path: Path) -> None:
    """Delete a clone; git keeps object files read-only, which ``rmtree`` alone cannot remove."""
    shutil.rmtree(path, onexc=_make_writable_and_retry)


# ---------------------------------------------------------------- fetch and verify


def problems(pin: Pin, base: Path | None = None) -> list[str]:
    path = checkout_dir(pin.name, base)
    if not (path / ".git").exists():
        return [f"{pin.name}: {path} missing; run `uv run python -m scripts.legacy fetch`"]
    found: list[str] = []
    head = git("rev-parse", "HEAD", cwd=path)
    if head != pin.commit:
        found.append(f"{pin.name}: HEAD {head}, pinned {pin.commit}")
    status = git("status", "--porcelain", "--untracked-files=all", cwd=path)
    if status:
        found.append(f"{pin.name}: working tree changed:\n{status}")
    if not is_locked(path):
        found.append(f"{pin.name}: not locked; run `uv run python -m scripts.legacy lock`")
    return found


def _replaceable_head(pin: Pin, path: Path, found: list[str]) -> str:
    """HEAD of a checkout that only differs from the pin by its commit; otherwise raise."""
    pin_moved = (path / ".git").exists() and all(
        line.startswith(f"{pin.name}: HEAD ") or "not locked" in line for line in found
    )
    if not pin_moved:
        raise LegacyError("\n".join(found))
    return git("rev-parse", "HEAD", cwd=path)


def fetch(pin: Pin, source: str, base: Path | None = None) -> str:
    """Clone a missing pin; replace a clean checkout at another commit (a pin update)."""
    path = checkout_dir(pin.name, base)
    replaced = ""
    if path.exists():
        found = problems(pin, base)
        if not found:
            return f"{pin.name}: {path} already at {pin.commit}, locked"
        replaced = _replaceable_head(pin, path, found)
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        remove_tree(partial)
    partial.parent.mkdir(parents=True, exist_ok=True)
    # --no-hardlinks: a local clone would otherwise share object files (and their ACLs) with source.
    git("clone", "--quiet", "--no-hardlinks", "--no-checkout", source, str(partial))
    try:
        git(
            "-c",
            "advice.detachedHead=false",
            "checkout",
            "--quiet",
            "--detach",
            pin.commit,
            cwd=partial,
        )
    except LegacyError as error:
        remove_tree(partial)
        hint = f"\n{pin.note}" if pin.note else ""
        msg = f"{pin.name}: commit {pin.commit} not found in {source}{hint}"
        raise LegacyError(msg) from error
    if replaced:
        unlock(path)
        remove_tree(path)
    partial.rename(path)
    lock(path)
    was = f" (replaced {replaced[:12]})" if replaced else ""
    return f"{pin.name}: {path} at {git('rev-parse', 'HEAD', cwd=path)}, locked{was}"


# ---------------------------------------------------------------- command line


class Options(argparse.Namespace):
    command: str = ""
    names: list[str] | None = None
    source: list[str] | None = None


def parse_sources(values: Sequence[str]) -> dict[str, str]:
    sources: dict[str, str] = {}
    for value in values:
        name, sep, where = value.partition("=")
        if not sep or not name or not where:
            msg = f"--source expects NAME=PATH_OR_URL, got {value!r}"
            raise LegacyError(msg)
        sources[name] = where
    return sources


def run(args: Options) -> int:
    pins = load_manifest()
    if args.command == "path":
        names = args.names or []
        print(checkout_dir(find_pin(names[0], pins).name) if names else legacy_dir())
        return 0
    selected = [find_pin(name, pins) for name in args.names] if args.names else pins
    if args.command == "fetch":
        sources = parse_sources(args.source or [])
        for pin in selected:
            print(fetch(pin, sources.get(pin.name, pin.url)))
        return 0
    if args.command in {"lock", "unlock"}:
        action = lock if args.command == "lock" else unlock
        for pin in selected:
            action(checkout_dir(pin.name))
            print(f"{pin.name}: {args.command}ed")
        return 0
    found = [problem for pin in selected for problem in problems(pin)]
    for line in found:
        print(line)
    if not found:
        print(f"ok: {', '.join(f'{pin.name}@{pin.commit[:12]}' for pin in selected)} locked")
    return 1 if found else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    fetch_parser = commands.add_parser(
        "fetch", help="clone missing pins, replace clean checkouts at an old pin, verify the rest"
    )
    fetch_parser.add_argument("names", nargs="*")
    fetch_parser.add_argument("--source", action="append", help="NAME=PATH_OR_URL override")
    for name in ("verify", "lock", "unlock"):
        commands.add_parser(name).add_argument("names", nargs="*")
    commands.add_parser("path").add_argument("names", nargs="*")
    args = parser.parse_args(argv, namespace=Options())
    try:
        return run(args)
    except LegacyError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
