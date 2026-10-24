#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:?set EVAL_LEGACY_SRC to the output of: uv run python -m scripts.legacy path pysport}"
FIX=3b55fe8b07910fcf16f9fd4b8574e382a3d905a5
PARENT=9e01b24378bb010ca3e0bf26eeff3eab04344f45
git clone -q --no-hardlinks --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_sfrx.py" > legacy/tests/test_sfrx.py
git -C legacy show "$FIX:tests/data/sfrx_file.sfrx" > legacy/tests/data/sfrx_file.sfrx
