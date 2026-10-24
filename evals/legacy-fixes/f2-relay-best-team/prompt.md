---
name: f2-relay-best-team
tags: [legacy, relay, feature]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 50
timeout_seconds: 1200
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Feature request: in relay mode, add a "best team placing" option for a group: team places are
computed according to the rule specified by the tests, instead of the default relay placing. The
exact semantics (what counts as the team result, how ties and incomplete teams are handled, where
the option lives on the group) are specified by `legacy/tests/test_relay_results.py`. Read the tests
first; they are the specification.

Implement the feature by changing code under `legacy/sportorg/` only; do not modify anything under
`legacy/tests/`. Finish by running `uv run pytest tests/test_relay_results.py` inside `legacy` and
paste its summary line.
