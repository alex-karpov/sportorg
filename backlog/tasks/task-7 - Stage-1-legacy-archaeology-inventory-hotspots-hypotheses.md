---
id: TASK-7
title: 'Stage 1: legacy archaeology - inventory, hotspots, hypotheses'
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 12:12'
labels:
  - stage-1
milestone: m-1
dependencies: []
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per docs/brief.md, Stage 1. Read-only analysis of the legacy checkout at commit 30d849dd.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function inventory (code, menus, templates, docs) mapped to modules
- [ ] #2 Hotspots (change frequency x complexity), import graph, layer violations, dead code, dependency/licence/vulnerability lists produced by scripts in scripts/ with outputs in docs/evidence/stage-1/
- [ ] #3 Defect history by module and error class
- [ ] #4 All data formats and device protocols: readers, writers, hardcoded values
- [ ] #5 OS-specific code and Russian specifics in the core listed
- [ ] #6 Each hypothesis from the brief (memory.py 2910 lines and most changed; race() in 62 files; GUI imported outside gui; punch system in result classes; Qualification in domain; Win7 pins) confirmed or refuted with numbers
<!-- AC:END -->
