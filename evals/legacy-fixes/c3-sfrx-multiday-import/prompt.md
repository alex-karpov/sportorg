---
name: c3-sfrx-multiday-import
tags: [legacy, import]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 40
timeout_seconds: 900
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Bug report: a multi-day SFRX file defines groups with a different course per day, for example
"Дист1" on day 1 and "Финал" on day 2. After import, day 2 does not get its own course for the
group, so courses, splits and results of day 2 are wrong. Importing such a file must create one race
per day and assign each day's course to the group, with correct times, statuses and first split
codes per person per day.

`legacy/tests/test_sfrx.py` and the fixture `legacy/tests/data/sfrx_file.sfrx` contain the failing
test. Make it pass by changing code under `legacy/sportorg/` only; do not modify anything under
`legacy/tests/`. Finish by running `uv run pytest tests/test_sfrx.py` inside `legacy` and paste its
summary line.
