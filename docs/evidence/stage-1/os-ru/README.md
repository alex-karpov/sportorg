# os-ru: OS-specific code and Russian specifics of pysport@b548c35

Produced by `scripts/archaeology/os_ru.py` (commands in `commands.txt`). The script lists hits with `file:line`; it classifies nothing (the agent classifies them in `classification.agent.md`, TASK-7 criterion 5). Files: `hits.{json,md}` (all hits, core first), `summary.{json,md}` (rule x core/outside x kind), `recall.{json,md}` (against `git grep`).

## Definitions

- core = layer rank 1 or 2 (`foundation`, `domain`) by `common.layer_of` on the module name; `sportorg.libs` (rank 0), gui, modules, startup and every file outside `sportorg/` are not core.
- kind: `code` (ast node), `string`, `docstring`, `comment` (tokenize), `config` (line of a non-Python file; Rust lines are `code`, comment lines `comment`).
- Python strings are scanned per constant (f-string parts separately); a match in a multi-line string is placed at its line inside the string, RU01 at the string start.

## Rules and exact patterns

| rule | what | patterns |
|---|---|---|
| OS01 | platform branches | ast dotted names `os.name`, `sys.getwindowsversion`, `sys.platform`, `platform.<name>`; `from sys import platform`, `from os import name`; compared literal in `detail` (`==`, `in`, `.startswith`) |
| OS02 | OS-only modules | imports of `_winreg`, `fcntl`, `grp`, `msvcrt`, `pwd`, `pythoncom`, `pywintypes`, `pywinusb`, `termios`, `winreg`, `winsound`, `wmi`, `win32*`; `ctypes.OleDLL`, `ctypes.WinDLL`, `ctypes.WinError`, `ctypes.oledll`, `ctypes.windll` (import and attribute) |
| OS03 | OS-only calls | ast `os.add_dll_directory`, `os.startfile`, names starting `ShellExecute`; first word `cmd`, `explorer`, `explorer.exe`, `open`, `start`, `xdg-open` of the first argument of `Popen`, `check_call`, `check_output`, `os.popen`, `os.system`, `subprocess.Popen`, `subprocess.call`, `subprocess.check_call`, `subprocess.check_output`, `subprocess.getoutput`, `subprocess.run`; text regex `\bxdg-open\b|ShellExecute\w*|\bexplorer(?:\.exe)?\b|\bcmd(?:\.exe)?\s+/[ck]\b|\bos\.startfile\b` |
| OS04 | OS paths and devices | text regexes com: `\bCOM\d+\b`; tty: `/dev/(?:tty|cu\.|serial)[\w./-]*`; drive: `[A-Z]:\\`; ext: `\.(?:exe|bat|dll)\b`; env: `\b(?:APPDATA|LOCALAPPDATA|USERPROFILE|HOME|XDG_[A-Z_]+)\b`; backslash: `\w\\(?![ux][0-9a-fA-F]{2}|U[0-9a-fA-F]{8})[A-Za-z_]\w+` |
| OS05 | dependency markers | `\b(?:sys_platform|platform_system|os_name)\b` and packages `\b(?:pywin32-ctypes|pypiwin32|pywin32|pywinusb|pyimpinj|comtypes|wmi)\b` (case-insensitive) in `*.toml`, `uv.lock` |
| OS06 | Rust cfg | `\bcfg(?:_attr)?!?\s*\([^\n]*?\b(windows|unix|target_os(?:\s*=\s*\"\w+\")?|target_family(?:\s*=\s*\"\w+\")?)` in `*.rs`, `*.toml` |
| RU01 | Cyrillic | `[\u0400-\u04ff]` in a string, docstring or comment; token shown only if one word of at most 40 characters, else `<text omitted: N chars>`; `detail` is a guess (log, exception, ui, data-literal, comparison, assignment, ...) from the parent node |
| RU02 | EVSK ranks | ast `Qualification`, `Qualification.<member>`, class `Qualification` members; text `МСМК|ЗМС|(?<!\w)МС(?!\w)|(?<!\w)КМС(?!\w)|[Рр]азряд\w*|[Мм]астер\w* спорта|\bQualification\b` |
| RU03 | Russian services | domains `\b[\w-]+(?:\.[\w-]+)*\.(?:ru|рф)\b`, keywords `orgeo|sportident\.ru|yandex|vk\.com|telegram|\bt\.me/` (case-insensitive; `telegram` is not checked for being bound to a Russian service) |
| RU04 | Cyrillic encodings | `cp-?1251|windows-1251|cp-?866|koi8(?:-?[ru])?` (case-insensitive) |
| RU05 | Russian locale defaults | substrings `Europe/Moscow|ru_RU|ru-RU`; whole strings `(?:ru|RU|RUS|ru_RU|ru-RU|Europe/Moscow)`; in comments quoted `[\"'](?:ru|RU|RUS|ru_RU|ru-RU)[\"']` |

