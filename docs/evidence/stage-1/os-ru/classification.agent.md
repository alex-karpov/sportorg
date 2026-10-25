# OS-specific code and Russian specifics: classification by the agent

The labels in this file are the judgement of the main session's agent (Claude Code, Opus 5.5) on 2026-10-25, not script output; no human reviewed them. Source: `hits.json` (`scripts/archaeology/os_ru.py`). Plan Task 11: every core hit and every OS hit is classified. Coverage was checked: 686 hits = 603 OS hits (OS01–OS05; OS06 has none) + 83 core hits (RU01–RU05 with core = yes). Each hit sits in exactly one group below. Hits are grouped by the code they belong to; every tag of a group is listed except O16, which lists the line range.

## Criteria

OS categories (from the Stage 1 prompt), judged by reading the code around each hit:

- **all three**: works on Windows, Linux and macOS, with a branch per OS or OS-neutral code.
- **Windows-only with fallback**: a Windows-specific path exists and other OSes take another working path.
- **Windows-only without fallback**: the function is not available, or fails, on other OSes.
- **not-Windows**: specific to Linux or macOS.
- **false positive**: the match is not OS-dependent behaviour of the program (debug code, docstrings, tests of path logic).

RU categories:

- **national rule**: encodes a Russian sports regulation.
- **locale default or translation**: a Russian default for language, encoding or locale.
- **national integration**: binds to a Russian service.
- **false positive**: not Russia-specific.

Core = layer ranks 1–2 of the approved layer model.

## OS hits (603)

