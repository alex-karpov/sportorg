# Structure of the legacy code (TASK-7 criterion 2: hotspots, import graph, layer violations, dead code)

What: static structure of `pysport@b548c35`, produced by `scripts/archaeology/structure.py` (command in `commands.txt`). Legacy is read through `git show` at the pin and through static tools with their caches off; it is not run or imported. `scripts.legacy verify` and `assert_tree_clean` pass after the run.

Files:
- `hotspots.{json,md}`: every tracked `.py` file (220), top 30 in the md.
- `imports.{json,md}`: own import edges with `file:line` and the local flag, per-module fan-in/fan-out, grimp cross-check, `SyntaxWarning`s.
- `violations.{json,md}`: V1, V2, V3 with `file:line`, plus the import-linter result.
- `dead-code.{json,md}`: all vulture findings with the string-dispatch flags.
- `rust.{json,md}`: tracked `*.rs`, `Cargo.toml`, `Cargo.lock`.
- `summary.{json,md}`: the key numbers below, as emitted by the script.

## Definitions

- **Commits**: non-merge commits reachable from the pin that touch the path (`git log --no-renames`, so a renamed file has two histories).
- **Complexity**: ruff C901 with `max-complexity=0`, one value per function or method (2333 functions; module-level code and classes are not counted; a nested function is counted on its own and inside its parent, as ruff does).
- **SLOC**: lines that carry at least one token other than a comment or a line break (`tokenize`); docstring lines count.
- **Score** = commits x total complexity. Ranking: score, then commits, then path. A file without functions scores 0.
- **Edge**: an `ast` import statement resolved to an internal module (`from m import x` gives `m.x` when that is a module, else `m`); relative imports are resolved; self-edges dropped. `local` = inside a function body. Only `sportorg/**.py` is in the graph (177 modules).
- **Layers**: `common.layer_of` (the model approved on 2026-10-25). Ranks: 5 entry, 4 ui, 3 application, 2 domain, 1 foundation, 0 vendored; `sportorg.data` is outside the model.
- **V1**: an edge from rank r to rank > r (both inside the model). **V2**: a module of `sportorg.libs.<a>` imports any `sportorg.*` outside `sportorg.libs.<a>`. **V3**: a module of rank 0-2 imports a GUI or I/O library from the list below. One edge can be V1 and V2 at once.
- **V3 library list** (explicit in `IO_LIBS` in the script, repeated in `violations.json`): `PySide6`, `PySide2`, `PyQt5`, `PyQt6` (Qt GUI toolkits); `serial` (COM ports), `pywinusb` (USB HID readers), `pyImpinj` (Impinj RFID), `sportident` (SPORTident reader library, serial); `requests`, `aiohttp`, `socket` (network); `win32*`, `pywintypes`, `winreg`, `psutil`, `webbrowser` (OS APIs); `playsound3` (audio). A module name matches by its root (`serial.tools.list_ports` matches `serial`).
- **name_in_string** (dead code): the vulture name is a word (`\w+`) of some string literal, docstrings excluded, in any tracked legacy `.py` file. **name_is_string**: the name is a whole string literal. Both are False for the two nameless kinds (`unreachable code`, `redundant if-condition`). They are hints for string dispatch (menu `"action": "NewAction"`), not verdicts.
- **import-linter**: a `layers` contract in a temporary config in `$TMPDIR` (never in the repository); layers highest first: `startup`, `gui`, `modules : rust_example`, `models`, `common : utils : config : settings : language : paths`, `libs` (a colon means siblings that may import each other).

## Key numbers

Hotspots (top 10 by score; file, commits, total CC, SLOC):

| # | File | Commits | Total CC | SLOC |
|---|---|---|---|---|
| 1 | `sportorg/models/memory.py` | 218 | 666 | 2420 |
| 2 | `sportorg/gui/main_window.py` | 133 | 240 | 1023 |
| 3 | `sportorg/gui/menu/actions.py` | 127 | 174 | 829 |
| 4 | `sportorg/models/result/result_calculation.py` | 66 | 109 | 436 |
| 5 | `sportorg/gui/tabs/memory_model.py` | 62 | 116 | 580 |
| 6 | `sportorg/models/start/start_preparation.py` | 39 | 172 | 668 |
| 7 | `sportorg/models/result/result_checker.py` | 62 | 100 | 482 |
| 8 | `sportorg/gui/dialogs/timekeeping_properties.py` | 62 | 89 | 755 |
| 9 | `sportorg/modules/live/orgeo.py` | 46 | 79 | 332 |
| 10 | `sportorg/gui/dialogs/settings.py` | 52 | 65 | 386 |

- 220 `.py` files, 176 with functions, 33086 SLOC, total complexity 6108.
- Spearman(commits, total complexity) = 0.6433 over all 220 files, 0.4764 over the 176 files with functions.

