# Corpus manifest (TASK-8 AC #2, Stage 2 S3)

Built by `scripts/corpus/catalog.py` on `$SPORTORG_CORPUS/raw` and `inventory.csv` as they were at the run; the corpus is still being assembled. Directories by their neutral names, files by `<directory>/<keyed hash of the path>`; no file name, race name or personal value. The anonymized copies are outside the repository (D2 (a)), in the cache named in `commands.txt`, with `MANIFEST.json`.

Key id `98e603834506`. 25 directories, 63 race files, 100 races, 24 distinct starts (races that share a race id or the same persons count once).

- kinds of files: html 110, pdf 33, race 63, readout-log 1, sportorg-log 1, text 26
- person cards by card type: 8 digits 10, SI10 297, SI11 196, SI5 290, SI5 series 2 99, SI5 series 3 15, SI5 series 4 1, SI6 593, SI8 2282, SI9 3661, SIAC1 18952, gap 13, none 861, pCard 1190, tCard 221
- race file formats: cp1251 6, gzip 28, utf-8 29
- SportOrg versions of the last save: (none) 1, 0.11.0.0 1, 1.3.0.0 2, 1.4.0.0 1, 1.5.0.0 4, 1.6.0.0 18, v1.7.1 16, v1.7.2 1, v1.8.0b1 13, v1.8.0b2 6
- races with `result_processing_mode = ardf`: 0
- files with `scores_mode = formula` (R22): 0
- leak check of the copies: leak 0, residual 29 (residual by category: residual:contact 5, residual:org 1, residual:person 1, residual:place 10, residual:text 12)
- status comments (C1): rule clause kept 5312, clause kept and hint masked 0, masked 6

| directory | kinds | files.tsv: listed / matched / missing on disk / not listed / other hash | passport |
|---|---|---|---|
| C01 | html 1, race 2, text 1 | 3 / 3 / 0 / 1 / 0 | — |
| C02 | html 1, race 1, text 1 | 2 / 2 / 0 / 1 / 0 | — |
| C03 | html 5, pdf 3, race 3, text 1 | 11 / 11 / 0 / 1 / 0 | — |
| C04 | html 1, race 1, text 1 | 2 / 2 / 0 / 1 / 0 | — |
| C05 | html 2, race 6, text 1 | 8 / 8 / 0 / 1 / 0 | — |
| C05b | race 3, text 1 | 3 / 3 / 0 / 1 / 0 | — |
| C06 | html 4, race 2, text 1 | 6 / 6 / 0 / 1 / 0 | — |
| C07 | html 5, pdf 2, race 2, text 2 | 10 / 10 / 0 / 1 / 0 | — |
| N01 | html 14, race 5, text 1 | 19 / 19 / 0 / 1 / 0 | — |
| N02 | html 21, pdf 4, race 4, text 1 | 29 / 29 / 0 / 1 / 0 | — |
| N03 | html 16, pdf 9, race 4, text 1 | 29 / 29 / 0 / 1 / 0 | — |
| N04 | html 5, pdf 4, race 3, text 1 | 14 / 12 / 2 / 1 / 0 | — |
| N04b | html 4, race 2, text 1 | 6 / 6 / 0 / 1 / 0 | — |
| N05 | html 3, race 1, text 1 | 4 / 4 / 0 / 1 / 0 | — |
| N06 | html 1, pdf 1, race 1, text 1 | 3 / 3 / 0 / 1 / 0 | — |
| N07 | html 1, race 1, readout-log 1, sportorg-log 1, text 1 | 2 / 2 / 0 / 3 / 0 | — |
| N08 | html 1, race 1, text 1 | 2 / 2 / 0 / 1 / 0 | — |
| N09 | html 11, pdf 7, race 2, text 1 | 20 / 20 / 0 / 1 / 0 | — |
| N10 | html 2, pdf 1, race 1, text 1 | 4 / 4 / 0 / 1 / 0 | — |
| N12 | html 4, race 3, text 1 | 7 / 7 / 0 / 1 / 0 | — |
| N13 | html 6, pdf 1, race 4, text 1 | 10 / 10 / 0 / 2 / 0 | — |
| N14 | html 1, pdf 1, race 2, text 1 | 4 / 4 / 0 / 1 / 0 | — |
| N15 | html 1, race 1, text 1 | 2 / 2 / 0 / 1 / 0 | — |
| Q2 | race 4, text 1 | 4 / 4 / 0 / 1 / 0 | — |
| R1 | race 4, text 1 | 4 / 4 / 0 / 1 / 0 | — |

