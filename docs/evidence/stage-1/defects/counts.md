# Defect history of pysport@b548c35 (pin `b548c35ba18fe85e2526f96bbd3b4cf94f58b6f6`)

Produced by `scripts/archaeology/defects.py`; definitions in `README.md`. Cache SHA-256 (GitHub, key relative to the cache):
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=1`: `b100361fbc5a9125de14f23c6751a1083d7be3f39540cc941cd97534fb7a3de0`
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=2`: `989e833860b9d32ba0d1169aed4d5ed23a976864f477a4aedae2b68c082b0457`
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=3`: `ba0a473118aed39878a7d13f6b2aac28a179e8d504763479dce4a59432821010`
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=4`: `1ca8f815c863fc116d07b47691dab90be4c9d5103a2d4523e66fc0a39c5d599f`
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=5`: `ab9d7d1d34f8e306fedd12ea502f1b562947db5fa25d295b53d0701870b0e303`
- `repos/sportorg/pysport/issues?state=all&per_page=100&page=6`: `fc4d3c2c56017f3c5677692c6654f9034d750ef9067560173d79b75ba7c772a8`
- `repos/sportorg/pysport/labels?per_page=100`: `c7bbedce526c1b06006e3c8bb9dca8d94a6e6fd755051f44632b940326c8c5a3`

## Class totals (fix commits, non-merge)

| class | product defects | all fix commits |
|---|---|---|
| calc | 13 | 13 |
| time | 2 | 2 |
| device | 14 | 14 |
| import-export | 15 | 15 |
| report-print | 12 | 12 |
| online | 9 | 9 |
| persistence | 10 | 10 |
| i18n | 4 | 4 |
| platform-build | 4 | 10 |
| ui | 35 | 35 |
| other | 50 | 50 |
| docs-only | 0 | 2 |

## Module x class (product defects; a commit counts once per module it touches)

| module | calc | time | device | import-export | report-print | online | persistence | i18n | platform-build | ui | other | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| other | 5 | 0 | 2 | 3 | 7 | 3 | 3 | 4 | 3 | 7 | 27 | 64 |
| sportorg.models | 5 | 0 | 4 | 1 | 2 | 2 | 1 | 1 | 0 | 4 | 17 | 37 |
| sportorg.gui.dialogs | 2 | 0 | 2 | 1 | 2 | 2 | 0 | 2 | 0 | 19 | 5 | 35 |
| sportorg.gui | 4 | 0 | 5 | 1 | 0 | 3 | 2 | 2 | 0 | 10 | 7 | 34 |
| sportorg.gui.menu | 2 | 0 | 3 | 4 | 0 | 3 | 0 | 1 | 0 | 7 | 2 | 22 |
| sportorg.models.result | 8 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 2 | 4 | 18 |
| sportorg.gui.tabs | 3 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | 0 | 4 | 2 | 13 |
| sportorg.modules.sportident | 1 | 0 | 4 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 10 |
| sportorg.modules.backup | 1 | 0 | 1 | 1 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 9 |
| sportorg.modules.live | 1 | 0 | 1 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 9 |
| tests | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 5 | 9 |
| sportorg.modules.printing | 1 | 0 | 0 | 1 | 4 | 0 | 0 | 1 | 0 | 1 | 0 | 8 |
| sportorg.app.models | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 7 |
| sportorg.modules.winorient | 1 | 0 | 1 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 7 |
| sportorg.app.controllers | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 2 | 5 |
| sportorg.libs.iof | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 5 |
| sportorg.libs.sfr | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 5 |
| sportorg.libs.winorient | 1 | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 5 |
| sportorg.models.start | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 5 |
| sportorg.modules.iof | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 5 |
| sportorg | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 4 |
| sportorg.app.plugins | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 4 |
| sportorg.utils | 0 | 1 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| sportorg.libs.ocad | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| sportorg.modules.recovery | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| sportorg.modules.teamwork | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| sportorg.app.modules | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 |
| sportorg.core | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| sportorg.gui.utils | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| sportorg.libs.sportident | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 |
| sportorg.libs.sportiduino | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| sportorg.libs.template | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| sportorg.modules.configs | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 |
| sportorg.modules.telegram | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| sportorg.app.controller | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| sportorg.app.gui | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| sportorg.common | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.lib.template | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| sportorg.lib.winorient | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.libs.huichang | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.libs.settings | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| sportorg.modules.huichang | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.modules.ocad | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.modules.rfid_impinj | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.modules.sportiduino | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.modules.srpid | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| sportorg.ttk | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| sportorg.winorient | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |

## Fix share per module (fix commits / non-merge commits touching the module)

| module | non-merge commits | fix commits | fix share % | product defects |
|---|---|---|---|---|
| other | 548 | 71 | 13.0 | 64 |
| sportorg.models | 230 | 37 | 16.1 | 37 |
| sportorg.gui.dialogs | 304 | 35 | 11.5 | 35 |
| sportorg.gui | 192 | 34 | 17.7 | 34 |
| sportorg.gui.menu | 140 | 22 | 15.7 | 22 |
| sportorg.models.result | 136 | 18 | 13.2 | 18 |
| sportorg.gui.tabs | 105 | 13 | 12.4 | 13 |
| sportorg.modules.sportident | 81 | 10 | 12.3 | 10 |
| sportorg.modules.backup | 44 | 9 | 20.5 | 9 |
| sportorg.modules.live | 52 | 9 | 17.3 | 9 |
| tests | 55 | 9 | 16.4 | 9 |
| sportorg.modules.printing | 57 | 8 | 14.0 | 8 |
| sportorg.app.models | 140 | 7 | 5.0 | 7 |
| sportorg.modules.winorient | 53 | 7 | 13.2 | 7 |
| sportorg | 96 | 5 | 5.2 | 4 |
| sportorg.app.controllers | 110 | 5 | 4.5 | 5 |
| sportorg.libs.iof | 30 | 5 | 16.7 | 5 |
| sportorg.libs.sfr | 23 | 5 | 21.7 | 5 |
| sportorg.libs.winorient | 34 | 5 | 14.7 | 5 |
| sportorg.models.start | 55 | 5 | 9.1 | 5 |
| sportorg.modules.iof | 32 | 5 | 15.6 | 5 |
| sportorg.app.plugins | 82 | 4 | 4.9 | 4 |
| sportorg.utils | 25 | 4 | 16.0 | 4 |
| sportorg.libs.ocad | 15 | 3 | 20.0 | 3 |
| sportorg.modules.recovery | 8 | 3 | 37.5 | 3 |
| sportorg.modules.teamwork | 39 | 3 | 7.7 | 3 |
| sportorg.app.modules | 41 | 2 | 4.9 | 2 |
| sportorg.core | 49 | 2 | 4.1 | 2 |
| sportorg.gui.utils | 15 | 2 | 13.3 | 2 |
| sportorg.libs.sportident | 12 | 2 | 16.7 | 2 |
| sportorg.libs.sportiduino | 13 | 2 | 15.4 | 2 |
| sportorg.libs.template | 14 | 2 | 14.3 | 2 |
| sportorg.modules.configs | 27 | 2 | 7.4 | 2 |
| sportorg.modules.telegram | 9 | 2 | 22.2 | 2 |
| sportorg.app.controller | 30 | 1 | 3.3 | 1 |
| sportorg.app.gui | 56 | 1 | 1.8 | 1 |
| sportorg.common | 24 | 1 | 4.2 | 1 |
| sportorg.lib.template | 5 | 1 | 20.0 | 1 |
| sportorg.lib.winorient | 30 | 1 | 3.3 | 1 |
| sportorg.libs.huichang | 4 | 1 | 25.0 | 1 |
| sportorg.libs.settings | 4 | 1 | 25.0 | 1 |
| sportorg.modules.huichang | 2 | 1 | 50.0 | 1 |
| sportorg.modules.ocad | 10 | 1 | 10.0 | 1 |
| sportorg.modules.rfid_impinj | 10 | 1 | 10.0 | 1 |
| sportorg.modules.sportiduino | 19 | 1 | 5.3 | 1 |
| sportorg.modules.srpid | 8 | 1 | 12.5 | 1 |
| sportorg.ttk | 4 | 1 | 25.0 | 1 |
| sportorg.winorient | 3 | 1 | 33.3 | 1 |
| crates.sportorg-core | 2 | 0 | 0.0 | 0 |
| crates.sportorg-rust-example | 1 | 0 | 0.0 | 0 |
| sportorg.app | 2 | 0 | 0.0 | 0 |
| sportorg.app.contoller | 4 | 0 | 0.0 | 0 |
| sportorg.app.view | 6 | 0 | 0.0 | 0 |
| sportorg.core.backup | 2 | 0 | 0.0 | 0 |
| sportorg.data | 1 | 0 | 0.0 | 0 |
| sportorg.data.configs | 1 | 0 | 0.0 | 0 |
| sportorg.data.img | 1 | 0 | 0.0 | 0 |
| sportorg.data.languages | 12 | 0 | 0.0 | 0 |
| sportorg.data.sounds | 1 | 0 | 0.0 | 0 |
| sportorg.data.styles | 1 | 0 | 0.0 | 0 |
| sportorg.data.templates | 1 | 0 | 0.0 | 0 |
| sportorg.etc | 2 | 0 | 0.0 | 0 |
| sportorg.lib | 2 | 0 | 0.0 | 0 |
| sportorg.lib.iof | 3 | 0 | 0.0 | 0 |
| sportorg.lib.jinja2 | 2 | 0 | 0.0 | 0 |
| sportorg.lib.ocad | 11 | 0 | 0.0 | 0 |
| sportorg.lib.sportident | 3 | 0 | 0.0 | 0 |
| sportorg.libs | 10 | 0 | 0.0 | 0 |
| sportorg.libs.srpid | 7 | 0 | 0.0 | 0 |
| sportorg.libs.telegram | 5 | 0 | 0.0 | 0 |
| sportorg.models.api | 2 | 0 | 0.0 | 0 |
| sportorg.models.processes | 3 | 0 | 0.0 | 0 |
| sportorg.modules | 1 | 0 | 0.0 | 0 |
| sportorg.modules.plugins | 1 | 0 | 0.0 | 0 |
| sportorg.modules.sfr | 20 | 0 | 0.0 | 0 |
| sportorg.modules.sound | 9 | 0 | 0.0 | 0 |
| sportorg.modules.testing | 8 | 0 | 0.0 | 0 |
| sportorg.modules.updater | 4 | 0 | 0.0 | 0 |
| sportorg.modules.utils | 3 | 0 | 0.0 | 0 |
| sportorg.modules.web | 2 | 0 | 0.0 | 0 |
| sportorg.ocad | 2 | 0 | 0.0 | 0 |
| sportorg.so_import | 2 | 0 | 0.0 | 0 |
| sportorg.so_import.winorient | 3 | 0 | 0.0 | 0 |
| sportorg.var | 2 | 0 | 0.0 | 0 |
| sportorg.widget | 3 | 0 | 0.0 | 0 |

## Per year

| year | all commits | merges | non-merge | fix commits | fix share % | product defects |
|---|---|---|---|---|---|---|
| 2017 | 485 | 100 | 385 | 35 | 9.1 | 35 |
| 2018 | 373 | 42 | 331 | 41 | 12.4 | 40 |
| 2019 | 98 | 39 | 59 | 2 | 3.4 | 2 |
| 2020 | 58 | 6 | 52 | 16 | 30.8 | 16 |
| 2021 | 40 | 4 | 36 | 11 | 30.6 | 11 |
| 2022 | 34 | 4 | 30 | 4 | 13.3 | 4 |
| 2023 | 63 | 3 | 60 | 11 | 18.3 | 9 |
| 2024 | 56 | 0 | 56 | 16 | 28.6 | 14 |
| 2025 | 76 | 0 | 76 | 27 | 35.5 | 26 |
| 2026 | 57 | 0 | 57 | 13 | 22.8 | 11 |

## Platform-build fixes (type `ci:`/`build:`; excluded from the product table)

| year | fix commits of type ci/build |
|---|---|
| 2023 | 2 |
| 2024 | 2 |
| 2026 | 2 |

| type | fix commits |
|---|---|
| build | 2 |
| ci | 4 |

Product fixes (other types) whose class is `platform-build`: 4.

## Stage 0 heuristic candidates under the new rule

| commit | found | is fix | type | class | product defect |
|---|---|---|---|---|---|
| [история: pysport@b0391dd] | True | True | fix | other | True |
| [история: pysport@393b630] | True | True | fix | other | True |
| [история: pysport@57ac99d] | True | True | fix | other | True |
| [история: pysport@2b31638] | True | False | feat | other | False |
| [история: pysport@3b55fe8] | True | True | fix | other | True |
| [история: pysport@c8761e7] | True | True | fix | other | True |
| [история: pysport@ef983f3] | True | False | feat | ui | False |
| [история: pysport@42e806a] | True | True | fix | import-export | True |
| [история: pysport@5170d6c] | True | True | fix | calc | True |
| [история: pysport@aee1e99] | True | True | fix | online | True |
| [история: pysport@ab72a79] | True | True | fix | persistence | True |
