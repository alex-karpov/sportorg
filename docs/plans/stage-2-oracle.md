# Stage 2 — Oracle and Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Checkboxes are not status (AGENTS.md rule 6): progress is recorded in the notes of Backlog TASK-8 and in the Session log at the end of this file.

**Backlog task:** TASK-8 (seven acceptance criteria), milestone m-2. Branch: `stage-2` (from `main`).

**Goal:** a headless oracle over the pinned legacy (`pysport@b548c35`) that recalculates a race file
and exports normalized results; golden-master tests on synthetic data and, locally, on the anonymized
corpus; replay of device dumps through virtual serial ports; legacy smoke on three OS; a baseline.
Ends with `docs/reports/stage-2.md` and a verification prompt.

**Architecture:** legacy runs only as a separate process in its own environment in
`.legacy-run/pysport` (Python chosen by measurement, ADR-0009). The project side (`scripts/`) never
imports `sportorg`: it starts the legacy interpreter on a small driver, receives raw JSON on stdout and
normalizes it in project code under TDD. Golden files are protected by a CI check that is not tied to
any agent (ADR-0008). Every number comes from a script; outputs are deterministic so a rerun is
byte-identical.

**Tech Stack:** Python 3.14 stdlib + pytest on the project side; legacy's own `uv.lock` in
`.legacy-run/pysport` (PySide6 with `QT_QPA_PLATFORM=offscreen`); `git` for the golden guard; virtual
serial ports per OS (S5, ADR by measurement).

**Spec:** `docs/brief.md` §«Этап 2», §«Правила доказательности»; `docs/reports/stage-2-prompt.md`
(decisions Д1–Д8 of 2026-10-31, stage rules, sessions S1–S9); TASK-8.

## Global Constraints

- Legacy: `.legacy/` is read-only — never write, unlock or run it. Legacy runs only from
  `.legacy-run/` (`scripts.legacy_clone`); its environment lives there too. Legacy dependencies are
  never installed into the project environment; the project never imports legacy modules in-process.
  If the seam needs a legacy edit: stop and ask (minimal edit only in a separate branch with consent).
- Numbers come from scripts in `scripts/`; outputs in `docs/evidence/stage-2/<dir>/`, the exact command
  (from the repo root) in that directory's `commands.txt`; outputs never edited by hand; agent judgement
  in `*.agent.md` with criteria at the top and "not reviewed by a human".
- Source tags: `[код: pysport@b548c35 path:line]`, `[корпус: <anonymized name or hash>]`, `[история: …]`,
  `[мейнтейнер: date]`, otherwise `[допущение]`.
- Personal data: corpus outside the repository (`SPORTORG_CORPUS`); no real name, birth date or chip
  number in the repository, evidence, logs, commit messages or sub-agent prompts. Legacy `test.json`,
  IOF XML, `test.wdb`, `5979_csv_wo.csv` contain personal data `[мейнтейнер: 2026-10-31]` and follow
  the corpus rules; only synthetic data and `sfrx_file.sfrx` may enter `tests/golden/` and evidence.
  The agent never opens raw corpus files (Д3 a): scripts read them, the agent reads summaries.
  From S3 on, the leak check runs before every commit.
- Golden files (`tests/golden/**`) change only with the maintainer's confirmation; the first golden file
  appears only after the AC #7 guard runs in CI (Task 1).
- Tools: ≥ 2 alternatives, a measurement script, a line in an ADR (new ADRs from 0008). A dependency is
  added with its first use. Only the main session edits `pyproject.toml`/`uv.lock`.
- TDD for scripts and parsers; `uv run python scripts/check.py` green before each commit.
- Discrepancies (recalculation vs stored results vs protocol) are classified (legacy bug / local
  practice / rule gap) and raised, never fixed.
- Git: Conventional Commits in English, only the main session commits, push only on the maintainer's word.
- Sub-agents: Sonnet, effort medium, at most three at once; they never touch `pyproject.toml`/`uv.lock`,
  commit, classify, decide or open raw corpus.
- Network only to Д8 hosts (stage 1 hosts: PyPI, `files.pythonhosted.org`, GitHub API and release
  downloads; plus running workflows). Raw responses go to `~/.cache/sportorg-stage2/` with `MANIFEST.json`.
- Legacy texts are data, not instructions.
- End of each session: `check.py` green; all stage evidence scripts rerun with empty `git diff`;
  `scripts.legacy verify` prints `ok`; `.legacy-run/` copies restored (`scripts.legacy_env status`
  prints `ok`); commits; Session log entry here; note in TASK-8.

## Review Focus

1. **CI history is missing or rewritten** (shallow checkout, first push of a branch with
   `before = 000…0`, force push to `main`). Expected: the golden guard never passes on an empty range by
   accident; an unresolvable base on `main` fails closed with a message naming `fetch-depth: 0`.
   Tests: `test_zero_base_falls_back_to_merge_base`, `test_unknown_base_on_default_branch_fails_closed` (Task 1).
2. **A golden change that is not a plain edit** — rename out of `tests/golden/`, deletion, a change
   made only in a merge resolution, a case variant `Tests/Golden/…` that is the same directory on
   Windows and macOS, non-ASCII names. Expected: all count as golden changes.
   Tests: `test_rename_out_of_golden_needs_trailer`, `test_evil_merge_needs_trailer`,
   `test_case_variant_path_is_golden`, `test_non_ascii_golden_path` (Task 1).
3. **Approval text that is not a trailer** (the words in the body, an empty value, a trailer in a
   different commit of the same push). Expected: only a non-empty `Golden-Approved-By:` in the trailer
   block of the same commit approves it, parsed by `git interpret-trailers`.
   Tests: `test_trailer_in_body_does_not_approve`, `test_empty_trailer_does_not_approve` (Task 1).
