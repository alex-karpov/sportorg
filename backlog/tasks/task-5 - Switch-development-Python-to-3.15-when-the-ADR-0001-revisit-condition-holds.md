---
id: TASK-5
title: Switch development Python to 3.15 when the ADR-0001 revisit condition holds
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 12:12'
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
- [ ] #1 uv run python -m scripts.python_support_matrix shows cp315 wheels for pyyaml and every direct dependency on win/linux/mac
- [ ] #2 CI 3.15 lane green for 4 consecutive weeks (link to runs)
- [ ] #3 .python-version, pyproject comment and ADR-0001 updated in one commit
<!-- AC:END -->
