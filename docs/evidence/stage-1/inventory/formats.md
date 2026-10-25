# Import/export formats of pysport@b548c35

Format labels come from the module table in `scripts/archaeology/inventory.py` (`FORMAT_MODULES`, an assumption). Protocol details are W5.

## Menu action to format chains

| menu path | action | formats (by module) | modules | calls into them | dialog filters | class |
| --- | --- | --- | --- | --- | --- | --- |
| File > Open | OpenAction |  |  |  | SportOrg file (*.json) [код: pysport@b548c35 sportorg/gui/menu/actions.py:116] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:113] |
| File > Import > Import from SportOrg file | ImportSportOrgAction | SportOrg JSON (.json, gzip) | sportorg.modules.backup.file, sportorg.modules.backup.json | get_races_from_file, is_gzip_file | SportOrg (*.json) [код: pysport@b548c35 sportorg/gui/menu/actions.py:929] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:926] |
| File > Import > CSV Winorient | CSVWinorientImportAction | WinOrient (CSV, WDB) | sportorg.modules.winorient | winorient.import_csv | CSV Winorient (*.csv) [код: pysport@b548c35 sportorg/gui/menu/actions.py:170] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:167] |
| File > Import > WDB Winorient | WDBWinorientImportAction | WinOrient (CSV, WDB) | sportorg.modules.winorient, sportorg.modules.winorient.wdb | winorient.import_wo_wdb | WDB Winorient (*.wdb) [код: pysport@b548c35 sportorg/gui/menu/actions.py:206] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:203] |
| File > Import > SFRX | SFRXImportAction | SFRx | sportorg.libs.sfr | sfrximporter.import_sfrx | SFRX (*.sfrx) [код: pysport@b548c35 sportorg/gui/menu/actions.py:188] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:185] |
| File > Import > Ocad txt v8 | OcadTXTv8ImportAction | OCAD | sportorg.modules.ocad, sportorg.modules.ocad.ocad | ocad.import_txt_v8 | Ocad classes v8 (*.txt) [код: pysport@b548c35 sportorg/gui/menu/actions.py:225] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:222] |
| File > Import > IOF xml | IOFEntryListImportAction | IOF XML | sportorg.modules.iof | iof_xml.import_from_iof | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:329] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:326] |
| File > Import > SPORTident master station CSV | RecoverySportidentMasterCsvAction | Recovery import (CSV, HTML, SI log) | sportorg.modules.recovery | recovery_si_master_csv.recovery | CSV file (*.csv) [код: pysport@b548c35 sportorg/gui/menu/actions.py:419] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:415] |
| File > Import > SportOrg SI log | RecoverySportorgSiLogAction | Recovery import (CSV, HTML, SI log) | sportorg.modules.recovery | recovery_sportorg_si_log.recovery | SportOrg SI log (*.log) [код: pysport@b548c35 sportorg/gui/menu/actions.py:408] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:404] |
| File > Import > Orgeo.ru CSV | RecoveryOrgeoFinishCsvAction | Recovery import (CSV, HTML, SI log) | sportorg.modules.recovery | recovery_orgeo_finish_csv.recovery | CSV file (*.csv) [код: pysport@b548c35 sportorg/gui/menu/actions.py:430] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:426] |
| File > Import > SportOrg HTML | RecoverySportorgHtmlAction | Recovery import (CSV, HTML, SI log), SportOrg JSON (.json, gzip) | sportorg.modules.backup.json, sportorg.modules.recovery | get_races_from_file, recovery_sportorg_html.recovery | SportOrg HTML report (*.html) [код: pysport@b548c35 sportorg/gui/menu/actions.py:390] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:386] |
| File > Export > WDB Winorient | WDBWinorientExportAction | WinOrient (CSV, WDB) | sportorg.libs.winorient.wdb, sportorg.modules.winorient.wdb | WinOrientBinary, write_wdb | WDB file (*.wdb) [код: pysport@b548c35 sportorg/gui/menu/actions.py:244] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:240] |
| File > Export > IOF xml > ResultList | IOFResultListExportAction | IOF XML | sportorg.modules.iof | iof_xml.export_result_list | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:271] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:267] |
| File > Export > IOF xml > ResultListAllSplits | IOFResultListAllSplitsExportAction | IOF XML | sportorg.modules.iof | iof_xml.export_result_list | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:290] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:286] |
| File > Export > IOF xml > EntrytList | IOFEntryListExportAction | IOF XML | sportorg.modules.iof | iof_xml.export_entry_list | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:311] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:307] |
| File > Export > IOF xml > CompetitorList | IOFCompetitorListExportAction | IOF XML | sportorg.modules.iof | iof_xml.export_competitor_list | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:367] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:363] |
| File > Export > IOF xml > StartList | IOFStartListExportAction | IOF XML | sportorg.modules.iof | iof_xml.export_start_list | IOF xml (*.xml) [код: pysport@b548c35 sportorg/gui/menu/actions.py:348] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:344] |
| File > Export > SFRX | SFRExportAction | SFRx | sportorg.modules.sfr.sfrxexporter | export_sfrx | SFRX (*.sfrx) [код: pysport@b548c35 sportorg/gui/menu/actions.py:991] | [код: pysport@b548c35 sportorg/gui/menu/actions.py:987] |
| Results > Create report | CreateReportAction | Report output (HTML, DOCX, CSV) | sportorg.gui.dialogs.report_dialog | ReportDialog |  | [код: pysport@b548c35 sportorg/gui/menu/actions.py:628] |
| Service > On/Off card readout | CardReadoutAction | SFRx | sportorg.modules.sfr.sfrreader | SFRReaderClient |  | [код: pysport@b548c35 sportorg/gui/menu/actions.py:609] |
| Options > Printer settings | PrinterSettingsAction | Report templates (HTML) | sportorg.gui.dialogs.print_properties | PrintPropertiesDialog |  | [код: pysport@b548c35 sportorg/gui/menu/actions.py:812] |