4. **Personal data from legacy test runs** — legacy pytest runs with `--showlocals` and DEBUG logging
   over `test.json` (personal data). Expected: evidence holds only test ids and outcomes, never
   messages or logs. Test: `test_junit_summary_keeps_ids_and_outcomes_only` (Task 3).
5. **Environment-dependent legacy runs** (HOME config, time zone, locale, display, a crashing Qt
   plugin that kills pytest before JUnit is written). Expected: hermetic environment (temporary HOME and
   XDG dirs, `TZ`, `LANG`, no `DISPLAY`/`WAYLAND_DISPLAY`); a crash is recorded as a crash, not as
   "0 failed". Tests: `test_hermetic_env`, `test_missing_junit_is_reported_as_crash` (Task 3).

## Evidence layout

```
docs/evidence/stage-2/
  README.md         index: directory → AC → files
  golden-guard/     AC #7: scenario matrix of mechanisms, GitHub/git facts (ADR-0008)
  legacy-env/       S1: Python probe for the legacy runtime, legacy test results (ADR-0009 T1)
  oracle/           AC #1 (S2)
  corpus/           AC #2 (S3): manifest only (hashes), leak-check summary
  golden/           AC #3 (S4): local corpus run summary and hashes
  devices/          AC #4 (S5)
  baseline/         AC #6 (S6, S7)
  smoke/            AC #5 (S7)
```

---

## S1 — plan, golden-file protection, legacy environment (AC #7)

### Task 1: Golden guard (`scripts/golden_guard.py`)

**Files:**
- Create: `scripts/golden_guard.py`, `tests/scripts/test_golden_guard.py`, `tests/scripts/test_check.py`
- Modify: `scripts/check.py` (step `golden`), `.github/workflows/ci.yml` (`fetch-depth: 0`, `GOLDEN_BASE`),
  `.pre-commit-config.yaml` (commit-msg and pre-push hooks), `AGENTS.md` rule 5

