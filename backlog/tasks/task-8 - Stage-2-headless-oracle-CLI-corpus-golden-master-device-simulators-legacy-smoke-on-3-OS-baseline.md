---
id: TASK-8
title: >-
  Stage 2: headless oracle CLI, corpus, golden master, device simulators, legacy
  smoke on 3 OS, baseline
status: To Do
assignee: []
created_date: '2026-10-24 12:06'
updated_date: '2026-10-24 15:20'
labels:
  - stage-2
milestone: m-2
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Blocked by data request items 1-4 (corpus, protocols, personal-data decision, device dumps).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 uv run python scripts/oracle.py race-file recalculates and exports normalized results from a pinned legacy clone without GUI
- [ ] #2 Anonymization script reproducible; corpus in repo only after the personal-data decision
- [ ] #3 Golden-master tests pass on the corpus; masked fields listed in the report
- [ ] #4 Recorded device dumps replay through virtual COM ports
- [ ] #5 Legacy smoke (GUI, SportIdent read, print) on Windows, Linux, macOS with logs
- [ ] #6 Baseline: branch coverage, mutation score, complexity, operator task timings, split print time
- [ ] #7 Agent-neutral protection of tests/golden/** in CI before the first golden file: a changed golden file fails CI unless the commit carries the maintainer's approval (mechanism recorded in an ADR)
<!-- AC:END -->
