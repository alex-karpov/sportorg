# Defect classifier: sample check 1 of 50 commits (agent judgement)

The labels in this file are the judgement of the main session's agent (Claude Code, Opus 5.5) on 2026-10-25, not script output; no human reviewed them. **Classifier of commit 75474c0, before the maintainer's change of 2026-10-25 (question 5 of the report); the current classifier is checked in `sample-check-2.agent.md`. The "predicted" columns here no longer match `commits.json`.** The sample itself was
chosen by a script: 25 commits predicted as fixes and 25 predicted as non-fixes, non-merge only.

```
uv run python -m scripts.archaeology.sample --json docs/evidence/stage-1/defects/commits.json \
    --n 50 --seed 20261025 --where is_merge=false --stratify is_fix \
    --fields sha,type,is_fix,product_defect,class,modules
```

## Criteria
For each commit the agent read the subject, the changed files and, when the subject did not say enough, the diff
(`git -C .legacy/pysport show <sha>`). Issue #276 was read from the cache. The texts themselves are not
copied here (Stage 1 rule 4); the "why" column paraphrases them.
- **fix**: the commit corrects behaviour that was wrong: a crash, a wrong result, a broken function,
  data loss, an unusable performance problem, a broken build, or wrong docs. A new feature, a refactoring,
  typing/debug aids, a performance tweak without a reported defect and a work-in-progress commit are not fixes.
- **class**: one of the 12 classes of the plan (plus `docs-only`), chosen from what the change does,
  not from which files it touches. `unknown` is not used: every commit could be read.

