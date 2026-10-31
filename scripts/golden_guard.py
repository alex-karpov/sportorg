"""Golden files change only with the maintainer's approval in the commit (rule 5, ADR-0008).

Every commit that adds, changes, renames or deletes anything under ``tests/golden/`` must carry a
non-empty ``Golden-Approved-By:`` trailer. The check runs the same way in CI, in
``scripts/check.py`` and in the git hooks, so it does not depend on which agent or person made the
commit.

Which commits are checked (``range``): those reachable from HEAD but not from the merge-base with
``origin/main`` (else ``main``), plus those after ``--base`` / ``GOLDEN_BASE`` (CI passes the pushed
``before`` or the pull-request base, which covers pushes to ``main`` itself). A base of zeros means
"no base". An unknown base is tolerated while the merge-base range is not empty; on the default
branch it fails closed, because the range would otherwise be empty.

The trailer is parsed by ``git interpret-trailers``: text in the body is not an approval.
The trailer can be typed by anyone who can commit; ADR-0008 records that limit.

``protected`` lists the files that define the checks (CI, hooks, ``check.py``, the guard, project
configuration, golden files) changed in the same range, with the ``git diff`` command to review.
It never fails: it makes condition 3 of ADR-0008 visible on every push (pre-push hook, verbose).
With ``--pre-push`` (only the git hooks pass it) the head is the pushed ref (``PRE_COMMIT_TO_REF``,
set by pre-commit) and pushing a deletion checks nothing. Without the flag the variable is ignored:
pre-commit exports it to every pre-push hook, the test run included.

Usage::

    uv run python -m scripts.golden_guard range [--base REV] [--head REV] [--pre-push]
    uv run python -m scripts.golden_guard protected [--base REV] [--head REV] [--pre-push]
    uv run python -m scripts.golden_guard commit-msg FILE        # git commit-msg hook

Exit codes: 0 ok, 1 unapproved golden changes, 2 history or usage error.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

GOLDEN_DIR = "tests/golden"
TRAILER = "Golden-Approved-By"
DEFAULT_BRANCH = "main"
ZERO_SHA = "0" * 40
STAGED = "(staged)"
# Files that define what "green" means and how golden files are protected (ADR-0008, condition 3).
# A trailing "/" marks a directory; other entries are fnmatch patterns on the repository path.
PROTECTED = (
    ".github/",
    ".pre-commit-config.yaml",
    ".claude/settings.json",
    "AGENTS.md",
    "pyproject.toml",
    "scripts/check.py",
    "scripts/golden_*.py",
    "scripts/hooks/",
    f"{GOLDEN_DIR}/",
)
HINT = (
    f'Add a "{TRAILER}: <maintainer>" trailer to the commit only after the maintainer confirmed '
    "the change (AGENTS.md rule 5, ADR-0008)."
)


class GuardError(RuntimeError):
    """The range of commits to check cannot be determined."""


@dataclass(frozen=True, slots=True)
class Violation:
    commit: str
    subject: str
    paths: tuple[str, ...]


def _git(*args: str, cwd: Path, stdin: str | None = None) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=cwd,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        check=False,
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)}: {result.stderr.strip()}"
        raise GuardError(msg)
    return result.stdout


def _split_z(output: str) -> list[str]:
    return [item for item in output.split("\0") if item]


def is_golden(path: str) -> bool:
    """Whether ``path`` is under ``tests/golden`` (case-insensitive: Windows and macOS defaults)."""
    normalized = path.replace("\\", "/").casefold()
    golden = GOLDEN_DIR.casefold()
    return normalized == golden or normalized.startswith(golden + "/")


def is_protected(path: str) -> bool:
    """Whether ``path`` is one of the files that define the checks (case-insensitive)."""
    normalized = path.replace("\\", "/").casefold()
    for pattern in (p.casefold() for p in PROTECTED):
        if pattern.endswith("/"):
            if normalized.startswith(pattern) or normalized == pattern[:-1]:
                return True
        elif fnmatch.fnmatchcase(normalized, pattern):
            return True
    return False


def approvals(message: str, *, cwd: Path) -> list[str]:
    """Non-empty values of the approval trailer in ``message``, as git parses trailers."""
    parsed = _git("interpret-trailers", "--parse", cwd=cwd, stdin=message)
    found: list[str] = []
    for line in parsed.splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip().casefold() == TRAILER.casefold() and value.strip():
            found.append(value.strip())
    return found


def changed_paths(commit: str, *, cwd: Path) -> list[str]:
    """Paths a commit changes; for a merge, only paths that differ from every parent."""
    output = _git(
        "diff-tree",
        "-r",
        "--root",
        "--cc",
        "--no-renames",
        "--no-commit-id",
        "--name-only",
        "-z",
        commit,
        cwd=cwd,
    )
    return _split_z(output)


def _resolve(rev: str, *, cwd: Path) -> str | None:
    try:
        return _git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", cwd=cwd).strip()
    except GuardError:
        return None


def _merge_base(head: str, *, cwd: Path) -> str | None:
    for ref in (f"origin/{DEFAULT_BRANCH}", DEFAULT_BRANCH):
        sha = _resolve(ref, cwd=cwd)
        if sha is not None:
            try:
                return _git("merge-base", head, sha, cwd=cwd).strip()
            except GuardError:
                return None
    return None


def _rev_list(base: str, head: str, *, cwd: Path) -> list[str]:
    return _git("rev-list", "--reverse", "--topo-order", f"{base}..{head}", cwd=cwd).split()


def range_commits(head: str, *, base: str | None, cwd: Path) -> list[str]:
    """Commits to check, oldest first (see the module docstring)."""
    head_sha = _resolve(head, cwd=cwd)
    if head_sha is None:
        msg = f"head {head!r} is not a commit"
        raise GuardError(msg)
    if base is not None and (not base.strip() or base.strip() == ZERO_SHA):
        base = None
    merge_base = _merge_base(head_sha, cwd=cwd)
    if merge_base is None and base is None:
        msg = f"no {DEFAULT_BRANCH} or origin/{DEFAULT_BRANCH} to compare with: pass --base"
        raise GuardError(msg)
    commits = _rev_list(merge_base, head_sha, cwd=cwd) if merge_base is not None else []
    if base is None:
        return commits
    base_sha = _resolve(base, cwd=cwd)
    if base_sha is None:
        if not commits:
            msg = (
                f"base {base} is not in the local history and the range since the merge-base "
                f"with {DEFAULT_BRANCH} is empty: fetch the full history "
                "(actions/checkout fetch-depth: 0)"
            )
            raise GuardError(msg)
        print(f"note: base {base} not found; checked the commits since the merge-base instead")
        return commits
    seen = set(commits)
    return commits + [c for c in _rev_list(base_sha, head_sha, cwd=cwd) if c not in seen]


def protected_changes(head: str = "HEAD", *, base: str | None, cwd: Path) -> list[str]:
    """Protected paths changed by the commits of the range (see ``range_commits``), sorted."""
    paths = {
        path
        for commit in range_commits(head, base=base, cwd=cwd)
        for path in changed_paths(commit, cwd=cwd)
        if is_protected(path)
    }
    return sorted(paths)


def _subject(message: str) -> str:
    for line in message.splitlines():
        if line.strip() and not line.startswith("#"):
            return line.strip()
    return ""


def check_range(head: str = "HEAD", *, base: str | None, cwd: Path) -> list[Violation]:
    return [v for v, _ in _review_range(head, base=base, cwd=cwd) if v is not None]


def _review_range(
    head: str, *, base: str | None, cwd: Path
) -> list[tuple[Violation | None, tuple[str, str] | None]]:
    """Per golden commit: a violation, or (approver, subject) when approved."""
    reviewed: list[tuple[Violation | None, tuple[str, str] | None]] = []
    for commit in range_commits(head, base=base, cwd=cwd):
        paths = tuple(sorted(p for p in changed_paths(commit, cwd=cwd) if is_golden(p)))
        if not paths:
            continue
        message = _git("log", "-1", "--format=%B", commit, cwd=cwd)
        approved = approvals(message, cwd=cwd)
        if approved:
            reviewed.append((None, (", ".join(approved), _subject(message))))
        else:
            reviewed.append((Violation(commit, _subject(message), paths), None))
    return reviewed


def check_commit_message(message_file: Path, *, cwd: Path) -> Violation | None:
    """For the commit-msg hook: staged golden changes need the trailer in the message."""
    staged = _git("diff", "--cached", "--no-renames", "--name-only", "-z", cwd=cwd)
    paths = tuple(sorted(p for p in _split_z(staged) if is_golden(p)))
    if not paths:
        return None
    message = message_file.read_text(encoding="utf-8")
    if approvals(message, cwd=cwd):
        return None
    return Violation(STAGED, _subject(message), paths)


def uncommitted_golden(*, cwd: Path) -> list[str]:
    output = _git(
        "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all", cwd=cwd
    )
    return sorted(entry[3:] for entry in _split_z(output) if is_golden(entry[3:]))


def _print_violation(violation: Violation) -> None:
    print(f"FAIL {violation.commit[:12]} {violation.subject}")
    for path in violation.paths:
        print(f"  {path}")


def _protected_report(head: str, *, base: str | None, cwd: Path) -> None:
    paths = protected_changes(head, base=base, cwd=cwd)
    if not paths:
        print("protected files: no protected files changed")
        return
    head_sha = _resolve(head, cwd=cwd) or head
    since = _merge_base(head_sha, cwd=cwd) or base or ""
    print(f"protected files changed ({len(paths)}): review the diff before it reaches main")
    for path in paths:
        print(f"  {path}")
    print(f"review: git diff {since[:12]}..{head_sha[:12]} -- " + " ".join(paths))


class Options(argparse.Namespace):
    command: str = ""
    base: str | None = None
    head: str = "HEAD"
    pre_push: bool = False
    message_file: Path = Path()


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    base = os.environ.get("GOLDEN_BASE")
    for name, text in (
        ("range", "check committed history"),
        ("protected", "list changed files that define the checks"),
    ):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--base", default=base, help="default: $GOLDEN_BASE")
        cmd.add_argument("--head", default="HEAD")
        cmd.add_argument(
            "--pre-push", action="store_true", help="head = $PRE_COMMIT_TO_REF (git pre-push hook)"
        )
    msg = sub.add_parser("commit-msg", help="check staged changes against a commit message")
    msg.add_argument("message_file", type=Path)
    return parser.parse_args(argv, namespace=Options())


def _commit_msg_command(message_file: Path, *, cwd: Path) -> int:
    violation = check_commit_message(message_file, cwd=cwd)
    if violation is None:
        return 0
    _print_violation(violation)
    print(HINT)
    return 1


def _range_command(head: str, *, base: str | None, cwd: Path) -> int:
    reviewed = _review_range(head, base=base, cwd=cwd)
    for path in uncommitted_golden(cwd=cwd):
        print(f"note: uncommitted change under {GOLDEN_DIR}/: {path} (commit it with the trailer)")
    for _, approved in reviewed:
        if approved is not None:
            print(f"approved by {approved[0]}: {approved[1]}")
    violations = [v for v, _ in reviewed if v is not None]
    for violation in violations:
        _print_violation(violation)
    if violations:
        print(HINT)
        return 1
    print(f"ok: no unapproved changes under {GOLDEN_DIR}/ ({len(reviewed)} golden commits)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cwd = Path.cwd()
    try:
        if args.command == "commit-msg":
            return _commit_msg_command(args.message_file, cwd=cwd)
        head = args.head
        if args.pre_push:
            head = os.environ.get("PRE_COMMIT_TO_REF") or head
            if head.strip() == ZERO_SHA:
                print("pre-push: deleting a remote ref, nothing to check")
                return 0
        if args.command == "protected":
            _protected_report(head, base=args.base, cwd=cwd)
            return 0
        return _range_command(head, base=args.base, cwd=cwd)
    except GuardError as error:
        print(f"golden guard: error: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
