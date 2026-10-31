# Oracle lanes and determinism (TASK-8 AC #1, ADR-0009 T1)

Each input runs three times: twice on the first lane and once on the second. `run.json` names the interpreter, so between lanes only `results.json`, `stored.json` and `comparison.json` are compared.

| input | first lane | rerun: 4 files identical | second lane: 3 data files identical |
|---|---|---|---|
| inputs/individual.json | 3.8.20 | True | 3.13.17: True |
| inputs/relay.json | 3.8.20 | True | 3.13.17: True |
| inputs/rogaine.json | 3.8.20 | True | 3.13.17: True |
