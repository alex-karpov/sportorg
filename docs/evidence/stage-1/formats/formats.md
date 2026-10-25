# Formats: I/O of files and devices in pysport@b548c35

Produced by `scripts/archaeology/formats.py` (command in `commands.txt`).

## Functions

| format | direction | module | function | calls | values |
|---|---|---|---|---|---|
| audio | read | sportorg.common.audio | play | `playsound3.playsound` [код: pysport@b548c35 sportorg/common/audio.py:18] | - |
| text file | read | sportorg.config | commit_version | `.read_text` [код: pysport@b548c35 sportorg/config.py:87] | encoding="utf-8" |
| printer | device | sportorg.gui.dialogs.print_properties | PrintPropertiesDialog.set_values | `PySide2.QtPrintSupport.QPrinter` [код: pysport@b548c35 sportorg/gui/dialogs/print_properties.py:133] | - |
| printer | device | sportorg.gui.dialogs.print_properties | PrintPropertiesDialog.select_printer | `PySide2.QtPrintSupport.QPrinter` [код: pysport@b548c35 sportorg/gui/dialogs/print_properties.py:151] `PySide2.QtPrintSupport.QPrintDialog` [код: pysport@b548c35 sportorg/gui/dialogs/print_properties.py:152] | - |
| text file | write | sportorg.gui.dialogs.rent_cards_dialog | RentCardsDialog.apply_changes_impl | `open` [код: pysport@b548c35 sportorg/gui/dialogs/rent_cards_dialog.py:81] | encoding="utf-8", other="w" |
| docx, text file | both | sportorg.gui.dialogs.report_dialog | ReportDialog.apply_changes_impl | `docxtpl.DocxTemplate` [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:213] `.save` [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:232] `codecs.open` [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:258] `codecs.open` [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:285] | byte-constant=2, byte-constant=3, byte-constant=4, extension=".docx", extension="MS Word file (*.docx)", extension=".csv", extension="CSV file (*.csv)", encoding="utf-8", other="w", extension="HTML file (*.html)", encoding="utf-8", other="w" |
| text file | read | sportorg.gui.main | Application.set_status_comments | `open` [код: pysport@b548c35 sportorg/gui/main.py:64] `open` [код: pysport@b548c35 sportorg/gui/main.py:72] | encoding="utf-8", encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_countries | `open` [код: pysport@b548c35 sportorg/gui/main.py:81] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_groups | `open` [код: pysport@b548c35 sportorg/gui/main.py:90] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_names | `open` [код: pysport@b548c35 sportorg/gui/main.py:99] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_middle_names | `open` [код: pysport@b548c35 sportorg/gui/main.py:108] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_regions | `open` [код: pysport@b548c35 sportorg/gui/main.py:117] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_ranking | `open` [код: pysport@b548c35 sportorg/gui/main.py:126] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_ranking_ardf | `open` [код: pysport@b548c35 sportorg/gui/main.py:135] | encoding="utf-8" |
| text file | read | sportorg.gui.main | Application.set_rent_cards | `open` [код: pysport@b548c35 sportorg/gui/main.py:144] | encoding="utf-8" |
| text file | both | sportorg.gui.main_window | MainWindow.lock_file | `open` [код: pysport@b548c35 sportorg/gui/main_window.py:1158] `open` [код: pysport@b548c35 sportorg/gui/main_window.py:1176] | extension=".lock", other="w" |
| text file | read | sportorg.gui.menu.actions | RecoverySportorgHtmlAction.execute | `open` [код: pysport@b548c35 sportorg/gui/menu/actions.py:397] | extension="SportOrg HTML report (*.html)" |
| text file | unknown | sportorg.gui.menu.actions | ImportSportOrgAction.execute | `open` [код: pysport@b548c35 sportorg/gui/menu/actions.py:949] `open` [код: pysport@b548c35 sportorg/gui/menu/actions.py:956] | extension="SportOrg (*.json)", encoding="utf-8", encoding="utf-8" |
| INI | both | sportorg.language | _get_conf_locale_old | `configparser.ConfigParser` [код: pysport@b548c35 sportorg/language.py:16] `.read` [код: pysport@b548c35 sportorg/language.py:18] | - |
| JSON, text file | read | sportorg.language | _get_conf_locale | `.read_text` [код: pysport@b548c35 sportorg/language.py:31] `json.loads` [код: pysport@b548c35 sportorg/language.py:31] | encoding="utf-8" |
| PO | read | sportorg.language | generate_mo | `polib.pofile` [код: pysport@b548c35 sportorg/language.py:44] | extension=".po", extension=".mo" |
| Huichang serial | write | sportorg.libs.huichang.huichang | Huichang.send_command | `_serial.write` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:87] | offset-or-width=1, byte-constant=b"\xaa\xbb\xff" |
| Huichang serial | encode | sportorg.libs.huichang.huichang | Huichang._set_master_mode | `<protocol>` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:107] | byte-constant=b"\x02", byte-constant=b"\x01", byte-constant=b"\x28" |
| serial | device | sportorg.libs.huichang.huichang | Huichang._connect_master_station | `serial.Serial` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:132] | baudrate=9600, timeout=3 |
| Huichang serial | read | sportorg.libs.huichang.huichang | Huichang._read_response | `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:159] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:166] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:167] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:172] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:173] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:174] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:175] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:181] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:191] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:192] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:204] `serial.read` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:205] | byte-constant=b"\xaa\xbb\xff", byte-constant=b"\xaa\xbb\xff", byte-constant=b"\xaa\xbb\xff", offset-or-width=2, byte-constant=b"\x1b", byte-constant=b"\x40", byte-constant=b"\x20", byte-constant=b"\x0d", byte-constant=b"\x0a", byte-constant=b"\x1b", byte-constant=b"\x20", byte-constant=b"\x60", offset-or-width=1, byte-constant=b"\xa1" |
| Huichang serial | decode | sportorg.libs.huichang.huichang | Huichang._process_response | `<protocol>` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:237] | byte-constant=b"\x0a", byte-constant=b"\x28", byte-constant=b"\xcc", byte-constant=b"\xee", byte-constant=b"\x20", byte-constant=b"\x60", offset-or-width=4, offset-or-width=5, offset-or-width=9, offset-or-width=10, offset-or-width=14, offset-or-width=15, offset-or-width=18, offset-or-width=18, offset-or-width=4, offset-or-width=1, offset-or-width=4, byte-constant=b"\x20", timeout=0.2, byte-constant=b"\xa1", byte-constant=b"\xa1" |
| Huichang serial | decode | sportorg.libs.huichang.huichang | Huichang.crc8 | `<protocol>` [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:294] | byte-constant=0xFF, offset-or-width=8, byte-constant=0x80, byte-constant=0xFF, offset-or-width=1, byte-constant=0xFF, offset-or-width=1, byte-constant=0x00 |
| XML | write | sportorg.libs.iof.iof | BaseElement.write | `.write` [код: pysport@b548c35 sportorg/libs/iof/iof.py:56] | - |
| XML | read | sportorg.libs.iof.parser | parse | `xml.etree.ElementTree.parse` [код: pysport@b548c35 sportorg/libs/iof/parser.py:15] | url="http://www.orienteering.org/datastandard/3.0", url="http://orgeo.ru/iof-xml-extensions/3.0" |
| file object (parameter), text file | read | sportorg.libs.ocad.ocad | ClassesV8.parse | `open` [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:72] `file.readlines` [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:77] | encoding="windows-1251" |
| XML | read | sportorg.libs.ocad.ocad | IofXMLv3.parse | `xml.etree.ElementTree.parse` [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:202] | - |
| JSON, text file | both | sportorg.libs.settings | save_settings | `.open` [код: pysport@b548c35 sportorg/libs/settings/__init__.py:16] `json.dump` [код: pysport@b548c35 sportorg/libs/settings/__init__.py:17] | encoding="utf-8" |
| JSON, text file | read | sportorg.libs.settings | _load_settings | `.open` [код: pysport@b548c35 sportorg/libs/settings/__init__.py:39] `json.load` [код: pysport@b548c35 sportorg/libs/settings/__init__.py:40] | encoding="utf-8" |
| binary file | write | sportorg.libs.sfr.sfrreader | SFRReader.__init__ | `open` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:74] | other="ab" |
| SFR HID | decode | sportorg.libs.sfr.sfrreader | SFRReader.check_sum | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:100] | byte-constant=0xFF, byte-constant=0x100 |
| SFR HID | decode | sportorg.libs.sfr.sfrreader | SFRReader._read_bib | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] | offset-or-width=200, offset-or-width=40000, offset-or-width=5, offset-or-width=6, offset-or-width=7 |
| SFR HID | decode | sportorg.libs.sfr.sfrreader | SFRReader._read_data_counter | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:255] | offset-or-width=1, offset-or-width=5 |
| HID, SFR HID | both | sportorg.libs.sfr.sfrreader | SFRReader._connect_reader | `pywinusb.hid.HidDeviceFilter` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:281] `device.set_raw_data_handler` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:296] | byte-constant=0x2047, byte-constant=0x301 |
| SFR HID | decode | sportorg.libs.sfr.sfrreader | SFRReader._decode_time | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:310] | offset-or-width=2, offset-or-width=10, offset-or-width=16, offset-or-width=10, offset-or-width=16, offset-or-width=10, offset-or-width=16, offset-or-width=2, byte-constant=23, byte-constant=59 |
| SFR HID | decode | sportorg.libs.sfr.sfrreader | SFRReader._decode_time_subseconds | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:339] | offset-or-width=2, offset-or-width=16, offset-or-width=10, offset-or-width=16, offset-or-width=10, offset-or-width=16, offset-or-width=2, offset-or-width=16, byte-constant=59, byte-constant=9, byte-constant=20, offset-or-width=20, byte-constant=10, offset-or-width=10, byte-constant=10, byte-constant=4, offset-or-width=100000 |
| SFR HID | decode | sportorg.libs.sfr.sfrximporter | import_sfrx | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:49] | offset-or-width=1, offset-or-width=1, offset-or-width=1, offset-or-width=2, offset-or-width=4 |
| SFR HID | decode | sportorg.libs.sfr.sfrximporter | convert_bib | `<protocol>` [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:217] | byte-constant=10000 |
| text file | read | sportorg.libs.sfr.sfrxparser | SFRXParser.parse | `codecs.open` [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:18] | encoding="UTF-8", other="r" |
| Sportiduino serial | decode | sportorg.libs.sportiduino.sportiduino | Sportiduino.Version.__init__ | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:126] | byte-constant=100, byte-constant=104, offset-or-width=100, offset-or-width=100, offset-or-width=1, offset-or-width=6, byte-constant=0x0F, offset-or-width=1, offset-or-width=2, byte-constant=0x03 |
| Sportiduino serial | decode | sportorg.libs.sportiduino.sportiduino | Sportiduino.Config.unpack | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:156] | offset-or-width=15 |
| Sportiduino serial | write | sportorg.libs.sportiduino.sportiduino | Sportiduino.SerialProtocol.send_command | `serial.write` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:189] | offset-or-width=28 |
| Sportiduino serial | read | sportorg.libs.sportiduino.sportiduino | Sportiduino.SerialProtocol._read_response | `serial.read` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:204] `serial.read` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:215] `serial.read` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:216] `serial.read` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:230] `serial.read` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:231] | offset-or-width=0x1E, offset-or-width=0x1E, offset-or-width=28, offset-or-width=1 |
| Sportiduino serial | encode | sportorg.libs.sportiduino.sportiduino | Sportiduino.init_card | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:436] | byte-constant=b"\x00\x00\x00\x00", byte-constant=b"\x00\x00\x00\x00", offset-or-width=5, offset-or-width=5, byte-constant=b"\x44" |
| Sportiduino serial | encode | sportorg.libs.sportiduino.sportiduino | Sportiduino.enable_continuous_read | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:542] | byte-constant=b"\x01" |
| Sportiduino serial | encode | sportorg.libs.sportiduino.sportiduino | Sportiduino.disable_continuous_read | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:546] | byte-constant=b"\x00" |
| Sportiduino serial, serial | both | sportorg.libs.sportiduino.sportiduino | Sportiduino._connect_master_station | `serial.Serial` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:591] `_serial.reset_input_buffer` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:600] | baudrate=38400, timeout=3, timeout=2 |
| Sportiduino serial | both | sportorg.libs.sportiduino.sportiduino | Sportiduino._to_str | `<protocol>` [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:660] | offset-or-width=8, offset-or-width=1, byte-constant=0xFF, offset-or-width=8 |
| SRPID serial, serial | both | sportorg.libs.srpid.srpid | SRPid._conn_m_station | `serial.Serial` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:63] `_serial.reset_input_buffer` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:69] | baudrate=9600, timeout=5 |
| SRPID serial | decode | sportorg.libs.srpid.srpid | SRPid.read_ver | `<protocol>` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:83] | byte-constant=b"\x32", byte-constant=b"\x72" |
| SRPID serial | write | sportorg.libs.srpid.srpid | SRPid._send_command | `_serial.write` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:108] | byte-constant=b"\0", byte-constant=b"\xce", byte-constant=b"\xc1", byte-constant=b"\0", byte-constant=b"\0", byte-constant=b"\0", byte-constant=b"\0", byte-constant=b"\0", byte-constant=b"\0", byte-constant=b"\xce" |
| SRPID serial | decode | sportorg.libs.srpid.srpid | SRPid.read_chip | `<protocol>` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:134] | byte-constant=b"\x2f", byte-constant=b"\x70" |
| SRPID serial | read | sportorg.libs.srpid.srpid | SRPid._get_response | `_serial.read` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:149] `_serial.read` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:158] `_serial.read` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:159] `_serial.read` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:161] `_serial.read` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:162] | byte-constant=b"\xec" |
| SRPID serial | encode | sportorg.libs.srpid.srpid | SRPid.beep_ok | `<protocol>` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:175] | byte-constant=b"\x36" |
| SRPID serial | both | sportorg.libs.srpid.srpid | SRPid._to_str | `<protocol>` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:206] | offset-or-width=8, offset-or-width=1, byte-constant=0xFF, offset-or-width=8 |
| SRPID serial | decode | sportorg.libs.srpid.srpid | SRPid._preprocess_response | `<protocol>` [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:216] | byte-constant=b"\x76", byte-constant=b"\x01", byte-constant=b"\x02", byte-constant=b"\x03", byte-constant=b"\x75" |
| HTTP | write | sportorg.libs.telegram.telegram | Telegram.send_message | `requests.post` [код: pysport@b548c35 sportorg/libs/telegram/telegram.py:27] | url="sendMessage" |
| jinja2, text file | both | sportorg.libs.template.template | get_text_from_path | `open` [код: pysport@b548c35 sportorg/libs/template/template.py:42] `jinja2.Template` [код: pysport@b548c35 sportorg/libs/template/template.py:45] `.render` [код: pysport@b548c35 sportorg/libs/template/template.py:46] | encoding="utf-8" |
| jinja2 | both | sportorg.libs.template.template | get_text_from_template | `jinja2.Environment` [код: pysport@b548c35 sportorg/libs/template/template.py:54] `jinja2.FileSystemLoader` [код: pysport@b548c35 sportorg/libs/template/template.py:54] `.render` [код: pysport@b548c35 sportorg/libs/template/template.py:61] | - |
| binary file | read | sportorg.libs.winorient.wdb | parse_wdb | `open` [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1207] | other="rb" |
| binary file | write | sportorg.libs.winorient.wdb | write_wdb | `open` [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1216] | other="wb" |
| CSV, text file | read | sportorg.libs.winorient.wo | CSVReader.parse | `open` [код: pysport@b548c35 sportorg/libs/winorient/wo.py:13] `csv.reader` [код: pysport@b548c35 sportorg/libs/winorient/wo.py:14] | encoding="cp1251", delimiter=";" |
| text file | read | sportorg.models.constant | _read_config_items | `.open` [код: pysport@b548c35 sportorg/models/constant.py:13] | encoding="utf-8" |
| gzip | read | sportorg.modules.backup.file | is_gzip_file | `gzip.open` [код: pysport@b548c35 sportorg/modules/backup/file.py:15] | - |
| text file | unknown | sportorg.modules.backup.file | File._backup | `open` [код: pysport@b548c35 sportorg/modules/backup/file.py:42] `open` [код: pysport@b548c35 sportorg/modules/backup/file.py:50] | encoding="utf-8", encoding="utf-8" |
| JSON, file object (parameter) | write | sportorg.modules.backup.json | dump | `orjson.dumps` [код: pysport@b548c35 sportorg/modules/backup/json.py:25] `file.write` [код: pysport@b548c35 sportorg/modules/backup/json.py:27] `file.write` [код: pysport@b548c35 sportorg/modules/backup/json.py:29] | - |
| JSON, file object (parameter) | read | sportorg.modules.backup.json | get_races_from_file | `file.read` [код: pysport@b548c35 sportorg/modules/backup/json.py:52] `orjson.loads` [код: pysport@b548c35 sportorg/modules/backup/json.py:52] `file.read` [код: pysport@b548c35 sportorg/modules/backup/json.py:54] `orjson.loads` [код: pysport@b548c35 sportorg/modules/backup/json.py:54] | - |
| file object (parameter) | write | sportorg.modules.backup.sfr_results_board | dump | `file.write` [код: pysport@b548c35 sportorg/modules/backup/sfr_results_board.py:18] `file.write` [код: pysport@b548c35 sportorg/modules/backup/sfr_results_board.py:20] | delimiter="\t", encoding="utf-8" |
| INI | both | sportorg.modules.configs.configs | Config.__init__ | `configparser.ConfigParser` [код: pysport@b548c35 sportorg/modules/configs/configs.py:76] | - |
| XML, binary file | write | sportorg.modules.iof.iof_xml | export_result_list | `.write` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:38] `open` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:38] | encoding="UTF-8", other="wb" |
| XML, binary file | write | sportorg.modules.iof.iof_xml | export_entry_list | `.write` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:46] `open` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:46] | encoding="UTF-8", other="wb" |
| XML, binary file | write | sportorg.modules.iof.iof_xml | export_start_list | `.write` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:54] `open` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:54] | encoding="UTF-8", other="wb" |
| XML, binary file | write | sportorg.modules.iof.iof_xml | export_competitor_list | `.write` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:62] `open` [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:62] | encoding="UTF-8", other="wb" |
| HTTP | both | sportorg.modules.live.live | create_session | `aiohttp.ClientSession` [код: pysport@b548c35 sportorg/modules/live/live.py:17] `aiohttp.ClientTimeout` [код: pysport@b548c35 sportorg/modules/live/live.py:17] | - |
| JSON | write | sportorg.modules.live.orgeo | Orgeo.send | `json.dumps` [код: pysport@b548c35 sportorg/modules/live/orgeo.py:50] | encoding="utf-8" |
| JSON | write | sportorg.modules.plugins.manager | _json_dumps | `json.dumps` [код: pysport@b548c35 sportorg/modules/plugins/manager.py:131] | - |
| JSON | write | sportorg.modules.plugins.manager | _stable_json | `json.dumps` [код: pysport@b548c35 sportorg/modules/plugins/manager.py:135] | - |
| JSON | read | sportorg.modules.plugins.manager | PluginProcess._read_loop | `json.loads` [код: pysport@b548c35 sportorg/modules/plugins/manager.py:668] | - |
| printer | device | sportorg.modules.printing.printing | PrintProcess.run | `PySide2.QtPrintSupport.QPrinter` [код: pysport@b548c35 sportorg/modules/printing/printing.py:61] | byte-constant=5, byte-constant=5 |
| printer | device | sportorg.modules.printing.printout_split | SportorgPrinter.__init__ | `win32print.GetDefaultPrinter` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:16] `win32ui.CreateDC` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:18] | - |
| printer | device | sportorg.modules.printing.printout_split | SportorgPrinter.print_line | `win32ui.CreateFont` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:47] | - |
| printer | device | sportorg.modules.printing.printout_split | SportorgPrinter.print_bib_line | `win32ui.CreateFont` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:88] | - |
| printer | device | sportorg.modules.printing.printout_split | SportorgPrinter.print_penalty_line | `win32ui.CreateFont` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:112] `win32ui.CreateFont` [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:129] | offset-or-width=2 |
| CSV, text file | read | sportorg.modules.recovery.recovery_orgeo_finish_csv | recovery | `open` [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:47] `csv.reader` [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:48] | encoding="cp1251", delimiter=";", delimiter="\|", offset-or-width=9, offset-or-width=4, offset-or-width=2, offset-or-width=3, offset-or-width=9, offset-or-width=9, offset-or-width=5, offset-or-width=5, offset-or-width=7 |
| CSV, text file | read | sportorg.modules.recovery.recovery_si_master_csv | recovery | `open` [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:42] `csv.reader` [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:43] | delimiter=";", offset-or-width=2, encoding="cp1251", offset-or-width=45, offset-or-width=2, offset-or-width=15, offset-or-width=21, offset-or-width=44, offset-or-width=44, offset-or-width=44, offset-or-width=44 |
| gzip, text file | read | sportorg.modules.recovery.recovery_sportorg_html | recovery | `open` [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:20] `gzip.GzipFile` [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:26] | other="r", offset-or-width=-2, offset-or-width=12, encoding="utf-8", offset-or-width=11 |
| text file | write | sportorg.modules.recovery.recovery_sportorg_html | save_to_tmp_file | `open` [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:44] | extension=.json, encoding="utf-8", other="w" |
| text file | read | sportorg.modules.recovery.recovery_sportorg_si_log | recovery | `open` [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:50] | offset-or-width=2 |
| Impinj RFID | device | sportorg.modules.rfid_impinj.rfid_impinj | ImpinjThread.run | `pyImpinj.ImpinjR2KReader` [код: pysport@b548c35 sportorg/modules/rfid_impinj/rfid_impinj.py:53] | timeout=0.1, timeout=1 |
| text file | write | sportorg.modules.sfr.sfrxexporter | export_sfrx | `open` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] | delimiter="", encoding="utf-8", extension=".sfrx", other="w", extension=".sfrx" |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_header | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:83] | - |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_days | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:101] | - |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_descriptions | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:108] | - |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_clubs | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:115] | - |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_groups | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:142] | offset-or-width=5 |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_teams | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:151] | offset-or-width=5 |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_courses | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:180] | offset-or-width=5, offset-or-width=2 |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_controls | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:204] | offset-or-width=5 |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_competitors | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:265] | offset-or-width=5 |
| file object (parameter) | write | sportorg.modules.sfr.sfrxexporter | _write_splits | `f.write` [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:338] | offset-or-width=1, offset-or-width=1, offset-or-width=5 |
| text file | write | sportorg.modules.sportident.backup | BackupProcess.run | `open` [код: pysport@b548c35 sportorg/modules/sportident/backup.py:20] | other="a", extension="si{}.log" |
| SPORTident lib | device | sportorg.modules.sportident.sireader | SIReaderThread.run | `sportident.SIReaderReadout` [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:52] `sportident.SIReaderSRR` [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:55] `sportident.SIReaderControl` [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:61] | timeout=1 |
| SPORTident serial | decode | sportorg.modules.sportident.sireader | ResultThread._check_data | `<protocol>` [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:137] | offset-or-width=12, offset-or-width=24, offset-or-width=12, offset-or-width=3600, offset-or-width=12 |
| serial | device | sportorg.modules.sportident.sireader | SIReaderClient.get_ports | `serial.tools.list_ports.comports` [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:263] | - |
| socket | write | sportorg.modules.teamwork.client | ClientSender.__call__ | `conn.sendall` [код: pysport@b548c35 sportorg/modules/teamwork/client.py:25] | timeout=0.1 |
| JSON, socket | read | sportorg.modules.teamwork.client | ClientReceiver.__call__ | `conn.recv` [код: pysport@b548c35 sportorg/modules/teamwork/client.py:43] `orjson.loads` [код: pysport@b548c35 sportorg/modules/teamwork/client.py:64] | offset-or-width=1024 |
| socket | both | sportorg.modules.teamwork.client | ClientThread.run | `socket.socket` [код: pysport@b548c35 sportorg/modules/teamwork/client.py:114] | timeout=1 |
| JSON | write | sportorg.modules.teamwork.command | Command.get_packet | `orjson.dumps` [код: pysport@b548c35 sportorg/modules/teamwork/command.py:32] | - |
| text file | read | sportorg.modules.teamwork.crypto | load_teamwork_key_from_file | `.read_text` [код: pysport@b548c35 sportorg/modules/teamwork/crypto.py:57] | encoding="utf-8" |
| struct | both | sportorg.modules.teamwork.packet_header | Header.<class> | `struct.calcsize` [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:86] | struct-format="=2s2H36sLQ" |
| struct | read | sportorg.modules.teamwork.packet_header | Header.unpack_header | `struct.unpack` [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:123] | struct-format="=2s2H36sLQ" |
| struct | write | sportorg.modules.teamwork.packet_header | Header.pack_header | `struct.pack` [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:147] | struct-format="=2s2H36sLQ", encoding="ascii" |
| socket | read | sportorg.modules.teamwork.server | ServerReceiver.__call__ | `sock.recv` [код: pysport@b548c35 sportorg/modules/teamwork/server.py:39] | offset-or-width=1024 |
| JSON, socket | both | sportorg.modules.teamwork.server | ServerReceiver._process_packet | `orjson.loads` [код: pysport@b548c35 sportorg/modules/teamwork/server.py:75] `sock.sendall` [код: pysport@b548c35 sportorg/modules/teamwork/server.py:99] | - |
| socket | write | sportorg.modules.teamwork.server | ServerSender.__call__ | `sock.sendall` [код: pysport@b548c35 sportorg/modules/teamwork/server.py:157] | timeout=0.1 |
| socket | both | sportorg.modules.teamwork.server | ServerThread.run | `socket.socket` [код: pysport@b548c35 sportorg/modules/teamwork/server.py:415] | timeout=1 |
| HTTP | read | sportorg.modules.updater.checker | get_last_tag_name | `requests.get` [код: pysport@b548c35 sportorg/modules/updater/checker.py:11] | timeout=5, url="https://api.github.com/repos/sportorg/pysport/releases/latest" |
| binary file | read | sportorg.modules.winorient.wdb | WinOrientBinary._read_file | `open` [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:65] | other="rb" |
| file system | write | sportorg.paths | seed_if_first_run | `shutil.copytree` [код: pysport@b548c35 sportorg/paths.py:155] | - |
| binary file | read | sportorg.utils.text | detect_encoding | `open` [код: pysport@b548c35 sportorg/utils/text.py:6] | other="rb", encoding="UTF-8-SIG", encoding="utf-8", encoding="windows-1251", encoding="utf-8" |

## Values

| kind | value | origin | function | tag |
|---|---|---|---|---|
| encoding | `"utf-8"` | keyword encoding of .read_text | sportorg.config.commit_version | [код: pysport@b548c35 sportorg/config.py:87] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.dialogs.rent_cards_dialog.RentCardsDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/rent_cards_dialog.py:81] |
| other | `"w"` | mode of open | sportorg.gui.dialogs.rent_cards_dialog.RentCardsDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/rent_cards_dialog.py:81] |
| byte-constant | `2` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:159] |
| byte-constant | `3` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:167] |
| byte-constant | `4` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:181] |
| extension | `".docx"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:210] |
| extension | `"MS Word file (*.docx)"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:226] |
| extension | `".csv"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:235] |
| extension | `"CSV file (*.csv)"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:251] |
| encoding | `"utf-8"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:258] |
| other | `"w"` | mode of codecs.open | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:258] |
| extension | `"HTML file (*.html)"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:278] |
| encoding | `"utf-8"` | literal | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:285] |
| other | `"w"` | mode of codecs.open | sportorg.gui.dialogs.report_dialog.ReportDialog.apply_changes_impl | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:285] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_status_comments | [код: pysport@b548c35 sportorg/gui/main.py:64] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_status_comments | [код: pysport@b548c35 sportorg/gui/main.py:72] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_countries | [код: pysport@b548c35 sportorg/gui/main.py:81] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_groups | [код: pysport@b548c35 sportorg/gui/main.py:90] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_names | [код: pysport@b548c35 sportorg/gui/main.py:99] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_middle_names | [код: pysport@b548c35 sportorg/gui/main.py:108] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_regions | [код: pysport@b548c35 sportorg/gui/main.py:117] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_ranking | [код: pysport@b548c35 sportorg/gui/main.py:126] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_ranking_ardf | [код: pysport@b548c35 sportorg/gui/main.py:135] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.gui.main.Application.set_rent_cards | [код: pysport@b548c35 sportorg/gui/main.py:144] |
| extension | `".lock"` | literal | sportorg.gui.main_window.MainWindow.lock_file | [код: pysport@b548c35 sportorg/gui/main_window.py:1156] |
| other | `"w"` | mode of open | sportorg.gui.main_window.MainWindow.lock_file | [код: pysport@b548c35 sportorg/gui/main_window.py:1176] |
| extension | `"SportOrg HTML report (*.html)"` | literal | sportorg.gui.menu.actions.RecoverySportorgHtmlAction.execute | [код: pysport@b548c35 sportorg/gui/menu/actions.py:390] |
| extension | `"SportOrg (*.json)"` | literal | sportorg.gui.menu.actions.ImportSportOrgAction.execute | [код: pysport@b548c35 sportorg/gui/menu/actions.py:929] |
| encoding | `"utf-8"` | literal | sportorg.gui.menu.actions.ImportSportOrgAction.execute | [код: pysport@b548c35 sportorg/gui/menu/actions.py:944] |
| encoding | `"utf-8"` | literal | sportorg.gui.menu.actions.ImportSportOrgAction.execute | [код: pysport@b548c35 sportorg/gui/menu/actions.py:954] |
| encoding | `"utf-8"` | keyword encoding of .read_text | sportorg.language._get_conf_locale | [код: pysport@b548c35 sportorg/language.py:31] |
| extension | `".po"` | literal | sportorg.language.generate_mo | [код: pysport@b548c35 sportorg/language.py:44] |
| extension | `".mo"` | literal | sportorg.language.generate_mo | [код: pysport@b548c35 sportorg/language.py:45] |
| offset-or-width | `1` | literal | sportorg.libs.huichang.huichang.Huichang.send_command | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:80] |
| byte-constant | `b"\xaa\xbb\xff"` | constant START_SEQUENCE | sportorg.libs.huichang.huichang.Huichang.send_command | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:29] |
| byte-constant | `b"\x02"` | literal | sportorg.libs.huichang.huichang.Huichang._set_master_mode | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:107] |
| byte-constant | `b"\x01"` | literal | sportorg.libs.huichang.huichang.Huichang._set_master_mode | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:109] |
| byte-constant | `b"\x28"` | constant CMD_SET_MASTER_MODE | sportorg.libs.huichang.huichang.Huichang._set_master_mode | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:33] |
| baudrate | `9600` | keyword baudrate of serial.Serial | sportorg.libs.huichang.huichang.Huichang._connect_master_station | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:132] |
| timeout | `3` | keyword timeout of serial.Serial | sportorg.libs.huichang.huichang.Huichang._connect_master_station | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:132] |
| byte-constant | `b"\xaa\xbb\xff"` | constant START_SEQUENCE | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:29] |
| byte-constant | `b"\xaa\xbb\xff"` | constant START_SEQUENCE | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:29] |
| byte-constant | `b"\xaa\xbb\xff"` | constant START_SEQUENCE | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:29] |
| offset-or-width | `2` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:167] |
| byte-constant | `b"\x1b"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:171] |
| byte-constant | `b"\x40"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:172] |
| byte-constant | `b"\x20"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:173] |
| byte-constant | `b"\x0d"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:174] |
| byte-constant | `b"\x0a"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:175] |
| byte-constant | `b"\x1b"` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:182] |
| byte-constant | `b"\x20"` | constant CMD_CARD_DATA | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:32] |
| byte-constant | `b"\x60"` | constant CMD_CONTACT_CARD_DATA | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:35] |
| offset-or-width | `1` | literal | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:204] |
| byte-constant | `b"\xa1"` | constant CMD_CARD_BATTERY_LEVEL | sportorg.libs.huichang.huichang.Huichang._read_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:38] |
| byte-constant | `b"\x0a"` | constant CMD_TIME_SYNC | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:31] |
| byte-constant | `b"\x28"` | constant CMD_SET_MASTER_MODE | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:33] |
| byte-constant | `b"\xcc"` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:237] |
| byte-constant | `b"\xee"` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:240] |
| byte-constant | `b"\x20"` | constant CMD_CARD_DATA | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:32] |
| byte-constant | `b"\x60"` | constant CMD_CONTACT_CARD_DATA | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:35] |
| offset-or-width | `4` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:244] |
| offset-or-width | `5` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:245] |
| offset-or-width | `9` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:245] |
| offset-or-width | `10` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:246] |
| offset-or-width | `14` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:246] |
| offset-or-width | `15` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:247] |
| offset-or-width | `18` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:247] |
| offset-or-width | `18` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:250] |
| offset-or-width | `4` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:250] |
| offset-or-width | `1` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:252] |
| offset-or-width | `4` | literal | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:252] |
| byte-constant | `b"\x20"` | constant CMD_CARD_DATA | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:32] |
| timeout | `0.2` | keyword timeout of self._read_response | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:258] |
| byte-constant | `b"\xa1"` | constant CMD_CARD_BATTERY_LEVEL | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:38] |
| byte-constant | `b"\xa1"` | constant CMD_CARD_BATTERY_LEVEL | sportorg.libs.huichang.huichang.Huichang._process_response | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:38] |
| byte-constant | `0xFF` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:289] |
| offset-or-width | `8` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:293] |
| byte-constant | `0x80` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:294] |
| byte-constant | `0xFF` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:295] |
| offset-or-width | `1` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:295] |
| byte-constant | `0xFF` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:297] |
| offset-or-width | `1` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:297] |
| byte-constant | `0x00` | literal | sportorg.libs.huichang.huichang.Huichang.crc8 | [код: pysport@b548c35 sportorg/libs/huichang/huichang.py:298] |
| url | `"http://www.orienteering.org/datastandard/3.0"` | literal | sportorg.libs.iof.parser.parse | [код: pysport@b548c35 sportorg/libs/iof/parser.py:12] |
| url | `"http://orgeo.ru/iof-xml-extensions/3.0"` | literal | sportorg.libs.iof.parser.parse | [код: pysport@b548c35 sportorg/libs/iof/parser.py:13] |
| encoding | `"windows-1251"` | literal | sportorg.libs.ocad.ocad.ClassesV8.parse | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:71] |
| encoding | `"utf-8"` | keyword encoding of .open | sportorg.libs.settings.save_settings | [код: pysport@b548c35 sportorg/libs/settings/__init__.py:16] |
| encoding | `"utf-8"` | keyword encoding of .open | sportorg.libs.settings._load_settings | [код: pysport@b548c35 sportorg/libs/settings/__init__.py:39] |
| other | `"ab"` | mode of open | sportorg.libs.sfr.sfrreader.SFRReader.__init__ | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:74] |
| byte-constant | `0xFF` | literal | sportorg.libs.sfr.sfrreader.SFRReader.check_sum | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:100] |
| byte-constant | `0x100` | literal | sportorg.libs.sfr.sfrreader.SFRReader.check_sum | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:101] |
| offset-or-width | `200` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] |
| offset-or-width | `40000` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] |
| offset-or-width | `5` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] |
| offset-or-width | `6` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] |
| offset-or-width | `7` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:250] |
| offset-or-width | `1` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_data_counter | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:255] |
| offset-or-width | `5` | literal | sportorg.libs.sfr.sfrreader.SFRReader._read_data_counter | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:255] |
| byte-constant | `0x2047` | constant VENDOR_ID | sportorg.libs.sfr.sfrreader.SFRReader._connect_reader | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:41] |
| byte-constant | `0x301` | constant PRODUCT_ID | sportorg.libs.sfr.sfrreader.SFRReader._connect_reader | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:42] |
| offset-or-width | `2` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:309] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:310] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:310] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:311] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:311] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:312] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:312] |
| offset-or-width | `2` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:312] |
| byte-constant | `23` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:314] |
| byte-constant | `59` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:314] |
| offset-or-width | `2` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:338] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:339] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:340] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:340] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:341] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:341] |
| offset-or-width | `2` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:341] |
| offset-or-width | `16` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:342] |
| byte-constant | `59` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:344] |
| byte-constant | `9` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:344] |
| byte-constant | `20` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:352] |
| offset-or-width | `20` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:356] |
| byte-constant | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:360] |
| offset-or-width | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:364] |
| byte-constant | `10` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:366] |
| byte-constant | `4` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:372] |
| offset-or-width | `100000` | literal | sportorg.libs.sfr.sfrreader.SFRReader._decode_time_subseconds | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:384] |
| offset-or-width | `1` | literal | sportorg.libs.sfr.sfrximporter.import_sfrx | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:23] |
| offset-or-width | `1` | literal | sportorg.libs.sfr.sfrximporter.import_sfrx | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:49] |
| offset-or-width | `1` | literal | sportorg.libs.sfr.sfrximporter.import_sfrx | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:138] |
| offset-or-width | `2` | literal | sportorg.libs.sfr.sfrximporter.import_sfrx | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:171] |
| offset-or-width | `4` | literal | sportorg.libs.sfr.sfrximporter.import_sfrx | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:174] |
| byte-constant | `10000` | literal | sportorg.libs.sfr.sfrximporter.convert_bib | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:214] |
| encoding | `"UTF-8"` | literal | sportorg.libs.sfr.sfrxparser.SFRXParser.parse | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:18] |
| other | `"r"` | mode of codecs.open | sportorg.libs.sfr.sfrxparser.SFRXParser.parse | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:18] |
| byte-constant | `100` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:120] |
| byte-constant | `104` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:120] |
| offset-or-width | `100` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:121] |
| offset-or-width | `100` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:122] |
| offset-or-width | `1` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:125] |
| offset-or-width | `6` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:125] |
| byte-constant | `0x0F` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:126] |
| offset-or-width | `1` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:126] |
| offset-or-width | `2` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:126] |
| byte-constant | `0x03` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Version.__init__ | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:127] |
| offset-or-width | `15` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.Config.unpack | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:156] |
| offset-or-width | `28` | constant MAX_DATA_LEN | sportorg.libs.sportiduino.sportiduino.Sportiduino.SerialProtocol.send_command | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:167] |
| offset-or-width | `0x1E` | constant OFFSET | sportorg.libs.sportiduino.sportiduino.Sportiduino.SerialProtocol._read_response | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:166] |
| offset-or-width | `0x1E` | constant OFFSET | sportorg.libs.sportiduino.sportiduino.Sportiduino.SerialProtocol._read_response | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:166] |
| offset-or-width | `28` | constant MAX_DATA_LEN | sportorg.libs.sportiduino.sportiduino.Sportiduino.SerialProtocol._read_response | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:167] |
| offset-or-width | `1` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.SerialProtocol._read_response | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:256] |
| byte-constant | `b"\x00\x00\x00\x00"` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.init_card | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:436] |
| byte-constant | `b"\x00\x00\x00\x00"` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.init_card | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:438] |
| offset-or-width | `5` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.init_card | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:444] |
| offset-or-width | `5` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.init_card | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:445] |
| byte-constant | `b"\x44"` | constant CMD_INIT_CARD | sportorg.libs.sportiduino.sportiduino.Sportiduino.init_card | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:61] |
| byte-constant | `b"\x01"` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.enable_continuous_read | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:542] |
| byte-constant | `b"\x00"` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino.disable_continuous_read | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:546] |
| baudrate | `38400` | keyword baudrate of serial.Serial | sportorg.libs.sportiduino.sportiduino.Sportiduino._connect_master_station | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:591] |
| timeout | `3` | keyword timeout of serial.Serial | sportorg.libs.sportiduino.sportiduino.Sportiduino._connect_master_station | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:591] |
| timeout | `2` | keyword timeout of self.read_version | sportorg.libs.sportiduino.sportiduino.Sportiduino._connect_master_station | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:617] |
| offset-or-width | `8` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino._to_str | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:661] |
| offset-or-width | `1` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino._to_str | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:664] |
| byte-constant | `0xFF` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino._to_str | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:665] |
| offset-or-width | `8` | literal | sportorg.libs.sportiduino.sportiduino.Sportiduino._to_str | [код: pysport@b548c35 sportorg/libs/sportiduino/sportiduino.py:665] |
| baudrate | `9600` | keyword baudrate of serial.Serial | sportorg.libs.srpid.srpid.SRPid._conn_m_station | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:63] |
| timeout | `5` | keyword timeout of serial.Serial | sportorg.libs.srpid.srpid.SRPid._conn_m_station | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:63] |
| byte-constant | `b"\x32"` | literal | sportorg.libs.srpid.srpid.SRPid.read_ver | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:83] |
| byte-constant | `b"\x72"` | literal | sportorg.libs.srpid.srpid.SRPid.read_ver | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:84] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:90] |
| byte-constant | `b"\xce"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:90] |
| byte-constant | `b"\xc1"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:93] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:95] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:96] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:97] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:98] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:99] |
| byte-constant | `b"\0"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:100] |
| byte-constant | `b"\xce"` | literal | sportorg.libs.srpid.srpid.SRPid._send_command | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:101] |
| byte-constant | `b"\x2f"` | literal | sportorg.libs.srpid.srpid.SRPid.read_chip | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:134] |
| byte-constant | `b"\x70"` | literal | sportorg.libs.srpid.srpid.SRPid.read_chip | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:135] |
| byte-constant | `b"\xec"` | literal | sportorg.libs.srpid.srpid.SRPid._get_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:152] |
| byte-constant | `b"\x36"` | literal | sportorg.libs.srpid.srpid.SRPid.beep_ok | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:175] |
| offset-or-width | `8` | literal | sportorg.libs.srpid.srpid.SRPid._to_str | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:207] |
| offset-or-width | `1` | literal | sportorg.libs.srpid.srpid.SRPid._to_str | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:210] |
| byte-constant | `0xFF` | literal | sportorg.libs.srpid.srpid.SRPid._to_str | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:211] |
| offset-or-width | `8` | literal | sportorg.libs.srpid.srpid.SRPid._to_str | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:211] |
| byte-constant | `b"\x76"` | literal | sportorg.libs.srpid.srpid.SRPid._preprocess_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:216] |
| byte-constant | `b"\x01"` | literal | sportorg.libs.srpid.srpid.SRPid._preprocess_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:217] |
| byte-constant | `b"\x02"` | literal | sportorg.libs.srpid.srpid.SRPid._preprocess_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:219] |
| byte-constant | `b"\x03"` | literal | sportorg.libs.srpid.srpid.SRPid._preprocess_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:221] |
| byte-constant | `b"\x75"` | literal | sportorg.libs.srpid.srpid.SRPid._preprocess_response | [код: pysport@b548c35 sportorg/libs/srpid/srpid.py:225] |
| url | `"sendMessage"` | first argument of requests.post | sportorg.libs.telegram.telegram.Telegram.send_message | [код: pysport@b548c35 sportorg/libs/telegram/telegram.py:27] |
| encoding | `"utf-8"` | literal | sportorg.libs.template.template.get_text_from_path | [код: pysport@b548c35 sportorg/libs/template/template.py:41] |
| other | `"rb"` | mode of open | sportorg.libs.winorient.wdb.parse_wdb | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1207] |
| other | `"wb"` | mode of open | sportorg.libs.winorient.wdb.write_wdb | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1216] |
| encoding | `"cp1251"` | keyword encoding of open | sportorg.libs.winorient.wo.CSVReader.parse | [код: pysport@b548c35 sportorg/libs/winorient/wo.py:13] |
| delimiter | `";"` | keyword delimiter of csv.reader | sportorg.libs.winorient.wo.CSVReader.parse | [код: pysport@b548c35 sportorg/libs/winorient/wo.py:14] |
| encoding | `"utf-8"` | keyword encoding of .open | sportorg.models.constant._read_config_items | [код: pysport@b548c35 sportorg/models/constant.py:13] |
| encoding | `"utf-8"` | literal | sportorg.modules.backup.file.File._backup | [код: pysport@b548c35 sportorg/modules/backup/file.py:37] |
| encoding | `"utf-8"` | literal | sportorg.modules.backup.file.File._backup | [код: pysport@b548c35 sportorg/modules/backup/file.py:48] |
| delimiter | `"\t"` | literal | sportorg.modules.backup.sfr_results_board.dump | [код: pysport@b548c35 sportorg/modules/backup/sfr_results_board.py:8] |
| encoding | `"utf-8"` | literal | sportorg.modules.backup.sfr_results_board.dump | [код: pysport@b548c35 sportorg/modules/backup/sfr_results_board.py:18] |
| encoding | `"UTF-8"` | keyword encoding of open | sportorg.modules.iof.iof_xml.export_result_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:38] |
| other | `"wb"` | mode of open | sportorg.modules.iof.iof_xml.export_result_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:38] |
| encoding | `"UTF-8"` | keyword encoding of open | sportorg.modules.iof.iof_xml.export_entry_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:46] |
| other | `"wb"` | mode of open | sportorg.modules.iof.iof_xml.export_entry_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:46] |
| encoding | `"UTF-8"` | keyword encoding of open | sportorg.modules.iof.iof_xml.export_start_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:54] |
| other | `"wb"` | mode of open | sportorg.modules.iof.iof_xml.export_start_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:54] |
| encoding | `"UTF-8"` | keyword encoding of open | sportorg.modules.iof.iof_xml.export_competitor_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:62] |
| other | `"wb"` | mode of open | sportorg.modules.iof.iof_xml.export_competitor_list | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:62] |
| encoding | `"utf-8"` | encode argument | sportorg.modules.live.orgeo.Orgeo.send | [код: pysport@b548c35 sportorg/modules/live/orgeo.py:50] |
| byte-constant | `5` | constant qt_version | sportorg.modules.printing.printing.PrintProcess.run | [код: pysport@b548c35 sportorg/modules/printing/printing.py:6] |
| byte-constant | `5` | literal | sportorg.modules.printing.printing.PrintProcess.run | [код: pysport@b548c35 sportorg/modules/printing/printing.py:72] |
| offset-or-width | `2` | literal | sportorg.modules.printing.printout_split.SportorgPrinter.print_penalty_line | [код: pysport@b548c35 sportorg/modules/printing/printout_split.py:106] |
| encoding | `"cp1251"` | literal | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:43] |
| delimiter | `";"` | literal | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:44] |
| delimiter | `"\|"` | literal | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:45] |
| offset-or-width | `9` | constant POS_START | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:35] |
| offset-or-width | `4` | constant POS_BIB | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:32] |
| offset-or-width | `2` | constant POS_NAME | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:30] |
| offset-or-width | `3` | constant POS_TEAM | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:31] |
| offset-or-width | `9` | constant POS_START | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:35] |
| offset-or-width | `9` | constant POS_START | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:35] |
| offset-or-width | `5` | constant POS_CARD | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:33] |
| offset-or-width | `5` | constant POS_CARD | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:33] |
| offset-or-width | `7` | constant POS_RES | sportorg.modules.recovery.recovery_orgeo_finish_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_orgeo_finish_csv.py:34] |
| delimiter | `";"` | literal | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:35] |
| offset-or-width | `2` | literal | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:39] |
| encoding | `"cp1251"` | keyword encoding of open | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:42] |
| offset-or-width | `45` | literal | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:45] |
| offset-or-width | `2` | constant POS_CARD | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:28] |
| offset-or-width | `15` | constant POS_START | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:29] |
| offset-or-width | `21` | constant POS_FINISH | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:30] |
| offset-or-width | `44` | constant POS_COUNT | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:31] |
| offset-or-width | `44` | constant POS_COUNT | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:31] |
| offset-or-width | `44` | constant POS_COUNT | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:31] |
| offset-or-width | `44` | constant POS_COUNT | sportorg.modules.recovery.recovery_si_master_csv.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_si_master_csv.py:31] |
| other | `"r"` | mode of open | sportorg.modules.recovery.recovery_sportorg_html.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:20] |
| offset-or-width | `-2` | literal | sportorg.modules.recovery.recovery_sportorg_html.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:23] |
| offset-or-width | `12` | literal | sportorg.modules.recovery.recovery_sportorg_html.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:23] |
| encoding | `"utf-8"` | decode argument | sportorg.modules.recovery.recovery_sportorg_html.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:27] |
| offset-or-width | `11` | literal | sportorg.modules.recovery.recovery_sportorg_html.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:32] |
| extension | `.json` | literal | sportorg.modules.recovery.recovery_sportorg_html.save_to_tmp_file | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:42] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.modules.recovery.recovery_sportorg_html.save_to_tmp_file | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:44] |
| other | `"w"` | mode of open | sportorg.modules.recovery.recovery_sportorg_html.save_to_tmp_file | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:44] |
| offset-or-width | `2` | literal | sportorg.modules.recovery.recovery_sportorg_si_log.recovery | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_si_log.py:41] |
| timeout | `0.1` | keyword timeout of tag_queue.get | sportorg.modules.rfid_impinj.rfid_impinj.ImpinjThread.run | [код: pysport@b548c35 sportorg/modules/rfid_impinj/rfid_impinj.py:74] |
| timeout | `1` | keyword timeout of self._queue.put | sportorg.modules.rfid_impinj.rfid_impinj.ImpinjThread.run | [код: pysport@b548c35 sportorg/modules/rfid_impinj/rfid_impinj.py:110] |
| delimiter | `""` | keyword newline of open | sportorg.modules.sfr.sfrxexporter.export_sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] |
| encoding | `"utf-8"` | keyword encoding of open | sportorg.modules.sfr.sfrxexporter.export_sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] |
| extension | `".sfrx"` | literal | sportorg.modules.sfr.sfrxexporter.export_sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] |
| other | `"w"` | mode of open | sportorg.modules.sfr.sfrxexporter.export_sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] |
| extension | `".sfrx"` | literal | sportorg.modules.sfr.sfrxexporter.export_sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:45] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_groups | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:120] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_teams | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:147] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_courses | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:156] |
| offset-or-width | `2` | literal | sportorg.modules.sfr.sfrxexporter._write_courses | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:175] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_controls | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:192] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_competitors | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:209] |
| offset-or-width | `1` | literal | sportorg.modules.sfr.sfrxexporter._write_splits | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:315] |
| offset-or-width | `1` | literal | sportorg.modules.sfr.sfrxexporter._write_splits | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:316] |
| offset-or-width | `5` | literal | sportorg.modules.sfr.sfrxexporter._write_splits | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:328] |
| other | `"a"` | mode of open | sportorg.modules.sportident.backup.BackupProcess.run | [код: pysport@b548c35 sportorg/modules/sportident/backup.py:22] |
| extension | `"si{}.log"` | literal | sportorg.modules.sportident.backup.BackupProcess.run | [код: pysport@b548c35 sportorg/modules/sportident/backup.py:21] |
| timeout | `1` | keyword timeout of self._queue.put | sportorg.modules.sportident.sireader.SIReaderThread.run | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:85] |
| offset-or-width | `12` | literal | sportorg.modules.sportident.sireader.ResultThread._check_data | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:137] |
| offset-or-width | `24` | literal | sportorg.modules.sportident.sireader.ResultThread._check_data | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:137] |
| offset-or-width | `12` | literal | sportorg.modules.sportident.sireader.ResultThread._check_data | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:143] |
| offset-or-width | `3600` | literal | sportorg.modules.sportident.sireader.ResultThread._check_data | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:143] |
| offset-or-width | `12` | literal | sportorg.modules.sportident.sireader.ResultThread._check_data | [код: pysport@b548c35 sportorg/modules/sportident/sireader.py:147] |
| timeout | `0.1` | keyword timeout of self._in_queue.get | sportorg.modules.teamwork.client.ClientSender.__call__ | [код: pysport@b548c35 sportorg/modules/teamwork/client.py:24] |
| offset-or-width | `1024` | constant MSG_SIZE | sportorg.modules.teamwork.client.ClientReceiver.__call__ | [код: pysport@b548c35 sportorg/modules/teamwork/client.py:32] |
| timeout | `1` | keyword timeout of selector.select | sportorg.modules.teamwork.client.ClientThread.run | [код: pysport@b548c35 sportorg/modules/teamwork/client.py:131] |
| encoding | `"utf-8"` | keyword encoding of .read_text | sportorg.modules.teamwork.crypto.load_teamwork_key_from_file | [код: pysport@b548c35 sportorg/modules/teamwork/crypto.py:57] |
| struct-format | `"=2s2H36sLQ"` | constant header_struck via first argument of struct.calcsize | sportorg.modules.teamwork.packet_header.Header.<class> | [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:85] |
| struct-format | `"=2s2H36sLQ"` | constant header_struck via first argument of struct.unpack | sportorg.modules.teamwork.packet_header.Header.unpack_header | [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:85] |
| struct-format | `"=2s2H36sLQ"` | constant header_struck via first argument of struct.pack | sportorg.modules.teamwork.packet_header.Header.pack_header | [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:85] |
| encoding | `"ascii"` | literal | sportorg.modules.teamwork.packet_header.Header.pack_header | [код: pysport@b548c35 sportorg/modules/teamwork/packet_header.py:152] |
| offset-or-width | `1024` | constant MSG_SIZE | sportorg.modules.teamwork.server.ServerReceiver.__call__ | [код: pysport@b548c35 sportorg/modules/teamwork/server.py:16] |
| timeout | `0.1` | keyword timeout of self._in_queue.get | sportorg.modules.teamwork.server.ServerSender.__call__ | [код: pysport@b548c35 sportorg/modules/teamwork/server.py:150] |
| timeout | `1` | keyword timeout of selector.select | sportorg.modules.teamwork.server.ServerThread.run | [код: pysport@b548c35 sportorg/modules/teamwork/server.py:455] |
| timeout | `5` | keyword timeout of requests.get | sportorg.modules.updater.checker.get_last_tag_name | [код: pysport@b548c35 sportorg/modules/updater/checker.py:12] |
| url | `"https://api.github.com/repos/sportorg/pysport/releases/latest"` | first argument of requests.get | sportorg.modules.updater.checker.get_last_tag_name | [код: pysport@b548c35 sportorg/modules/updater/checker.py:12] |
| other | `"rb"` | mode of open | sportorg.modules.winorient.wdb.WinOrientBinary._read_file | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:65] |
| other | `"rb"` | mode of open | sportorg.utils.text.detect_encoding | [код: pysport@b548c35 sportorg/utils/text.py:6] |
| encoding | `"UTF-8-SIG"` | literal | sportorg.utils.text.detect_encoding | [код: pysport@b548c35 sportorg/utils/text.py:15] |
| encoding | `"utf-8"` | literal | sportorg.utils.text.detect_encoding | [код: pysport@b548c35 sportorg/utils/text.py:15] |
| encoding | `"windows-1251"` | literal | sportorg.utils.text.detect_encoding | [код: pysport@b548c35 sportorg/utils/text.py:15] |
| encoding | `"utf-8"` | literal | sportorg.utils.text.detect_encoding | [код: pysport@b548c35 sportorg/utils/text.py:22] |

## Summary

```
{
 "by_context_direction": {
  "IOF XML": {
   "write": 4
  },
  "Impinj RFID": {
   "device": 1
  },
  "SFR": {
   "write": 11
  },
  "SPORTident": {
   "decode": 1,
   "device": 2,
   "write": 1
  },
  "WinOrient": {
   "read": 1
  },
  "backup": {
   "read": 2,
   "unknown": 1,
   "write": 2
  },
  "lib:huichang": {
   "decode": 2,
   "device": 1,
   "encode": 1,
   "read": 1,
   "write": 1
  },
  "lib:iof": {
   "read": 1,
   "write": 1
  },
  "lib:ocad": {
   "read": 2
  },
  "lib:settings": {
   "both": 1,
   "read": 1
  },
  "lib:sfr": {
   "both": 1,
   "decode": 7,
   "read": 1,
   "write": 1
  },
  "lib:sportiduino": {
   "both": 2,
   "decode": 2,
   "encode": 3,
   "read": 1,
   "write": 1
  },
  "lib:srpid": {
   "both": 2,
   "decode": 3,
   "encode": 1,
   "read": 1,
   "write": 1
  },
  "lib:telegram": {
   "write": 1
  },
  "lib:template": {
   "both": 2
  },
  "lib:winorient": {
   "read": 2,
   "write": 1
  },
  "live": {
   "both": 1,
   "write": 1
  },
  "other": {
   "both": 4,
   "device": 2,
   "read": 18,
   "unknown": 1,
   "write": 4
  },
  "printing": {
   "device": 5
  },
  "recovery": {
   "read": 4,
   "write": 1
  },
  "teamwork": {
   "both": 4,
   "read": 4,
   "write": 4
  }
 },
 "by_kind_direction": {
  "CSV": {
   "read": 3
  },
  "HID": {
   "device": 1
  },
  "HTTP": {
   "both": 1,
   "read": 1,
   "write": 1
  },
  "Huichang serial": {
   "decode": 2,
   "encode": 1,
   "read": 1,
   "write": 1
  },
  "INI": {
   "both": 2
  },
  "Impinj RFID": {
   "device": 1
  },
  "JSON": {
   "read": 6,
   "write": 6
  },
  "PO": {
   "read": 1
  },
  "SFR HID": {
   "decode": 7,
   "read": 1
  },
  "SPORTident lib": {
   "device": 1
  },
  "SPORTident serial": {
   "decode": 1
  },
  "SRPID serial": {
   "both": 1,
   "decode": 3,
   "encode": 1,
   "read": 2,
   "write": 1
  },
  "Sportiduino serial": {
   "both": 1,
   "decode": 2,
   "encode": 3,
   "read": 2,
   "write": 1
  },
  "XML": {
   "read": 2,
   "write": 5
  },
  "audio": {
   "read": 1
  },
  "binary file": {
   "read": 3,
   "write": 6
  },
  "docx": {
   "both": 1
  },
  "file object (parameter)": {
   "read": 2,
   "write": 12
  },
  "file system": {
   "write": 1
  },
  "gzip": {
   "read": 2
  },
  "jinja2": {
   "both": 2
  },
  "printer": {
   "device": 7
  },
  "serial": {
   "device": 4
  },
  "socket": {
   "both": 2,
   "read": 2,
   "write": 3
  },
  "struct": {
   "both": 1,
   "read": 1,
   "write": 1
  },
  "text file": {
   "both": 1,
   "read": 24,
   "unknown": 2,
   "write": 5
  }
 },
 "by_value_kind": {
  "baudrate": 3,
  "byte-constant": 80,
  "delimiter": 6,
  "encoding": 43,
  "extension": 14,
  "offset-or-width": 107,
  "other": 18,
  "struct-format": 3,
  "timeout": 13,
  "url": 4
 },
 "contexts_without_reader": [
  "IOF XML",
  "SFR",
  "SPORTident",
  "lib:telegram"
 ],
 "contexts_without_writer": [
  "WinOrient",
  "lib:ocad"
 ],
 "device_only_contexts": [
  "Impinj RFID",
  "printing"
 ],
 "device_only_formats": [
  "HID",
  "Impinj RFID",
  "SPORTident lib",
  "printer",
  "serial"
 ],
 "functions": 124,
 "io_calls": 184,
 "values": 291,
 "without_reader": [
  "SPORTident serial",
  "file system"
 ],
 "without_writer": [
  "CSV",
  "PO",
  "SFR HID",
  "SPORTident serial",
  "audio",
  "gzip"
 ]
}
```
