# Plugin source inventory (read-only; facts only)

Roots: SP = C:\Users\USER\.claude\plugins\cache\claude-plugins-official\superpowers\7.0.0\
       CM = C:\Users\USER\.claude\plugins\cache\claude-plugins-official\code-modernization\1.0.0\
Neither plugin has `.mcp.json` / MCP servers.

======================================================================
# A. SUPERPOWERS 7.0.0
======================================================================
## A1. Manifest
- SP.claude-plugin/plugin.json: name `superpowers`, version `7.0.0`, description "Core skills library for Claude Code: TDD, debugging, collaboration patterns, and proven techniques" (author Jesse Vincent, MIT).
- Commands: none (no `commands/` dir). Agents: none (no `agents/` dir). MCP: none.
- Skills (SP.skills/<dir>/SKILL.md, `description:` at line 3 of each):
  - brainstorming: "You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it..."
  - diagnosing-superpowers: "Use when a superpowers session went wrong and your human partner wants to know why ... or wants to build a bug report for the superpowers maintainers..."
  - dispatching-parallel-agents: "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies"
  - executing-plans: "Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available"
  - finishing-a-development-branch: "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work"
  - receiving-code-review: "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable..."
  - requesting-code-review: "Use when completing tasks, implementing major features, or before merging to verify work meets requirements"
  - subagent-driven-development: "Use when executing implementation plans with independent tasks in the current session"
  - systematic-debugging: "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes"
  - test-driven-development: "Use when implementing any feature or bugfix, before writing implementation code"
  - using-git-worktrees: "Use when starting feature work that needs isolation from current workspace or before executing implementation plans..."
  - using-superpowers: "Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions"
  - verification-before-completion: "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always"
  - writing-plans: "Use when you have a spec or requirements for a multi-step task, before touching code"
  - writing-skills: "Use when creating new skills, editing existing skills, or verifying skills work before deployment"
- Hooks: SP.hooks/hooks.json (only one):
  - event `SessionStart`, matcher `startup|clear|compact`, command `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start`, `"shell": "bash"`, async false.
  - What it does: SP.hooks/session-start reads skills/using-superpowers/SKILL.md and injects it as additionalContext wrapped in `<EXTREMELY_IMPORTANT>You have superpowers...`. Writes nothing to disk.
  - (hooks/hooks-cursor.json exists for Cursor; not used by Claude Code.)
- Scripts: SP.scripts/ = maintainer tooling only (bump-version.sh, lint-shell.sh, package-codex-plugin.sh, render-antigravity-logo.sh, sync-to-codex-plugin.sh). Skill-embedded scripts: skills/brainstorming/scripts/{start-server.sh, stop-server.sh, server.cjs, helper.js, frame-template.html}; skills/executing-plans/scripts/{task-start, task-done}; skills/subagent-driven-development/scripts/{sdd-workspace, task-brief, review-package}; skills/systematic-debugging/find-polluter.sh.

