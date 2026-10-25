# Menu tree of pysport@b548c35

Parsed from the `menu_list()` literal [код: pysport@b548c35 sportorg/gui/menu/menu.py:1] with `ast`; plugin items are added at run time and are not listed.

| menu path (translation keys) | kind | shortcut | action | class | other keys | item |
| --- | --- | --- | --- | --- | --- | --- |
| File | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:68] |
| File > New | action | Ctrl+N | NewAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:103] | icon=config.icon_dir('file.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:71] |
| File > Save | action | Ctrl+S | SaveAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:108] | icon=config.icon_dir('save.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:77] |
| File > Open | action | Ctrl+O | OpenAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:113] | icon=config.icon_dir('folder.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:83] |
| File > Save As | action | Ctrl+Shift+S | SaveAsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:121] | icon=config.icon_dir('save.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:89] |
| File > <separator> | separator |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:95] |
| File > Settings | action | Ctrl+Alt+S | SettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:157] | icon=config.icon_dir('settings.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:98] |
| File > Event Settings | action | Ctrl+I | EventSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:162] | icon=config.icon_dir('form.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:104] |
| File > <separator> | separator |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:110] |
| File > Import | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:113] |
| File > Import > Import from SportOrg file | action |  | ImportSportOrgAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:926] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:116] |
| File > Import > CSV Winorient | action |  | CSVWinorientImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:167] | feature=settings.FEATURE_WINORIENT; icon=config.icon_dir('csv.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:120] |
| File > Import > WDB Winorient | action |  | WDBWinorientImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:203] | feature=settings.FEATURE_WINORIENT | [код: pysport@b548c35 sportorg/gui/menu/menu.py:126] |
| File > Import > SFRX | action |  | SFRXImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:185] | feature=settings.FEATURE_SFR | [код: pysport@b548c35 sportorg/gui/menu/menu.py:131] |
| File > Import > Ocad txt v8 | action |  | OcadTXTv8ImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:222] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:136] |
| File > Import > IOF xml | action |  | IOFEntryListImportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:326] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:140] |
| File > Import > SPORTident master station CSV | action |  | RecoverySportidentMasterCsvAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:415] | feature=settings.FEATURE_SPORTIDENT | [код: pysport@b548c35 sportorg/gui/menu/menu.py:144] |
| File > Import > SportOrg SI log | action |  | RecoverySportorgSiLogAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:404] | feature=settings.FEATURE_SPORTIDENT | [код: pysport@b548c35 sportorg/gui/menu/menu.py:149] |
| File > Import > Orgeo.ru CSV | action |  | RecoveryOrgeoFinishCsvAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:426] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:154] |
| File > Import > SportOrg HTML | action |  | RecoverySportorgHtmlAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:386] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:158] |
| File > Import > Import persons from table (clipboard) | action |  | ImportPersonsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:728] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:162] |
| File > Export | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:168] |
| File > Export > WDB Winorient | action |  | WDBWinorientExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:240] | feature=settings.FEATURE_WINORIENT | [код: pysport@b548c35 sportorg/gui/menu/menu.py:171] |
| File > Export > IOF xml | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:176] |
| File > Export > IOF xml > ResultList | action |  | IOFResultListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:267] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:179] |
| File > Export > IOF xml > ResultListAllSplits | action |  | IOFResultListAllSplitsExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:286] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:183] |
| File > Export > IOF xml > EntrytList | action |  | IOFEntryListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:307] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:187] |
| File > Export > IOF xml > CompetitorList | action |  | IOFCompetitorListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:363] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:191] |
| File > Export > IOF xml > StartList | action |  | IOFStartListExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:344] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:195] |
| File > Export > SFRX | action |  | SFRExportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:987] | feature=settings.FEATURE_SFR | [код: pysport@b548c35 sportorg/gui/menu/menu.py:201] |
| Edit | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:210] |
| Edit > Add object | action | ['insert', 'i'] | AddObjectAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:437] | icon=config.icon_dir('add.svg'); tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:213] |
| Edit > Delete | action | Del | DeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:442] | icon=config.icon_dir('delete.svg'); tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:220] |
| Edit > Copy | action | Ctrl+C | CopyAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:131] | tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:227] |
| Edit > Duplicate | action | Ctrl+D | DuplicateAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:145] | tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:233] |
| Edit > Text exchange | action | Ctrl+T | TextExchangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:447] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:239] |
| Edit > Mass edit | action | Ctrl+E | MassEditAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:454] | tabs=[0, 2, 4] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:244] |
| View | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:252] |
| View > Refresh | action | F5 | RefreshAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:470] | icon=config.icon_dir('refresh.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:255] |
| View > Filter | action | F2 | FilterAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:475] | icon=config.icon_dir('filter.svg'); tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:261] |
| View > Filter reset | action | Ctrl+F2 | FilterResetAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:482] | icon=config.icon_dir('filter_reset.svg'); tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:268] |
| View > Search | action | Ctrl+F | SearchAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:490] | icon=config.icon_dir('search.svg'); tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:275] |
| View > <separator> | separator |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:282] |
| View > Start Preparation | action | Ctrl+1 | ToStartPreparationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:499] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:285] |
| View > Race Results | action | Ctrl+2 | ToRaceResultsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:504] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:290] |
| View > Groups | action | Ctrl+3 | ToGroupsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:509] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:295] |
| View > Courses | action | Ctrl+4 | ToCoursesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:514] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:300] |
| View > Teams | action | Ctrl+5 | ToTeamsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:519] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:305] |
| View > Logs | action | Ctrl+6 | ToLogsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:524] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:310] |
| Start Preparation | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:317] |
| Start Preparation > Start Preparation | action | F6 | StartPreparationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:529] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:320] |
| Start Preparation > Guess courses | action |  | GuessCoursesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:535] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:325] |
| Start Preparation > Guess corridors | action |  | GuessCorridorsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:541] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:329] |
| Start Preparation > Relay number assign mode | action |  | RelayNumberAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:547] | tabs=[0] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:333] |
| Start Preparation > Start time change | action |  | StartTimeChangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:559] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:338] |
| Start Preparation > Handicap start time | action |  | StartHandicapAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:565] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:342] |
| Start Preparation > Clone relay legs | action |  | RelayCloneAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:571] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:346] |
| Start Preparation > Use bib as card number | action |  | CopyBibToCardNumber | [код: pysport@b548c35 sportorg/gui/menu/actions.py:577] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:350] |
| Start Preparation > Use card number as bib | action |  | CopyCardNumberToBib | [код: pysport@b548c35 sportorg/gui/menu/actions.py:588] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:354] |
| Start Preparation > Marked route course generation | action |  | MarkedRouteCourseGeneration | [код: pysport@b548c35 sportorg/gui/menu/actions.py:969] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:358] |
| Start Preparation > Extract person middle name | action |  | ExtractPersonMiddleName | [код: pysport@b548c35 sportorg/gui/menu/actions.py:975] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:362] |
| Race | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:368] |
| Race > Manual finish | action | F3 | ManualFinishAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:599] | icon=config.icon_dir('flag.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:371] |
| Race > Add SPORTident result | action | F7 | AddSPORTidentResultAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:758] | feature=settings.FEATURE_SPORTIDENT | [код: pysport@b548c35 sportorg/gui/menu/menu.py:377] |
| Results | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:385] |
| Results > Create report | action | Ctrl+P | CreateReportAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:628] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:388] |
| Results > Split printout | action | Ctrl+L | SplitPrintoutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:633] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:393] |
| Results > <separator> | separator |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:398] |
| Results > Rechecking | action | Ctrl+R | RecheckingAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:638] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:401] |
| Results > Find group by punches | action | Ctrl+G | GroupFinderAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:645] | tabs=[1] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:406] |
| Results > Penalty calculation | action |  | PenaltyCalculationAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:665] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:412] |
| Results > Penalty removing | action |  | PenaltyRemovingAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:676] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:416] |
| Results > Change status | action | F4 | ChangeStatusAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:687] | tabs=[1] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:420] |
| Results > Set DNS numbers | action |  | SetDNSNumbersAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:722] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:426] |
| Results > Control time change | action |  | ControlTimeChangeAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:734] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:430] |
| Results > Delete CP | action |  | CPDeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:740] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:434] |
| Results > Delete Split | action |  | SplitDeleteAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:746] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:435] |
| Results > Merge results | action |  | MergeResultsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:752] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:436] |
| Results > Assign result by bib | action |  | AssignResultByBibAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:910] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:440] |
| Results > Assign result by card number | action |  | AssignResultByCardNumberAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:918] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:444] |
| Service | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:450] |
| Service > On/Off card readout | action | F8 | CardReadoutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:609] | feature=settings.FEATURE_SPORTIDENT; icon=config.icon_dir('sportident.png') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:453] |
| Service > Huichang management | action |  | HuichangManagementAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:982] | feature=settings.FEATURE_HUICHANG; id='huichang_management' | [код: pysport@b548c35 sportorg/gui/menu/menu.py:460] |
| Service > Teamwork | submenu |  |  |  | icon=config.icon_dir('network.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:466] |
| Service > Teamwork > Send selected | action | Ctrl+Shift+K | TeamworkSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:785] | tabs=list(range(5)) | [код: pysport@b548c35 sportorg/gui/menu/menu.py:470] |
| Service > Teamwork > <separator> | separator |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:476] |
| Service > Teamwork > On/Off | action |  | TeamworkEnableAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:779] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:479] |
| Service > Telegram | submenu |  |  |  | feature=settings.FEATURE_TELEGRAM | [код: pysport@b548c35 sportorg/gui/menu/menu.py:485] |
| Service > Telegram > Send results | action |  | TelegramSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:841] | tabs=[1] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:489] |
| Service > Online | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:496] |
| Service > Online > Send selected | action | Ctrl+K | OnlineSendAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:859] | tabs=[0, 1, 2, 3, 4] | [код: pysport@b548c35 sportorg/gui/menu/menu.py:499] |
| Options | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:509] |
| Options > Timekeeping settings | action | F9 | TimekeepingSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:768] | icon=config.icon_dir('stopwatch.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:512] |
| Options > Teamwork | action |  | TeamworkSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:774] | icon=config.icon_dir('network.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:518] |
| Options > Printer settings | action |  | PrinterSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:812] | icon=config.icon_dir('printer.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:523] |
| Options > Live | action |  | LiveSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:817] | icon=config.icon_dir('live.svg') | [код: pysport@b548c35 sportorg/gui/menu/menu.py:528] |
| Options > Telegram | action |  | TelegramSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:836] | feature=settings.FEATURE_TELEGRAM | [код: pysport@b548c35 sportorg/gui/menu/menu.py:533] |
| Options > Rent cards | action |  | RentCardsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:963] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:538] |
| Options > Plugins | action |  | PluginsSettingsAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:823] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:542] |
| Help | submenu |  |  |  |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:548] |
| Help > About | action | F1 | AboutAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:891] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:551] |
| Help > Check updates | action |  | CheckUpdatesAction | [код: pysport@b548c35 sportorg/gui/menu/actions.py:896] |  | [код: pysport@b548c35 sportorg/gui/menu/menu.py:556] |

Unresolved action names: none.
Unused action classes: LiveToggleAction, OpenRecentAction.
Class names defined twice: none.
