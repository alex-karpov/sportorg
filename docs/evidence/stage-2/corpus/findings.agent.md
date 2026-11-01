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
