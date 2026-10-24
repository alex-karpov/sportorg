# os-ru hits (core first)

Produced by `scripts/archaeology/os_ru.py` on pysport@b548c35; see README.md.

## OS01 platform branches: 20 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| no | outside | code | `sys.platform` | win32 | [код: pysport@b548c35 builder.py:15] |
| no | outside | code | `sys.platform` | win32 | [код: pysport@b548c35 builder.py:123] |
| no | ui | code | `platform.system` | Linux | [код: pysport@b548c35 sportorg/gui/dialogs/file_dialog.py:28] |
| no | ui | code | `sys.platform` | win32 | [код: pysport@b548c35 sportorg/gui/tabs/persons.py:110] |
| no | ui | code | `sys.platform` | win32 | [код: pysport@b548c35 sportorg/gui/theme.py:100] |
| no | ui | code | `sys.platform` | darwin | [код: pysport@b548c35 sportorg/gui/theme.py:102] |
| no | ui | code | `sys.platform` | linux | [код: pysport@b548c35 sportorg/gui/theme.py:104] |
| no | vendored | code | `platform.system` | Windows | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:30] |
| no | vendored | code | `platform.system` | Windows | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:278] |
| no | vendored | code | `platform.system` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:279] |
| no | vendored | code | `platform.system` | Linux | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:313] |
| no | vendored | code | `platform.system` | Windows | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:320] |
| no | vendored | code | `platform.system` |  | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:324] |
| no | application | code | `os.name` | nt | [код: pysport@b548c35 sportorg/modules/plugins/manager.py:519] |
| no | application | code | `platform.system` | Windows | [код: pysport@b548c35 sportorg/modules/printing/model.py:42] |
| no | application | code | `platform.system` | Windows | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:7] |
| no | outside | code | `platform.system` | Linux | [код: pysport@b548c35 tests/test_reader.py:241] |
| no | outside | code | `platform.system` | Linux | [код: pysport@b548c35 tests/test_reader.py:289] |
| no | outside | code | `platform.system` | Linux | [код: pysport@b548c35 tests/test_reader.py:339] |
| no | outside | code | `sys.platform` | win32 | [код: pysport@b548c35 tests/test_theme.py:85] |

## OS02 OS-only modules: 6 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| no | ui | code | `winreg` |  | [код: pysport@b548c35 sportorg/gui/theme.py:110] |
| no | vendored | code | `pywinusb.hid` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:31] |
| no | application | code | `win32con` |  | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:8] |
| no | application | code | `win32print` |  | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:9] |
| no | application | code | `win32ui` |  | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:10] |
| no | outside | code | `winreg` |  | [код: pysport@b548c35 tests/test_theme.py:87] |

## OS03 OS-only calls: 1 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| no | ui | code | `os.startfile` |  | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:233] |

