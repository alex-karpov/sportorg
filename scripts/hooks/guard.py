"""PreToolUse guard: legacy stays read-only, golden files need the maintainer.

Input: hook JSON on stdin (``tool_name``, ``tool_input``). Output: a PreToolUse decision JSON on
stdout (``deny`` or ``ask``), or nothing to let the tool proceed. Best effort: shell matching is
textual, so the rule in AGENTS.md remains the real rule. Runs with ``uv run --no-project`` so it
does not depend on the project environment.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from typing import Literal

from scripts._json import Json, as_dict, as_str
from scripts.hooks._common import GOLDEN_PREFIXES, is_legacy, read_payload, relative_to_root

FILE_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
SHELL_TOOLS = frozenset({"Bash", "PowerShell"})

# Commands that change files or repository state when combined with a legacy path.
MUTATING = re.compile(
    r"(^|[\s;&|(`])("
    r"rm|rmdir|del|erase|mv|move|cp|copy|touch|mkdir|md|tee|sed\s+-i|chmod|chown|truncate|"
    r"uv\s+(sync|add|remove|lock|pip|init|build|venv)|pip|poetry|maturin|cargo|npm|make|"
    r"git(\s+-C\s+\S+|\s+--git-dir=\S+|\s+-c\s+\S+)*\s+(checkout|switch|reset|stash|clean|commit|"
    r"rebase|merge|pull|push|add|rm|mv|restore|apply|am|cherry-pick|tag|worktree|submodule|gc|prune|"
    r"branch\s+-[dDm])|"
    r"cd|Set-Location|Remove-Item|Move-Item|Copy-Item|New-Item|Set-Content|Add-Content|Out-File"
    r")\b|>>?",
)

LEGACY_FILE_REASON = "Legacy checkout is read-only (AGENTS.md rule 1)."
LEGACY_SHELL_REASON = (
    "This command could modify the read-only legacy checkout (AGENTS.md rule 1). "
    "Read-only git/grep commands are fine; to execute legacy use scripts/legacy_clone.py."
)


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


def evaluate(tool_name: str, tool_input: dict[str, Json]) -> Decision | None:
    """Decide for one tool call; None means "no opinion, let the tool run"."""
    if tool_name in FILE_TOOLS:
        path = as_str(tool_input.get("file_path")) or as_str(tool_input.get("notebook_path"))
        if not path:
            return None
        if is_legacy(path):
            return Decision("deny", LEGACY_FILE_REASON)
        rel = relative_to_root(path)
        if rel is not None and rel.startswith(GOLDEN_PREFIXES):
            reason = f"{rel} is a golden file: changes need the maintainer's confirmation (rule 5)."
            return Decision("ask", reason)
        return None
    if tool_name in SHELL_TOOLS:
        command = as_str(tool_input.get("command"))
        if is_legacy(command) and MUTATING.search(command):
            return Decision("deny", LEGACY_SHELL_REASON)
    return None


def main() -> int:
    payload = read_payload()
    decision = evaluate(as_str(payload.get("tool_name")), as_dict(payload.get("tool_input")))
    if decision is not None:
        print(decision.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
