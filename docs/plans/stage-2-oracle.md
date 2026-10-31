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

**Decisions to make at the start of S2 (record in ADR-0009):**
- How the driver is type-checked: (a) a basedpyright `executionEnvironments` entry for
  `scripts/oracle_driver` with `extraPaths = [".legacy/pysport"]` and its Python, rule relaxations
  listed with reasons; (b) exclude the driver and keep it under 100 lines with its own tests run
  in the legacy env. Recommendation: (a) — nothing leaves the checker silently.
- Driver protocol: raw JSON of the legacy objects on stdout (`Result.to_dict()` fields plus computed
  `get_result_otime()`), normalization in project code.

**Interfaces:**
- `uv run python scripts/oracle.py <race-file> --out <dir> [--no-recalc]` → `<dir>/results.json`
  (normalized) and `<dir>/stored.json` (values stored in the file, read with
  `get_races_from_file` — `load()` already recalculates `[код: pysport@b548c35 sportorg/modules/backup/json.py:34-47]`).
- Recalculation: set the race as current (`new_event`, `set_current_race_index`) because
  `_check_all` uses the global race `[код: pysport@b548c35 sportorg/models/result/result_tools.py:105]`,
  then `recalculate_results(race_object=…)`.
- Normalized schema (version 1, refine in S2 and copy into the evidence README): per race
  `{race_id, sport/race type, results:[{person_id (uuid from file), result_id, group, bib, status
  (ResultStatus name), time_ms, place, scores, splits:[{code, time_ms, leg_ms, is_correct}]}]}`;
  canonical order: group name, place (0 = last), person_id; times in integer milliseconds; no names,
  birth dates or chip numbers in the output.

**Tests:** normalizer by TDD on synthetic raw dicts; `test_two_runs_byte_identical`;
canary `test_finish_change_moves_place` (change one finish → time and place change).
Data: synthetic races from `scripts/corpus/synth.py` (individual, relay, rogaine by score per legacy
code). Legacy `test.json` contains personal data: run on it locally, evidence only counts and hashes.
Compare stored vs recalculated; each difference classified for the maintainer.

**Done when:** the TASK-8 AC #1 command works without GUI and display, tests and canary green,
evidence `stage-2/oracle/`.

## S3 — anonymization and corpus manifest (AC #2)

`scripts/corpus/anonymize.py` (Д1 a + deterministic HMAC birthday in the same year; key from an
environment variable, no key → error), `scripts/corpus/leakcheck.py` (no original name, chip or date in
output), invariant test: oracle(anonymized) == oracle(original) on statuses, times, places;
manifest (hash of original and anonymized copy, SportOrg version, sport, start format) is the only
corpus file in the repository. Card number renumbered inside the same card-type range.
**Done when:** reproducible, leak check and invariant green on synthetic data and on the corpus if present.

## S4 — golden master (AC #3)

Golden tests compare oracle output with files in `tests/golden/` (synthetic + `sfrx_file.sfrx` only,
each addition confirmed by the maintainer and committed with `Golden-Approved-By:`); the golden loader
refuses symlinks. Corpus: local command, summary and hashes in `stage-2/golden/`. Masked fields only
for known volatile values, each with a reason, listed in the report. Canary: a deliberate change in a
`.legacy-run` copy (rounding rule) turns a golden test red.

## S5 — device simulators (AC #4)

Dump format (bytes, direction, timestamp, port parameters) with a README spec; recording instructions
and script for Windows; replay through virtual ports — compare ≥ 2 mechanisms per OS (own pty pair /
socat / tty0tty; com0com and alternatives), ADR. Test: legacy reader (`sportident` package) in
`.legacy-run` reads a replayed card headless; canary: corrupted CRC byte. Hardware available
`[мейнтейнер: 2026-10-31]`: BSM7-USB, BSF8, BSF8-SRR, SRR USB dongle; SI5, SI6, SI8, SI9, SIAC,
pCard, tCard.

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
- Q1: explanation asked for; still open. Q4: instruction given for a run of the legacy tests outside the
  sandbox (`--name legacy-tests-outside-sandbox`); its result is brought to S2.
