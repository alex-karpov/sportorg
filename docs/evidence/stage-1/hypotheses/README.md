# Hypotheses of the brief (TASK-7 criterion 6)

What: verdicts on the six hypotheses of `docs/brief.md` §«Этап 1» on `pysport@b548c35`.
- `hypotheses.json`: per hypothesis the claim, the definition fixed before the run, the numbers, the verdict and every `[код]` tag.
- `hypotheses.md`: the table «гипотеза | число | вердикт | источник».

Verdict rule (`scripts/archaeology/hypotheses.py`):
- `confirmed`: every part of the claim holds;
- `refuted`: no part holds;
- `partly`: some parts hold.

H2 has a numeric rule of its own: exact match, ±20 %, otherwise refuted. It is applied to `sportorg/` [мейнтейнер: 2026-10-25].

| H | Verdict | Key numbers |
|---|---|---|
| H1 memory.py | confirmed | 2910 physical lines; 218 non-merge commits, rank 1 of 324 tracked files. By churn it ranks 2nd, after `sportorg/libs/iof/data/IOF.xsd` |
| H2 race() in 62 files | confirmed for `sportorg/` (refuted by the definition fixed before the run: all files) | 78 tracked files use it: 62 in `sportorg/`, 16 outside (tests, benches). 77 files call it |
| H3 GUI outside gui | confirmed, with a caveat | 12 modules outside `sportorg.gui`, 29 import edges to the GUI or Qt. 8 of the modules (18 edges) import only `QtCore` (threads, signals, dates); 4 modules (11 edges) import the UI proper (`sportorg.gui`, `QtWidgets`, `QtGui`, `QtPrintSupport`), 3 of them `sportorg.gui` (3 edges). In result generation: `sportorg.modules.printing` |
| H4 punch system in result classes | confirmed | 7 Result subclasses, each bound to one `SystemType`. 7 `is_<system>` helpers. 7 branches in 3 files outside memory.py |
| H5 Qualification in domain | confirmed (layer only) | defined in `sportorg.models.memory` (domain), 10 members. The EVSK match is not judged (needs the rules document) |
| H6 Windows 7 pins | partly | `requires-python >=3.8.1`, 4 markers for Python 3.8. 60 files import PySide2 as a fallback. `uv.lock` has no orjson/cryptography at or below the Win7 limits of `CONTRIBUTING.md` (orjson 3.10.15/3.11.3, cryptography 46.0.6) |

Observations for the report (classified there, raised to the maintainer):
1. **H2 scope.** The claimed 62 equals the count in `sportorg/` exactly. The definition fixed before the run counted all tracked files (78, refuted). The maintainer set the scope to `sportorg/` after the result was known [мейнтейнер: 2026-10-25] (report question 1). Both numbers stay in `hypotheses.json`, and the brief names the scope.
2. **H3: the module named `result_generation`.** `sportorg/modules/sportident/result_generation.py:7` imports the GUI layer. The predefined "result generation" set does not include it, so the verdict does not depend on it. `sportorg/utils/time.py` (foundation layer) imports Qt.
3. **H5: a second definition.** `tests/test_sfrxexporter.py:29` defines another `class Qualification`. The vendored `sportorg/libs/sfr/sfrximporter.py:8` references the name. After `libs` was split by role [мейнтейнер: 2026-10-25] it is an I/O codec of rank 3, so the reference is not a layer violation.
4. **H6: where the Windows 7 build lives.** It is a manual procedure in `CONTRIBUTING.md:93-125` (pins applied by hand before syncing), not a state of `pyproject.toml`/`uv.lock`.

Checks:
- `verify_locs`: 197 tags, 0 problems. The 10-tag sample (seed 7) was compared by eye with the source lines, which the command prints.
- A rerun is byte-identical.
- `scripts.legacy verify` ok.
