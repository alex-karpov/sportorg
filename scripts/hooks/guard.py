"""PreToolUse guard: legacy stays read-only, golden files need the maintainer.

Input: hook JSON on stdin (``tool_name``, ``tool_input``). Output: a PreToolUse decision JSON on
stdout (``deny`` or ``ask``), or nothing to let the tool proceed. The exit code is always 0: a guard
that fails closed blocks every tool of the session (Stage 0 incident), so an internal error turns
into ``ask`` for commands that mention legacy and into silence otherwise. The hook command in
``.claude/settings.json`` adds ``|| exit 1`` for failures of uv itself, which exits 2 ("block").

File tools are checked on the path as written and after resolving links and junctions. Shell
commands are checked textually, best effort: each simple command of a compound command (``;``,
``&&``, ``|``, command substitutions, ``bash -c``) is classified by its verb, ``cd`` into legacy is
tracked, and redirection targets are inspected; the project's ``scripts.legacy unlock`` is denied by
name. Subprocesses that open files themselves
(``python -c "open(...)"``) are invisible here; the read-only file modes of ``.legacy/`` stop them
(ADR-0006).
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from scripts._json import Json, as_dict, as_str
from scripts.hooks._common import (
    GOLDEN_PREFIXES,
    is_legacy_path,
    mentions_legacy,
    normalize,
    read_payload,
    relative_to_root,
)

if TYPE_CHECKING:
    from collections.abc import Callable

FILE_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
SHELL_TOOLS = frozenset({"Bash", "PowerShell"})

CD_VERBS = frozenset({"cd", "pushd", "chdir", "set-location", "sl", "push-location"})
# Every path argument of these is changed.
WRITE_VERBS = frozenset(
    {
        *("rm", "rmdir", "del", "erase", "rd", "unlink", "shred", "mkdir", "md", "touch"),
        *("truncate", "chmod", "chown", "chgrp", "chattr", "takeown"),
        *("mv", "move", "ren", "rename", "tee", "patch", "remove-item", "ri", "new-item", "ni"),
        *("set-content", "sc", "add-content", "ac", "clear-content", "clc", "out-file"),
        *("move-item", "mi", "rename-item", "rni", "set-itemproperty", "sp", "set-acl"),
    },
)
# Only the destination (last argument, or -Destination / -t / --target-directory) is changed.
COPY_VERBS = frozenset({"cp", "copy", "copy-item", "cpi", "rsync", "ln", "install", "scp", "xcopy"})
IN_PLACE_VERBS = frozenset({"sed", "perl"})
PYTHONS = frozenset({"python", "python3", "py", "pythonw"})
# Running these inside legacy, or on legacy paths, executes or installs legacy in place.
RUNNERS = frozenset(
    {
        *("pytest", "pip", "pip3", "poetry", "pdm", "hatch", "nox", "tox", "make", "npm"),
        *("npx", "pnpm", "yarn", "cargo", "maturin", "poe"),
    },
)
SHELLS = frozenset({"bash", "sh", "zsh", "dash", "pwsh", "powershell", "cmd"})
WRAPPERS = frozenset({"sudo", "command", "exec", "time", "nohup", "builtin", "&", "."})
GIT_READ = frozenset(
    {
        *("log", "show", "diff", "status", "grep", "ls-files", "ls-tree", "ls-remote"),
        *("rev-parse", "rev-list", "merge-base", "blame", "annotate", "cat-file", "describe"),
        *("shortlog", "for-each-ref", "show-ref", "name-rev", "whatchanged", "count-objects"),
        *("check-ignore", "check-attr", "var", "help", "version", "cherry", "range-diff"),
        *("show-branch", "verify-commit", "verify-tag", "fsck", "archive"),
    },
)
GIT_PATH_ARGS = frozenset({"add", "rm", "mv", "restore", "checkout", "clean", "clone", "worktree"})
GIT_OPTS_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace"})
GIT_LISTING_FIRST_ARG: dict[str, frozenset[str]] = {
    "remote": frozenset({"", "show", "get-url"}),
    "stash": frozenset({"list", "show"}),
    "notes": frozenset({"list", "show"}),
    "reflog": frozenset({"", "show"}),
    "worktree": frozenset({"list"}),
    "submodule": frozenset({"status", "summary"}),
}
BRANCH_CHANGING = frozenset(
    {
        *("-d", "-D", "-m", "-M", "-c", "-C", "-f", "-u", "--delete", "--move", "--copy"),
        *("--force", "--set-upstream-to", "--unset-upstream", "--track"),
    },
)
BRANCH_LISTING = frozenset(
    {"-l", "--list", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"},
)
UV_WRITES = frozenset({"run", "sync", "add", "remove", "lock", "pip", "init", "build", "venv"})
UV_DIR_OPTS = frozenset({"--directory", "--project"})
MAX_NESTING = 3

_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?:\n|$)", re.DOTALL)
_SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
_REDIRECT = re.compile(r"(?<![<>=-])(?:\d|&)?>>?\|?\s*(['\"]?)([^\s'\";|&<>]+)")
_ABSOLUTE = re.compile(r"^(/|[a-z]:/|\$|&)")
_FALLBACK_VERBS = re.compile(
    r"(^|[\s;&|(`])(rm|rmdir|del|mv|cp|touch|mkdir|tee|chmod|cd|remove-item|set-content|"
    r"move-item|copy-item|new-item|out-file|add-content)\b",
)
# The project's own unlock (``-m scripts.legacy unlock``, ``scripts/legacy.py unlock``, or an import
# of ``unlock``); it names no legacy path, so the checks below would not see it.
_UNLOCK = re.compile(r"scripts[./]legacy\b[^;&|\n]*\bunlock\b")

LEGACY_FILE_REASON = "Legacy is read-only (AGENTS.md rule 1)."
LEGACY_SHELL_REASON = (
    "This command could modify legacy or run it in place (AGENTS.md rule 1): {why}. Reading with "
    "git, grep, cat or a script is fine; to run legacy use scripts/legacy_clone.py."
)
GUARD_ERROR_REASON = "The legacy guard failed on this command; confirm it does not write legacy."

type Shell = Literal["bash", "powershell"]


@dataclass(frozen=True, slots=True)
class Decision:
    permission: Literal["deny", "ask"]
    reason: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": self.permission,
                    "permissionDecisionReason": self.reason,
                },
            },
        )


@dataclass(slots=True)
class Context:
    shell: Shell
    in_legacy: bool = False
    depth: int = 0


type Handler = Callable[[str, list[str], Context], str | None]


# ---------------------------------------------------------------- splitting


def _split(text: str, shell: Shell) -> list[str]:
    """Split a command line into simple commands on unquoted separators."""
    separators = ";|&\n(){}`" if shell == "bash" else ";|\n"
    parts: list[str] = []
    buf: list[str] = []
    quote = ""
    i = 0
    while i < len(text):
        ch, nxt = text[i], text[i + 1 : i + 2]
        if quote:
            buf.append(ch)
            quote = "" if ch == quote else quote
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == "&" and (nxt == ">" or (buf and buf[-1] == ">")):
            buf.append(ch)  # &> and >& are redirections, not separators
        elif (ch, nxt, shell) in {("&", "&", "powershell"), ("$", "(", "bash")}:
            parts.append("".join(buf))
            buf = []
            i += 1
        elif ch in separators:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return [part.strip() for part in parts if part.strip()]


def simple_commands(command: str, shell: Shell) -> list[str]:
    """Simple commands in execution order, plus the bodies of command substitutions."""
    if shell == "powershell":
        return _split(command.replace("`\n", " "), shell)
    text = _HEREDOC.sub("\n", command.replace("\\\n", " "))
    found = _split(text, shell)
    for match in _SUBSTITUTION.finditer(text):
        found += _split(match.group(1) or match.group(2) or "", shell)
    return found


def _words(segment: str) -> list[str] | None:
    try:
        return shlex.split(normalize(segment), posix=True)
    except ValueError:
        return None


def _verb_of(word: str) -> str:
    name = word.rsplit("/", 1)[-1].lower()
    for suffix in (".exe", ".cmd", ".bat", ".ps1"):
        name = name.removesuffix(suffix)
    return name


def _strip_wrappers(words: list[str]) -> list[str]:
    i = 0
    while i < len(words):
        word = words[i]
        if re.fullmatch(r"[A-Za-z_]\w*=.*", word) or _verb_of(word) in WRAPPERS:
            i += 1
        elif _verb_of(word) == "env":
            i += 1
            while i < len(words) and (words[i].startswith("-") or "=" in words[i]):
                i += 1
        else:
            break
    return words[i:]


def _positionals(args: list[str]) -> list[str]:
    return [arg for arg in args if not arg.startswith("-")]


def _option_value(args: list[str], i: int, inline: str) -> tuple[str, int]:
    """Value of the option at ``args[i]`` (``--opt=value`` or ``--opt value``), next index."""
    if inline:
        return inline, i + 1
    return (args[i + 1] if i + 1 < len(args) else ""), i + 2


def _targets_legacy(args: list[str], ctx: Context) -> bool:
    return ctx.in_legacy or any(mentions_legacy(arg) for arg in args)


def _is_relative(path: str) -> bool:
    return not _ABSOLUTE.match(path.lower())


# ---------------------------------------------------------------- handlers per verb


def _cd(_verb: str, args: list[str], ctx: Context) -> str | None:
    positionals = _positionals(args)
    ctx.in_legacy = bool(positionals) and mentions_legacy(positionals[0])
    return None


def _write(verb: str, args: list[str], ctx: Context) -> str | None:
    return f"{verb} on legacy" if _targets_legacy(args, ctx) else None


def _copy(verb: str, args: list[str], ctx: Context) -> str | None:
    destination = ""
    for i, arg in enumerate(args):
        option, _, inline = arg.lower().partition("=")
        if option in {"-destination", "-t", "--target-directory"}:
            destination = _option_value(args, i, inline)[0]
            break
    else:
        positionals = _positionals(args)
        destination = positionals[-1] if positionals else ""
    into = mentions_legacy(destination) or (ctx.in_legacy and _is_relative(destination))
    return f"{verb} into legacy" if into else None


def _in_place(verb: str, args: list[str], ctx: Context) -> str | None:
    in_place = any(arg.startswith(("-i", "--in-place", "-pi")) for arg in args)
    return f"{verb} -i on legacy" if in_place and _targets_legacy(args, ctx) else None


def _find(_verb: str, args: list[str], ctx: Context) -> str | None:
    deletes = any(arg in {"-delete", "-exec", "-execdir", "-ok"} for arg in args)
    return "find -delete/-exec on legacy" if deletes and _targets_legacy(args, ctx) else None


def _dd(_verb: str, args: list[str], _ctx: Context) -> str | None:
    into = any(arg.startswith("of=") and mentions_legacy(arg) for arg in args)
    return "dd into legacy" if into else None


def _acl(verb: str, args: list[str], ctx: Context) -> str | None:
    """Read-only for icacls/attrib unless a changing switch is given (/grant, +R, -R, ...)."""
    switches = {"/grant", "/deny", "/remove", "/reset", "/setowner", "/inheritance"}
    switches |= {"/restore", "/setintegritylevel", "/substitute"}
    changes = any(arg.lower().split(":", 1)[0] in switches or arg[:1] in {"+", "-"} for arg in args)
    return f"{verb} changing legacy permissions" if changes and _targets_legacy(args, ctx) else None


def _xargs(_verb: str, args: list[str], _ctx: Context) -> str | None:
    inner = _positionals(args)
    return "xargs writing legacy" if inner and _verb_of(inner[0]) in WRITE_VERBS else None


def _git_listing(sub: str, rest: list[str]) -> bool:
    """Subcommands that only list in the given form (``git branch -a``, ``git stash list``)."""
    positionals = _positionals(rest)
    if sub in GIT_LISTING_FIRST_ARG:
        return (positionals[0] if positionals else "") in GIT_LISTING_FIRST_ARG[sub]
    options = {arg.split("=", 1)[0] for arg in rest if arg.startswith("-")}
    if sub == "branch":
        lists = not positionals or bool(options & BRANCH_LISTING)
        return lists and not options & BRANCH_CHANGING
    if sub == "tag":
        return not positionals or bool(options & {"-l", "--list"})
    if sub == "config":
        reads = {"--get", "--get-all", "--get-regexp", "--list", "-l"}
        return bool(options & reads) or len(positionals) == 1
    return False


def _git(_verb: str, args: list[str], ctx: Context) -> str | None:
    location = ctx.in_legacy
    i = 0
    while i < len(args) and args[i].startswith("-"):
        option, _, inline = args[i].partition("=")
        if option in GIT_OPTS_WITH_VALUE:
            value, i = _option_value(args, i, inline)
            location = location or (option != "-c" and mentions_legacy(value))
        else:
            i += 1
    sub, rest = (args[i], args[i + 1 :]) if i < len(args) else ("", [])
    if sub in GIT_READ or _git_listing(sub, rest):
        return None
    if sub == "clone":
        positionals = _positionals(rest)
        destination = positionals[1] if len(positionals) > 1 else ""
        into = mentions_legacy(destination) or (location and _is_relative(destination))
        return f"git clone into legacy ({destination or 'current directory'})" if into else None
    if location:
        return f"git {sub} in legacy"
    if sub in GIT_PATH_ARGS and any(mentions_legacy(arg) for arg in rest):
        return f"git {sub} on a legacy path"
    return None


def _uv_options(args: list[str], *, location: bool) -> tuple[list[str], bool]:
    """Skip leading options; note whether --directory/--project points into legacy."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        option, _, inline = args[i].partition("=")
        if option in UV_DIR_OPTS:
            value, i = _option_value(args, i, inline)
            location = location or mentions_legacy(value)
        else:
            i += 1
    return args[i:], location


