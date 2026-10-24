@AGENTS.md

## Claude Code layer (optional, thin)
- Plugins: project settings enable `superpowers` (brainstorming → writing-plans → TDD →
  verification-before-completion → code review). `code-modernization` is enabled per machine in
  `.claude/settings.local.json` until the pilot (Backlog TASK-2) shows that it helps (ADR-0005).
  Install once per machine: `claude plugin install superpowers@claude-plugins-official --scope project`
  and, if wanted, `claude plugin install code-modernization@claude-plugins-official --scope local`.
- Superpowers writes plans to `docs/plans/` and specs to `docs/specs/` (overrides `docs/superpowers/…`);
  each names its Backlog.md task id.
- `code-modernization` writes `analysis/sportorg/` (committed, except `*.local.*`) and expects the
  git-ignored junction `legacy/sportorg` → `.legacy/pysport` (Windows:
  `cmd /c mklink /J legacy\sportorg .legacy\pysport`; POSIX: `ln -s ../.legacy/pysport legacy/sportorg`).
  Its `MODERNIZATION_BRIEF.md` is not used. Its scripts need `python3` and Git Bash (ADR-0003).
- Hooks (`.claude/settings.json` → `scripts/hooks/`): PreToolUse guard (writes into legacy denied,
  `tests/golden/**` asks), PostToolUse ruff + basedpyright on the edited file, Stop fast tests of the
  touched packages.
- Deny rules `Edit(/.legacy/**)` and `Edit(/legacy/**)` anchor at the directory the session starts in:
  start Claude Code at the repository root (ADR-0006). Machine-specific extra rules go to
  `.claude/settings.local.json`.
- Claude Code has no OS sandbox on native Windows: `claude plugin eval` suites that grant shell tools
  run under WSL2 (ADR-0003).
