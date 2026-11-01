# Oracle seam (Stage 2, S2; TASK-8 AC #1)

Every `.json`/`.md` file here except `*.agent.md` is output of a script; the commands are in
`commands.txt`. `inputs/` is written by `scripts/corpus/synth.py`, `synthetic/` and the tables by
`scripts/oracle_evidence.py`, which calls the oracle (`scripts/oracle_cli.py`) the same way as the
command of AC #1:

```
uv run python scripts/oracle.py RACE_FILE              # normalized results on stdout
uv run python scripts/oracle.py RACE_FILE --out DIR    # results.json, stored.json, comparison.json, run.json
```

| File | What it shows |
|---|---|
| `inputs/{individual,relay,rogaine}.json` | synthetic race files in legacy's JSON format (no personal data: "Synthetic Runner NNN", chip 0, no birth date) |
| `inputs/{f3_rogaine_tie,f4_slow_leader,f6_two_races}.json` | one finding each (F3, F4, F6 of `findings.agent.md`), for the maintainer's check in legacy's GUI (`docs/reports/stage-2-check-f3-f4-f6.md`); `f6_two_races` holds two races, the first current, not a multi-day event |
| `synthetic/<race>/results.json` | legacy's recalculation, normalized (schema below), first lane |
| `synthetic/<race>/stored.json` | the values stored in the file, normalized the same way (synthetic files store no computed values) |
| `synthetic/<race>/comparison.json` | stored vs recalculated, field by field (`scripts/oracle_compare.py`) |
| `synthetic/<race>/run.json` | how the run was made: legacy pin and version, Python, clock, state, file format, input SHA-256, count of results without a stored finish |
| `synthetic/f6_two_races/after-open/` | the same four files for `--state after-open`: what the GUI shows for each race after File > Open and a switch to it, before a recheck (F6) |
| `lanes.md`, `.json` | each input three times: a rerun on the first lane (all four files byte-identical) and the second lane (the three data files identical) |
| `canary.md`, `.json` | a later finish of one runner changes their place and time |
| `legacy-test-json.md`, `.json` | legacy `tests/data/test.json` (personal data `[мейнтейнер: 2026-10-31]`): counts and hashes only |
| `typecheck.md`, `.json` | basedpyright on the driver with legacy sources, without them (CI), with the stubs (ADR-0009 T3) |
| `findings.agent.md` | agent judgement: what the outputs show about legacy, classification proposals, questions |

## How the oracle runs

- Legacy runs only as a separate process: `python -m scripts.oracle_driver.driver` under
  `.legacy-run/pysport/.venv` (CPython 3.8.20, first lane, ADR-0009 T1) or `--venv
  .legacy-run/pysport/.venv-3.13` (3.13.17, second lane). The project never imports `sportorg`.
- Environment: `scripts.legacy_env.hermetic_env` (temporary HOME and XDG directories, `TZ=UTC`,
  `C.UTF-8`, `PYTHONHASHSEED=0`, no `DISPLAY`/`WAYLAND_DISPLAY`), `QT_QPA_PLATFORM=offscreen`,
  `PYTHONDONTWRITEBYTECODE=1`; working directory is a temporary one; nothing is written into the copy.
