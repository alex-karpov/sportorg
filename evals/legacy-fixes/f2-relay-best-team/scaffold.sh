#!/usr/bin/env bash
set -euo pipefail
SRC="${EVAL_LEGACY_SRC:-$HOME/Prog/Orient/_other/pysport-legacy}"
FIX=e0c0480a9c844439893186747311ce0327f29ad7
PARENT=0952a379e2345a92724cc747ffcbba6490a58102
git clone -q --no-checkout "$SRC" legacy
git -C legacy checkout -q --detach "$PARENT"
git -C legacy show "$FIX:tests/test_relay_results.py" > legacy/tests/test_relay_results.py