## A2. Files the plugin writes (path | skill | content | task-list/status that could duplicate an external tracker?)
1. `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | brainstorming | design spec, committed. brainstorming/SKILL.md:156-158: "**Where it goes:** in a software repo, `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed. Otherwise, ask. Your human partner's preferences override both." | Spec prose (intent, goals, constraints); no checkboxes. Tracker duplication: no.
2. `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` | writing-plans | implementation plan. writing-plans/SKILL.md:16: "**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`" and line 17 "(User preferences for plan location override this default)". Header line 59: "Steps use checkbox (`- [ ]`) syntax for tracking." Steps at lines 108-132: `- [ ] **Step 1: Write the failing test**` ... `- [ ] **Step 5: Commit**`. | YES: task list with checkboxes (task/step granularity, committed in repo).
3. `<repo-root>/.superpowers/sdd/<plan-basename>/progress.md` (the "ledger") | executing-plans (SKILL.md:118-139) and subagent-driven-development (SKILL.md:125-150) | git-ignored per-plan workspace; first line `# SDD ledger — plan: <plan file path>`; lines `Task <N>: complete (commits abc..def, tests: <cmd> → <last line>)` (task-done script; SKILL.md:343). executing-plans:118-119: "Track progress in a ledger file, not only in todos. Harness todos are a live view; the ledger is the record." | YES: per-task completion/status record (git-ignored scratch, but is a progress tracker). Also creates a harness todo per task (executing-plans:144 "create a todo per task").
4. `.superpowers/sdd/<plan-basename>/task-<N>-brief.md`, `task-<N>-tests.log`, implementer reports, review packages | task-brief / task-done / review-package scripts | briefs, test logs, review diffs | briefs/logs: no. Workspace gets self-ignoring `.gitignore` containing `*` at `.superpowers/sdd/` (sdd-workspace:84-86). `git clean -fdx` destroys it (executing-plans:140). Deleted after final review (executing-plans:103 "Final review clean: delete this plan's workspace").
5. `.superpowers/brainstorm/<pid>-<ts>/{content,state}` | brainstorming visual companion (visual-companion.md:42-58,294) | HTML mockups/state; falls back to `/tmp` without `--project-dir`. Tells user to add `.superpowers/` to .gitignore. | no.
6. `.worktrees/` or `worktrees/` at repo root | using-git-worktrees (SKILL.md:71-83,150-153); finishing-a-development-branch:169 cleans only those | git worktrees; verifies path is git-ignored via `git check-ignore`. Default `.worktrees/` if no other guidance. | no.
7. `~/.superpowers/diagnosing-superpowers/<session-id>/` (report.md, case.md, bundle) | diagnosing-superpowers (SKILL.md:33, templates/report.md:3) | diagnostic reports | no.
8. `~/.config/superpowers/hooks/` appears only as an example user-level option in an SDD transcript example (subagent-driven-development/SKILL.md:519); not written by the plugin.
- Other skills (verification-before-completion, TDD, debugging, code-review skills) write no files.

## A3. writing-plans / executing-plans / SDD detail
- writing-plans: reads a spec; writes plan to docs/superpowers/plans/...; plan header has `**Spec:** [path ...]` (line 67); offers choice SDD vs executing-plans (lines 189,198: "Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Please review the plan. Which execution approach would you prefer?").
- executing-plans: reads plan once + spec; runs `../subagent-driven-development/scripts/sdd-workspace PLAN_FILE`; checks `<workspace>/progress.md` for `Task <N>: complete` to resume; per task `task-start` (prints BASE sha, makes brief) and `task-done PLAN_FILE N BASE -- TEST_CMD` (runs tests, appends ledger line only on success; "A failing command records nothing"). Loads test-driven-development before Task 1; verification-before-completion governs (executing-plans:219). Requires isolated worktree: "Never start implementation on a main/master branch without your human partner's explicit consent." (executing-plans:111-113; same in SDD:125-128).
- subagent-driven-development: same workspace and ledger format (so executors can swap mid-plan); dispatches implementer/reviewer subagents with implementer-prompt.md, task-reviewer-prompt.md, re-review-prompt.md; plan conflict-scan table before Task 1 (SKILL.md ~160-175).
- Whether the plan file's own `- [ ]` boxes are ticked by the agents: not stated in the lines read; scripts record progress only in the ledger.

## A4. verification-before-completion (SKILL.md)
- Iron Law (lines 14-18): "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"; "If you haven't run the verification command in this message, you cannot claim it passes."
- Gate: IDENTIFY command -> RUN full command fresh -> READ full output/exit code/failure count -> VERIFY -> only then claim.
- Table: tests pass requires test output 0 failures (not previous run); build requires exit 0 (not linter); bug fixed requires original symptom test; regression test requires red-green cycle; agent completed requires VCS diff; requirements met requires line-by-line checklist. Applies before commit/PR/task completion/delegating. Writes no files; no fresh-session requirement.

## A5. External trackers
- grep of `backlog|issue|ticket|Jira|Linear|TodoWrite|todo` across skills: no mention of Jira, Linear, backlog, or tickets as an external tracker. "issue(s)" appears only as code-review severity/generic wording (requesting-code-review, receiving-code-review, dispatching-parallel-agents). Tracking constructs present: harness todos (executing-plans:144, :332 "[Create todos for all tasks]"), the ledger, and plan checkboxes. diagnosing-superpowers/references/github-issues.md concerns filing bug reports to superpowers maintainers (not project tracking).

