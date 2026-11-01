# What using PySide6 imposes (agent judgement, 2026-11-01)

This file is the judgement of the agent (Claude Code, Opus 5.5), not script output and not reviewed by
a human. It answers the maintainer's question of 2026-11-01 that follows the pysport author's remark
in TASK-10 (in paraphrase: with Qt only GPL or LGPL could be used, perhaps this has changed).
Legal readings are `[допущение]`: nobody here is a lawyer, and the Qt page itself
recommends a legal advisor.

## Facts

| # | Fact | Source |
|---|---|---|
| 1 | Legacy started on PyQt5 and moved to PySide2 on 2018-11-09; today it requires `PySide6>=6,<7` | `[история: pysport eaa4843 "To PySide2"]`, `git log -S PyQt5`; `[код: pysport@b548c35 pyproject.toml:27]` |
| 2 | Legacy imports four Qt modules: QtWidgets (91 imports), QtGui (66), QtCore (40), QtPrintSupport (4) | `grep` of `from/import PySide6.Qt*` over `.legacy/pysport/sportorg` at b548c35 |
| 3 | PySide6 6.12.0 (latest on PyPI, 2026-11-01): the `License` field of `PySide6`, `PySide6-Essentials`, `PySide6-Addons` and `shiboken6` is `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; no `License-Expression`; `Requires-Python: <3.16,>=3.10` | `https://pypi.org/pypi/<name>/json`; wheel `METADATA` of `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` (SHA-256 prefix `c9a95102aa23c1f8`) and `pyside6_addons-…-win_amd64.whl` (`98d8d62010da6605`) |
| 4 | The only licence file in the Essentials wheel is `licenses/LicenseRef-Qt-Commercial.txt` (470 characters: "Licensees holding valid commercial Qt licenses may use this software…"). The wheel ships no LGPL or GPL text | the same wheel |
| 5 | The meta-package `PySide6` 6.12.0 requires `PySide6_Essentials`, `PySide6_Addons`, `PySide6_WebEngine`, `PySide6_Pdf` | PyPI JSON `requires_dist` |
| 6 | Essentials holds all four modules legacy uses (QtCore, QtGui, QtWidgets, QtPrintSupport). Addons holds, among others, QtCharts, QtDataVisualization, QtGraphs, QtGraphsWidgets, QtQuick3D, QtHttpServer, QtNetworkAuth, QtCanvasPainter, QtSerialPort | module list of the two win_amd64 wheels |
| 7 | Qt Print Support: "available under … The GNU Lesser General Public License, version 3, or the GNU General Public License, version 2" | `https://doc.qt.io/qt-6/qtprintsupport-index.html` (Qt 6.12.0), "Licenses and Trademarks" |
| 8 | "For open-source licensed Qt, some specific parts (modules) are not available under the GNU LGPL version 3": Qt Canvas Painter, CoAP, Graphs, GRPC, HTTP Server, Lottie Animation, MQTT, Network Authorization, Qml Compiler, Quick 3D, Quick 3D Physics, Quick Timeline, Virtual Keyboard, Wayland Compositor | `https://doc.qt.io/qt-6/licensing.html` (Qt 6.12) |
| 9 | Qt Charts: "available under commercial licenses … In addition, it is available under the GNU General Public License, version 3" (not in the list of fact 8); `qtmodules.html` lists Qt Charts as obsolete | `https://doc.qt.io/qt-6/qtcharts-index.html`, `https://doc.qt.io/qt-6/qtmodules.html` (Qt 6.12.0) |
| 10 | Qt's own summary of LGPLv3 duties: complete corresponding source of the library or a written offer, also for unmodified Qt; the user may change and re-link the library and must be able to run the result, with "sufficient installation information"; a copy of the LGPL and a prominent notice that an LGPL library is used; no added restrictions; some app stores conflict with the LGPL; static linking may make the application no longer a "work that uses the library" | `https://www.qt.io/licensing/open-source-lgpl-obligations` |
| 12 | Essentials alone is enough for legacy's modules. Checked in a clean Python 3.14 venv on Linux, 2026-11-01: `uv pip install PySide6-Essentials==6.12.0` installs only `pyside6-essentials` and `shiboken6`. Then `from PySide6 import QtCore, QtGui, QtWidgets, QtPrintSupport`, a `QApplication` with `QT_QPA_PLATFORM=offscreen`, a `QMainWindow` and a `QPrinter` all work. `import PySide6.QtCharts` fails with `No module named 'PySide6.QtCharts'`. The tools `pyside6-deploy`, `-uic`, `-rcc`, `-designer`, `-lupdate` come with Essentials | session commands (scratchpad venv, not kept) |
| 11 | Wheels of 6.12.0 exist for Windows x64 and arm64 (no 32-bit), macOS 14+ universal2, Linux x86_64 with glibc 2.34+ and aarch64 with glibc 2.39+; all `cp310-abi3`. Download size of Essentials for win_amd64: 78 MiB, Addons: 38 MiB | PyPI JSON `urls` |

