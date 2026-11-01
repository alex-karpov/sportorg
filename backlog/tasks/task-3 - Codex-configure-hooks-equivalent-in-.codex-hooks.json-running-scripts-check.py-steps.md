---
id: TASK-3
title: >-
  Codex: configure hooks equivalent in .codex/hooks.json running
  scripts/check.py steps
status: To Do
assignee: []
created_date: 2026-10-24 12:05
updated_date: '2026-11-01T11:54:00Z'
labels:
  - stage-0
  - codex
milestone: m-0
dependencies: []
documentation:
  - docs/assignments/task-3-codex-hooks.md
priority: medium
ordinal: 3000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PostToolUse hook in .codex/hooks.json runs the same file-level steps as scripts/hooks/post_edit.py
- [ ] #2 A Codex user confirms the hook fires on apply_patch; output pasted into docs/agents/environments.md
- [ ] #3 No rule exists only in the Codex hook (AGENTS.md stays the source)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-01: assignment for a Codex user written (docs/assignments/task-3-codex-hooks.md, Russian). Part A records the real hook payloads of apply_patch, because the Codex docs say only that apply_patch puts its input in tool_input.command (learn.chatgpt.com/docs/hooks, read 2026-11-01), while scripts/hooks/post_edit.py reads tool_input.file_path. AC #1 is implemented on those payloads; part B is the confirmation for AC #2.
<!-- SECTION:NOTES:END -->
