# sportorg_ng

Timing, results and publication software for orienteering (primary) and related sports
(rogaining, ARDF, sport tourism, cyclic sports). A modernization of
[SportOrg](https://github.com/sportorg/pysport): the legacy program is the behavioural oracle,
the new code must reproduce its results or deviate only with a documented reason.

Status: **Stage 0 — development environment.** No product functionality yet.

## Install (development)

Tested on Windows 11, Ubuntu (WSL/Docker) and macOS via CI; see `.github/workflows/ci.yml`.

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (0.13.1 or newer):
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone and enter the repository:
   `git clone https://github.com/alex-karpov/sportorg.git && cd sportorg`
3. Create the environment (uv downloads Python 3.14 itself if it is missing):
   `uv sync`
4. Run all quality checks:
   `uv run python scripts/check.py`
5. Optional, for contributors: install the git hooks
   `uvx pre-commit install`

Windows contributors who work with coding agents: use WSL2 and clone the repository inside the WSL
filesystem (see `docs/adr/0003-development-environment.md`; cold `uv sync` is 37 s on NTFS vs 10 s on
ext4, and agent sandboxes exist only there). A devcontainer definition is in `.devcontainer/`.

Everything a contributor or an agent needs to know is in [AGENTS.md](AGENTS.md).
Tasks live in `backlog/` (Backlog.md); decisions in `docs/adr/`; the modernization brief in
`docs/brief.md` (Russian).

## Licence

GPL-3.0-or-later (provisional; see ADR-0001).
