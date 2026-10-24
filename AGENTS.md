# AGENTS.md — sportorg_ng

Single source of instructions for every contributor, human or agent, in any environment.
Agent-specific layers (`CLAUDE.md`, `.codex/`) only point here and add what that tool needs.

## What this is
Modernization of SportOrg (orienteering timing/results). The legacy program is the behavioural
**oracle**: new code must reproduce its results, or deviate only with a documented, maintainer-approved
reason. Full brief: `docs/brief.md` (Russian). Stage reports: `docs/reports/`.

## Layout
- `src/sportorg_ng/` — product code; layer rules in `src/sportorg_ng/AGENTS.md`
- `tests/` — pytest; golden files under `tests/golden/` are protected (see Rules)
- `scripts/` — project commands and measurements; `scripts/check.py` runs every quality check
- `backlog/` — Backlog.md tasks (the only task registry)
- `docs/adr/` decisions · `docs/sources/` primary sources · `docs/evidence/` tool outputs · `docs/risks.md`
- `.legacy/<name>` — legacy repositories, **read-only**, git-ignored clones at the commits pinned in
  `legacy.toml` (ADR-0006): `pysport` (the program) and `templates` (Russian report templates; legacy
  reads them with `SPORTORG_TEMPLATES_PATH=<.legacy/templates>/ru`); `.legacy-run/<name>` — writable
  copies for running legacy

## Commands (same on Windows, Linux, macOS)
```
uv sync                                  # environment, Python 3.14 (ADR-0001)
uv run python scripts/check.py           # ALL checks: format, lint, types, imports, tests (fail-fast)
uv run python scripts/check.py --fix     # apply ruff format + autofixes, then run checks
uv run python scripts/check.py --only tests
uvx --python 3.14 pre-commit@4.7.0 install  # git hooks: fast checks on commit, tests on push
uv audit                                 # vulnerabilities (also in CI)
uv run python -m scripts.check_licenses  # licence compatibility of runtime dependencies (also in CI)
uv run python -m scripts.legacy fetch    # clone or update the pinned legacy repositories in .legacy/, locked
uv run python -m scripts.legacy verify   # pinned commit, clean tree, still locked
uv run python -m scripts.legacy_clone    # writable copy in .legacy-run/ for running legacy
```
Scripts that import `scripts.*` run as modules (`python -m scripts.x`), not as files.
Only `scripts/check.py` defines what "green" means; pre-commit, CI and agent hooks call the same steps.

Environment (ADR-0003): on a Windows host, agent-driven work runs in WSL2 with the repository cloned on
ext4 (not under `/mnt/c`; setup with VS Code: `docs/windows-wsl-vscode.md`); a native Windows clone is a separate checkout for GUI/printing tests. Never
open one checkout from both toolchains — the `.venv` breaks. `.devcontainer/` is the reproducible
equivalent (Docker) for unattended agents and for hosts without WSL.

## Rules
1. **Legacy is read-only.** Never write under `.legacy/` (or the maintainer's sibling checkout it is
   fetched from). Run legacy code only from a copy made by `scripts.legacy_clone`, never in `.legacy/`.
   Never unlock `.legacy/`. Pins in `legacy.toml` change only by the maintainer's decision; then
   `scripts.legacy fetch` replaces the old clone.
2. **Evidence.** A claim about rules, formats or behaviour carries a source tag:
   `[код: path:line]`, `[правила: doc, edition, clause]`, `[корпус: file]`, `[история: commit/issue]`,
   `[мейнтейнер: date]`; otherwise `[допущение]`. Sport rules are never quoted from memory.
3. **Done = tool output.** "Tests pass" means the command was run now and its output is attached.
   Stage verification is repeated in a fresh session.
4. **No silencing.** No `Any`, `cast`, `# type: ignore`, `# noqa` or skipped tests without an error code
   and a one-line reason; unused suppressions fail the build. Do not lower thresholds to pass.
5. **Golden files** (`tests/golden/**`) change only with the maintainer's explicit confirmation.
6. **Tasks live in Backlog.md** (`backlog task create|edit|list`, files in `backlog/tasks/`).
   Plans and specs written by agent skills are working documents linked from a task; their
   checkboxes are not status. Status changes only in Backlog.md.
7. **Decisions are ADRs** in `docs/adr/` (options, data, decision, revisit condition). "Like legacy"
   and "by default" are not arguments. New dependency = first use + ADR line.
8. **Personal data** of participants never enters the repository (see `docs/data-request.md`).
9. **Discrepancies** between code, rules and protocols are not fixed silently: classify
   (legacy bug / local practice / rule gap) and raise to the maintainer.
10. Code, comments, commits (Conventional Commits), ADRs and tasks are in English. Documents addressed
    to the maintainer (`docs/brief.md`, `docs/reports/`, `docs/data-request.md`) are in Russian.

## Agent environments
- Claude Code: `CLAUDE.md` (plugins, hooks, deny rules). Codex and others: `docs/agents/environments.md`.
- Nothing in this project requires a specific agent: every check and proof is a plain command.

<!-- BACKLOG.MD MANAGED BLOCK START -->
Backlog.md: run `backlog instructions` for the CLI workflow (`backlog task create "title" --ac "..."`,
`backlog task edit <id> -s "In Progress"`, `backlog task list --plain`). Change tasks through the CLI.
<!-- BACKLOG.MD MANAGED BLOCK END -->
