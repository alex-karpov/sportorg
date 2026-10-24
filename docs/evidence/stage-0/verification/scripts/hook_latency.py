"""Wall time of the PostToolUse hook command from .claude/settings.json, run through Git Bash.

Usage: python hook_latency.py <repo> <bash.exe> <runs> <file>...
"""

import json
import statistics
import subprocess
import sys
import time

REPO, BASH, RUNS = sys.argv[1], sys.argv[2], int(sys.argv[3])
CMD = 'cd "$CLAUDE_PROJECT_DIR" && uv run --no-sync python -m scripts.hooks.post_edit'

for target in sys.argv[4:]:
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": target}})
    times, codes = [], []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        proc = subprocess.run(
            [BASH, "-c", CMD], input=payload, text=True, capture_output=True, check=False,
            env={**__import__("os").environ, "CLAUDE_PROJECT_DIR": REPO},
        )
        times.append(time.perf_counter() - t0)
        codes.append(proc.returncode)
    print(
        f"{target.rsplit('/', 1)[-1]:<16} runs={RUNS} exit codes={sorted(set(codes))} "
        f"first={times[0]:.2f}s median={statistics.median(times):.2f}s "
        f"min={min(times):.2f}s max={max(times):.2f}s"
    )
