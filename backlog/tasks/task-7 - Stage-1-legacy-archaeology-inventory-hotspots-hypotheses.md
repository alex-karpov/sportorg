---
id: TASK-7
title: 'Stage 1: legacy archaeology - inventory, hotspots, hypotheses'
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 17:24'
labels:
  - stage-1
milestone: m-1
dependencies: []
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per docs/brief.md, Stage 1. Read-only analysis of the pinned legacy clones (legacy.toml, ADR-0006): .legacy/pysport at sportorg/pysport b548c35 (code) and .legacy/templates at alex-karpov/sportorg-templates cd95382 (Russian report templates).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function inventory: every legacy menu action, report template and import/export format listed with module and file:line in docs/evidence/stage-1/, produced or cross-checked by a script in scripts/
- [ ] #2 Hotspots (change frequency x complexity), import graph, layer violations, dead code, dependency/licence/vulnerability lists produced by scripts in scripts/ with outputs in docs/evidence/stage-1/
- [ ] #3 Defect history: fix commits classified by module and error class by a script; the counts table in docs/evidence/stage-1/ is reproducible from that script
- [ ] #4 Data formats and device protocols: every reader and writer listed with file:line and its hard-coded values (table in docs/evidence/stage-1/, each row with a [код] tag)
- [ ] #5 OS-specific code and Russian specifics in the core: a script lists the file:line hits; the manual classification of each hit is attached
- [ ] #6 Each hypothesis from the brief (memory.py 2910 lines and most changed; race() in 62 files; GUI imported outside gui; punch system in result classes; Qualification in domain; Win7 pins) confirmed or refuted with numbers
<!-- AC:END -->
