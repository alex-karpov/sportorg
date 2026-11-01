---
id: TASK-8
title: >-
  Stage 2: headless oracle CLI, corpus, golden master, device simulators, legacy
  smoke on 3 OS, baseline
status: In Progress
assignee: []
created_date: 2026-10-24 12:06
updated_date: '2026-11-01T12:04:00Z'
labels:
  - stage-2
milestone: m-2
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Blocked by data request items 1-4 (corpus, protocols, personal-data decision, device dumps).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 uv run python scripts/oracle.py race-file recalculates and exports normalized results from a pinned legacy clone without GUI
- [ ] #2 Anonymization script reproducible; corpus in repo only after the personal-data decision
- [ ] #3 Golden-master tests pass on the corpus; masked fields listed in the report
- [ ] #4 Recorded device dumps replay through virtual COM ports
- [ ] #5 Legacy smoke (GUI, SportIdent read, print) on Windows, Linux, macOS with logs
- [ ] #6 Baseline: branch coverage, mutation score, complexity, operator task timings, split print time
- [x] #7 Agent-neutral protection of tests/golden/** in CI before the first golden file: a changed golden file fails CI unless the commit carries the maintainer's approval (mechanism recorded in an ADR)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
S1 (2026-10-31): plan docs/plans/stage-2-oracle.md; AC #7 implemented (scripts/golden_guard.py, check.py step golden, CI fetch-depth 0 + GOLDEN_BASE, ADR-0008, canary in tests/scripts/test_golden_probe.py), unchecked until a CI run shows it; legacy runtime .legacy-run/pysport/.venv on CPython 3.13.17 (ADR-0009 T1, 3.8.20 as second oracle lane), legacy tests headless: 282 passed, 3 failed (sandbox /tmp), 10 skipped of 295, 5 unstable teamwork tests deselected; evidence docs/evidence/stage-2/{golden-guard,legacy-env}. Open questions: plan Session log S1 (1-5). Next: S2.

S1 follow-up (2026-10-31, maintainer): oracle first line CPython 3.8.20 (.venv re-synced), 3.13.17 second lane (ADR-0009 T1); gh api cache moved to ~/.cache/sportorg-stage2/github; commit-msg hook installed. Open: ADR-0008 question (signed manifest), legacy tests outside the sandbox (maintainer runs, result to S2).

S1 follow-up 2 (2026-10-31): maintainer ran legacy tests outside the sandbox (3.8.20): test_reader sportident and sportiduino pass, huichang fails, cause unknown (finding for S5); evidence legacy-tests-outside-sandbox.*

S1 follow-up 3 (2026-11-01): AC #7 checked: CI run 41222366113 (stage-2@dab1040) green on all 7 jobs, golden step ok on Linux/Windows/macOS 3.14+3.15 and the clean machine, 329 tests incl. the canary. Signed manifest (c2) deferred to a later stage by the maintainer (ADR-0008). Pre-push hook protected-files added (condition 3, informational).

S2 (2026-11-01): oracle seam for AC #1: uv run python scripts/oracle.py RACE_FILE [--out DIR] (driver under .legacy-run/pysport/.venv 3.8.20, second lane .venv-3.13 3.13.17; whitelisted snapshot, schema v1, stored-vs-recalculated comparison). Evidence docs/evidence/stage-2/oracle: lanes and reruns byte-identical, canary fired, legacy test.json counts only (1 stored value differs, F1). ADR-0009 T3-T5 proposed, risk R22. check.py green, 432 tests. AC #1 unchecked until verification in a fresh session. Open questions: plan Session log S2 (1-5). Next: S3.

After S2 (2026-11-01): Fable reviews of S1 and S2 (exception to stage rule 10): with fixes, 0 critical, 3 important (commit-msg hook on a clean merge; crash path of legacy test runs untested; stored null counted as not_stored); fix pass awaits the maintainer. Maintainer: ADR-0009 T3-T5 accepted; F1 representation; F2 legacy bug (three ways to show out-of-competition runners); R22 formula files listed in the S3 manifest, run only with consent. F3/F4/F6 check files and guide docs/reports/stage-2-check-f3-f4-f6.md. Open: plan Session log 'After S2'.

