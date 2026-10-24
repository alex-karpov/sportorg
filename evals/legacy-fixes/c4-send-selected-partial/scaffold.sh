#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:?set EVAL_LEGACY_SRC to the output of: uv run python -m scripts.legacy path pysport}"
FIX=b0391dd14aff7f48492ff7cc2d364a6e4796284f
PARENT=980659f9e7b7044ce1dd32bf42a53c9bf0793c38
git clone -q --no-hardlinks --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_race_partial.py" > legacy/tests/test_race_partial.py
