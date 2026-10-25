"""Tests for scripts/archaeology/inventory.py on synthetic sources (no legacy data)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.archaeology import inventory as inv
from scripts.archaeology.common import git_raw, tracked_files

if TYPE_CHECKING:
    from pathlib import Path

    from tests.scripts.archaeology.conftest import Commit

MENU = """
from sportorg import settings

def helper():
    return 1

def menu_list():
    items = [
        {
            "title": translate("File"),
            "actions": [
                {
                    "title": translate("New"),
                    "shortcut": "Ctrl+N",
                    "icon": config.icon_dir("file.svg"),
                    "action": "NewAction",
                },
                {"type": "separator"},
                {
                    "title": translate("Import"),
                    "actions": [
                        {
                            "title": translate("CSV"),
                            "action": "CsvAction",
                            "feature": settings.FEATURE_WINORIENT,
                            "tabs": [0, 2],
                        },
                        {"title": translate("Gone"), "action": "MissingAction"},
                    ],
                },
            ],
        },
        {"title": translate("Edit"), "actions": [
            {"title": translate("Add"), "shortcut": ["insert", "i"], "action": "NewAction"},
        ]},
    ]
    items.extend(plugin_menu_items())
    return filter_menu_items(items)
"""

ACTIONS = """
from os import remove
from sportorg.modules.iof import iof_xml
from sportorg.modules.winorient import winorient as wo
try:
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError:
    from PySide2.QtWidgets import QApplication


class ActionFactory(type):
    actions = {}


class NewAction(Action, metaclass=ActionFactory):
    def execute(self):
        remove("x")


class CsvAction(Action, metaclass=ActionFactory):
    def execute(self):
        name = get_open_file_name("Open", translate("CSV Winorient (*.csv)"))
        iof_xml.import_from_iof(name)
        QApplication.beep()


class NewAction(Action, metaclass=ActionFactory):
    def execute(self):
        pass


class UnusedAction(Action, metaclass=ActionFactory):
    pass


class Plain:
    pass
"""


def test_menu_tree_from_literal() -> None:
    items = inv.parse_menu(MENU, "menu.py")
    by_title = {i.title: i for i in items if i.title}
    assert [i.title for i in items if not i.path[:-1]] == ["File", "Edit"]
    new = by_title["New"]
    assert new.path == ("File", "New")
    assert new.shortcut == "Ctrl+N"
    assert new.action == "NewAction"
    assert new.extra == {"icon": "config.icon_dir('file.svg')"}
    assert new.line == 12
    csv = by_title["CSV"]
    assert csv.path == ("File", "Import", "CSV")
    assert csv.extra == {"feature": "settings.FEATURE_WINORIENT", "tabs": "[0, 2]"}
    assert by_title["Add"].shortcut == "['insert', 'i']"
    assert by_title["Import"].action is None
    assert by_title["Import"].kind == "submenu"
    assert [i.kind for i in items].count("separator") == 1
    assert sum(1 for i in items if i.action) == 4


def test_menu_without_menu_list_is_an_error() -> None:
    with pytest.raises(inv.InventoryError, match="menu_list"):
        inv.parse_menu("x = 1\n", "menu.py")


def test_action_resolution_missing_class() -> None:
    items = inv.parse_menu(MENU, "menu.py")
    classes = inv.action_classes(ACTIONS, "actions.py")
    assert [c.name for c in classes] == ["NewAction", "CsvAction", "NewAction", "UnusedAction"]
    result = inv.resolve_actions(items, classes)
    assert result.unresolved == ["MissingAction"]
    assert result.unused == ["UnusedAction"]
    assert result.duplicates == ["NewAction"]
    assert result.resolved["NewAction"].line == 27  # the last definition wins in the registry
    assert result.resolved["CsvAction"].line == 20


def test_class_imports_use_module_level_bindings() -> None:
    classes = inv.action_classes(ACTIONS, "actions.py")
    uses = inv.class_imports(ACTIONS, "sportorg.gui.menu.actions", "actions.py", classes)
    csv = uses[("CsvAction", 20)]
    assert csv == {"iof_xml": "sportorg.modules.iof", "QApplication": "PySide6.QtWidgets"}
    assert "get_open_file_name" not in csv
    assert uses[("NewAction", 15)] == {"remove": "os"}
    assert uses[("UnusedAction", 32)] == {}


def test_parse_filters_and_extensions() -> None:
    source = """
a = translate("CSV Winorient (*.csv)")
b = dialog("Open", "IOF xml (*.xml *.XML)",
           "x")
