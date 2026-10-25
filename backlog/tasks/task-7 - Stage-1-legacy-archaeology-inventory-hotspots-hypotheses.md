---
id: TASK-7
title: 'Stage 1: legacy archaeology - inventory, hotspots, hypotheses'
status: In Progress
assignee: []
created_date: 2026-10-24 12:05
updated_date: '2026-10-25T09:10:00Z'
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
- [x] #1 Function inventory: every legacy menu action, report template and import/export format listed with module and file:line in docs/evidence/stage-1/, produced or cross-checked by a script in scripts/
- [x] #2 Hotspots (change frequency x complexity), import graph, layer violations, dead code, dependency/licence/vulnerability lists produced by scripts in scripts/ with outputs in docs/evidence/stage-1/
- [x] #3 Defect history: fix commits classified by module and error class by a script; the counts table in docs/evidence/stage-1/ is reproducible from that script
- [x] #4 Data formats and device protocols: every reader and writer listed with file:line and its hard-coded values (table in docs/evidence/stage-1/, each row with a [код] tag)
- [x] #5 OS-specific code and Russian specifics in the core: a script lists the file:line hits; the manual classification of each hit is attached
- [x] #6 Each hypothesis from the brief (memory.py 2910 lines and most changed; race() in 62 files; GUI imported outside gui; punch system in result classes; Qualification in domain; Win7 pins) confirmed or refuted with numbers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-25 Phase A (session 1): branch stage-1 from main 170a28a. Environment: uv sync ok; scripts.legacy fetch -> both already at pin, locked; verify -> 'ok: pysport@b548c35ba18f, templates@cd953823beb3 locked'; check.py -> format/lint/types/imports/tests ok, 105 passed. Plan written: docs/plans/stage-1-archaeology.md (tool candidates N1-N8, layer model, defect rule/taxonomy, W1-W6 ownership). STOP: waiting for the maintainer's review of plan, tools, taxonomy, layer model. Status stays To Do until approval.

2026-10-25: network cache ~/.cache/sportorg-stage1 added to sandbox allowWrite by the maintainer; directory created (one mkdir outside the sandbox: bubblewrap cannot bind a missing path); write from inside the sandbox ok. gh: logged in as alex-karpov, 'gh api rate_limit' core 4998/5000 (the earlier 'invalid token' was the sandbox blocking api.github.com, not the token). W4 issues/PRs will use gh api.

2026-10-25 [мейнтейнер: 2026-10-25]: Phase A plan approved — (1) layer model and core = ranks 1-2 approved; (2) fix rule and the 12-class taxonomy approved; (3) PyPI/GitHub requests in Phase B allowed, per-host confirmations collected before Phase B. Status -> In Progress.

2026-10-25 [мейнтейнер: 2026-10-25]: network hosts allowed for Phases B-C: pypi.org + files.pythonhosted.org, api.github.com (gh), api.osv.dev, crates.io (UA 'sportorg-stage1-archaeology'). Non-Python tools: only a pinned osv-scanner release binary (github.com + release-assets.githubusercontent.com, sha256 checked against the release checksums, kept outside the repo); no Rust toolchain; cargo-audit/cargo-deny/code-maat from primary sources only, marked 'not measured: needs cargo/JVM'. Next: Phase B Task 1 (scripts/archaeology/common.py, TDD).

2026-10-25 Phase B Task 1 done: scripts/archaeology/{common,verify_locs}.py + tests (37 passed). Smoke on pysport@b548c35: 1340 commits (198 merges, 178 binary numstat rows), 324 tracked, 220 .py, 1398 import statements, 0 unparsed, memory.py 2910 physical lines; trees clean; legacy verify ok. Added physical_lines (CR/LF/CRLF only; str.splitlines also breaks at FF/U+2028) and parse_source (records SyntaxWarning, e.g. invalid escape at sportorg/gui/dialogs/about.py:747 — future SyntaxError, note for H6/Stage 2). check.py green (142 passed). Next: Task 4 fetch.py (moved before Task 2: tool metadata uses the same cache).

2026-10-25 Phase B: Task 4 fetch.py (cache + MANIFEST, fake-opener tests) done early; Task 2 done: tool_bench.py (PyPI facts, parsers) + tool_runs.py (measurements), evidence docs/evidence/stage-1/tools/ (bench rerun byte-identical), ADR-0007 written; uv add --dev vulture>=2.16 grimp>=3.17; uv sync --locked --no-build ok; check_licenses ok; uv audit: 0 vulns in 17 packages. Findings: grimp misses namespace pkg sportorg.modules.recovery (15 edges); skylos fails in sandbox (forkserver AF_UNIX), deadcode fails on 3.14 (ast.Str). Next: Task 3 hypotheses.

