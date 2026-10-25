# Action classes of pysport@b548c35

Resolved through the `ActionFactory` registry of [код: pysport@b548c35 sportorg/gui/menu/actions.py:1]; imports are the module-level names of actions.py used in the class body.

| action class | class | module-level names used ← source module |
| --- | --- | --- |
| AboutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:891] | AboutDialog ← sportorg.gui.dialogs.about |
| AddObjectAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:437] |  |
| AddSPORTidentResultAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:758] | Teamwork ← sportorg.modules.teamwork.teamwork, logging ← logging, race ← sportorg.models.memory |
| AssignResultByBibAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:910] | race ← sportorg.models.memory |
| AssignResultByCardNumberAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:918] | race ← sportorg.models.memory |
| CPDeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:740] | CPDeleteDialog ← sportorg.gui.dialogs.cp_delete |
| CSVWinorientImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:167] | QMessageBox ← PySide6.QtWidgets, get_open_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, translate ← sportorg.language, winorient ← sportorg.modules.winorient |
| CardReadoutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:609] | HuichangClient ← sportorg.modules.huichang.huichang, ImpinjClient ← sportorg.modules.rfid_impinj.rfid_impinj, SFRReaderClient ← sportorg.modules.sfr.sfrreader, SIReaderClient ← sportorg.modules.sportident.sireader, SportiduinoClient ← sportorg.modules.sportiduino.sportiduino, SrpidClient ← sportorg.modules.srpid.srpid, SystemType ← sportorg.models.memory, race ← sportorg.models.memory, time ← time |
| ChangeStatusAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:687] | QMessageBox ← PySide6.QtWidgets, ResultStatus ← sportorg.models.memory, Teamwork ← sportorg.modules.teamwork.teamwork, live_client ← sportorg.modules.live.live, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| CheckUpdatesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:896] | QMessageBox ← PySide6.QtWidgets, checker ← sportorg.modules.updater, config ← sportorg, logging ← logging, translate ← sportorg.language |
| ControlTimeChangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:734] | ControlTimeChangeDialog ← sportorg.gui.dialogs.control_time_change_dialog |
| CopyAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:131] | QApplication ← PySide6.QtWidgets |
| CopyBibToCardNumber | [код: pysport@b548c35 sportorg/gui/menu/actions.py:577] | QMessageBox ← PySide6.QtWidgets, copy_bib_to_card_number ← sportorg.models.start.start_preparation, messageBoxQuestion ← sportorg.gui.utils.custom_controls, translate ← sportorg.language |
| CopyCardNumberToBib | [код: pysport@b548c35 sportorg/gui/menu/actions.py:588] | QMessageBox ← PySide6.QtWidgets, copy_card_number_to_bib ← sportorg.models.start.start_preparation, messageBoxQuestion ← sportorg.gui.utils.custom_controls, translate ← sportorg.language |
| CreateReportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:628] | ReportDialog ← sportorg.gui.dialogs.report_dialog |
| DeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:442] |  |
| DuplicateAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:145] |  |
| EventSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:162] | EventPropertiesDialog ← sportorg.gui.dialogs.event_properties |
| ExtractPersonMiddleName | [код: pysport@b548c35 sportorg/gui/menu/actions.py:975] | race ← sportorg.models.memory |
| FilterAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:475] | DialogFilter ← sportorg.gui.dialogs.filter_dialog |
| FilterResetAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:482] |  |
| GroupFinderAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:645] | ResultStatus ← sportorg.models.memory, race ← sportorg.models.memory |
| GuessCorridorsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:541] | guess_corridors_for_groups ← sportorg.models.start.start_preparation |
| GuessCoursesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:535] | guess_courses_for_groups ← sportorg.gui.dialogs.start_preparation |
| HuichangManagementAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:982] | HuichangManagementDialog ← sportorg.gui.dialogs.huichang_management_dialog |
| IOFCompetitorListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:363] | QMessageBox ← PySide6.QtWidgets, config ← sportorg, get_save_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| IOFEntryListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:307] | QMessageBox ← PySide6.QtWidgets, config ← sportorg, get_save_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| IOFEntryListImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:326] | QMessageBox ← PySide6.QtWidgets, get_open_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, translate ← sportorg.language |
| IOFResultListAllSplitsExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:286] | QMessageBox ← PySide6.QtWidgets, config ← sportorg, get_save_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| IOFResultListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:267] | QMessageBox ← PySide6.QtWidgets, config ← sportorg, get_save_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| IOFStartListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:344] | QMessageBox ← PySide6.QtWidgets, config ← sportorg, get_save_file_name ← sportorg.gui.dialogs.file_dialog, iof_xml ← sportorg.modules.iof, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| ImportPersonsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:728] | ImportPersonsTableDialog ← sportorg.gui.dialogs.import_persons_table_dialog |
| ImportSportOrgAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:926] | SportOrgImportDialog ← sportorg.gui.dialogs.sportorg_import_dialog, get_open_file_name ← sportorg.gui.dialogs.file_dialog, get_races_from_file ← sportorg.modules.backup.json, is_gzip_file ← sportorg.modules.backup.file, settings ← sportorg, translate ← sportorg.language |
| LiveSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:817] | LiveDialog ← sportorg.gui.dialogs.live_dialog |
| ManualFinishAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:599] | ResultManual ← sportorg.models.memory, Teamwork ← sportorg.modules.teamwork.teamwork, live_client ← sportorg.modules.live.live, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| MarkedRouteCourseGeneration | [код: pysport@b548c35 sportorg/gui/menu/actions.py:969] | MarkedRouteDialog ← sportorg.gui.dialogs.marked_route_dialog |
| MassEditAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:454] | GroupMassEditDialog ← sportorg.gui.dialogs.group_mass_edit, MassEditDialog ← sportorg.gui.dialogs.entry_mass_edit, OrganizationMassEditDialog ← sportorg.gui.dialogs.organization_mass_edit, race ← sportorg.models.memory |
| MergeResultsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:752] | MergeResultsDialog ← sportorg.gui.dialogs.merge_results |
| NewAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:103] |  |
| OcadTXTv8ImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:222] | OcadImportException ← sportorg.modules.ocad.ocad, QMessageBox ← PySide6.QtWidgets, get_open_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, ocad ← sportorg.modules.ocad, translate ← sportorg.language |
| OnlineSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:859] | live_client ← sportorg.modules.live.live, logging ← logging, race ← sportorg.models.memory |
| OpenAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:113] | get_open_file_name ← sportorg.gui.dialogs.file_dialog, translate ← sportorg.language |
| PenaltyCalculationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:665] | ResultChecker ← sportorg.models.result.result_checker, logging ← logging, race ← sportorg.models.memory, recalculate_results ← sportorg.models.result.result_tools |
| PenaltyRemovingAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:676] | OTime ← sportorg.common.otime, logging ← logging, race ← sportorg.models.memory, recalculate_results ← sportorg.models.result.result_tools |
| PluginsSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:823] | PluginsDialog ← sportorg.gui.dialogs.plugins |
| PrinterSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:812] | PrintPropertiesDialog ← sportorg.gui.dialogs.print_properties |
| RecheckingAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:638] | race ← sportorg.models.memory, recalculate_results ← sportorg.models.result.result_tools |
| RecoveryOrgeoFinishCsvAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:426] | get_open_file_name ← sportorg.gui.dialogs.file_dialog, race ← sportorg.models.memory, recovery_orgeo_finish_csv ← sportorg.modules.recovery, translate ← sportorg.language |
| RecoverySportidentMasterCsvAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:415] | get_open_file_name ← sportorg.gui.dialogs.file_dialog, race ← sportorg.models.memory, recovery_si_master_csv ← sportorg.modules.recovery, translate ← sportorg.language |
| RecoverySportorgHtmlAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:386] | SportOrgImportDialog ← sportorg.gui.dialogs.sportorg_import_dialog, detect_encoding ← sportorg.utils.text, get_open_file_name ← sportorg.gui.dialogs.file_dialog, get_races_from_file ← sportorg.modules.backup.json, recovery_sportorg_html ← sportorg.modules.recovery, remove ← os, translate ← sportorg.language |
| RecoverySportorgSiLogAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:404] | get_open_file_name ← sportorg.gui.dialogs.file_dialog, race ← sportorg.models.memory, recovery_sportorg_si_log ← sportorg.modules.recovery, translate ← sportorg.language |
| RefreshAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:470] |  |
| RelayCloneAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:571] | RelayCloneDialog ← sportorg.gui.dialogs.relay_clone_dialog |
| RelayNumberAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:547] | QApplication ← PySide6.QtWidgets, QtCore ← PySide6, RelayNumberDialog ← sportorg.gui.dialogs.relay_number_dialog |
| RentCardsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:963] | RentCardsDialog ← sportorg.gui.dialogs.rent_cards_dialog |
| SFRExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:987] | QMessageBox ← PySide6.QtWidgets, get_save_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language |
| SFRXImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:185] | QMessageBox ← PySide6.QtWidgets, get_open_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, sfrximporter ← sportorg.libs.sfr, translate ← sportorg.language |
| SaveAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:108] |  |
| SaveAsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:121] |  |
| SearchAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:490] | SearchDialog ← sportorg.gui.dialogs.search_dialog |
| SetDNSNumbersAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:722] | InputStartNumbersDialog ← sportorg.gui.dialogs.not_start_dialog |
| SettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:157] | SettingsDialog ← sportorg.gui.dialogs.settings |
| SplitDeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:746] | SplitDeleteDialog ← sportorg.gui.dialogs.split_delete |
| SplitPrintoutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:633] |  |
| StartHandicapAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:565] | StartHandicapDialog ← sportorg.gui.dialogs.start_handicap_dialog |
| StartPreparationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:529] | StartPreparationDialog ← sportorg.gui.dialogs.start_preparation |
| StartTimeChangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:559] | StartTimeChangeDialog ← sportorg.gui.dialogs.start_time_change_dialog |
| TeamworkEnableAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:779] | Teamwork ← sportorg.modules.teamwork.teamwork, configure_teamwork_from_settings ← sportorg.modules.teamwork.teamwork |
| TeamworkSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:785] | Teamwork ← sportorg.modules.teamwork.teamwork, logging ← logging, race ← sportorg.models.memory |
| TeamworkSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:774] | TeamworkPropertiesDialog ← sportorg.gui.dialogs.teamwork_properties |
| TelegramSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:841] | logging ← logging, race ← sportorg.models.memory, telegram_client ← sportorg.modules.telegram.telegram, translate ← sportorg.language |
| TelegramSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:836] | TelegramDialog ← sportorg.gui.dialogs.telegram_dialog |
| TextExchangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:447] | TextExchangeDialog ← sportorg.gui.dialogs.text_io, race ← sportorg.models.memory |
| TimekeepingSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:768] | TimekeepingPropertiesDialog ← sportorg.gui.dialogs.timekeeping_properties |
| ToCoursesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:514] |  |
| ToGroupsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:509] |  |
| ToLogsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:524] |  |
| ToRaceResultsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:504] |  |
| ToStartPreparationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:499] |  |
| ToTeamsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:519] |  |
| WDBWinorientExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:240] | QMessageBox ← PySide6.QtWidgets, WinOrientBinary ← sportorg.modules.winorient.wdb, get_save_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, race ← sportorg.models.memory, translate ← sportorg.language, write_wdb ← sportorg.libs.winorient.wdb |
| WDBWinorientImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:203] | QMessageBox ← PySide6.QtWidgets, WDBImportError ← sportorg.modules.winorient.wdb, get_open_file_name ← sportorg.gui.dialogs.file_dialog, logging ← logging, translate ← sportorg.language, winorient ← sportorg.modules.winorient |
