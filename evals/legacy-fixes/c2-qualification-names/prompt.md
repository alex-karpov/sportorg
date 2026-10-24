---
name: c2-qualification-names
tags: [legacy, import, national-ru]
plugins: ["../../../tools/plugins/code-modernization"]
runs: 3
max_turns: 40
timeout_seconds: 900
---
You are working in `./legacy`, a checkout of SportOrg (Python, orienteering timing software).
Install with `uv sync --frozen --extra gui` and run tests with `uv run pytest <file>`.

Bug report: when entries are imported, external qualification strings such as "кмс", "мс", "I",
"ii", "3", "1р", "2Р", "1ю", "IIIЮ" and "б.р." are not recognised, so the athlete gets no or the
wrong qualification. Case, surrounding spaces, trailing dots and the common short forms should all
map to the canonical qualification. Unknown strings must still yield "no qualification".

`legacy/tests/test_qualification.py` contains the failing tests. Make them pass by changing code
under `legacy/sportorg/` only; do not modify anything under `legacy/tests/`. Finish by running
`uv run pytest tests/test_qualification.py` inside `legacy` and paste its summary line.
