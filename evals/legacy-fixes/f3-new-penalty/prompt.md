---
name: f3-new-penalty
tags: [legacy, results, penalties, feature]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 60
timeout_seconds: 1500
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Feature request: a new penalty mode for result checking. The tests in
`legacy/tests/test_penalty_checking.py` and `legacy/tests/test_result_checking.py` were rewritten
for it and specify how penalties are counted for missing, extra and wrongly ordered controls, how
they turn into penalty time or laps, and how the result status is derived. Read both test files
first; they are the specification.

Implement the feature by changing code under `legacy/sportorg/` only; do not modify anything under
`legacy/tests/`. Finish by running `uv run pytest tests/test_penalty_checking.py
tests/test_result_checking.py` inside `legacy` and paste its summary line.
