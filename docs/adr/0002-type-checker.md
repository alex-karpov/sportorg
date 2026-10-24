# ADR-0002: Type checker — basedpyright

- Status: accepted (Stage 0), revisit condition below
- Date: 2026-10-24
- Evidence: `docs/evidence/stage-0/typecheckers/results.md` (+ `results.json`, per-tool outputs,
  `help-*.txt`, `commands.txt`). Reproduce: `uv run --no-project --python 3.14 python -m scripts.bench_typecheckers`
  (fixtures in `scripts/typecheck_fixtures/`, strict configs in `scripts/typecheck_configs/`).

## Context
Code is written mostly by agents. The brief's criteria: speed of feedback in the edit cycle, resistance
to evasions (`Any`, `cast`, suppressions), message quality, rule stability, three OSes, licence, overlap
with what ruff already catches. Candidates named by the brief: mypy, pyright/basedpyright, ty, pyrefly,
zuban.

## Data (2026-10-24, Windows 11, 12 CPUs; legacy corpus = 177 files of SportOrg)

| tool | version | licence | evasion fixtures caught (of 17) | fixtures run | one file | legacy cold | legacy warm |
|---|---|---|---|---|---|---|---|
| mypy | 2.4.0 | MIT | 14 | 1.25 s | 1.54 s | 4.05 s | 3.43 s |
| pyright | 1.1.414 | MIT | 10 | 2.30 s | 1.21 s | 7.28 s | 6.80 s |
| basedpyright | 1.40.2 | MIT | **15** | 1.07 s | 1.19 s | 9.00 s | 7.67 s |
| ty | 0.0.91 | MIT | 8 | 0.11 s | 0.13 s | 0.36 s | 0.34 s |
| pyrefly | 1.4.0 | MIT | 12 | 0.43 s | 0.46 s | 0.63 s | 0.58 s |
| zuban | 0.10.1 | **AGPL-3.0** | 12 | 0.11 s | 0.10 s | 0.88 s | 0.45 s |

Times include ~0.4 s `uvx` launcher overhead (0.06 s for ty/pyrefly/zuban). All six run on Windows,
Linux and macOS wheels. No tool produced a false positive on the clean control file.

What each of the two leaders misses, and whether ruff (`select = ["ALL"]`) covers it:

| fixture | mypy | basedpyright | ruff overlap |
|---|---|---|---|
| wrong `cast(int, "s")` (real bug class) | silent | caught (`reportInvalidCast`) | no |
| `getattr(obj, "attr")` leaking Any | silent | caught (`reportAny`) | B009 (constant attr only) |
| unnecessary `# pyright: ignore` | silent | caught | PGH003 (bare only) |
| redundant `cast(int, 1)` | caught | silent | no (cosmetic) |
| `assert isinstance(v, int)` on a `str` | caught (`warn_unreachable`) | silent | S101 forbids `assert` in `src/` |

ty misses untyped defs, explicit Any, Any leaks from untyped calls, redundant casts, unreachable code;
ruff ANN rules cover the first two. Message quality: ty and pyrefly render source snippets with hints;
pyright-family gives line, column and rule name; mypy/zuban give line and error code only.

## Decision
**basedpyright 1.40.2**, `typeCheckingMode = "all"`, `reportUnnecessaryTypeIgnoreComment = "error"`,
`reportIgnoreCommentWithoutRule = "error"`. Two rules are switched off with a reason in `pyproject.toml`:
`reportImplicitStringConcatenation` (ruff ISC001/ISC002 cover it) and `reportUnusedCallResult` (flags every
`parser.add_argument(...)`; ruff B018 keeps the useless-expression case). Every other adjustment needs a
line here.

Why over mypy (14/17): catches the invalid-cast bug class and `getattr` Any leaks; column + rule name in
every message; faster on a single file, which is the agent hook path. Why over ty (10× faster): 8/17
evasions caught, pre-1.0 (0.0.91) with rules still changing. Why not zuban: AGPL-3.0 and no unused-ignore
detection. Why not pyrefly: 12/17, misses the redundant/unused-ignore cases agents produce most often.

Runtime dependency: basedpyright pulls `nodejs-wheel-binaries` (bundled Node), so no system Node is needed.

## Consequences
- Hook latency after an edit ≈ 1.8–2.0 s for ruff + basedpyright on one file (measured 2026-10-24).
- JSON and argparse results are `Any`; code must narrow them (`scripts/_json.py` helpers, typed
  `argparse.Namespace` subclasses with class-body defaults). This is intended: the same discipline
  applies to file formats in `adapters/` later.

## Revisit
Re-run `scripts/bench_typecheckers.py` when ty reaches 1.0, when any tool catches ≥ 15/17 fixtures and
checks the legacy corpus in under 1 s, or if basedpyright's whole-project time exceeds 30 s on CI.
