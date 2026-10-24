# Environment benchmark (stage 0)

Date: 2026-10-24

## Versions

- Windows uv: 0.13.1 (62faed335 2026-10-13, x86_64-pc-windows-msvc)
- WSL uv: 0.13.5 (x86_64-unknown-linux-gnu)
- WSL kernel: 6.18.33.2-microsoft-standard-WSL2; distro: Ubuntu 26.04 LTS
- Docker client 29.8.2; Docker Desktop server 29.8.2, kernel 6.18.33.2-microsoft-standard-WSL2
- Image `ghcr.io/astral-sh/uv:python3.14-bookworm-slim`: digest sha256:7cf77f594be8042dab6daa9fe326f90962252268b4f120a7f5dccce4d947e6c1, but it ships uv 0.9.30, which fails the project's `required-version >=0.13.1`. Docker rows therefore use a derived local image `uvbench:0.13.5` (uv 0.13.5 musl binary copied from `ghcr.io/astral-sh/uv:0.13.5` over /usr/local/bin/uv; bash and Python 3.14 from the original image).

## Results (seconds; pytest/ruff/basedpyright are medians of 3)

| env | uname | fs | cold uv sync --no-cache | warm uv sync | pytest | ruff | basedpyright |
|---|---|---|---|---|---|---|---|
| native-windows (REUSED, uv 0.13.1) | MINGW64_NT-10.0-26300 | ntfs | 37.29 | 0.39 | 1.64 | 0.29 | 1.39 |
| wsl-ext4 (uv 0.13.5) | Linux 6.18.33.2-microsoft-standard-WSL2 | ext4 | 10.53 | 0.02 | 0.28 | 0.03 | 1.02 |
| wsl-mntc (uv 0.13.5) | Linux 6.18.33.2-microsoft-standard-WSL2 | 9p | 75.37 | 0.32 | 2.49 | 0.35 | 4.29 |
| docker-bind (uv 0.13.5, derived image) | Linux 6.18.33.2-microsoft-standard-WSL2 | 9p | 83.20 | 0.46 | 2.81 | 0.34 | 4.70 |
| docker-internal (uv 0.13.5, derived image) | Linux 6.18.33.2-microsoft-standard-WSL2 | overlay | 10.99 | 0.23 | 0.31 | 0.02 | 1.08 |

Notes: ruff exits non-zero in every environment (finding RUF043 in tests, "Found 1 error"); its time is still measured. pytest reports 5 passed, basedpyright 0 errors.

## Commands

All run with the cwd inside a copy of the repo (copies' `scripts/`, `pyproject.toml`, `uv.lock` refreshed from the main checkout by copying).
Scratchpad = `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\33a8a286-529a-4024-bb4b-7f1f54ecf08b\scratchpad`.

```
# wsl-ext4 (literal paths; see failures)
wsl -d Ubuntu --cd '~' -- bash -lc 'export PATH="$HOME/.local/bin:$PATH"; cd /home/USER/envbench/sportorg && pwd && df -T . && bash scripts/bench_env.sh wsl-ext4 /home/USER/envbench/sportorg'

# wsl-mntc
wsl -d Ubuntu --cd '~' -- bash -lc "export PATH=\"\$HOME/.local/bin:\$PATH\"; cd /mnt/c/Users/USER/AppData/Local/Temp/claude/C--Users-USER-Prog-Orient-sportorg/33a8a286-529a-4024-bb4b-7f1f54ecf08b/scratchpad/envbench/wsl-mnt/sportorg && pwd && df -T . && bash scripts/bench_env.sh wsl-mntc <same path>"

# docker-bind
docker run --rm -v "<scratchpad>\envbench\docker\sportorg:/work" -w /work uvbench:0.13.5 bash scripts/bench_env.sh docker-bind /work

# docker-internal
docker run --rm -v "<scratchpad>\envbench\docker\sportorg:/src:ro" uvbench:0.13.5 bash -c "cp -r /src /work && cd /work && rm -rf .venv && bash scripts/bench_env.sh docker-internal /work"

# derived image
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /usr/local/bin/
```

## Failures and deviations (verbatim where applicable)

1. First wsl-ext4 attempts were invalid and discarded (fs column 9p, and `error: No \`pyproject.toml\` found in current directory or any parent dir`). Causes: (a) `wsl --cd ~` typed in Git Bash expands `~` to /mnt/c/Users/USER; (b) wsl.exe passes the command through the default shell, which expands `$PWD`/`$VAR` in the outer shell (cwd /home/USER) before `bash -lc` sees them, so `"$PWD"` became `/home/USER`. Fix: literal paths with no shell variables; `MSYS_NO_PATHCONV=1` for Git Bash. Reported fs of the final wsl-ext4 run is ext4 (`df -T`: /dev/sdd ext4).
2. docker-bind with the image as specified (first attempt, discarded): `error: Required uv version \`>=0.13.1\` does not match the running version \`0.9.30\`` (all commands; row showed 0.02s everywhere). Tags `0.13.5-python3.14-bookworm-slim`, `0.13.1-python3.14-bookworm-slim`, `0.13-python3.14-bookworm-slim` do not exist ("not found"); `ghcr.io/astral-sh/uv:0.13.5` / `0.13.1` pull but are distroless (no bash), hence the derived image.
3. Docker "fs" for docker-bind reads 9p as reported by `df -T` in the container (Docker Desktop bind mount from Windows).
