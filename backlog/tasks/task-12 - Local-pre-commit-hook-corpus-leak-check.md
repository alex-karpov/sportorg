---
id: TASK-12
title: 'Local pre-commit hook: corpus leak check'
status: To Do
assignee: []
created_date: '2026-11-01T10:08:00Z'
updated_date: '2026-11-01T10:56:00Z'
labels:
  - stage-2
milestone: m-2
dependencies: []
priority: medium
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stage 2 S3, question 5 of docs/evidence/stage-2/corpus/findings.agent.md, decided by the maintainer on 2026-11-01: run scripts.corpus.leakcheck scan (the command of docs/evidence/stage-2/corpus/commands.txt) as a local pre-commit hook. It needs the corpus and the key, so it is not a step of check.py and not in CI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A pre-commit hook runs the leak check over the stage evidence, the staged files and the commit message when SPORTORG_CORPUS is set
- [ ] #2 Without SPORTORG_CORPUS the hook says that the check was skipped, and does not fail silently or pass silently
- [ ] #3 The hook prints counts, categories, file names and line numbers only, never a found value
- [ ] #4 Tests on a temporary repository with a synthetic corpus: a staged file holding a corpus surname is refused, a clean one passes
- [ ] #5 The hook also refuses staged lines inside code blocks of Markdown/text files that look like quoted code with a name-like string literal (the heuristic of S3, 2026-11-01), so that legacy's test code is not quoted (AGENTS.md rule 8)
<!-- AC:END -->
