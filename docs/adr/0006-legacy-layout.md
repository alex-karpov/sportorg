# ADR-0006: Legacy as pinned, git-ignored, read-only clones in `.legacy/`

- Status: accepted — the layout and its protection `[мейнтейнер: 2026-10-24, decision 7]`, the two
  public repositories `[мейнтейнер: 2026-10-25]`; probed on Windows and in WSL2 (Backlog TASK-1)
- Date: 2026-10-24, sources 2026-10-25
- Supersedes: ADR-0005 decision 4 (absolute deny rule)
- Evidence: `docs/evidence/stage-0/legacy-layout/` (README, commands, probe outputs),
  `scripts/probe_legacy_protection.py`, `tests/scripts/test_guard.py`

## Context
Stage 0 kept legacy as the maintainer's sibling checkout `../_other/pysport-legacy`, protected by the
deny rule `Edit(//c/Users/USER/Prog/Orient/_other/**)` and a textual guard. The independent reviews of
2026-10-24 found: the absolute path only works on one Windows machine (not in WSL, the recommended
agent environment, ADR-0003) and puts a username into a public repository; the guard matched only the
marker `pysport-legacy`, so commands through code-modernization's junction `legacy/sportorg` passed
unchecked; the legacy path was hard-coded in 13 places (7 scaffolds, 3 scripts, guard, tests).
The maintainer decided: clone inside the repository, git-ignored, pinned SHA, without write bits,
portable rule `Edit(/.legacy/**)`, guard on resolved paths; probe on Windows and in WSL first.