c = "*.sfrx"
d = ".wdb"
e = base + ".tmp"
f = "no filter here"
g = ".x"
"""
    filters = inv.parse_filters(source, "x.py")
    assert [(f.label, f.extensions, f.line) for f in filters] == [
        ("CSV Winorient (*.csv)", (".csv",), 2),
        ("IOF xml (*.xml *.XML)", (".xml",), 3),
        ("*.sfrx", (".sfrx",), 5),
    ]
    assert [(s.text, s.line) for s in inv.parse_extension_strings(source, "x.py")] == [
        (".wdb", 6),
        (".tmp", 7),
    ]


def test_scan_template_loaders() -> None:
    source = """
import os
from jinja2 import Environment, FileSystemLoader
from docxtpl import DocxTemplate
TEMPLATES_PATH = os.getenv("X_TEMPLATES_PATH", "")
# jinja2 in a comment is skipped
def f():
    names = get_templates(settings.template_dir("reports"))
    doc = DocxTemplate(path)
    env = Environment(loader=FileSystemLoader(searchpath))
"""
    refs = inv.scan_template_loaders(source, "x.py")
    assert [(r.kind, r.line) for r in refs] == [
        ("jinja2", 3),
        ("docxtpl", 4),
        ("env_config", 5),
        ("list_templates", 8),
        ("template_dir", 8),
        ("docxtpl", 9),
        ("jinja2", 10),
    ]


def test_template_files_and_docs(repo: Path, commit: Commit) -> None:
    sha = commit(
        "files",
        {
            "templates/a.html": b"<p>\n</p>\n",
            "templates/b.docx": b"PK\x03\x04\xff\xfe",
            "docs/one.md": b"# one\r\ntwo\r\n",
            "README.md": b"r",
            "src/code.py": b"x = 1\n",
        },
    )
    tracked = tracked_files(repo)
    files = inv.template_files(repo, sha, tracked, "templates")
    assert [(f.path, f.format, f.lines, f.size) for f in files] == [
        ("templates/a.html", "html", 2, 9),
        ("templates/b.docx", "docx", None, 6),
    ]
    docs = inv.doc_files(repo, sha, tracked)
    assert [(d.path, d.lines) for d in docs] == [
        ("README.md", 1),
        ("docs/one.md", 2),
    ]
    assert git_raw(repo, "status", "--porcelain") == ""


def test_format_chains() -> None:
    items = inv.parse_menu(MENU, "menu.py")
    classes = inv.action_classes(ACTIONS, "actions.py")
    uses = inv.class_imports(ACTIONS, "sportorg.gui.menu.actions", "actions.py", classes)
    filters = inv.parse_filters(ACTIONS, inv.ACTIONS_PATH)
    local = inv.class_local_imports(ACTIONS, "sportorg.gui.menu.actions", "actions.py", classes)
    chains = inv.format_chains(
        items, inv.resolve_actions(items, classes), uses, filters, ACTIONS, local=local
    )
    assert len(chains) == 1
    chain = chains[0]
    assert chain.menu_path == ("File", "Import", "CSV")
    assert chain.formats == ("IOF XML",)
    assert chain.calls == ("iof_xml.import_from_iof",)
    assert [f.label for f in chain.filters] == ["CSV Winorient (*.csv)"]


def test_local_imports_and_foreign_filters() -> None:
    source = ACTIONS.replace(
        "        pass\n\n\nclass Unused",
        "        from sportorg.modules.sfr.sfrxexporter import export_sfrx\n\n\nclass Unused",
    )
    classes = inv.action_classes(source, "actions.py")
    local = inv.class_local_imports(source, "sportorg.gui.menu.actions", "actions.py", classes)
    assert local["NewAction", 27] == {"export_sfrx": "sportorg.modules.sfr.sfrxexporter"}
    assert local["CsvAction", 20] == {}
    foreign = inv.FilterRef("X (*.xml)", (".xml",), "sportorg/other.py", 21)
    items = inv.parse_menu(MENU, "menu.py")
    uses = inv.class_imports(source, "sportorg.gui.menu.actions", "actions.py", classes)
    chains = inv.format_chains(
        items, inv.resolve_actions(items, classes), uses, [foreign], source, local=local
    )
    assert [c.action for c in chains] == ["NewAction", "CsvAction", "NewAction"]
    assert chains[0].formats == ("SFRx",)
    assert chains[0].filters == ()
    assert chains[1].filters == ()


def test_format_of_names_the_sfr_results_board_apart_from_backup() -> None:
    assert inv.format_of("sportorg.modules.backup.json") == "SportOrg JSON (.json, gzip)"
    assert (
        inv.format_of("sportorg.modules.backup.sfr_results_board")
        == "SFR results board (.srb, TSV)"
    )
