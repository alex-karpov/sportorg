---
id: TASK-5
title: Switch development Python to 3.15 when the ADR-0001 revisit condition holds
status: To Do
assignee: []
created_date: 2026-10-24 12:05
updated_date: '2026-10-31T14:28:00Z'
labels:
  - stage-0
  - python
milestone: m-0
dependencies: []
priority: low
ordinal: 5000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every package in uv.lock installs from wheels on 3.15 on win/linux/mac: the CI 3.15 lanes (uv sync --locked --no-build) are green, and pyyaml (pre-commit) ships cp315 wheels
- [ ] #2 CI 3.15 lane green for 4 consecutive weeks (link to runs)
- [ ] #3 .python-version, pyproject comment and ADR-0001 updated in one commit
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-31 re-check (PyPI): of 18 uv.lock packages only grimp 3.17 lacked cp315 on macOS (3.18 has win/linux/mac; lock updated). Remaining blocker for AC #1: pyyaml 6.0.3 (pre-commit) has wheels only up to cp314. AC #2 clock has not started.
<!-- SECTION:NOTES:END -->
