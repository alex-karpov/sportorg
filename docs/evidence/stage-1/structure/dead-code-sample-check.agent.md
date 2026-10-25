# Dead code: sample check of 30 vulture findings (agent judgement)

The labels in this file are the judgement of the main session's agent (Claude Code, Opus 5.5) on 2026-10-25, not script output; no human reviewed them. The sample itself was
chosen by a script:

```
uv run python -m scripts.archaeology.sample --json docs/evidence/stage-1/structure/dead-code.json \
    --key findings --n 30 --seed 20261025 --fields kind,name,confidence,name_in_string,tag
```

## Criteria
The agent checked each finding against both pinned repositories (`git grep -n -w <name>` in pysport and in
templates, then reading the context):
- **TP**: truly unused. Nothing refers to the name: no call, no read, no string, no name-built
  `getattr`, no use in templates. Unreachable code counts as TP when every branch before it returns.
- **FP-string**: the name is used as a string. Menu actions are named in `menu.py`/`toolbar.py`, e.g.
  `"action": "OpenAction"` [код: pysport@b548c35 sportorg/gui/menu/menu.py:87].
- **FP-convention**: the dialog base class calls the method by a name it builds, `getattr(self,
  f"convert_{id}")`, `f"on_{id}_changed"`, `f"on_{id}_button_clicked"` [код: pysport@b548c35
  sportorg/gui/dialogs/dialog.py:172-233], or `f"parse_{id}"` [код: pysport@b548c35
  sportorg/gui/dialogs/dialog.py:343], and a form field with that `id` exists in the dialog.
- **FP-enum**: a member of an `Enum` that is reached through a value lookup, e.g. `ResultStatus(int(data["status"]))`
  [код: pysport@b548c35 sportorg/models/memory.py:651].
- **tests-only**: product code never reads or calls it; only `tests/` does. Not dead to the test suite,
  dead to the product.

## Sample
| # | kind | name | name_in_string | tag | label | why |
|---|---|---|---|---|---|---|
| 1 | unused method | convert_race_type | False | [код: pysport@b548c35 sportorg/gui/dialogs/group_edit.py:133] | FP-convention | field `id="race_type"` [код: pysport@b548c35 sportorg/gui/dialogs/group_edit.py:105] |
| 2 | unused method | on_name_changed | False | [код: pysport@b548c35 sportorg/gui/dialogs/organization_edit.py:49] | FP-convention | field `id="name"` [код: pysport@b548c35 sportorg/gui/dialogs/organization_edit.py:22] |
| 3 | unused method | parse_group | False | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:194] | FP-convention | field `id="group"` [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:78] |
| 4 | unused method | parse_qual | False | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:205] | FP-convention | field `id="qual"` [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:110] |
| 5 | unused method | on_bib_button_clicked | False | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:292] | FP-convention | field `id="bib"` [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:117] |
| 6 | unused method | load_from_file | False | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:158] | TP | nothing refers to it; the dialog's signals connect other slots [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:145-185] |
| 7 | unused class | OpenAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:113] | FP-string | menu and toolbar |
| 8 | unused class | OpenRecentAction | False | [код: pysport@b548c35 sportorg/gui/menu/actions.py:126] | TP | no reference anywhere (W1 agrees) |
| 9 | unused class | EventSettingsAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:162] | FP-string | menu |
| 10 | unused class | IOFEntryListImportAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:326] | FP-string | menu |
| 11 | unused class | ToCoursesAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:514] | FP-string | menu |
| 12 | unused class | GuessCoursesAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:535] | FP-string | menu |
| 13 | unused class | TeamworkSendAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:785] | FP-string | menu |
| 14 | unused class | AssignResultByCardNumberAction | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:918] | FP-string | menu |
| 15 | unused class | ExtractPersonMiddleName | True | [код: pysport@b548c35 sportorg/gui/menu/actions.py:975] | FP-string | menu |
| 16 | unused variable | FINISHED | True | [код: pysport@b548c35 sportorg/libs/iof/iof.py:417] | TP | constant of a plain class (not an Enum). The string `"FINISHED"` in `orgeo.py` belongs to `memory.ResultStatus`, so `name_in_string` misleads here |
| 17 | unused method | reconnect | False | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:356] | TP | no caller in either repository |
| 18 | unused method | init_time_card | False | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:470] | TP | no caller |
| 19 | unreachable code | if | False | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:583] | TP | every branch of the `if/elif/else` chain before it returns |
| 20 | unused method | reconnect | False | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:181] | TP | no caller |
| 21 | unused attribute | team_filer | False | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:621] | TP | parsed from the WDB file (bytes 998–1000) and never read |
| 22 | unused variable | ONLINE_PARAM1 | False | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:18] | TP | no reference |
| 23 | unused variable | INACTIVE | True | [код: pysport@b548c35 sportorg/models/memory.py:82] | FP-enum | `ResultStatus(_TitleType)`, `_TitleType(Enum)` [код: pysport@b548c35 sportorg/models/memory.py:45] |
| 24 | unused variable | DID_NOT_ENTER | True | [код: pysport@b548c35 sportorg/models/memory.py:89] | FP-enum | same Enum |
| 25 | unused method | get_count_finished | False | [код: pysport@b548c35 sportorg/models/memory.py:336] | TP | templates read the attribute `count_finished`, never the method |
| 26 | unused attribute | has_penalty | False | [код: pysport@b548c35 sportorg/models/memory.py:1200] | tests-only | read only in `tests/test_result_checking.py` |
| 27 | unused attribute | has_penalty | False | [код: pysport@b548c35 sportorg/models/memory.py:1230] | tests-only | same |
| 28 | unused method | set_bibs | False | [код: pysport@b548c35 sportorg/models/memory.py:2724] | TP | no caller in either repository |
| 29 | unused method | get_leg_leader | False | [код: pysport@b548c35 sportorg/models/result/split_calculation.py:225] | tests-only | called only in `tests/test_split_calculation.py` |
| 30 | unused attribute | _debug | False | [код: pysport@b548c35 sportorg/modules/huichang/huichang.py:40] | TP | assigned, never read |

