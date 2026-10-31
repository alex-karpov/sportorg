# ADR-0008: Golden-file protection that does not depend on the agent

- Status: accepted (Stage 2, S1); the signed manifest (c2) is deferred to a later stage
  `[мейнтейнер: 2026-11-01]`, see "Maintainer's decision"
- Date: 2026-10-31
- Scope: `tests/golden/**` (AGENTS.md rule 5), Backlog TASK-8 AC #7. Prerequisite for the first
  golden file (Stage 2 rules, item 5).

## Context
Golden files hold the expected output of the legacy oracle. The likely failure is not an attack but
an agent that "updates the snapshot" so that a red golden test turns green, or edits a golden file
next to a code change without anybody noticing. The protection must work the same way for Claude Code,
Codex, any other agent and humans. Claude Code's PreToolUse guard already asks before an edit under
`tests/golden/` (`scripts/hooks/guard.py`), but only Claude Code runs it; Codex has no equivalent yet
(TASK-3). That guard stays as an early warning and does not count as the protection.

## Options
- **(a) Trailer check.** Every commit that adds, changes, renames or deletes a path under
  `tests/golden/` carries a non-empty `Golden-Approved-By:` trailer (parsed by
  `git interpret-trailers`). Checked by `scripts/golden_guard.py` in `scripts/check.py` (step
  `golden`), CI and the git hooks (commit-msg, pre-push).
- **(b) CODEOWNERS + required review** (branch protection or ruleset on GitHub).
- **(c) Signed hash manifest.** `tests/golden.manifest` (SHA-256 per file) with an
  `ssh-keygen -Y sign` signature by the maintainer. (c1) allowed signers kept in the repository;
  (c2) the maintainer's public key kept outside the repository (for example a GitHub Actions
  variable), so only CI can verify it.
