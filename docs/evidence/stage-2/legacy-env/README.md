# Legacy runtime (Stage 2, S1; ADR-0009 T1–T2)

Every `.json`/`.md` file except `*.agent.md` is output of `scripts/legacy_env.py`; the commands are in
`commands.txt`. Legacy runs only in `.legacy-run/pysport` (writable copy at `pysport@b548c35`) with its
own lock file; managed Pythons are in `.legacy-run/python`.

| File | What it shows |
|---|---|
| `python-probe.md`, `.json` | candidates 3.14 (resolves to 3.14.9), 3.14.0, 3.13, 3.8: `uv sync --frozen --extra gui` result and legacy test counts per candidate, ids of tests that did not pass |
| `legacy-tests-offscreen.md`, `.json` | legacy tests in `.venv` (3.8.20, first line of the oracle by the maintainer's decision of 2026-10-31), `QT_QPA_PLATFORM=offscreen`, no display: every test id and outcome; recalculation tests separately |
| `legacy-tests-noplatform.md`, `.json` | the same without `QT_QPA_PLATFORM` |
| `legacy-tests-outside-sandbox.md`, `.json` | the `offscreen` run made by the maintainer outside the sandbox (2026-10-31, one run): 284 passed, 1 failed, 10 skipped of 295; differs from the sandbox run only in `test_reader::test_sportident` and `::test_sportiduino`, which pass there |
| `unstable-tests.agent.md` | agent observation: which legacy tests change outcome between identical runs and why they are deselected; why `test_reader` fails in the sandbox |

How a legacy test run is made hermetic (`scripts/legacy_env.py`):
- temporary HOME and XDG directories, `TZ=UTC`, `LANG=LC_ALL=C.UTF-8`, `PYTHONHASHSEED=0`,
  `PYTHONDONTWRITEBYTECODE=1`, no `DISPLAY`, `WAYLAND_DISPLAY`, `VIRTUAL_ENV`, `PYTHONPATH`;
- templates from `.legacy-run/templates/ru` (`SPORTORG_TEMPLATES_PATH`);
- before pytest, `python -m sportorg.language` compiles the translations, as legacy's `poe test` does;
- the copy is cleaned back to its pin before and after each run (environments `.venv*` are kept);
- the five unstable tests (`deselected` in each output) are not run;
- legacy's console output (it uses `--showlocals` over data with personal data) is discarded; only
  JUnit test ids and outcomes are kept.

Results depend on the environment: inside the Claude Code sandbox `/tmp` is read-only, so the three
`tests/test_reader.py` tests fail. Outside the sandbox (`legacy-tests-outside-sandbox.md`) two of them
pass; `test_huichang` still fails, for a reason not yet known (messages are not kept; see ADR-0009,
"Environment limits found").

End of a session: `uv run python -m scripts.legacy_env status` prints
`ok: pysport@…, templates@… clean in .legacy-run`; `restore` brings the copies back if not.

Personal data check: parametrized test ids contain names such as "Ivanov Ivan Ivanovich" and
"Sidorov Ivan Petrovich" and the numbers "1993"/"4651993". They are literals of legacy test code
`[код: pysport@b548c35 tests/test_memory_model.py:21-45]`, stock placeholder names, not values from
`tests/data/` `[допущение: not real people]`.
