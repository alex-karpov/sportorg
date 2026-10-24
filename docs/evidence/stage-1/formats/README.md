# Formats: readers and writers of files and devices (TASK-7 criterion 4)

What: every I/O site in tracked `sportorg/**/*.py` of `pysport@b548c35`, one row per function, with direction, format and the hard-coded values of the function.
- `formats.json`: rows (calls and values, each with a `[код]` tag) and the summary.
- `formats.md`: the function table, the value table and the summary.

Definitions (`scripts/archaeology/formats.py`):
- io_site: a call matching the API tables of formats.py (open family with the mode's direction; csv/json/orjson/xml/lxml/struct/zip/gzip/docx/jinja2/INI/PO; serial, socket, HTTP, SPORTident, HID, Impinj, printer; Path.read_*/write_*).
- row: one per enclosing function, class body or module level with at least one I/O site; nested functions are rows of their own.
- direction: read, write, both (read and write, or both in one call), device (only device calls), unknown (open with a non-literal mode).
- values: literals in the same scope: keyword/positional parameters, strings classified by content, bytes and hex constants, ints in comparisons, subscripts and packing, and module or class constants referenced by name (tag at the assignment line, use_tag at the use).
- device_methods: [допущение] a call of one of DEVICE_METHODS (read, readline, write, flush, send, recv, reset_input_buffer, send_output_report, set_raw_data_handler, ...) on a name or attribute chain whose last part, case-insensitive and without leading underscores, is in DEVICE_VOCABULARY = {serial, ser, port, sock, socket, conn, device, dev, reader, station, hid}; direction comes from the method; format is the device format of the module path (e.g. Sportiduino serial, SFR HID), `socket` for sock/socket/conn, else `device stream`.
- protocol_rows: in the device paths of DEVICE_KINDS (libs/{sportiduino,sfr,srpid,huichang}, modules/{sportident,sfr,sportiduino,srpid,rfid_impinj,huichang}) a function without I/O calls gets a row (call `<protocol>`, direction decode/encode/both) when it has a non-empty bytes literal, `int.from_bytes`, `.to_bytes`, or byte arithmetic: `& | ^ << >>` with a hex mask or on an indexed value with an int, and, beyond the original list, `+ - * // %` on an indexed value with an int. encode = `.to_bytes` or a bytes literal that is not compared; decode = the rest. Named upper-case int constants referenced there are byte-constants.
- host: a host or URL value is reported with kind url; newline and quotechar as delimiter.

Key numbers (from the script):
- functions with I/O: 113; I/O calls: 167; hard-coded values: 277.
- per format and direction: `{"CSV": {"read": 3}, "HID": {"device": 1}, "HTTP": {"both": 1, "read": 1, "write": 1}, "Huichang serial": {"decode": 2, "encode": 1, "read": 1, "write": 1}, "INI": {"both": 2}, "Impinj RFID": {"device": 1}, "JSON": {"read": 6, "write": 6}, "PO": {"read": 1}, "SFR HID": {"decode": 7, "read": 1}, "SPORTident lib": {"device": 1}, "SPORTident serial": {"decode": 1}, "SRPID serial": {"both": 1, "decode": 3, "encode": 1, "read": 2, "write": 1}, "Sportiduino serial": {"both": 1, "decode": 2, "encode": 3, "read": 2, "write": 1}, "XML": {"read": 2, "write": 5}, "audio": {"read": 1}, "binary file": {"read": 3, "write": 6}, "docx": {"both": 1}, "file system": {"write": 1}, "gzip": {"read": 2}, "jinja2": {"both": 2}, "printer": {"device": 7}, "serial": {"device": 4}, "socket": {"both": 2, "read": 2, "write": 3}, "struct": {"both": 1, "read": 1, "write": 1}, "text file": {"both": 1, "read": 24, "unknown": 2, "write": 5}}`.
- per value kind: `{"baudrate": 3, "byte-constant": 80, "delimiter": 2, "encoding": 42, "extension": 14, "offset-or-width": 98, "other": 18, "struct-format": 3, "timeout": 13, "url": 4}`.
- formats without a reader: ['SPORTident serial', 'file system']; without a writer: ['CSV', 'PO', 'SFR HID', 'SPORTident serial', 'audio', 'gzip']; device-only: ['HID', 'Impinj RFID', 'SPORTident lib', 'printer', 'serial'].
- contexts (modules) without a reader: ['IOF XML', 'SFR', 'SPORTident', 'lib:telegram']; without a writer: ['WinOrient', 'lib:ocad'].
- files that `ast` could not parse: 0.

Limits:
- Static names only: methods of objects are found by receiver name (DEVICE_VOCABULARY), `tree.write` through the companion rules; other receivers are missed.
- `.open` counts only on receivers named like a path; `json.loads`/`dumps` are counted although they work on strings.
- Protocol rows are heuristics: a decoder that only slices (`data[5:9]`) and no I/O or arithmetic gets no row. Receivers outside DEVICE_VOCABULARY are missed.
- A value is attributed to the function that contains it, not to the call it feeds.
- Writes through file objects received as parameters (e.g. `file.write` in a dump function), directory listing (`os.listdir`), file-choosing dialogs and `webbrowser` are not I/O sites.
- An int compared with `==`/`<` is reported as `byte-constant` unless the other side is `len(...)`; plain index comparisons are therefore included.
- Lists of formats without a reader or writer are not judgements: they only show that no site of that kind was found.
