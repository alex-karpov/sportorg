"""Tests for scripts/archaeology/os_ru.py on inline synthetic sources (no legacy data)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.archaeology import os_ru

if TYPE_CHECKING:
    from scripts.archaeology.os_ru import Hit


def _py(source: str, path: str = "sportorg/common/x.py") -> list[Hit]:
    return os_ru.scan_python(path, source)


def _rules(hits: list[Hit]) -> set[str]:
    return {h.rule for h in hits}


def test_os_rules_hit_and_miss() -> None:
    source = (
        "import sys, os, platform\n"
        "import winreg\n"
        "from ctypes import windll\n"
        "import json\n"
        "if sys.platform == 'win32':\n"
        "    os.startfile('a')\n"
        "if os.name == 'nt' or platform.system() == 'Linux':\n"
        "    port = 'COM3'\n"
        "    path = 'C:\\\\Users\\\\x'\n"
        "    os.system('open x')\n"
        "x = 'sys.platform is only text'\n"
    )
    hits = _py(source)
    by_rule = {(h.rule, h.line, h.token) for h in hits}
    assert ("OS01", 5, "sys.platform") in by_rule
    assert ("OS01", 7, "os.name") in by_rule
    assert ("OS01", 7, "platform.system") in by_rule
    assert ("OS02", 2, "winreg") in by_rule
    assert ("OS02", 3, "ctypes.windll") in by_rule
    assert ("OS03", 6, "os.startfile") in by_rule
    assert ("OS03", 10, "open") in by_rule
    assert ("OS04", 8, "COM3") in by_rule
    assert any(h.rule == "OS04" and h.line == 9 and h.detail == "drive" for h in hits)
    assert "json" not in {h.token for h in hits if h.rule == "OS02"}
    assert not any(h.rule == "OS01" and h.line == 11 for h in hits)
    compared = {h.token: h.detail for h in hits if h.rule == "OS01" and h.line in {5, 7}}
    assert compared["sys.platform"] == "win32"
    assert compared["os.name"] == "nt"


def test_ru_rules() -> None:
    source = (
        "from sportorg.models.constant import Qualification\n"
        "q = Qualification.MSMK\n"
        "enc = 'cp1251'\n"
        "lang = 'ru'\n"
        "tz = 'Europe/Moscow'\n"
        "url = 'https://orgeo.ru/x'\n"
        "t = 'МСМК'\n"
        "other = 'rust'\n"
    )
    hits = _py(source)
    tokens = {(h.rule, h.token) for h in hits}
    assert ("RU02", "Qualification.MSMK") in tokens
    assert ("RU04", "cp1251") in tokens
    assert ("RU05", "ru") in tokens
    assert ("RU05", "Europe/Moscow") in tokens
    assert ("RU03", "orgeo") in tokens
    assert ("RU03", "orgeo.ru") in tokens
    assert ("RU02", "МСМК") in tokens
    assert not any(h.line == 8 for h in hits)


def test_ru01_ignores_comments_flag() -> None:
    source = '"""Модуль."""\nx = "Привет"  # комментарий\n'
    ru01 = {(h.line, h.kind) for h in _py(source) if h.rule == "RU01"}
    assert ru01 == {(1, "docstring"), (2, "string"), (2, "comment")}


def test_core_flag_by_layer() -> None:
    src = "import sys\nsys.platform\n"
    flags = {
        path: (h.layer, h.core)
        for path in (
            "sportorg/common/a.py",
            "sportorg/models/b.py",
            "sportorg/gui/c.py",
            "sportorg/libs/d/e.py",
            "builder.py",
        )
        for h in _py(src, path)
        if h.rule == "OS01"
    }
    assert flags["sportorg/common/a.py"] == ("foundation", True)
    assert flags["sportorg/models/b.py"] == ("domain", True)
    assert flags["sportorg/gui/c.py"] == ("ui", False)
    assert flags["sportorg/libs/d/e.py"] == ("vendored", False)
    assert flags["builder.py"] == ("outside", False)


def test_ru01_text_is_omitted_when_long() -> None:
    long_text = "Очень длинная строка " * 5
    source = f'a = "слово"\nb = "{long_text}"\nc = "два слова"\n'
    ru01 = {h.line: h.token for h in _py(source) if h.rule == "RU01"}
    assert ru01[1] == "слово"
    assert ru01[2] == f"<text omitted: {len(long_text)} chars>"
    assert ru01[3] == "<text omitted: 9 chars>"


def test_markers_in_pyproject() -> None:
    text = (
        "[project]\n"
        'dependencies = ["pywin32>=300; sys_platform == \'win32\'", "pyserial"]\n'
        "[[package]]\n"
        'name = "pywinusb"\n'
    )
    hits = os_ru.scan_text_file("pyproject.toml", text)
    tokens = {(h.line, h.token) for h in hits if h.rule == "OS05"}
    assert (2, "sys_platform") in tokens
    assert (2, "pywin32") in tokens
    assert (4, "pywinusb") in tokens
    assert all(not h.core and h.layer == "outside" and h.kind == "config" for h in hits)
    assert "pyserial" not in {h.token for h in hits if h.line == 2}


def test_rust_cfg_and_batch() -> None:
    rust = '#[cfg(windows)]\nfn a() {}\n#[cfg(target_os = "linux")]\nfn b() {}\nfn c() {}\n'
    hits = os_ru.scan_text_file("crates/x/src/lib.rs", rust)
    assert {(h.rule, h.line) for h in hits} == {("OS06", 1), ("OS06", 3)}
    bat = "start explorer.exe C:\\data\n"
    assert {"OS03", "OS04"} <= _rules(os_ru.scan_text_file("run.bat", bat))


def test_unparsable_python_is_reported() -> None:
    result = os_ru.scan_files({"sportorg/a.py": "def (:\n"})
    assert result.unparsed == ["sportorg/a.py"]


def test_recall_buckets() -> None:
    grep = {("a.py", 1), ("a.py", 2)}
    ours = {("a.py", 2), ("a.py", 3)}
    both, only_grep, only_ours = os_ru.compare_sets(grep, ours)
    assert both == [("a.py", 2)]
    assert only_grep == [("a.py", 1)]
    assert only_ours == [("a.py", 3)]


def test_ru05_single_hit_and_noise_filters() -> None:
    source = "a = 'ru_RU'\n# lang is 'RUS' here\nb = 'x\\u043e y\\dir'\n"
    hits = _py(source)
    assert [(h.line, h.token) for h in hits if h.rule == "RU05"] == [(1, "ru_RU"), (2, "'RUS'")]
    assert not any(h.rule == "OS04" and "u043e" in h.token for h in hits)


def test_ru01_title_case_word_is_omitted() -> None:
    source = 'a = "Иван"\nb = "МСМК"\nc = "б/р"\nd = "М21"\ne = "Эстафета"\nf = "место"\n'
    ru01 = {h.line: h.token for h in _py(source) if h.rule == "RU01"}
    assert ru01[1] == "<text omitted: 4 chars>"
    assert ru01[2] == "МСМК"
    assert ru01[3] == "б/р"
    assert ru01[4] == "М21"
    assert ru01[5] == "<text omitted: 8 chars>"
    assert ru01[6] == "место"


def test_ru01_text_in_tests_is_omitted() -> None:
    hits = _py('a = "МСМК"\nb = "Qualification кмс"\n', "tests/test_x.py")
    shown = {h.token for h in hits if "Cyrillic" and any(c > "Ѐ" for c in h.token)}
    assert shown == set()
    assert {h.token for h in hits if h.rule == "RU01"} == {
        "<text omitted: 4 chars>",
        "<text omitted: 17 chars>",
    }
