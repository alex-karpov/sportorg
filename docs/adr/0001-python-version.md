# ADR-0001: Python version for development and lower bound of the code

- Status: accepted (Stage 0), confirmed by the maintainer `[мейнтейнер: 2026-10-24]`; revisit condition below
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

Legacy pins `>=3.8.1,<=3.14` `[код: pysport@b548c35 pyproject.toml:6]`; 3.8 is the last Python for
Windows 7. Python 3.14 supports Windows 10 and newer only ("If you require Windows 7 support, install
Python 3.8. If you require Windows 8.1 support, install Python 3.12." `[docs.python.org/3.14/using/windows.html,
§4.5, per PEP 11]`). A distributed bundle carries its own interpreter, but that interpreter still sets the
minimum OS: **a product on 3.14 cannot run on Windows 7 or 8.1 at all.** How many operators still run them
is unknown (data request item 10), so that data is needed before Stage 2, not only for the Stage 4 ADR.
`hidapi` is a candidate from the matrix, not a legacy dependency (absent from legacy `pyproject.toml` and
imports); `orjson` is a legacy runtime dependency, and its cp315 Linux wheels need glibc ≥ 2.39
(`manylinux_2_39`: Ubuntu 24.04 yes, RHEL 9 no) — the matrix script counts any manylinux tag, so this
matters for the Stage 4 minimum-OS ADR (independent check, 2026-10-24).

## Decision
Option 2. `.python-version` = 3.14; `requires-python = ">=3.14"`; CI matrix runs 3.14 and 3.15 on three
OSes with `uv sync --locked --no-build` (no third-party source builds anywhere). Tools that are not
project dependencies run via `uvx` with the interpreter and version pinned
(`uvx --python 3.14 pre-commit@4.7.0`): a bare `uvx pre-commit` picks the newest installed Python and,
with 3.15 installed, has to build pyyaml from source. On Windows without a C compiler that failed
("Microsoft Visual C++ 14.0 or greater is required", independent check, 2026-10-24); on Linux with a
compiler it built and ran (independent round-2 check, 2026-10-25). Pinning avoids the dependency on a
compiler.

Why not 1: two weeks after release the long tail (pyyaml) still has no wheels; on Windows this means a
compiler requirement for every contributor. Why not 3/4: 3.14 already has wheels for everything in the
matrix, one extra year of support over 3.13, and no operator data yet justifies a lower bound below the
development version (that would be "by default").

## Consequences
- Agents may use 3.14 features (t-strings, deferred annotations) but nothing from 3.15.
- The 3.15 lane is non-blocking (`continue-on-error`): it reports, it does not gate merges. When it fails
  because of a missing wheel, the fix is to wait or to drop the dependency, never to build from source.
  Known on 2026-10-24: macOS/3.15 has only `cp315t` wheels for grimp 3.17 (import-linter), so that lane
  is expected to be red until grimp ships a cp315 macOS wheel; before `--no-build` it was green only
  because CI compiled grimp.

## Revisit
Switch development to 3.15 when (a) every package in `uv.lock` (not only direct dependencies) installs
from wheels on 3.15 on win/linux/mac — the CI 3.15 lanes with `--no-build` show it — and pre-commit's
pyyaml has cp315 wheels, and (b) the 3.15 CI lane has been green for 4 consecutive weeks. Re-run the matrix script and record the
date here. Also revisit when the Stage 4 minimum-OS ADR lands.
