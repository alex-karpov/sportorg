# Corpus and anonymization findings — agent judgement

Agent judgement (Claude Code, Opus 5.5, session S3 of 2026-11-01), not script output, **not reviewed
by a human**.

Criteria. A *finding* is something in this directory's script output (or in a test that ran
legacy) where legacy, the corpus guide or the corpus behave otherwise than the code or the
documents of this project expect. Each names the output, the code, and a classification proposal
from Stage 2 rule 8 (*legacy bug*, *local practice*, *rule gap*); every classification is
`[допущение]` until the maintainer decides. A *question* is a choice the session made with an
explicit `[допущение]` because no decision existed; the recommendation is the option built.
The agent never opened a corpus file: everything below comes from counts, hashes, JSON paths and
legacy stack frames printed by the scripts of `commands.txt`.

## Findings

| # | Output | Code | Proposal |
|---|---|---|---|
| F7 | First corpus run of the invariant: all 28 gzip files failed with `OSError`; `tests/scripts/corpus/test_invariant.py::test_a_read_only_gzip_original_runs` failed the same way on a synthetic gzip file with mode 0444 before the fix | legacy opens a gzip race file with mode `r+b` (read **and write**) also to read it: `mode = f"{mode}+b"` after `is_gzip_file` `[код: pysport@b548c35 sportorg/modules/backup/file.py:33-41]`. `raw/` of the corpus is read-only for the sandbox | legacy bug (candidate): an operator who follows `docs/data-request.md` («сразу получают атрибут „только чтение“») cannot open the gzip original in legacy `[допущение по коду: not tried on Windows]`; a discrepancy between the guide and legacy (rule 9). Done here: the invariant runs the oracle on copies in a temporary directory, so the original never sits behind a write handle. S4 runs the oracle on the corpus too: recommended to make the copy in `scripts/oracle_cli.py` itself (S2 code, so not changed in S3) |
| F8 | `invariant.md`, `C02/b6306ffadea6` (version `1.3.0.0`, UTF-8): legacy fails on the original and on the copy alike: `ValueError at sportorg/models/memory.py:1155:check` | `ResultSportident.check` parses a course control template with a list `…(31,32,35-45)` and calls `int()` on the punch code and on the parts of the list `[код: pysport@b548c35 sportorg/models/memory.py:1147-1160]`; a code or a part that is not a whole number raises, and nothing catches it on the way from `File.open` | open: legacy bug (no guard for a template the GUI accepts) or a file legacy@b548c35 cannot read any more (saved by 1.3.0.0). Groups and courses are kept by Д1, so the copy fails the same way: the anonymization is not the cause. Check: open the file in legacy's GUI at `b548c35` |

**F7, maintainer's check on Windows `[мейнтейнер: 2026-11-01]`: legacy bug.** A gzip file with the
read-only flag: `File.open` fails with `PermissionError: [Errno 13]` (shown in the Logs tab). A
file saved without gzip and flagged read-only opens, but saving fails silently (only an error in
the Logs tab) and leaves `<file>.json.tmp` beside it: `save` writes `<file>.tmp` and then renames
it over the original `[код: pysport@b548c35 sportorg/modules/backup/file.py:62-69]`, and the rename
onto a read-only file fails `[допущение по коду и наблюдению мейнтейнера]`. The maintainer's
traceback is not copied here: it names a local user directory.