## Filters (`*.ext` string literals in sportorg/)

| label | extensions | source |
| --- | --- | --- |
| HTML file (*.html) | .html | [код: pysport@b548c35 sportorg/gui/dialogs/print_properties.py:85] |
| HTML file (*.html) | .html | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:80] |
| MS Word file (*.docx) | .docx | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:226] |
| CSV file (*.csv) | .csv | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:251] |
| HTML file (*.html) | .html | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:278] |
| SportOrg file (*.json) | .json | [код: pysport@b548c35 sportorg/gui/main_window.py:896] |
| SportOrg file (*.json) | .json | [код: pysport@b548c35 sportorg/gui/menu/actions.py:116] |
| CSV Winorient (*.csv) | .csv | [код: pysport@b548c35 sportorg/gui/menu/actions.py:170] |
| SFRX (*.sfrx) | .sfrx | [код: pysport@b548c35 sportorg/gui/menu/actions.py:188] |
| WDB Winorient (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/gui/menu/actions.py:206] |
| Ocad classes v8 (*.txt) | .txt | [код: pysport@b548c35 sportorg/gui/menu/actions.py:225] |
| WDB file (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/gui/menu/actions.py:244] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:271] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:290] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:311] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:329] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:348] |
| IOF xml (*.xml) | .xml | [код: pysport@b548c35 sportorg/gui/menu/actions.py:367] |
| SportOrg HTML report (*.html) | .html | [код: pysport@b548c35 sportorg/gui/menu/actions.py:390] |
| SportOrg SI log (*.log) | .log | [код: pysport@b548c35 sportorg/gui/menu/actions.py:408] |
| CSV file (*.csv) | .csv | [код: pysport@b548c35 sportorg/gui/menu/actions.py:419] |
| CSV file (*.csv) | .csv | [код: pysport@b548c35 sportorg/gui/menu/actions.py:430] |
| SportOrg (*.json) | .json | [код: pysport@b548c35 sportorg/gui/menu/actions.py:929] |
| SFRX (*.sfrx) | .sfrx | [код: pysport@b548c35 sportorg/gui/menu/actions.py:991] |
| WDB Winorient (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender_dialog.py:31] |
| WDB file (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/modules/winorient/wdb_number_setter.py:26] |
| WDB file (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/modules/winorient/wdb_number_setter.py:29] |
| WDB file (*.wdb) | .wdb | [код: pysport@b548c35 sportorg/modules/winorient/wdb_number_setter.py:36] |