def _uv(_verb: str, args: list[str], ctx: Context) -> str | None:
    rest, location = _uv_options(args, location=ctx.in_legacy)
    sub, rest = (rest[0], rest[1:]) if rest else ("", [])
    if sub == "run":
        rest, location = _uv_options(rest, location=location)
    if location and sub in UV_WRITES:
        return f"uv {sub} inside legacy"
    return _classify(rest, ctx) if sub == "run" else None


def _python(_verb: str, args: list[str], ctx: Context) -> str | None:
    if ctx.in_legacy:
        return "python run inside legacy"
    i = 0
    while i < len(args) and args[i].startswith("-") and args[i] not in {"-c", "-m"}:
        i += 2 if args[i] in {"-W", "-X"} else 1
    head, rest = (args[i], args[i + 1 :]) if i < len(args) else ("", [])
    if head == "-m":
        module = rest[0] if rest else ""
        runs = module in {"pytest", "pip", "unittest", "build"} and _targets_legacy(rest[1:], ctx)
        return f"python -m {module} on legacy" if runs else None
    if head and head != "-c" and mentions_legacy(head):
        return f"legacy script {head} executed in place"
    return None


def _runner(verb: str, args: list[str], ctx: Context) -> str | None:
    return f"{verb} on legacy" if _targets_legacy(args, ctx) else None


