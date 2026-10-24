#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:?set EVAL_LEGACY_SRC to the output of: uv run python -m scripts.legacy path pysport}"
FIX=20b51465f015f003fb6f1617bdd3e75c0846965b
PARENT=f92d32f1b31fffa3dd35f74284e16a8e37bf62ba
git clone -q --no-hardlinks --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_credit_calculation.py" > legacy/tests/test_credit_calculation.py
