---
id: TASK-2
title: >-
  Run the plugin pilot: claude plugin eval with --ablation with-without on
  evals/
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 17:25'
labels:
  - stage-0
  - claude-code
  - pilot
milestone: m-2
dependencies: []
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deferred to Stages 2-3 by the maintainer (2026-10-24), when project code and golden tests exist; the 7 cases in evals/legacy-fixes/ stay as they are. The decision rule is written in advance (evals/README.md, Decision rule; draft). Shell-granting suites need WSL2. The cases measure fixing legacy code, not code-modernization's rule extraction (ADR-0005 decision 5).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Decision rule in evals/README.md approved by the maintainer before the first full run (approval date recorded here)
- [ ] #2 Maintainer consent and --max-cost-usd value recorded in this task
- [ ] #3 Run executed from WSL2 with --scaffold and EVAL_LEGACY_SRC=.legacy/pysport; aggregate-result.json and report.html stored under docs/evidence/pilot/ with the plugin versions
- [ ] #4 ADR-0005 updated: each plugin classified useful, harmful or no evidence by the pre-registered rule
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Maintainer, 2026-10-25: pilot deferred to later stages; the decision rule in evals/README.md stays a draft and is approved (or amended) by the maintainer before the first run.
<!-- SECTION:NOTES:END -->
