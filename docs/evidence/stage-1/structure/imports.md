# Import graph

Legacy pin: pysport@b548c35. Produced by `scripts/archaeology/structure.py` (command in `commands.txt`). Own edges: `ast` imports of every tracked `sportorg/**.py`, relative imports resolved, `from m import x` counted as an edge to `m.x` when that is a module. Full edge list (file:line, local flag) in `imports.json`.

| measure | value |
|---|---|
| modules (`sportorg/**.py`) | 177 |
| import statements resolved to an internal module | 613 |
| ...of them module level / function-local | 606 / 7 |
| distinct module pairs, own extractor | 603 |
| distinct module pairs, grimp | 588 |
| in both | 588 |
| only own | 15 |
| only grimp | 0 |

## Top 20 by fan-in

| module | layer | fan-in | fan-out |
|---|---|---|---|
| `sportorg.models.memory` | domain | 71 | 4 |
| `sportorg.language` | foundation | 60 | 1 |
| `sportorg.config` | foundation | 48 | 1 |
| `sportorg.gui.global_access` | ui | 48 | 1 |
| `sportorg.gui.utils.custom_controls` | ui | 29 | 3 |
| `sportorg.settings` | foundation | 29 | 4 |
| `sportorg.common.otime` | foundation | 27 | 0 |
| `sportorg.utils.time` | foundation | 23 | 1 |
| `sportorg.models.constant` | domain | 15 | 3 |
| `sportorg.models.result.result_tools` | domain | 15 | 6 |
| `sportorg.common.singleton` | foundation | 13 | 0 |
| `sportorg.modules.teamwork.teamwork` | application | 10 | 7 |
| `sportorg.models.result.result_calculation` | domain | 8 | 4 |
| `sportorg.modules.live.live` | application | 7 | 2 |
| `sportorg.gui.dialogs.file_dialog` | ui | 6 | 1 |
| `sportorg.gui.tabs.memory_model` | ui | 6 | 6 |
| `sportorg.gui.tabs.table` | ui | 5 | 0 |
| `sportorg.models.start.start_preparation` | domain | 5 | 3 |
| `sportorg.modules.sportident.backup` | application | 5 | 3 |
| `sportorg.modules.teamwork.crypto` | application | 5 | 0 |

## Top 20 by fan-out

| module | layer | fan-in | fan-out |
|---|---|---|---|
| `sportorg.gui.menu.actions` | ui | 1 | 66 |
| `sportorg.gui.main_window` | ui | 1 | 38 |
| `sportorg.gui.dialogs.result_edit` | ui | 1 | 13 |
| `sportorg.gui.dialogs.settings` | ui | 1 | 11 |
| `sportorg.gui.dialogs.report_dialog` | ui | 1 | 10 |
| `sportorg.gui.dialogs.group_edit` | ui | 2 | 9 |
| `sportorg.gui.dialogs.not_start_dialog` | ui | 1 | 9 |
| `sportorg.gui.dialogs.person_edit` | ui | 4 | 9 |
| `sportorg.gui.main` | ui | 0 | 9 |
| `sportorg.gui.dialogs.print_properties` | ui | 1 | 8 |
| `sportorg.gui.dialogs.timekeeping_properties` | ui | 1 | 8 |
| `sportorg.gui.tabs.results` | ui | 1 | 8 |
| `sportorg.gui.dialogs.import_persons_table_dialog` | ui | 1 | 7 |
| `sportorg.gui.dialogs.merge_results` | ui | 1 | 7 |
| `sportorg.gui.dialogs.organization_edit` | ui | 2 | 7 |
| `sportorg.gui.dialogs.start_handicap_dialog` | ui | 1 | 7 |
| `sportorg.gui.dialogs.start_preparation` | ui | 1 | 7 |
| `sportorg.modules.printing.model` | application | 1 | 7 |
| `sportorg.modules.teamwork.teamwork` | application | 10 | 7 |
| `sportorg.gui.dialogs.course_edit` | ui | 2 | 6 |

## Edges only in the own extractor

| importer | imported | [код] |
|---|---|---|
| `sportorg.gui.menu.actions` | `sportorg.modules.recovery.recovery_orgeo_finish_csv` | [код: pysport@b548c35 sportorg/gui/menu/actions.py:72] |
| `sportorg.gui.menu.actions` | `sportorg.modules.recovery.recovery_si_master_csv` | [код: pysport@b548c35 sportorg/gui/menu/actions.py:72] |
| `sportorg.gui.menu.actions` | `sportorg.modules.recovery.recovery_sportorg_html` | [код: pysport@b548c35 sportorg/gui/menu/actions.py:72] |
| `sportorg.gui.menu.actions` | `sportorg.modules.recovery.recovery_sportorg_si_log` | [код: pysport@b548c35 sportorg/gui/menu/actions.py:72] |
| `sportorg.modules.recovery.recovery_orgeo_finish_csv` | `sportorg.models.memory` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:18] |
| `sportorg.modules.recovery.recovery_orgeo_finish_csv` | `sportorg.utils.time` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:27] |
| `sportorg.modules.recovery.recovery_si_master_csv` | `sportorg.common.otime` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:23] |
| `sportorg.modules.recovery.recovery_si_master_csv` | `sportorg.models.memory` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:24] |
| `sportorg.modules.recovery.recovery_si_master_csv` | `sportorg.modules.sportident.fix_time_sicard_5` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:25] |
| `sportorg.modules.recovery.recovery_si_master_csv` | `sportorg.utils.time` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:26] |
| `sportorg.modules.recovery.recovery_sportorg_html` | `sportorg.utils.text` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:15] |
| `sportorg.modules.recovery.recovery_sportorg_si_log` | `sportorg.common.otime` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:32] |
| `sportorg.modules.recovery.recovery_sportorg_si_log` | `sportorg.models.memory` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:33] |
| `sportorg.modules.recovery.recovery_sportorg_si_log` | `sportorg.modules.sportident.fix_time_sicard_5` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:34] |
| `sportorg.modules.recovery.recovery_sportorg_si_log` | `sportorg.utils.time` | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:35] |

## Edges only in grimp

| importer | imported |
|---|---|

## SyntaxWarnings (1)

| message | [код] |
|---|---|
| `` "\`" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\`"? A raw string is also an option. `` | [код: pysport@b548c35 sportorg/gui/dialogs/about.py:747] |

## Files that `ast` cannot parse (0)

| file | reason |
|---|---|
