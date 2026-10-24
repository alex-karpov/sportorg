# Windows: working in VS Code with WSL2

The recommended setup for agent work on a Windows host (ADR-0003): the repository lives on WSL's
ext4 file system, the tools and agents run inside WSL, and VS Code on Windows connects to it. A native
Windows clone stays a separate checkout for GUI and printing tests.

**One checkout, one toolchain.** Never run Windows tools (`uv`, Python, Claude Code for Windows) on
the WSL clone (`\\wsl.localhost\…`), and never run WSL tools in a Windows checkout (`/mnt/c/…`): in
Stage 0 that turned the Windows `.venv` into a broken Linux one.

## Once per machine

1. **WSL2 with Ubuntu.** In PowerShell: `wsl --install -d Ubuntu`; `wsl -l -v` must show `VERSION 2`
   (the Claude Code sandbox needs WSL2).
2. **VS Code on Windows** with the extension **WSL** (`ms-vscode-remote.remote-wsl`).
3. **Tools in Ubuntu** (open the Ubuntu terminal):
   ```
   sudo apt-get update
   sudo apt-get install -y git curl ca-certificates bubblewrap socat nodejs npm
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   npm install -g --prefix ~/.local backlog.md
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
   ```
   The last line lets `git push` from WSL use the GitHub login stored by Git for Windows. `bubblewrap`
   and `socat` are what the Claude Code sandbox needs on Linux and WSL2. `nodejs` and `npm` run the
   Backlog.md CLI (`backlog`, the task registry), installed for your user into `~/.local/bin`; the
   Windows `backlog` that WSL sees on its PATH needs a Linux `node` and fails with
   `node: not found`. Check with `command -v backlog` (a path in Linux, not under `/mnt/c`) and
   `backlog --version`. Verified on 2026-10-25 in a clean `ubuntu:26.04` container: Node.js 22.22.1,
   npm 9.2.0, Backlog.md 1.55.3, `backlog task list --plain` in a clone of this repository.
4. **Claude Code in Ubuntu:**
   ```
   curl -fsSL https://claude.ai/install.sh | bash
   claude
   ```
   Log in with `/login`. Turn the sandbox on with `/sandbox` in a session, or with
   `"sandbox": {"enabled": true}` in `~/.claude/settings.json`. If `bubblewrap` or `socat` is missing,
   Claude Code runs commands without the sandbox, unless `"sandbox": {"failIfUnavailable": true}`
   makes it stop at startup instead. Of the two `/sandbox` modes, auto-allow is the one probed for
   this project: Bash commands run without prompts inside the sandbox, and `.legacy/` stays read-only
   for them and for the processes they start (ADR-0006). If
   `sysctl kernel.apparmor_restrict_unprivileged_userns` prints `1` (Ubuntu 24.04+ with AppArmor),
   apply "Ubuntu 24.04 and later: allow bubblewrap to create user namespaces" from the
   [sandboxing docs](https://code.claude.com/docs/en/sandboxing); if the key does not exist, nothing
   is needed.

   The sandbox lets commands write only under the session's directory, and uv keeps its cache in
   `~/.cache/uv`: a sandboxed `uv run …` then fails with "Read-only file system". Allow the cache in
   `~/.claude/settings.json`:
   ```json
   "sandbox": {"enabled": true, "filesystem": {"allowWrite": ["~/.cache/uv"]}}
   ```
   With it, `uv run python scripts/check.py --only tests` ran inside the sandbox
   (`docs/evidence/stage-0/sandbox-uv-wsl.md`; the cache was already filled, so downloads through the
   sandbox's network rules were not tried). Hooks run outside the sandbox and do not need this.

## Clone and check

In the Ubuntu terminal, somewhere under your home directory (ext4), never under `/mnt/c` (5–7 times
slower, ADR-0003):

```
mkdir -p ~/src && cd ~/src
git clone https://github.com/alex-karpov/sportorg.git
cd sportorg
uv sync
uvx --python 3.14 pre-commit@4.7.0 install
uv run python -m scripts.legacy fetch
uv run python -m scripts.legacy verify
uv run python scripts/check.py
```

`verify` prints `ok: pysport@…, templates@… locked`; `check.py` ends with five `ok` lines.

## Open in VS Code

From the repository directory in the Ubuntu terminal: `code .`. The first time, VS Code installs its
server inside WSL; the status bar then shows `WSL: Ubuntu`. (Alternatively, in VS Code: Command
Palette → `WSL: Connect to WSL`, then File → Open Folder → `~/src/sportorg`.)

- Extensions run on the WSL side. Install the recommended **Ruff** and **BasedPyright**
  (`.vscode/extensions.json`) with "Install in WSL: Ubuntu". BasedPyright finds `.venv` through
  `pyproject.toml`. If the Python extension is installed as well, set `"python.languageServer": "None"`
  in the WSL settings so that Pylance does not report the same problems a second time.
- Editor diagnostics come from the extensions' own tool versions; "green" is what
  `uv run python scripts/check.py` says.
- The VS Code terminal in this window is a WSL shell.

## Claude Code in the project

Start it at the repository root: the deny rules that protect `.legacy/` anchor at the directory the
session starts in (ADR-0006).

```
cd ~/src/sportorg
claude
```

Plugins are installed once per machine, as `CLAUDE.md` describes (`superpowers` with
`--scope project`; `code-modernization` with `--scope local` if wanted, which writes the per-machine
`.claude/settings.local.json`).

## Removing a clone

`.legacy/` is read-only, so a plain `rm -rf` stops there:

```
chmod -R u+w ~/src/sportorg/.legacy && rm -rf ~/src/sportorg
```