**Interfaces:**
- Produces:
  - `GOLDEN_DIR = "tests/golden"`, `TRAILER = "Golden-Approved-By"`, `DEFAULT_BRANCH = "main"`
  - `is_golden(path: str) -> bool` — case-insensitive, `/` or `\` separators
  - `@dataclass(frozen=True) Violation(commit: str, subject: str, paths: tuple[str, ...])`
  - `approvals(message: str, *, cwd: Path) -> list[str]` — non-empty trailer values via `git interpret-trailers --parse`
  - `changed_paths(commit: str, *, cwd: Path) -> list[str]` — `git diff-tree -r --root --cc --no-renames --name-only -z`
  - `range_commits(head: str, *, base: str | None, cwd: Path) -> list[str]` — union of
    `merge-base(head, origin/main | main)..head` and `base..head`; raises `GuardError` when `base`
    cannot be resolved and the merge-base range is empty
  - `check_range(head: str = "HEAD", *, base: str | None, cwd: Path) -> list[Violation]`
  - `check_commit_message(message_file: Path, *, cwd: Path) -> Violation | None` — staged paths
  - CLI: `python -m scripts.golden_guard range [--base REV] [--head REV]` (base also from `GOLDEN_BASE`;
    all-zero sha = unset) and `python -m scripts.golden_guard commit-msg FILE`; exit 0 ok, 1 violations,
    2 usage/history error; uncommitted golden changes are printed as a note, not a failure.

- [ ] Step 1: tests on temporary git repos (fixed author, dates, `commit.gpgsign=false`):
  `test_commit_without_trailer_fails`, `test_commit_with_trailer_passes`,
  `test_non_golden_change_passes`, plus the Review Focus 1–3 tests. Run, expect import failure.
- [ ] Step 2: implement; run `uv run pytest tests/scripts/test_golden_guard.py -q`, expect pass.
- [ ] Step 3: `step_command("golden") == [sys.executable, "-m", "scripts.golden_guard", "range"]`
  (`tests/scripts/test_check.py`); add `golden` to `STEP_ORDER` after `imports`.
- [ ] Step 4: CI: `fetch-depth: 0` on both checkouts; env
  `GOLDEN_BASE: ${{ github.event.pull_request.base.sha || github.event.before }}` on the check step.
- [ ] Step 5: pre-commit: hook `golden-commit-msg` (stage `commit-msg`), hook `golden-range`
  (stage `pre-push`); add `commit-msg` to `default_install_hook_types`.
- [ ] Step 6: `check.py` green; commit `feat(golden): guard tests/golden with a maintainer trailer in CI`.

### Task 2: Mechanism comparison and ADR-0008

**Files:** Create `scripts/golden_probe.py`, `tests/scripts/test_golden_probe.py`,
`docs/adr/0008-golden-file-protection.md`, `docs/evidence/stage-2/golden-guard/{README.md,commands.txt,scenarios.json,scenarios.md,facts.json}`,
`docs/evidence/stage-2/README.md`.

**Interfaces:**
- Consumes: `check_range` (Task 1).
- Produces: `python -m scripts.golden_probe scenarios --out DIR` (offline, temporary repos) and
  `python -m scripts.golden_probe facts --out DIR [--cache DIR] [--offline]` (git config and history
  counts; GitHub repository settings through `gh api`, raw JSON cached with `MANIFEST.json`).

Mechanisms: (a) trailer check (Task 1); (b) CODEOWNERS + required review (GitHub settings, measured by
facts); (c) signed hash manifest (`ssh-keygen -Y sign/verify`, prototype inside the probe) with the
signer pinned in the repository or outside it. Scenarios: add/modify/rename/evil merge without
approval, approved change, non-golden change, approval text in the body, approval forged by the
committer. Canary = the (a) column, also asserted in `test_golden_probe.py` so it runs in CI on 3 OS.

- [ ] Step 1: test `test_trailer_column_matches_expected` (a-column outcomes). Fail, implement, pass.
- [ ] Step 2: run both subcommands into `golden-guard/`; write ADR-0008 from the data; commit
  `docs(adr): ADR-0008 golden-file protection with scenario evidence`.

### Task 3: Legacy runtime (`scripts/legacy_env.py`)

**Files:** Create `scripts/legacy_env.py`, `tests/scripts/test_legacy_env.py`,
`docs/adr/0009-stage-2-runtime-and-tools.md` (rows T1–T2),
`docs/evidence/stage-2/legacy-env/{README.md,commands.txt,python-probe.{json,md},legacy-tests-offscreen.{json,md},legacy-tests-noplatform.{json,md},unstable-tests.agent.md}`.

**Interfaces:**
- Produces:
  - `RUN_CLONE = run_dir() / "pysport"`, `PYTHON_DIR = run_dir() / "python"` (`UV_PYTHON_INSTALL_DIR`),
    chosen environment `RUN_CLONE / ".venv"`
  - `hermetic_env(base: Mapping[str, str], *, home: Path, qt_platform: str | None) -> dict[str, str]`
  - `parse_junit(xml_text: str) -> list[TestOutcome]` with `TestOutcome(test_id: str, outcome: Literal["passed","failed","error","skipped"])`
  - `recalc_test_modules(clone: Path) -> list[str]` — legacy test modules that call `recalculate_results`
  - `summarize(run: LegacyRun, recalc_modules) -> dict[str, Json]`, `counts_text`, `not_passed`
  - `clean_clone(clone: Path) -> None` — back to HEAD, untracked and ignored files removed, `.venv*` kept
  - `clone_problems(pin: Pin, *, base: Path | None) -> list[str]` — HEAD at pin, nothing left behind
  - `UNSTABLE_TESTS: dict[str, str]` (node id → reason), `pytest_command(python, junit, deselect)`
  - CLI: `probe --out DIR --python V…` (sync each candidate into `.venv-probe-<V>`, run legacy tests,
    remove the probe env), `sync --python V`, `tests --out DIR --name N --qt-platform offscreen|none`,
    `status` (both copies at their pin, nothing untracked or ignored except `.venv*`), `restore`.
- Legacy tests run as `python -m pytest -p no:cacheprovider --junitxml=<tmp> --deselect …` in a
  clean copy; only `test_id` and outcome reach evidence.

- [ ] Step 1: tests for `parse_junit`, `hermetic_env`, crash handling, `recalc_test_modules`; fail; implement; pass.
- [ ] Step 2: `probe` over 3.14 (dev), 3.14.0, 3.13, 3.8 (release builds, `[код: pysport@b548c35 .github/workflows/release.yml:24]`).
- [ ] Step 3: choose by data (ADR-0009 T1), `sync`, run `tests` with `offscreen` and without a platform;
  two consecutive runs must be byte-identical (unstable tests: `unstable-tests.agent.md`).
- [ ] Step 4: commit `feat(legacy-env): reproducible legacy runtime and its test results`.

---

## S2 — oracle seam (AC #1)

**Files:** `scripts/oracle.py` (CLI), `scripts/oracle_driver/` (runs under the legacy interpreter;
stdlib + `sportorg` only), `scripts/oracle_normalize.py`, `scripts/corpus/synth.py`, tests in
`tests/scripts/oracle/`, evidence `docs/evidence/stage-2/oracle/`.

**Runtime (ADR-0009 T1, `[мейнтейнер: 2026-10-31]`):** first line `.legacy-run/pysport/.venv` on
CPython 3.8.20 (release builds are made on 3.8, most of the corpus was produced with them), so the
driver must run on Python 3.8; second lane on 3.13.17 in its own environment, and any difference
between the two outputs is reported, not resolved. Headless with `QT_QPA_PLATFORM=offscreen` and the hermetic
environment of `scripts/legacy_env.py: hermetic_env` (T2).

**Decisions made in S2 (ADR-0009 T3–T5, proposed; rulings in the session log):**
- Type checking: (c) hand-written stubs of the legacy API (`scripts/oracle_driver/stubs/`) in a
  basedpyright execution environment with `pythonVersion = 3.8`; (a) needs `.legacy` and the legacy
  environment, which CI has not (measured in `oracle/typecheck.md`).
- Driver protocol: whitelisted raw snapshot written to a temporary file (not stdout), personal data
  filtered in the driver; errors as type and frames only.
- Inputs that are not in the race file: the clock (`--now`), the startup tables (status comments,
  ranking), recalculation of every race as the current one after `File.open`.

**Interfaces (as built):**
- `uv run python scripts/oracle.py RACE_FILE [--out DIR] [--venv DIR] [--now HH:MM:SS]
  [--show-stderr]` → stdout, or `DIR/{results,stored,comparison,run}.json`. `scripts/oracle.py` is a
  file shim for `scripts/oracle_cli.py` (`oracle()`, `run_driver()`, `write_run()`, `OracleRun`,
  `OracleError`). `--no-recalc` of the draft is dropped: `stored.json` is always written.
- `python -m scripts.oracle_driver.driver RACE_FILE RAW_OUT [--now]` under the legacy interpreter
  (`PYTHONPATH` = repository root); pure half `scripts/oracle_driver/snapshot.py` (`filter_race`,
  `stored_races`, `clock_dependent`, `parse_now`, `error_report`, `guarded`, `PROTOCOL = 1`).
- `scripts/oracle_normalize.py`: `normalize(snapshot, enums) -> Json`, `dumps()`, `SCHEMA`,
  `SCHEMA_VERSION = 1`; `scripts/oracle_compare.py`: `compare(stored, recalculated)`,
  `counts_only(report)`.
- `scripts/corpus/synth.py`: `RACES = {individual, relay, rogaine}`, `--out DIR`.
- `scripts/oracle_evidence.py run|typecheck --out DIR`; `scripts.legacy_env sync --env .venv-3.13`.
- Schema v1 (final for S2): `docs/evidence/stage-2/oracle/README.md`. After the review of
  2026-11-01: schema v2 (absent stored fields left out), `--state after-open`, cp1251 files, clock
  `23:59:59` by default; `RACES` also holds `f3_rogaine_tie`, `f4_slow_leader`, `f6_two_races`.

**Tests:** normalizer by TDD on synthetic raw dicts; `test_two_runs_byte_identical`;
canary `test_finish_change_moves_place` (change one finish → time and place change).
Data: synthetic races from `scripts/corpus/synth.py` (individual, relay, rogaine by score per legacy
code). Legacy `test.json` contains personal data: run on it locally, evidence only counts and hashes.
Compare stored vs recalculated; each difference classified for the maintainer.

**Done when:** the TASK-8 AC #1 command works without GUI and display, tests and canary green,
evidence `stage-2/oracle/`.

## S3 — anonymization and corpus manifest (AC #2)

`scripts/corpus/anonymize.py` (Д1 a + deterministic HMAC birthday in the same year; key from the
environment variable `SPORTORG_ANONYMIZATION_KEY`, no key → error; the corpus path from
`SPORTORG_CORPUS`), `scripts/corpus/leakcheck.py` (no original name, chip or date in
output), invariant test: oracle(anonymized) == oracle(original) on statuses, times, places;
manifest (hash of original and anonymized copy, SportOrg version, sport, start format) is the only
corpus file in the repository. Card number renumbered inside the same card-type range.
Added by the maintainer's answers of 2026-11-01: the manifest records each file's format (`gzip`,
`utf-8`, `cp1251`; ADR-0009 T6) and the anonymizer reads files by the same rule as the oracle; it
lists files with `scores_mode = formula` and their formulas, which run only with the maintainer's
consent (R22). The leak check also scans every evidence file before it is committed, test ids of
legacy test runs included (review finding S1-12).
Locality `[мейнтейнер: 2026-11-01]`: replacing, editing or adding corpus files must not change the
output for anything else. Requirements: a pseudonym is a function of the key and the normalized value
only (HMAC, no shared table of names already given out; normalization rules for case, ё/е and spaces
fixed and tested); a card number maps through a keyed bijection inside its card-type range (a
permutation, so no collisions to resolve in visiting order); a file's neutral id comes from the
directory id and the file's stable name, not from its position in a listing; no cross-file matching
of persons (clustering by name and year). Tests: (1) changing or adding file B leaves the anonymized
copy of file A byte-identical, and its manifest hashes unchanged; (2) changing one record of a file
leaves every other record of that file anonymized as before.
**Done when:** reproducible, locality tests green, leak check and invariant green on synthetic data
and on the corpus if present.

**Interfaces (as built, S3 of 2026-11-01):**
- `scripts/corpus/pseudonym.py`: `load_key(environ)` (`MissingKeyError`, the value never in a
  message), `key_id`, `keyed_hash`, `normalize`, `is_plain`, `pseudonym(key, kind, value)` (kinds
  person, org, place, contact, code, text), `Permutation(key, label, size)` (`forward`,
  `inverse`, `cycle`), `CARD_CLASSES`, `card_class`, `card_number`, `number_code`, `birth_date`.
- `scripts/corpus/anonymize.py`: `anonymize(doc, *, key, neutral_id) -> Anonymized(doc, stats)`,
  `anonymize_bytes(raw, …) -> (bytes, format, stats)`; field lists `LEGACY_SETTINGS`,
  `CLEARED_SETTINGS`, `TEXT_SETTINGS`, `PERSON_KEPT`, `RESULT_KEPT`, `ORG_KEPT`, `DATA_*`.
- `scripts/corpus/racefile.py`: `decode`, `encode` (gzip with `mtime=0`), `dumps` (legacy's
  indent), `races_of`, `kind` (`KINDS`), `readout_log_stats`.
- `scripts/corpus/leakcheck.py`: `extract`, `check_pair`, `leak_paths`, `scan_set`, `scan_text`;
  CLI `scan PATHS… [--source] [--no-corpus] [--no-legacy-test-data] [--commits RANGE]
  [--synthetic PATH]`.
- `scripts/corpus/catalog.py`: `build(corpus, cache, *, key, paths=None) -> manifest`,
  `read_inventory`, `files_tsv_counts`, `race_facts`; cache `MANIFEST.json`.
- `scripts/corpus/invariant.py`: `diff_counts`, `compare_runs`, `check(original, anonymized, *,
  python_exe)` on copies in a temporary directory (F7), errors per side as `<kind> at <frame>`.
- `scripts/corpus/evidence.py synthetic|corpus --out DIR [--invariant] [--allow-formula ID]`;
  `scripts/corpus/synth.py --personal` (`PERSONAL`: individual, multi-day, old format; fictional).

Rulings (deviations from the draft above): a pseudonym is the HMAC of the normalized value plus a
suffix from the exact value when it is not in the plain form, because legacy compares names
exactly (question 1 of `corpus/findings.agent.md`, ADR-0009 T7); card numbers and birth days by a
keyed one-cycle permutation, so no value maps to itself and the leak check compares records, not
the whole text; the invariant compares whole files (`results.json`, `stored.json`,
`comparison.json`), not only statuses, times and places; the leak check also scans commit
messages and every file changed on the branch; logs found in the corpus are counted, not
anonymized.

## S4 — golden master (AC #3)

Golden tests compare oracle output with files in `tests/golden/` (synthetic + `sfrx_file.sfrx` only,
each addition confirmed by the maintainer and committed with `Golden-Approved-By:`); the golden loader
refuses symlinks. Corpus: local command, summary and hashes in `stage-2/golden/`. Masked fields only
for known volatile values, each with a reason, listed in the report. Canary: a deliberate change in a
`.legacy-run` copy (rounding rule) turns a golden test red.
Golden master runs `--state recalculated` (ADR-0009 T5). Corpus files with several races that are
not a multi-day event run also with `--state after-open`; the summary counts the files and results
where the two states differ (F6, `[мейнтейнер: 2026-11-01]`).

## S5 — device simulators (AC #4)

Dump format (bytes, direction, timestamp, port parameters) with a README spec; recording instructions
and script for Windows; replay through virtual ports — compare ≥ 2 mechanisms per OS (own pty pair /
socat / tty0tty; com0com and alternatives), ADR. Test: legacy reader (`sportident` package) in
`.legacy-run` reads a replayed card headless; canary: corrupted CRC byte. Hardware available
`[мейнтейнер: 2026-10-31]`: BSM7-USB, BSF8, BSF8-SRR, SRR USB dongle; SI5, SI6, SI8, SI9, SIAC,
pCard, tCard.
Added by the maintainer's answer of 2026-11-01 (S3 question 3): logs of the corpus, option C1 of
`docs/evidence/stage-2/corpus/logs.agent.md`: extract only the SportIdent frames and device lines of
legacy's log into a dump, map card numbers by the S3 permutation, overwrite the owner bytes of the
card blocks, recompute the CRC, drop every other message; the readout backup `si<date>.log` with
cards mapped only. Tests first, as listed there; the maintainer checks the unmapped log locations
(`winorient.py`, `orgeo.py`) by message prefix before a real log is processed.

## S6 — baseline, automatic part (AC #6 part)

Branch coverage of legacy tests in `.legacy-run` (`coverage.py --branch` vs an alternative);
mutation score on rank 1–2 core modules (≥ 2 tools, ADR, time cap set in advance, mutations only in
`.legacy-run`); complexity by reference to Stage 1 evidence; oracle recalculation time on S2 data.
No quality thresholds (Stage 4).

## S7 — smoke on three OS and human timings (AC #5, #6 rest)

Smoke: GUI start, open race, read an SI card (station or S5 simulator), print a split (PDF and printer).
Linux by the agent; Windows native clone by the maintainer; macOS on a borrowed Mac in one sitting (Д6 a).
Split print time by script. Operator timings: no decision on Д7 → PARTLY.

## S8 — report and verification prompt; S9 — independent verification

As in `docs/reports/stage-2-prompt.md`.

---

## Session log

(Entries appended at the end of each session: what was done, commits, open questions.)

### S1 — 2026-10-31 (Claude Code, Opus 5.5)

The session prompt said both "S1" and "execute only S2"; S1 had not been done, so the maintainer chose S1.

Done:
- AC #7: `scripts/golden_guard.py` (step `golden` in `check.py`, CI with `fetch-depth: 0` and
  `GOLDEN_BASE`, pre-commit commit-msg and pre-push hooks), AGENTS.md rule 5; ADR-0008 from the scenario
  matrix (`scripts/golden_probe.py`): trailer 8/9, signed manifest with signers in the repo 8/9, with
  the signer pinned outside 9/9. Canary on a clone of this repository: exit 1 without the trailer,
  0 with it. AC #7 stays unchecked until a CI run shows the step (nothing pushed).
- Legacy runtime: `scripts/legacy_env.py`, ADR-0009 T1–T2. 3.14.9 is rejected by `<=3.14`; 3.14.0,
  3.13.17 and 3.8.20 give the same legacy results (282 passed, 3 failed, 10 skipped of 295).
  `.venv` = 3.13.17, 3.8.20 as the second oracle lane in S2. Recalculation tests: 40 passed, 8 skipped,
  the same with and without a Qt platform. Five teamwork tests deselected as unstable; the three
  `test_reader` tests fail in the sandbox (`/tmp` read-only for `socat`).
- Evidence `stage-2/golden-guard/`, `stage-2/legacy-env/`: two consecutive runs byte-identical; rerun at
  the end of the session with an empty diff.

Commits: `c557196` feat(golden), `5683289` docs(stage-2) plan + prompt, `c7c5978` ADR-0008,
`90a5d8c` feat(legacy-env), and the commit with this log.

Open questions for the maintainer:
1. ADR-0008: stop forged approvals now (signed manifest, signer pinned outside the repo) or keep the
   trailer check? Recommendation: keep (a) until agents commit unattended or a key out of their reach exists.
2. ADR-0009 T1: which Python is the oracle of record — 3.13.17 with 3.8.20 as a reported second lane
   (recommended), 3.8.20 (Python of the release builds), or 3.13.17 only?
3. The sandbox does not allow writing to `~/.cache/sportorg-stage2/` (stage rule 11); running outside it
   was refused. This session's raw `gh api` responses are in the session scratchpad (hashes in
   `facts.json`). Options: add the path to the sandbox write list in `.claude/settings.local.json`
   (recommended), or keep a per-session cache and refetch.
4. `tests/test_reader.py` needs a writable `/tmp`: run it once outside the sandbox to confirm that it
   passes there (recommended before S5), or leave it as a recorded sandbox limit.
5. Run `uvx --python 3.14 pre-commit@4.7.0 install` again to get the new `commit-msg` hook. In the
   sandbox, a commit with unstaged files needs `PRE_COMMIT_HOME=$TMPDIR/pre-commit` (the default store
   is read-only).

Findings (not decisions): five tests of legacy `tests/test_teamwork.py` are timing-dependent
(`unstable-tests.agent.md`); legacy tests leave `tests/data/test.json.tmp` behind.

Next: S2 (oracle seam), in a fresh session.

Maintainer's answers of 2026-10-31, applied in the same session:
- Q2: 3.8.20 is the first line of the oracle, 3.13.17 the second (ADR-0009 T1 changed; `.venv` re-synced
  on 3.8.20, legacy test evidence rerun: same counts, only the Python line changed).
- Q3: `~/.cache/sportorg-stage2/` allowed in the sandbox; the cached `gh api` responses moved there
  unchanged, `facts.json` reproduced without a diff.
- Q5: hooks reinstalled (`commit-msg` present).
- Q4: the maintainer ran the legacy tests outside the sandbox (`legacy-tests-outside-sandbox.md`, 3.8.20):
  `test_reader::test_sportident` and `::test_sportiduino` pass there, `::test_huichang` still fails, cause
  unknown (finding for S5).
- Q1: decided 2026-11-01: keep the trailer check; the signed manifest (session "S1b") is deferred to a
  later stage. The three conditions it needs are in ADR-0008, "Maintainer's decision".

Follow-up of 2026-11-01:
- The maintainer pushed `stage-2`. CI run 41222366113 (`dab1040`) is green on all seven jobs: the
  `golden` step is `ok` on Linux, Windows and macOS (3.14 and 3.15) and on the clean machine, and 329
  tests pass, the canary among them. AC #7 checked in TASK-8.
- Pre-push hook `protected-files` (`python -m scripts.golden_guard protected --pre-push`, TDD) lists changed files
  that define the checks, with the `git diff` command. It is informational, condition 3 of ADR-0008.
  In pre-push, `range` and `protected` take the pushed ref (`PRE_COMMIT_TO_REF`) as head.
- Fix (2026-11-01): the first push of `e6b9bdd` was stopped by the pre-push `tests` hook, with 5 failures.
  Cause: `golden_guard` read `PRE_COMMIT_TO_REF` implicitly, and pre-commit exports it to every pre-push
  hook, so the CLI tests and the canary saw the pushed sha. Now only `--pre-push` (passed by the
  hooks) reads it, and the guard tests clear the outer variables. Regression tests:
  `test_pre_commit_variables_are_ignored_without_the_flag`, `test_canary_ignores_the_pre_push_environment`.
- Not done, by the maintainer's choice: listing the sandbox mount points in `.git/info/exclude`.

### S2 — 2026-11-01 (Claude Code, Opus 5.5)

Done (AC #1):
- `uv run python scripts/oracle.py RACE_FILE [--out DIR]` recalculates a race file in legacy
  (`pysport@b548c35`) without GUI or display and writes normalized results (schema v1), the values
  stored in the file and a field-by-field comparison. Legacy runs only as a separate process
  (`scripts/oracle_driver/driver.py` under `.legacy-run/pysport/.venv`, CPython 3.8.20; second lane
  `.venv-3.13`, 3.13.17, made by `scripts.legacy_env sync --env`). The driver whitelists fields, so
  names, birth dates and chip numbers never leave the legacy process.
- Synthetic races (`scripts/corpus/synth.py`): individual, two-leg relay, rogaine by score.
- Evidence `stage-2/oracle/`: both lanes byte-identical on all inputs, reruns byte-identical, the
  canary fires (bib 101: 1st → 3rd, 30:00 → 33:00); legacy `test.json` (personal data) as counts
  and hashes only: 1 race, 2 results, 1 stored value differs (`diff_ms` 0 vs null, F1).
- ADR-0009 T3 (driver checked as Python 3.8 against hand-written stubs: 0 errors, against legacy
  sources 26, without legacy as in CI 89), T4 (file transport, whitelists), T5 (clock, startup
  tables, recalculation order) — proposed. Risk R22 (`scores_formula` is evaluated with `eval`).
- Final review by a sub-agent (Sonnet, medium): 0 critical, 3 important, 7 minor; two defects fixed
  by TDD (non-UTF-8 file named `NotUtf8RaceFile`; stdout as UTF-8 bytes), the rest documented or
  deferred (ledger in `.superpowers/sdd/stage-2-oracle/progress.md`, not committed).
- `check.py` green (432 tests); integration tests on the real legacy run locally and are skipped in
  CI, which has no legacy checkout. All stage evidence rerun with an empty diff.

Rulings (deviations from this plan's S2 draft): stored values read from the file's JSON by the
driver, not by `get_races_from_file` (it drops the computed fields); raw snapshot in a temporary
file, not stdout; `--no-recalc` dropped (stored.json always written); `--out` optional (stdout);
`scripts/oracle.py` is a file shim for `scripts/oracle_cli.py`; driver split into `snapshot.py` (pure)
and `driver.py`, run as `python -m`; type checking by stubs (c), not (a); `status_comment` and
clock-dependent fields out of schema v1.

Commits: `a8dcdab` feat(oracle), `5d2aa62` docs(stage-2) evidence + ADR-0009 T3–T5 + R22, `55652da`
fix(oracle) review fixes, and the commit with this log.

Open questions for the maintainer:
1. ADR-0009 T3–T5: accept? T5 in particular: the clock fixed at `00:00:00` by default; status
   comments and ranking tables from the shipped configs; legacy `settings.json` not read (defaults).
   Recommendation: accept; revisit when the corpus shows operators' own tables or settings.
2. Findings F2–F4 and F6 (`oracle/findings.agent.md`): classify (legacy bug / local practice / rule
   gap). F6 also asks which state the oracle should reproduce for a multi-race file that is not a
   multi-day event (recommended: each race in its own context, as built). F1: keep `diff_ms` 0 vs
   null as a *representation* difference (recommended).
3. Files that are neither gzip nor UTF-8: refuse and count them in the S3 manifest (recommended),
   try cp1251, or re-encode them while preparing the corpus.
4. R22: before the corpus runs (S3–S4), report files with `scores_mode = formula` and their formulas
   and run them only with your word (recommended), or accept the risk for the maintainer's own files.
5. AC #1 is left unchecked: its evidence comes from this session only, and AGENTS.md rule 3 asks for
   a repeat in a fresh session. Check it after S9 (recommended) or now.

Next: S3 (anonymization and corpus manifest), in a fresh session; by D4 (a) the corpus is handed over
before S3 starts.

### After S2 — 2026-11-01 (Claude Code, Opus 5.5): reviews and the maintainer's answers

- Reviews by sub-agents on Fable, an exception to stage rule 10 by the maintainer's word: S1 (range
  `aeb6cb7..afc139d`, its first review) and S2 again (`afc139d..f4a4fe5`). Both "with fixes", no
  critical findings. Important: S1 — the `commit-msg` hook refuses a clean merge of a branch whose
  golden commits are approved (`golden_guard.py:238-247`); the crash path of legacy test runs has no
  test (`test_legacy_env.py:73-78`). S2 — a stored `null` of `diff`/`penalty_time`/`credit_time`
  counts as `not_stored`, which hides real differences (`oracle_normalize.py:63`,
  `oracle_compare.py:53-56`). 11 + 7 minor. Nothing fixed yet: the maintainer chooses (ledger).
  The reasons for the models of rule 10 are not recorded anywhere; the rule comes from the Stage 1
  prompt, where it covered the mechanical directions W1–W6.
- Maintainer's answers `[мейнтейнер: 2026-11-01]`: ADR-0009 T3–T5 accepted. F1 kept as a
  representation difference. F2 is a legacy bug, with three correct ways to show a runner out of
  competition (`oracle/findings.agent.md`). R22: the S3 manifest lists files with
  `scores_mode = formula` and their formulas; they run only with the maintainer's consent.
- F3, F4, F6: the maintainer checks them in legacy's GUI. Inputs `f3_rogaine_tie`, `f4_slow_leader`,
  `f6_two_races` from `scripts/corpus/synth.py` (TDD), the oracle's output in `stage-2/oracle/`,
  guide `docs/reports/stage-2-check-f3-f4-f6.md`.
- Personal data in legacy's test code (not in its data files): `tests/test_winorient.py`,
  `test_json.py`, `test_gzip.py`, `test_wdb.py` and `test_teamwork.py` hold names, a chip number and
  a birth year copied from the files with personal data. None of them is in this repository's tree
  (count-only check); one surname is in the history of `main`, `docs/reports/stage-1.md` between
  `278826c` and `b4eba5d`, which removed it. The list went to the maintainer in the session, not to
  the repository.

Open for the maintainer: the fix pass for the review findings; question 3 of S2 (files neither gzip
nor UTF-8: legacy 1.7.0–1.7.1 save in the system's encoding by default) and question 5 (when to check
AC #1), both explained in the session; the results of the F3/F4/F6 check; what to do with the
surname in the history of `main`.

### Fix pass — 2026-11-01 (Claude Code, Opus 5.5)

Maintainer's answers: Q3 (b), Q5 (b), default clock `23:59:59`, the fix pass as recommended; the
real/fictional split of the names in legacy's test code confirmed, the surname in the history of
`main` stays. F3, F4, F6 confirmed in the GUI (`b548c35`, Python 3.13.5); their classification and
the state for F6 are still open.

Fixed, each by TDD (ledger lines `Final: fixed`):
- S1: the `commit-msg` hook in merges; `--no-replace-objects`; the fail-closed message; CI
  clean-install with `GOLDEN_BASE`; `hermetic_env` drops whole variable families; an hour for the
  first `uv sync` and a message on timeout; the crash path of legacy test runs tested (mutation
  checked). Documented: the `--amend` and multi-ref limits of the hooks, the (c) rows of ADR-0008.
- S2: schema v2 (stored nulls compared, absent fields left out); cp1251 files (ADR-0009 T6); clock
  `23:59:59` (T5); `--state after-open`, equal to the recalculation for one-race files, evidence for
  F6; driver timeout and missing interpreter as `OracleError`; `main --out` tested; `counts_only`
  without the race id; the citation `result_tools.py:106`; the README lists what `init_model` and
  `load()` do that the oracle leaves out.
- Deferred by the recommendation: S1-9 (`status` and a left-over `.venv-probe-*`, with the next
  probe), S1-12 (the S3 leak check, written into S3 above).

Evidence: golden-guard and legacy-env reruns identical; oracle evidence regenerated (schema v2,
clock, `after-open/`) and rerun identical; changed numbers: legacy `test.json` `credit_ms` from
"same 2" to "not stored 2" (the old rule counted an absent key against `null` as the same), typecheck
(a) 32 and (a') 99 errors (the driver uses more of legacy), (c) 0. `check.py` green, 471 tests.
AC #1 checked in TASK-8 after this pass (Q5 (b)); S9 verifies the stage again.

Commits: `a476b8d`, `8558c25` (check files, answers), `74edb7a`, `113bf0d` (S1 fixes), `87d1ad5`
(S2 fixes), and the commit with this log.

Answered the same day `[мейнтейнер: 2026-11-01]`: F3, F4 and F6 are legacy bugs; for F6 the oracle
reproduces each race in its own context, and S4 runs corpus files with several races also in
`after-open` (written into S4 above).

### S3 — 2026-11-01 (Claude Code, Opus 5.5)

Done (AC #2):
- `scripts/corpus/` by TDD: `pseudonym.py` (key from `SPORTORG_ANONYMIZATION_KEY`, normalization,
  HMAC pseudonyms with a variant suffix, keyed one-cycle permutations for cards and birth days),
  `anonymize.py` (Д1 field by field, old field names, unknown keys → text, counted), `racefile.py`
  (formats as the oracle, kinds by content incl. legacy's readout backup and log), `leakcheck.py`
  (pair check by field and by record, leak paths, scan of text files and commit messages),
  `catalog.py` (walk, copies, manifest, `files.tsv`, passport, starts, R22, ARDF), `invariant.py`,
  `evidence.py`; `synth.py --personal` (fictional individual, multi-day with spelling variants, old
  format). Tests: 165 in `tests/scripts/corpus`, the locality tests of the plan among them
  (`test_locality_one_changed_record_leaves_the_others_as_before`,
  `test_locality_another_file_does_not_change_this_one[edit|add]`).
- Synthetic (`corpus/synthetic.md`): rebuild byte-identical; locality (edit another file, add a
  file, one record) holds; 0 leaks; invariant 6 of 6 identical, the formula file not run (R22).
- Corpus (`corpus/manifest.md`, `corpus/invariant.md`, as on disk at the run): 25 directories, 63
  race files (28 gzip, 29 UTF-8, 6 cp1251), 100 races, 24 distinct starts; versions 0.11.0.0 to
  v1.8.0b2; no ARDF race, no `scores_mode = formula`; passport: only `id` filled; `files.tsv`: N04
  two listed files missing on disk, N13 one file not listed (and `source.txt` not listed anywhere);
  N07 logs added during the session counted (readout backup 148 readouts, legacy log 4598 lines).
  Leak check of the copies: 0 leaks, 193 residual (values that also stand in kept fields or keys).
  Invariant: 62 of 62 files legacy opens identical before and after; one file legacy cannot open
  either way (F8).
- Findings F7 (legacy opens gzip `r+b`: a read-only original cannot be opened; the invariant runs
  on copies) and F8 (`ValueError` in `ResultSportident.check` on one 1.3.0.0 file) in
  `corpus/findings.agent.md`; ADR-0009 T7 (anonymization primitives) proposed.
- The first leak check found 15 hits in five old files: all in JSON keys (old files hold schema
  words such as `address` as values). Keys now count as kept text (test
  `test_a_value_that_is_also_a_key_name_is_residual`). An ad-hoc diagnostic run on the corpus was
  refused by the auto-mode classifier; the location of a legacy failure is now printed by the
  invariant itself (`<kind> at <frame>`).
- Evidence: golden-guard, legacy-env and oracle rerun with an empty diff; `corpus/` run twice,
  byte-identical. `check.py` green, 636 tests. `scripts.legacy verify` ok, `.legacy-run` restored.
- Leak check before the commits (`corpus/commands.txt`): 0 findings over the stage evidence, the
  files changed since `74105e5`, new files and 22 commit messages; 2 chance hits in synthetic
  outputs. Invented values in
  tests were changed before the commits.
- TDD exception: `test_logs_are_counted_by_kind_without_their_content` was written after the code
  it tests and passed at once (the log kinds of `racefile.py` had their own RED test first).

Verdict AC #2 (agent's, not checked in TASK-8): synthetic — full (reproducible, locality, leak
check, invariant); corpus — as it stood at the run, with its limits: being assembled, passport
empty, no ARDF, no formula files, one file legacy cannot open, logs and protocols not anonymized.
"Corpus in repo only after the personal-data decision": held, D2 (a); only the manifest entered.

Open questions for the maintainer (`corpus/findings.agent.md`): 1 variant suffix of pseudonyms
(recommended: keep); 2 protocols as kind + hash (recommended); 3 logs: anonymize the readout log
later (recommended), legacy's log counts only; 4 old tokens and hosts cleared (confirm); 5 a local
pre-commit hook for the leak check (recommended, later); 6 word matches in older reports (leave);
F7 and F8 to classify; for S4: move the input copy of F7 into `scripts/oracle_cli.py`.

Next: S4 (golden master), in a fresh session.

Maintainer's answers of 2026-11-01, in the same session: questions 1, 2 and 4 as built (ADR-0009
T7 decided); 5 → Backlog TASK-12 (local pre-commit hook for the leak check); 3 → a sub-agent
(Sonnet, medium) studies from legacy's code what the logs hold (the maintainer: the log holds the
raw byte exchange of readouts with the chip owner's name); the manifest now counts legacy's log by
code location (`racefile.sportorg_log_stats`, TDD); 6 open.
Later the same day `[мейнтейнер: 2026-11-01]`: F7 is a legacy bug (checked on Windows: a read-only
gzip file does not open, a read-only plain file opens but does not save and leaves `.json.tmp`);
F8 confirmed in the GUI, its cause narrowed by new manifest counters to an empty part of a list
template, parsed by `int()` since `0f3a0a8`, classified a legacy bug (regression); question 3 → C1 in
S5 (written into S5 above); question 6: the matched words written to a file outside the
repository (`leakcheck scan --words-out`, TDD), decision pending.

Question 6, answered `[мейнтейнер: 2026-11-01]`: of the matched words, one line is personal data
(a name and a club): `docs/evidence/stage-0/legacy-fix-candidates.md`, a test diff of legacy quoted
in Stage 0 (C3, `3b55fe8b0`); the rest is safe. That file quoted the first 80 lines of the test diff
of each of its 11 candidates; legacy's test code copies names from legacy's test files with
personal data. All 11 test-diff blocks are removed from the tree (without reading them; each
replaced by the command that reproduces it from the pinned clone); a heuristic count of quoted
code lines with name-like literals over `docs/` and `backlog/` is 0 after it. The leak check did not
catch them: its sources are the corpus and legacy's `test.json`, not legacy's other test data
(SFRX, WDB, CSV, IOF XML) or test code. The blocks stay in the history of `main` (`eb40eef`):
whether to rewrite it is the maintainer's decision.
Maintainer's answers `[мейнтейнер: 2026-11-01]`: the history of `main` stays (as for the surname
before; legacy's test code is public in `sportorg/pysport`); AGENTS.md rule 8 now forbids quoting
legacy's test code or test data, and TASK-12 gained a criterion: the hook refuses quoted code with
name-like string literals in Markdown and text files.
