---
id: TASK-10
title: Ask the pysport authors whether GPLv3 was meant with 'or later'
status: To Do
assignee: []
created_date: 2026-10-24 17:24
updated_date: '2026-11-01T16:29:00Z'
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
- [ ] #3 Question to the sportorg/sireader maintainer recorded: why commit d209fef removed the copyright notices of Gaudenz Steinlin and Simon Harston from the code published as sportident, and whether they can be restored; the answer goes to ADR-0004 (licence exceptions)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-25, independent round-2 check: the legacy About dialog shows the program's own filled-in GPL notice with 'or (at your option) any later version' (pysport@b548c35 sportorg/gui/dialogs/about.py:720-726), and sfrreader.py, sportiduino.py, srpid.py carry the clause besides huichang.py. ADR-0004 data corrected; the maintainer may decide on this before the authors answer.

2026-10-25: maintainer switched the project to GPL-3.0-or-later on the corrected data; this task now only confirms it with the authors.

2026-10-25, Stage 1 report question 4 [мейнтейнер: 2026-10-25]: added the sireader attribution question (sportorg/sireader is a fork of gaudenz/sireader; d209fef removed both copyright lines; evidence docs/evidence/stage-1/dependencies/licence-sources.agent.md). The new project keeps the attribution if it uses that code.

2026-11-01 [мейнтейнер: 2026-11-01]: answer of a pysport author, who also maintains sportorg/sireader, of 2026-10-25 (private correspondence, no public link) recorded in ADR-0004, both sections, in paraphrase (no verbatim quotes of private correspondence, maintainer 2026-11-01). Licence: GPL was chosen because of Qt; he prefers MIT if the dependencies allow it; the About dialog was not asked about, so 'or later' is still unconfirmed and AC #1 stays open. sireader: the code has been practically rewritten, so only a thank-you to the original authors remains (paraphrase); this explains d209fef but does not say whether the notices can be restored; the claim was not compared with gaudenz/sireader. AC #3 is left for the maintainer to close or to ask again.

2026-11-01: PySide6 restrictions checked from primary sources (docs/evidence/licences/pyside6.agent.md): Qt modules legacy uses are LGPLv3; GPL-only Qt modules, LGPL duties of a frozen build and wheel platform limits listed; proposals for the Stage 4 dependency ADR, not decided.

2026-11-01, legacy licence history (corrects a wrong note of the same day): LICENSE was MIT from 2017-10-18 [история: pysport 17a12ca]. Commit f74877e "Changed license" (2018-07-25) replaced it with the full GPLv3 text and pasted the same text into about.py under the label "GPL v3 License". The three "any later version" lines are the GPLv3 text itself: twice in section 14 and once in the unfilled sample notice of "How to Apply These Terms" (placeholders <one line to give the program's name…>, <year>, <name of author>) [история: pysport f74877e]. Commit eaa4843 "To PySide2" (2018-11-09) filled the placeholders with "SportOrg / Copyright (C) 2018  SportOrg team" in both files [история: pysport eaa4843]; 9d8cfb2 (2020-07-16) changed one year in LICENSE. At b548c35 the About text equals LICENSE except that year. No own source file of legacy carries the notice; only the four vendored libraries do. So the "or later" basis of ADR-0004 is a filled-in sample inside the licence document, not a notice attached to the program. 17 distinct author e-mails since 2018-07-25; CONTRIBUTING.md has no CLA/DCO or licence clause. The MIT-notice side finding is withdrawn: the GPL header of f74877e kept the same holder name.

2026-11-01 [мейнтейнер: 2026-11-01]: GPL-3.0-or-later stays until the authors answer, although the licence history reads closer to version 3 only (ADR-0004, "Precision of the correction"). Names of the authors are not written into the repository (Stage 1 plan: no names of commit authors in evidence; Stage 2 prompt rule 4: no real full name in the repository).
<!-- SECTION:NOTES:END -->
