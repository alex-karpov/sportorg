# ADR-0007: Stage 1 analysis tools

- Status: accepted (Stage 1, Phase B); N3, N4 and N5 completed with Phase D data
- Date: 2026-10-25
- Scope: tools that measure the pinned legacy (`pysport@b548c35`) for Backlog TASK-7. Rule of the
  brief («Как выбирать инструменты»): ≥ 2 alternatives including an own script; version, date, status
  and licence from the primary source; measured by a script; overlaps with tools already chosen are
  counted once. None of these tools ships with the product.
- Data:
  - `docs/evidence/stage-1/tools/candidates.{json,md}`: PyPI JSON of 2026-10-25 (version, first upload
    of the latest version, licence, status, cp314/cp315 wheels);
  - `docs/evidence/stage-1/tools/bench.{json,md}`: counts and agreement on the legacy;
  - `timings.json`: median of 5 runs on WSL2 (Ubuntu, ext4). Commands are in `commands.txt`.

| # | Need | Options (version, licence, status) | Decision | Data / why | Revisit when |
|---|---|---|---|---|---|
| N1 | Cyclomatic complexity per function (hotspots) | (a) ruff `C901` with `max-complexity = 0` — 0.17.2, MIT, already locked; (b) radon 6.0.1, MIT, last release 2023-03-26, no `requires-python`; (c) lizard 1.24.3, MIT; (d) complexipy 8.1.0, MIT, measures *cognitive* complexity; (e) own `ast` counter | **(a)** | Functions: ruff 1973, radon 1961, lizard 1967. Every radon/lizard function is also in ruff. radon misses 12 functions: methods of classes nested in a class (`sportorg/libs/sportiduino/sportiduino.py`, `import_persons_table_dialog.py`). lizard misses 6: the `...` stubs of a `Protocol` (`sportorg/modules/plugins/manager.py:91-112`). Same complexity for 1511/1961 and 1513/1967 functions; Spearman ρ = 0.899 (radon) and 0.898 (lizard). Ranking hotspots by file sums needs rank agreement, not equal values. Time: 0.03 s against 0.44–0.50 s. (a) adds no dependency. (d) is a different metric that the brief does not ask for. (e) would re-implement McCabe; the 23 % of functions with different values among (a)–(c) show that the definition is not unique, so a fourth variant adds no evidence. Rust has 336 lines in total: complexity is not measured, only lines and changes. | a stage needs cognitive complexity or Rust complexity |
| N2 | Import graph, layer violations | (a) grimp 3.17, BSD-2-Clause, locked through import-linter; (b) import-linter 2.15 `layers` contract; (c) pydeps 3.0.9, BSD-2-Clause; (d) own `ast` extractor (`scripts/archaeology/common.py: iter_imports`) | **(d) primary, (a) cross-check**; (b) as an independent count of violations in W2 | Internal edges: own 603, grimp 588. Every grimp edge is also found by (d) (`only_grimp` = 0). The 15 edges only (d) finds all touch `sportorg.modules.recovery`, a directory without `__init__.py` (namespace package), which grimp does not see. (d) also gives the line and whether the import is local to a function, both needed for the evidence. (c) draws graphs through modulefinder; it was not measured because (a)+(d) already agree edge by edge. grimp becomes an explicit dev dependency, since the scripts import it directly. | legacy gains more namespace packages, or (d) and (a) disagree on edges other than these |
| N3 | Dead code | (a) vulture 2.16, MIT, pure Python, no dependencies; (b) skylos 5.0.0, Apache-2.0, Beta, 69 packages installed; (c) deadcode 2.4.1, AGPL-3.0, Alpha, last release 2024-08-09; (d) own def/use scan | **(a)**, precision measured in Phase D by the agent's sample check (30 findings) | (a): 282 findings (92 unused classes, 81 methods, 50 variables, 41 attributes, 12 functions, 3 properties, 3 unreachable/redundant), exit code 3 = findings present. (b) failed inside the sandbox: `[Errno 1] Operation not permitted`. A probe of `ProcessPoolExecutor` shows the cause: on 3.14 the forkserver needs an AF_UNIX socket, which the sandbox forbids. (b) also has cloud upload and LLM options. (c) crashes on 3.14: `module 'ast' has no attribute 'Str'`. (d) would reproduce what (a) does, and (a) has no dependencies. The legacy menu names its actions as strings (`"action": "NewAction"`), so false positives are expected; the sample check measures them. New dev dependency: `vulture>=2.16`. **Phase D sample** (`structure/dead-code-sample-check.agent.md`, 30 findings): raw precision 12/30 = 40 %, below the revisit threshold. With W2's `name_in_string` flag, precision is 11/19 = 58 %. Remaining false positives come from methods that the dialog base class reaches through name-built `getattr`. Kept with that condition: findings are read only together with `name_in_string`. | precision on the sample < 50 % after the `name_in_string` filter |
| N4 | Python dependencies of legacy: licences, vulnerabilities | lock: own `tomllib` parser (as `scripts/check_licenses.py`); licences: PyPI JSON; vulnerabilities: (a) `uv audit` on a temporary copy of legacy `pyproject.toml` + `uv.lock`, (b) pip-audit 2.10.1, Apache-2.0, (c) own OSV `v1/query` client (`scripts/archaeology/fetch.py osv`) | **(c) primary, (a) cross-check** | (c) runs offline on the cache (the outputs are reproducible) and uses the same source for Python and Rust. (a) is already the project's tool (ADR-0004 row 6). (b) overlaps with (a): same PyPA advisory source. **W3 cross-check** (`dependencies/crosscheck.md`): on the 123 registry package versions, own client and `uv audit` agree on all 227 OSV records (both 227, only own 0, only uv audit 0). Matching uses id plus aliases. | (a) and (c) disagree on a later run |
| N5 | Rust crates of legacy | (a) cargo-audit / cargo-deny (need cargo, which is not installed); (b) osv-scanner (Go binary, pinned release with checksum, `[мейнтейнер: 2026-10-25]`); (c) own `Cargo.lock` parser + OSV + crates.io API | **(c) primary, (b) cross-check**; (a) not measured | 16 packages in `Cargo.lock`. The maintainer decided not to install a Rust toolchain (2026-10-25). **W3 cross-check**: own client and osv-scanner 2.7.0 agree on 227/227 records for `uv.lock` and 4/4 for `Cargo.lock` (all on `pyo3` 0.28.3). | the Rust part of legacy grows, or (b) and (c) disagree |
| N6 | Git history | (a) own `git log --numstat -z` parser (`common.git_log`); (b) PyDriller 2.12, Apache-2.0; (c) code-maat (JVM, not installed) | **(a)** | Commits 1340 = 1340, merges 198 = 198. Non-merge change counts are equal for 323 of 324 tracked files (the one difference is the empty `sportorg/models/__init__.py`: 3 commits in (a) with `--no-renames`, 2 in (b); that (b)'s rename detection pairs the empty files is `[допущение]`). Time 0.41 s against 6.7 s. (a) has no dependency and reads no author fields (personal data, rule 8). (c) was not measured: it needs a JVM. | rename tracking becomes necessary |
| N7 | Issues and PRs of `sportorg/pysport` | (a) `gh api` (gh is installed, token of the maintainer, 5000 requests/h); (b) own unauthenticated client (60 requests/h) | **(a)** through `fetch.py github` | Verified `gh api rate_limit` → core 4998/5000 (2026-10-25). The token stays with gh; raw pages go to the cache outside the repository. Only number, state, labels and is-PR reach the evidence. | gh is unavailable to a verifier: (b) works with the same cache keys |
| N8 | OS- and Russia-specific scans, hard-coded values | (a) own `tokenize` + `ast` scanner (W6, W5); (b) ast-grep 0.51.0 (`ast-grep-cli`), MIT, Alpha; (c) semgrep 1.182.1, LGPL-2.1-or-later, **no cp315 wheel**; (d) `git grep` | **(a)**, recall measured against (d) in W6 | Probe `sys.platform`: git grep 7 hits, ast-grep 7, the same 7. The rules need context that patterns do not give: string or comment, layer, Cyrillic in strings but not in `.po` files. (a) has that context, (b)/(c) would need it written in their rule languages. (c) also lacks 3.15 wheels and sends metrics unless told not to. | a rule needs structural matching that `ast` makes awkward |

## Wheels and Python versions
Dev dependencies added: `vulture>=2.16` (pure Python wheel) and `grimp>=3.17` (already locked as an
import-linter dependency). Both have cp314 wheels for Linux x86_64, macOS and Windows amd64.
grimp has no macOS wheel for 3.15 (`candidates.md`), the same gap as for import-linter, which is
already in the 3.15 lane. Checked:
- `uv sync --locked --no-build`: ok;
- `uv run python -m scripts.check_licenses`: vulture 2.16 MIT ok;
- `uv audit`: no known vulnerabilities in 17 packages.

Tools that are not dependencies run from throwaway environments:
`uvx --python 3.14 <tool>@<version>` (radon, lizard, skylos, deadcode, PyDriller, ast-grep). Their
versions are pinned in `scripts/archaeology/tool_runs.py`.

## Lint configuration
`RUF001` (ambiguous Unicode characters in strings) is off for `scripts/archaeology/**` and
`tests/scripts/archaeology/**` only. These scripts match Russian legacy text, such as the claims of the
brief and Cyrillic patterns, so Cyrillic letters there are data, not look-alikes of Latin ones.
Everywhere else the rule stays on.

## Revisit
Per row above. The whole ADR is revisited if Stage 2 reuses these tools for the new code: there the
choice is made against `src/`, not against legacy.