def _shell_inner(verb: str, args: list[str], ctx: Context) -> str | None:
    if ctx.depth >= MAX_NESTING:
        return None
    for i, arg in enumerate(args[:-1]):
        if arg.lower() in {"-c", "-command", "/c"}:
            inner: Shell = "powershell" if verb in {"pwsh", "powershell", "cmd"} else "bash"
            return analyze_shell(args[i + 1], Context(inner, ctx.in_legacy, ctx.depth + 1))
    return None


HANDLERS: dict[str, Handler] = {
    **dict.fromkeys(CD_VERBS, _cd),
    **dict.fromkeys(WRITE_VERBS, _write),
    **dict.fromkeys(COPY_VERBS, _copy),
    **dict.fromkeys(IN_PLACE_VERBS, _in_place),
    **dict.fromkeys(PYTHONS, _python),
    **dict.fromkeys(RUNNERS, _runner),
    **dict.fromkeys(SHELLS, _shell_inner),
    "find": _find,
    "icacls": _acl,
    "attrib": _acl,
    "dd": _dd,
    "xargs": _xargs,
    "git": _git,
    "uv": _uv,
}


def _classify(words: list[str], ctx: Context) -> str | None:
    """Deny reason for one simple command, or None; ``cd`` updates ``ctx.in_legacy``."""
    words = _strip_wrappers(words)
    if not words:
        return None
    verb = _verb_of(words[0])
    handler = HANDLERS.get(verb)
    return handler(verb, words[1:], ctx) if handler else None


