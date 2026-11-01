# Legacy repo fix candidates (stage 0)

## 1. Repository facts

- HEAD: `30d849dde1f7ebe04599098b3344b72fdb1210fe`
- HEAD date: 2026-10-18
- Total commits (`git rev-list --count HEAD`): 1341

Last 15 commits:
```
30d849d 2026-10-18 feat: add russian templates
b548c35 2026-09-25 ci: fix building rust code
8a96fb6 2026-09-25 fix(huichang): zero finish and reading contactless cards (#579)
f1cbf4e 2026-09-15 refactor: update py comments
5ea8c40 2026-09-15 refactor: update dict inits
83d3e0a 2026-09-15 refactor: fix index key type
f32d076 2026-09-15 refactor: remove unused set_bib func
ff701a9 2026-09-15 docs: result calculation speed increased 3x
b58130d 2026-09-06 feat(config): rework installers, resolve data, logs and resources rel… (#577)
4824d96 2026-09-01 docs: fix imgs path
981c77c 2026-08-31 perf(results): speed up result recalculation
ea32df0 2026-08-31 perf(splits): speed up split place calculation
b0391dd 2026-07-13 fix(report): correct `Send selected` ordering and multi-day results (refactor to_dict_partial) (#574)
980659f 2026-06-28 fix(printing): apply page margins when printing splits (#568)
c11c36d 2026-05-28 feat: add Light/Dark/System theme switcher (#566)
```

## 2. Candidate search

Rule: message matches `fix|bug|исправ|correct|wrong|error|crash|не ` (case-insensitive) or Conventional Commit type `fix`, AND the commit touches >=1 file under `tests/` AND >=1 file under `sportorg/`. Script: `scripts/legacy_fix_candidates.py`.

**Total matching commits: 11.** Only 11 exist, so the requested 12 cannot be reached; all 11 are listed below. Full list:

