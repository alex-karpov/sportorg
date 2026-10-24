---
id: TASK-6
title: Maintainer decisions pending from Stage 0
status: To Do
assignee: []
created_date: '2026-10-24 12:05'
updated_date: '2026-10-24 20:10'
labels:
  - stage-0
  - decision
milestone: m-0
dependencies: []
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
See docs/reports/stage-0.md (questions section) and docs/data-request.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Project licence chosen; pyproject.toml, LICENSE, README and ADR-0004 updated
- [x] #2 Personal-data rule for the corpus decided and written into docs/data-request.md
- [ ] #3 Data request items 1-13 have a status other than nothing-received, or an explicit replacement
- [x] #4 Decisions 2-7 recorded in the ADRs, settings and docs named in the notes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Maintainer decisions of 2026-10-24: (1) licence GPL-3.0-or-later after confirming the legacy licence from the primary source - finding: legacy declares GPLv3 without 'or later' (ADR-0004, last section), question raised; (2) corpus outside the repository, variant (a) - written into docs/data-request.md; (3) merge stage-0 into main after the Stage 0 work is finished; (4) plugin pilot deferred to Stages 2-3, criterion written in advance (evals/README.md), 7 cases unchanged; (5) Python 3.14 confirmed (ADR-0001); (6) code-modernization enabled locally until the pilot (.claude/settings.local.json); (7) legacy as a git-ignored pinned clone with a portable deny rule (ADR-0006, TASK-1).

Maintainer answers of 2026-10-25: (1) GPL-3.0-only (LICENSE, pyproject, README, ADR-0004); the maintainer will ask the pysport authors (TASK-10). (2) Two legacy repositories: sportorg/pysport@b548c35 and alex-karpov/sportorg-templates@cd95382, the templates of 30d849d without .docx except one cleaned diploma (ADR-0006, legacy.toml). (3) Username in public history accepted; evidence files now say USER instead of it, with a note in docs/evidence/stage-0/README.md. (4) Environment: answered in docs/reports/stage-0.md (addendum of 2026-10-25). (5) Pilot stays deferred; its decision rule is approved before the pilot starts (TASK-2 AC #1). (6) Commit and push to stage-0.

Maintainer answers of 2026-10-25, third round: (1) licence GPL-3.0-or-later on the corrected legacy data (About dialog grants 'or later'); pyproject.toml, README, ADR-0004, data-request item 13 follow it; TASK-10 now only confirms it with the pysport authors. (2) Stage 0 closed with TASK-3 and TASK-4 open (no macOS machine, no Codex); milestone m-0 archived, its open tasks keep m-0. (3) Backlog.md CLI in WSL: Node.js from apt plus backlog.md in ~/.local, added to docs/windows-wsl-vscode.md; confirmed by the maintainer's WSL session and in a clean ubuntu:26.04 container.
<!-- SECTION:NOTES:END -->