2026-10-25 Phase B committed ac78964 (check.py green: format/lint/types/imports/tests ok). AC #6 checked: docs/evidence/stage-1/hypotheses/ — H1 confirmed (2910 lines, 218 commits rank 1/324), H2 refuted by the fixed definition (78 tracked files; exactly 62 in sportorg/ — scope question for the maintainer), H3 confirmed (12 modules, 29 edges; printing), H4 confirmed (7 subclasses bound to SystemType, 7 branches), H5 confirmed for layer (domain; EVSK match needs rules, Stage 3), H6 partly (py3.8 + 60 PySide2 fallback files; lock above CONTRIBUTING Win7 limits). verify_locs 197 tags 0 problems; rerun byte-identical. Next: Phase C batch 1 (W1, W2, W5 subagents).

2026-10-25 Phase C batch 1 launched (W1, W2, W5 subagents, sonnet/medium). Cache for batch 2 filled by main session: pypi 123 (legacy uv.lock registry pkgs), osv 137 (123 PyPI + 14 crates.io), crates 14, github issues/PRs 578 (6 pages of 100, page 7 empty) + repo + labels, osv-scanner v2.7.0 release metadata; MANIFEST.json in ~/.cache/sportorg-stage1. Binary ~/.cache/sportorg-stage1/bin/osv-scanner-v2.7.0 (sha256 checked against release SHA256SUMS). Cross-check outputs in ~/.cache/sportorg-stage1/tools/: uv-audit-legacy.json (sha256 83886763…, 123 pkgs, 227 vulns, exit 1), osv-scanner-legacy.json (sha256 af422970…, exit 1); run on a temp copy of legacy pyproject/uv.lock/Cargo.lock.

2026-10-25 W1 inventory returned and accepted (pending commit until check.py is green with batch 1 complete): rerun byte-identical (10 outputs), 9 tests pass, verify_locs 423 tags 0 problems, sample seed 20261025 checked by eye (menu.py:71-76 NewAction -> actions.py:103 ok). Numbers: 102 menu nodes (82 actions, all resolved; 2 classes unused by menu: OpenRecentAction, LiveToggleAction — the latter looked up by name in main_window/toolbar), templates 62 (templates repo) + 8 (pysport), 21 menu->format chains, 28 filter literals, 9 docs. Open: menu filtered at run time by show/feature (menu.py:9-17); FORMAT_MODULES mapping is [допущение].

