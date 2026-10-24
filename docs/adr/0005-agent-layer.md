# ADR-0005: Agent layer — Backlog.md as the single task registry, plugins, hooks, deny rules

- Status: accepted (Stage 0), with findings to confirm in a fresh session
- Date: 2026-10-24
- Evidence: `docs/evidence/stage-0/plugins-inventory.md`, `docs/evidence/stage-0/agent-tooling-facts.md`,
  `docs/evidence/stage-0/claude-code-facts.md`, this session's hook outputs quoted in
  `docs/reports/stage-0.md`.

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

## Decisions
1. **Backlog.md is the only status.** Plans and specs are working documents linked from a task
   (`backlog task edit <id> --plan`/`--ref`); their checkboxes carry no status (AGENTS.md rule 6).
   Locations are overridden in `CLAUDE.md`: `docs/plans/`, `docs/specs/` (the skill allows a user
   preference). `.superpowers/` and `.worktrees/` are git-ignored.
2. **code-modernization is used for analysis and verification only**: `/modernize-extract-rules`,
   `/modernize-review`, `/modernize-verify` (Stages 3 and 5). `MODERNIZATION_BRIEF.md`, `transform`,
   `reimagine` and `uplift` are not used: `docs/brief.md` and Backlog.md are the plan, `src/` is the
   code. `analysis/sportorg/` is committed (except `*.local.*`); `legacy/` and `modernized/` are
   git-ignored. Whether `/modernize-verify` can point at `src/` instead of `modernized/` is a Stage 5
   question; the project's own oracle CLI remains the proof.
3. **Hooks run project commands only** (`scripts/hooks/`): PreToolUse guard (deny writes into the
   legacy checkout, ask for `tests/golden/**`), PostToolUse ruff + basedpyright on the edited file, Stop
   fast tests of the touched packages. The guard runs with `uv run --no-project` so that a broken
   `.venv` cannot disable every tool — learned the hard way in this session (see report).
4. **Deny rules**: `permissions.deny` `Edit(//c/Users/ank/Prog/Orient/_other/**)` (absolute form).
   Probe in this session on a sibling directory `../_deny_probe/`: with only the relative rule
   `Edit(../_deny_probe/**)` an Edit succeeded; after adding the absolute rule the same Edit was refused
   with "File is in a directory that is denied by your permission settings". The docs list no `../`
   form. The absolute path is machine-specific: other maintainers add their own path in
   `.claude/settings.local.json` (deny lists merge across files). To be re-confirmed in a fresh session
   (Backlog task-1); the guard hook and AGENTS.md rule 1 protect regardless.
5. **Pilot of the plugins**: `evals/` holds 5–10 cases from legacy history (see `docs/evidence/stage-0/
   legacy-fix-candidates.md`); the full `claude plugin eval --ablation with-without` run needs the
   maintainer's consent and `--max-cost-usd`, and shell-granting suites need WSL2 (no sandbox backend on
   native Windows). Keep a plugin only if the with-arm beats the without-arm.
6. **Codex**: reads AGENTS.md natively (root and nested), has hooks (`.codex/hooks.json`), MCP,
   permission profiles with filesystem `deny` (beta) and a native Windows sandbox; Superpowers installs
   from the Codex plugin marketplace. Equivalents are listed in `docs/agents/environments.md`; no step of
   the work requires a specific agent.

## Revisit
After the pilot (decision 5) and after the fresh-session deny-rule test (decision 4).
