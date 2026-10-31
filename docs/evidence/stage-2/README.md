# Stage 2 evidence (TASK-8)

Legacy pins: `pysport@b548c35`, `templates@cd95382` (`legacy.toml`). Plan and session log:
`docs/plans/stage-2-oracle.md`. Every number here comes from a script in `scripts/`; the commands are in
each directory's `commands.txt`. Files named `*.agent.md` are the judgement of the agent (Claude Code,
Opus 5.5), not script output and not reviewed by a human.

| Directory | AC of TASK-8 | Content | State |
|---|---|---|---|
| `golden-guard/` | #7 | scenario matrix of protection mechanisms, canary, facts (ADR-0008) | S1 |
| `legacy-env/` | (#1, #5, #6 prerequisite) | Python for the legacy runtime, legacy test results headless (ADR-0009) | S1 |
