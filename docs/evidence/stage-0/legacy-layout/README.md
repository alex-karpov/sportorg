# Legacy licence, pinned commit, templates and protection probes

Collected on 2026-10-24 for the maintainer decisions of the same day (TASK-6): decision 1 (licence,
"confirm the legacy licence from the primary source first") and decision 7 (legacy as a git-ignored
clone inside the repository with a portable deny rule; "probe it on Windows and in WSL first"; consider
two legacy repositories, pysport and templates). Legacy checkout: `../_other/pysport-legacy`, read only
with `git -C`. Section 4 was added on 2026-10-25, after the maintainer chose two repositories.
Commands are listed in `commands.txt`.

## 1. Legacy licence (primary sources)

| Source | What it says |
|---|---|
| `LICENSE` at 30d849d | Full GPLv3 text. Blob `ef7c3112` is identical at upstream `b548c35`. "any later version" appears only inside the licence text itself (§14, lines 569 and 571; "How to apply" appendix, line 639). |
| `pyproject.toml` at 30d849d | No `license` field and no licence classifier. |
| `README.md:2` at 30d849d | Badge "license-GPLv3" linking to `LICENSE`. |
| Source headers (corrected 2026-10-25, see below) | Four vendored readers carry "either version 3 of the License, or (at your option) any later version": `sportorg/libs/huichang/huichang.py:7-9`, `sportorg/libs/sfr/sfrreader.py:7-9`, `sportorg/libs/sportiduino/sportiduino.py:7-9`, `sportorg/libs/srpid/srpid.py:6-8`. `builder.py:118` sets `copyright="GNU GENERAL PUBLIC LICENSE …"`. |
| `sportorg/gui/dialogs/about.py` (the About dialog) | Embeds the GPLv3 text. Its "How to Apply These Terms" appendix is filled in for the program: "SportOrg / Copyright (C) 2018  SportOrg team / … either version 3 of the License, or (at your option) any later version" (lines 720-726), and the interactive notice at line 742 names "SportOrg  Copyright (C) 2018 SportOrg team". |
| GitHub API `repos/sportorg/pysport` | `license.spdx_id = "GPL-3.0"` (GitHub's detection of the LICENSE text, not a statement by the authors). |
| GitHub API `repos/sportorg/templates` | `license = null` (no licence file). One commit `fecebb45` (2024-10-07) "refactor: move templates from the app repository". |

Finding: `LICENSE`, README and `pyproject.toml` name GPL version 3 without "or any later version";
the About dialog shows the program's own filled-in notice with "or (at your option) any later
version", and four vendored files carry the same clause. Correction: until 2026-10-25 this section
said that only `huichang.py` had the clause and missed the About dialog; the independent round-2 check
of 2026-10-25 found the rest (`git -C .legacy/pysport grep -n -I -i "any later version" HEAD`).
Interpretation `[допущение]`: GPLv3 §14 gives the "or later" option when "the Program specifies" it;
the About dialog is the program specifying it, so the legacy reads as GPL-3.0-or-later rather than
GPL-3.0-only. The authors can settle it (Backlog TASK-10). This is a reading of the licence text, not
legal advice.

## 2. The pinned legacy commit

- `30d849dde1f7…` "feat: add russian templates", author: the maintainer, 2026-10-18. `git branch -a
  --contains 30d849d` lists only the local branch `templates`: the commit is not on
  github.com/sportorg/pysport, so nobody else can fetch it.
- Its parent is `origin/master` = `b548c35ba18f…` "ci: fix building rust code" (2026-09-25);
  `git log 30d849d..origin/master` is empty.
- `git diff --name-status b548c35 30d849d`: 71 paths, all under `sportorg/data/templates/`: 69 added,
  2 modified (`script.js.html`, `split/1_split_printout.html`). No code differs, so the Stage 0 code
  measurements (type checkers, history candidates) hold for `b548c35` as well.

## 3. Templates: pinned commit versus github.com/sportorg/templates

Matched by git blob id (identical content has the identical id regardless of path). sportorg/templates
keeps its files under `ru/`; the pinned commit puts them directly under `sportorg/data/templates/`.

| Files added by 30d849d | Count |
|---|---|
| identical to a file in sportorg/templates | 19 |
| same file name, different content | 25 |
| absent from sportorg/templates | 25 |
| total | 69 |

sportorg/templates (48 files) has 28 files without an identical blob in 30d849d: the 25 changed ones
plus `ru/base.html`, `ru/script.js.html`, `ru/style.css.html`.

How legacy finds templates: `settings.template_dir()` returns
`paths.resolve_seeded("templates", …, override=SETTINGS.templates_path or config.TEMPLATES_PATH)`
[код: sportorg/settings.py:104-107]; `TEMPLATES_PATH` comes from the environment variable
`SPORTORG_TEMPLATES_PATH` [код: sportorg/config.py:15-17]; with an override the whole template root is
that directory [код: sportorg/paths.py:92-107], rendered by one `FileSystemLoader`
[код: sportorg/libs/template/template.py:54]; a source checkout seeds nothing [код: sportorg/paths.py:110-118].
So "pysport at an upstream commit + a separate templates directory" is supported by legacy itself.

Personal data (pattern scan: surname with initials, e-mail, Russian phone number; values are not
reproduced here): of 77 template files at 30d849d, 11 `.docx` files contain an e-mail address (one
distinct address, gmail.com) and between them 3 distinct phone numbers. 9 of the 11 are byte-identical
to files already public in sportorg/templates. No surname-with-initials pattern was found. A pattern
scan can miss names written in full.
Re-scan of 2026-10-24 that also read `docProps/*.xml`: all 16 `.docx` at 30d849d carry author names
in `docProps/core.xml` (`dc:creator`, `cp:lastModifiedBy`), 8 distinct; the 10 `.docx` of
sportorg/templates carry 5. The e-mail address and all 3 phone numbers are already in sportorg/templates.

## 4. The templates repository that replaced 30d849d (2026-10-25)

Maintainer decision of 2026-10-25: option B of ADR-0006, without the `.docx` files except one
diploma that the maintainer cleaned. Built in a scratch clone of the fork
github.com/alex-karpov/sportorg-templates (parent `fecebb45`, the only commit of sportorg/templates):

- The index of `ru/` was replaced by the tree `30d849d:sportorg/data/templates` (`git read-tree`, so
  blobs are copied exactly, without line-ending conversion), the 16 `.docx` were removed from the
  index and the cleaned `reports/диплом_Кубок_России_word.docx` added.
- `git diff-tree -r 30d849d:sportorg/data/templates <new tree>:ru` → 15 `D` (`.docx`) and 1 `M`
  (the diploma); all 61 HTML templates are byte-identical. Against `fecebb45`: 23 HTML added,
  28 changed, nothing of `ru/` lost.
- Cleaned diploma against the 30d849d version: `docProps/core.xml` creator and last-modified-by
  empty (were filled), `docProps/app.xml` company empty (was filled); visible text of
  `word/document.xml`, footnotes and endnotes identical; 25 template tags (`{{ }}`, `{% %}`, `{# #}`)
  identical and in the same order.
- The scan of section 3 with `docProps` over the new tree: no e-mail address, phone number or author
  name.
- Pushed as `22088f8`; the maintainer amended only the commit message, giving `cd953823`, whose tree
  `3a64f3c4` equals that of `22088f8` (`gh api …/commits/cd95382`).

Fetch: `uv run python -m scripts.legacy fetch` (no `--source`) → `pysport … at b548c35…, locked
(replaced 30d849dde1f7)`, `templates … at cd953823…, locked`; `verify` → `ok:
pysport@b548c35ba18f, templates@cd953823beb3 locked`. At `b548c35`, pysport's own
`sportorg/data/templates` holds 8 upstream HTML files; legacy uses the Russian set when
`SPORTORG_TEMPLATES_PATH` points to `.legacy/templates/ru`.

## 5. Protection probes — `scripts/probe_legacy_protection.py`

The probe builds a throwaway project with the planned layout (`.legacy/pysport/…`, `.gitignore`
`.legacy/`, `.claude/settings.json` deny `Edit(/.legacy/**)`) outside this repository. Raw outputs:
`probe-fsmode-windows.md`, `probe-fsmode-wsl.md`, `probe-agent-windows.md`, `probe-agent-wsl.md`,
`probe-agent-wsl-sandbox.md`, `probe-hook-exit-code.md`.

### 5.1 Read-only file modes, no agent (`fsmode`)

Files 0o444, directories 0o555; each case starts from a fresh tree; the effect is read from disk.

| Write attempt | WSL2 ext4 | Windows, read-only attribute | Windows, attribute + deny ACE |
|---|---|---|---|
| `echo >>` | blocked | blocked | blocked |
| `sed -i` | blocked | **written** | blocked |
| `cp` new file into the tree | blocked | **written** | blocked |
| `mv` | blocked | **written** | blocked |
| `rm -f` | blocked | **written** | blocked |
| `rm -rf` | blocked | **written** | blocked |
| `git rm` inside the clone | blocked | **written** | blocked |
| `chmod u+w`, then append | **written** | **written** | blocked |
| Python `open(…, 'a')` | blocked | blocked | blocked |
| Python `os.remove` | blocked | blocked | blocked |
| PowerShell `Set-Content` | n/a | blocked | blocked |
| PowerShell `Remove-Item` | n/a | blocked | blocked |
| PowerShell `Remove-Item -Force` | n/a | **written** | blocked |
| PowerShell `Remove-Item -Recurse -Force` | n/a | **written** | blocked |

The deny ACE is an inherited (container + object) deny for the current user of WriteData, AppendData,
WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles, set with PowerShell 7
`Set-Acl`. Reading and listing keep working (the "before" snapshots under the ACE were complete).
`icacls /deny user:(OI)(CI)(WD,AD,WEA,WA,D,DC)` is not usable: icacls stored it as `(W,D,DC)`, `W`
includes SYNCHRONIZE, and `ls`/`cat` on the tree failed with "Permission denied" (tried on a scratch
directory, then removed). On Linux the owner can always `chmod u+w` back; only root-level tools
(`chattr +i`, a read-only bind mount) close that.

### 5.2 Claude Code deny rule, agent (`agent`), Windows and WSL2, no sandbox

Claude Code 2.1.310, model sonnet, `claude -p` started at the probe project root with
`--permission-mode acceptEdits --allowedTools Bash,PowerShell,Edit,Write,Read`; files writable (rule
only). Windows 11: 2026-10-24, cost USD 0.35. WSL2 Ubuntu (ext4, Python 3.14.4): 2026-10-25, after the
maintainer installed Claude Code there, probe script from the fresh clone of `stage-0` at `882bd00`,
cost USD 0.15.

| Attempt | Windows | WSL2 | Tool result |
|---|---|---|---|
| Edit, relative path | unchanged | unchanged | "File is in a directory that is denied by your permission settings." |
| Edit, absolute path | unchanged | unchanged | same |
| Edit, `src/../.legacy/…` | unchanged | unchanged | same |
| Edit, `.LEGACY/PYSPORT/…` (case variant) | unchanged | unchanged | same (on ext4 that path does not exist, Read says so; the Edit is still refused by the rule) |
| Edit through a link `src/link → .legacy/pysport` (junction on Windows, symlink on Linux) | unchanged | unchanged | "Permission to edit … has been denied." (a refused permission request, not the deny-rule message) |
| Edit in a subdirectory | unchanged | unchanged | deny-rule message |
| Write a new file | unchanged | unchanged | deny-rule message |
| Bash `echo >>`, `sed -i`, `cp`, `mv`, `rm` | unchanged | unchanged | "Permission to use Bash with command … has been denied." |
| Bash `python -c "open(…, 'a')"` (`python3` on Linux) | **written** | **written** | ok (documented gap: subprocesses that open files themselves) |
| PowerShell `Set-Content`, `Remove-Item` | unchanged | n/a (no PowerShell tool) | Windows: "set-content targeting '…\.legacy\pysport\s14.txt' was blocked. For security, Claude Code may only access files in the allowed working directories for this session" (same for remove-item) |
| Read | content returned | content returned | ok |
| Edit `src/control.txt` (control) | changed | changed | ok |

Refused: 15 of 16 write attempts on Windows, 12 of 13 in WSL2. The one that passes in both is a
subprocess opening the file itself; in the real `.legacy/` the file layer stops it (section 5.1:
Python `open(…, 'a')` blocked on ext4 and under the Windows ACE). Documented limits that need no
probe: a `/path` rule anchors at the session's primary working directory, so a session started in a
subdirectory or a worktree does not get this rule for the root `.legacy/` (docs: "Where a pattern
anchors"); deny rules do not cover subprocesses that open files themselves (docs: Read and Edit
warning).

### 5.3 The same agent probe with the Bash sandbox, WSL2

2026-10-25, same rule and steps, option `--sandbox`: the probe project's `.claude/settings.json` also
has `"sandbox": {"enabled": true, "autoAllowBashIfSandboxed": true, "failIfUnavailable": true}`, which
is the auto-allow mode of `/sandbox`, and Claude Code stops instead of running commands unconfined if
the sandbox cannot start. bubblewrap and socat from apt; cost USD 0.17.

| Attempt | WSL2, no sandbox (5.2) | WSL2, sandbox | Tool result with the sandbox |
|---|---|---|---|
| Edit and Write, steps 1–7 | unchanged | unchanged | the permission messages of 5.2; the sandbox does not apply to these tools |
| Bash `echo >>`, `sed -i`, `cp`, `mv`, `rm` | unchanged | unchanged | the command ran without a permission check and failed with "Read-only file system", e.g. `rm: cannot remove '.legacy/pysport/s12.txt': Read-only file system` |
| Bash `python3 -c "open(…, 'a')"` | **written** | unchanged | `OSError: [Errno 30] Read-only file system: '.legacy/pysport/s13.txt'` (full line from `agent-stream.jsonl`; the table in the raw output cuts it) |
| PowerShell | n/a | n/a | no PowerShell tool on Linux |
| Read; Edit `src/control.txt` (control) | ok | ok | ok |

Refused: 13 of 13 write attempts. The probe files stayed writable (`-rw-r--r--` after the run), so
"Read-only file system" comes from the sandbox's mount, not from file modes: `.legacy/` was read-only
inside a writable working directory for every process that Bash started. That matches the sandboxing
docs, which merge Edit deny rules into the sandbox's write restrictions; a run with the sandbox and
without the rule was not made. No tool call asked to run outside the sandbox
(`dangerouslyDisableSandbox` occurs 0 times in the stream). Not tested: such a retry, which
`allowUnsandboxedCommands` (default true) permits and ordinary permissions then govern; a Bash write
into `src/` under the sandbox (the control step uses Edit).

### 5.4 Exit code of the guard's hook command when uv itself fails

Found by the independent round-2 check (2026-10-25): with an unwritable uv cache the guard's hook
command exited 2, and the Python guard's "always 0" did not apply because Python never started. Raw
output: `probe-hook-exit-code.md`. uv exits 2 on its own errors (missing interpreter, unwritable cache).
A PreToolUse hook whose uv fails that way blocked the Bash call (`out.txt` not written, "PreToolUse:Bash
hook error: …"); the same command with `|| exit 1` let it run (`out.txt` written). The guard's command
in `.claude/settings.json` now ends in `|| exit 1`; its Python part still exits 0.
