---
name: c1-multiday-overtime
tags: [legacy, results]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 40
timeout_seconds: 900
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Bug report: a multi-day group on day 2 has race type MULTI_DAY_RACE and a 60-minute maximum time.
An athlete ran 45 minutes on day 1 and 55 minutes on day 2: the cumulative time is 100 minutes, but
today's time is within the limit. The athlete is wrongly marked as overtime. An athlete who ran
65 minutes on day 2 must still be marked overtime. For multi-day groups the overtime check must
depend only on the current day's time.

The test file `legacy/tests/test_result_checking.py` already contains the failing tests for this
behaviour. Make them pass by changing code under `legacy/sportorg/` only; do not modify anything
under `legacy/tests/`. Finish by running `uv run pytest tests/test_result_checking.py` inside
`legacy` and paste its summary line in your final message.
