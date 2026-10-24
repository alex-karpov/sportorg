#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:-$HOME/Prog/Orient/_other/pysport-legacy}"
FIX=6446c7008f942a4d884532885cb5a9a01f9f565b
PARENT=fccfc27dce15b5228ba42099fb44a0c4414e6c30
git clone -q --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_penalty_checking.py" > legacy/tests/test_penalty_checking.py
git -C legacy show "$FIX:tests/test_result_checking.py" > legacy/tests/test_result_checking.py
