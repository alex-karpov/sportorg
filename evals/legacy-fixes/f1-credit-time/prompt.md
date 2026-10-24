---
name: f1-credit-time
tags: [legacy, results, feature]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 50
timeout_seconds: 1200
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Feature request: "credit time" — a time credit that is taken into account when a result is
calculated and shown on the split printout. The exact semantics (where the credit is configured,
how it combines with penalties and the raw finish time, which results it applies to) are specified by
the tests in `legacy/tests/test_credit_calculation.py`. Read the tests first; they are the
specification.

Implement the feature by changing code under `legacy/sportorg/` only; do not modify anything under
`legacy/tests/`. Finish by running `uv run pytest tests/test_credit_calculation.py` inside `legacy`
and paste its summary line.
