# Agent environments

Facts checked 2026-10-24 (sources with URLs: `docs/evidence/stage-0/agent-tooling-facts.md`).
Nothing here is required to work on the project: every check and every proof is a plain `uv run` command.

| Practice | Claude Code 2.1.310 | OpenAI Codex CLI 0.164 | Any other agent / human |
|---|---|---|---|
| Project instructions | `CLAUDE.md` imports `AGENTS.md`; nested `CLAUDE.md` shims import nested `AGENTS.md` | reads `AGENTS.md` directly, root and nested (32 KiB combined limit) | read `AGENTS.md` |
| Quality checks | `scripts/check.py` steps run from hooks (PreToolUse guard, PostToolUse, Stop) | same commands; hooks exist (`.codex/hooks.json`: PreToolUse, PostToolUse, Stop) but are not configured yet — Backlog task | `uv run python scripts/check.py` |
| Legacy write protection | `permissions.deny` Edit rules + PreToolUse guard script | permission profiles (beta): `[permissions.<name>.filesystem]` with `deny`; sandbox `read-only`/`workspace-write` incl. native Windows | the rule in `AGENTS.md`; OS file permissions if desired |
| Superpowers | plugin `superpowers@claude-plugins-official` | plugin from the Codex marketplace (`/plugins` → superpowers); skills also load from `.agents/skills` | the discipline is in `AGENTS.md` rules 3–4; no tool needed |
| code-modernization | plugin, commands `/modernize-*` | not available; equivalents are the project scripts (oracle comparison from Stage 2) | same scripts |
| Backlog.md | CLI; MCP optional: `claude mcp add backlog -- backlog mcp start` | CLI; MCP optional: `codex mcp add backlog -- backlog mcp start` | CLI |
| Sandbox for autonomous runs | macOS, Linux, WSL2 only; none on native Windows | native Windows sandbox (MXC) available | devcontainer or VM (ADR-0003) |

What is deliberately not an equivalent: `/modernize-verify` (Claude Code only) is an extra check on top
of the project's own oracle comparison; the comparison itself must pass from the command line in any
environment (brief, Stage 5).
