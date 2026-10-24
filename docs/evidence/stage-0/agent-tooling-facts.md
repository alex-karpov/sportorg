# Agent tooling facts (date seen: 2026-10-24). Facts only, no recommendations.

Note on sources: developers.openai.com/codex/* pages return HTTP 308 redirects to learn.chatgpt.com/docs/* (server-supplied Location header). Facts below were read from the redirect targets (OpenAI-operated docs; the redirect itself came from developers.openai.com).

## 1. OpenAI Codex CLI
- Latest release: rust-v0.164.0 (name "0.164.0"), published 2026-10-23T04:48:10Z. https://github.com/openai/codex/releases/tag/rust-v0.164.0 (via GitHub API repos/openai/codex/releases/latest).
- AGENTS.md: reads it, root and nested. https://learn.chatgpt.com/docs/agent-configuration/agents-md (from developers.openai.com/codex/guides/agents-md)
  - "Starting at the project root (typically the Git root), Codex walks down to your current working directory."
  - "Files closer to your current directory override earlier guidance because they appear later in the combined prompt."
  - "Codex includes at most one file per directory." Per directory AGENTS.override.md takes precedence over AGENTS.md. Global scope: "Codex uses only the first non-empty file at this level" (AGENTS.override.md then AGENTS.md in Codex home).
  - Size: stops adding files at `project_doc_max_bytes` (default 32 KiB). Alternate names via `project_doc_fallback_filenames`; "Filenames not on this list are ignored for instruction discovery."
- Skills (SKILL.md): https://learn.chatgpt.com/docs/build-skills (from developers.openai.com/codex/skills)
  - Repo: "Codex scans `.agents/skills` in every directory from your current working directory up to the repository root."
  - User: `$HOME/.agents/skills`. Admin: `/etc/codex/skills`. System: bundled with Codex.
  - The page does NOT list `~/.codex/skills` as a location.
  - "Codex supports symlinked skill folders and follows the symlink target when scanning these locations." "Codex detects skill changes automatically."
- Hooks: YES. https://learn.chatgpt.com/docs/hooks (from developers.openai.com/codex/hooks)
  - Events: PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, UserPromptSubmit, SubagentStop, Stop, SessionStart, SubagentStart, SessionEnd. "PreToolUse and PostToolUse cover shell commands, `apply_patch`, MCP tools, and other local function tools. Hosted tools such as WebSearch aren't covered."
  - Locations: `~/.codex/hooks.json`, `~/.codex/config.toml`, `<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml`. "Project-local hooks load only when the project `.codex/` layer is trusted." "Before a non-managed hook can run, Codex requires you to review and trust the exact hook definition."
  - "Hooks are enabled by default." (disable: `[features] hooks = false`; `codex_hooks` deprecated alias). Windows: "`commandWindows` is an optional Windows-only command override."
- MCP: YES. https://learn.chatgpt.com/docs/extend/mcp?surface=cli (from developers.openai.com/codex/mcp)
  - "Codex stores MCP configuration in `config.toml`... By default this is `~/.codex/config.toml`"; "you can also scope MCP servers to a project with `.codex/config.toml` (trusted projects only)."
  - `codex mcp add <server-name> --env VAR1=VALUE1 -- <stdio server-command>`; example `codex mcp add context7 -- npx -y @upstash/context7-mcp`.
- Plugins: YES (Codex CLI and ChatGPT desktop app; not IDE extension). https://learn.chatgpt.com/docs/plugins
  - "Plugins aren't available in the IDE extension." "In Codex CLI, enter `/plugins` to open the plugin browser." Plugins bundle skills, MCP servers, hooks (and possibly browser extensions). Page does not mention the manifest path; the Superpowers repo ships `.codex-plugin/plugin.json` (see section 2).
- Sandbox modes: `read-only`, `workspace-write`, `danger-full-access` (https://learn.chatgpt.com/docs/agent-approvals-security and non-interactive-mode page). "Defaults include no network access and write permissions limited to the active workspace." Approval policy `untrusted` retired. `<writable_root>/.git` is protected read-only.
- Windows native sandbox: YES. https://learn.chatgpt.com/docs/windows/windows-sandbox: "The app can run natively in PowerShell with a Windows sandbox instead of requiring WSL or a virtual machine." "Codex supports three Windows sandbox implementations": MXC (recommended on compatible devices), Elevated (legacy fallback, needs admin approval for setup), Unelevated (legacy; "provides weaker network isolation than `elevated`", does not support denied read paths). WSL2 uses the Linux sandbox; WSL1 support ended after 0.114 (agent-approvals-security page).
- `codex exec`: YES. https://learn.chatgpt.com/docs/non-interactive-mode: "While `codex exec` runs, Codex streams progress to `stderr` and prints only the final agent message to `stdout`." Flags: `--sandbox` (default read-only), `--json`, `-o/--output-last-message`, `--output-schema`, `--ephemeral`, `--skip-git-repo-check`, `--ignore-user-config`, `--ignore-rules`, `resume --last`, `-` for stdin; "`--full-auto` is no longer supported."; `--approve-for-me` routes approvals to automatic review.
- Path deny equivalent: YES, in permission profiles, labelled Beta. https://learn.chatgpt.com/docs/permissions: "Beta. Permission profiles are under active development and may change." `[permissions.<name>.filesystem]."<path>"` takes `read`, `write`, or `deny`; "`deny` beats `write`, and `write` beats `read`." Example: `"**/*.env" = "deny"` under `[permissions.project-edit.filesystem.":workspace_roots"]` ("denies reads for matching `.env` files"). "Glob rules only cover files that exist when a sandboxed process starts." Top-level `default_permissions` selects the profile; older `sandbox_mode` settings conflict with it. "Local permission profiles are supported on macOS, Linux, WSL, and native Windows." Separately, `.rules` files (https://learn.chatgpt.com/docs/agent-configuration/rules) control commands run outside the sandbox: "Rules are experimental and may change."; precedence forbidden > prompt > allow. Rules do not cover filesystem deny paths.