| group | hits | category | why | tags |
|---|---|---|---|---|
| O1 | 2 | Windows-only with fallback | build script: line 15 picks the cx_Freeze GUI base on Windows (default `None` elsewhere); line 123 adds the Windows-only MSI packager | [код: pysport@b548c35 builder.py:15] [код: pysport@b548c35 builder.py:123] |
| O2 | 1 | not-Windows | Linux-only workaround: adds the missing file suffix in the save dialog | [код: pysport@b548c35 sportorg/gui/dialogs/file_dialog.py:28] |
| O3 | 1 | Windows-only with fallback | suppresses a Windows alt-code quirk; other OSes do not need it | [код: pysport@b548c35 sportorg/gui/tabs/persons.py:110] |
| O4 | 7 | all three | theme detection has a branch per OS (registry / `defaults` / gsettings) and returns None otherwise | [код: pysport@b548c35 sportorg/gui/theme.py:100] [код: pysport@b548c35 sportorg/gui/theme.py:102] [код: pysport@b548c35 sportorg/gui/theme.py:104] [код: pysport@b548c35 sportorg/gui/theme.py:110] [код: pysport@b548c35 sportorg/gui/theme.py:112] |
| O5 | 4 | Windows-only without fallback | SFR reader over pywinusb HID; other OSes raise `Unsupported platform` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:278-279] | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:30] [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:31] [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:278] [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:279] |
| O6 | 3 | Windows + Linux; macOS without fallback | port auto-scan covers Linux `ttyUSB*` and Windows `COM0-31`, else raises; an explicit port works everywhere. **Outside the five categories; for the maintainer** | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:313] [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:320] [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:324] |
| O7 | 1 | all three | `shlex.split(posix=os.name != "nt")`, both paths | [код: pysport@b548c35 sportorg/modules/plugins/manager.py:519] |
| O8 | 5 | Windows-only with fallback | fast direct split printing via win32print on Windows; elsewhere the HTML/jinja2 path [код: pysport@b548c35 sportorg/modules/printing/model.py:42]. The fallback covers the HTML templates only: the options "Internal printing" are offered on every OS [код: pysport@b548c35 sportorg/gui/dialogs/print_properties.py:74-77], and outside Windows the setting goes to `get_template` as a template name [код: pysport@b548c35 sportorg/modules/printing/model.py:79] [код: pysport@b548c35 sportorg/libs/template/template.py:59], which by the code ends in `TemplateNotFound` (finding 6; added 2026-10-25 after the independent check) | [код: pysport@b548c35 sportorg/modules/printing/model.py:42] [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:7] [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:8] [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:9] [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:10] |
| O9 | 3 | not-Windows | tests skipped outside Linux | [код: pysport@b548c35 tests/test_reader.py:241] [код: pysport@b548c35 tests/test_reader.py:289] [код: pysport@b548c35 tests/test_reader.py:339] |
| O10 | 2 | Windows-only with fallback | test of the registry theme branch, skipped elsewhere | [код: pysport@b548c35 tests/test_theme.py:85] [код: pysport@b548c35 tests/test_theme.py:87] |
| O11 | 1 | Windows-only without fallback | `os.startfile` after saving a .docx report: no guard, so on Linux/macOS it raises `AttributeError` after the file is written. **Discrepancy: candidate legacy bug** | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:233] |
| O12 | 17 | Windows-only without fallback | packaging: the release workflow, Inno Setup script and cx_Freeze target build only a Windows installer/portable zip. Several OS04 `backslash` tokens are regex noise inside these genuine Windows paths | [код: pysport@b548c35 .github/workflows/release.yml:47] [код: pysport@b548c35 .github/workflows/release.yml:58] [код: pysport@b548c35 .github/workflows/release.yml:64] [код: pysport@b548c35 .github/workflows/release.yml:97] [код: pysport@b548c35 builder.py:87] [код: pysport@b548c35 sportorg.iss:7] [код: pysport@b548c35 sportorg.iss:18] [код: pysport@b548c35 sportorg.iss:47] [код: pysport@b548c35 sportorg.iss:51] [код: pysport@b548c35 sportorg.iss:60] [код: pysport@b548c35 sportorg.iss:83] [код: pysport@b548c35 sportorg.iss:97] |
| O13 | 1 | false positive | `/dev/ttyACM0` only in the module's `__main__` debug block | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:311] |
| O14 | 2 | false positive | docstring that mentions where the Windows build writes its log | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:2] |
| O15 | 1 | false positive | test builds a Windows path on purpose to test path handling on every OS | [код: pysport@b548c35 tests/test_paths.py:37] |
| O16 | 510 | all three | `sys_platform` resolution markers of third-party packages in `uv.lock`: the lock resolves per platform for Linux, macOS and Windows; not product code | uv.lock lines 5–4489 (all 510 `sys_platform` marker lines; list in hits.json) |
| O17 | 32 | Windows-only with fallback | `pywin32` (`win` extra): used only by the direct split printing of O8 | [код: pysport@b548c35 pyproject.toml:30] [код: pysport@b548c35 pyproject.toml:53] [код: pysport@b548c35 uv.lock:2776] [код: pysport@b548c35 uv.lock:2799] [код: pysport@b548c35 uv.lock:3609] [код: pysport@b548c35 uv.lock:3613] [код: pysport@b548c35 uv.lock:3614] [код: pysport@b548c35 uv.lock:3615] [код: pysport@b548c35 uv.lock:3616] [код: pysport@b548c35 uv.lock:3617] [код: pysport@b548c35 uv.lock:3618] [код: pysport@b548c35 uv.lock:3619] [код: pysport@b548c35 uv.lock:3620] [код: pysport@b548c35 uv.lock:3621] [код: pysport@b548c35 uv.lock:3622] [код: pysport@b548c35 uv.lock:3623] [код: pysport@b548c35 uv.lock:3624] [код: pysport@b548c35 uv.lock:3625] [код: pysport@b548c35 uv.lock:3626] [код: pysport@b548c35 uv.lock:3627] [код: pysport@b548c35 uv.lock:3628] [код: pysport@b548c35 uv.lock:3629] [код: pysport@b548c35 uv.lock:3630] [код: pysport@b548c35 uv.lock:3631] [код: pysport@b548c35 uv.lock:3632] [код: pysport@b548c35 uv.lock:3933] [код: pysport@b548c35 uv.lock:3958] [код: pysport@b548c35 uv.lock:3959] [код: pysport@b548c35 uv.lock:3982] [код: pysport@b548c35 uv.lock:4006] [код: pysport@b548c35 uv.lock:4155] [код: pysport@b548c35 uv.lock:4173] |
| O18 | 5 | Windows-only without fallback | `pywinusb` (runtime): the SFR reader of O5 | [код: pysport@b548c35 pyproject.toml:20] [код: pysport@b548c35 uv.lock:3636] [код: pysport@b548c35 uv.lock:3639] [код: pysport@b548c35 uv.lock:3920] [код: pysport@b548c35 uv.lock:3983] |
| O19 | 5 | Windows-only without fallback | `pyImpinj` (`win` extra, marker `python_version == '3.8'`): the Impinj RFID reader; its import is guarded [код: pysport@b548c35 sportorg/modules/rfid_impinj/rfid_impinj.py:16-19], so the reader is missing without the extra and on Python ≥ 3.9 (see H6). "Windows-only" rests on local practice, not on code: the install guide gives `--extra win` for Windows only [код: pysport@b548c35 CONTRIBUTING.md:38] and CI installs it on `windows-latest` [код: pysport@b548c35 .github/workflows/check.yml:49]; the lock does not restrict the OS (pyImpinj 1.2 is a `py3-none-any` wheel [код: pysport@b548c35 uv.lock:3202], libscrc has a manylinux wheel for Python 3.8 [код: pysport@b548c35 uv.lock:1712]) (basis added 2026-10-25 after the independent check) | [код: pysport@b548c35 pyproject.toml:31] [код: pysport@b548c35 uv.lock:3194] [код: pysport@b548c35 uv.lock:3202] [код: pysport@b548c35 uv.lock:3932] [код: pysport@b548c35 uv.lock:3979] |

