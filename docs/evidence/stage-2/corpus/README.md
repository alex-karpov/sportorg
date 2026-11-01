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
| `logs.agent.md` | a sub-agent's study, from code only, of what legacy's two logs hold and how to anonymize them |

## Scripts

| Script | Role |
|---|---|
| `scripts/corpus/pseudonym.py` | key from `SPORTORG_ANONYMIZATION_KEY` (no key → error, never printed); `normalize` (NFC, case fold, ё → е, invisible format marks dropped, whitespace); pseudonyms as HMAC of the normalized value plus a suffix from HMAC of the exact value when it is not in the plain form; keyed permutations (Feistel with cycle walking, one cycle, so no fixed point) for card numbers inside their card-type range and for birth days inside their year |
| `scripts/corpus/anonymize.py` | Д1 field by field; a status comment that is a rule clause (`п.п.6.6.4`, `пп6.6.4`, alone or with one of legacy's hints) kept, a free hint after a clause masked, any other comment masked, also where legacy copies it (`result`, `result_relay`, `result_current`, the day fields of `multi_day_results`) `[мейнтейнер: 2026-11-01]`; a card number in a shape legacy cannot read → 0; unknown keys of persons, results, organizations, race data, settings and the file → text pseudonyms, counted by key name |
| `scripts/corpus/racefile.py` | bytes → text by the oracle's rule (gzip, UTF-8, cp1251; ADR-0009 T6); kinds by content: race, json, pdf, html, zip, image, readout-log, sportorg-log, text, binary |
| `scripts/corpus/leakcheck.py` | `check_pair` (original vs copy, by field and by record), `leak_paths` (where, never what), `scan` (text files and commit messages against every corpus race file and legacy `tests/data/test.json`) |
| `scripts/corpus/catalog.py` | walks `raw/`, anonymizes, builds the manifest and the cache `MANIFEST.json` |
| `scripts/corpus/invariant.py` | oracle before and after, on copies in a temporary directory (legacy opens gzip read-write, F7) |
| `scripts/corpus/evidence.py` | the two commands of `commands.txt` |

## What the manifest shows and what it hides

- Directories by their names when they follow the corpus guide's ids (`C01`, `N04b`, `Q2`), else
  `dir-<keyed hash>`; files by
  `<directory>/<keyed hash of the path>`: from the name, not the position, so a new file does not
  renumber the others. No file name, title, place or personal value (R21).
- Hashes: SHA-256 of the original bytes, of the copy and of the copy's decoded text (the bytes of
  a gzip copy depend on the zlib build, the text does not); keyed hashes (`race_key`, `persons_key`)
  of the race id and of its person ids, which mark the same race in a day file and in the file of
  the whole event without revealing either.
- The passport: only values from the vocabulary of `docs/data-request.md`; free text as `filled`;
  `source` never; counts of unfilled cells.
- Other files (protocols, notes, logs): kind, size and hash; a readout log adds counts of
  readouts and punches, legacy's log counts of lines per level and per code location (`file:line`), never a message. Their content is not anonymized
  and not copied.
- Person cards counted by card type (SI5, SI6, …, `gap`, `none`), never a number.
- Status comments counted by outcome: rule clause kept, clause kept and hint masked, masked.
- The leak check: `leak:` counts must be 0; `residual:` counts a sensitive value that also stands
  in a field the anonymization keeps (a group or course name, a setting legacy reads, a key of
  the schema, a kept rule clause): the copy holds it because that field is kept, not because a
  masked field was missed. `leak_paths` names the JSON path of each leak and of each residual
  (`residual <category> in <path>`), never the value. The strings legacy derives from the status
  comment (`result`, `result_relay`, `result_current`, `multi_day_results`) are not kept fields:
  a masked comment left there is a leak.
- `key_id` tells keys apart: with another key every pseudonym and hash of the copies changes.

## Limits

- The corpus is being assembled (25 directories at the run); `inventory.csv` has only `id`
  filled. The manifest describes the disk at the run; reruns replace it.
- Given names and middle names (formed from given names) are searched in copies (`check_pair`)
  but not in free text (`scan`): too common. `scan` searches surnames (four letters or more),
  organizations and places (five or more), contacts and codes (whole values). A value that also
  stands in a kept field of its file (a key of the schema, a group name) or in legacy's own texts
  (status titles, the hints of rule clauses) is not searched: its presence in the repository says
  nothing about the corpus.
- Numbers in free text are searched only for cards and numeric codes of six digits or more and
  birth dates other than 1 January. Card numbers of five digits or fewer (SI5) are searched only
  as the value of a card field (`"card_number": 12345`): with thousands of SI5
  cards in the corpus a five-digit number in free text would match by chance
  `[мейнтейнер: 2026-11-01]`. A coincidence in a synthetic output is counted apart.
- Not addressed: keys of objects inside unknown fields stay (M5; legacy writes no personal data
  as keys); `special_cases` of the passport and setting values that match a safe pattern are
  printed as written (M9; maintainer-controlled or legacy enumerations).
- Logs and protocols are counted, not anonymized (questions in `findings.agent.md`).