**F8, follow-up `[мейнтейнер: 2026-11-01]`:** confirmed in legacy's GUI: `ValueError: invalid
literal for int() with base 10: ''`; running 1.3.0 needs its own environment, not tried. The
manifest now counts, per race, list templates with a part `int()` refuses and punch codes that
are not whole numbers (`list_templates_not_integer`, `punch_codes_not_integer`): only this file
has any, 2 templates and 0 punch codes, so an empty part of a list template is the cause. History
(read only): at 1.3.0.0 (`615049a`, `VERSION = Version(1, 3, 0, 0)`) a list matched by string,
`str(cur_code) in template[…].split(',')`, so an empty part matched nothing and raised nothing
`[код: pysport@615049a sportorg/models/memory.py:876-883]`; commit `0f3a0a8` (2019-11-26, "CP
generic set e.g. '%(31,32,35-45)'") parses each part with `int()` `[история: pysport 0f3a0a8]`.
Classified: legacy bug `[мейнтейнер: 2026-11-01]` (a regression in reading older files since
`0f3a0a8`).

## Questions (built as recommended, `[допущение]` until answered)

1. **A pseudonym for a spelling variant.** The plan says "a pseudonym is a function of the key and
   the normalized value only". Legacy joins the days of a multi-day event by the exact string
   `surname name group` `[код: pysport@b548c35 sportorg/models/memory.py:830-845,1401-1422]`, and a
   relay team's name by the exact organization name (`result_calculation.py:192`,
   `memory.py:2716`). If two spellings of one person (Ёжиков/Ежиков) got one pseudonym, the
   anonymized file would join what legacy keeps apart: the canary
   `test_the_invariant_sees_a_merged_spelling` turns red exactly so. Options: (a) base from the
   normalized value, plus a 4-character suffix from the exact value when it is not in the plain form
   (title case, single spaces, no ё) — built; variants share the base and stay distinct, still a
   function of the key and the value; (b) normalized value only, as written — fails the invariant
   on such files; (c) exact value only — no common base for variants. Recommendation: (a).
2. **Protocols in the manifest** (110 HTML, 33 PDF in the corpus). Options: (a) kind, size and
   SHA-256 — built; (b) counts per directory only; (c) nothing. Recommendation: (a): the hash ties a
   later golden check to the file without revealing it.
3. **Logs** (N07, added 2026-11-01: a readout backup `si<date>.log` with 148 readouts and 1534
   punches, legacy's own log with 4598 lines). Both formats are legacy's
   `[код: pysport@b548c35 sportorg/modules/sportident/backup.py:29-46, sportorg/config.py:114,130]`.
   Counted now, not anonymized. Options: (a) counts only; (b) a later session anonymizes the
   readout log with the same card permutation, so it lines up with the anonymized race file (a
   second source of punches, R1, S5); legacy's log stays counts only (free text with names and
   paths); (c) leave logs out of the corpus. Recommendation: (b), not in S3.
4. **Secrets in old settings.** The corpus holds keys legacy@b548c35 no longer reads:
   `live_token` (40 races), `teamwork_token`, `teamwork_host` (85). Applied the addition to Д1
   (fields not in the list follow its rules): cleared, as `live_urls`. Printer names
   (`main_printer`, `split_printer`, one race) and other unknown strings become text pseudonyms.
   Confirm, or say which should stay.
5. **The leak check before each commit** needs the corpus and the key, so it is not a step of
   `check.py` (CI has neither). Options: (a) run by hand, command in `commands.txt` — done in this
   session before each commit; (b) a local pre-commit hook that runs it when `SPORTORG_CORPUS` is
   set and says so when it is not. Recommendation: (b), in a later session.
6. **Word matches in older documents.** A scan of all of `docs/` (not only evidence and this
   branch's changes) finds 40 lines in reports written before the corpus came (stage 0, stage 1,
   the stage 2 prompt with 8 of them, and one line of `docs/risks.md`) whose words equal a surname
   or an organization of the corpus. The agent read
   one such line: it holds only common words, among them an adjective that is also a surname
   (`[допущение]`: the scan does not say which word). They are not counted as findings of this
   session. Invented examples in this
   session's own tests were changed before the commit.
   Options: (a) leave; (b) a stop list of common words for the scan. Recommendation: (a) now.
7. **D2 (b) and R21** are untouched: the copies stay outside the repository; the manifest holds
   counts, hashes and neutral ids only.

## Maintainer's answers `[мейнтейнер: 2026-11-01]`

1. Pseudonyms of spelling variants: (a), as built.
2. Protocols in the manifest: kind, size and SHA-256, as built.
3. Logs: a sub-agent studies, from legacy's code only, what the logs hold; the maintainer notes
   that the log holds the raw byte exchange of chip readouts, with the owner's name stored in the
   chip. The manifest counts legacy's log by level and by code location (`file:line`), never a
   message. The study is `logs.agent.md`: the log was written by a build of 2025-06 after the
   v1.7.1 tag (`fd98887` or a neighbour); the SportIdent frames are logged whole in hex
   (`sportident.py:974,1047`), so card numbers and the owner bytes of the card blocks that legacy
   reads reach the log; other records may hold names (`live.py:80`), file paths and server texts.
   Proposed: extract only the SportIdent frames into a dump, map card numbers by the same
   permutation, overwrite owner bytes, recompute the CRC, drop every other message (C1); the
   readout backup keeps everything but the card number. Decided: C1, in session S5
   `[мейнтейнер: 2026-11-01]`.
4. Old tokens and hosts of the settings cleared: confirmed.
5. A local pre-commit hook for the leak check: Backlog TASK-12.
6. The maintainer asked for the list of words: written by `leakcheck scan docs backlog --words-out
   ~/.cache/sportorg-stage2/leakcheck/old-docs-words.tsv` (91 matches over `docs/` and `backlog/`,
   synthetic outputs included), outside the repository and not shown in the session: the words are
   values of the corpus. Decision pending the maintainer's reading.

## Review of S3 and the fix pass (2026-11-01)

A sub-agent (Fable, at the maintainer's request) reviewed `74105e5..HEAD` on synthetic data only:
1 critical, 4 important, 9 minor findings. Decisions `[мейнтейнер: 2026-11-01]`: C1 option (в)
with `пп` without dots as a valid clause; I3 the three points on SI5 numbers; the rest as
recommended. Each fix by TDD (the RED run before the code); outputs in this directory.

| # | Finding | Done |
|---|---|---|
| C1 | legacy copies `status_comment` into `result`, `result_relay`, `result_current` and the 14-character day fields of `multi_day_results` `[код: pysport@b548c35 sportorg/models/memory.py:480-490,702-747,969-973]`; the anonymizer kept them, the leak check called them residual | a rule clause (`п.п.6.6.4`, `пп6.6.4`, alone or with one of legacy's hints) is kept; a free hint after a clause is masked; any other comment is masked, also in the four derived strings (legacy never reads them back, `memory.py:650-700`). The leak check treats the derived strings as neither kept nor a source and searches a masked comment also as cut to 14 characters; `leak_paths` names residual paths too. Synthetic file `personal_legacy_shape` (legacy's shape). Corpus: 5312 comments kept as rule clauses, 6 masked, 0 with a free hint; `residual:text` 176 → 12 |
| — | first corpus run after C1: 1 leak (`leak:org`, one file, 12 derived strings) | without a comment legacy writes the status title `[код: pysport@b548c35 sportorg/models/memory.py:52-53,702-706; ru_RU sportorg.po]`, and a value of that file equals a title `[допущение по коду: the value was not read; the fix below turned exactly this leak into one residual and changed nothing else]`. Legacy's status titles (English and Russian, checked against legacy by a test) count as kept text |
| I1 | a file with a BOM, NBSP, ZWSP or soft hyphen was classed binary and skipped by `scan` | such text is text; `normalize` drops format marks; `scan` reads every decodable file (logs too) and prints `not text: N` |
| I2 | a card as `212345.0` or `"212 345"`, a numeric `birth_date`, a `birthday` without `birth_date` passed unmasked and unseen | a whole float is renumbered as a float, any other shape becomes 0 (counted); a non-string birth date becomes `null`; `birthday` always follows `birth_date` or is blanked; the leak check reads numbers in every shape and `birthday` by record |
| I3 | `scan` missed contacts, codes, middle names, places, SI5 cards | contacts and codes (whole values), places (five letters or more) searched; card numbers under 100 000 only as the value of a card field; the manifest counts person cards by card type (corpus: SI5 290, SI5 series 2–4 115 of 28 681 persons). Not done as proposed: middle names are not searched in text, as given names (formed from them, too common) |
| I4 | the S3 log and the message of the first S3 commit told which invented value of an S2 test had matched the corpus | the 9 unpushed commits after `74105e5` were rewritten (`git filter-branch`): the sentence removed from the message and from the plan and this file; the same commit now changes an invented card number of that test too |
| M1 | text after a birth date was written back | a date with any text after it (but a time of day) is unparsed → `null` |
| M2 | `isdigit()` accepts `²`, then `int()` raises with the value | ASCII digits only (anonymizer, leak check, passport) |
| M3 | Latin directory names up to 16 characters were printed | only the guide's ids `[A-Z]{1,2}[0-9]{1,3}[a-z]?` are printed, any other name as `dir-<hash>` |
| M4 | gzip bytes depend on the zlib build | the manifest also holds `anonymized_text_sha256` of the decoded copy |
| M5 | keys inside unknown structures are kept | not changed (legacy writes no personal data as keys); in README «Limits» |
| M6 | mask counters were partial | organizations, race data, settings (`clear:` and `mask:`), cards and codes counted |
| M7 | tests | the weak year assertion fixed; a legacy-shaped fixture and negative tests added (C1, I1–I3) |
| M8 | README wording on residuals | rewritten |
| M9 | `special_cases` and setting values matching a safe pattern are printed | not changed; in README «Limits» |

Scan of this pass: the new categories first matched words of the schema (old files hold
`address` and similar as contact and place values), counter lines of the manifest
(`"values:card_number": 844`) and a few words of this pass's code. Fixed in the scan, by TDD: values that also stand in a kept field of their file or in legacy's own
texts are not searched, short cards only as a field value, middle names not searched.

## Re-review of `aceedf4` and its fix pass (2026-11-01)

A second Fable sub-agent reviewed `aceedf4` on synthetic data only (adversarial inputs it made
itself; 252 tests passed, synthetic evidence byte-identical under two hash seeds). No critical
finding: no input of a shape legacy writes left personal data in a copy with a silent check. Four
important, ten minor. Maintainer's decisions `[мейнтейнер: 2026-11-01]`: fix 1–4, 6, 8, 9, 11–13
by TDD (RED run first); 5, 7, 10, 14 to README «Limits». Not run on the corpus: the sandbox
withholds it; the corpus part of the evidence (`commands.txt`) is for the maintainer to rerun.

| # | Finding | Done |
|---|---|---|
| 1 | the check did not find a free comment cut to 14 characters in a day field other than the last of `multi_day_results` (the next time follows without a separator) | the copy is searched field by field (`_copy_strings`, `_nodes`) |
| 2 | `scan` did not search surnames of `chief_referee`, `secretary` | added to the scanned surnames |
| 3 | a day field of digits, `:`, `.`, `,` was kept as a time: a numeric comment (phone, date, card) stayed in `multi_day_results`; non-ASCII digits too | a time is `h:mm:ss[.f]` in ASCII digits or empty |
| 4 | a numeric code written as a whole float was not masked | renumbered as a float, like cards |
| 6 | an unknown race-level key was kept text in the check, masked text in the anonymizer | the check treats it as sensitive text |
| 8 | a non-string `status_comment` was kept text in the check | sensitive text, like in the anonymizer |
| 9 | a clause with a free hint: the hint cut into a day field was not searched | the cut hint is searched |
| 11 | a birth date written as a number was not in the `scan` set | scanned as a word (not `…0101`) |
| 12 | `scan` found a card only as one token | also in groups of three (`8 123 456`, `8'123'456`, no-break spaces) |
| 13 | `пп 12345678` was kept as a rule clause | a clause number has up to three digits |
| 5, 7, 10, 14 | derived strings equal to the comment only; numbers in text fields; a name starting like a legacy hint; no free-text category in `scan` | not changed; in README «Limits» |

### Opus review of that fix pass (2026-11-01)

An Opus sub-agent reviewed the uncommitted pass on synthetic data only: nothing critical, two
important, eight minor. Maintainer's decisions `[мейнтейнер: 2026-11-01]`: fix I-1, I-2, M-1, M-2,
M-5, M-8, then M-3, M-4; M-6 and M-7 to README «Limits». Each fix by TDD (RED run first).

| # | Finding | Done |
|---|---|---|
| I-1 | the check searched the cut of a legacy hint, which the anonymizer keeps → `leak:text` on a correct copy (`пп6.6.4 # не с`) | the cut is searched as the anonymizer masks it (`status_comment_free_text(cut, cut=True)`); a clause or the start of a legacy hint is not |
| I-2 | the words of a referee field were all searched as surnames | by the maintainer's six formats (`Фамилия И. О.`, `Фамилия И.`, `И. О. Фамилия`, `И. Фамилия`, `Фамилия И.О.`, `И.О. Фамилия`) the surname is the only word of four letters or more; the code did that already, the tests now pin the formats and README names the rule |
| M-1 | a text not starting on a 14-character boundary was missed | the whole string is searched with the fields |
| M-2 | any int was a birth date in `scan` (`1990`, `0`); `"19900517"`, `19900517.0` missing | only `YYYYMMDD` other than 1 January, as an int, a whole float or ASCII digits |
| M-3 | unknown file-level keys invisible to the check | sensitive text, like in the anonymizer |
| M-4 | cards in groups with `,`, `.`, thin space, leading zero, a number before the card | all of these; the leading groups may be another number |
| M-5 | a dotted number with many groups was a rule clause | three to four numbers of one or two digits, as legacy's clauses |
| M-6, M-7 | time shape wider than legacy's; negative codes | not changed; README «Limits» |
| M-8 | README: eight letters of a cut hint | ten (no spaces around `#`) |
