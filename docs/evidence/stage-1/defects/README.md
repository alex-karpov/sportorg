# Defect history (TASK-7 criterion 3)

What: fix commits of `pysport@b548c35` by module and error class, a reproducible counts table,
issues and PRs of `sportorg/pysport` by class. Produced by `scripts/archaeology/defects.py`
(command in `commands.txt`).
- `commits.json`: per commit short sha, date, merge flag, Conventional type, `is_fix`, class,
  `product_defect`, modules, changed lines per module. `commits.md`: the fix commits.
- `counts.json`, `counts.md`: class totals, module x class, fix share per module, per-year
  counts, platform-build table, Stage 0 comparison, cache SHA-256 values.
- `issues.json`, `issues.md`: number, state, is-PR, merged, labels, created/closed year, class.
  Titles and bodies are not written.

## Definitions (plan, "Defect rule and taxonomy", approved 2026-10-25)

Fix commit (non-merge; merges are counted separately and are never fixes):
1. Conventional subject type `fix`/`hotfix` (`^(hot)?fix(\([^)]*\))?!?:`), or
2. no Conventional type, or a type outside {feat, docs, refactor, style, test, perf, chore},
   and the subject matches `FIX_RE` =
   `\b(fix(e[sd]|ing)?|bug\w*|hotfix|crash\w*|broken|regression|wrong)\b|исправ|ошибк|не работа|падени` (case-insensitive).

`ci:`/`build:` fixes are class `platform-build` and are excluded from the product defect table.
A commit that touches only `docs/`, `*.md` or images is class `docs-only` and is not a
product defect. Product defect = fix, not of type `ci`/`build`, not docs-only.

Class: if exactly one class matches the subject keywords, that class; otherwise the class of
the module with the most changed lines (path table, `classify()`); otherwise `other`.
- Keyword stems match at the start of a word; short or ambiguous stems (`ci`, `mac`, `read`,
  `port`, `open`, `load`, `save`, `tab`, `path`, `place`, `round`) are whole words with an
  optional s/es/ed/ing [допущение: the plan lists stems without saying how they match].
- Fallback: the module with the most changed lines is chosen (ties by name), then the class
  with the most changed lines among its paths that the table maps [допущение: the plan says
  "class of the module"; modules are coarser than the path table]. `persistence` for
  `memory.py` needs a keyword, so it is not in the path table.
- A `ci:`/`build:` commit is class `platform-build` whether or not it is a fix.

Extensions of 2026-10-25 (maintainer, question В5 of `docs/reports/stage-1.md`):
- Old layout. Paths are normalised before the path table and before the module is computed
  (`normalise_path`, constant `LAYOUT_MAP`; first prefix wins):
  `sportorg/app/gui/` -> `sportorg/gui/`
  `sportorg/app/models/` -> `sportorg/models/`
  `sportorg/app/modules/` -> `sportorg/modules/`
  `sportorg/app/plugins/` -> `sportorg/modules/`
  `sportorg/app/controllers/` -> `sportorg/gui/`
  `sportorg/app/controller/` -> `sportorg/gui/`
  `sportorg/app/contoller/` -> `sportorg/gui/`
  `sportorg/app/view/` -> `sportorg/gui/`
  `sportorg/lib/` -> `sportorg/libs/`
  `sportorg/core/otime.py` -> `sportorg/common/otime.py`
  `sportorg/core/template.py` -> `sportorg/common/template.py`
  [допущение: mapping read off `git -C .legacy/pysport show --stat ef2a741` ("Moved from app",
  2017-11-24) for `app/gui`, `app/models`, `app/modules`, `lib`; `app/plugins`,
  `app/controllers` (also `controller`, the typo `contoller`, `view`) are earlier names and are
  mapped by the same file names, and `core/otime.py`, `core/template.py` by `git log --follow`
  of the current files]. Top-level files of the 2017 layout (`app.py`, `SportOrg.pyw`, ...)
  and the rest of `core/` are not clearly mappable and stay `other`. `commits.json` keeps the
  original path and the normalised module per file (`files`); `modules` and `lines` use
  the normalised modules.
- `sportorg/models/memory.py` by changed functions. If the keywords decide nothing and the path fallback gives
  `other`, and the commit changed `sportorg/models/memory.py` (or its old-layout path), the headers of
  `git show --format= -U0 <sha> -- <path>` are read. A throwaway attributes file gives git a
  `def`/`class` funcname pattern, so the context is the innermost enclosing `def` or `class`.
  The names are split into words (snake_case, CamelCase), only names are used, not parameters.
  The keyword classifier runs on these words: exactly one class decides, otherwise the commit
  stays `other`.