2026-10-25 Batch 1 accepted and committed: c562024 W1 inventory (AC #1 checked), ab28161 W2 structure (+ sample.py; dead-code manual sample 30: TP 12, FP-string 8, FP-convention 5, FP-enum 2, tests-only 3 -> raw precision 40 %, 58 % with name_in_string; ADR-0007 N3 updated), b802fdd W5 formats (after one rework round: device method calls + protocol encoders/decoders; 113 rows, 277 values; AC #4 checked). Each: rerun byte-identical, verify_locs sample of 10 checked by eye, check.py green, legacy verify ok. Commits need PRE_COMMIT_HOME=$TMPDIR/pre-commit inside the sandbox (~/.cache/pre-commit read-only). AC #2 waits for W3. Next: batch 2 (W3, W4, W6).

2026-10-25 W4 defects returned and accepted (commit waits for a green check.py: W3/W6 files in progress): rerun byte-identical (8 outputs), 8 tests. Numbers: 1142 non-merge, 176 fix (56 conventional + 120 keyword), 168 product defects; issues 46 / PRs 532. Manual 50-commit sample (defects/sample.manual.md, sample.py --where is_merge=false --stratify is_fix, seed 20261025): agreement 47/50 = 94 %, precision 24/25 = 96 %, population-weighted recall ~69 % (CP interval 40-95 %), class agreement 18/24 = 75 % (misses concentrate in 'other': memory.py and old sportorg/app/* paths not in the path table). sample.py gained --where (tests).

2026-10-25 Batch 2 accepted and committed: 75474c0 W4 defects (+ sample.manual.md; AC #3), eef08fb W3 dependencies (own OSV = uv audit = osv-scanner on all records; ADR-0007 N4/N5; AC #2 now complete), W6 os-ru commit (rework round: RU text redaction after person names from test fixtures were found in hits; classification.manual.md: 603 OS hits + 83 core hits, coverage 686/686; AC #5). All six AC checked. Discrepancies to raise in the report: O11 os.startfile crash on Linux/macOS after .docx save (legacy bug candidate); sportident runtime dep has a proprietary classifier (licence vs GPL); PySide6 LGPL/proprietary classifiers unknown; unicode-ident Unicode-3.0 not on allowlist; H2 scope (62 = sportorg/ only); defect path table lacks old sportorg/app/* layout; check_licenses.lock_graph keeps last version per name (latent). Next: Phase E (report, risks, verification prompt).

2026-10-25 Phase E: docs/reports/stage-1.md (Russian report: verdict PROVEN on six AC with limits, hypotheses table, discrepancies R1-R6, questions В1-В6, unproven items), docs/risks.md R17-R20, docs/reports/stage-1-verification-prompt.md (command per number, 4 canaries tested in this session: H1 +1 line -> 2911/219/partly; defects reword 2988024 -> fix 175; menu Save removed -> actions 81; tag edit -> 1 problem), evidence README index complete. Canary base override: 886862a (ARCHAEOLOGY_LEGACY_BASE -> .legacy-run). check.py green, legacy verify ok. Status stays In Progress until the independent verification (AGENTS.md rule 3) and the maintainer's answers. Branch not pushed; Stage 2 not started.

2026-10-25 [мейнтейнер: 2026-10-25] decisions on В1-В6 after the review session (scratchpad report stage-1-review-v1-v6.md, checked by the main session; its claim that codecs give no violations at any rank is wrong for V3: sportiduino/sfrreader/srpid/telegram import serial/pywinusb/requests): В1 H2 confirmed for sportorg/ (scope refined after the result, both numbers kept, brief clarified); В2 Р1 = legacy bug; В3 layer model (а″): libs adapters and I/O codecs -> rank 3, wdb_online_sender_dialog -> ui, pure parsers (iof, wo, wdb, template) stay rank 0, V2 dropped; В4 Р2 reclassified as package-metadata error (GPLv3+), evidence file with primary sources, ADR-0004 single-package exception for sportident, attribution question (Steinlin/Harston) to TASK-10; В5 extend defect classifier (sportorg/app/* -> sportorg/*, memory.py by changed functions) and check on a new 50-commit sample with another seed; В6 Backlog task for check_licenses (versions per name, dependency extras); WdbOnlineSenderDialog status noted in evidence.

2026-10-25 Maintainer decisions on report questions 1-6 implemented. b49f9f5: libs split by role (V1 3+1, V3 3, V2 dropped), H2 confirmed on sportorg/ (78 over all files kept), defect classifier maps sportorg/app/* and classifies memory.py by changed functions (other 50 -> 44). Sample check 2 (seed 20261026, agent judgement): agreement 88 %, precision 92 %, recall ~51 % (CP 32-79 %), pooled ~59 % (41-79 %), class 9/23. Licences from primary sources (dependencies/licence-sources.agent.md), ADR-0004 single-package exception for sportident, attribution question in TASK-10, check_licenses fixes in TASK-11. Wording: sample checks and classification were done by the agent (*.agent.md), no human review. check.py green (266 tests), evidence reruns byte-identical, verify_locs 2867 tags / 0 problems, canaries defects 175/167 and H1 2911/219/partly re-run. Status stays In Progress until the fresh-session verification.

2026-10-25: first independent verification (fresh agent session on 14277d5): items 1, 2, 3, 5 PROVEN; 4 and 6 PARTLY; criterion 4 PARTLY (.srb writer missing). Fixed: formats.py sees file-object parameters (.srb, SFRx export), H3 split QtCore vs UI, sample check 2 relabel #47 and intervals with precision uncertainty, O8 -> discrepancy Р8, O19 basis, fixture names removed from the report. Open for the maintainer: class of Р8, rewriting history for the names in 278826c, copyright-holder names in licence-sources.agent.md. A second fresh-session verification is needed before Done.

2026-10-25 maintainer decisions after the verification: Р8 is a legacy bug; history is not rewritten (the fixture names in 278826c are fictional); copyright-holder names in licence-sources.agent.md stay.
<!-- SECTION:NOTES:END -->
