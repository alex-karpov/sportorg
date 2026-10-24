# ADR-0004: Small tooling choices of Stage 0

- Status: accepted (Stage 0)
- Date: 2026-10-24
- Scope: choices too small for their own ADR. Tools named by the brief (uv, ruff, import-linter,
  pre-commit, Backlog.md) are the maintainer's `[мейнтейнер: 2026-10-24]` and are not compared here;
  only their placement is decided.

| # | Need | Options considered | Decision | Data / why |
|---|---|---|---|---|
| 1 | One command that defines "green" | (a) `poethepoet` tasks (legacy used it), (b) `nox`/`tox` sessions, (c) `just`/Makefile, (d) own stdlib script | **(d) `scripts/check.py`** | Zero dependencies, identical on three OSes, importable by hooks (`step_command`), fail-fast with a summary. (a)–(c) add a dependency or a non-Python tool for five fixed commands. `[допущение]` on startup overhead: not measured, the steps dominate. |
| 2 | Where pre-commit runs | (a) project dev dependency, (b) `uvx pre-commit` | **(b)** | On Python 3.15 pre-commit's dependency pyyaml 6.0.3 has no wheel and the project sync fails (ADR-0001 evidence). pre-commit is a tool, not a library; its hooks call `uv run --no-sync …`, so versions still come from `uv.lock`. Fast checks at commit, tests at push (`stages: [pre-push]`). |
| 3 | Lint/format | ruff `select = ["ALL"]`, explicit ignores with reasons; `RUF100` makes unused `noqa` an error | — | Named by the brief. `CPY001` (copyright header) off until the licence decision. Fixture directories excluded. |
| 4 | Import boundaries | import-linter, three `forbidden` contracts (core pure; nothing imports ui; no national deps) | — | Named by the brief. Verified: `Contracts: 3 kept, 0 broken` on the skeleton. |
| 5 | Tests | pytest 9.1 with `--strict-markers --strict-config`, `xfail_strict`, `filterwarnings = error` | — | Warnings fail the run so agents cannot leave deprecations silent. Coverage/mutation thresholds come after the Stage 2 baseline (brief). |
| 6 | Vulnerabilities | (a) `uv audit` (uv 0.13, experimental), (b) `pip-audit` 2.10.1, (c) `osv-scanner` (Go binary) | **(a)** now, (b) as fallback | `uv audit` reads `uv.lock` directly: no extra dependency, one command in CI (`uv audit --locked`). Verified: "Found no known vulnerabilities … in 19 packages". Flagged as experimental by uv; if its output format breaks CI, switch to (b) (same advisory source, PyPA). |
| 7 | Licence compatibility | (a) `pip-licenses` 5.5.5 + allowlist script, (b) `licensecheck` 2026.0.8, (c) `liccheck` 0.9.2 (last release 2023), (d) own PyPI-metadata script | **(a) via `scripts/check_licenses.py`** | Reads installed metadata (what is really shipped), MIT, wheels everywhere. (d) was already half-written in the support-matrix script but depends on network and on PyPI's inconsistent licence fields ("Dual License"). (c) is stale. (b) not measured `[допущение]`. Allowlist assumes GPL-3.0-or-later (open question). |
| 8 | CI | GitHub Actions (repo is public on GitHub, three OS runners free) | matrix 3 OS × {3.14, 3.15} + `clean-install` job in `ubuntu:24.04` container following README verbatim | Runner labels per `actions/runner-images` on 2026-10-24: ubuntu-latest = 24.04, windows-latest = Server 2025, macos-latest = macOS 26 arm64. `astral-sh/setup-uv` pinned to `v10.3.2` (no floating `v10` tag exists: checked via GitHub API). |
| 9 | Build backend | `uv_build` (no runtime deps, src layout) | — | Nothing is distributed yet; packaging is a Stage 4 ADR (cx_Freeze/PyInstaller/briefcase all have cp314 wheels). |
| 10 | Line length | 100 | — | `[допущение]`: fits side-by-side diffs; agents produce many long f-strings at 88. |

## Open question for the maintainer
Project licence: GPL-3.0-or-later (compatible with copying legacy templates/data, which are GPL-3) or a
permissive licence (then nothing from legacy may be copied, only behaviour reproduced). The licence
check allowlist and the `CPY001` header rule depend on it.
