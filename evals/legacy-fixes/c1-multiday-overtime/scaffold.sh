#!/usr/bin/env bash
# Clone the read-only legacy checkout at the parent of the real fix and add the real fix's test file.
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:-$HOME/Prog/Orient/_other/pysport-legacy}"
FIX=57ac99d048fc4453dccdf0f2ac1d1d6f72093f5d
PARENT=ced57547d37451f8afdb835d0f6a3a7ed4a7214a
git clone -q --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_result_checking.py" > legacy/tests/test_result_checking.py