- **(d) Signed commits** (`git verify-commit` on commits that touch golden files). Not measured
  separately: it has the same trust root as (c) (a key out of the agent's reach), and in addition every
  such commit has to be signed.

## Data
Commands: `docs/evidence/stage-2/golden-guard/commands.txt`.

Scenario matrix (`scenarios.md`): one temporary repository per scenario and mechanism, (c) as a
prototype in `scripts/golden_probe.py`, OpenSSH 10.2p1 on WSL2 Ubuntu.

| Scenario | Expected | (a) | (c1) | (c2) |
|---|---|---|---|---|
| add / modify / delete / rename out / change only in a merge resolution, no approval | detected | detected | detected | detected |
| approval words in the body instead of a trailer | detected | detected | detected | detected |
| approved change, code-only change | passed | passed | passed | passed |
| the committer (an agent) writes the approval itself | detected | **passed** | **passed** | detected |
| matches expected, of 9 | | 8 | 8 | 9 |

Canary on a clone of this repository (`canary.json`): a golden commit without the trailer makes
`scripts/check.py --only golden` exit 1; the same commit with the trailer exits 0.

Facts (`facts.json`, history at `aeb6cb7`, GitHub API of 2026-10-31):
- 30 commits; 27 carry the `Co-Authored-By: Claude` trailer, and all 27 have one author identity.
  The agent commits under the maintainer's identity, so neither the author nor the pusher tells an
  agent's commit from the maintainer's.
- 2 of 30 commits are signed: commit signing is not in use.
- The repository is public, owned by a user, has 1 collaborator, 0 rulesets, `main` is not
  protected. The maintainer merges locally and pushes `main` `[история: d3a6b56]`.

## Evaluation
- (a) catches every accidental or silent change, including a rename out of the directory and a change
  made only in a merge, and gives the agent feedback in the same loop as the other checks (local
  `check.py`, offline, git only, on all three OS). It does not stop a committer who writes the trailer
  without approval. Such a commit breaks rule 5 explicitly and leaves a record: `check.py` and CI
  print every approved golden commit (`approved by …: <subject>`), and `git log --grep
  Golden-Approved-By` lists them.
- (b) does not fit this repository. With one collaborator, a required review would need someone who
  is not the author of the pull request. GitHub does not let the author approve their own pull request
  `[допущение: GitHub documentation not fetched in this session]`. The admin bypasses the rule, and the
  admin is the account that pushes the agent's commits. The rule also covers only pull requests,
  while `main` is pushed directly. The settings live outside the repository, so a verifier cannot
  reproduce them from a checkout, and the agent learns about the problem only on GitHub.
- (c1) behaves like (a): whoever can commit can also replace the allowed signers file.
- (c2) is the only option that stops a forged approval, but only while the agent cannot reach either
  the maintainer's private key or the token that edits repository variables. On this machine the
  agent runs under the maintainer's account and `gh` is logged in with the maintainer's token (used
  for the facts above), so that separation does not hold today `[допущение: the key would be on the
  same machine]`. It also costs a key ceremony for every golden change on every OS. A local
  `check.py` can verify only (c1), so in the edit loop (c2) adds nothing over (a).

## Decision
**(a)**, implemented in `scripts/golden_guard.py` with tests in `tests/scripts/test_golden_guard.py`
(Review Focus 1–3 of `docs/plans/stage-2-oracle.md`) and the canary in
`tests/scripts/test_golden_probe.py`, which runs in CI on all three OS.
- Range: commits reachable from HEAD but not from the merge-base with `origin/main` (else `main`),
  plus commits after `GOLDEN_BASE`. CI sets `GOLDEN_BASE` to the pull-request base or the pushed
  `before`, so pushes to `main` are checked too. CI checks out with `fetch-depth: 0`. If the base is
  unknown and the range is empty, the check fails closed.
- Each commit needs its own trailer. For a merge, only paths that differ from every parent count
  (`git diff-tree --cc`). Paths are compared case-insensitively; renames count as delete plus add.
- Writing the trailer: only after the maintainer's confirmation (AGENTS.md rule 5). An agent that
  commits on the maintainer's behalf writes the date of the confirmation in the trailer value.
- Uncommitted golden changes are reported as a note, not a failure: `check.py` must be able to pass
  before the commit that will carry the trailer. The commit-msg hook checks the staged changes against
  the message. Run `pre-commit install` again to get the new `commit-msg` hook type.

Observed in CI `[история: GitHub Actions run 41222366113, stage-2@dab1040, 2026-10-31]`. All seven jobs
passed: Linux, Windows and macOS on 3.14 and 3.15, plus the clean machine. In each, the `golden` step
printed `ok: no unapproved changes under tests/golden/`. `GOLDEN_BASE` was zeros (the first push of the
branch), so the check fell back to the merge-base with `main` as designed. 329 tests passed, the canary
among them. A red CI run caused by a real unapproved golden commit was not observed. The canary runs the
same command (`scripts/check.py --only golden`) on a clone inside those jobs.

## Maintainer's decision `[мейнтейнер: 2026-11-01]`
The question was: stop forged approvals now with (c2), or only make them visible with (a)? Options were
(i) keep (a) now, (ii) set up (c2) now, (iii) add (b) once a second collaborator exists. Decision: (i).
The move to (c2) (session "S1b") is deferred to a later stage.

(c2) adds strength only when all three conditions hold at once; one unmet condition leaves a bypass:
1. **The signing key is out of the agent's reach.** A dedicated key with a passphrase, never loaded
   into an ssh-agent, or a hardware key that needs a touch. Without it, the agent signs a changed
   manifest itself.
2. **The agent's GitHub token cannot change repository variables or settings.** A fine-grained token
   without Administration, Variables or Secrets; admin actions only in the browser. Without it, the
   agent replaces the trusted public key.
3. **Changes to the checking code are reviewed before they reach `main`.** That code is
   `.github/`, `.pre-commit-config.yaml`, `.claude/settings.json`, `AGENTS.md`, `pyproject.toml`,
   `scripts/check.py`, `scripts/golden_*.py`, `scripts/hooks/` and `tests/golden/`. Without the review,
   the agent removes the check itself. This holds for (a) too. Since 2026-11-01 the pre-push hook
   `protected-files` (`python -m scripts.golden_guard protected`) prints these files and the `git diff`
   command on every push. It informs and never blocks: the review itself is the maintainer's.

## Revisit
- an agent commit with the trailer is found without a recorded confirmation of the maintainer;
- agents get commit or push rights without a human in the session;
- the maintainer has a signing key that agents cannot reach: then (c2) on top of (a).
