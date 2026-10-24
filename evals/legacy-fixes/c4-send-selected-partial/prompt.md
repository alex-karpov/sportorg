---
name: c4-send-selected-partial
tags: [legacy, reports, teamwork]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 50
timeout_seconds: 1200
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Bug report: "Send selected" builds a partial copy of the race from the selected persons, groups,
courses, organizations or results. The partial copy does not follow the order of the main model, and
selecting by results can include unselected results of the same person. For multi-day races,
selecting an athlete should also pull the same athlete (matched by multi-day id) from the other days.
A selection with no matches must still produce a valid empty structure, and an empty selection must
produce no data.

`legacy/tests/test_race_partial.py` contains the failing tests; it names the builder methods it
expects, so read it first. Make it pass by changing code under `legacy/sportorg/` only; do not modify
anything under `legacy/tests/`. Finish by running `uv run pytest tests/test_race_partial.py` inside
`legacy` and paste its summary line.