## Core hits: Russian specifics (83)

| group | hits | category | why | tags |
|---|---|---|---|---|
| R1 | 76 | national rule | the `Qualification` rank scale and its text↔code tables (`б/р`, `Iю…IIIю`, `I…III`, `КМС`, `МС`, `МСМК`, `ЗМС`), rank assignment (`assigned_rank`), ranking items with `max_place` per rank. Whether it equals the EVSK of the current edition needs the rules document: `[допущение]` until Stage 3 | [код: pysport@b548c35 sportorg/models/constant.py:8] [код: pysport@b548c35 sportorg/models/constant.py:85] [код: pysport@b548c35 sportorg/models/constant.py:242] [код: pysport@b548c35 sportorg/models/constant.py:243] [код: pysport@b548c35 sportorg/models/constant.py:244] [код: pysport@b548c35 sportorg/models/constant.py:245] [код: pysport@b548c35 sportorg/models/constant.py:246] [код: pysport@b548c35 sportorg/models/constant.py:247] [код: pysport@b548c35 sportorg/models/constant.py:248] [код: pysport@b548c35 sportorg/models/constant.py:249] [код: pysport@b548c35 sportorg/models/memory.py:511] [код: pysport@b548c35 sportorg/models/memory.py:662] [код: pysport@b548c35 sportorg/models/memory.py:1357] [код: pysport@b548c35 sportorg/models/memory.py:1465] [код: pysport@b548c35 sportorg/models/memory.py:2314] [код: pysport@b548c35 sportorg/models/memory.py:2315] [код: pysport@b548c35 sportorg/models/memory.py:2316] [код: pysport@b548c35 sportorg/models/memory.py:2317] [код: pysport@b548c35 sportorg/models/memory.py:2318] [код: pysport@b548c35 sportorg/models/memory.py:2319] [код: pysport@b548c35 sportorg/models/memory.py:2320] [код: pysport@b548c35 sportorg/models/memory.py:2321] [код: pysport@b548c35 sportorg/models/memory.py:2322] [код: pysport@b548c35 sportorg/models/memory.py:2323] [код: pysport@b548c35 sportorg/models/memory.py:2324] [код: pysport@b548c35 sportorg/models/memory.py:2334] [код: pysport@b548c35 sportorg/models/memory.py:2335] [код: pysport@b548c35 sportorg/models/memory.py:2336] [код: pysport@b548c35 sportorg/models/memory.py:2337] [код: pysport@b548c35 sportorg/models/memory.py:2341] [код: pysport@b548c35 sportorg/models/memory.py:2342] [код: pysport@b548c35 sportorg/models/memory.py:2343] [код: pysport@b548c35 sportorg/models/memory.py:2344] [код: pysport@b548c35 sportorg/models/memory.py:2354] [код: pysport@b548c35 sportorg/models/memory.py:2355] [код: pysport@b548c35 sportorg/models/memory.py:2356] [код: pysport@b548c35 sportorg/models/memory.py:2357] [код: pysport@b548c35 sportorg/models/memory.py:2358] [код: pysport@b548c35 sportorg/models/memory.py:2359] [код: pysport@b548c35 sportorg/models/memory.py:2363] [код: pysport@b548c35 sportorg/models/memory.py:2364] [код: pysport@b548c35 sportorg/models/memory.py:2365] [код: pysport@b548c35 sportorg/models/memory.py:2374] [код: pysport@b548c35 sportorg/models/memory.py:2375] [код: pysport@b548c35 sportorg/models/memory.py:2376] [код: pysport@b548c35 sportorg/models/memory.py:2377] [код: pysport@b548c35 sportorg/models/memory.py:2378] [код: pysport@b548c35 sportorg/models/memory.py:2382] [код: pysport@b548c35 sportorg/models/memory.py:2383] [код: pysport@b548c35 sportorg/models/memory.py:2384] [код: pysport@b548c35 sportorg/models/memory.py:2397] [код: pysport@b548c35 sportorg/models/memory.py:2403] [код: pysport@b548c35 sportorg/models/memory.py:2438] [код: pysport@b548c35 sportorg/models/memory.py:2454] [код: pysport@b548c35 sportorg/models/memory.py:2455] [код: pysport@b548c35 sportorg/models/memory.py:2457] [код: pysport@b548c35 sportorg/models/memory.py:2458] [код: pysport@b548c35 sportorg/models/memory.py:2460] [код: pysport@b548c35 sportorg/models/memory.py:2461] [код: pysport@b548c35 sportorg/models/memory.py:2462] [код: pysport@b548c35 sportorg/models/memory.py:2463] [код: pysport@b548c35 sportorg/models/memory.py:2464] [код: pysport@b548c35 sportorg/models/memory.py:2465] [код: pysport@b548c35 sportorg/models/memory.py:2468] [код: pysport@b548c35 sportorg/models/result/result_calculation.py:6] [код: pysport@b548c35 sportorg/models/result/result_calculation.py:267] [код: pysport@b548c35 sportorg/models/result/split_calculation.py:4] [код: pysport@b548c35 sportorg/models/result/split_calculation.py:19] |
| R2 | 1 | false positive | `FEATURE_TELEGRAM`: Telegram is an international service, not Russian-specific; the rule matched the name only | [код: pysport@b548c35 sportorg/settings.py:17] |
| R3 | 2 | locale default or translation | `windows-1251` is one of the encodings tried when reading text files; the comment names Russian users and OCAD < 11 as the reason | [код: pysport@b548c35 sportorg/utils/text.py:15] [код: pysport@b548c35 sportorg/utils/text.py:22] |
| R4 | 4 | locale default or translation | `ru_RU` is the fallback locale of `language.py` and `settings.py` | [код: pysport@b548c35 sportorg/language.py:23] [код: pysport@b548c35 sportorg/language.py:32] [код: pysport@b548c35 sportorg/settings.py:41] [код: pysport@b548c35 sportorg/settings.py:261] |

