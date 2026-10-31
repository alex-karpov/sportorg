# Oracle findings — agent judgement

Agent judgement (Claude Code, Opus 5.5, session S2 of 2026-11-01), not script output, **not reviewed
by a human**.

Criteria. A *finding* is a value in this directory's script output that (1) differs between the
file and the recalculation, or (2) on a synthetic input differs from what the legacy code itself
suggests the author intended (comments, names, other code paths). Each finding names the output, the
legacy code that produces it, and a classification proposal from Stage 2 rule 8: *legacy bug*,
*local practice*, *rule gap*, or *representation* (a serialization difference, no rule involved —
added here because rule 8's three classes do not fit it). No sport rule was consulted: every
classification is `[допущение]` until the maintainer or a rules document decides. Nothing was
fixed or masked: the oracle reports what legacy computes.

## Stored vs recalculated

| # | Input | Output | Legacy code | Proposal |
|---|---|---|---|---|
| F1 | legacy `tests/data/test.json` (file version `1.0.0.0`) | `legacy-test-json.md`: 1 of 2 results differs, field `diff_ms`: the leader's stored `0` against recalculated `null` (values only, no data of the file) | `Result.to_dict` writes a zero `OTime` as `null` `[код: pysport@b548c35 sportorg/models/memory.py:612]`; the file was saved by an older version that wrote `0` | representation: the same "no time behind the leader" in two encodings. Not a recalculation difference |

The synthetic files carry no computed values (`place` 0, no `result_msec`), so their
`comparison.json` differences (13, 7 and 5) are the generator's placeholders against the
recalculation, not findings.

## Legacy behaviour seen on the synthetic inputs

| # | Output | Legacy code | Proposal |
|---|---|---|---|
| F2 | `synthetic/individual/results.json`, M21: the winner (bib 101, 30:00) has `diff_ms` 60 000, the next two 180 000. The reference is bib 105, out of competition, 29:00, first in the sorted group | `res.diff = current_result - array[0].get_result_otime()` uses the first sorted result, whatever its status of competition; the out-of-competition check comes after it `[код: pysport@b548c35 sportorg/models/result/result_calculation.py:157,164-166]` | legacy bug (candidate): a time behind the leader measured from a runner who has no place. Visible wherever a protocol prints the time behind |
| F3 | `synthetic/rogaine/results.json`: bib 5 (5 points, 50:00) has place 3, the same as bibs 2 and 4 (7 points, 50:00) | a shared place is decided by `current_result != last_result`, which compares time only, also in score mode `[код: pysport@b548c35 sportorg/models/result/result_calculation.py:156,169-174]` | legacy bug (candidate): in a rogaine fewer points with the same time share a place |
| F4 | same file: `diff_ms` 85 950 000 (bib 1) and 85 650 000 (bibs 2, 4, 5): negative differences to a leader who took longer, carried over midnight | `OTime` adds a day to a negative value `[код: pysport@b548c35 sportorg/common/otime.py:150-155]`; `diff` is computed for score mode too `[код: …/result_calculation.py:157]` | legacy bug (candidate) in the time behind; `diff_scores` (3, 8, 10) carries the meaning in score mode |
| F5 | `synthetic/individual/results.json`: DNS without a finish (bib 106) has `time_ms` 50 100 000 (clock 00:00:00 minus start 10:05, over midnight) | a result without a stored finish takes the clock `[код: pysport@b548c35 sportorg/models/memory.py:499,878-882]` | not a finding about rules: the oracle fixes the clock (`--now`, `run.json`), and the status keeps the result out of the places. Recorded because golden files will contain this value |
| F6 | a file with several races that is not a multi-day event. Seen once in S2, not kept as evidence: with the driver's second pass removed (only `File.open`), the synthetic rogaine as the second race of a two-race file differed from the rogaine alone, and `test_each_race_of_a_multi_race_file_in_its_own_context` failed; restored, it passes | on open, `load()` recalculates every race, but the check and the course lookup read the *current* race (`_check_all` → `ResultChecker.check_all()` over `race().results`; `find_course` uses `race()`) `[код: pysport@b548c35 sportorg/modules/backup/json.py:42-44, sportorg/models/result/result_tools.py:105, sportorg/models/memory.py:2102]`; the GUI recalculates each race as the current one only for a multi-day event, also on a race switch `[код: pysport@b548c35 sportorg/gui/main_window.py:659,678-686, sportorg/gui/dialogs/settings.py:345-348]` | legacy bug (candidate): a non-current race may show statuses and places computed in the context of another race until something recalculates it. The oracle recalculates each race in its own context (ADR-0009 T5) |

## Not a finding, but a risk

- A race file can make legacy run code: `scores_mode = formula` evaluates `scores_formula` with
  `eval` `[код: pysport@b548c35 sportorg/models/result/score_calculation.py:21-27]`. The oracle runs
  it in the legacy process, with the hermetic environment and the rights of the session. Corpus files
  come from the maintainer. Proposed as R22 in `docs/risks.md`.

## Questions for the maintainer

1. F2–F4: classify (legacy bug / local practice / rule gap)? Recommendation: check against the rules
   of the sport (time behind the leader; ranking in a rogaine) before Stage 3; until then golden files
   keep legacy's values, with these findings listed in the stage report.
2. F6: should the oracle reproduce what the operator sees after opening such a file (each
   non-current race as `load()` left it) instead of each race in its own context? Options: (a) own
   context (as built; recommended: it is what a recalculation in the GUI gives); (b) the state after
   `load()`; (c) both, reported side by side. The corpus will show whether such files exist.
3. Files that are neither gzip nor UTF-8 (legacy reads them in the machine's locale): (a) refuse
   them, as built, and count them in the corpus manifest (S3) (recommended); (b) let the oracle try
   cp1251, the Russian Windows locale `[допущение]`; (c) re-encode them to UTF-8 while preparing the
   corpus.
4. F1: may the comparison treat `diff_ms` `0` and `null` as equal? Options: (a) keep it as a
   difference of class *representation* (recommended: nothing is hidden, the corpus will show how
   common it is); (b) map `null` to `0` in the normalizer; (c) leave `diff_ms` out of the comparison.
