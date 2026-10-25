# Layer violations

Legacy pin: pysport@b548c35. Produced by `scripts/archaeology/structure.py` (command in `commands.txt`). Layer model from the plan (approved 2026-10-25), ranks from `common.layer_of`.

| kind | module level | function-local |
|---|---|---|
| V1 | 3 | 1 |
| V3 | 3 | 0 |

V1 = upward edge (rank r to rank > r), V3 = ranks 0-2 importing a GUI or I/O library (list in `violations.json`, `libraries`). `sportorg/libs` is split by role (`common.LIBS_APPLICATION`, `common.LIBS_UI`) and V2 is dropped [мейнтейнер: 2026-10-25] (report question 3).

## import-linter `layers` contract

```json
{
 "both": 4,
 "dependencies_analysed": 588,
 "entries": 4,
 "exit": 1,
 "files_analysed": 173,
 "linter_direct_pairs": 4,
 "linter_indirect_entries": 0,
 "only_linter": [],
 "only_v1": [],
 "v1_pairs": 4
}
```

## V1 (4)

| source | layer | target | layer | local | [код] |
|---|---|---|---|---|---|
| `sportorg.modules.printing.printing` | application | `sportorg.gui.global_access` | ui | no | [код: pysport@b548c35 sportorg/modules/printing/printing.py:21] |
| `sportorg.modules.sportident.result_generation` | application | `sportorg.gui.dialogs.bib_dialog` | ui | no | [код: pysport@b548c35 sportorg/modules/sportident/result_generation.py:7] |
| `sportorg.modules.winorient.wdb_number_setter` | application | `sportorg.gui.dialogs.file_dialog` | ui | no | [код: pysport@b548c35 sportorg/modules/winorient/wdb_number_setter.py:6] |
| `sportorg.settings` | foundation | `sportorg.modules.configs.configs` | application | yes | [код: pysport@b548c35 sportorg/settings.py:257] |

## V3 (3)

| source | layer | target | layer | local | [код] |
|---|---|---|---|---|---|
| `sportorg.common.audio` | foundation | `playsound3` | external audio | no | [код: pysport@b548c35 sportorg/common/audio.py:7] |
| `sportorg.utils.time` | foundation | `PySide2.QtCore` | external gui | no | [код: pysport@b548c35 sportorg/utils/time.py:5] |
| `sportorg.utils.time` | foundation | `PySide6.QtCore` | external gui | no | [код: pysport@b548c35 sportorg/utils/time.py:2] |