## OS04 OS paths and devices: 24 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| no | outside | config | `.exe` | ext | [код: pysport@b548c35 .github/workflows/release.yml:47] |
| no | outside | config | `6\ISCC` | backslash | [код: pysport@b548c35 .github/workflows/release.yml:47] |
| no | outside | config | `C:\` | drive | [код: pysport@b548c35 .github/workflows/release.yml:47] |
| no | outside | config | `t\SportOrg` | backslash | [код: pysport@b548c35 .github/workflows/release.yml:58] |
| no | outside | config | `.exe` | ext | [код: pysport@b548c35 .github/workflows/release.yml:64] |
| no | outside | config | `.exe` | ext | [код: pysport@b548c35 .github/workflows/release.yml:97] |
| no | outside | string | `.exe` | ext | [код: pysport@b548c35 builder.py:87] |
| no | outside | config | `.exe` | ext | [код: pysport@b548c35 sportorg.iss:7] |
| no | outside | config | `d\exe` | backslash | [код: pysport@b548c35 sportorg.iss:18] |
| no | outside | config | `g\data` | backslash | [код: pysport@b548c35 sportorg.iss:47] |
| no | outside | config | `g\icon` | backslash | [код: pysport@b548c35 sportorg.iss:47] |
| no | outside | config | `s\Russian` | backslash | [код: pysport@b548c35 sportorg.iss:51] |
| no | outside | comment | `.exe` | ext | [код: pysport@b548c35 sportorg.iss:60] |
| no | outside | comment | `t\vc_redist` | backslash | [код: pysport@b548c35 sportorg.iss:60] |
| no | outside | comment | `.exe` | ext | [код: pysport@b548c35 sportorg.iss:83] |
| no | outside | config | `0\VC` | backslash | [код: pysport@b548c35 sportorg.iss:97] |
| no | outside | config | `E\Microsoft` | backslash | [код: pysport@b548c35 sportorg.iss:97] |
| no | ui | string | `e\Microsoft` | backslash | [код: pysport@b548c35 sportorg/gui/theme.py:112] |
| no | ui | string | `s\CurrentVersion` | backslash | [код: pysport@b548c35 sportorg/gui/theme.py:112] |
| no | ui | string | `s\Personalize` | backslash | [код: pysport@b548c35 sportorg/gui/theme.py:112] |
| no | vendored | string | `/dev/ttyACM0` | tty | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:311] |
| no | application | docstring | `C:\` | drive | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:2] |
| no | application | docstring | `g\log` | backslash | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:2] |
| no | outside | string | `.exe` | ext | [код: pysport@b548c35 tests/test_paths.py:37] |

## OS05 dependency markers: 552 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| no | outside | config | `pywinusb` | package | [код: pysport@b548c35 pyproject.toml:20] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 pyproject.toml:30] |
| no | outside | config | `pyImpinj` | package | [код: pysport@b548c35 pyproject.toml:31] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 pyproject.toml:53] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:5] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:6] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:7] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:8] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:9] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:10] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:11] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:12] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:13] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:14] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:15] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:16] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:17] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:18] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:28] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:29] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:30] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:31] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:32] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:33] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:34] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:46] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:47] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:48] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:49] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:50] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:51] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:52] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:66] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:67] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:68] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:69] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:70] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:71] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:72] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:182] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:183] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:184] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:185] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:186] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:187] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:188] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:330] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:331] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:332] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:333] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:334] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:335] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:336] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:351] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:352] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:353] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:354] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:355] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:356] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:357] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:384] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:385] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:386] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:387] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:388] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:389] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:390] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:402] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:403] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:404] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:405] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:406] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:407] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:408] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:461] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:462] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:463] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:464] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:465] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:466] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:467] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:547] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:548] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:549] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:550] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:551] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:552] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:553] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:791] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:792] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:793] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:794] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:795] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:796] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:797] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1003] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1004] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1005] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1006] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1007] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1008] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1009] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1179] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1180] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1181] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1182] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1183] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1184] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1185] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1188] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1189] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1190] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1233] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1234] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1235] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1236] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1237] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1238] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1239] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1242] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1243] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1244] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1246] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1248] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1250] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1293] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1314] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1335] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1336] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1379] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1413] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1414] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1415] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1416] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1417] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1418] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1419] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1521] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1522] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1523] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1524] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1525] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1526] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1527] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1722] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1744] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1927] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1928] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1929] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1930] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1931] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1932] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1933] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1994] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1995] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1996] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1997] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1998] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:1999] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2000] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2125] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2126] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2127] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2128] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2129] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2130] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2131] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2236] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2237] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2238] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2239] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2240] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2241] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2242] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2403] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2404] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2405] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2406] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2407] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2408] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2409] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2462] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2463] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2464] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2465] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2466] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2467] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2468] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2530] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2531] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2532] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2533] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2534] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2535] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2536] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2625] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2626] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2627] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2628] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2629] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2630] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2631] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2767] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2768] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2769] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2770] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2771] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2772] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2773] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:2776] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2776] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2788] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2789] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2790] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2791] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2792] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2793] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2794] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:2799] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2799] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2811] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2812] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2813] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2814] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2815] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2816] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2817] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2829] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2830] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2831] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2832] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2833] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2834] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2835] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2872] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2873] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2874] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2875] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2876] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2877] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2878] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2986] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2987] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2988] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2989] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2990] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2991] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:2992] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3151] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3152] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3153] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3154] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3155] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3156] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3157] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3170] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3171] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3172] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3173] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3174] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3175] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3176] |
| no | outside | config | `pyimpinj` | package | [код: pysport@b548c35 uv.lock:3194] |
| no | outside | config | `pyImpinj` | package | [код: pysport@b548c35 uv.lock:3202] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3219] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3220] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3221] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3222] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3223] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3224] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3225] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3244] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3245] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3246] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3247] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3248] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3249] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3250] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3272] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3273] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3274] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3275] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3276] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3277] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3278] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3296] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3297] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3298] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3299] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3300] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3301] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3302] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3323] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3324] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3325] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3326] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3327] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3328] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3329] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3346] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3347] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3348] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3349] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3350] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3351] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3352] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3372] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3373] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3374] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3375] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3376] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3377] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3378] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3381] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3398] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3399] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3400] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3401] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3402] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3403] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3404] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3409] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3441] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3442] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3443] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3444] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3445] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3446] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3447] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3463] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3464] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3465] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3466] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3467] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3468] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3469] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3502] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3503] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3504] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3505] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3506] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3507] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3508] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3523] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3524] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3525] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3526] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3527] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3528] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3529] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3558] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3559] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3560] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3561] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3562] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3563] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3564] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3580] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3581] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3582] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3583] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3584] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3585] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3586] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3609] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3613] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3614] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3615] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3616] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3617] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3618] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3619] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3620] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3621] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3622] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3623] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3624] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3625] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3626] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3627] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3628] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3629] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3630] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3631] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3632] |
| no | outside | config | `pywinusb` | package | [код: pysport@b548c35 uv.lock:3636] |
| no | outside | config | `pywinusb` | package | [код: pysport@b548c35 uv.lock:3639] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3726] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3727] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3728] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3729] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3730] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3731] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3732] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3750] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3751] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3752] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3753] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3754] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3755] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3756] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3802] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3803] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3804] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3805] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3806] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3807] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3808] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3820] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3821] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3822] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3823] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3824] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3825] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3826] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3840] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3841] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3842] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3843] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3844] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3845] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3846] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3860] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3861] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3862] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3863] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3864] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3865] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:3866] |
| no | outside | config | `pywinusb` | package | [код: pysport@b548c35 uv.lock:3920] |
| no | outside | config | `pyimpinj` | package | [код: pysport@b548c35 uv.lock:3932] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3933] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3958] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3959] |
| no | outside | config | `pyimpinj` | package | [код: pysport@b548c35 uv.lock:3979] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:3982] |
| no | outside | config | `pywinusb` | package | [код: pysport@b548c35 uv.lock:3983] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:4006] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4083] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4084] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4085] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4086] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4087] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4088] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4089] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4101] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4102] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4103] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4104] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4105] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4106] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4107] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4121] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4122] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4123] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4124] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4125] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4126] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4127] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4139] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4140] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4141] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4142] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4143] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4144] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4145] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:4155] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4159] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4160] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4161] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4162] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4163] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4164] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4165] |
| no | outside | config | `pywin32` | package | [код: pysport@b548c35 uv.lock:4173] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4177] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4178] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4179] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4180] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4181] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4182] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4183] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4197] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4198] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4199] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4200] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4201] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4202] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4203] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4218] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4219] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4220] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4221] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4222] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4223] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4224] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4241] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4242] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4243] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4244] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4245] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4246] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4247] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4259] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4260] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4261] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4262] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4263] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4264] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4265] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4279] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4280] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4281] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4282] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4283] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4284] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4285] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4297] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4298] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4299] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4300] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4301] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4302] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4303] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4317] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4318] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4319] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4320] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4321] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4322] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4323] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4335] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4336] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4337] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4338] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4339] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4340] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4341] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4364] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4365] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4366] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4367] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4368] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4369] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4370] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4483] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4484] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4485] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4486] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4487] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4488] |
| no | outside | config | `sys_platform` | marker | [код: pysport@b548c35 uv.lock:4489] |

## OS06 Rust cfg: 0 hits, 0 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|

## RU01 Cyrillic in Python strings, docstrings and comments: 140 hits, 25 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| yes | domain | string | `б/р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2334] |
| yes | domain | string | `IIIю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2335] |
| yes | domain | string | `IIю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2336] |
| yes | domain | string | `Iю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2337] |
| yes | domain | string | `КМС` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2341] |
| yes | domain | string | `МС` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2342] |
| yes | domain | string | `МСМК` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2343] |
| yes | domain | string | `ЗМС` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2344] |
| yes | domain | string | `бр` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2354] |
| yes | domain | string | `б\р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2355] |
| yes | domain | string | `б-р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2356] |
| yes | domain | string | `1ю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2357] |
| yes | domain | string | `2ю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2358] |
| yes | domain | string | `3ю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2359] |
| yes | domain | string | `1р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2363] |
| yes | domain | string | `2р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2364] |
| yes | domain | string | `3р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2365] |
| yes | domain | string | `б/р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2374] |
| yes | domain | string | `б/р` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2375] |
| yes | domain | string | `IIIю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2376] |
| yes | domain | string | `IIю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2377] |
| yes | domain | string | `Iю` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2378] |
| yes | domain | string | `КМС` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2382] |
| yes | domain | string | `МС` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2383] |
| yes | domain | string | `МСМК` | data-literal | [код: pysport@b548c35 sportorg/models/memory.py:2384] |
| no | ui | comment | `<text omitted: 47 chars>` | comment | [код: pysport@b548c35 sportorg/gui/tabs/persons.py:109] |
| no | vendored | string | `cнят` | comparison | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:269] |
| no | vendored | string | `<text omitted: 12 chars>` | comparison | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:271] |
| no | vendored | string | `<text omitted: 10 chars>` | comparison | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:273] |
| no | vendored | string | `н/с` | comparison | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:275] |
| no | vendored | string | `<text omitted: 8 chars>` | comparison | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:37] |
| no | vendored | docstring | `<text omitted: 121 chars>` | docstring | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:32-35] |
| no | application | docstring | `<text omitted: 233 chars>` | docstring | [код: pysport@b548c35 sportorg/modules/live/orgeo.py:208-213] |
| no | application | docstring | `<text omitted: 627 chars>` | docstring | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:1-14] |
| no | application | string | `<text omitted: 8 chars>` | data-literal | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:38] |
| no | application | string | `непр.отмет.` | data-literal | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:39] |
| no | application | string | `<text omitted: 12 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:55] |
| no | application | string | `<text omitted: 5 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:56] |
| no | application | string | `<text omitted: 24 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:57] |
| no | application | string | `<text omitted: 38 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:58] |
| no | application | string | `<text omitted: 14 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:60] |
| no | application | string | `<text omitted: 8 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:62] |
| no | application | string | `<text omitted: 14 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:96] |
| no | application | string | `<text omitted: 8 chars>` | assignment | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:98] |
| no | application | string | `cнят` | return-value | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:374] |
| no | application | string | `н/с` | return-value | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:374] |
| no | application | string | `<text omitted: 10 chars>` | return-value | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:403] |
| no | application | string | `н/с` | return-value | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:405] |
| no | application | string | `cнят` | return-value | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:406] |
| no | outside | comment | `<text omitted: 59 chars>` | comment | [код: pysport@b548c35 tests/test_credit_calculation.py:22] |
| no | outside | string | `<text omitted: 4 chars>` | data-literal | [код: pysport@b548c35 tests/test_memory_model.py:19] |
| no | outside | string | `<text omitted: 4 chars>` | data-literal | [код: pysport@b548c35 tests/test_memory_model.py:43] |
| no | outside | string | `<text omitted: 4 chars>` | data-literal | [код: pysport@b548c35 tests/test_memory_model.py:67] |
| no | outside | string | `<text omitted: 3 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:5] |
| no | outside | string | `<text omitted: 2 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:6] |
| no | outside | string | `<text omitted: 2 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:13] |
| no | outside | string | `<text omitted: 2 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:14] |
| no | outside | string | `<text omitted: 2 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:15] |
| no | outside | string | `<text omitted: 2 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:16] |
| no | outside | string | `<text omitted: 4 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:17] |
| no | outside | string | `<text omitted: 4 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:18] |
| no | outside | string | `<text omitted: 4 chars>` | call-argument | [код: pysport@b548c35 tests/test_qualification.py:19] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:89] |
| no | outside | comment | `<text omitted: 49 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:90] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:101] |
| no | outside | comment | `<text omitted: 84 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:102] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:115] |
| no | outside | comment | `<text omitted: 85 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:116] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:122] |
| no | outside | comment | `<text omitted: 51 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:123] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:134] |
| no | outside | comment | `<text omitted: 34 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:135] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:188] |
| no | outside | comment | `<text omitted: 69 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:189] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:213] |
| no | outside | comment | `<text omitted: 69 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:214] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:222] |
| no | outside | comment | `<text omitted: 49 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:223] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:249] |
| no | outside | comment | `<text omitted: 84 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:250] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:267] |
| no | outside | comment | `<text omitted: 85 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:268] |
| no | outside | comment | `<text omitted: 24 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:276] |
| no | outside | comment | `<text omitted: 51 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:277] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:297] |
| no | outside | comment | `<text omitted: 69 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:298] |
| no | outside | comment | `<text omitted: 30 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:299] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:321] |
| no | outside | comment | `<text omitted: 71 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:322] |
| no | outside | comment | `<text omitted: 42 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:323] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:356] |
| no | outside | comment | `<text omitted: 69 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:357] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:381] |
| no | outside | comment | `<text omitted: 69 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:382] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:390] |
| no | outside | comment | `<text omitted: 49 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:391] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:416] |
| no | outside | comment | `<text omitted: 84 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:417] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:434] |
| no | outside | comment | `<text omitted: 85 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:435] |
| no | outside | comment | `<text omitted: 32 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:443] |
| no | outside | comment | `<text omitted: 51 chars>` | comment | [код: pysport@b548c35 tests/test_relay_results.py:444] |
| no | outside | string | `<text omitted: 4 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:20] |
| no | outside | string | `<text omitted: 8 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:20] |
| no | outside | string | `<text omitted: 9 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:22] |
| no | outside | string | `<text omitted: 7 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:23] |
| no | outside | string | `<text omitted: 8 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:24] |
| no | outside | string | `<text omitted: 5 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:31] |
| no | outside | string | `<text omitted: 5 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:38] |
| no | outside | string | `<text omitted: 4 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:48] |
| no | outside | string | `<text omitted: 8 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:48] |
| no | outside | string | `<text omitted: 9 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:50] |
| no | outside | string | `<text omitted: 7 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:51] |
| no | outside | string | `<text omitted: 8 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:52] |
| no | outside | string | `<text omitted: 5 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:59] |
| no | outside | string | `<text omitted: 9 chars>` | data-literal | [код: pysport@b548c35 tests/test_sfrx.py:66] |
| no | outside | comment | `<text omitted: 37 chars>` | comment | [код: pysport@b548c35 tests/test_sfrx.py:103] |
| no | outside | string | `<text omitted: 21 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:66] |
| no | outside | string | `<text omitted: 16 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:67] |
| no | outside | string | `<text omitted: 17 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:72] |
| no | outside | string | `<text omitted: 13 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:73] |
| no | outside | string | `<text omitted: 9 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:74] |
| no | outside | string | `<text omitted: 3 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:77] |
| no | outside | string | `<text omitted: 7 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:79] |
| no | outside | string | `<text omitted: 7 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:86] |
| no | outside | string | `<text omitted: 4 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:88] |
| no | outside | string | `<text omitted: 6 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:89] |
| no | outside | string | `<text omitted: 8 chars>` | comparison | [код: pysport@b548c35 tests/test_sfrxexporter.py:227] |
| no | outside | string | `<text omitted: 4 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:231] |
| no | outside | string | `<text omitted: 6 chars>` | call-argument | [код: pysport@b548c35 tests/test_sfrxexporter.py:232] |
| no | outside | string | `<text omitted: 6 chars>` | comparison | [код: pysport@b548c35 tests/test_sfrxexporter.py:266] |
| no | outside | string | `<text omitted: 4 chars>` | comparison | [код: pysport@b548c35 tests/test_sfrxexporter.py:267] |
| no | outside | string | `<text omitted: 12 chars>` | assignment | [код: pysport@b548c35 tests/test_wdb.py:72] |
| no | outside | string | `<text omitted: 7 chars>` | assignment | [код: pysport@b548c35 tests/test_wdb.py:84] |
| no | outside | string | `<text omitted: 6 chars>` | assignment | [код: pysport@b548c35 tests/test_wdb.py:98] |
| no | outside | string | `<text omitted: 13 chars>` | assignment | [код: pysport@b548c35 tests/test_wdb.py:113] |
| no | outside | string | `<text omitted: 6 chars>` | call-argument | [код: pysport@b548c35 tests/test_winorient.py:14] |
| no | outside | string | `<text omitted: 8 chars>` | call-argument | [код: pysport@b548c35 tests/test_winorient.py:14] |
| no | outside | string | `<text omitted: 7 chars>` | comparison | [код: pysport@b548c35 tests/test_winorient.py:17] |
| no | outside | string | `<text omitted: 19 chars>` | comparison | [код: pysport@b548c35 tests/test_winorient.py:19] |

## RU02 EVSK ranks and Qualification: 116 hits, 51 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| yes | domain | code | `Qualification` | import | [код: pysport@b548c35 sportorg/models/constant.py:8] |
| yes | domain | code | `Qualification` |  | [код: pysport@b548c35 sportorg/models/constant.py:85] |
| yes | domain | code | `Qualification.I` |  | [код: pysport@b548c35 sportorg/models/constant.py:242] |
| yes | domain | code | `Qualification.II` |  | [код: pysport@b548c35 sportorg/models/constant.py:243] |
| yes | domain | code | `Qualification.III` |  | [код: pysport@b548c35 sportorg/models/constant.py:244] |
| yes | domain | code | `Qualification.I_Y` |  | [код: pysport@b548c35 sportorg/models/constant.py:245] |
| yes | domain | code | `Qualification.II_Y` |  | [код: pysport@b548c35 sportorg/models/constant.py:246] |
| yes | domain | code | `Qualification.III_Y` |  | [код: pysport@b548c35 sportorg/models/constant.py:247] |
| yes | domain | code | `Qualification.KMS` |  | [код: pysport@b548c35 sportorg/models/constant.py:248] |
| yes | domain | code | `Qualification.MS` |  | [код: pysport@b548c35 sportorg/models/constant.py:249] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/memory.py:511] |
| yes | domain | code | `Qualification.get_qual_by_code` |  | [код: pysport@b548c35 sportorg/models/memory.py:662] |
| yes | domain | code | `Qualification` |  | [код: pysport@b548c35 sportorg/models/memory.py:1357] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/memory.py:1357] |
| yes | domain | code | `Qualification.get_qual_by_code` |  | [код: pysport@b548c35 sportorg/models/memory.py:1465] |
| yes | domain | code | `class Qualification` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2314] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2315] |
| yes | domain | code | `Qualification.I_Y` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2316] |
| yes | domain | code | `Qualification.II_Y` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2317] |
| yes | domain | code | `Qualification.III_Y` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2318] |
| yes | domain | code | `Qualification.I` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2319] |
| yes | domain | code | `Qualification.II` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2320] |
| yes | domain | code | `Qualification.III` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2321] |
| yes | domain | code | `Qualification.KMS` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2322] |
| yes | domain | code | `Qualification.MS` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2323] |
| yes | domain | code | `Qualification.MSMK` | definition | [код: pysport@b548c35 sportorg/models/memory.py:2324] |
| yes | domain | string | `КМС` |  | [код: pysport@b548c35 sportorg/models/memory.py:2341] |
| yes | domain | string | `МС` |  | [код: pysport@b548c35 sportorg/models/memory.py:2342] |
| yes | domain | string | `МСМК` |  | [код: pysport@b548c35 sportorg/models/memory.py:2343] |
| yes | domain | string | `ЗМС` |  | [код: pysport@b548c35 sportorg/models/memory.py:2344] |
| yes | domain | string | `КМС` |  | [код: pysport@b548c35 sportorg/models/memory.py:2382] |
| yes | domain | string | `МС` |  | [код: pysport@b548c35 sportorg/models/memory.py:2383] |
| yes | domain | string | `МСМК` |  | [код: pysport@b548c35 sportorg/models/memory.py:2384] |
| yes | domain | code | `Qualification` |  | [код: pysport@b548c35 sportorg/models/memory.py:2397] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/memory.py:2403] |
| yes | domain | code | `Qualification.get_qual_by_code` |  | [код: pysport@b548c35 sportorg/models/memory.py:2438] |
| yes | domain | code | `Qualification.MS` |  | [код: pysport@b548c35 sportorg/models/memory.py:2454] |
| yes | domain | code | `Qualification.MS` |  | [код: pysport@b548c35 sportorg/models/memory.py:2455] |
| yes | domain | code | `Qualification.KMS` |  | [код: pysport@b548c35 sportorg/models/memory.py:2457] |
| yes | domain | code | `Qualification.KMS` |  | [код: pysport@b548c35 sportorg/models/memory.py:2458] |
| yes | domain | code | `Qualification.I` |  | [код: pysport@b548c35 sportorg/models/memory.py:2460] |
| yes | domain | code | `Qualification.II` |  | [код: pysport@b548c35 sportorg/models/memory.py:2461] |
| yes | domain | code | `Qualification.III` |  | [код: pysport@b548c35 sportorg/models/memory.py:2462] |
| yes | domain | code | `Qualification.I_Y` |  | [код: pysport@b548c35 sportorg/models/memory.py:2463] |
| yes | domain | code | `Qualification.II_Y` |  | [код: pysport@b548c35 sportorg/models/memory.py:2464] |
| yes | domain | code | `Qualification.III_Y` |  | [код: pysport@b548c35 sportorg/models/memory.py:2465] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/memory.py:2468] |
| yes | domain | code | `Qualification` | import | [код: pysport@b548c35 sportorg/models/result/result_calculation.py:6] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/result/result_calculation.py:267] |
| yes | domain | code | `Qualification` | import | [код: pysport@b548c35 sportorg/models/result/split_calculation.py:4] |
| yes | domain | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 sportorg/models/result/split_calculation.py:19] |
| no | ui | code | `Qualification` | import | [код: pysport@b548c35 sportorg/gui/dialogs/entry_mass_edit.py:18] |
| no | ui | code | `Qualification.list_qual` |  | [код: pysport@b548c35 sportorg/gui/dialogs/entry_mass_edit.py:69] |
| no | ui | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 sportorg/gui/dialogs/entry_mass_edit.py:173] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/entry_mass_edit.py:249] |
| no | ui | code | `Qualification` | import | [код: pysport@b548c35 sportorg/gui/dialogs/group_ranking.py:26] |
| no | ui | code | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/group_ranking.py:77] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/import_persons_table_dialog.py:58] |
| no | ui | code | `Qualification` | import | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:24] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:107] |
| no | ui | code | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:111] |
| no | ui | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 sportorg/gui/dialogs/person_edit.py:206] |
| no | ui | code | `Qualification` | import | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:24] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:44] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:347] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:412] |
| no | ui | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 sportorg/gui/dialogs/text_io.py:413] |
| no | ui | string | `Qualification` |  | [код: pysport@b548c35 sportorg/gui/tabs/memory_model.py:330] |
| no | vendored | code | `Qualification` | import | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:7] |
| no | vendored | code | `Qualification` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:124] |
| no | application | code | `Qualification` | import | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:17] |
| no | application | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:204] |
| no | application | code | `Qualification` | import | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:7] |
| no | application | code | `Qualification` |  | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:511] |
| no | application | code | `Qualification` | import | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:12] |
| no | application | code | `Qualification.MSMK` |  | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:127] |
| no | application | code | `Qualification.get_qual_by_code` |  | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:128] |
| no | application | code | `Qualification` |  | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:262] |
| no | application | code | `Qualification` | import | [код: pysport@b548c35 sportorg/modules/winorient/winorient.py:6] |
| no | application | code | `Qualification` |  | [код: pysport@b548c35 sportorg/modules/winorient/winorient.py:47] |
| no | outside | code | `Qualification` | import | [код: pysport@b548c35 tests/test_qualification.py:1] |
| no | outside | code | `Qualification.KMS` |  | [код: pysport@b548c35 tests/test_qualification.py:5] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:5] |
| no | outside | code | `Qualification.MS` |  | [код: pysport@b548c35 tests/test_qualification.py:6] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:6] |
| no | outside | code | `Qualification.I` |  | [код: pysport@b548c35 tests/test_qualification.py:10] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:10] |
| no | outside | code | `Qualification.II` |  | [код: pysport@b548c35 tests/test_qualification.py:11] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:11] |
| no | outside | code | `Qualification.III` |  | [код: pysport@b548c35 tests/test_qualification.py:12] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:12] |
| no | outside | code | `Qualification.I` |  | [код: pysport@b548c35 tests/test_qualification.py:13] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:13] |
| no | outside | code | `Qualification.II` |  | [код: pysport@b548c35 tests/test_qualification.py:14] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:14] |
| no | outside | code | `Qualification.III` |  | [код: pysport@b548c35 tests/test_qualification.py:15] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:15] |
| no | outside | code | `Qualification.I_Y` |  | [код: pysport@b548c35 tests/test_qualification.py:16] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:16] |
| no | outside | code | `Qualification.III_Y` |  | [код: pysport@b548c35 tests/test_qualification.py:17] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:17] |
| no | outside | code | `Qualification.III_Y` |  | [код: pysport@b548c35 tests/test_qualification.py:18] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:18] |
| no | outside | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 tests/test_qualification.py:19] |
| no | outside | code | `Qualification.get_qual_by_name` |  | [код: pysport@b548c35 tests/test_qualification.py:19] |
| no | outside | code | `Qualification` | import | [код: pysport@b548c35 tests/test_sfrx.py:2] |
| no | outside | code | `Qualification.I` |  | [код: pysport@b548c35 tests/test_sfrx.py:28] |
| no | outside | code | `Qualification.II` |  | [код: pysport@b548c35 tests/test_sfrx.py:56] |
| no | outside | string | `Qualification` |  | [код: pysport@b548c35 tests/test_sfrx.py:101] |
| no | outside | code | `class Qualification` | definition | [код: pysport@b548c35 tests/test_sfrxexporter.py:29] |
| no | outside | code | `Qualification.NOT_QUALIFIED` | definition | [код: pysport@b548c35 tests/test_sfrxexporter.py:30] |
| no | outside | code | `Qualification` |  | [код: pysport@b548c35 tests/test_sfrxexporter.py:36] |
| no | outside | code | `Qualification.NOT_QUALIFIED` |  | [код: pysport@b548c35 tests/test_sfrxexporter.py:152] |
| no | outside | code | `Qualification` | import | [код: pysport@b548c35 tests/test_winorient.py:1] |
| no | outside | code | `Qualification.MS` |  | [код: pysport@b548c35 tests/test_winorient.py:23] |
| no | outside | string | `Qualification` |  | [код: pysport@b548c35 tests/test_winorient.py:23] |

## RU03 Russian services and domains: 47 hits, 1 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| yes | foundation | string | `telegram` |  | [код: pysport@b548c35 sportorg/settings.py:17] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/settings.py:229] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:46] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:110] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:111] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:112] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:114] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:116] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:140] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:141] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:142] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:143] |
| no | ui | string | `telegram` |  | [код: pysport@b548c35 sportorg/gui/dialogs/telegram_dialog.py:144] |
| no | ui | string | `orgeo` |  | [код: pysport@b548c35 sportorg/gui/menu/actions.py:429] |
| no | ui | string | `orgeo.ru` |  | [код: pysport@b548c35 sportorg/gui/menu/actions.py:429] |
| no | ui | string | `Orgeo` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:155] |
| no | ui | string | `Orgeo.ru` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:155] |
| no | ui | string | `Orgeo` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:156] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:486] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:492] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:534] |
| no | ui | string | `Telegram` |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:535] |
| no | vendored | string | `orgeo` |  | [код: pysport@b548c35 sportorg/libs/iof/parser.py:13] |
| no | vendored | string | `orgeo.ru` |  | [код: pysport@b548c35 sportorg/libs/iof/parser.py:13] |
| no | vendored | string | `orgeo` |  | [код: pysport@b548c35 sportorg/libs/iof/parser.py:170] |
| no | vendored | string | `orgeo` |  | [код: pysport@b548c35 sportorg/libs/iof/parser.py:173] |
| no | vendored | comment | `mail.ru` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:20] |
| no | vendored | comment | `www.sportsystem.ru` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:20] |
| no | vendored | string | `orgeo` |  | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:52] |
| no | vendored | docstring | `yandex` |  | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:3] |
| no | vendored | docstring | `yandex.ru` |  | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:3] |
| no | vendored | string | `telegram` |  | [код: pysport@b548c35 sportorg/libs/telegram/telegram.py:5] |
| no | vendored | string | `orgeo` |  | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:40] |
| no | vendored | string | `orgeo.ru` |  | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:40] |
| no | application | string | `Orgeo` |  | [код: pysport@b548c35 sportorg/modules/live/orgeo.py:172] |
| no | application | docstring | `orgeo` |  | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:2] |
| no | application | docstring | `orgeo.ru` |  | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:2] |
| no | application | string | `Telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:14] |
| no | application | string | `telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:48] |
| no | application | string | `telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:49] |
| no | application | string | `telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:50] |
| no | application | string | `telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:51] |
| no | application | string | `telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:52] |
| no | application | string | `Telegram` |  | [код: pysport@b548c35 sportorg/modules/telegram/telegram.py:79] |
| no | outside | string | `Telegram` |  | [код: pysport@b548c35 tests/test_menu_features.py:56] |
| no | outside | string | `Telegram` |  | [код: pysport@b548c35 tests/test_menu_features.py:57] |
| no | outside | string | `Telegram` |  | [код: pysport@b548c35 tests/test_menu_features.py:91] |

## RU04 Cyrillic encodings: 9 hits, 2 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| yes | foundation | string | `windows-1251` |  | [код: pysport@b548c35 sportorg/utils/text.py:15] |
| yes | foundation | comment | `windows-1251` |  | [код: pysport@b548c35 sportorg/utils/text.py:22] |
| no | vendored | string | `windows-1251` |  | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:71] |
| no | vendored | docstring | `Windows-1251` |  | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:7] |
| no | vendored | string | `windows-1251` |  | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:8] |
| no | vendored | docstring | `windows-1251` |  | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:34] |
| no | vendored | string | `cp1251` |  | [код: pysport@b548c35 sportorg/libs/winorient/wo.py:13] |
| no | application | string | `cp1251` |  | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:43] |
| no | application | string | `cp1251` |  | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:42] |

## RU05 Russian locale defaults: 8 hits, 4 core

| core | layer | kind | token | detail | location |
|---|---|---|---|---|---|
| yes | foundation | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/language.py:23] |
| yes | foundation | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/language.py:32] |
| yes | foundation | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/settings.py:41] |
| yes | foundation | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/settings.py:261] |
| no | application | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/modules/configs/configs.py:80] |
| no | application | string | `ru_RU` |  | [код: pysport@b548c35 sportorg/modules/configs/configs.py:201] |
| no | application | comment | `'RUS'` | quoted | [код: pysport@b548c35 sportorg/modules/live/orgeo.py:116] |
| no | outside | string | `ru_RU` |  | [код: pysport@b548c35 tests/test_theme_settings.py:31] |
