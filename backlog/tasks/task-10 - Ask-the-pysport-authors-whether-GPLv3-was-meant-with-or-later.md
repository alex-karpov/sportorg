---
id: TASK-10
title: Ask the pysport authors whether GPLv3 was meant with 'or later'
status: To Do
assignee: []
created_date: '2026-10-24 17:24'
updated_date: '2026-10-24 20:10'
labels:
  - decision
dependencies: []
priority: low
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The project is GPL-3.0-or-later (maintainer, 2026-10-25) on the reading of the legacy About dialog, which shows the program's own filled-in notice 'either version 3 of the License, or (at your option) any later version' (pysport@b548c35 sportorg/gui/dialogs/about.py:720-726; ADR-0004, last section). The maintainer will ask the pysport authors to confirm.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Answer of the pysport authors recorded in ADR-0004 with date and link
- [ ] #2 If the authors meant version 3 only: maintainer decision recorded; pyproject.toml, README and ADR-0004 switch to GPL-3.0-only
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-25, independent round-2 check: the legacy About dialog shows the program's own filled-in GPL notice with 'or (at your option) any later version' (pysport@b548c35 sportorg/gui/dialogs/about.py:720-726), and sfrreader.py, sportiduino.py, srpid.py carry the clause besides huichang.py. ADR-0004 data corrected; the maintainer may decide on this before the authors answer.

2026-10-25: maintainer switched the project to GPL-3.0-or-later on the corrected data; this task now only confirms it with the authors.
<!-- SECTION:NOTES:END -->
