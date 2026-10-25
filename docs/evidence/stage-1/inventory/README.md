# Inventory of user-facing features (TASK-7 criterion 1, direction W1)

What: menu actions, report templates, import/export formats and documentation files of `pysport@b548c35` and `templates@cd95382`, each with module and `file:line`. Static: the sources are parsed with `ast` (or scanned by line) from `git show` at the pin; no legacy code is run or imported.

Files (`.json` is the machine output, `.md` the table; all rows about code carry a `[код: …]` tag):
- `menu.*`: the menu tree. Per node: path of translation keys, kind, shortcut, action name, other keys (`feature`, `icon`, `tabs`, `id`), the line in `menu.py`, and the class line in `actions.py`.
- `actions.*`: per resolved action class, the module-level names of `actions.py` that its body uses, with their source modules.
- `templates.*`: template files of both repositories (path, format, lines, bytes) and the lines of code that locate, list or render templates.
- `formats.*`: chains menu item → action class → format modules and calls into them → dialog filters; all `*.ext` filter literals and exact extension strings in `sportorg/`; reader/writer candidates by function name in format modules.
- `docs.*`: `docs/`, `*.md`, `*.rst`, `changelog*` files of both repositories.

## Definitions (fixed in `scripts/archaeology/inventory.py` before the run)
- **Menu node**: a dict inside the list assigned in `menu_list()` of `menu.py`, recursively through the `"actions"` key. `action` = has an `"action"` key; `submenu` = has an `"actions"` key; `separator` = `"type": "separator"`. The title is the key of `translate("…")`.
- **Action class**: a module-level class of `actions.py` with `metaclass=ActionFactory` (or inheriting such a class). The registry keeps the last class of a given name. Resolved = the menu name has such a class; unused = a class that no menu item names.
- **Class imports**: names bound at module level of `actions.py` (via `common.iter_imports`, not inside functions) that appear as a name in the class body (not in its bases). Function-local imports inside the class are listed apart and used for the chains.
- **Template file**: a tracked file with extension html, htm, docx, xlsx, xls, odt, ods, j2, jinja, jinja2, tpl or mustache. `lines` = physical lines (empty for the binary formats docx, xlsx, xls, odt, ods).
- **Loader line**: a non-comment line of a tracked `.py` file matching one of seven patterns (`LOADER_PATTERNS`: jinja2, docxtpl, env_config = `TEMPLATES_PATH`, list_templates, template_dir, render_text, setting). A line can match several patterns.
- **Filter**: a string literal in `sportorg/**.py` that contains `*.ext`. **Extension string**: a literal that is exactly a dot and 2-6 letters or digits.
- **Format chain**: menu item whose class (a) uses a name imported from a format module or (b) holds a filter literal in its line range of `actions.py`. The module → format table `FORMAT_MODULES` is `[допущение]` (taken from the directory names of `sportorg/modules` and `sportorg/libs`); it is printed in `formats.json`.
- **Reader/writer candidate**: a function or method defined in a format module whose name starts with a read-like (`read|import|parse|load|open|get_races`) or write-like (`write|export|save|dump|create|build|make|send`) verb. This is a name heuristic, not a classification of behaviour.
- **Documentation file**: tracked path under `docs/`, extension `.md`/`.rst`, or a basename starting with `changelog`.

## Key numbers (from the run)
| Item | Value |
|---|---|
| Menu nodes | 102: 82 actions, 15 submenus, 5 separators |
| Actions with a shortcut / with a `feature` key | 35 / 12 (counted over all nodes) |
| Registered action classes | 84; 82 resolved, 0 unresolved names, 2 unused: `OpenRecentAction` (actions.py:126), `LiveToggleAction` (actions.py:828) |
| Duplicate class names | 0 |
| Template files, templates repo | 62: 61 html, 1 docx (`ru/reports`: 47, `ru/split`: 9, root: 6) |
| Template files, pysport | 8 html under `sportorg/data/templates/` |
| Loader lines | 48 (setting 16, template_dir 12, render_text 7, list_templates 5, env_config 4, docxtpl 2, jinja2 2) |
| Format chains | 21 (13 distinct filter labels over the extensions .csv .docx .html .json .log .sfrx .txt .wdb .xml) |
| Filter literals / extension strings | 28 / 16 |
| Reader/writer candidates | 70: 40 read-like, 30 write-like (WinOrient 22, SFRx 21, IOF 14, SportOrg JSON 7, OCAD 5, Recovery 1) |
| Documentation files | 9 in pysport, 0 in templates repo |

## Observations (no classification; raised as open questions)
1. `OpenRecentAction` has no other reference in the code. `LiveToggleAction` is not in the menu but is requested by name at `sportorg/gui/main_window.py:564` and `sportorg/gui/toolbar.py:24`. So "unused by the menu" is not "dead".
2. The menu literal is only the static part. `plugin_menu_items()` adds a «Plugins» menu at run time, and `filter_menu_items()` drops items by `"show": False` or a disabled `feature` [код: pysport@b548c35 sportorg/gui/menu/menu.py:9-17]. The set a user sees depends on the settings.
3. The templates repo holds 62 files, the program holds 8; the file names of the two overlap only partly (e.g. both have `1_results.html`, `2_start_list.html`). Whether they are the same text was not compared here.
4. Format modules are shared with device drivers (`sportorg.modules.sfr`: the reader client and the SFRx exporter). The chain for «On/Off card readout» is therefore labelled SFRx although it is a device, not a file format. Devices and protocols are W5.
5. Some filter literals sit outside `actions.py` (`report_dialog.py`, `print_properties.py`, `wdb_number_setter.py`, `wdb_online_sender_dialog.py`, `main_window.py`) and are listed in `formats.md` but not attached to a menu item.
6. `File > Open` shows only a filter: the file is opened by the application (`self.app.open_file`), not by a module of the table.

## Limits
- Imports under an alias (`import x as y`) are not resolved by `common.iter_imports` (it keeps the original name). `actions.py` at the pin has no module-level aliased import (the grep for ` as ` shows only `except … as`).
- A class that reaches a format only through a helper defined elsewhere (e.g. `self.app.open_file`) shows no format module.
- Extension strings and filters are found as literals only; names built at run time, or extensions kept in configuration, are not seen.
- Loader lines come from regular expressions on lines, so they include definitions, tests and unrelated uses of the setting `templates_path`; the `kind` column lets the reader filter.
- No data of people is in the outputs.

## Checks
- `verify_locs`: 423 tags, 0 problems (sample of 10, seed 1, compared with the source lines printed by the command).
- A rerun is byte-identical (compared with `cmp`).
- `scripts.legacy verify` ok.
