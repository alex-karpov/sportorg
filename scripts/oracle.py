"""File entry point of the oracle: ``uv run python scripts/oracle.py RACE_FILE`` (TASK-8 AC #1).

Running a file puts its own directory on ``sys.path``, not the repository, so ``scripts.*`` would
not import (AGENTS.md: such scripts run as modules). This shim adds the repository root and runs
``scripts.oracle_cli`` as ``__main__``; the code and its documentation are there.
"""

import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
runpy.run_module("scripts.oracle_cli", run_name="__main__", alter_sys=True)
