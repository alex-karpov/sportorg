# ADR-0001: Python version for development and lower bound of the code

- Status: accepted (Stage 0), revisit condition below
- Date: 2026-10-24
- Evidence: `docs/evidence/stage-0/python-support-matrix.md` (+ `.json` with hashed raw PyPI
  responses), `docs/evidence/stage-0/endoflife-python.json`, `docs/evidence/stage-0/uv-python-downloads.txt`.
  Reproduce: `uv run python -m scripts.python_support_matrix`.

## Context
Python 3.15.0 was released on 2026-10-09; development will take several months; the product must run on
Windows, Linux and macOS; code is written mostly by agents, so the toolchain (ruff, type checker, pytest,
import-linter) must be available as wheels on every OS. The brief asks for a comparison by library
support and support horizon, not for "the newest".

## Options
1. Develop on 3.15, lower bound 3.15.
2. Develop on 3.14, lower bound 3.14, CI also runs 3.15 as an early-warning lane. **(chosen)**
3. Develop on 3.14, lower bound 3.13 (wider reach for contributors running from source).
4. Develop on 3.13 (one more year of field maturity).

## Data (2026-10-24, PyPI JSON API, 62 packages)
Support horizon (endoflife.date): 3.13 → 2029-10-31, 3.14 → 2030-10-31, 3.15 → 2031-10-31.

Wheels for cp315 on all three platforms exist for the core runtime candidates and the toolchain:
PySide6 6.12.0 (`requires_python <3.16`), PyQt6, cryptography, orjson, msgspec, pydantic, lxml, psutil,
pytest 9.1.1, hypothesis, ruff 0.17.2, mypy 2.4.0, basedpyright 1.40.2, ty, pyrefly, import-linter (py3),
cx_Freeze 8.7.3 (`<3.16`), pyinstaller 6.22.3 (`<3.16`), briefcase.

Missing for cp315 as of today: **pyyaml 6.0.3** (wheels only up to cp314; pulled in by pre-commit),
hidapi 0.15.0, nuitka (sdist only). Observed consequence on this machine (project on 3.15):

```
uv add --dev basedpyright
error: Failed to build `pyyaml==6.0.3`
error: Microsoft Visual C++ 14.0 or greater is required.
```

Legacy pins `>=3.8.1,<=3.14` for Windows 7 operators `[код: ../_other/pysport-legacy/pyproject.toml]`.
The new product's minimum OS is a Stage 4 decision from operator data; the distributed bundle carries its
own interpreter, so the lower bound here constrains contributors, not operators.

## Decision
Option 2. `.python-version` = 3.14; `requires-python = ">=3.14"`; CI matrix runs 3.14 and 3.15 on three
OSes. Tools that are not project dependencies (pre-commit) run via `uvx`, so a missing 3.15 wheel in a
tool's dependency tree cannot block the project environment.

Why not 1: two weeks after release the long tail (pyyaml) still has no wheels; on Windows this means a
compiler requirement for every contributor. Why not 3/4: 3.14 already has wheels for everything in the
matrix, one extra year of support over 3.13, and no operator data yet justifies a lower bound below the
development version (that would be "by default").

## Consequences
- Agents may use 3.14 features (t-strings, deferred annotations) but nothing from 3.15.
- The 3.15 lane is a required CI job: when it fails because of a missing wheel, the fix is to wait or to
  drop the dependency, never to build from source in CI.

## Revisit
Switch development to 3.15 when (a) pyyaml and every direct dependency ship cp315 wheels for win/linux/mac
and (b) the 3.15 CI lane has been green for 4 consecutive weeks. Re-run the matrix script and record the
date here. Also revisit when the Stage 4 minimum-OS ADR lands.