## 2. Superpowers
- Installed copy: `C:\Users\ank\.claude\plugins\cache\claude-plugins-official\superpowers\7.0.0\` (package.json version 7.0.0). Upstream GitHub latest release seen: v7.0.1, published 2026-10-21T21:05:11Z (installed copy is one patch behind; v7.0.1 content NOT inspected).
- README.md "Installation" lists: Claude Code, Antigravity, Codex App, Codex CLI, Cursor, Devin CLI, Factory Droid, Gemini CLI, GitHub Copilot CLI, Grok Build CLI, Kimi Code, OpenCode, Pi, Qwen Code, Hermes Agent, Muse. Quote: "Installation differs by harness. If you use more than one, install Superpowers separately for each one."
- Codex CLI install (README.md lines 104-118): "Superpowers is available via the official Codex plugin marketplace (https://github.com/openai/plugins)." Steps: open `/plugins`; search `superpowers`; select `Install Plugin`. Codex App: Plugins in sidebar, "Superpowers" in Coding section, click `+`. Repo has `.codex-plugin/plugin.json` (name superpowers, version 7.0.0, `"skills": "./skills/"`, `"hooks": {}`).
- Claude Code install: `/plugin install superpowers@claude-plugins-official`.
- Skills in 7.0.0 (15 dirs under skills/): brainstorming, diagnosing-superpowers, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills.
- Root of installed copy also has AGENTS.md, GEMINI.md, gemini-extension.json, hooks/, plus per-harness dirs (.codex-plugin, .cursor-plugin, .opencode, .pi, .kimi-plugin, .hermes-plugin, .muse-plugin, .devin-plugin, .antigravity-plugin, .claude-plugin).
- `skills/using-superpowers/references/codex-tools.md` EXISTS. Content (in this version it is not a name-by-name Claude-to-Codex tool table; it covers):
  - Subagents need `[features] multi_agent = true` in `~/.codex/config.toml`.
  - Spawning: `spawn_agent {fork_turns: "none"}` for clean context; default `"all"` copies the transcript; on Codex 0.145+, role files under `~/.codex/agents/` attach via `agent_type`. Fix rounds: `followup_task`. V2 has no `close_agent`; V1 does. "Trust your actual tool list over any table".
  - `wait_agent` is an event subscription; recommended `timeout_ms` 300000-600000; `list_agents`.
  - Every `spawn_agent` should set `model` and `reasoning_effort` explicitly; suggests `[agents] default_subagent_model` / `default_subagent_reasoning_effort` in config.toml.
  - Environment detection via `git rev-parse --git-dir` vs `--git-common-dir`, `git branch --show-current`; Codex App finishing: commit and use "Create branch" / "Hand off to local" UI.
- State/plan file paths mentioned in installed skills (path, file:line):
  - `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`: skills/writing-plans/SKILL.md:16, :189, :198 (examples: executing-plans/SKILL.md:329, subagent-driven-development/SKILL.md:509, requesting-code-review/SKILL.md:60).
  - `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, "committed": skills/brainstorming/SKILL.md:157.
  - `.superpowers/sdd/<plan-basename>/` (workspace; `progress.md` ledger, `task-<N>-brief.md`, `review-<base7>..<head7>.diff`): skills/subagent-driven-development/SKILL.md:138,146; scripts/sdd-workspace:6,24,49; scripts/task-brief:7; scripts/review-package:8; skills/executing-plans/SKILL.md:128. RELEASE-NOTES.md:171: workspace "is deleted once the final review is clean".
  - `.superpowers/brainstorm/` (visual companion; `.last-port`, `.last-token`, `<pid-ts>/content`, `/state`): skills/brainstorming/scripts/start-server.sh:9,117,120,121; scripts/stop-server.sh:6; visual-companion.md:42,43,56,58,294. visual-companion.md:58: "Remind the user to add `.superpowers/` to `.gitignore` if it's not already there."
  - `.superpowers/diagnosing-superpowers/<session-id>/report.md`: skills/diagnosing-superpowers/SKILL.md:33; templates/report.md:3; templates/case.md:3.
  - Words `plans/`, `specs/` also in skills/diagnosing-superpowers/prompts/plan-adherence.md:12 (generic reference to plan files).
  - Older `docs/plans/` paths appear only in RELEASE-NOTES.md (historical; line 640: "Migration: move existing files from `docs/plans/` to new locations if desired").

