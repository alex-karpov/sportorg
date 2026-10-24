# ADR-0004: Small tooling choices of Stage 0

- Status: accepted (Stage 0); rows 2, 7 and 8 revised after the independent check of 2026-10-24; the
  project licence decided by the maintainer on 2026-10-25 (last section)
- Date: 2026-10-24, licence 2026-10-25
- Scope: choices too small for their own ADR. Tools named by the brief (uv, ruff, import-linter,
  pre-commit, Backlog.md) are the maintainer's `[мейнтейнер: 2026-10-24]` and are not compared here;
  rows 3–5 record their configuration, not a choice.

| # | Need | Options considered | Decision | Data / why | Revisit when |
|---|---|---|---|---|---|
| 1 | One command that defines "green" | (a) `poethepoet` tasks (legacy used it), (b) `nox`/`tox` sessions, (c) `just`/Makefile, (d) own stdlib script | **(d) `scripts/check.py`** | Zero dependencies, identical on three OSes, importable by hooks (`step_command`), fail-fast with a summary. (a)–(c) add a dependency or a non-Python tool for five fixed commands. It is code to maintain; for five steps that is acceptable. `[допущение]` on startup overhead: not measured, the steps dominate. | more than ~10 steps, or steps need parallelism or parametrised sessions |
| 2 | Where pre-commit runs | (a) project dev dependency, (b) `uvx` tool | **(b) `uvx --python 3.14 pre-commit@4.7.0`** | On Python 3.15 pre-commit's dependency pyyaml 6.0.3 has no wheel, so as a dev dependency it breaks the project sync (ADR-0001). A bare `uvx pre-commit` picks the newest installed interpreter and fails the same way, hence the pinned interpreter and version. Hooks call `uv run --no-sync …`, so tool versions still come from `uv.lock`. Deliberately broken fixtures and frozen evidence are excluded and ruff gets `--force-exclude` (pre-commit passes file names; without it ruff ignored `extend-exclude` and the run was red, independent check 2026-10-24). | pyyaml ships cp315 wheels; a new pre-commit major |
| 3 | Lint/format | ruff `select = ["ALL"]`, explicit ignores with reasons; `RUF100` makes unused `noqa` an error | — | Named by the brief. `CPY001` (copyright header) off: the whole project has one licence, stated in `LICENSE` and `pyproject.toml`, so per-file headers would repeat it. Fixture directories excluded. | files under another licence enter the repository (`CPY001` or SPDX headers) |
| 4 | Import boundaries | import-linter, three `forbidden` contracts (core pure; nothing imports ui; no national deps) | — | Named by the brief. Verified: `Contracts: 3 kept, 0 broken`. | Stage 4 architecture ADR |
| 5 | Tests | pytest 9.1 with `--strict-markers --strict-config`, `xfail_strict`, `filterwarnings = error` | — | Warnings fail the run so agents cannot leave deprecations silent. Coverage/mutation thresholds come after the Stage 2 baseline (brief). | Stage 2 baseline |
| 6 | Vulnerabilities | (a) `uv audit` (uv 0.13, experimental), (b) `pip-audit` 2.10.1, (c) `osv-scanner` (Go binary) | **(a)** now, (b) as fallback | `uv audit` reads `uv.lock` directly: no extra dependency, one command in CI (`uv audit --locked`). Verified: "Found no known vulnerabilities … in 16 packages" (2026-10-24, after pip-licenses was removed). It is experimental and a CI gate. | its output format or exit codes change (switch to (b), same PyPA advisory source) |
| 7 | Licence compatibility | (a) `pip-licenses` 5.5.5 + allowlist script, (b) `licensecheck` 2026.0.8, (c) `liccheck` 0.9.2 (last release 2023), (d) own script over `uv.lock` + installed metadata | **(d) `scripts/check_licenses.py`** | Package sets come from `uv.lock` offline: runtime = reachable from the project's dependencies, dev = the rest. Licences come from installed metadata (`License-Expression`, then classifiers, then `License`), are normalised to SPDX and evaluated as expressions (`OR`/`AND`/`WITH`) against an exact allowlist compatible with GPL-3.0. (a) was used first and was wrong: substring matching passed `GPL-2.0-only` and "Limited use license", it did not check itself or its own dependencies, and it gated dev tools (not distributed) like runtime dependencies. Runtime problems fail the check; dev packages are reported and fail only with `--strict-dev`. No network, no extra dependency (pip-licenses removed). (c) is stale; (b) not measured `[допущение]`. | first runtime dependency added; the project licence changes |
| 8 | CI | GitHub Actions (repo is public on GitHub, three OS runners free) | matrix 3 OS × {3.14, 3.15} with `uv sync --locked --no-build`, the 3.15 lane non-blocking; `clean-install` job in `ubuntu:24.04` following README | Runner labels per `actions/runner-images` on 2026-10-24: ubuntu-latest = 24.04, windows-latest = Server 2025, macos-latest = macOS 26 **arm64 only — Intel macOS is not covered**. Actions are pinned by commit SHA with the version in a comment (tags can be moved): `actions/checkout` v5.0.1, `astral-sh/setup-uv` v10.3.2. `clean-install` deliberately installs the latest uv, as a newcomer would; it runs the README Linux steps in order plus a CI-only checkout of the commit under test. The devcontainer base images are pinned by tag, not digest. | a runner label changes; an action release is needed (bump the SHA); Intel macOS operators turn up in the inventory |
| 9 | Build backend | `uv_build` (no runtime deps, src layout) | — | Nothing is distributed yet; packaging is a Stage 4 ADR (cx_Freeze/PyInstaller/briefcase all have cp314 wheels). Only one option was considered because nothing is built yet. | Stage 4 packaging ADR |
| 10 | Line length | 100 (one option) | — | `[допущение]`: fits side-by-side diffs; agents produce many long f-strings at 88. Not measured. | formatter churn or review complaints |

## Project licence: GPL-3.0-only
Decision `[мейнтейнер: 2026-10-25]`: **GPL-3.0-only** for the whole project; `LICENSE` holds the
canonical GPLv3 text (gnu.org, git blob `f288702d`), `pyproject.toml` declares `GPL-3.0-only`.

Options (`docs/reports/stage-0.md`, question 1): (a) GPL-3.0-only for everything; (b) GPL-3.0-or-later
for own code plus `SPDX-License-Identifier: GPL-3.0-only` on everything derived from legacy; (c) ask
the pysport authors whether "or later" was meant. The maintainer's first decision of 2026-10-24 was
GPL-3.0-or-later on condition of confirming the legacy licence from the primary source.

Data (`docs/evidence/stage-0/legacy-layout/README.md`, section 1): the legacy names GPL version 3 —
the full GPLv3 text in `LICENSE`, the README badge "GPLv3" — and nowhere grants "or any later version"
at project level; `pyproject.toml` has no licence field. Only the vendored
`sportorg/libs/huichang/huichang.py` carries an explicit "or (at your option) any later version".
Reading `[допущение]`: by GPLv3 §14 the legacy is GPL-3.0-only, so code and templates derived from it
can only be distributed under version 3. The agent reads legacy constantly, so no part of the project
can be shown to be free of it (maintainer's argument of 2026-10-24); (b) would need that proof file by
file. The dependency allowlist of row 7 is the same for every option.

Revisit: the maintainer asks the pysport authors (c) (Backlog TASK-10); if they grant "or later", the
project may switch to GPL-3.0-or-later.
