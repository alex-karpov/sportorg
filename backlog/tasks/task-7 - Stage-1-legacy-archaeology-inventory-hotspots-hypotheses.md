---
id: TASK-7
title: 'Stage 1: legacy archaeology - inventory, hotspots, hypotheses'
status: In Progress
assignee: []
created_date: 2026-10-24 12:05
updated_date: '2026-10-24T21:49:00Z'
labels:
  - stage-1
milestone: m-1
dependencies: []
documentation:
  - docs/plans/stage-1-archaeology.md
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per docs/brief.md, Stage 1. Read-only analysis of the pinned legacy clones (legacy.toml, ADR-0006): .legacy/pysport at sportorg/pysport b548c35 (code) and .legacy/templates at alex-karpov/sportorg-templates cd95382 (Russian report templates).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Function inventory: every legacy menu action, report template and import/export format listed with module and file:line in docs/evidence/stage-1/, produced or cross-checked by a script in scripts/
- [ ] #2 Hotspots (change frequency x complexity), import graph, layer violations, dead code, dependency/licence/vulnerability lists produced by scripts in scripts/ with outputs in docs/evidence/stage-1/
- [ ] #3 Defect history: fix commits classified by module and error class by a script; the counts table in docs/evidence/stage-1/ is reproducible from that script
- [ ] #4 Data formats and device protocols: every reader and writer listed with file:line and its hard-coded values (table in docs/evidence/stage-1/, each row with a [код] tag)
- [ ] #5 OS-specific code and Russian specifics in the core: a script lists the file:line hits; the manual classification of each hit is attached
- [ ] #6 Each hypothesis from the brief (memory.py 2910 lines and most changed; race() in 62 files; GUI imported outside gui; punch system in result classes; Qualification in domain; Win7 pins) confirmed or refuted with numbers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-25 Phase A (session 1): branch stage-1 from main 170a28a. Environment: uv sync ok; scripts.legacy fetch -> both already at pin, locked; verify -> 'ok: pysport@b548c35ba18f, templates@cd953823beb3 locked'; check.py -> format/lint/types/imports/tests ok, 105 passed. Plan written: docs/plans/stage-1-archaeology.md (tool candidates N1-N8, layer model, defect rule/taxonomy, W1-W6 ownership). STOP: waiting for the maintainer's review of plan, tools, taxonomy, layer model. Status stays To Do until approval.

2026-10-25: network cache ~/.cache/sportorg-stage1 added to sandbox allowWrite by the maintainer; directory created (one mkdir outside the sandbox: bubblewrap cannot bind a missing path); write from inside the sandbox ok. gh: logged in as alex-karpov, 'gh api rate_limit' core 4998/5000 (the earlier 'invalid token' was the sandbox blocking api.github.com, not the token). W4 issues/PRs will use gh api.

2026-10-25 [мейнтейнер: 2026-10-25]: Phase A plan approved — (1) layer model and core = ranks 1-2 approved; (2) fix rule and the 12-class taxonomy approved; (3) PyPI/GitHub requests in Phase B allowed, per-host confirmations collected before Phase B. Status -> In Progress.

2026-10-25 [мейнтейнер: 2026-10-25]: network hosts allowed for Phases B-C: pypi.org + files.pythonhosted.org, api.github.com (gh), api.osv.dev, crates.io (UA 'sportorg-stage1-archaeology'). Non-Python tools: only a pinned osv-scanner release binary (github.com + release-assets.githubusercontent.com, sha256 checked against the release checksums, kept outside the repo); no Rust toolchain; cargo-audit/cargo-deny/code-maat from primary sources only, marked 'not measured: needs cargo/JVM'. Next: Phase B Task 1 (scripts/archaeology/common.py, TDD).

2026-10-25 Phase B Task 1 done: scripts/archaeology/{common,verify_locs}.py + tests (37 passed). Smoke on pysport@b548c35: 1340 commits (198 merges, 178 binary numstat rows), 324 tracked, 220 .py, 1398 import statements, 0 unparsed, memory.py 2910 physical lines; trees clean; legacy verify ok. Added physical_lines (CR/LF/CRLF only; str.splitlines also breaks at FF/U+2028) and parse_source (records SyntaxWarning, e.g. invalid escape at sportorg/gui/dialogs/about.py:747 — future SyntaxError, note for H6/Stage 2). check.py green (142 passed). Next: Task 4 fetch.py (moved before Task 2: tool metadata uses the same cache).

2026-10-25 Phase B: Task 4 fetch.py (cache + MANIFEST, fake-opener tests) done early; Task 2 done: tool_bench.py (PyPI facts, parsers) + tool_runs.py (measurements), evidence docs/evidence/stage-1/tools/ (bench rerun byte-identical), ADR-0007 written; uv add --dev vulture>=2.16 grimp>=3.17; uv sync --locked --no-build ok; check_licenses ok; uv audit: 0 vulns in 17 packages. Findings: grimp misses namespace pkg sportorg.modules.recovery (15 edges); skylos fails in sandbox (forkserver AF_UNIX), deadcode fails on 3.14 (ast.Str). Next: Task 3 hypotheses.
<!-- SECTION:NOTES:END -->