| race file | format | shape | version | races: type / mode / persons / results | same start as | leaks |
|---|---|---|---|---|---|---|
| C01/2c64d3d295c1 | utf-8 | races | 1.3.0.0 | INDIVIDUAL_RACE / time / 291 / 195 | 1 | 0 |
| C01/492aeefcee2f | cp1251 | single race | None | INDIVIDUAL_RACE / time / 291 / 195 | 1 | 0 |
| C02/b6306ffadea6 | utf-8 | races | 1.3.0.0 | INDIVIDUAL_RACE / time / 250 / 218 | 0 | 0 |
| C03/3c9fb767a32f | cp1251 | races | 1.5.0.0 | INDIVIDUAL_RACE / time / 341 / 293 | 2 | 0 |
| C03/db66b1180b9a | cp1251 | races | 1.5.0.0 | INDIVIDUAL_RACE / time / 292 / 292 | 2 | 0 |
| C03/9725bb6dbdd2 | cp1251 | races | 1.5.0.0 | INDIVIDUAL_RACE / time / 292 / 292; RELAY / time / 289 / 291 | 2 | 0 |
| C04/6fd5e5494153 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 84 / 84 | 33 | 0 |
| C05/5e5549beccc9 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 491 / 490 | 33 | 0 |
| C05/ce7cda5435ac | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 479 / 479 | 33 | 0 |
| C05/39731ac7e971 | utf-8 | races | 1.6.0.0 | RELAY / time / 471 / 470 | 33 | 0 |
| C05/164cd631c6dc | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 656 / 665 | 33 | 0 |
| C05/abaa6d477530 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 479 / 479; INDIVIDUAL_RACE / time / 656 / 665; INDIVIDUAL_RACE / time / 650 / 650 | 99 | 0 |
| C05/522fd2552cdb | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 491 / 490; INDIVIDUAL_RACE / time / 471 / 470; INDIVIDUAL_RACE / time / 479 / 479; INDIVIDUAL_RACE / time / 656 / 665; INDIVIDUAL_RACE / time / 650 / 650 | 165 | 0 |
| C05b/487b8e321b36 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 650 / 655 | 33 | 0 |
| C05b/724a195e6cba | utf-8 | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 479 / 479; INDIVIDUAL_RACE / time / 656 / 665; INDIVIDUAL_RACE / time / 106 / 109 | 99 | 0 |
| C05b/cab8253f25e1 | utf-8 | races | v1.7.2 | INDIVIDUAL_RACE / time / 113 / 113 | 33 | 0 |
| C06/0a23103384e5 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 109 / 109 | 33 | 0 |
| C06/42790523ed5a | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / scores / 49 / 48 | 33 | 0 |
| C07/2b07e2e56182 | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 391 / 405; INDIVIDUAL_RACE / time / 403 / 411; RELAY / time / 398 / 403 | 17 | 0 |
| C07/e6e75e52cfda | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 145 / 411; INDIVIDUAL_RACE / time / 141 / 403 | 17 | 0 |
| N01/03087790dcb5 | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 106 / 117; INDIVIDUAL_RACE / time / 103 / 122; INDIVIDUAL_RACE / time / 96 / 117; INDIVIDUAL_RACE / time / 113 / 119 | 48 | 0 |
| N01/7bbcd6387a3d | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 106 / 117 | 16 | 0 |
| N01/f5c58ec1fc2e | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 103 / 122 | 16 | 0 |
| N01/788db7fe5835 | gzip | races | v1.8.0b2 | RELAY / time / 97 / 117 | 16 | 0 |
| N01/7e5a1d85271d | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 113 / 119 | 16 | 0 |
| N02/17283244e1e3 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 60 / 60 | 5 | 0 |
| N02/efcdaafdd365 | gzip | races | v1.7.1 | RELAY / time / 60 / 61 | 5 | 0 |
| N02/29b4e3001635 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 60 / 60; MULTI_DAY_RACE / time / 60 / 60 | 10 | 0 |
| N02/d063a2da9d84 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 60 / 60; INDIVIDUAL_RACE / time / 60 / 62 | 10 | 0 |
| N03/74e2e412b83f | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 270 / 269; INDIVIDUAL_RACE / time / 270 / 269; INDIVIDUAL_RACE / time / 269 / 269 | 24 | 0 |
| N03/bd1e19c8c656 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 268 / 269; INDIVIDUAL_RACE / time / 270 / 269; RELAY / time / 269 / 269 | 24 | 0 |
| N03/7b6ca1a77523 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 270 / 269; INDIVIDUAL_RACE / time / 268 / 269; RELAY / time / 269 / 269 | 24 | 0 |
| N03/1ad41def7986 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 270 / 269; INDIVIDUAL_RACE / time / 270 / 269; RELAY / time / 267 / 267 | 24 | 0 |
| N04/44778e16e4d4 | gzip | races | v1.8.0b1 | RELAY / time / 44 / 21 | 4 | 0 |
| N04/d65244b424c4 | utf-8 | races | v1.8.0b1 | INDIVIDUAL_RACE / scores / 175 / 175 | 4 | 0 |
| N04/fb692407121a | utf-8 | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 31 / 31 | 4 | 0 |
| N04b/88de9a368511 | utf-8 | races | v1.7.1 | INDIVIDUAL_RACE / scores / 255 / 239 | 4 | 0 |
| N04b/35f5404dbbe8 | utf-8 | races | v1.7.1 | INDIVIDUAL_RACE / time / 258 / 37 | 4 | 0 |
| N05/8e7ae32c0d31 | utf-8 | races | 0.11.0.0 | INDIVIDUAL_RACE / time / 66 / 65 | 0 | 0 |
| N06/6975e0478084 | utf-8 | races | 1.4.0.0 | INDIVIDUAL_RACE / time / 242 / 189 | 0 | 0 |
| N07/d33becb09434 | utf-8 | races | v1.7.1 | RELAY / time / 146 / 151 | 33 | 0 |
| N08/ae9fe5fc3fb4 | gzip | races | v1.8.0b2 | INDIVIDUAL_RACE / time / 161 / 135 | 33 | 0 |
| N09/c0f7f8d166b9 | gzip | races | v1.7.1 | INDIVIDUAL_RACE / time / 91 / 108; INDIVIDUAL_RACE / time / 91 / 99; INDIVIDUAL_RACE / time / 89 / 93; INDIVIDUAL_RACE / time / 92 / 94 | 7 | 0 |
| N09/75229e81d712 | gzip | races | v1.7.1 | RELAY / time / 92 / 94 | 5 | 0 |
| N10/d32263a3fbee | cp1251 | races | v1.7.1 | INDIVIDUAL_RACE / time / 254 / 666 | 33 | 0 |
| N12/8a95ffde6b10 | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 206 / 135 | 33 | 0 |
| N12/07525bcd7ac3 | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 32 / 36 | 33 | 0 |
| N12/23992aac7105 | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 16 / 18 | 33 | 0 |
| N13/f67f346c8323 | gzip | races | v1.7.1 | RELAY / time / 275 / 262 | 4 | 0 |
| N13/d587580e8882 | gzip | races | v1.7.1 | RELAY / time / 140 / 137 | 4 | 0 |
| N13/8e1452ad8a37 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 86 / 51 | 4 | 0 |
| N13/8e3c32a7b2bd | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 138 / 280; INDIVIDUAL_RACE / time / 140 / 143; INDIVIDUAL_RACE / time / 186 / 185; INDIVIDUAL_RACE / time / 175 / 174 | 8 | 0 |
| N14/2e9b3817e401 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / scores / 364 / 364 | 1 | 0 |
| N14/86c18f6f05e9 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / scores / 364 / 364 | 1 | 0 |
| N15/a05829ab5422 | cp1251 | races | 1.5.0.0 | INDIVIDUAL_RACE / time / 55 / 48 | 0 | 0 |
| Q2/766475f2834f | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 750 / 753; RELAY / time / 743 / 745; INDIVIDUAL_RACE / time / 730 / 732 | 16 | 0 |
| Q2/8195d26c95ba | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 760 / 758 | 16 | 0 |
| Q2/68690c30de67 | gzip | races | v1.8.0b1 | RELAY / time / 748 / 748 | 16 | 0 |
| Q2/f21a8a2906be | gzip | races | v1.8.0b1 | INDIVIDUAL_RACE / time / 734 / 734 | 16 | 0 |
| R1/009b442d5599 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 404 / 406; INDIVIDUAL_RACE / time / 342 / 338; INDIVIDUAL_RACE / time / 416 / 409 | 99 | 0 |
| R1/50fed5d890c3 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 404 / 400 | 33 | 0 |
| R1/d7dd47952e76 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 404 / 380; RELAY / time / 342 / 335 | 66 | 0 |
| R1/06ac0f7b7377 | utf-8 | races | 1.6.0.0 | INDIVIDUAL_RACE / time / 398 / 384; INDIVIDUAL_RACE / time / 416 / 405 | 66 | 0 |

Passport (`inventory.csv`): unfilled cells per column: days 25, edits_after_print 25, may_share 25, persons 25, processing_mode 25, protocol_kind 25, protocol_matches_file 25, protocol_signed 25, punch_system 25, race_type 25, resaved_after_race 25, source 25, special_cases 25, sport 25, version_race_day 25.