## Reading `[допущение]`

1. **Has it changed? Yes, since 2018.** The GPL constraint the author recalls
   fits PyQt5, which legacy used until 2018 (fact 1). PySide2/PySide6 are offered under LGPLv3 (fact 3).
   The modules legacy needs are LGPLv3 too (facts 6–7). Qt alone therefore does not force the
   application to be GPL: under the LGPL the application code may carry any licence, MIT included.
2. **What does force GPL in legacy is its own code.** Legacy is GPL-3.0-or-later by its About dialog,
   and it vendors GPL files (`huichang.py`, `sfrreader.py`, `sportiduino.py`, `srpid.py`; ADR-0004).
   Its runtime dependency `sportident` is GPL-3.0-or-later. Code derived from legacy stays under GPL
   whatever Qt is under. So the MIT wish of TASK-10 is not blocked by Qt. It is blocked by the
   copyright holders of legacy and the vendored libraries.
3. **For this project (GPL-3.0-or-later) PySide6 is no obstacle.** The LGPL is compatible with the
   GPL. `scripts/check_licenses.py` evaluates `OR` expressions, and `LGPL-3.0-only` is in its allowlist
   (`scripts/check_licenses.py:53`), so the check would pass `[допущение]`: not run, because PySide6 is
   not a project dependency yet.
4. **Restrictions that do apply:**
   - **GPL-only modules.** Any module of facts 8–9 (Charts, Graphs, Quick 3D, Virtual Keyboard, HTTP
     Server and the rest) puts the distributed program under GPLv3 only. For the project's own source
     that changes nothing. For the distributed build, "or later" is lost while the module is in it.
     The `PySide6` meta-package installs these modules (facts 5–6). Their mere presence in a build is
     a grey zone; their use is not.
   - **Package metadata cannot tell the modules apart.** Addons declares the same LGPL triple as
     Essentials although it contains GPL-only modules (facts 3, 6, 8–9). A licence check over
     `uv.lock` therefore does not catch a GPL-only module. Only a rule on imports can, for example an
     import-linter contract.
   - **Distribution of a frozen build** (PyInstaller, cx_Freeze, briefcase; Stage 4) carries the
     duties of fact 10:
     - the Qt source or a written offer for it;
     - the LGPL text and a notice that Qt is used;
     - Qt libraries the user can replace, so a separate directory, not a self-extracting one-file
       bundle, `[допущение]` on how the bundlers behave;
     - no store that forbids it.
     The wheel ships only the commercial notice (fact 4), so the LGPL/GPL texts must be added by the
     project.
   - **Platforms** (fact 11) are not a licence matter but a constraint of the same dependency.
     6.12.0 gives no build for 32-bit Windows, for macOS older than 14, or for Linux older than glibc
     2.34. Python 3.14 already excludes Windows 7/8.1 (ADR-0001). The macOS and Linux limits are
     new and depend on the operator inventory (`docs/data-request.md` item 10).
   - **Size.** The meta-package also pulls WebEngine and Pdf. The four modules legacy uses are all in
     `PySide6-Essentials` (78 MiB for win_amd64).

## Proposed, for the Stage 4 dependency ADR (not decided)
- Depend on `PySide6-Essentials`, not on `PySide6`: this gives the smallest set and no GPL-only modules
  in the environment.
- Add an import-linter contract that forbids the GPL-only modules of facts 8–9 (it fails the build
  on the first import).
- Make the LGPL duties of fact 10 acceptance criteria of the installer task.

Not checked: the third-party components that Qt bundles in the wheels (their licences are listed at
`https://doc.qt.io/qtforpython-6/licenses.html`; the page was too long to read in full); PyQt6 terms;
Qt for Python's own "Commercial Use" page.
