# Stage 1 tools: candidates and measurements (ADR-0007)

What: facts and measurements behind `docs/adr/0007-stage-1-analysis-tools.md`, on the legacy pin
`pysport@b548c35`. Commands: `commands.txt`.

| File | Content | Deterministic |
|---|---|---|
| `candidates.json`, `candidates.md` | PyPI facts per candidate: latest version, first upload of that version, licence, status, `requires-python`, cp314/cp315 wheels for Linux x86_64 / macOS / Windows amd64; SHA-256 of each cached PyPI document | yes, from the cache `~/.cache/sportorg-stage1/pypi/` |
| `bench.json`, `bench.md` | counts and agreement: N1 complexity (ruff/radon/lizard), N2 import edges (own `ast`/grimp), N3 dead code (vulture; skylos and deadcode failures), N6 history (own `git log`/PyDriller), N8 probe `sys.platform` (git grep/ast-grep) | yes (rerun compared byte for byte, 2026-10-25) |
| `timings.json` | median wall time of 5 runs, seconds, WSL2 Ubuntu on ext4 | no |

Key numbers (from `bench.json`):
- N1: functions ruff 1973 / radon 1961 / lizard 1967; Spearman ρ 0.8986 (ruff/radon), 0.898 (ruff/lizard).
- N2: internal import edges own 603 / grimp 588. Every grimp edge is also in own. 15 edges only own finds, all
  around the namespace package `sportorg.modules.recovery` (no `__init__.py`).
- N3: vulture 282 findings. skylos exit 1 (`Operation not permitted`: forkserver needs an AF_UNIX
  socket, denied by the sandbox). deadcode exit 1 (`module 'ast' has no attribute 'Str'` on 3.14).
- N6: commits 1340 = 1340, merges 198 = 198; equal change counts for 323 of 324 tracked files.
- N8: `sys.platform` 7 hits in both tools, identical.

Limits:
- Times are from one machine.
- skylos and deadcode were run once (they fail).
- N4/N5 (vulnerabilities) are measured in W3, `docs/evidence/stage-1/dependencies/`.
- No tool wrote into `.legacy/`: `assert_tree_clean` ran after each need, then `scripts.legacy verify` printed `ok`.
