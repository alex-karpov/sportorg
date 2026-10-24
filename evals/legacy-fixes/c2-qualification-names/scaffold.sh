#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:?set EVAL_LEGACY_SRC to the output of: uv run python -m scripts.legacy path pysport}"
FIX=2b316380f2ccc95abd8100a6039b1371306cce36
PARENT=7b03c958770ab73d868a8fd7ea24c4c977880183
git clone -q --no-hardlinks --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_qualification.py" > legacy/tests/test_qualification.py
