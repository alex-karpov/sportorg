---
id: TASK-2
title: >-
  Run the plugin pilot: claude plugin eval with --ablation with-without on
  evals/
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 12:12'
labels:
  - stage-0
  - claude-code
  - pilot
milestone: m-0
dependencies: []
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Full run only with the maintainer consent and a cost ceiling. Shell-granting suites need WSL2 (no sandbox backend on native Windows). Cases live in evals/legacy-fixes/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Maintainer consent and --max-cost-usd value recorded in this task
- [ ] #2 Run executed from WSL2 with --scaffold and the needed --allow-tools; aggregate-result.json and report.html stored under docs/evidence/pilot/
- [ ] #3 ADR-0005 updated: keep or drop each plugin based on the with-arm minus without-arm delta
<!-- AC:END -->