## Result

| OS category | hits |
|---|---|
| Windows + Linux; macOS without fallback | 3 |
| Windows-only with fallback | 42 |
| Windows-only without fallback | 32 |
| all three | 518 |
| false positive | 4 |
| not-Windows | 4 |

| RU category (core) | hits |
|---|---|
| false positive | 1 |
| locale default or translation | 6 |
| national rule | 76 |

Findings for the report:

1. **No OS-specific code in the core.** OS01–OS05 have no hit in ranks 1–2. Windows-only behaviour lives in the device libraries (SFR via pywinusb, Impinj via pyImpinj on Python 3.8), the printing adapter (with a fallback for HTML templates, see finding 6), one GUI call (`os.startfile`) and the packaging.
2. **Features unavailable outside Windows:** the SFR reader (O5, O18), the Impinj RFID reader (O19: by the install practice, not by code; and only on Python 3.8), and opening a saved .docx report (O11).
3. **O11 is a discrepancy** (rule 9). On Linux/macOS saving a .docx report ends with an `AttributeError`. Proposed class: legacy bug. Raised to the maintainer.
4. **O6 does not fit the five categories:** Windows and Linux are supported, macOS needs an explicit port.
5. **Russian specifics in the core are one block:** the rank scale `Qualification` with its tables and rank assignment (76 hits, national rule), plus the defaults `ru_RU` and `windows-1251` (6 hits). The one service-name hit (Telegram) is a false positive. Russian services outside the core (`orgeo.ru`, `mail.ru`, `yandex.ru`, Telegram dialogs) are listed in `hits.md` and are not classified here; the plan asks for the core only.
6. **O8 is a probable discrepancy** (rule 9, found by the independent check on 2026-10-25 and confirmed by reading the code). The split-printing dialog offers "Internal printing" on every OS. Outside Windows that choice is passed to jinja2 as a template name, so split printing fails, by the code. Legacy is not run, so this is not confirmed by a run. Proposed class: legacy bug. Raised to the maintainer.

Limits:

- One agent labelled, no human review.
- The OS categories describe the code paths read, not runs on three OSes; legacy is not run in Stage 1.
- O16 is classified as a block.