## A6. OS notes
- Hook is bash via polyglot `hooks/run-hook.cmd`, which on Windows searches for Git for Windows bash (`C:\Program Files\Git\bin\bash.exe` etc.; run-hook.cmd ~lines 15-24); documented in SP.docs/windows/polyglot-hooks.md. session-start has Windows/Git-Bash EPIPE workarounds.
- SDD/executing-plans scripts (`task-start`, `task-done`, `sdd-workspace`, `task-brief`, `review-package`) are extensionless `#!/usr/bin/env bash` scripts (need bash on Windows). brainstorming start-server.sh has explicit Windows/MSYS detection (lines 82-105,161-165).

======================================================================
# B. CODE-MODERNIZATION 1.0.0
======================================================================
## B1. Manifest
- CM.claude-plugin/plugin.json: name `code-modernization`, version `1.0.0`, description "Guided modernization for any legacy codebase: start with /modernize, get an assessment, an interactive map, the business rules mined from the code, and a plan you approve, then an upgrade, a rewrite or a rebuild with independent proof that the new code behaves like the old. Includes security hardening, a one-page report, specialist agents, and an optional live progress pane (early access)." (author Anthropic). userConfig keys: system, track (auto|transform|uplift|reimagine), panel (auto|command|off), xray (bool, true), commandPrefix (`/code-modernization:modernize-`), legacyDir (`legacy`), telemetry (bool, true).
- Skills: none (no `skills/` dir). MCP: none.
- Commands (CM.commands/*.md; `description:` at line 2):
  - modernize: "Start here — say what you want done with your code and get the plan and the first step"
  - modernize-preflight: "Run this first — checks the environment, records where the code lives, and says what to fix before anything else runs"
  - modernize-assess: "What am I dealing with? Inventory, complexity, debt, security and a recommended modernization pattern"
  - modernize-map: "Show me the structure — dependencies, data flow, entry points and business flows, as an interactive map"
  - modernize-extract-rules: "Mine the business rules out of the code into testable Given/When/Then rule cards with file:line citations"
  - modernize-review: "Confirm or correct the business rules that need a person's judgement; the plan and the build read your answers"
  - modernize-brief: "Write the phased Modernization Brief — the plan a steering committee approves and the build commands execute against"
  - modernize-transform: "Rewrite one legacy module in the target stack, with tests that prove it behaves the same"
  - modernize-uplift: "Same-stack version uplift (e.g. .NET Framework 4.8 to .NET 8, Java 8 to 17) — keep the code, fix the version deltas, prove nothing changed"
  - modernize-reimagine: "Rebuild the system from its extracted intent on a new architecture, with two human checkpoints"
  - modernize-verify: "Prove the modernized code behaves like the legacy, with an independent re-check and one verdict per module"
  - modernize-harden: "Security scan of the legacy system with a reviewable remediation patch (OWASP, CWE, CVEs, secrets, injection)"
  - modernize-status: "Where am I? Progress, what is stale, and the exact next command to run — start here when unsure"
  (README also mentions pane commands `/modernize-panel`, `/modernize-review-pane`, provided by hooks/register.ts.)
- Agents (CM.agents/*.md, `description:` line 3): architecture-critic; business-rules-extractor; legacy-analyst; scaffolder; security-auditor; test-engineer; uplift-migrator; version-delta-analyst. (e.g. test-engineer: "Writes characterization, contract, and equivalence tests that pin down legacy behavior so transformation can be proven correct. Use before any rewrite.")
- Workflows (CM.workflows/): extract-rules.js, harden-scan.js, portfolio-assess.js, reimagine-scaffold.js, uplift-deltas.js, uplift-migrate.js.
- Hooks (CM.hooks/hooks.json), all `type: command`, no matchers, timeout 10, asyncRewake true, command `sh "${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.sh" <arg>`:
  - UserPromptSubmit -> `command`; Stop -> `state` and `run`; SessionStart -> `health`; PostToolUseFailure -> `failure`; StopFailure -> `failure`.
  - plus `"modules": ["./register.ts"]` (function hooks / live pane; hooks/README.md:5-9: needs `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, otherwise the pane never loads). hooks/*.ts read analysis/ and modernized/ for the pane; x-ray reads attach context on legacy file reads (userConfig `xray`).
  - Telemetry: whole-number counts via Claude Code telemetry; off via userConfig `telemetry`, `CODE_MODERNIZATION_TELEMETRY=0`, or `DISABLE_TELEMETRY=1` (README "Telemetry"). Fallback temp dir `${TMPDIR:-/tmp}/code-modernization-<uid>` (scripts/telemetry.sh:59).
- Scripts (CM.scripts/): baseline_diff.py, build_report.py, compare.py, make_shards.py, proof_pack.py, render_rules.py, telemetry.py, telemetry.sh, trace_rules.py, uplift_checks.py, tests/.

## B2. Files written (relative to workspace root). README: "Nothing edits your legacy source. Commands write only to `analysis/<name>/` and `modernized/` ..."
| Command | Path | Content | Task list / status duplicating a tracker? |
|---|---|---|---|
| modernize | `analysis/$system/INTENT.md` (modernize.md:48) | goal, from/to, "what must stay true", date, user answers | no |
| preflight | `legacy/<name>` link (preflight.md:22-26): `mkdir -p legacy && ln -s <abs path> legacy/$system` (Windows: `cmd /c mklink /J legacy\$system <abs>`) | symlink/junction to the code | no |
| preflight | `analysis/$system/PREFLIGHT.md` (:196) | 5 human answers, scope boundary, build checks | no (answers/state) |
| preflight | `.claude/settings.json` (proposes deny-rule merge, :166-181) | `permissions.deny` for legacy | no |
| assess | `analysis/$system/ASSESSMENT.md`, `ARCHITECTURE.mmd`, `analysis/portfolio.html` (portfolio mode), `analysis/$system/REPORT.html`, `analysis/$system/SECRETS.local.md` (gitignored; else `~/.modernize/$system/`), `analysis/.gitignore` (assess.md:50,120-157) | assessment, diagram, masked credential inventory | no |
| map | `analysis/$system/map/<chunk>.json`, `extract_topology.py` or `.sh`, `topology.json`, `TOPOLOGY.html` (map.md:33-189) | dependency graph and viewer | no |
| extract-rules | `analysis/$system/extract-rules.modules.json`, `rules_result.json` (:30,:90), `BUSINESS_RULES.md`, `DATA_OBJECTS.md` (:98,:119) | rule cards `### RULE-NNN: <name>` Given/When/Then with file:line, P0/P1/P2, SME question list | no tasks; rule catalogue. :138 "Headings are exactly `### RULE-NNN: <name>`, numbered in sequence: later commands find rules by..." |
| review | `analysis/$system/RULE_REVIEWS.json` (merged), `RULE_REVIEWS.md` (review.md:7-31) | per-rule verdict (confirmed / wrong / discuss) | per-rule decision status; not a task list |
| brief | `analysis/$system/MODERNIZATION_BRIEF.md` (brief.md:46) | phased plan; exit criteria checkboxes at lines 77/79 `- [ ] <a condition that can be checked>`; §7 Open Questions "each a checkbox the approver ticks" (:117-118); build commands "may tick a box or add a note but never reword a criterion" (:91) | YES: phased plan with checkbox exit criteria and open questions |
| transform | `modernized/$system/<module>/src/test/`, `src/main/`, `TRANSFORMATION_NOTES.md` (transform.md:52-93); `analysis/$system/equivalence/legacy/`, `.../new/`, `equivalence/cases.json`, `EQUIVALENCE.json` (:80-83) | code, tests naming RULE-NNN, mapping notes, old-vs-new output pairs | no |
| uplift | `modernized/$system-uplifted/` working copy (`rsync -a --exclude .git legacy/$system/ modernized/$system-uplifted/` :66, or `git worktree add --detach` :73), `analysis/$system/DELTA_CATALOG.md` (:104), `BASELINE.md` (:143), `baseline/` (:146), `PLAYBOOK.md` (:180), `modernized/$system-uplifted/UPLIFT_NOTES.md` (:254) | delta catalog, measured baseline table, pilot playbook | BASELINE.md has an "Approved differences" table `| Test | Reason |`; not a task list |
| reimagine | `analysis/$system/AI_NATIVE_SPEC.md` (:35), `REIMAGINED_ARCHITECTURE.md` (:54), `modernized/$system-reimagined/<service>/` (:77-87), `modernized/$system-reimagined/CLAUDE.md` (:94, handoff context for the new system) | spec, architecture, scaffolds | no |
| verify | `analysis/$system/equivalence/<suite>.test-output.txt`, `equivalence/canary/<module>/`, `equivalence/cases.json` + `fresh-cases.json`, `equivalence/fresh/{legacy,new}/<id>/`, `equivalence/FRESH_EQUIVALENCE.json`, `analysis/$system/EQUIVALENCE.json`, `equivalence/test-runs.json`, `analysis/$system/VERIFICATION.md` + `VERIFICATION.json` (verify.md ~60-122) | evidence + verdict | VERIFICATION.md has a "blank sign-off block"; verdict per module is a status record |
| harden | `analysis/$system/SECURITY_FINDINGS.md` (:68), `SECRETS.local.md` (:77, gitignored), `security_remediation.patch` (:89), `security_remediation.local.patch` (gitignored :92); apply with `patch -p1 -d legacy/$system < analysis/$system/security_remediation.patch` (:115) | findings + patch | findings list; not tasks |
| status | refreshes `analysis/$system/REPORT.html` via `python3 scripts/build_report.py` (status.md:8) | one-page report with tabs for assessment/map/rules/plan/proof, computed "Next" command | computed status view |
| (assess/harden) | `~/.modernize/$system/` fallback for secrets when not git-ignored | secrets | no |
- README "Working in a team": "State lives in files, not in chat... The commands never commit to your repository, so commit `analysis/` and `modernized/` yourself."

## B3. Command chain and data flow
Order (README table "The path"): modernize(0) -> preflight(1) -> assess(2) -> map(3) -> extract-rules(4) -> review(4b) -> brief(5) -> uplift | transform | reimagine (6) -> verify(7) -> harden(8); `status` any time.
- modernize writes INTENT.md; brief takes its target stack from it (modernize.md:49-50).
- extract-rules reads `topology.json` (if map ran) to make shards -> `extract-rules.modules.json` (extract-rules.md:28-30) -> workflow output `rules_result.json` -> script writes BUSINESS_RULES.md (:90-98). Needs `legacy/$system`, else stops (:13).
- review reads BUSINESS_RULES.md (+ existing RULE_REVIEWS.json), writes RULE_REVIEWS.json/.md; transform reads them: "a rule marked `wrong` is not pinned as the oracle" (transform.md:42).
- brief reads everything in analysis/$system/; target stack from arg else INTENT.md (brief.md:7-9). README: "Nothing is built until you approve it."
- transform/uplift/reimagine: "The brief is binding" (uplift.md:58, reimagine.md:15); transform reads MODERNIZATION_BRIEF.md (:12), BUSINESS_RULES.md, RULE_REVIEWS.json; uplift gate: "`analysis/$system/BASELINE.md` must exist" (uplift.md:156); uplift can skip extract-rules/review (README).
- verify reads modernized/ outputs, BUSINESS_RULES.md (via trace_rules.py), cases.json, BASELINE.md, DELTA_CATALOG.md, INTENT.md ("What must stay true"), PREFLIGHT.md (legacy mtime check).

## B4. Where rules / evidence / verdicts are stored
- Extracted rules: `analysis/$system/BUSINESS_RULES.md` (RULE-NNN cards, Given/When/Then, file:line, P0/P1/P2), `DATA_OBJECTS.md`, raw `rules_result.json`; reviewer verdicts in `RULE_REVIEWS.json/.md`.
- Equivalence evidence: `analysis/$system/equivalence/` (cases.json, legacy/ and new/ outputs, fresh/, canary/, *.test-output.txt, test-runs.json, FRESH_EQUIVALENCE.json) and `analysis/$system/EQUIVALENCE.json` (compare.py output).
- Verdicts: `analysis/$system/VERIFICATION.md` / `VERIFICATION.json`, written by `scripts/proof_pack.py`. Verdict words PROVEN / PARTLY PROVEN / NOT PROVEN (verify.md:2,5-6). README: PARTLY PROVEN = "with what is missing"; NOT PROVEN = "nothing ran, something differs, a test fails". verify.md:7: "A script computes the verdict, not you". If legacy cannot run: "the proof is then trace-based and the verdict cannot be PROVEN" (verify.md ~line 100). End of verify.md: "PROVEN: it is evidence, not approval. A named person signs `analysis/$system/VERIFICATION.md`".
- Status rules: "A built module with no `VERIFICATION.md`, or one older than the module's code or tests, is **not proven yet**" (status.md:31); "built module done until `verify` says PROVEN and a person has signed it" (status.md:57).

## B5. /modernize-verify requirements (verify.md)
- Args `<system> [module]`. Run from workspace root (line 13). Requires built output: `modernized/$system/<module>/`, or `modernized/$system-uplifted/`, or `modernized/$system-reimagined/<svc>`; "If nothing is built, say so and stop" (~line 28). Requires `legacy/$system` (says where it points via `readlink`).
- Needs python3 + scripts (trace_rules.py, compare.py, baseline_diff.py, proof_pack.py, build_report.py), the module's real test toolchain, and for a rewrite `BUSINESS_RULES.md`, `equivalence/cases.json` if present, `INTENT.md`; for uplift `BASELINE.md`, `DELTA_CATALOG.md`.
- Procedure: delete build output and caches, run full suite, keep JUnit XML or raw log (never typed counts); canary in a scratch copy outside modernized/ and analysis/; invent at least 10 fresh inputs; write `test-runs.json`, run proof_pack.py; never edit legacy, built code, outputs; never tick/approve person-owned items; run subagents in the foreground; stop servers it started; check DB/service config is local/throwaway or stop and ask (verify.md:15-16).
- Fresh session: "Run it after `transform`, `uplift` or `reimagine`, in a fresh session if you can: what the build left behind is a claim, and this command re-runs it." (verify.md:5-6); README: "ideally in a fresh session". A recommendation, not enforced by any hook found.
- Human decision points (README): preflight answers, rules that look wrong, approving the brief, accepting proof differences, signing the proof, applying the security patch.

## B6. OS-specific / Windows notes
- README: Python 3.8+ as `python3` ("on Windows `python` or `py -3` works"); commands invoke `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/*.py"` literally (verify.md, map.md:157, etc.).
- Hooks run via `sh "${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.sh"`: needs POSIX `sh` (Git Bash). README: "A machine where the shell cannot start the hooks at all (for example Windows without Git Bash) sends nothing". telemetry.sh detects MSYS/Cygwin/WSL and the Windows Store python stub, and flags folder paths with spaces / non-ASCII / over 200 chars as ones that "break scripts on Windows" (telemetry.sh:45; telemetry.py:397). Falls back to `${TMPDIR:-/tmp}` (telemetry.sh:59).
- preflight symlink: `ln -s` with Windows alternative `cmd /c mklink /J legacy\$system <abs>` (preflight.md:24-25); also `readlink`, `mktemp -d` (:116). preflight.md:172-182 advises an extra deny rule for the real symlink target (`Edit(//real/path/**)`).
- Commands rely on POSIX tools: `readlink`, `rsync -a` (uplift.md:66), `mktemp -d`, `patch -p1`, `tee`, `git worktree add`, `scc`/`cloc`; command markdown contains ```bash blocks (extract-rules.md:24,94).
- Live pane requires env `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` and TypeScript hooks (hooks/*.ts); README says tested on Claude Code 2.1.280.
- Artifact dirs `analysis/`, `modernized/`, `legacy/` are created at the workspace (repo) root; `legacyDir` default `legacy`.