## Options
| Option | For | Against |
|---|---|---|
| (a) Sibling checkout + absolute deny rule (Stage 0) | nothing to fetch | machine-specific rule, username in history, not pinned (it is the maintainer's working checkout with their own branches) |
| (b) git submodule at the pinned commit | pin recorded by git itself | a writable working tree that agents can commit in; pointer churn in project history; the pinned commit must be public |
| (c) Vendored copy committed to this repository | no fetch step | 19 MB of legacy in project history; template `.docx` files with an e-mail and phone numbers would enter the repository (AGENTS.md rule 8); legacy and product mixed |
| (d) **Git-ignored clone `.legacy/<name>` at the pinned commit, locked read-only, fetched by a script from a manifest** | portable rule, one place for paths, pinned and verifiable | a fetch step; the pinned commit must be reachable from the manifest URL (open, below) |
| (e) Link `legacy/…` to the sibling checkout | no copy | link targets were refused only by a permission prompt in the probe, not by the deny rule; still not pinned |

## Data (2026-10-24, Windows 11 + WSL2 Ubuntu, Claude Code 2.1.310)
- Agent probe, Windows, rule `Edit(/.legacy/**)` only (files writable): 15 of 16 write attempts
  refused — Edit by relative, absolute, `src/..`, upper-case and junction paths, Write, Bash `>>`,
  `sed -i`, `cp`, `mv`, `rm`, PowerShell `Set-Content`/`Remove-Item`. Passed: `python -c "open(…)"`
  (documented gap: subprocesses that open files themselves). Read and a control edit worked.
- Agent probe, WSL2 (2026-10-25), same rule and steps: 12 of 13 write attempts refused with the same
  messages; passed again only `python3 -c "open(…)"`; the two PowerShell steps do not apply on Linux.
- Same probe in WSL2 with the Claude Code Bash sandbox in auto-allow mode (2026-10-25): 13 of 13
  refused. Edit/Write by the rule as before; every Bash step, `python3 -c "open(…)"` included, ran
  without a permission check and failed with "Read-only file system" on writable files.
- File modes, no agent: WSL ext4 with `chmod a-w` — 9 of 10 blocked (the owner can `chmod u+w` back).
  Windows read-only attribute — 5 of 14 blocked (`sed -i`, `cp`, `mv`, `rm`, `git rm`, `chmod u+w`,
  `Remove-Item -Force` pass). Windows attribute + inherited deny ACE (write, append, attributes,
  delete, delete-child) — 14 of 14 blocked, reading unaffected. `icacls /deny` cannot express that
  ACE (it widens it to `W`, which includes SYNCHRONIZE and breaks reading); PowerShell 7 `Set-Acl` can.
- Live check in this repository after the change: Edit of `.legacy/pysport/README.md` →
  "File is in a directory that is denied by your permission settings." (the rule, not the guard).
- `uv run python -m scripts.legacy fetch --source pysport=../_other/pysport-legacy`: 1.4 s, 19 MB;
  `verify` → `ok: pysport@30d849dde1f7 locked`; `git log`/`git status` keep working on the locked clone.
- After the decision on sources (2026-10-25), `fetch` without `--source`: 6.9 s from GitHub, replaced
  pysport 30d849d by b548c35 (15 MB) and cloned templates (1.7 MB); `verify` →
  `ok: pysport@b548c35ba18f, templates@cd953823beb3 locked`. Same in WSL2 on a fresh ext4 clone of
  `stage-0` from GitHub: `fetch` 7.2 s, `verify` ok, modes `dr-xr-xr-x`/`-r--r--r--`.

## Decision
1. **Layout.** `legacy.toml` lists each pinned repository (name, URL, 40-character commit).
   `uv run python -m scripts.legacy fetch` clones it into `.legacy/<name>` (`--no-hardlinks`, so no
   object file is shared with the source) and locks it; `verify` checks HEAD, a clean tree and the
   lock. `scripts/legacy.py` is the only place that knows these paths; from a git worktree it finds
   the main checkout. Executable copies: `uv run python -m scripts.legacy_clone` → `.legacy-run/<name>`.
2. **Lock.** Write bits removed (executable bits kept, so `git status` stays clean); on Windows also
   the deny ACE above. A pin update is an edit of `legacy.toml` by the maintainer's decision; `fetch`
   then clones the new commit and replaces the old checkout only if its working tree is clean (tested
   in `tests/scripts/test_legacy.py`). `unlock`/`lock` remain for manual maintenance.
3. **Claude Code rules.** `.claude/settings.json` denies `Edit(/.legacy/**)` and `Edit(/legacy/**)`
   (the code-modernization junction `legacy/sportorg → .legacy/pysport`). No absolute paths are
   committed; a maintainer may add machine-specific rules in `.claude/settings.local.json`.
4. **Guard.** File tools: the path as written and after `resolve()` (links, junctions, `..`, case).
   Shell: every simple command of a compound command is classified by verb; `cd` into legacy is
   tracked; redirection targets, `git`/`uv` subcommands, `bash -c` and command substitutions are
   inspected; reading and copying out stay allowed. The hook always exits 0 and turns its own errors
   into `ask` (Stage 0 incident).

| Write path | Deny rule | Guard | File modes (Linux / Windows with ACE) |
|---|---|---|---|
| Edit/Write/NotebookEdit | yes | yes (resolved path) | yes / yes |
| Shell commands naming legacy | redirections and file commands Claude Code recognises | yes (best effort) | yes / yes |
| Subprocess opening files itself | no | no | yes / yes |
| Owner restoring write access | no | denies `chmod`/`attrib`/`icacls` on legacy | no / yes |
| Session started in a subdirectory or worktree | no (`/path` anchors at the session's start directory) | yes | yes / yes |

With the Claude Code Bash sandbox on (WSL2, Linux, macOS; not native Windows, ADR-0003), the deny rule
also covers everything Bash starts, subprocesses included (probe above). The repository's settings do
not turn the sandbox on, so the table does not count on it.

## Sources of the pins: two repositories `[мейнтейнер: 2026-10-25]`
The first pin, `30d849d`, was the maintainer's local commit "feat: add russian templates" on top of
upstream `b548c35`; it existed only in the local branch `templates`, so nobody else could fetch it. It
differs from upstream only under `sportorg/data/templates/` (69 files added, 2 changed). Options were:
- **A — one fork:** push the branch to the existing public fork `alex-karpov/pysport`, keep `30d849d`.
  One SHA; templates stay mixed with code; every upstream update means a rebase and a new SHA.
- **B — two repositories (chosen):** `pysport` at upstream `b548c35` from `sportorg/pysport` plus a
  templates repository with the Russian set at its own pinned commit (a fork of `sportorg/templates`,
  which upstream split out of the app in 2024 and has not updated since). Code and templates are
  pinned and updated independently. Of the 69 added templates, 19 are identical to
  `sportorg/templates`, 25 are newer versions of its files and 25 are new.

Result, as pinned in `legacy.toml`:
- `pysport` = `sportorg/pysport@b548c35`, current upstream `master`; same code as `30d849d`.
- `templates` = `alex-karpov/sportorg-templates@cd95382`: `ru/` holds the 61 HTML templates of
  `30d849d`, byte-identical, and one `.docx`, the Cup-of-Russia diploma re-saved by the maintainer
  with empty author, last-modified-by and company properties (text and its 25 template tags unchanged).
  The other `.docx` templates are not in the tree: their text or document properties name people or
  carry contact details (one e-mail address, three phone numbers, eight author names). The ten that
  upstream had already published stay in that repository's history; the six that existed only in
  `30d849d` were never published. A scan of the tree before the push found no e-mail address, phone
  number or author name (`docs/evidence/stage-0/legacy-layout/README.md`, section 4).
- Legacy reads the set through `SPORTORG_TEMPLATES_PATH=<.legacy/templates>/ru`
  `[код: pysport@b548c35 sportorg/config.py:17, sportorg/settings.py:104-107]`; without it, legacy
  uses its own 8 upstream HTML templates. Consequence: running legacy reproduces Word reports only for
  the diploma; the other `.docx` templates remain only in the maintainer's own checkout (Stage 2,
  golden master).

## Revisit
When either pin moves
(maintainer's decision, then `fetch`); if Claude Code changes how `/path` rules anchor or starts
covering subprocess writes.
