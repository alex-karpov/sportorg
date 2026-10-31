# Oracle canary (TASK-8 AC #1)

`inputs/individual.json` with the finish of bib 101 moved 3 minutes later, through the same oracle (first lane). Also asserted by `tests/scripts/oracle/test_oracle_cli.py::test_finish_change_moves_place`.

| bib | before | after |
|---|---|---|
| 101 | OK, place 1, 1800000 ms | OK, place 3, 1980000 ms |
| 102 | OK, place 2, 1920000 ms | OK, place 1, 1920000 ms |
| 103 | OK, place 2, 1920000 ms | OK, place 1, 1920000 ms |
| 107 | OK, place 4, 2100000 ms | OK, place 4, 2100000 ms |

Canary fired (place and time of bib 101 changed): True
