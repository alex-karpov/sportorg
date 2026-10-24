# sportorg_ng

Timing, results and publication software for orienteering (primary) and related sports
(rogaining, ARDF, sport tourism, cyclic sports). A modernization of
[SportOrg](https://github.com/sportorg/pysport): the legacy program is the behavioural oracle,
the new code must reproduce its results or deviate only with a documented reason.

Status: **Stage 0 — development environment.** No product functionality yet.

## Install (development)

CI runs the Linux steps below on a clean Ubuntu 24.04 container and the checks on Windows, Linux and macOS;
see `.github/workflows/ci.yml`.

### Prerequisites

- Linux (Ubuntu/Debian), in a terminal:
  ```
  sudo apt-get update
  sudo apt-get install -y git curl ca-certificates
  ```
- macOS: `git` comes with the Xcode command line tools (`xcode-select --install`).
- Windows 11: install [Git for Windows](https://git-scm.com/download/win) and open a new PowerShell window.

### Linux and macOS

```
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
git clone https://github.com/alex-karpov/sportorg.git
cd sportorg
uv sync
uv run python scripts/check.py
```

`source` makes `uv` visible in the current shell; a new terminal does the same.
`uv sync` downloads Python 3.14 itself if it is missing.

### Windows (PowerShell)

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close PowerShell and open a new window (so that `uv` is on `PATH`), then:

```
git clone https://github.com/alex-karpov/sportorg.git
cd sportorg
uv sync
uv run python scripts/check.py
```

### Optional: git hooks for contributors

```
uvx --python 3.14 pre-commit@4.7.0 install
```

Windows contributors who work with coding agents: use WSL2 and clone the repository inside the WSL
filesystem (see `docs/adr/0003-development-environment.md`; in two single-run measurements on one machine,
cold `uv sync` took 21.6-37 s on NTFS versus 10.5-10.7 s on ext4, and agent sandboxes exist only there).
Step by step, with VS Code: [docs/windows-wsl-vscode.md](docs/windows-wsl-vscode.md).
A devcontainer definition is in `.devcontainer/`.

Everything a contributor or an agent needs to know is in [AGENTS.md](AGENTS.md).
Tasks live in `backlog/` (Backlog.md); decisions in `docs/adr/`; the modernization brief in
`docs/brief.md` (Russian).

## Licence

GPL-3.0-only, the licence of the legacy SportOrg it is derived from ([LICENSE](LICENSE); ADR-0004).
