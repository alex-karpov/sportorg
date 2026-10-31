# ADR-0009: Stage 2 runtime and tools

- Status: accepted (Stage 2, S1) for T1–T2; T1 decided by the maintainer on 2026-10-31; later
  sessions of Stage 2 add rows
- Date: 2026-10-31
- Scope: runtimes and tools that run or measure the pinned legacy (`pysport@b548c35`) for Backlog
  TASK-8. Brief rule «Как выбирать инструменты»: ≥ 2 alternatives, data from a script, overlaps
  counted once. None of these ships with the product.
- Data: `docs/evidence/stage-2/legacy-env/` (commands in `commands.txt`), WSL2 Ubuntu inside the
  Claude Code sandbox, uv 0.13.5.

| # | Need | Options | Decision | Data / why | Revisit when |
|---|---|---|---|---|---|
| T1 | Python of the legacy runtime `.legacy-run/pysport/.venv` (oracle, legacy tests, later coverage and mutation) | (a) 3.14.9, the latest 3.14 and the line of the project's Python (ADR-0001); (b) 3.14.0, the only 3.14 that satisfies legacy `requires-python = ">=3.8.1,<=3.14"` `[код: pysport@b548c35 pyproject.toml:6]`; (c) 3.13.17, the latest 3.13; (d) 3.8.20, the Python of legacy's release builds `[код: pysport@b548c35 .github/workflows/release.yml:24]` (legacy CI tests 3.8 and 3.14 `[код: pysport@b548c35 .github/workflows/check.yml:37,61]`); (e) change legacy `requires-python` — excluded, legacy is read-only (AGENTS.md rule 1) | **(d)** for `.venv`, the first line of the oracle; **(c)** as the second lane `[мейнтейнер: 2026-10-31]`: release builds are made on 3.8, and most of the corpus was produced with them. (The agent had proposed the reverse; the reasons are kept in the next column.) | `python-probe.md`: (a) `uv sync --frozen` exits 2 ("resolved to Python 3.14.9, which is incompatible"), which confirms the PEP 440 trap of the stage prompt. (b), (c) and (d) sync and give the same legacy test outcomes: 282 passed, 3 failed, 10 skipped of 295 (5 unstable tests deselected, T2). Support (`docs/evidence/stage-0/endoflife-python.json`): 3.8 end of life 2024-10-07; 3.13 security fixes until 2029-10-31; 3.14.0 is nine bugfix releases behind 3.14.9. (b) gives nothing that (c) does not, and it is frozen at a `.0` release. (d) is what operators on Windows run, but it is end of life, and the S6 tools (coverage, mutation testing) need a newer Python `[допущение: versions checked in S6]`. Consequences of the decision: the oracle driver of S2 must run on Python 3.8; S2 also runs the oracle on (c), and any difference between the two outputs is a finding for the maintainer, not a fix; S6 tools that no longer support 3.8 run in the (c) environment `[допущение: checked in S6]`. Managed Pythons live in `.legacy-run/python` (`UV_PYTHON_INSTALL_DIR`, `--python-preference only-managed`). The runtime does not depend on the machine's interpreters; this machine's system 3.14.4 is rejected by legacy too. | legacy relaxes `requires-python` or moves its release builds off 3.8 (new pin); S2 finds a difference between the 3.8 and 3.13 outputs; the corpus turns out to come mostly from other versions |
| T2 | Headless legacy runs: Qt platform and stability | (a) `QT_QPA_PLATFORM=offscreen`; (b) no platform variable; both without `DISPLAY`/`WAYLAND_DISPLAY`, in a hermetic environment (`scripts/legacy_env.py: hermetic_env`) | **(a)** for every legacy run; five tests of `tests/test_teamwork.py` deselected | `legacy-tests-offscreen.md` and `legacy-tests-noplatform.md`: the whole suite runs in both modes without a crash. The 48 recalculation tests (`test_result_calculation.py`, `test_relay_results.py`) give the same result in both: 40 passed, 8 skipped by legacy's own markers. Recalculation therefore needs neither a display nor the offscreen plugin. (a) is kept because only it lets code that creates a `QGuiApplication` start without a display; the oracle driver of S2 may reach such code `[допущение]`. Stability: two teamwork tests changed outcome between identical runs, both times without a platform. All five tests that start a real TCP server and client are deselected and listed in every output (`unstable-tests.agent.md`). Two consecutive evidence runs are then byte-identical. | a deselected test is needed as evidence; the oracle driver creates no Qt objects (then (b) suffices) |

## Environment limits found
- `tests/test_reader.py` (3 tests) fails in every run inside the sandbox: its fixture creates ptys at
  `/tmp/pty0` and `/tmp/pty1` with `socat` `[код: pysport@b548c35 tests/test_reader.py:166-175]`, and the
  sandbox makes `/tmp` read-only. These tests stay in the runs: the failure is deterministic and it is
  documented. Outside the sandbox (run by the maintainer on 2026-10-31,
  `legacy-tests-outside-sandbox.md`) `test_sportident` and `test_sportiduino` pass. `test_huichang`
  still fails, for a reason not yet known: the test decodes card times from synthetic bytes
  `[код: pysport@b548c35 tests/test_reader.py:114-125,341-390]`, and without the assertion message
  it is open whether the cause is the time zone, timing or legacy itself. Finding for S5; Huichang is
  not in the maintainer's hardware list (D5). S5 meets the same `/tmp` limit when it replays dumps
  through virtual ports.
- Legacy pytest runs with `--showlocals` and DEBUG logging over `tests/data/test.json`, which contains
  personal data `[мейнтейнер: 2026-10-31]`. Only test ids and outcomes are kept. The console output is
  discarded, and the copy is cleaned before and after each run (`clean_clone`): a legacy test leaves
  `tests/data/test.json.tmp` behind.
