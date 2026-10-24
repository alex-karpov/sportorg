# Stage 1 evidence (TASK-7)

Legacy pins: `pysport@b548c35`, `templates@cd95382` (`legacy.toml`). Plan: `docs/plans/stage-1-archaeology.md`.
Every number here comes from a script in `scripts/archaeology/`. The commands are in each directory's
`commands.txt`. Files named `*.manual.md` are manual classification, with their criteria at the top.

| Directory | Criterion of TASK-7 | Content | State |
|---|---|---|---|
| `tools/` | (rule «Как выбирать инструменты») | tool candidates and measurements behind ADR-0007 | done (Phase B) |
| `hypotheses/` | #6 | verdicts on the six hypotheses of the brief | done (Phase B) |
| `inventory/` | #1 | menu actions, report templates, import/export formats | W1 |
| `structure/` | #2 | hotspots, import graph, layer violations, dead code | W2 |
| `dependencies/` | #2 | dependencies, licences, vulnerabilities (Python and Rust) | W3 |
| `defects/` | #3 | fix commits by module and error class; issues/PRs | W4 |
| `formats/` | #4 | readers/writers of files and devices with hard-coded values | W5 |
| `os-ru/` | #5 | OS-specific code and Russian specifics, with manual classification | W6 |
