# Stage 1 evidence (TASK-7)

Legacy pins: `pysport@b548c35`, `templates@cd95382` (`legacy.toml`). Plan: `docs/plans/stage-1-archaeology.md`.
Every number here comes from a script in `scripts/archaeology/`. The commands are in each directory's
`commands.txt`. Files named `*.agent.md` are the judgement of the main session's agent (Claude Code, Opus 5.5), not
script output and not reviewed by a human; their criteria are at the top.

| Directory | Criterion of TASK-7 | Content | State |
|---|---|---|---|
| `tools/` | (rule «Как выбирать инструменты») | tool candidates and measurements behind ADR-0007 | done (Phase B) |
| `hypotheses/` | #6 | verdicts on the six hypotheses of the brief | done (Phase B) |
| `inventory/` | #1 | menu actions, report templates, import/export formats | done (W1, Phase D) |
| `structure/` | #2 | hotspots, import graph, layer violations, dead code | done (W2, Phase D) |
| `dependencies/` | #2 | dependencies, licences, vulnerabilities (Python and Rust) | done (W3, Phase D) |
| `defects/` | #3 | fix commits by module and error class; issues/PRs | done (W4, Phase D) |
| `formats/` | #4 | readers/writers of files and devices with hard-coded values | done (W5, Phase D) |
| `os-ru/` | #5 | OS-specific code and Russian specifics, classified by the agent | done (W6, Phase D) |

Agent judgement files:
- `structure/dead-code-sample-check.agent.md`: sample check of 30 vulture findings; status of `WdbOnlineSenderDialog`.
- `defects/sample-check-1.agent.md`: sample check of 50 commits against the first classifier (superseded).
- `defects/sample-check-2.agent.md`: sample check of 50 other commits against the classifier changed on 2026-10-25.
- `os-ru/classification.agent.md`: classification of all 603 OS hits and 83 core hits (not a sample).
- `dependencies/licence-sources.agent.md`: licences of `sportident`, PySide6 and `Unicode-3.0` from primary sources.

Report: `docs/reports/stage-1.md`. Independent check: `docs/reports/stage-1-verification-prompt.md`.
Canaries point the scripts at `.legacy-run/` through `ARCHAEOLOGY_LEGACY_BASE`
(`scripts/archaeology/common.py: repo_root`).
