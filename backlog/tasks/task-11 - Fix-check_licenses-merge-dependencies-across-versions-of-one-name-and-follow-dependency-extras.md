---
id: TASK-11
title: >-
  Fix check_licenses: merge dependencies across versions of one name and follow
  dependency extras
status: To Do
assignee: []
created_date: '2026-10-25T07:47:00Z'
labels:
  - tooling
dependencies: []
priority: medium
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found in Stage 1 (report question 6, [мейнтейнер: 2026-10-25]). scripts/check_licenses.py lock_graph keeps the dependency list of only the last version of each package name, and it ignores optional-dependencies / extra entries of dependencies although its docstring says 'all groups'. Both errors drop packages from the runtime set (false negative, never a false alarm): on the legacy lock the runtime set did not change (41 = 41), the project has no runtime dependencies yet.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Failing tests first: a package name in two versions with different dependency lists; a dependency reached through an extra
- [ ] #2 lock_graph merges the dependencies of all versions of a name and follows extras; tests pass
- [ ] #3 Done before the first runtime dependency is added to the project; ADR-0004 row 7 updated if the behaviour description changes
<!-- AC:END -->
