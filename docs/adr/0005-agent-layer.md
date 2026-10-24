# ADR-0005: Agent layer — Backlog.md as the single task registry, plugins, hooks

- Status: accepted (Stage 0); decisions 2, 4 and 5 revised by the maintainer `[мейнтейнер: 2026-10-24]`
- Date: 2026-10-24
- Evidence: `docs/evidence/stage-0/plugins-inventory.md`, `docs/evidence/stage-0/agent-tooling-facts.md`,
  `docs/evidence/stage-0/claude-code-facts.md`, `docs/evidence/stage-0/eval-smoke*.json`,
  `docs/evidence/stage-0/legacy-layout/` (deny-rule probes), `tests/scripts/test_guard.py`.

## Context
Maintainers use different agents (Claude Code here; Codex and others elsewhere) on different OSes. The
brief requires: AGENTS.md as the only instruction source; project checks independent of any agent;
Backlog.md as the only task registry; a thin, optional Claude Code layer (Superpowers, code-modernization,
hooks, deny rule); a pilot before keeping any plugin.

## Findings from the plugin sources
Superpowers 7.0.0 writes `docs/superpowers/specs/*.md` (brainstorming) and `docs/superpowers/plans/*.md`
(writing-plans) — the plan is a checkbox list per task and step, i.e. a second task tracker — plus a
git-ignored ledger `.superpowers/sdd/<plan>/progress.md`. It never mentions an external tracker.
code-modernization 1.0.0 writes `analysis/<system>/…` (rules, reviews, equivalence evidence, verdicts
PROVEN / PARTLY PROVEN / NOT PROVEN computed by `proof_pack.py`) and `MODERNIZATION_BRIEF.md`, a phased
plan with checkbox exit criteria — a third plan. Its commands rely on `python3`, `ln -s`/`mklink /J`,
`readlink`, `rsync`, `mktemp`, `patch` (POSIX; Git Bash on Windows) and need a `legacy/<system>` link at
the workspace root. `/modernize-verify` expects built code under `modernized/…`.

## Options
| Question | Options | Chosen and why |
|---|---|---|
| Task registry | (a) Backlog.md files in the repo; (b) GitHub Issues/Projects; (c) Superpowers plan checkboxes; (d) code-modernization `MODERNIZATION_BRIEF.md` | (a): named by the brief, plain files any agent can read offline, one status per task. (b) needs network and an account per agent and lives outside the repository. (c) and (d) are per-plan checklists with no cross-plan view; they drift from each other. |
| Enforcing "legacy is read-only" | (a) rule in AGENTS.md only; (b) OS sandbox; (c) permission deny rules + guard hook + read-only file modes | (c), see ADR-0006: (a) has no enforcement; (b) does not exist for Claude Code on native Windows and covers only Bash. |
| Plugins | (a) enable by default; (b) gate each plugin on a pilot; (c) none | (b): the brief asks for data before keeping a plugin; Superpowers stays enabled because its discipline matches AGENTS.md rules 3–7, code-modernization only per machine. |
| Hooks | (a) agent-specific logic in hooks; (b) hooks call project commands only | (b): the same checks run in CI, pre-commit and for agents without hooks (Codex). |

## Decisions
1. **Backlog.md is the only status.** Plans and specs are working documents linked from a task
   (`backlog task edit <id> --plan`/`--ref`); their checkboxes carry no status (AGENTS.md rule 6).
   Locations are overridden in `CLAUDE.md`: `docs/plans/`, `docs/specs/`. `.superpowers/` and
   `.worktrees/` are git-ignored.
2. **code-modernization is local until the pilot** `[мейнтейнер: 2026-10-24]`: enabled per machine in
   `.claude/settings.local.json`, moved to project settings only after a positive pilot result
   (decision 5). When used, only for analysis and verification (`/modernize-extract-rules`,
   `/modernize-review`, `/modernize-verify`); `MODERNIZATION_BRIEF.md`, `transform`, `reimagine` and
   `uplift` are not used. `analysis/sportorg/` is committed (except `*.local.*`); `legacy/` and
   `modernized/` are git-ignored.
3. **Hooks run project commands only** (`scripts/hooks/`): PreToolUse guard (deny writes into legacy,
   ask for `tests/golden/**`), PostToolUse ruff + basedpyright on the edited file, Stop fast tests of
   the touched packages. The guard always exits 0 and turns its own errors into `ask`: a guard that
   failed closed blocked every tool in Stage 0. It runs with `uv run --no-project --python 3.14`, which
   skips syncing the project; with a healthy `.venv` uv still picks that interpreter, with a broken or
   missing one it falls back to a managed CPython 3.14 (verified in the independent check of
   2026-10-24). Its imports are stdlib, `scripts._json` and `scripts.legacy` only.
4. **Deny rules**: superseded by ADR-0006 (portable `Edit(/.legacy/**)` and `Edit(/legacy/**)`, no
   absolute paths committed).
5. **Pilot of the plugins: deferred to Stages 2–3** `[мейнтейнер: 2026-10-24]`, when project code and
   golden tests exist. The 7 cases in `evals/legacy-fixes/` stay as they are. The decision rule is
   written before the first full run (`evals/README.md`, "Decision rule"); it needs the maintainer's
   approval and a `--max-cost-usd` ceiling (Backlog TASK-2). The cases measure fixing and extending
   legacy code; they do not measure code-modernization's rule extraction and verification, which needs
   its own criterion before Stage 3 uses it. Shell-granting suites run from WSL2.
6. **Plugin versions**: `enabledPlugins` takes no version, so a plugin update changes behaviour
   silently. The versions in use (Superpowers 7.0.0, code-modernization 1.0.0 on 2026-10-24) are recorded
   with every pilot run; an update is a revisit trigger.
7. **Codex and agent-neutral protection**: Codex reads AGENTS.md natively, has hooks
   (`.codex/hooks.json`), MCP, permission profiles with filesystem `deny` (beta) and a native Windows
   sandbox; equivalents are in `docs/agents/environments.md` (hooks for Codex: TASK-3). Golden files get
   an agent-neutral check in CI before the first golden file lands (TASK-8), because the guard exists
   only for Claude Code.

## Revisit
After the pilot (decision 5); when a plugin version changes; when Codex hooks are configured (TASK-3).