## 3. Backlog.md
- Repo https://github.com/MrLesk/Backlog.md. Licence: MIT (GitHub API spdx_id). Latest release v1.55.3 published 2026-10-23T16:21:16Z. Installed CLI `backlog --version` = 1.54.0 (one minor behind).
- `backlog init [projectName]` non-interactive flags (local `backlog init --help`): `--defaults`, `--agent-instructions <claude,agents,gemini,copilot,cursor,none>` ("cursor (writes AGENTS.md)"), `--integration-mode <cli|mcp|none>` (default cli), `--backlog-dir`, `--config-location <folder|root>`, `--task-prefix`, `--no-git`, `--check-branches`, `--include-remote`, `--branch-days`, `--bypass-git-hooks`, `--zero-padded-ids`, `--default-editor`, `--web-port`, `--auto-open-browser`, `--install-claude-agent`. Help example: `backlog init "My Project" --defaults --agent-instructions agents,claude`.
- `backlog task create [title]` (local help): `-d/--description`, `-a/--assignee`, `-s/--status`, `-l/--labels`, `--priority`, `--type`, `--due-date`, `--ac <criteria>` (repeatable; alias `--acceptance-criteria`), `--dod`, `--plan`, `--notes`, `--final-summary`, `-m/--milestone`, `--draft`, `-p/--parent`, `--depends-on` / `--dep`, `--ref`, `--doc`, `--plain`. Default statuses: Draft, To Do, In Progress, Done; priorities High, Medium, Low; types bug, feature, enhancement, task, chore, docs, spike. Help example: `backlog task create "Add OAuth" --ac "Login succeeds"`. `backlog task edit` supports `--check-ac <index>`, `--add-label`, `--remove-label`, `--comment`, etc. Other subcommands: list, view, archive, delete, restore, demote; global `--plain` and `--json`.
- `backlog board` (`--vertical`, `-m/--milestones`; `board export [filename]`) = terminal Kanban. `backlog browser` = "open browser interface on this machine only at 127.0.0.1" (`-p/--port`, `--no-open`, `--non-interactive`); default port 6420.
- Files: README: "Everything is stored as human-readable Markdown in a project-local backlog folder such as `backlog/`, `.backlog/`, or a custom project-relative path"; config in `backlog.config.yml`, `backlog/config.yml` or `.backlog/config.yml`; tasks in `backlog/tasks/`. IDs default `TASK-N` (prefix configurable).
- Sample task file (real file from the Backlog.md repo, backlog/tasks/back-200 - Add-Claude-Code-integration-with-workflow-commands-during-init.md, truncated):

```
---
id: BACK-200
title: Add Claude Code integration with workflow commands during init
status: To Do
assignee: []
created_date: '2025-07-23'
updated_date: '2025-09-06 21:22'
labels:
  - enhancement
  - developer-experience
dependencies:
  - task-24.1
  - task-208
priority: medium
---

## Description

Enable users to leverage Claude Code's custom commands feature ...

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Claude Code template files are stored in src/templates/claude/
- [ ] #2 backlog init copies .claude directory ...
<!-- AC:END -->
```

