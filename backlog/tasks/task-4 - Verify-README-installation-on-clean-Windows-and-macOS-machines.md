---
id: TASK-4
title: Verify README installation on clean Windows and macOS machines
status: To Do
assignee: []
created_date: 2026-10-24 12:05
updated_date: '2026-11-01T11:54:00Z'
labels:
  - stage-0
  - ci
milestone: m-0
dependencies: []
documentation:
  - docs/assignments/task-4-clean-install.md
priority: medium
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The CI clean-install job covers Ubuntu in a container; Windows and macOS matrix jobs start from runner images with git and curl preinstalled.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A log of the README steps executed on a machine or VM without uv, Python or the repo, for Windows and for macOS, stored in docs/evidence/stage-0/ as clean-install-windows.txt and clean-install-macos.txt
- [ ] #2 Any extra prerequisite discovered is added to README
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-01: assignment for volunteers written (docs/assignments/task-4-clean-install.md, Russian): clean VM or Windows Sandbox, session logs via Start-Transcript / script, the logs come back to the maintainer and go to docs/evidence/stage-0/.
<!-- SECTION:NOTES:END -->
