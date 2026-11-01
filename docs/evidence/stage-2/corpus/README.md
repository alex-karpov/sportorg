# Anonymization and corpus manifest (Stage 2, S3; TASK-8 AC #2)

Every `.json`/`.md` file here except `*.agent.md` is output of a script; the commands are in
`commands.txt`. Decisions applied: Д1 (а) with the additions of 2026-10-31, Д2 (а), Д3 (а)
(`docs/reports/stage-2-prompt.md`); locality `[мейнтейнер: 2026-11-01]` (plan, S3).

| File | What it shows |
|---|---|
| `synthetic.{json,md}` | the whole pipeline on a synthetic corpus in the real layout, with a fixed synthetic key: rebuild byte-identical, locality (edit another file, add a file, edit one record), leak check of every copy, invariant (oracle output before and after byte-identical) |
| `manifest.{json,md}` | the corpus manifest: per directory the kinds of files, `files.tsv` against the disk, the passport; per race file format, shape, version, hashes of the original and the copy, per race the settings that choose the calculation and counts, the leak check of the copy; races that are one start; `scores_mode = formula` files (R22); ARDF races |
| `invariant.{json,md}` | the oracle (first lane, CPython 3.8.20) on every runnable corpus file and its anonymized copy |
| `findings.agent.md` | the agent's findings and questions for the maintainer |

## Scripts

| Script | Role |
|---|---|
| `scripts/corpus/pseudonym.py` | key from `SPORTORG_ANONYMIZATION_KEY` (no key → error, never printed); `normalize` (NFC, case fold, ё → е, whitespace); pseudonyms as HMAC of the normalized value plus a suffix from HMAC of the exact value when it is not in the plain form; keyed permutations (Feistel with cycle walking, one cycle, so no fixed point) for card numbers inside their card-type range and for birth days inside their year |
| `scripts/corpus/anonymize.py` | Д1 field by field; unknown keys of persons, results, organizations, race data, settings and the file → text pseudonyms, counted by key name |
| `scripts/corpus/racefile.py` | bytes → text by the oracle's rule (gzip, UTF-8, cp1251; ADR-0009 T6); kinds by content: race, json, pdf, html, zip, image, readout-log, sportorg-log, text, binary |
| `scripts/corpus/leakcheck.py` | `check_pair` (original vs copy, by field and by record), `leak_paths` (where, never what), `scan` (text files and commit messages against every corpus race file and legacy `tests/data/test.json`) |
| `scripts/corpus/catalog.py` | walks `raw/`, anonymizes, builds the manifest and the cache `MANIFEST.json` |
| `scripts/corpus/invariant.py` | oracle before and after, on copies in a temporary directory (legacy opens gzip read-write, F7) |
| `scripts/corpus/evidence.py` | the two commands of `commands.txt` |

## What the manifest shows and what it hides

- Directories by their names when neutral (`C01`), else `dir-<keyed hash>`; files by
  `<directory>/<keyed hash of the path>`: from the name, not the position, so a new file does not
  renumber the others. No file name, title, place or personal value (R21).
- Hashes: SHA-256 of the original bytes and of the copy; keyed hashes (`race_key`, `persons_key`)
  of the race id and of its person ids, which mark the same race in a day file and in the file of
  the whole event without revealing either.
- The passport: only values from the vocabulary of `docs/data-request.md`; free text as `filled`;
  `source` never; counts of unfilled cells.
- Other files (protocols, notes, logs): kind, size and hash; a readout log adds counts of
  readouts and punches, legacy's log counts of lines per level and per code location (`file:line`), never a message. Their content is not anonymized
  and not copied.
- The leak check: `leak:` counts must be 0; `residual:` counts a sensitive value that also stands
  in a kept field of the same original (a group name, a setting legacy reads, a key of the schema),
  which the anonymization keeps by Д1.
- `key_id` tells keys apart: with another key every pseudonym and hash of the copies changes.

## Limits

- The corpus is being assembled (25 directories at the run); `inventory.csv` has only `id`
  filled. The manifest describes the disk at the run; reruns replace it.
- Given names are searched in copies (`check_pair`) but not in free text (`scan`): too common.
- Numbers in free text are searched only for cards of six digits or more and birth dates other
  than 1 January; a coincidence in a synthetic output is counted apart.
- Logs and protocols are counted, not anonymized (questions in `findings.agent.md`).