- What the driver does, each step as legacy does it (`scripts/oracle_driver/driver.py`):
  1. the clock is an input: `OTime.now()` returns `--now`, because a result without a stored finish
     takes the clock `[код: pysport@b548c35 sportorg/models/memory.py:499,878-882]`. The default is
     `23:59:59` `[мейнтейнер: 2026-11-01]`: `OTime` is false only at `00:00:00` and legacy branches
     on that `[код: pysport@b548c35 sportorg/common/otime.py:104-105, sportorg/models/memory.py:544,879]`,
     and the last second of the day keeps such a time from wrapping over midnight;
  2. startup tables that the recalculation reads: status default comments and ranking tables from the
     shipped configs `[код: pysport@b548c35 sportorg/gui/main.py:47-56,62-75,124-137]`; legacy's
     `settings.json` is not read, its defaults apply `[допущение: an operator's settings.json is not part of the race file]`;
  3. `stored`: the file's own JSON, read the way legacy opens it: gzip if the file is gzip, otherwise
     UTF-8, otherwise the machine's locale encoding `[код: pysport@b548c35 sportorg/modules/backup/file.py:28-51]`;
     legacy's own load would drop the computed values the file holds
     `[код: pysport@b548c35 sportorg/models/memory.py:472-478,650-692]`. SportOrg 1.7.0 and 1.7.1 save
     in the locale encoding by default, cp1251 on Russian Windows `[история: pysport f26c80f]`; the
     oracle runs in C.UTF-8, so it tries cp1251 itself and gives legacy's `json.load` the decoded
     text, as `File.open` does there (Q3 (b) `[мейнтейнер: 2026-11-01]`). `run.json` names the
     format: `gzip`, `utf-8` or `cp1251`. A file that is none of them is refused
     (`UndecodableRaceFile`). cp1251 decodes almost any bytes, so a file in another 8-bit encoding
     would pass with garbled text, which changes group names, not numbers `[допущение]`;
  4. `--state recalculated` (the default): `File.open` (legacy's load, which already recalculates),
     then for every race: make it current, rebuild indexes, `recalculate_results(race_object=race())`,
     as the GUI does for a multi-day event `[код: pysport@b548c35 sportorg/gui/main_window.py:678-686]`;
     each race is then serialized with `Race.to_dict()` while it is current. For a file with several
     races that is not a multi-day event the GUI does not do this pass: there a non-current race shows
     what `load()` computed while another race was current
     `[код: pysport@b548c35 sportorg/modules/backup/json.py:42-44, sportorg/models/result/result_tools.py:106]`
     (`findings.agent.md`, F6, confirmed in the GUI by the maintainer). The oracle gives each race the
     result it has when it is alone in a file
     (`test_oracle_cli.py::test_each_race_of_a_multi_race_file_in_its_own_context`);
  5. `--state after-open`: `File.open` and what the GUI does next, `init_model`: a multi-day event
     recalculates every race, any other file only rebuilds indexes (`rebuild_indexes(True, True)`);
     a switch to a race runs `init_model` again, so each race is serialized while it is current
     after that rebuild `[код: pysport@b548c35 sportorg/gui/main_window.py:951-961,659-687,
     sportorg/gui/dialogs/settings.py:317-329]`. For a file with one race both states give the same
     results (`test_after_open_equals_the_recalculation_for_one_race`); `synthetic/f6_two_races/after-open/`
     shows the difference for F6. Not reproduced in either state: `load()` sets `live_enabled` off
     `[код: pysport@b548c35 sportorg/modules/backup/json.py:45-47]` (a setting, outside the schema),
     and the GUI's lock file, title and recent files.
- Personal data: the driver copies only whitelisted keys (`scripts/oracle_driver/snapshot.py`), so
  names, birth dates, chip numbers, organizations, comments and `status_comment` never leave the
  legacy process. A legacy error is reported as its type and stack frames without the message; the
  driver's stderr is hidden unless `--show-stderr`.

## Normalized schema, version 2

```
{"schema": "sportorg-ng/oracle-results", "schema_version": 2,
 "races": [{"race_id", "race_index", "race_type", "processing_mode", "time_accuracy",
            "time_rounding", "results": [...], "relay_teams": [...]}]}
result: {"result_id", "person_id", "group", "bib", "system", "status", "place", "time_ms",
         "start_ms", "finish_ms", "penalty_ms", "credit_ms", "penalty_laps", "diff_ms", "scores",
         "rogaine_score", "rogaine_penalty", "scores_ardf", "diff_scores", "rank", "order",
         "splits": [{"code", "time_ms", "leg_ms", "relative_ms", "leg_place", "relative_place",
                     "is_correct", "course_index"}]}
relay team: {"group", "bib", "place", "order", "time_ms", "correct_legs", "status_ok",
             "legs": [{"leg", "result_id"}]}
```

- Identity: `result_id` and `person_id` are the UUIDs from the file; `group` is the group name.
- Enums by legacy's own names, taken from the legacy enums at run time: `status` (`ResultStatus`),
  `system` (`SystemType`), `race_type` (`RaceType`), `rank` (`Qualification`); an unknown value
  shows as `<n>`.
- Times are integer milliseconds as legacy computes them (`result_msec`, `leg_time`, …); `place` is
  legacy's integer (`-1` = no place, `0` = not set). In `results.json` every field is present and
  `null` means legacy has no value. In `stored.json` (version 2) a field the file does not hold is
  left out, and `null` means the file holds `null`: legacy writes a zero time behind, penalty or
  credit so `[код: pysport@b548c35 sportorg/models/memory.py:612,614,615]`. Version 1 wrote both as
  `null`, which hid a real difference behind `not_stored` (review of 2026-11-01).
  `processing_mode`, `time_accuracy`, `time_rounding`: `null` when not set in the file, legacy
  defaults `time`, `0`, `math` apply.
- Canonical order: results by group name (results without a group last), place (`<= 0` last),
  `person_id`, `result_id`; splits in punch order; relay teams by group, place, bib. This is the
  oracle's order, not legacy's display order.
- Not in the schema: names, birth dates, chip numbers, organizations, comments, `status_comment` (free
  text, D1), `created_at`, `can_win_count` and `final_result_time` (clock), formatted and translated
  strings (`result`, `result_current`), `speed`.
- `comparison.json` matches results by `result_id`; per field it counts `same`, `different` and
  `not_stored` (the file does not hold the field; not a difference) and lists each difference with
  both values. A `null` the file holds is compared like any value: `null` against `60000` is a
  difference.
- What the comparison cannot see: a file holds only what its SportOrg version saved. Older files
  have no `result_msec`, `start_msec`, `finish_msec` (legacy `test.json`: `time_ms`, `start_ms`,
  `finish_ms` all `not_stored`), so their times are not compared, only status, place, splits and the
  other stored fields. Relay teams are never stored in a file, so `relay_teams` is not compared.
  Results that share a `result_id` count once.
