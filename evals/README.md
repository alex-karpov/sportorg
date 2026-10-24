# Plugin pilot: eval suite

Purpose (brief, Stage 0): decide with data whether the Claude Code plugins `code-modernization` and
`superpowers` help on this project. `claude plugin eval <plugin> --ablation with-without` runs every
case with and without the plugin and reports the score delta. Cases come from the legacy history
(`docs/evidence/stage-0/legacy-fix-candidates.md`): a real bug, its parent commit as the starting
point, and the test added by the real fix as the visible failing test.

Layout (format of `claude plugin eval`, Claude Code ≥ 2.1.269):

```
evals/
  smoke/                 # no tools, one turn: proves the runner works on this machine
    prompt.md
    graders/ready.md
  legacy-fixes/<case>/
    prompt.md            # frontmatter: name, tags, runs, max_turns, timeout_seconds; body = task
    case.yaml            # schema_version "1.1", context.scaffold_script
    scaffold.sh          # clones the pinned legacy repo at the parent commit, adds the real test
    graders/*.md         # llm rubric + regex on the final message
```

## Running

`claude plugin eval` reads cases from the *plugin's* eval directory when the target is an installed
plugin, so the repo's own cases are run with the repo as target (`.`) and the plugin under test copied
into the repo (the runner refuses junctions that resolve outside it and plugin copies inside `evals/`):

```
uv run python scripts/pilot_setup.py code-modernization      # -> tools/plugins/code-modernization (git-ignored)
```

Smoke (cheap, no shell tools; works on native Windows). `smoke` runs without a plugin, `smoke-plugin`
loads the copied plugin and runs both arms:

```
claude plugin eval . --eval-dir evals --case smoke --runs 1 --ablation none --no-publish --trust-plugin --max-cost-usd 0.50 --model haiku
claude plugin eval . --eval-dir evals --case smoke-plugin --runs 1 --ablation with-without --no-publish --trust-plugin --max-cost-usd 1 --model haiku
```

Full pilot (maintainer consent + ceiling required, Backlog task-2). Shell tools need a sandbox
backend, so run it from WSL2, not native Windows:

```
claude plugin eval . --eval-dir evals --tag legacy --scaffold --allow-tools Bash Edit Write \
  --ablation with-without --trust-plugin --max-cost-usd 25 --json results.json
```

`EVAL_LEGACY_SRC` (env, optional) points at the read-only legacy checkout used as the clone source;
the scaffold never writes into it. Results go to `evals/results/` (git-ignored); copy the aggregate
and the HTML report to `docs/evidence/pilot/` when a run is kept as evidence.

## Case list

| case | legacy fix | parent | area | test added by the fix |
|---|---|---|---|---|
| c1-multiday-overtime | 57ac99d04 | ced57547d | results / status | tests/test_result_checking.py |
| c2-qualification-names | 2b316380f | 7b03c9587 | import, national (RU) | tests/test_qualification.py |
| c3-sfrx-multiday-import | 3b55fe8b0 | 9e01b2437 | import format | tests/test_sfrx.py + tests/data/sfrx_file.sfrx |
| c4-send-selected-partial | b0391dd14 | 980659f9e | reports / teamwork export | tests/test_race_partial.py |
| f1-credit-time | 20b51465f | f92d32f1b | results (feature with tests) | tests/test_credit_calculation.py |
| f2-relay-best-team | e0c0480a9 | 0952a379e | relay (feature with tests) | tests/test_relay_results.py |
| f3-new-penalty | 6446c7008 | fccfc27dc | penalties (feature with tests) | tests/test_penalty_checking.py, tests/test_result_checking.py |

Not included: the other fix commits that touch tests (393b6303b, c8761e709, 42e806a58, 5170d6c31,
aee1e994e, ab72a7987, ef983f3e9) change tests only cosmetically, so no visible failing test exists
for them (see the candidates document).

Known limits: the visible test is the real fix's test, so the task is "make this test pass without
touching tests/" (SWE-bench style with a visible test). c4 is coupled to method names introduced by
the real refactor; f1–f3 are feature tasks where the tests are the specification. Scaffold viability
(legacy `uv sync --frozen` at old commits; the oldest, f2, dates from 2024-10) is checked at the
pilot run.