Scope: tracked `*.py`, `*.rs`, `*.toml`, `*.iss`, `*.spec`, `*.bat`, `*.ps1`, `*.sh`, `Makefile`, `uv.lock`, `.github/**`. Non-Python files get OS03, OS04, RU03, RU04 (and OS05, OS06 where they apply); RU01, RU02, RU05 and ast rules are Python only.

## Key numbers

- files scanned: 240; unparsed by ast: 0 (none); undecodable: 0; hits: 923.

| rule | scope | code | string | docstring | comment | config | total |
|---|---|---|---|---|---|---|---|
| OS01 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS01 | outside | 20 | 0 | 0 | 0 | 0 | 20 |
| OS02 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS02 | outside | 6 | 0 | 0 | 0 | 0 | 6 |
| OS03 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS03 | outside | 1 | 0 | 0 | 0 | 0 | 1 |
| OS04 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS04 | outside | 0 | 6 | 2 | 3 | 13 | 24 |
| OS05 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS05 | outside | 0 | 0 | 0 | 0 | 552 | 552 |
| OS06 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| OS06 | outside | 0 | 0 | 0 | 0 | 0 | 0 |
| RU01 | core | 0 | 25 | 0 | 0 | 0 | 25 |
| RU01 | outside | 0 | 69 | 3 | 43 | 0 | 115 |
| RU02 | core | 44 | 7 | 0 | 0 | 0 | 51 |
| RU02 | outside | 56 | 9 | 0 | 0 | 0 | 65 |
| RU03 | core | 0 | 1 | 0 | 0 | 0 | 1 |
| RU03 | outside | 0 | 40 | 4 | 2 | 0 | 46 |
| RU04 | core | 0 | 1 | 0 | 1 | 0 | 2 |
| RU04 | outside | 0 | 5 | 2 | 0 | 0 | 7 |
| RU05 | core | 0 | 4 | 0 | 0 | 0 | 4 |
| RU05 | outside | 0 | 3 | 0 | 1 | 0 | 4 |

## Recall against git grep (line level, `*.py`)

| rule | grep lines | scanner lines | both | only grep | only scanner |
|---|---|---|---|---|---|
| OS01 | 20 | 20 | 20 | 0 | 0 |
| OS02 | 6 | 6 | 6 | 0 | 0 |
| OS04-com | 0 | 0 | 0 | 0 | 0 |
| OS04-drive | 1 | 1 | 1 | 0 | 0 |
| RU04 | 9 | 9 | 9 | 0 | 0 |
| RU05 | 8 | 8 | 8 | 0 | 0 |

## Limits

- Aliases (`import platform as p`, `from os import name as n` used later) are not followed; only the import line is a hit.
- Dynamic strings (concatenation, `format`, `chr`) are not evaluated; the backslash path join is a noisy regex (it also hits some regex-like strings).
- `HOME` in OS04 matches the word in any string or comment; line numbers inside multi-line strings count `\n` in the decoded value (escapes in non-raw strings can shift them).
- A hit is a place to look at, not a verdict: nothing here says whether the code is reachable, guarded by a fallback, or a false positive.
