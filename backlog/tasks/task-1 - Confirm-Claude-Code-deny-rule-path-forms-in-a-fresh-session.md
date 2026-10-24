---
id: TASK-1
title: Confirm Claude Code deny-rule path forms in a fresh session
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 12:12'
labels:
  - stage-0
  - claude-code
milestone: m-0
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the Stage 0 session a relative rule Edit(../_deny_probe/**) did not block an Edit, while the absolute form Edit(//c/.../_deny_probe/**) did (message: File is in a directory that is denied by your permission settings). Repeat in a fresh session. See ADR-0005 decision 4.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fresh Claude Code session: Edit of a file under the legacy checkout is refused by the permission rule itself (not by the guard hook)
- [ ] #2 Relative and absolute forms both tested; result recorded in ADR-0005 with the tool output
- [ ] #3 CLAUDE.md tells other maintainers how to add their absolute path in settings.local.json
<!-- AC:END -->