- MCP server: YES. `backlog mcp start` = "Start the MCP server using stdio transport" (`-d/--debug`, `--cwd <path>`; env `BACKLOG_CWD`). README: `codex mcp add backlog -- backlog mcp start`; `claude mcp add backlog --scope user -- backlog mcp start`; workflow resources `backlog://workflow/overview`.
- `backlog agents --update-instructions`: local help only says "Interactively select instruction files and refresh the short Backlog.md CLI nudge". Interactive list not run (needs a Backlog project; empty dir returned "No Backlog.md project found"). From source src/agent-instructions.ts (GitHub main): `AgentInstructionFile` = AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md, README.md (default set: first four). Cursor maps to AGENTS.md. Claude subagent file `.claude/agents/project-manager-backlog.md` is written with `--install-claude-agent`.
- Codex integration: no dedicated Codex instruction file. README: "works with Claude Code, Gemini CLI, Codex, Kiro & any other MCP or CLI compatible AI assistant"; Codex is covered by the AGENTS.md nudge (`--agent-instructions agents`) and by manual `codex mcp add backlog -- backlog mcp start`; init's MCP mode "optionally auto-configures Claude Code, Codex, Gemini CLI, Kiro or Cursor".
- Default CLI nudge tells agents to run `backlog instructions overview` (README).

## 4. `claude plugin eval` (official doc exists)
- URL: https://code.claude.com/docs/en/plugin-evals ("Test plugins with evals"). Local `claude --version` = 2.1.310. Doc: "Claude Code v2.1.269 or later." Git 2.31+ if git is installed.
- Suite format: `evals/` dir in plugin; each case a subdirectory with `prompt.md` (frontmatter: case/run fields, body: prompt), `case.yaml` (optional; requires `schema_version: "1.1"` and `name`), and `graders/<name>.md` (frontmatter `type` + options, body rubric/pattern) or `graders:` in case.yaml; "a case without one fails to load". Six grader types: `regex`, `tool_used`, `tool_order`, `file_exists` (free) and `llm`, `baseline` (judge model calls, cost). Defaults: 10 turns, 300 s; runs per case default 3. Results go to `evals/results/`. `claude plugin eval init` scaffolds a suite.
- `--ablation with-without`: runs each case also without the plugin; summary shows both scores and Δ = "the with-arm score minus the without-arm score". `none` = one arm. Local help: default is with-without whenever a plugin resolves; graders marked `with-only` (incl. `tool_used: Skill`) are an indicator, not part of the score.
- `--max-cost-usd <usd>`: "A ceiling on the run's list-price cost estimate, not on plan usage. Checked before each run starts... runs that already started finish, so spend can pass the ceiling by those runs. If any run is left unstarted, the command exits 2 with partial results." Exit 1 if any case below `--threshold` (default 1.0); exit 2 partial run.
- Sandbox/Windows: "When you grant `Bash` in any form, every command runs under Claude Code's OS-level sandbox... If you grant Bash or PowerShell on a machine with no sandbox backend, Claude Code refuses each run rather than running it unconfined... Native Windows has no backend, so run shell-granting suites under WSL2; on Linux, install `bubblewrap` and `socat` first." For suites granting no shell tools the doc states no Windows restriction (that I found). https://code.claude.com/docs/en/sandboxing: "The sandbox runs on macOS, Linux, and WSL2. On native Windows, Claude Code runs commands unsandboxed."
- CI: `--trust-plugin` skips first-run trust prompt; `--no-publish` keeps HTML report local; `--json`, `--concurrency 1-8`.

## 5. GitHub Actions runners
Source: https://github.com/actions/runner-images README.md (fetched via API 2026-10-24), "Available Images" table:
- `ubuntu-latest` -> Ubuntu 24.04 x64 (`ubuntu-latest` or `ubuntu-24.04`). Ubuntu 26.04 exists as `ubuntu-26.04`, not latest.
- `windows-latest` -> Windows Server 2025 x64 (`windows-latest`, `windows-2025`, or `windows-2025-vs2026`).
- `macos-latest` -> macOS 26 Arm64 (`macos-latest`, `macos-26` or `macos-26-xlarge`). Intel macOS 26 is `macos-26-intel`.
- `windows-11-arm`: EXISTS (Windows 11 Arm64); also `windows-11-vs2026-arm`.
- `macos-15-intel`: EXISTS (macOS 15 x64: `macos-15-large`, or `macos-15-intel`). macOS 14 is marked deprecated.
- README: "In general the `-latest` label is used for the latest OS image version that is GA."
- docs.github.com page NOT fetched (README used as primary source).
- `astral-sh/setup-uv`: latest release v10.3.2 published 2026-10-22T08:47:11Z; latest major = v10 (tags v10.3.2, v10.3.1 ... v10.0.0, v9.0.0). Whether a floating `v10` tag exists: NOT VERIFIED.

## NOT VERIFIED
- Contents of Superpowers v7.0.1 vs installed 7.0.0.
- Interactive file list shown by `backlog agents --update-instructions` (taken from source, not run).
- Whether Codex permission-profile deny works identically for all glob cases on native Windows MXC (doc says profiles are supported on native Windows; unelevated sandbox does not support denied read paths).