## Result
| Label | Count |
|---|---|
| TP | 12 |
| FP-string | 8 |
| FP-convention | 5 |
| FP-enum | 2 |
| tests-only | 3 |

- **Precision of raw vulture findings** = 12 / 30 = **40 %**. Counting tests-only as dead to the product
  gives 15 / 30 = 50 %.
- **The `name_in_string` flag of W2.**
  - 11 findings have `name_in_string = True`: all 10 FP-string/FP-enum, plus 1 TP (#16).
  - 19 findings have `name_in_string = False`: 11 TP, 5 FP-convention, 3 tests-only. Precision is 11 / 19 = **58 %**, or 14 / 19 = 74 % if tests-only counts as dead to the product.
- **Against the ADR-0007 N3 revisit condition** ("precision on the sample < 50 %"):
  - raw vulture output: 40 %, so the condition holds;
  - with the `name_in_string` filter: 58 %, so it does not.
  - Consequence for later stages: vulture findings are usable only together with `name_in_string`. The FP-convention class is still unflagged: methods the dialog base class reaches through name-built `getattr` (`convert_*`, `parse_*`, `on_*_changed`, `on_*_button_clicked`, `on_*_finished`, `on_*_clicked`).
- **Limits:** one agent labelled, no human review; with a sample of 30, every percentage is uncertain by roughly ±15 points.

## Status of `WdbOnlineSenderDialog` (outside the sample)
The maintainer asked for its status `[мейнтейнер: 2026-10-25]`. Agent judgement on facts the main
session re-checked at the pin:
- **Not part of the application.**
  - The class is created only under `if __name__ == "__main__"` [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:75-78].
  - `WdbOnlineSender` is created only by this dialog [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:62].
  - `git grep -w` finds no other reference to either name or to the module in pysport.
- **Never wired into the application.** `git log -S"WdbOnlineSenderDialog"` finds only the commit that added it [история: pysport@511c1ac].
- **vulture does not report it,** because it counts the call under `__main__` as a use. Among the dead-code findings are only the `ONLINE_*` constants of `wdb_online_sender.py` (#22 above).
- **What it is:** a standalone script (`python -m sportorg.libs.winorient.wdb_online_sender_dialog`).
  - It watches a WinOrient WDB file and sends the data to an online results service.
  - Its default URL is hard-coded to one event, with an access key [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:40].
- **Status:** dead for the application. Whether anyone runs the script cannot be known from the code. It is not ported to the new project unless someone asks for it.
- **Layer model:** placed in `ui` (`common.LIBS_UI`) [мейнтейнер: 2026-10-25].
