# Stage 0 independent verification — evidence

Tool outputs behind `docs/reports/stage-0-verification.md`. Produced on 2026-10-24 on the maintainer's
machine (Windows 11 Pro 26H2, 12 CPUs, uv 0.13.1) for commit `aeb0d35` of branch `stage-0`. Everything that
modifies files ran on clones of the project in a temporary directory, never in the working checkout or the
legacy checkout. The scripts that produced each file are in `scripts/` exactly as they were run.

| file | what | produced by |
|---|---|---|
| `checks-rerun.txt` | items 2–9 re-captured on a clean clone: `check.py --keep-going`, canaries (a)–(d) + extra, pre-commit (default interpreter, `--python 3.14`, pre-push), `ruff` with/without `--force-exclude`, guard payloads, `legacy_clone.py`, `uv audit`, licences, `uv lock --check`, Backlog.md lists, CI run 40093927242 jobs and `Building grimp` on macOS/3.15, gitleaks | `scripts/verification_rerun.sh` |
| `extra-checks.txt` | personal-data search (rule 8), licence-check heuristics and packages it does not see, guard hook with healthy/broken/absent `.venv` | `scripts/extra_capture.sh` |
| `supply-chain.txt` | lock-file canary committed through the real git pre-commit hook in a clone; `uv sync --locked`; CI action tags resolved via the GitHub API; image refs; `uv.lock` hash count | `scripts/supply_chain_capture.sh` |
| `guard-mutants.txt` | 21 hand-written mutants of the guard hook against `tests/scripts/test_guard.py`: 13 killed | `scripts/mutate_guard.py` (`scripts/mutant_detail.py` for single mutants) |
| `hook-latency.txt` | PostToolUse hook command from `.claude/settings.json`, 10 runs per file | `scripts/hook_latency.py` |
| `wheels-only-resolution.txt` | ADR-0001 cross-check with `uv pip compile --only-binary :all:`; the project lock on 3.15/macOS; grimp and orjson wheel lists | `scripts/wheels_capture.sh`, `scripts/wheels_matrix.sh` |
| `python-support-matrix.md`, `.json`, `endoflife-python.json`, `python-support-matrix-pyyaml.md` | `uv run python -m scripts.python_support_matrix --out-dir <tmp>` (and `--packages pyyaml`) | project script |
| `typecheckers-results.md`, `.json` | `uv run --no-project --python 3.14 python -m scripts.bench_typecheckers --legacy-path <pinned legacy clone>/sportorg`, run in a clone because the script always writes into its own `docs/evidence/stage-0/typecheckers/` | project script |
| `env-bench.txt` | `scripts/bench_env.sh` on a native Windows copy, a WSL ext4 clone and a WSL `/mnt/c` copy (raw log; NUL bytes and a WSL localhost notice removed) | project script, `scripts/wsl_bench.sh` |
| `devcontainer.txt` | `.devcontainer/Dockerfile` build, `postCreateCommand`, `check.py`, `pre-commit run` inside the image (clone mounted read-only) | inline `docker build` / `docker run` |
| `clean-install-ubuntu.txt` | README steps in a fresh `ubuntu:24.04` container | `scripts/readme_clean.sh` |
| `clean-install-windows.txt` | README steps in Windows Sandbox (`wsb` 0.8.107.0), steps 1–17 with outputs and exit codes | `scripts/run.ps1`, `rerun.ps1`, `rerun2.ps1`, `console.ps1` |

`scripts/*.json` are the hook payloads fed to `python -m scripts.hooks.guard`.

`bench_env.sh` rows (the ext4 row is interleaved with uv output in the raw log, line 77):

| env | system | fs | cold `uv sync` | warm | pytest | ruff | basedpyright |
|---|---|---|---|---|---|---|---|
| native-ntfs | MINGW64_NT-10.0-26300 | ntfs | 21.58 | 0.28 | 0.67 | 0.14 | 1.09 |
| wsl-ext4 | Linux 6.18.33.2-microsoft-standard-WSL2 | ext4 | 10.65 | 0.05 | 0.22 | 0.02 | 0.86 |
| wsl-9p | Linux 6.18.33.2-microsoft-standard-WSL2 | 9p | 59.44 | 0.24 | 1.78 | 0.29 | 3.18 |

Caveats:
- Windows Sandbox: the run lost its log writes from step 6 on; outputs of steps 6–17 were copied from the
  sandbox and their exit codes come from a rerun of the same commands in the same (warm) sandbox.
- `guard-mutants.txt` is the second run; a first run without `-B` was invalid (a same-size mutant written in
  the same second was served from the previous mutant's stale `.pyc`).
- Items whose output is a Claude Code tool message (the deny-rule refusal, the PostToolUse and Stop hook
  feedback) cannot be re-run from a script; they are quoted verbatim in the report.
