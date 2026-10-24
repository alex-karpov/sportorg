# Layer violations

Legacy pin: pysport@b548c35. Produced by `scripts/archaeology/structure.py` (command in `commands.txt`). Layer model from the plan (approved 2026-10-25), ranks from `common.layer_of`.

| kind | module level | function-local |
|---|---|---|
| V1 | 16 | 1 |
| V2 | 13 | 0 |
| V3 | 12 | 0 |

V1 = upward edge (rank r to rank > r), V2 = `sportorg.libs.<a>` importing another `sportorg.*`, V3 = ranks 0-2 importing a GUI or I/O library (list in `violations.json`, `libraries`). One edge can be both V1 and V2.

## import-linter `layers` contract

```json
{
 "both": 16,
 "dependencies_analysed": 588,
 "entries": 16,
 "exit": 1,
 "files_analysed": 173,
 "linter_direct_pairs": 16,
 "linter_indirect_entries": 0,
 "only_linter": [],
 "only_v1": [],
 "v1_pairs": 16
}
```

## V1 (17)

| source | layer | target | layer | local | [код] |
|---|---|---|---|---|---|
| `sportorg.libs.huichang.huichang` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:25] |
| `sportorg.libs.huichang.huichang` | vendored | `sportorg.language` | foundation | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:24] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:7] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:8] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.models.result.result_calculation` | domain | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:9] |
| `sportorg.libs.ocad.ocad` | vendored | `sportorg.utils.text` | foundation | no | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:4] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.language` | foundation | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:4] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:6] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:7] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.utils.time` | foundation | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:17] |
| `sportorg.libs.sfr.sfrxparser` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:3] |
| `sportorg.libs.winorient.wdb_online_sender` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:8] |
| `sportorg.libs.winorient.wdb_online_sender` | vendored | `sportorg.utils.time` | foundation | no | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:10] |
| `sportorg.modules.printing.printing` | application | `sportorg.gui.global_access` | ui | no | [код: pysport@b548c35 sportorg/modules/printing/printing.py:21] |
| `sportorg.modules.sportident.result_generation` | application | `sportorg.gui.dialogs.bib_dialog` | ui | no | [код: pysport@b548c35 sportorg/modules/sportident/result_generation.py:7] |
| `sportorg.modules.winorient.wdb_number_setter` | application | `sportorg.gui.dialogs.file_dialog` | ui | no | [код: pysport@b548c35 sportorg/modules/winorient/wdb_number_setter.py:6] |
| `sportorg.settings` | foundation | `sportorg.modules.configs.configs` | application | yes | [код: pysport@b548c35 sportorg/settings.py:257] |

## V2 (13)

| source | layer | target | layer | local | [код] |
|---|---|---|---|---|---|
| `sportorg.libs.huichang.huichang` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:25] |
| `sportorg.libs.huichang.huichang` | vendored | `sportorg.language` | foundation | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:24] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:7] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:8] |
| `sportorg.libs.iof.generator` | vendored | `sportorg.models.result.result_calculation` | domain | no | [код: pysport@b548c35 sportorg/libs/iof/generator.py:9] |
| `sportorg.libs.ocad.ocad` | vendored | `sportorg.utils.text` | foundation | no | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:4] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.language` | foundation | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:4] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:6] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:7] |
| `sportorg.libs.sfr.sfrximporter` | vendored | `sportorg.utils.time` | foundation | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:17] |
| `sportorg.libs.sfr.sfrxparser` | vendored | `sportorg.models.memory` | domain | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:3] |
| `sportorg.libs.winorient.wdb_online_sender` | vendored | `sportorg.common.otime` | foundation | no | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:8] |
| `sportorg.libs.winorient.wdb_online_sender` | vendored | `sportorg.utils.time` | foundation | no | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:10] |

## V3 (12)

| source | layer | target | layer | local | [код] |
|---|---|---|---|---|---|
| `sportorg.common.audio` | foundation | `playsound3` | external audio | no | [код: pysport@b548c35 sportorg/common/audio.py:7] |
| `sportorg.libs.huichang.huichang` | vendored | `serial` | external device | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:21] |
| `sportorg.libs.huichang.huichang` | vendored | `serial.serialutil` | external device | no | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:22] |
| `sportorg.libs.sfr.sfrreader` | vendored | `pywinusb.hid` | external device | no | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:31] |
| `sportorg.libs.sportiduino.sportiduino` | vendored | `serial` | external device | no | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:29] |
| `sportorg.libs.sportiduino.sportiduino` | vendored | `serial.serialutil` | external device | no | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:30] |
| `sportorg.libs.srpid.srpid` | vendored | `serial` | external device | no | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:22] |
| `sportorg.libs.srpid.srpid` | vendored | `serial.serialutil` | external device | no | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:23] |
| `sportorg.libs.telegram.telegram` | vendored | `requests` | external network | no | [код: pysport@b548c35 sportorg/libs/telegram/telegram.py:1] |
| `sportorg.libs.winorient.wdb_online_sender_dialog` | vendored | `PySide6.QtWidgets` | external gui | no | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:4] |
| `sportorg.utils.time` | foundation | `PySide2.QtCore` | external gui | no | [код: pysport@b548c35 sportorg/utils/time.py:5] |
| `sportorg.utils.time` | foundation | `PySide6.QtCore` | external gui | no | [код: pysport@b548c35 sportorg/utils/time.py:2] |