| hash | date | src lines changed (+/-) | test files | message |
|---|---|---|---|---|
| b0391dd14 | 2026-07-13 | 274 | tests/test_race_partial.py | fix(report): correct `Send selected` ordering and multi-day results (refactor to_dict_part |
| 393b6303b | 2026-05-14 | 38 | tests/test_otime.py | fix: set default OTime values and remove unnecessary isinstance |
| 57ac99d04 | 2026-05-01 | 65 | tests/test_result_checking.py | fix: use current-day time for MULTI_DAY_RACE overtime check (#556) |
| 2b316380f | 2026-04-29 | 36 | tests/test_qualification.py | feat: fix various qualification names (#555) |
| 3b55fe8b0 | 2025-11-01 | 36 | tests/data/sfrx_file.sfrx, tests/test_sfrx.py | fix: bug with import groups and refactor test with multiday sfrx (#525) |
| c8761e709 | 2025-09-16 | 6 | tests/test_sfrx.py | fix: fix file_autosave_interval was not saved in settings.json (#497) |
| ef983f3e9 | 2025-05-26 | 1289 | tests/test_sfrx.py | feat: middle name and birthday usage, minor fixes of May 2025 (#489) |
| 42e806a58 | 2024-11-24 | 65 | tests/test_gzip.py | fix: fix importing from file for compressed json files |
| 5170d6c31 | 2024-03-21 | 1095 | tests/test_penalty_checking.py, tests/test_result_checking.py | fix: fix penalty laps (#432) |
| aee1e994e | 2023-11-25 | 181 | tests/test_teamwork.py | fix: refactor teamwork client and fix invalid code for teamwork |
| ab72a7987 | 2023-10-15 | 104 | tests/test_json.py | fix: remove backup.binary |

Quality note (factual): in 7 of the 11 commits the diff of `tests/` is only formatting/refactor/timeout/API-rename (marked WEAK); commits with new or extended tests are 57ac99d04, 2b316380f, 3b55fe8b0, b0391dd14. 2b316380f has message type `feat` but matched on the word 'fix'.

## 3. Candidates

### C1. 57ac99d04 - Results/status calculation (multi-day overtime)

- Hash: `57ac99d048fc4453dccdf0f2ac1d1d6f72093f5d`
- Date: 2026-05-01
- Message: fix: use current-day time for MULTI_DAY_RACE overtime check (#556)
- Parent: `ced57547d37451f8afdb835d0f6a3a7ed4a7214a`
- Test quality: STRONG
- Test file(s): tests/test_result_checking.py

Files changed (`git show --stat`):
```
 sportorg/models/memory.py                |  16 +++++-----
 sportorg/models/result/result_checker.py |  49 +++++++++++++++++------------
 tests/test_result_checking.py            | 119 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 155 insertions(+), 29 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 57ac99d04 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** A multi-day event is configured so that the group on day 2 has race type 'multi-day' and a maximum time of 60 minutes. An athlete ran 45 minutes on day 1 and 55 minutes on day 2, so the cumulative time is 100 minutes but today's time is within the limit. When the result of day 2 is checked, the athlete is marked as overtime even though today's run is within the limit. Conversely, an athlete who ran 65 minutes on day 2 must still be marked as overtime. The overtime decision for multi-day groups should depend only on the time of the current day, while individual-race groups keep using their normal result time.

**Hidden test checks:** Overtime status for a MULTI_DAY_RACE result is decided from the current-day time only (OVERTIME when day-2 time exceeds max_time, OK when only the cumulative time does); the test calls a new `ResultChecker.check_overtime(result)` entry point and uses `set_current_race_index`.

### C2. 2b316380f - Import/export formats (qualification names)

- Hash: `2b316380f2ccc95abd8100a6039b1371306cce36`
- Date: 2026-04-29
- Message: feat: fix various qualification names (#555)
- Parent: `7b03c958770ab73d868a8fd7ea24c4c977880183`
- Test quality: STRONG
- Test file(s): tests/test_qualification.py

Files changed (`git show --stat`):
```
 changelog.md                |  1 +
 changelog_ru.md             |  1 +
 sportorg/models/memory.py   | 36 ++++++++++++++++++++++++++++++++----
 tests/test_qualification.py | 19 +++++++++++++++++++
 4 files changed, 53 insertions(+), 4 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 2b316380f -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** When qualification names come from outside (imported tables, entry files), values such as 'кмс' or 'мс' in lower case, 'I', 'ii', '3', '1р', '2Р', '3р', '1ю', 'IIIЮ', 'IIIю' or 'б.р.' are not recognized and the athlete ends up with no qualification (or the wrong one). Case, surrounding spaces, dots and the common short forms (digit only, digit plus 'р' or 'ю', Roman numerals) should all map to the same qualification as the canonical title. Unknown strings should still give 'no qualification'.

**Hidden test checks:** `Qualification.get_qual_by_name` resolves case-insensitive names and aliases (KMS, MS, I/II/III, junior I/II/III, 'б.р.') to the right enum member (new test file).

### C3. 3b55fe8b0 - Import formats (SFRX multi-day import)

- Hash: `3b55fe8b07910fcf16f9fd4b8574e382a3d905a5`
- Date: 2025-11-01
- Message: fix: bug with import groups and refactor test with multiday sfrx (#525)
- Parent: `9e01b24378bb010ca3e0bf26eeff3eab04344f45`
- Test quality: MEDIUM (test data file also changed in the commit)
- Test file(s): tests/data/sfrx_file.sfrx, tests/test_sfrx.py

Files changed (`git show --stat`):
```
 sportorg/libs/sfr/sfrximporter.py |   4 +--
 sportorg/libs/sfr/sfrxparser.py   |  32 ++++++++++++++++++----
 tests/data/sfrx_file.sfrx         |  91 +++++++++++++++++++++++++++++++++++++++----------------------
 tests/test_sfrx.py                | 116 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++--------
 4 files changed, 192 insertions(+), 51 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 3b55fe8b0 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** A multi-day SFR (.sfrx) file defines groups whose distance (course) differs by day, for example group 'Группа1' runs 'Дист1' on day 1 and 'Финал' on day 2. After importing the file, the second day's race does not get the course that belongs to that day for the group, so the athlete's course, splits and results on day 2 are wrong or the import fails. Importing should create two races and assign to each group the course defined for that specific day, together with the correct start/finish times, statuses and first split codes.

**Hidden test checks:** `import_sfrx('tests/data/sfrx_file.sfrx')` creates 2 races and, per person and per day, the expected middle name, group, org, birthday, qualification, course name, start/finish, status and first split code (needs the updated sfrx_file.sfrx fixture).

### C4. b0391dd14 - Teams/reports (Send selected, multi-day partial export)

- Hash: `b0391dd14aff7f48492ff7cc2d364a6e4796284f`
- Date: 2026-07-13
- Message: fix(report): correct `Send selected` ordering and multi-day results (refactor to_dict_partial) (#574)
- Parent: `980659f9e7b7044ce1dd32bf42a53c9bf0793c38`
- Test quality: MEDIUM-LARGE (274 changed lines in sportorg/, tests call new method names)
- Test file(s): tests/test_race_partial.py

Files changed (`git show --stat`):
```
 changelog.md                          |   2 +
 changelog_ru.md                       |   2 +
 sportorg/gui/dialogs/report_dialog.py | 113 ++++++++++-------------
 sportorg/models/memory.py             | 161 ++++++++++++++++----------------
 tests/test_race_partial.py            | 372 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 5 files changed, 505 insertions(+), 145 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show b0391dd14 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** In the report dialog, 'Send selected' builds a partial copy of the race from the selected persons, groups, courses, organizations or results. The groups, courses, organizations, results and persons in that partial copy do not follow the order of the main race model, and selecting by results can include results that were not selected for the same person. For multi-day races, selecting an athlete on one day should also include the same athlete (matched by multi-day id) from the other days, and a selection with no matches should still give a valid, empty structure. An empty selection must produce no data at all.

**Hidden test checks:** A new test file (27 tests) checks the partial race dict builders: empty selection gives None, output lists follow model order, courses matched by id, selected-result filtering, and multi-day matching across Race objects. Note the tests call new method names (`_build_partial`, `partial_for_*`).

### C5. 5170d6c31 - Result checking / penalty laps

- Hash: `5170d6c31044e1fff38c61efae0826483071c16a`
- Date: 2024-03-21
- Message: fix: fix penalty laps (#432)
- Parent: `7d005ecfc347895bf7466c5e929ee78a6583f6b9`
- Test quality: WEAK (1095 src lines; test diff is cleanup only)
- Test file(s): tests/test_penalty_checking.py, tests/test_result_checking.py

Files changed (`git show --stat`):
```
 builder.py                                                                  |    1 +
 configs/status_default.txt                                                  |    6 +
 languages/ru_RU/LC_MESSAGES/sportorg.po                                     |    3 +
 poetry.lock                                                                 | 2248 +++++++++++++++++------------------
 pyproject.toml                                                              |    2 +-
 sportorg/config.py                                                          |    2 +
 sportorg/gui/dialogs/bib_dialog.py                                          |    2 +-
 sportorg/gui/dialogs/entry_mass_edit.py                                     |    4 +-
 sportorg/gui/dialogs/merge_results.py                                       |    4 +-
 sportorg/gui/dialogs/not_start_dialog.py                                    |    4 +-
 sportorg/gui/dialogs/person_edit.py                                         |   36 +-
 sportorg/gui/dialogs/result_edit.py                                         |   12 +-
 sportorg/gui/dialogs/start_preparation.py                                   |    2 +-
 sportorg/gui/dialogs/text_io.py                                             |    2 +-
 sportorg/gui/dialogs/timekeeping_properties.py                              |    6 +
 sportorg/gui/main.py                                                        |    4 +
 sportorg/gui/main_window.py                                                 |   62 +-
 sportorg/gui/menu/actions.py                                                |   14 +-
 sportorg/gui/tabs/memory_model.py                                           |    8 +-
 sportorg/libs/iof/parser.py                                                 |   70 +-
 sportorg/libs/winorient/wdb.py                                              |   12 +-
 sportorg/models/constant.py                                                 |   16 +-
 sportorg/models/memory.py                                                   |  148 ++-
 sportorg/models/result/result_checker.py                                    |   69 +-
 sportorg/models/start/relay.py                                              |    2 +-
 sportorg/models/start/start_preparation.py                                  |  518 ++++++--
 sportorg/modules/backup/json.py                                             |    9 +
 sportorg/modules/iof/iof_xml.py                                             |   10 +-
 sportorg/modules/live/orgeo.py                                              |   31 +-
 sportorg/modules/printing/printout_split.py                                 |   17 +-
 sportorg/modules/recovery/recovery_orgeo_finish_csv.py                      |    3 +-
 sportorg/modules/recovery/recovery_si_master_csv.py                         |    1 +
 sportorg/modules/recovery/recovery_sportorg_html.py                         |    1 +
 sportorg/modules/sportident/result_generation.py                            |   16 +-
 sportorg/modules/winorient/wdb.py                                           |    6 +-
 sportorg/modules/winorient/winorient.py                                     |    4 +-
 ...74\320\274\320\265\320\275\321\202\320\260\321\200\320\270\320\271.html" |  227 ++++
 tests/test_penalty_checking.py                                              |    5 +-
 tests/test_result_checking.py                                               |   30 +-
 39 files changed, 2152 insertions(+), 1465 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 5170d6c31 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** In marked-route races with penalty laps, the status and penalty count for a result can be wrong after a plain result check: penalty laps are only produced if a second, separate penalty calculation step is also invoked. Checking a result with the normal check call alone should already set the status (OK / missing punch / penalty-lap related) and the penalty value consistently. This affects marked-route courses with extra or missing punches and penalty-lap station punches.

**Hidden test checks:** The existing penalty tests call only `ResultChecker.checking(result)` (the explicit `calculate_penalty` call is removed) and still expect the same status and penalty.

### C6. 393b6303b - GUI-independent utilities (OTime defaults)

- Hash: `393b6303b0649c8d4efff9f640250bc599c8405d`
- Date: 2026-05-14
- Message: fix: set default OTime values and remove unnecessary isinstance
- Parent: `4e686eb6810c4f5bb6a75817badc518c22e785bc`
- Test quality: WEAK (test diff is formatting only)
- Test file(s): tests/test_otime.py

Files changed (`git show --stat`):
```
 benches/test_otime_benchmark.py |  8 ++++----
 sportorg/models/memory.py       | 34 +++++++++++++++++-----------------
 sportorg/modules/iof/iof_xml.py |  4 +++-
 tests/test_otime.py             |  4 +---
 4 files changed, 25 insertions(+), 25 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 393b6303b -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** Fresh result objects hold 'no value' for start time, penalty time, credit time, diff and final result time instead of a zero time value. Code that uses these fields (arithmetic, comparisons, export to IOF XML) has to special-case the missing values, and some paths fail or print nothing for a new result. A new result should behave as if these times were zero.

**Hidden test checks:** Only a line-wrapping change in tests/test_otime.py; no behavioral check of the fix is present.

### C7. c8761e709 - GUI-independent utilities (settings persistence)

- Hash: `c8761e7096215c7394c9034cbbc8eee65d3df097`
- Date: 2025-09-16
- Message: fix: fix file_autosave_interval was not saved in settings.json (#497)
- Parent: `f270bfddf8d6fb39e1fcc5f938ded8b7bc482e17`
- Test quality: WEAK (test diff is formatting only)
- Test file(s): tests/test_sfrx.py

Files changed (`git show --stat`):
```
 changelog.md                       | 1 +
 changelog_ru.md                    | 1 +
 sportorg/libs/settings/__init__.py | 2 +-
 sportorg/settings.py               | 4 ++--
 tests/test_sfrx.py                 | 6 +++---
 5 files changed, 8 insertions(+), 6 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show c8761e709 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** The 'autosave interval' option is changed in the settings dialog and the application is restarted, but the value is not found in settings.json, so the option reverts to its default. The settings file is also written with non-ASCII text escaped. The saved settings file should contain the interval and keep Cyrillic text readable.

**Hidden test checks:** Only a formatting change in tests/test_sfrx.py; no check of settings persistence.

### C8. 42e806a58 - Import/export formats (compressed JSON)

- Hash: `42e806a5810c17c3ca20139c9341d654ab9f218d`
- Date: 2024-11-24
- Message: fix: fix importing from file for compressed json files
- Parent: `ab70d6c631fe33981ce4d2809c3d62fc0d751edc`
- Test quality: WEAK (test diff is a quote-style change)
- Test file(s): tests/test_gzip.py

Files changed (`git show --stat`):
```
 sportorg/gui/menu/actions.py    | 45 +++++++++++++++++++++++++++------------------
 sportorg/modules/backup/file.py | 20 ++++++++++++--------
 tests/test_gzip.py              |  2 +-
 3 files changed, 40 insertions(+), 27 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show 42e806a58 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** Opening a saved event file from the menu reads it with the wrong settings when the file is gzip-compressed but the current 'save in gzip' option is off (or the reverse). The loader should detect compression from the file contents, not from the option, and read the file regardless of the current save settings.

**Hidden test checks:** tests/test_gzip.py::test_save_and_open_gzip (open, save compressed, reopen); only quote style changed in the commit.

### C9. aee1e994e - Teams/relay (teamwork client)

- Hash: `aee1e994e58634d2ae850a1816446757fc73b62f`
- Date: 2023-11-25
- Message: fix: refactor teamwork client and fix invalid code for teamwork
- Parent: `12ea8fb92df7a2607463edfb07f0a53dcbc52527`
- Test quality: WEAK (test diff is a timeout change)
- Test file(s): tests/test_teamwork.py

Files changed (`git show --stat`):
```
 sportorg/gui/main_window.py         |   2 +-
 sportorg/models/memory.py           |   1 -
 sportorg/modules/teamwork/client.py | 165 ++++++++++++++++++++++++++++++++--------------------------------------------
 sportorg/modules/teamwork/server.py |  13 +++---
 tests/test_teamwork.py              |   2 +-
 5 files changed, 79 insertions(+), 104 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show aee1e994e -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** In teamwork mode, a client connected to a server does not reliably deliver objects created on the client side (for example a new Person) to the server queue and back; the client code contains invalid calls. The client should send a created object to the server and receive the echoed message within a reasonable time.

**Hidden test checks:** tests/test_teamwork.py::test_teamwork waits up to 10 s (was 5) for the Person 'Create' message; no new assertion.

### C10. ab72a7987 - Import/export formats (backup)

- Hash: `ab72a79879b49804dc8b19795cb21fb03ee0d0d0`
- Date: 2023-10-15
- Message: fix: remove backup.binary
- Parent: `f5e650108d9165c0d26d3df65dc991f9ca44dc03`
- Test quality: WEAK (removal/refactor, test API changed)
- Test file(s): tests/test_json.py

Files changed (`git show --stat`):
```
 sportorg/gui/main_window.py       |  6 +++---
 sportorg/modules/backup/binary.py | 41 -----------------------------------------
 sportorg/modules/backup/file.py   | 57 +++++++++++++++++++++++----------------------------------
 tests/test_json.py                |  4 +---
 4 files changed, 27 insertions(+), 81 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show ab72a7987 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** Event files are saved and opened through a File helper that accepts a file name only; the legacy binary backup format and the logger/format arguments are removed. Opening 'tests/data/test.json' with just a path must load the event with the expected organization, group and person.

**Hidden test checks:** tests/test_json.py::test_main opens the JSON via `File(path).open()` and checks person, group and organization.

### C11. ef983f3e9 - Mixed (middle names/birthday; 1289 src lines)

- Hash: `ef983f3e924fc4e1381615c0966d15cb03657cd7`
- Date: 2025-05-26
- Message: feat: middle name and birthday usage, minor fixes of May 2025 (#489)
- Parent: `fab209a8bb2482fe772f641c4eabcb6a8d56d1c7`
- Test quality: WEAK (mega-commit; test diff is formatting only)
- Test file(s): tests/test_sfrx.py

Files changed (`git show --stat`):
```
 configs/middle_names.txt                            | 269 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 languages/ru_RU/LC_MESSAGES/sportorg.po             |  24 +++++-
 sportorg/config.py                                  |   2 +
 sportorg/gui/dialogs/about.py                       |  11 ++-
 sportorg/gui/dialogs/bib_dialog.py                  |  23 +++++-
 sportorg/gui/dialogs/course_edit.py                 |   4 +-
 sportorg/gui/dialogs/cp_delete.py                   |  29 +++++--
 sportorg/gui/dialogs/dialog.py                      |  47 +++++++----
 sportorg/gui/dialogs/entry_mass_edit.py             |  11 ++-
 sportorg/gui/dialogs/event_properties.py            |  32 +++++---
 sportorg/gui/dialogs/file_dialog.py                 |   5 +-
 sportorg/gui/dialogs/filter_dialog.py               |  12 ++-
 sportorg/gui/dialogs/group_edit.py                  |   4 +-
 sportorg/gui/dialogs/group_mass_edit.py             |  11 ++-
 sportorg/gui/dialogs/group_ranking.py               |  26 ++++--
 sportorg/gui/dialogs/import_persons_table_dialog.py |  42 +++++++---
 sportorg/gui/dialogs/live_dialog.py                 |  35 +++++---
 sportorg/gui/dialogs/marked_route_dialog.py         |  29 +++++--
 sportorg/gui/dialogs/merge_results.py               |   8 +-
 sportorg/gui/dialogs/not_start_dialog.py            |  36 +++++---
 sportorg/gui/dialogs/organization_mass_edit.py      |  11 ++-
 sportorg/gui/dialogs/person_edit.py                 |  15 +++-
 sportorg/gui/dialogs/print_properties.py            |  41 ++++++---
 sportorg/gui/dialogs/relay_clone_dialog.py          |   8 +-
 sportorg/gui/dialogs/relay_number_dialog.py         |   8 +-
 sportorg/gui/dialogs/rent_cards_dialog.py           |  23 +++++-
 sportorg/gui/dialogs/report_dialog.py               |  30 +++++--
 sportorg/gui/dialogs/result_edit.py                 |  47 +++++++----
 sportorg/gui/dialogs/search_dialog.py               |  29 +++++--
 sportorg/gui/dialogs/settings.py                    |  41 ++++++---
 sportorg/gui/dialogs/split_delete.py                |  20 ++++-
 sportorg/gui/dialogs/sportorg_import_dialog.py      |  29 +++++--
 sportorg/gui/dialogs/start_handicap_dialog.py       |  26 ++++--
 sportorg/gui/dialogs/start_preparation.py           |  11 ++-
 sportorg/gui/dialogs/start_time_change_dialog.py    |   8 +-
 sportorg/gui/dialogs/teamwork_properties.py         |  35 +++++---
 sportorg/gui/dialogs/telegram_dialog.py             |  38 ++++++---
 sportorg/gui/dialogs/text_io.py                     |  38 ++++++++-
 sportorg/gui/dialogs/timekeeping_properties.py      |  41 ++++++---
 sportorg/gui/main.py                                |  16 +++-
 sportorg/gui/main_window.py                         |  33 +++++++-
 sportorg/gui/menu/actions.py                        |  17 +++-
 sportorg/gui/menu/menu.py                           |   4 +
 sportorg/gui/tabs/courses.py                        |   5 +-
 sportorg/gui/tabs/groups.py                         |   5 +-
 sportorg/gui/tabs/log.py                            |   5 +-
 sportorg/gui/tabs/memory_model.py                   |  21 ++++-
 sportorg/gui/tabs/organizations.py                  |   5 +-
 sportorg/gui/tabs/persons.py                        |   5 +-
 sportorg/gui/tabs/results.py                        |   8 +-
 sportorg/gui/tabs/table.py                          |  11 ++-
 sportorg/gui/utils/custom_controls.py               |  23 +++++-
 sportorg/libs/iof/parser.py                         |   4 +-
 sportorg/libs/sfr/sfrximporter.py                   |   6 +-
 sportorg/libs/sfr/sfrxparser.py                     |   3 +-
 sportorg/libs/srpid/srpid.py                        |   4 +-
 sportorg/models/constant.py                         |  18 ++++
 sportorg/models/memory.py                           | 111 +++++++++++++++++++++----
 sportorg/models/result/result_checker.py            |   1 +
 sportorg/models/start/start_preparation.py          |  14 +++-
 sportorg/modules/backup/json.py                     |   2 +
 sportorg/modules/iof/iof_xml.py                     |   1 +
 sportorg/modules/live/orgeo.py                      |   1 +
 sportorg/modules/ocad/ocad.py                       |   3 +-
 sportorg/modules/printing/printing.py               |  14 +++-
 sportorg/modules/rfid_impinj/rfid_impinj.py         |   6 +-
 sportorg/modules/sfr/sfrreader.py                   |   5 +-
 sportorg/modules/sportident/sireader.py             |   7 +-
 sportorg/modules/sportiduino/sportiduino.py         |   6 +-
 sportorg/modules/srpid/srpid.py                     |   6 +-
 sportorg/modules/teamwork/teamwork.py               |   5 +-
 sportorg/modules/winorient/wdb.py                   |   5 +-
 sportorg/modules/winorient/winorient.py             |   1 +
 sportorg/utils/time.py                              |  42 ++++++----
 tests/test_sfrx.py                                  |   6 +-
 75 files changed, 1264 insertions(+), 324 deletions(-)
```

Test diff: removed on 2026-11-01, legacy test code quotes personal data of legacy's test files `[мейнтейнер: 2026-11-01]`; reproduce with `git -C .legacy/pysport show ef983f3e9 -- tests/ ':!tests/data' | head -80`.

**TASK DESCRIPTION:** A large May-2025 batch: middle name and birth date usage in imports and dialogs plus assorted fixes. There is no single observable bug; the test change in the commit is only a wrapping change of an assertion.

**Hidden test checks:** Only formatting in tests/test_sfrx.py.

## 4. Side data

### Top 25 most frequently changed files (all history)
```

```

### `sportorg/models/memory.py` at HEAD
2910 lines (`git show HEAD:sportorg/models/memory.py | wc -l`).
