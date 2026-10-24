@AGENTS.md

## Claude Code layer (optional, thin)
- Plugins enabled for this project in `.claude/settings.json`: `superpowers` (development discipline:
  brainstorming → writing-plans → TDD → verification-before-completion → code review) and
  `code-modernization` (legacy analysis, rule extraction, equivalence proof). Install once per machine:
  `claude plugin install superpowers@claude-plugins-official --scope project` (same for `code-modernization`).
- Plan and spec locations for Superpowers skills: plans in `docs/plans/`, specs in `docs/specs/`
  (this overrides the skill defaults `docs/superpowers/...`). Each plan or spec header names its
  Backlog.md task id. Checkboxes in plans are not status; close tasks with `backlog task edit <id> -s Done`.
- `code-modernization` writes to `analysis/sportorg/` (committed, except `*.local.*`) and expects a
  `legacy/sportorg` junction (git-ignored, points to the read-only checkout). Its `MODERNIZATION_BRIEF.md`
  is not used: `docs/brief.md` and Backlog.md are the plan. Its scripts need `python3` and Git Bash on
  Windows (ADR-0003).
- Hooks in `.claude/settings.json` (scripts in `scripts/hooks/`): before Edit/Write/Bash — guard
  (deny writes into legacy, ask for `tests/golden/**`); after Edit/Write — ruff and basedpyright on the
  file; on Stop — fast tests of the affected package. Hooks only run project commands.
- Deny rule `Edit(//c/Users/ank/Prog/Orient/_other/**)` blocks Edit/Write in the legacy checkout on the
  maintainer's machine; relative rules did not work in testing (ADR-0005). On another machine add your
  absolute path to `permissions.deny` in `.claude/settings.local.json` (lists merge). Reading legacy is
  allowed; the guard hook also denies shell commands that would write there.
- No OS sandbox on native Windows: autonomous runs and `claude plugin eval` suites that grant shell
  tools run under WSL2 (ADR-0003).
