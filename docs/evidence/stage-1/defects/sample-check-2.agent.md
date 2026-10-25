# Defect classifier: sample check 2 of 50 commits (agent judgement)

The labels in this file are the judgement of the main session's agent (Claude Code, Opus 5.5) on
2026-10-25, not script output; no human reviewed them. It checks the classifier after the maintainer's
change of 2026-10-25 (report question 5: old `sportorg/app/*` layout mapped, `memory.py` classified by
changed functions) on a **new** sample with another seed. Sample check 1 (`sample-check-1.agent.md`) was
seen while the change was made, so it is not an independent test of the change. The sample was chosen
by a script:

```
uv run python -m scripts.archaeology.sample --json docs/evidence/stage-1/defects/commits.json \
    --n 50 --seed 20261026 --where is_merge=false --stratify is_fix \
    --fields sha,type,is_fix,product_defect,class,class_rule,modules
```

## Criteria
The same criteria as sample check 1:
- **fix** corrects wrong behaviour.
- **class** is one of the 12 classes, chosen from what the change does.

The agent read the subject, the files and, where needed, the diff. Texts are not copied (Stage 1 rule 4). Three commits are also in sample 1 (#9, #19, #41); their labels agree with it.

## Sample
| # | commit | predicted fix | predicted class (rule) | fix (agent) | class (agent) | why |
|---|---|---|---|---|---|---|
| 1 | [история: pysport@ea32df0] | no | calc (keyword) | no | — | `perf:` faster split places |
| 2 | [история: pysport@5df1b7a] | yes | report-print (path) | yes | report-print | print page margins under PySide2 |
| 3 | [история: pysport@42b19fd] | yes | other (other) | yes | persistence | table rows reversed after opening a file |
| 4 | [история: pysport@f732da3] | yes | ui (path) | yes | import-export | import of persons from a pasted table lost the last row |
| 5 | [история: pysport@ad49dbb] | yes | ui (path) | yes | import-export | index error in the same table import |
| 6 | [история: pysport@a051451] | no | ui (path) | no | — | new feature |
| 7 | [история: pysport@6b4e580] | no | report-print (keyword) | no | — | new setting |
| 8 | [история: pysport@3b1a5b5] | yes | online (keyword) | yes | online | teamwork client/server CPU load |
| 9 | [история: pysport@314ae59] | yes | calc (keyword) | no | — | `fix:` type, but typing and `repr` only (same commit as #11 of sample 1) |
| 10 | [история: pysport@06102cc] | no | ui (path) | no | — | new option: ignore punches before the start |
| 11 | [история: pysport@ca77b70] | no | ui (path) | no | — | new feature (merge results) |
| 12 | [история: pysport@286fc0c] | yes | persistence (path) | yes | persistence | data lost on power failure: flush and fsync added |
| 13 | [история: pysport@328f57d] | yes | i18n (path) | yes | ui | dialog and main-window fixes after a merge |
| 14 | [история: pysport@607dbe6] | no | calc (keyword) | no | — | new feature (delete splits) |
| 15 | [история: pysport@029e041] | yes | online (keyword) | yes | online | live upload |
| 16 | [история: pysport@bf6c804] | yes | device (path) | yes | device | Sportiduino driver fixes |
| 17 | [история: pysport@7e6a8c3] | yes | other (other) | yes | platform-build | setup script |
| 18 | [история: pysport@0f3a0a8] | no | other (other) | no | — | new feature (control-point ranges) |
| 19 | [история: pysport@af08823] | yes | other (other) | yes | import-export | organization contact in IOF XML (same commit as #20 of sample 1) |
| 20 | [история: pysport@920270d] | yes | report-print (keyword) | yes | ui | bugs reported by a user, fixed in the table model of the GUI |
| 21 | [история: pysport@27072f9] | no | other (other) | no | — | dependency list |
| 22 | [история: pysport@1bbab50] | yes | other (other) | yes | report-print | sorting in the results template |
| 23 | [история: pysport@9783cdb] | no | other (other) | **yes** | report-print | double place in the sum-of-times template; the subject names the error without a fix word |
| 24 | [история: pysport@868d5e3] | no | calc (keyword) | no | — | new feature (rogaining scores) |
| 25 | [история: pysport@592e51c] | yes | time (keyword) | yes | start-draw | start interval added wrongly in the start-time manager |
| 26 | [история: pysport@e4d5603] | yes | other (other) | yes | calc | default split code `'0'` → `''` |
| 27 | [история: pysport@73d329f] | no | calc (memory-functions) | no | — | the split matching in `get_course_splits` is replaced by a filter on `is_correct`; a behaviour change, but no fault named (corrected 2026-10-25 after the independent check: was "refactoring") |
| 28 | [история: pysport@7a35a21] | no | import-export (path) | no | — | new feature |
| 29 | [история: pysport@ffa73f9] | no | platform-build (keyword) | no | — | installer build path setting |
| 30 | [история: pysport@f0d2dff] | no | calc (keyword) | **yes** | calc | relay ranking used finished laps instead of correct laps; no fix word |
| 31 | [история: pysport@3c6b20e] | yes | device (memory-functions) | yes | ui | guards against missing tables in the main window |
| 32 | [история: pysport@86cdb59] | no | online (keyword) | no | — | new module |
| 33 | [история: pysport@fc7a97b] | yes | report-print (keyword) | yes | report-print | templates |
| 34 | [история: pysport@89f819d] | no | ui (path) | no | — | removal |
| 35 | [история: pysport@01ff985] | no | ui (path) | **yes** | ui | edit dialogs rejected an unchanged name as a duplicate; no fix word |
| 36 | [история: pysport@0b50f5a] | no | calc (keyword) | no | — | new feature |
| 37 | [история: pysport@c464bfe] | no | other (other) | no | — | changelog and version |
| 38 | [история: pysport@6f68935] | no | persistence (keyword) | no | — | new feature (recent file) |
| 39 | [история: pysport@3fb9a6a] | no | device (keyword) | **yes** | ui | year and numbers stored as text instead of int in the entry dialog; no fix word |
| 40 | [история: pysport@b16a6bd] | yes | device (keyword) | yes | import-export | WinOrient WDB course leg lengths read wrongly |
| 41 | [история: pysport@7ef8f57] | yes | ui (keyword) | yes | ui | table rows add/remove (same commit as #42 of sample 1) |
| 42 | [история: pysport@c813685] | no | import-export (keyword) | no | — | refactoring into a plugin |
| 43 | [история: pysport@03dd9a7] | no | ui (keyword) | no | — | performance cache and refactoring |
| 44 | [история: pysport@c48c611] | no | ui (keyword) | no | — | dialog placement |
| 45 | [история: pysport@5a49ea9] | yes | other (other) | yes | other | `find()` helper passed a control keyword on as a filter |
| 46 | [история: pysport@1c56296] | no | import-export (keyword) | no | — | new reader |
| 47 | [история: pysport@f5b2b92] | yes | other (other) | yes | ui | "Fix" subject; database set-up and window building move from `__init__` to `mainloop` of the 2017 prototype `so_widget/app.py`, so the behaviour changes (relabelled 2026-10-25 after the independent check: was "no, only moves a method"; the class is borderline) |
| 48 | [история: pysport@a4212b5] | yes | import-export (keyword) | yes | import-export | import |
| 49 | [история: pysport@35a6d98] | yes | other (other) | yes | persistence | opening and creating a file |
| 50 | [история: pysport@7d6a1bb] | yes | other (other) | yes | persistence | opening and creating a file |

## Result
**Fix / non-fix:**

| | agent: fix | agent: non-fix |
|---|---|---|
| predicted fix (25) | 24 | 1 (#9) |
| predicted non-fix (25) | 4 (#23, #30, #35, #39) | 21 |

- Agreement: 45 / 50 = **90 %**.
- **Precision of "is fix":** 24 / 25 = **96 %** (exact 95 % Clopper–Pearson interval 79.7–99.9 %).
- **Recall, estimated for the population** (strata 176 predicted fix and 966 predicted non-fix):
  - estimated true fixes found: 0.96 × 176 ≈ 169;
  - estimated fixes missed: 4/25 × 966 ≈ 155;
  - recall ≈ **52 %**.
- **Interval of the recall.** Both rates are uncertain, so the interval takes both:
  - each rate gets an exact 97.5 % Clopper–Pearson interval: precision 77.1–99.95 %, miss rate 3.7–38.9 %;
  - the recall bounds come from the worst and best corners, so together they cover at least 95 % (Bonferroni);
  - recall lies between **27 % and 83 %**;
  - for comparison, the interval of the miss rate alone (as written before 2026-10-25) gives 33–79 %.
- **Both samples pooled.** 97 distinct commits: the three commits of both samples (#9, #19, #41, all in the predicted-fix stratum) are counted once:
  - precision 46/47 = 98 % (97.5 % interval 87.2–99.97 %);
  - miss rate 6/50 = 12 % (97.5 % interval 3.9–26.2 %);
  - recall ≈ **60 %**, between **38 % and 82 %** by the same method;
  - the fix rule did not change between the samples, so pooling is fair for fix / non-fix. It is not fair for classes (below).
- **What the rule misses:** the same pattern as in sample 1. The subject describes the fault ("error", a wrong value) or the fix without a fix word.

**Class agreement** among the true fixes predicted as fixes: **9 / 24 = 38 %**. This is the only independent estimate of the class rule.
- The 15 disagreements:
  - `other` while the change has a clear class (#3, #17, #19, #22, #26, #47, #49, #50): templates under the old top-level `templates/`, `setup.py`, top-level 2017 files and `memory.py` methods without a keyword;
  - path to `ui` for the table-import dialog (#4, #5);
  - the `.po` file deciding `i18n` (#13);
  - keyword errors: "report" from "reporting bugs" (#20), "time" in a start-draw fix (#25), "read" in a file-format fix (#40);
  - `memory-functions` giving `device` for a GUI guard (#31).
- **Sample 1 is not an independent check of classes.** The new classifier agrees with its labels in 19/24 cases (79 %; before the change 18/24, 75 %). The agent saw that sample while changing the classifier, so the number is not pooled with this one. (Before 2026-10-25 this file gave a pooled 28/47 = 60 %; the independent check pointed out that it mixes the tuning sample in.)
- **Consequence:** the module × class table is a rough guide only. The class of a single commit is unreliable, especially before 2018 and for templates.

**Limits:**
- one agent labelled, no human review. The independent check (a fresh agent session on 2026-10-25) relabelled 10 rows (2, 7, …, 47) and disagreed on #47 only; that row is relabelled above;
- borderline class judgements in #4, #5, #25, #31 and #47.