Fix pass (2026-11-01): review findings fixed by TDD (S1: commit-msg on merges, replace refs, env families, sync limit, crash-path test, CI GOLDEN_BASE; S2: schema v2 stored nulls, cp1251 files per Q3 (b) = ADR-0009 T6, default clock 23:59:59 = T5, --state after-open, OracleError on timeout/missing interpreter, main --out test). F3/F4/F6 confirmed in the GUI by the maintainer (b548c35, Python 3.13.5); classification of F3/F4 and the F6 state open. AC #1 checked per Q5 (b): after the fix pass, oracle evidence rerun identical, the AC command run (exit 0, stdout = committed results.json); also reproduced by the Fable review in a separate context. check.py green, 471 tests. Deferred: S1-9, S1-12 (S3). Plan Session log 'Fix pass'.

Maintainer 2026-11-01: F3, F4, F6 are legacy bugs; for F6 the oracle reproduces each race in its own context (--state recalculated); S4 also runs corpus files with several races in --state after-open and counts where the states differ (plan S4).

S3 (2026-11-01): anonymization and corpus manifest for AC #2: scripts/corpus/{pseudonym,anonymize,racefile,leakcheck,catalog,invariant,evidence}.py by TDD (165 tests). Synthetic: rebuild byte-identical, locality (edit/add file, one record) holds, 0 leaks, invariant 6/6 (formula file not run, R22). Corpus as on disk: 25 dirs, 63 race files (28 gzip/29 utf-8/6 cp1251), 100 races, 24 distinct starts; no ARDF, no formula files; passport only id; copies 0 leaks; invariant 62/62 identical, 1 file legacy cannot open either way (F8). Findings F7 (legacy opens gzip r+b, read-only originals), F8; ADR-0009 T7 proposed. Evidence docs/evidence/stage-2/corpus. AC #2 unchecked: verdict synthetic full, corpus as of the run with limits; questions 1-6 in corpus/findings.agent.md. Next: S4.

S3 follow-up (2026-11-01, maintainer): answers 1, 2, 4 as built (ADR-0009 T7 decided); 5 -> TASK-12; 3: code-only study of legacy's logs (corpus/logs.agent.md, Sonnet sub-agent), decided C1 in S5 (frame-only dump, mapped cards, owner bytes overwritten, CRC recomputed); F7 legacy bug (Windows: read-only gzip does not open, read-only plain file does not save, leaves .json.tmp); F8 confirmed in GUI, narrowed by new manifest counters to an empty part of a list template parsed by int() since 0f3a0a8 (proposal: legacy bug, regression); 6: matched words written outside the repo (leakcheck --words-out), decision pending.

S3 follow-up 2 (2026-11-01): F8 classified legacy bug. Question 6: the maintainer found personal data (a name and a club) in docs/evidence/stage-0/legacy-fix-candidates.md, a quoted legacy test diff; all 11 test-diff blocks of that file removed from the tree, replaced by the git show command; they stay in main's history (eb40eef), rewrite is the maintainer's decision. Fable review of S3 (exception to stage rule 10 by the maintainer's word) running.

S3 review fix pass (2026-11-01): Fable review of S3 (1 critical, 4 important, 9 minor) fixed by TDD per the maintainer's decisions: C1 (в) status comments that are rule clauses kept, other text masked also in legacy's derived result strings; I1 BOM/NBSP files scanned; I2 card and birth-date shapes; I3 contacts, codes, places scanned, short cards only as card field values, card types counted (middle names not searched, as given names); I4 unpushed branch rewritten (filter-branch); M1-M4, M6-M8; M5, M9 in README Limits. Legacy status titles count as kept text (turned the one new corpus leak into a residual). Synthetic and corpus evidence rebuilt twice, byte-identical: corpus 0 leaks, 29 residual, invariant 62/62; check.py green. Table in corpus/findings.agent.md; plan Session log 'S3 review and fix pass'. AC #2 unchanged. Next: S4.
<!-- SECTION:NOTES:END -->