def _redirect_into_legacy(segment: str, ctx: Context) -> bool:
    for match in _REDIRECT.finditer(normalize(segment)):
        target = match.group(2)
        inside = ctx.in_legacy and _is_relative(target) and target != "/dev/null"
        if mentions_legacy(target) or inside:
            return True
    return False


def analyze_shell(command: str, ctx: Context) -> str | None:
    """Deny reason for a whole command line, or None."""
    if _UNLOCK.search(normalize(command).lower()):
        return "scripts.legacy unlock removes the lock"
    if not mentions_legacy(command) and not ctx.in_legacy:
        return None
    for segment in simple_commands(command, ctx.shell):
        if _redirect_into_legacy(segment, ctx):
            return "output redirected into legacy"
        words = _words(segment)
        if words is None:
            suspicious = ctx.in_legacy or mentions_legacy(segment)
            if suspicious and _FALLBACK_VERBS.search(segment.lower()):
                return "unparsable command with a write verb on legacy"
            continue
        reason = _classify(words, ctx)
        if reason:
            return reason
    return None


# ---------------------------------------------------------------- entry points


def evaluate(tool_name: str, tool_input: dict[str, Json]) -> Decision | None:
    """Decide for one tool call; None means "no opinion, let the tool run"."""
    if tool_name in FILE_TOOLS:
        path = as_str(tool_input.get("file_path")) or as_str(tool_input.get("notebook_path"))
        if not path:
            return None
        if is_legacy_path(path):
            return Decision("deny", LEGACY_FILE_REASON)
        rel = relative_to_root(path)
        if rel is not None and rel.startswith(GOLDEN_PREFIXES):
            reason = f"{rel} is a golden file: changes need the maintainer's confirmation (rule 5)."
            return Decision("ask", reason)
        return None
    if tool_name in SHELL_TOOLS:
        shell: Shell = "powershell" if tool_name == "PowerShell" else "bash"
        why = analyze_shell(as_str(tool_input.get("command")), Context(shell))
        return Decision("deny", LEGACY_SHELL_REASON.format(why=why)) if why else None
    return None


def main() -> int:
    payload = read_payload()
    tool_input = as_dict(payload.get("tool_input"))
    try:
        decision = evaluate(as_str(payload.get("tool_name")), tool_input)
    except Exception:  # noqa: BLE001 -- failing closed would block every tool (Stage 0 incident)
        text = json.dumps(tool_input)
        decision = Decision("ask", GUARD_ERROR_REASON) if mentions_legacy(text) else None
    if decision is not None:
        print(decision.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
