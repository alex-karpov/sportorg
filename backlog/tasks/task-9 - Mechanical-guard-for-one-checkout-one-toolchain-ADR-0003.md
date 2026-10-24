---
id: TASK-9
title: Mechanical guard for one checkout - one toolchain (ADR-0003)
status: To Do
assignee: []
created_date: '2026-10-24 15:20'
labels: []
dependencies: []
priority: low
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Stage 0 incident (a WSL process rebuilt the Windows .venv) is prevented only by discipline (ADR-0003, independent review 2026-10-24). Design a check that refuses to sync or run when the checkout is shared between a Windows and a Linux toolchain (for example a .venv built for another OS, or a Linux process on /mnt/c).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A scripted check fails with a clear message when .venv was built for another OS or the Linux toolchain runs on /mnt/c; it is wired into scripts/check.py or the hooks
- [ ] #2 Tests cover both directions (Windows venv seen from Linux, Linux venv seen from Windows)
<!-- AC:END -->