## Sample
| # | commit | predicted fix | predicted class | fix (agent) | class (agent) | why |
|---|---|---|---|---|---|---|
| 1 | [история: pysport@57ac99d] | yes | other | yes | calc | overtime check for multi-day races used the wrong day |
| 2 | [история: pysport@2048303] | yes | other | yes | ui | deleting table rows removed wrong records (row index instead of id) |
| 3 | [история: pysport@2988024] | yes | ui | yes | ui | group mass-edit dialog failed with no participants |
| 4 | [история: pysport@68f882a] | yes | calc | yes | calc | result indexing in multi-day races |
| 5 | [история: pysport@3ad85a9] | yes | report-print | yes | report-print | split printout crashed without group or course |
| 6 | [история: pysport@7d885f0] | no | report-print | no | — | new template feature (gzip) |
| 7 | [история: pysport@7b3b20c] | yes | ui | yes | ui | combo box behaviour in dialogs |
| 8 | [история: pysport@00885a2] | yes | persistence | yes | persistence | saving could wipe a corrupted file |
| 9 | [история: pysport@98f5e47] | yes | ui | yes | ui | GUI unusably slow with many participants |
| 10 | [история: pysport@fd98887] | no | device | no | — | `perf:` faster COM-port search, no defect named |
| 11 | [история: pysport@314ae59] | yes | calc | **no** | — | `fix:` type, but the change only adds typing and `repr` for debugging |
| 12 | [история: pysport@4ab5f11] | no | calc | no | — | new feature (penalty loops) |
| 13 | [история: pysport@12ea8fb] | yes | platform-build | yes | platform-build | build script repaired |
| 14 | [история: pysport@5a77f6a] | no | start-draw | no | — | `refactor:` docstrings |
| 15 | [история: pysport@7d15982] | yes | ui | yes | ui | duplicated menu entry after a bad merge |
| 16 | [история: pysport@f48a4d2] | no | device | **yes** | device | empty card readouts are now ignored. The subject describes the faulty behaviour without a fix word |
| 17 | [история: pysport@72cf448] | no | online | no | — | new toolbar and online sending |
| 18 | [история: pysport@854f7e7] | yes | online | yes | online | telegram client repaired |
| 19 | [история: pysport@c811833] | yes | calc | yes | calc | wrong type of the result status |
| 20 | [история: pysport@af08823] | yes | other | yes | import-export | organization contact in IOF XML export and live template |
| 21 | [история: pysport@315bc94] | no | import-export | no | — | importer improvement |
| 22 | [история: pysport@cf30498] | yes | other | yes | calc | result comparison compared an object with itself (issue #276, label `bug`) |
| 23 | [история: pysport@486926d] | no | ui | no | — | new feature |
| 24 | [история: pysport@ea5360d] | no | other | no | — | changelog |
| 25 | [история: pysport@2f355a4] | no | other | no | — | new template |
| 26 | [история: pysport@bcfd553] | no | other | no | — | browser compatibility added |
| 27 | [история: pysport@ff0a365] | no | ui | no | — | rebase bookkeeping |
| 28 | [история: pysport@04e2490] | no | report-print | no | — | work in progress; the subject says printing does not work yet |
| 29 | [история: pysport@3e024b1] | no | report-print | no | — | new feature (print margins) |
| 30 | [история: pysport@219301e] | yes (not product) | docs-only | yes (not product) | docs-only | changelog corrected |
| 31 | [история: pysport@32dd0c6] | yes | import-export | yes | import-export | OCAD/WinOrient import and export |
| 32 | [история: pysport@877cf9a] | yes | report-print | yes | report-print | report templates |
| 33 | [история: pysport@a9f7064] | yes | ui | yes | ui | click handling in the start tab |
| 34 | [история: pysport@bc67de4] | no | import-export | no | — | importer feature |
| 35 | [история: pysport@29d55b8] | yes | ui | yes | ui | dialog display |
| 36 | [история: pysport@ae4dbda] | yes | calc | yes | ui | results table not refreshed; the change is in `gui/tabs` |
| 37 | [история: pysport@5dab8cb] | yes | calc | yes | calc | result comparator |
| 38 | [история: pysport@1bb49aa] | no | other | no | — | data-model change |
| 39 | [история: pysport@17a12ca] | no | other | no | — | licence file |
| 40 | [история: pysport@d3e960e] | no | import-export | no | — | removal |
| 41 | [история: pysport@bafd5b9] | no | other | no | — | display improvement |
| 42 | [история: pysport@7ef8f57] | yes | ui | yes | ui | table rows add/remove |
| 43 | [история: pysport@9b86d5c] | no | other | **yes** | ui | adds a guard for an empty control-point list in the course dialog. The subject has no fix word |
| 44 | [история: pysport@605e32e] | yes | other | yes | persistence | "new race" reset did not take effect: a name was shadowed |
| 45 | [история: pysport@dc54810] | no | other | no | — | new dialog |
| 46 | [история: pysport@e517947] | yes | import-export | yes | import-export | OCAD class import |
| 47 | [история: pysport@8d71c2d] | no | import-export | no | — | new importer |
| 48 | [история: pysport@bfcd2fa] | no | import-export | no | — | new importer |
| 49 | [история: pysport@cc9813c] | no | persistence | no | — | new save method |
| 50 | [история: pysport@76fcc0c] | no | other | no | — | description and icon |

## Result
**Fix / non-fix** (confusion in the sample):

| | agent: fix | agent: non-fix |
|---|---|---|
| predicted fix (25) | 24 | 1 (#11) |
| predicted non-fix (25) | 2 (#16, #43) | 23 |

- Agreement in the sample: 47 / 50 = **94 %**.
- **Precision of "is fix"**: 24 / 25 = **96 %**.
- **Recall, estimated for the population.** The sample is stratified, so its raw recall (24/26 = 92 %) is biased. Each stratum has to be weighted by its population, from `counts.json`: 1142 non-merge commits, of them 176 predicted fix and 966 predicted non-fix.
  - estimated true fixes among the predicted fixes: 0.96 × 176 ≈ 169;
  - estimated fixes the rule misses: 2/25 × 966 ≈ 77;
  - recall ≈ 169 / (169 + 77) ≈ **69 %**.
  - With 2 misses in 25, the exact 95 % Clopper–Pearson interval of the miss rate is 1.0–26.0 %. Recall therefore lies between 40 % and 95 %.
- What the rule misses: subjects that describe the faulty behaviour or the guard without a fix word (#16, #43).

**Class agreement** among the 24 true fixes predicted as fixes: 18 / 24 = **75 %**.
- All 6 disagreements (#1, #2, #20, #22, #36, #44) are commits the rule put in `other` (5) or in `calc` by a keyword (#36). Four of them touch `sportorg/models/memory.py` or the old layout `sportorg/app/*`, which the path table does not cover.
- This matches W4's own warning: `other` holds 30 % of product defects.

**Limits:**
- one agent labelled, no human review;
- 50 commits;
- the class judgements in #2, #19, #36 and #44 are borderline. Read class percentages as ±10 points at best.
