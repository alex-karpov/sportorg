---
id: TASK-1
title: 'Legacy as pinned, locked clones in .legacy/ (ADR-0006)'
status: In Progress
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 17:25'
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
Maintainer decision 7 (2026-10-24): legacy is a git-ignored clone inside the repository at a pinned SHA, without write bits, portable deny rule Edit(/.legacy/**), guard on resolved paths, probed on Windows and in WSL first. Maintainer decision of 2026-10-25: two public repositories, sportorg/pysport@b548c35 (code) and alex-karpov/sportorg-templates@cd95382 (Russian templates). Done on Windows: legacy.toml + scripts/legacy.py (fetch, including pin updates; verify; lock), both clones locked (deny ACE on Windows), rules Edit(/.legacy/**) and Edit(/legacy/**), guard rewritten with tests. Open: verify in a WSL2 ext4 clone and the agent probe in WSL2 (Claude Code not installed there). Evidence: docs/evidence/stage-0/legacy-layout/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No absolute path in committed .claude/settings.json; guard tests cover compound commands, PowerShell, junctions, cd into legacy and main() failure modes (tests/scripts/test_guard.py green)
- [ ] #2 uv run python -m scripts.legacy verify prints ok on Windows and in a WSL2 ext4 clone (outputs attached here)
- [ ] #3 scripts/probe_legacy_protection.py agent run in WSL2: Edit, Write and Bash writes into .legacy refused; output added to docs/evidence/stage-0/legacy-layout/
- [x] #4 Pinned commit fetchable from the URL in legacy.toml without --source (maintainer chose option A or B; ADR-0006 updated)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-25, Windows: 'uv run python -m scripts.legacy fetch' replaced pysport 30d849d with b548c35 and cloned templates from GitHub without --source (6.9 s); 'verify' -> 'ok: pysport@b548c35ba18f, templates@cd953823beb3 locked', exit 0.
<!-- SECTION:NOTES:END -->
