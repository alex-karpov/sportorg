# Anonymization on a synthetic corpus (TASK-8 AC #2, Stage 2 S3)

Fictional data in the layout of the real corpus (`scripts/corpus/evidence.py: synthetic_corpus`), anonymized with a fixed synthetic key. Locality: editing a file of S02 and adding a file to S01 leave every other copy byte-identical; editing one record leaves the other records as before. The invariant runs the oracle (first lane) on each runnable original and its copy and compares `results.json`, `stored.json` and `comparison.json` byte for byte.

| check | result |
|---|---|
| rebuild_identical | True |
| locality_edit_other_file | True |
| locality_edit_changes_the_edited_file | True |
| locality_add_file | True |
| locality_one_record | True |
| leaks | 0 |

## Manifest of the synthetic corpus

Key id `737280f2c208`. 3 directories, 7 race files, 8 races, 6 distinct starts (races that share a race id or the same persons count once).

- kinds of files: pdf 1, race 7, readout-log 1, sportorg-log 1, text 2
- race file formats: cp1251 1, gzip 2, utf-8 4
- SportOrg versions of the last save: (none) 1, v1.8.0b2 6
- races with `result_processing_mode = ardf`: 0
- files with `scores_mode = formula` (R22): 1
- leak check of the copies: leak 0, residual 0 (residual by category: —)

| directory | kinds | files.tsv: listed / matched / missing on disk / not listed / other hash | passport |
|---|---|---|---|
| S01 | pdf 1, race 2, text 1 | 3 / 2 / 1 / 2 / 0 | sport ориентирование |
| S02 | race 3, readout-log 1, sportorg-log 1, text 1 | — | — |
| S03 | race 2 | — | — |

| race file | format | shape | version | races: type / mode / persons / results | same start as | leaks |
|---|---|---|---|---|---|---|
| S01/bdeea896cc01 | utf-8 | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 10 / 10 | 0 | 0 |
| S01/9ac0179a6f69 | cp1251 | single race | None | INDIVIDUAL_RACE / time / 2 / 2 | 0 | 0 |
| S02/fee3f0fc8ba6 | gzip | races | v1.8.0b2 | MULTI_DAY_RACE / time / 5 / 5; MULTI_DAY_RACE / time / 4 / 4 | 2 | 0 |
| S02/5f00dec11b5f | utf-8 | races | v1.8.0b2 | MULTI_DAY_RACE / time / 5 / 5 | 1 | 0 |
| S02/9a6113e14444 | utf-8 | races | v1.8.0b2 | MULTI_DAY_RACE / time / 4 / 4 | 1 | 0 |
| S03/2c45119473a3 | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 11 / 11 | 0 | 0 |
| S03/0fd67593e806 | utf-8 | races | v1.8.0b2 | INDIVIDUAL_RACE / scores / 5 / 5 | 0 | 0 |

Passport (`inventory.csv`): unfilled cells per column: days 3, edits_after_print 3, may_share 3, persons 3, processing_mode 3, protocol_kind 3, protocol_matches_file 3, protocol_signed 3, punch_system 3, race_type 3, resaved_after_race 3, source 3, special_cases 3, sport 2, version_race_day 3.

## Invariant: the oracle before and after

Lane `.venv`: 6 files ran, 6 identical, 0 different, 1 not run.

| race file | identical | not identical: paths and counts |
|---|---|---|
| S01/bdeea896cc01 | True | — |
| S01/9ac0179a6f69 | True | — |
| S02/fee3f0fc8ba6 | True | — |
| S02/5f00dec11b5f | True | — |
| S02/9a6113e14444 | True | — |
| S03/2c45119473a3 | True | — |
| S03/0fd67593e806 | None | scores_mode = formula (R22) |
