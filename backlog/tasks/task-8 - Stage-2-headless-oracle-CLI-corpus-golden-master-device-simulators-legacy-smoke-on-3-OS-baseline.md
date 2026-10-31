---
id: TASK-8
title: >-
  Stage 2: headless oracle CLI, corpus, golden master, device simulators, legacy
  smoke on 3 OS, baseline
status: In Progress
assignee: []
created_date: 2026-10-24 12:06
updated_date: '2026-10-31T16:47:00Z'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
S1 (2026-10-31): plan docs/plans/stage-2-oracle.md; AC #7 implemented (scripts/golden_guard.py, check.py step golden, CI fetch-depth 0 + GOLDEN_BASE, ADR-0008, canary in tests/scripts/test_golden_probe.py), unchecked until a CI run shows it; legacy runtime .legacy-run/pysport/.venv on CPython 3.13.17 (ADR-0009 T1, 3.8.20 as second oracle lane), legacy tests headless: 282 passed, 3 failed (sandbox /tmp), 10 skipped of 295, 5 unstable teamwork tests deselected; evidence docs/evidence/stage-2/{golden-guard,legacy-env}. Open questions: plan Session log S1 (1-5). Next: S2.

S1 follow-up (2026-10-31, maintainer): oracle first line CPython 3.8.20 (.venv re-synced), 3.13.17 second lane (ADR-0009 T1); gh api cache moved to ~/.cache/sportorg-stage2/github; commit-msg hook installed. Open: ADR-0008 question (signed manifest), legacy tests outside the sandbox (maintainer runs, result to S2).

S1 follow-up 2 (2026-10-31): maintainer ran legacy tests outside the sandbox (3.8.20): test_reader sportident and sportiduino pass, huichang fails, cause unknown (finding for S5); evidence legacy-tests-outside-sandbox.*
<!-- SECTION:NOTES:END -->