Import graph:
- 177 modules, 613 internal import statements (606 module level, 7 local).
- Distinct module pairs: own 603, grimp 588, in both 588, only own 15, only grimp 0.
- The 15 own-only edges are all the namespace package `sportorg.modules.recovery` (it has no `__init__.py`; grimp does not see its 4 modules): 4 edges into it from `sportorg/gui/menu/actions.py:72` and 11 out of it.
- Most imported: `sportorg.models.memory` (fan-in 71), `sportorg.language` (60), `sportorg.config` (48), `sportorg.gui.global_access` (48). Largest fan-out: `sportorg.gui.menu.actions` (66), `sportorg.gui.main_window` (38).
- 1 `SyntaxWarning` (invalid escape sequence) at `sportorg/gui/dialogs/about.py:747`. 0 files fail to parse.

Layer violations (module level / local):

| Kind | Module level | Local |
|---|---|---|
| V1 | 16 | 1 |
| V2 | 13 | 0 |
| V3 | 12 | 0 |

- V1 by layer pair: vendored to foundation 8, vendored to domain 5, application to ui 3, foundation to application 1 (local: `sportorg/settings.py:257` into `sportorg.modules.configs.configs`). Without vendored sources V1 is 3 module level + 1 local. All 13 V2 edges are also V1 (a vendored lib imports a higher layer).
- import-linter `layers`: exit 1 (broken), analysed 173 files and 588 dependencies, 16 entries, all direct (0 indirect chains). Its 16 module pairs equal the 16 distinct V1 pairs (own V1 has 17 statements because `sportorg/libs/sfr/sfrximporter.py:6` and `:7` import the same module; the contract lists module pairs, not statements). The contract also follows indirect chains and groups by layer pair; in this graph no indirect chain exists, so the counts agree. It does not see the `recovery` namespace package (173 files against 177 modules), which has no V1 edge, and it does not report V2 or V3.
- V3: 12 statements in 8 modules: Qt in `sportorg/utils/time.py` (PySide6 and the PySide2 fallback) and `sportorg/libs/winorient/wdb_online_sender_dialog.py`, `serial` or `pywinusb` in 4 vendored device libs (huichang, sfr, sportiduino, srpid), `requests` in `sportorg/libs/telegram/telegram.py`, `playsound3` in `sportorg/common/audio.py`.

Dead code (vulture `--min-confidence 0`): 282 findings (278 at 60 %, 4 at 100 %): unused class 92, method 81, variable 50, attribute 41, function 12, property 3, redundant if-condition 2, unreachable code 1. `name_in_string` is set on 109 findings (unused class 86, variable 21, property 2); `name_is_string` on 108. Nothing is judged here: the main session samples 30 by hand.

Rust: 3 `.rs` files, 336 lines (`crates/sportorg-core` 327, `crates/sportorg-rust-example` 9); `Cargo.toml` and `Cargo.lock` 171 lines (the two workspace-root files 146 of them). Non-merge commits: `sportorg-core` 2, `sportorg-rust-example` 1, workspace root 2.

## Limits

- The graph is static: `importlib`, `__import__`, string dispatch and `TYPE_CHECKING`-only imports are not distinguished; `try/except ImportError` fallbacks (PySide6 / PySide2) are counted as two imports.
- V3 matches module roots only. `sportorg/libs/winorient/wdb_online_sender.py:6` imports `requests` as `from pip._vendor import requests`, which the list does not match. The third-party roots imported from ranks 0-2 and not in the list are in `violations.json` (`core_third_party_not_listed`): `chardet`, `dateutil`, `importlib_resources`, `jinja2`, `lxml`, `pip`, `polib`, `six`, `sportorg_core`.
- Commit counts follow current paths (`--no-renames`); the hotspot score is a ranking, not a defect count.
- Complexity counts functions only; large data modules and module-level code score low.
- Tests, benches and other non-package `.py` files are in the hotspot table but not in the graph or the violations.

## Open questions (not decided here)

1. Vendored libs (`sportorg/libs/**`) import the application's own `common`, `models`, `utils`, `language` (13 edges, all V1 and V2). Are they vendored third-party code or project code under the `libs` name? This decides whether V1/V2 are defects or a layer-model gap.
2. `sportorg.data` (a package with `configs/*.txt` data) is outside the layer model. Which rank does it belong to?
3. `sportorg_core` (the Rust extension) is imported from `sportorg/common/otime.py:6` (core). The model does not name it: foundation or adapter?
4. `from pip._vendor import requests` (`sportorg/libs/winorient/wdb_online_sender.py:6`): a dependency on pip internals. Local practice or bug; not classified here.
5. The namespace package `sportorg.modules.recovery` has no `__init__.py`, so grimp and import-linter miss it. Intentional or an omission; relevant for any tool that reads the package structure.

Checks:
- `verify_locs`: 1067 tags, 0 problems (seed 1, 10-tag sample compared by eye with the source lines the command prints).
- Two runs produce byte-identical files (`cmp`).
