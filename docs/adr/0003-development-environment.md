# ADR-0003: Development environment — WSL2/ext4 for agent work on Windows, devcontainer as the reproducible equivalent

- Status: accepted (Stage 0), revisit condition below
- Date: 2026-10-24
- Evidence: `docs/evidence/stage-0/env-bench.md` (reproduce: `scripts/bench_env.sh <label> <copy of repo>`),
  `docs/evidence/stage-0/clean-install-ubuntu.txt`, `docs/evidence/stage-0/devcontainer-check.txt`,
  `docs/evidence/stage-0/agent-tooling-facts.md`, `docs/evidence/stage-0/claude-code-facts.md`,
  incident log in `docs/reports/stage-0.md`.

## Context
Maintainers work on Windows, Linux and macOS with different agents; agents run autonomously and in
parallel, so they need isolation (a broken environment must not take the host down) and fast feedback;
the product must be tested on operators' OSes; legacy analysis tooling (`code-modernization`) is POSIX.

## Options
1. Native host OS only.
2. **WSL2 (Ubuntu) with the repository on ext4** for agent work on Windows hosts; native elsewhere. **(chosen)**
3. Devcontainer (Docker) for everybody.
4. Virtual machines per OS.
5. Disposable sandboxes (agent-provided: Claude Code sandbox, Codex sandbox, `claude plugin eval` workspaces).

## Data (2026-10-24, this machine: Windows 11, 12 CPUs, WSL2 Ubuntu 26.04, Docker Desktop 29.8)

| environment | filesystem | cold `uv sync --no-cache` | warm sync | pytest | ruff | basedpyright |
|---|---|---|---|---|---|---|
| native Windows (Git Bash) | NTFS | 37.3 s | 0.39 s | 1.64 s | 0.29 s | 1.39 s |
| WSL2, repo on ext4 | ext4 | **10.5 s** | 0.02 s | 0.28 s | 0.03 s | **1.02 s** |
| WSL2, repo on /mnt/c | 9p | 75.4 s | 0.32 s | 2.49 s | 0.35 s | 4.29 s |
| Docker, bind-mounted Windows dir | 9p | 83.2 s | 0.46 s | 2.81 s | 0.34 s | 4.70 s |
| Docker, repo copied inside | overlay | 11.0 s | 0.23 s | 0.31 s | 0.02 s | 1.08 s |

Independent re-measurement with the same script (2026-10-24, separate session, uv 0.13.1 on Windows and
0.13.5 in WSL; single cold runs):

| environment | cold `uv sync --no-cache` | warm sync | pytest | ruff | basedpyright |
|---|---|---|---|---|---|
| native Windows (Git Bash), NTFS | 21.58 s | 0.28 s | 0.67 s | 0.14 s | 1.09 s |
| WSL2, ext4 | 10.65 s | 0.05 s | 0.22 s | 0.02 s | 0.86 s |
| WSL2, /mnt/c | 59.44 s | 0.24 s | 1.78 s | 0.29 s | 3.18 s |

The order of environments is the same, the ratios are smaller: ext4 is 2.0× faster than NTFS on a cold
sync (3.5× in the first run), 1.27× on type checking (1.4×), /mnt/c is 5.6× slower than ext4 (7×). Cold
runs were done once each, so the spread between the two runs is the noise level. Warm sync differs by
tenths of a second and does not matter.

Facts that are not timings:
- Claude Code has no OS sandbox backend on native Windows (commands run unconfined); `claude plugin eval`
  refuses shell-granting suites there and tells you to use WSL2. Codex has a native Windows sandbox.
- `code-modernization` commands call `python3`, `ln -s`, `readlink`, `rsync`, `mktemp`, `patch`. On this
  Windows host `python3` is the Microsoft Store stub ("Python was not found"), so they fail natively.
- Incident in this session: a WSL process ran `uv sync` in the NTFS checkout; the Windows `.venv` became a
  Linux venv with an undeletable symlink and every hook-guarded tool was blocked until manual repair.
  One checkout must never be shared between a Windows and a Linux toolchain.
- The official `ghcr.io/astral-sh/uv:python3.14-bookworm-slim` image ships uv 0.9.30 (< the project's
  `>=0.13.1`); the devcontainer therefore copies uv 0.13.5 from `ghcr.io/astral-sh/uv:0.13.5`.
- GUI and printing need a real desktop of the operator's OS; WSLg/Xvfb are not operator-representative
  `[допущение]` until the Stage 2 smoke.

## Decision
- **Windows host, agent-driven work**: WSL2 Ubuntu, repository cloned on ext4 (never under `/mnt/c`),
  Claude Code or Codex started inside WSL. Reasons, in order of weight: an OS sandbox exists there for
  Claude Code's Bash tool and for `claude plugin eval` (none on native Windows); the analysis plugin's
  POSIX tools work; cold syncs are 2–3.5× faster than on NTFS and type checks 1.3–1.4× faster (both
  measurements above), while warm syncs are equal for practical purposes. The sandbox confines Bash only:
  Read/Edit/Write are governed by permission rules, which is why legacy has its own protection
  (ADR-0006).
- **Windows native checkout**: a separate clone, used for GUI/printing tests and Windows-specific
  behaviour; never opened from WSL.
- **macOS / Linux hosts**: native (sandboxes available; measured Linux numbers apply).
- **Devcontainer** (`.devcontainer/`): the reproducible equivalent for unattended agents, contributors
  without WSL, and parity with the CI clean-install job. Docker internal copy ≈ WSL ext4 in the table.
  Bind-mounting a Windows directory into Docker is not supported for development (9p row).
- **Virtual machines**: only for operator-OS smoke tests (Stage 2; Windows versions from the operator
  inventory), not for development.
- **Disposable sandboxes**: `claude plugin eval` workspaces (pilot, from WSL2); agent sandboxes as the
  default for autonomous runs.

## Consequences
- AGENTS.md and README point Windows contributors to WSL2 for agent work; the one-checkout-per-toolchain
  rule is written down. It is enforced by nothing but discipline — the Stage 0 incident was exactly its
  violation — so a mechanical check (refuse to run when `.venv` was built for another OS) is tracked as a
  Backlog task.
- Three environments (WSL, native Windows clone, devcontainer) mean three setups to keep working; the
  devcontainer is verified by building the image and running the checks inside it, not from VS Code.
- Hooks that must never fail closed (the PreToolUse guard) run with `uv run --no-project`; the guard
  exits 0, and its hook command maps a failure of uv itself to the non-blocking exit 1 (ADR-0005).

## Revisit
When Claude Code gets a Windows sandbox backend; after the Stage 2 smoke on three OSes (GUI/printing
findings may change the native-vs-WSL split); if the devcontainer diverges from CI (different uv or
Python) for more than one release.