## Extension strings

| string | source |
| --- | --- |
| .log | [код: pysport@b548c35 sportorg/config.py:130] |
| .docx | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:210] |
| .csv | [код: pysport@b548c35 sportorg/gui/dialogs/report_dialog.py:235] |
| .lock | [код: pysport@b548c35 sportorg/gui/main_window.py:1156] |
| .lock | [код: pysport@b548c35 sportorg/gui/main_window.py:1182] |
| .po | [код: pysport@b548c35 sportorg/language.py:44] |
| .mo | [код: pysport@b548c35 sportorg/language.py:45] |
| .tmp | [код: pysport@b548c35 sportorg/modules/backup/file.py:56] |
| .tmp | [код: pysport@b548c35 sportorg/modules/backup/file.py:60] |
| .tmp | [код: pysport@b548c35 sportorg/modules/backup/file.py:65] |
| .tmp | [код: pysport@b548c35 sportorg/modules/backup/file.py:69] |
| .srb | [код: pysport@b548c35 sportorg/modules/backup/file.py:73] |
| .html | [код: pysport@b548c35 sportorg/modules/printing/model.py:42] |
| .json | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:42] |
| .sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:32] |
| .sfrx | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:45] |

## Reader/writer candidates in format modules (by function name)

| format | function | direction | source |
| --- | --- | --- | --- |
| IOF XML | make_create_time | write | [код: pysport@b548c35 sportorg/libs/iof/generator.py:12] |
| IOF XML | BaseElement.write | write | [код: pysport@b548c35 sportorg/libs/iof/iof.py:50] |
| IOF XML | parse | read | [код: pysport@b548c35 sportorg/libs/iof/parser.py:10] |
| OCAD | ClassesV8.parse | read | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:66] |
| OCAD | parse_txt_v8 | read | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:177] |
| OCAD | IofXMLv3.parse | read | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:201] |
| OCAD | parse_xml_v3 | read | [код: pysport@b548c35 sportorg/libs/ocad/ocad.py:207] |
| SFRx | SFRReader._send_command | write | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:117] |
| SFRx | SFRReader._read_card_id | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:246] |
| SFRx | SFRReader._read_bib | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:249] |
| SFRx | SFRReader._read_data_counter | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:253] |
| SFRx | SFRReader._read_data_punch | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:257] |
| SFRx | SFRReaderReadout.read_card | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrreader.py:433] |
| SFRx | import_sfrx | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrximporter.py:20] |
| SFRx | SFRXParser.parse | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:17] |
| SFRx | parse | read | [код: pysport@b548c35 sportorg/libs/sfr/sfrxparser.py:158] |
| WinOrient (CSV, WDB) | WDBPunch.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:83] |
| WinOrient (CSV, WDB) | WDBFinish.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:103] |
| WinOrient (CSV, WDB) | WDBFinish.create | write | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:110] |
| WinOrient (CSV, WDB) | WDBChip.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:135] |
| WinOrient (CSV, WDB) | WDBTeam.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:191] |
| WinOrient (CSV, WDB) | WDBDistance.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:242] |
| WinOrient (CSV, WDB) | WDBGroup.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:321] |
| WinOrient (CSV, WDB) | WDBMan.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:393] |
| WinOrient (CSV, WDB) | WDBInfo.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:604] |
| WinOrient (CSV, WDB) | WDBAdventure.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:885] |
| WinOrient (CSV, WDB) | WDB.parse_bytes | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:950] |
| WinOrient (CSV, WDB) | parse_wdb | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1206] |
| WinOrient (CSV, WDB) | write_wdb | write | [код: pysport@b548c35 sportorg/libs/winorient/wdb.py:1215] |
| WinOrient (CSV, WDB) | WdbOnlineSender.read | read | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:52] |
| WinOrient (CSV, WDB) | WdbOnlineSender.send | write | [код: pysport@b548c35 sportorg/libs/winorient/wdb_online_sender.py:96] |
| WinOrient (CSV, WDB) | CSVReader.parse | read | [код: pysport@b548c35 sportorg/libs/winorient/wo.py:12] |
| WinOrient (CSV, WDB) | parse_csv | read | [код: pysport@b548c35 sportorg/libs/winorient/wo.py:79] |
| SportOrg JSON (.json, gzip) | File.create | write | [код: pysport@b548c35 sportorg/modules/backup/file.py:53] |
| SportOrg JSON (.json, gzip) | File.save | write | [код: pysport@b548c35 sportorg/modules/backup/file.py:62] |
| SportOrg JSON (.json, gzip) | File.open | read | [код: pysport@b548c35 sportorg/modules/backup/file.py:78] |
| SportOrg JSON (.json, gzip) | dump | write | [код: pysport@b548c35 sportorg/modules/backup/json.py:19] |
| SportOrg JSON (.json, gzip) | load | read | [код: pysport@b548c35 sportorg/modules/backup/json.py:34] |
| SportOrg JSON (.json, gzip) | get_races_from_file | read | [код: pysport@b548c35 sportorg/modules/backup/json.py:50] |
| SFR results board (.srb, TSV) | dump | write | [код: pysport@b548c35 sportorg/modules/backup/sfr_results_board.py:6] |
| IOF XML | export_result_list | write | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:33] |
| IOF XML | export_entry_list | write | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:41] |
| IOF XML | export_start_list | write | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:49] |
| IOF XML | export_competitor_list | write | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:57] |
| IOF XML | import_from_iof | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:65] |
| IOF XML | import_from_course_data | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:85] |
| IOF XML | import_from_variation_data | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:108] |
| IOF XML | create_person | write | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:142] |
| IOF XML | import_from_entry_list | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:216] |
| IOF XML | import_from_result_list | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:251] |
| IOF XML | import_from_event_data | read | [код: pysport@b548c35 sportorg/modules/iof/iof_xml.py:316] |
| OCAD | import_txt_v8 | read | [код: pysport@b548c35 sportorg/modules/ocad/ocad.py:10] |
| Recovery import (CSV, HTML, SI log) | save_to_tmp_file | write | [код: pysport@b548c35 sportorg/modules/recovery/recovery_sportorg_html.py:39] |
| SFRx | export_sfr_data | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:15] |
| SFRx | export_sfrx | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:25] |
| SFRx | _write_header | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:54] |
| SFRx | _write_days | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:86] |
| SFRx | _write_descriptions | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:104] |
| SFRx | _write_clubs | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:111] |
| SFRx | _write_groups | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:118] |
| SFRx | _write_teams | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:145] |
| SFRx | _write_courses | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:154] |
| SFRx | _write_controls | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:183] |
| SFRx | _write_competitors | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:207] |
| SFRx | _write_splits | write | [код: pysport@b548c35 sportorg/modules/sfr/sfrxexporter.py:268] |
| WinOrient (CSV, WDB) | WinOrientBinary._read_file | read | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:63] |
| WinOrient (CSV, WDB) | WinOrientBinary.create_objects | write | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:74] |
| WinOrient (CSV, WDB) | WinOrientBinary.export | write | [код: pysport@b548c35 sportorg/modules/winorient/wdb.py:194] |
| WinOrient (CSV, WDB) | import_csv | read | [код: pysport@b548c35 sportorg/modules/winorient/winorient.py:10] |
| WinOrient (CSV, WDB) | import_wo_wdb | read | [код: pysport@b548c35 sportorg/modules/winorient/winorient.py:89] |
