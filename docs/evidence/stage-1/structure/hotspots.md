# Hotspots

Legacy pin: pysport@b548c35. Produced by `scripts/archaeology/structure.py` (command in `commands.txt`). score = non-merge commits touching the file x total cyclomatic complexity (ruff C901, one value per function and method); SLOC = lines with a token other than a comment. The `[код]` tag points at the most complex function of the file.

Spearman correlation of non-merge commits and total complexity: 0.6433 over all 220 `.py` files, 0.4764 over the 176 files that contain functions.

Top 30 of 220 files (all in the JSON):

| rank | file | commits | total CC | max CC (function) | SLOC | score | [код] |
|---|---|---|---|---|---|---|---|
| 1 | `sportorg/models/memory.py` | 218 | 666 | 29 (`check`) | 2420 | 145188 | [код: pysport@b548c35 sportorg/models/memory.py:1109] |
| 2 | `sportorg/gui/main_window.py` | 133 | 240 | 27 (`_delete_object`) | 1023 | 31920 | [код: pysport@b548c35 sportorg/gui/main_window.py:1050] |
| 3 | `sportorg/gui/menu/actions.py` | 127 | 174 | 12 (`execute`) | 829 | 22098 | [код: pysport@b548c35 sportorg/gui/menu/actions.py:860] |
| 4 | `sportorg/models/result/result_calculation.py` | 66 | 109 | 23 (`set_rank`) | 436 | 7194 | [код: pysport@b548c35 sportorg/models/result/result_calculation.py:253] |
| 5 | `sportorg/gui/tabs/memory_model.py` | 62 | 116 | 12 (`apply_search`) | 580 | 7192 | [код: pysport@b548c35 sportorg/gui/tabs/memory_model.py:173] |
| 6 | `sportorg/models/start/start_preparation.py` | 39 | 172 | 16 (`process_array_impl`) | 668 | 6708 | [код: pysport@b548c35 sportorg/models/start/start_preparation.py:427] |
| 7 | `sportorg/models/result/result_checker.py` | 62 | 100 | 12 (`calculate_scores_ardf`) | 482 | 6200 | [код: pysport@b548c35 sportorg/models/result/result_checker.py:529] |
| 8 | `sportorg/gui/dialogs/timekeeping_properties.py` | 62 | 89 | 33 (`set_values_from_model`) | 755 | 5518 | [код: pysport@b548c35 sportorg/gui/dialogs/timekeeping_properties.py:525] |
| 9 | `sportorg/modules/live/orgeo.py` | 46 | 79 | 19 (`_get_person_obj`) | 332 | 3634 | [код: pysport@b548c35 sportorg/modules/live/orgeo.py:100] |
| 10 | `sportorg/gui/dialogs/settings.py` | 52 | 65 | 12 (`__init__`) | 386 | 3380 | [код: pysport@b548c35 sportorg/gui/dialogs/settings.py:242] |
| 11 | `sportorg/models/result/split_calculation.py` | 63 | 53 | 8 (`generate`) | 195 | 3339 | [код: pysport@b548c35 sportorg/models/result/split_calculation.py:38] |
| 12 | `sportorg/gui/dialogs/text_io.py` | 33 | 101 | 33 (`set_property`) | 377 | 3333 | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:370] |
| 13 | `sportorg/modules/sportident/sireader.py` | 47 | 58 | 13 (`run`) | 245 | 2726 | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:50] |
| 14 | `sportorg/libs/winorient/wdb.py` | 18 | 149 | 18 (`parse_bytes`) | 1050 | 2682 | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:950] |
| 15 | `sportorg/modules/sportident/result_generation.py` | 39 | 66 | 8 (`_process_missed_finish`) | 219 | 2574 | [код: pysport@b548c35 sportorg/modules/sportident/result_generation.py:43] |
| 16 | `sportorg/gui/dialogs/result_edit.py` | 28 | 84 | 29 (`apply_changes_impl`) | 360 | 2352 | [код: pysport@b548c35 sportorg/gui/dialogs/result_edit.py:275] |
| 17 | `sportorg/modules/iof/iof_xml.py` | 32 | 73 | 17 (`import_from_result_list`) | 286 | 2336 | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:251] |
| 18 | `sportorg/modules/winorient/wdb.py` | 37 | 63 | 34 (`export`) | 271 | 2331 | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:194] |
| 19 | `sportorg/libs/iof/parser.py` | 19 | 108 | 27 (`entry_list`) | 581 | 2052 | [код: pysport@b548c35 sportorg/libs/iof/parser.py:139] |
| 20 | `sportorg/gui/dialogs/report_dialog.py` | 50 | 40 | 25 (`apply_changes_impl`) | 249 | 2000 | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:125] |
| 21 | `sportorg/libs/sportiduino/sportiduino.py` | 13 | 142 | 13 (`_read_response`) | 686 | 1846 | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:196] |
| 22 | `sportorg/modules/teamwork/server.py` | 24 | 74 | 9 (`_process_packet`) | 416 | 1776 | [код: pysport@b548c35 sportorg/modules/teamwork/server.py:66] |
| 23 | `sportorg/models/constant.py` | 25 | 68 | 5 (`set_from_text`) | 213 | 1700 | [код: pysport@b548c35 sportorg/models/constant.py:212] |
| 24 | `sportorg/gui/main.py` | 65 | 25 | 3 (`run`) | 133 | 1625 | [код: pysport@b548c35 sportorg/gui/main.py:39] |
| 25 | `sportorg/libs/sfr/sfrreader.py` | 16 | 80 | 12 (`_send_command`) | 345 | 1280 | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:117] |
| 26 | `sportorg/models/result/score_calculation.py` | 30 | 41 | 12 (`calculate_scores_result`) | 116 | 1230 | [код: pysport@b548c35 sportorg/models/result/score_calculation.py:37] |
| 27 | `sportorg/libs/iof/iof.py` | 11 | 104 | 7 (`indent`) | 454 | 1144 | [код: pysport@b548c35 sportorg/libs/iof/iof.py:6] |
| 28 | `sportorg/gui/menu/menu.py` | 80 | 14 | 8 (`filter_menu_items`) | 544 | 1120 | [код: pysport@b548c35 sportorg/gui/menu/menu.py:20] |
| 29 | `sportorg/gui/dialogs/group_edit.py` | 46 | 24 | 3 (`on_name_changed`) | 189 | 1104 | [код: pysport@b548c35 sportorg/gui/dialogs/group_edit.py:148] |
| 30 | `sportorg/modules/printing/printout_split.py` | 21 | 50 | 34 (`print_split_normal`) | 350 | 1050 | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:144] |