- `class_rule` in `commits.json`: `keyword`, `memory-functions`, `path` (module fallback),
  `other`; `type` for `ci:`/`build:` and docs-only commits, which are decided before the keywords.

Issues and PRs: class from labels first, mapping `{'github_actions': 'platform-build', 'dependencies': 'platform-build'}` [допущение: only these two
labels name a class; `bug`, `feature`, `enhancement`, `question`, `python` do not], then the
keyword classifier on the title in memory (exactly one class), otherwise `unclassified`.

## Key numbers

- Commits: 1340; merges 198; non-merge 1142.
- Fix commits: 176 (15.4 % of non-merge): rule 1 56, rule 2 120.
- Product defects: 168. Fix commits excluded from them: 2 docs-only,
  6 of type ci/build.
- Fix-like subjects excluded by type (a `feat`/`docs`/... type with a fix word): 11
  (docs 1, feat 2, refactor 5, style 3).
- Class totals of product defects: calc 15, time 2, device 16, import-export 15, report-print 12, online 9, persistence 10, i18n 4, platform-build 4, ui 37, other 44.
- Product defects by deciding rule: keyword 58, memory-functions 4, path 62, other 44. All fix commits: keyword 58, memory-functions 4, path 62, other 44, type 8.
- Before this extension (same pin): product classes calc 13, time 2, device 14, import-export 15,
  report-print 12, online 9, persistence 10, i18n 4, platform-build 4, ui 35, other 50; all fix
  commits: calc 13, time 2, device 14, import-export 15, report-print 12, online 9, persistence 10,
  i18n 4, platform-build 10, ui 35, other 50, docs-only 2. Now `other` is 44
  of the product defects. The remaining `other` are top-level files of the 2017 layout,
  `.travis.yml`, tests, and `memory.py` changes whose function names name no class or several.
- Top modules by product-defect count: `other` 64, `sportorg.models` 44, `sportorg.gui` 41, `sportorg.gui.dialogs` 35, `sportorg.gui.menu` 22.
- Top modules by fix share (at least 10 non-merge commits): `sportorg.libs.sfr` 21.7 %, `sportorg.modules.backup` 17.7 %, `sportorg.modules.live` 17.3 %, `sportorg.libs.template` 16.7 %, `tests` 16.4 %.
- Stage 0 heuristic: 9 of 11 candidates are fixes under the new rule, 9
  are product defects.
- Issues 46, PRs 532. Issues by class: {'calc': 5, 'device': 5, 'i18n': 1, 'import-export': 1, 'platform-build': 3, 'report-print': 1, 'time': 1, 'unclassified': 29}. PRs by class: {'calc': 55, 'device': 28, 'i18n': 12, 'import-export': 17, 'online': 13, 'persistence': 12, 'platform-build': 58, 'report-print': 22, 'time': 12, 'ui': 21, 'unclassified': 282}.
  Merged PRs: 460. Detail by state in `issues.md`.

## Limits

- Merge commits (198) are not counted. A PR with several commits counts per commit.
- Subjects are the only text signal; bodies are not read. A `feat:` subject with a fix word is
  not a fix by the rule, and a fix with a neutral subject is missed.
- Keywords such as `time`, `result`, `read` match many unrelated subjects; two matching
  classes fall to the path table.
- Precision and recall come from the agent's sample checks of 50 commits (Phase D, main
  session): `sample-check-1.agent.md` for the classifier before the change of 2026-10-25,
  `sample-check-2.agent.md` for the current one.
- Issues and PRs are a snapshot from the cache; the issues API gives `merged_at` only inside
  `pull_request`. Cache SHA-256 values are in the header of every `.md`.
- No author, login or e-mail is read into any output; subjects and titles are used in memory
  only.

## Open questions (for the maintainer, not decided here)

1. Is a `fix:` commit that touches only `tests/` a defect fix? Counted as a fix by the rule,
   shown under module `tests`.
2. Should `ci`/`build` fixes and product fixes whose class falls to `platform-build` by paths be
   reported together? They are separate here.
3. Squash commits that bundle features and fixes under one `feat:` subject are outside the rule.
