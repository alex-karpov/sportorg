#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:-$HOME/Prog/Orient/_other/pysport-legacy}"
FIX=b0391dd14aff7f48492ff7cc2d364a6e4796284f
PARENT=980659f9e7b7044ce1dd32bf42a53c9bf0793c38
git clone -q --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_race_partial.py" > legacy/tests/test_race_partial.py
