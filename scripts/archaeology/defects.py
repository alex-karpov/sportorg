"""Defect history of the legacy: fix commits by module and error class, issues and PRs (TASK-7 c.3).

Run from the repo root:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.defects \
        --out docs/evidence/stage-1/defects [--cache-dir DIR]

The rule is "Defect rule and taxonomy" of ``docs/plans/stage-1-archaeology.md`` (approved
2026-10-25). Commit subjects and issue titles are read in memory only: outputs carry short shas,
numbers, years, labels and classes, never the text of a subject or a title.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts import legacy
from scripts._json import as_dict, as_list, as_str
from scripts.archaeology import fetch
from scripts.archaeology.common import (
    PYSPORT,
    Commit,
    assert_tree_clean,
    git_log,
    git_raw,
    module_of,
    pin_short,
    repo_root,
    write_outputs,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from scripts._json import Json

SHA_LEN: Final = 7
FIX_RE: Final = re.compile(
    r"\b(fix(e[sd]|ing)?|bug\w*|hotfix|crash\w*|broken|regression|wrong)\b"
    r"|исправ|ошибк|не работа|падени",
    re.IGNORECASE,
)
FIX_TYPE_RE: Final = re.compile(r"^(hot)?fix(\([^)]*\))?!?:", re.IGNORECASE)
TYPE_RE: Final = re.compile(r"^([A-Za-z]+)(?:\([^)]*\))?!?:")
NOT_FIX_TYPES: Final = frozenset({"feat", "docs", "refactor", "style", "test", "perf", "chore"})
PLATFORM_TYPES: Final = frozenset({"ci", "build"})
DOCS_ONLY: Final = "docs-only"
PLATFORM: Final = "platform-build"
UNCLASSIFIED: Final = "unclassified"
OTHER: Final = "other"
IMAGE_SUFFIXES: Final = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".bmp", ".webp")
CLASSES: Final = (
    "calc",
    "time",
    "start-draw",
    "device",
    "import-export",
    "report-print",
    "online",
    "persistence",
    "i18n",
    PLATFORM,
    "ui",
    OTHER,
)


def _words(text: str) -> tuple[str, ...]:
    return tuple(text.split(", "))


# Subject keywords per class. A trailing ``$`` makes the stem a whole word with an optional
# inflection (s, es, ed, ing); other stems match at the start of a word.
KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "calc": _words(
        "result, score, place$, rank, penalt, overtime, relay, split, status, credit, очк, мест,"
        " штраф, результат, сплит"
    ),
    "time": _words("time, midnight, timezone, round$, врем, полноч"),
    "start-draw": _words("draw, start time, start list, жеребь, стартов"),
    "device": _words(
        "card, readout, read$, port$, serial, station, chip, sportident, sfr, srpid, impinj,"
        " чип, станц, считыв"
    ),
    "import-export": _words(
        "import, export, iof, xml, csv, ocad, winorient, sfrx, wdb, импорт, экспорт"
    ),
    "report-print": _words("print, template, report, html, margin, печат, шаблон, протокол, отчёт"),
    "online": _words("live, online, orgeo, server, client, teamwork, telegram, network, онлайн"),
    "persistence": _words("save$, saving, open$, load$, backup, recovery, migrat, сохран, открыт"),
    "i18n": _words("translat, locale, language, перевод"),
    PLATFORM: _words("build, install, ci$, freeze, windows, linux, mac$, path$, сборк"),
    "ui": _words("dialog, menu, tab$, table, window, theme, button, окно, диалог"),
}

# Layout before commit ef2a741 ("Moved from app", 2017-11-24) -> current layout; first match wins.
# [допущение] read off ``git -C .legacy/pysport show --stat ef2a741`` (app/gui, app/models,
# app/modules, lib) and ``git log --follow`` of ``common/otime.py`` and ``common/template.py``
# (``core/``); ``app/plugins`` and ``app/controllers`` are earlier names of modules and gui
# [допущение: by the same file names, e.g. plugins/sportident, controllers/dialogs].
LAYOUT_MAP: Final[tuple[tuple[str, str], ...]] = (
    ("sportorg/app/gui/", "sportorg/gui/"),
    ("sportorg/app/models/", "sportorg/models/"),
    ("sportorg/app/modules/", "sportorg/modules/"),
    ("sportorg/app/plugins/", "sportorg/modules/"),
    ("sportorg/app/controllers/", "sportorg/gui/"),
    ("sportorg/app/controller/", "sportorg/gui/"),
    ("sportorg/app/contoller/", "sportorg/gui/"),
    ("sportorg/app/view/", "sportorg/gui/"),
    ("sportorg/lib/", "sportorg/libs/"),
    ("sportorg/core/otime.py", "sportorg/common/otime.py"),
    ("sportorg/core/template.py", "sportorg/common/template.py"),
)
MEMORY: Final = "sportorg/models/memory.py"
# Rules that decide a class, recorded per commit.
RULE_KEYWORD: Final = "keyword"
RULE_MEMORY: Final = "memory-functions"
RULE_PATH: Final = "path"
RULE_OTHER: Final = "other"
RULE_TYPE: Final = "type"  # ci/build subject type or docs-only: decided before the keywords
RULES: Final = (RULE_KEYWORD, RULE_MEMORY, RULE_PATH, RULE_OTHER, RULE_TYPE)
# ``git`` finds no enclosing function in Python by default (only column-0 lines), so a throwaway
# attributes file in the temp dir gives the diff driver a ``def``/``class`` funcname regex.
_FUNCNAME_ARGS: Final = (
    "-c",
    "diff.pydef.xfuncname=^[ \t]*((class|def)[ \t]+[A-Za-z_].*)$",
)
_HUNK_RE: Final = re.compile(r"^@@ [^@]*@@ *(?:class|def) +(\w+)", re.MULTILINE)
_CAMEL_RE: Final = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")

# Path table (plan): (class, path prefixes, exact paths, substrings).
_DEVICE_MODULES: Final = ("sportident", "sfr", "sportiduino", "srpid", "rfid_impinj", "huichang")
_DEVICE_LIBS: Final = ("sfr", "sportiduino", "srpid", "huichang")
_IO_NAMES: Final = ("iof", "ocad", "winorient")
_PATH_PREFIXES: Final[tuple[tuple[str, str], ...]] = (
    ("calc", "sportorg/models/result/"),
    ("start-draw", "sportorg/models/start/"),
    *(("device", f"sportorg/modules/{n}/") for n in _DEVICE_MODULES),
    *(("device", f"sportorg/libs/{n}/") for n in _DEVICE_LIBS),
    *(("import-export", f"sportorg/modules/{n}/") for n in _IO_NAMES),
    *(("import-export", f"sportorg/libs/{n}/") for n in _IO_NAMES),
    ("import-export", "sportorg/modules/sfrxexporter"),
    ("report-print", "sportorg/modules/printing/"),
    ("report-print", "sportorg/libs/template/"),
    *(("online", f"sportorg/modules/{n}/") for n in ("live", "teamwork", "telegram")),
    ("online", "sportorg/libs/telegram/"),
    ("persistence", "sportorg/modules/backup/"),
    ("persistence", "sportorg/modules/recovery/"),
    (PLATFORM, ".github/"),
    ("ui", "sportorg/gui/"),
)
_PATH_EXACT: Final[tuple[tuple[str, str], ...]] = (
    ("time", "sportorg/common/otime.py"),
    ("time", "sportorg/utils/time.py"),
    ("report-print", "sportorg/common/template.py"),
    ("i18n", "sportorg/language.py"),
    (PLATFORM, "pyproject.toml"),
    (PLATFORM, "uv.lock"),
    (PLATFORM, "sportorg/config.py"),
    (PLATFORM, "sportorg/paths.py"),
)
_CARGO: Final = ("Cargo.toml", "Cargo.lock")

# Labels of sportorg/pysport present in the cache -> class. [допущение]: only the two labels that
# name a platform concern map to a class; bug/feature/enhancement/question/python say nothing about
# the error class, so those items go to the keyword classifier on the title.
LABEL_CLASS: Final = {"github_actions": PLATFORM, "dependencies": PLATFORM}
BUG_LABEL: Final = "bug"
MIN_SHARE_COMMITS: Final = 10
ISSUE_PAGES: Final = range(1, 7)
ISSUES_KEY: Final = "repos/sportorg/pysport/issues?state=all&per_page=100&page={n}"
LABELS_KEY: Final = "repos/sportorg/pysport/labels?per_page=100"
# Stage 0 candidates [код: docs/evidence/stage-0/legacy-fix-candidates.md], 9-hex prefixes.
STAGE0: Final = (
    "b0391dd14",
    "393b6303b",
    "57ac99d04",
    "2b316380f",
    "3b55fe8b0",
    "c8761e709",
    "ef983f3e9",
    "42e806a58",
    "5170d6c31",
    "aee1e994e",
    "ab72a7987",
)


def _ints(table: Mapping[str, int]) -> dict[str, Json]:
    return {k: v for k, v in sorted(table.items())}  # noqa: C416 - widens dict[str, int] to Json


def _strs(table: Mapping[str, str]) -> dict[str, Json]:
    return {k: v for k, v in sorted(table.items())}  # noqa: C416 - widens dict[str, str] to Json


def _nested(table: Mapping[str, Mapping[str, int]]) -> dict[str, Json]:
    return {k: _ints(v) for k, v in sorted(table.items())}


def _compile(stem: str) -> re.Pattern[str]:
    if stem.endswith("$"):
        return re.compile(rf"\b{re.escape(stem[:-1])}(?:s|es|ed|ing)?\b", re.IGNORECASE)
    return re.compile(rf"\b{re.escape(stem)}", re.IGNORECASE)


_KEYWORD_RES: Final = {cls: tuple(_compile(s) for s in stems) for cls, stems in KEYWORDS.items()}


def keyword_classes(text: str) -> set[str]:
    return {cls for cls, pats in _KEYWORD_RES.items() if any(p.search(text) for p in pats)}


# ---------------------------------------------------------------- commits


def conventional_type(subject: str) -> str | None:
    match = TYPE_RE.match(subject)
    return match.group(1).lower() if match else None


def is_fix(commit: Commit) -> bool:
    if commit.is_merge:
        return False
    if FIX_TYPE_RE.match(commit.subject):
        return True
    kind = conventional_type(commit.subject)
    if kind in NOT_FIX_TYPES:
        return False
    return FIX_RE.search(commit.subject) is not None


def _is_docs_path(path: str) -> bool:
    return path.startswith("docs/") or path.endswith(".md") or path.lower().endswith(IMAGE_SUFFIXES)


def is_docs_only(commit: Commit) -> bool:
    return bool(commit.files) and all(_is_docs_path(f.path) for f in commit.files)


def path_class(path: str) -> str | None:
    for cls, exact in _PATH_EXACT:
        if path == exact:
            return cls
    if path.endswith((".po", ".mo")):
        return "i18n"
    if path.rsplit("/", 1)[-1] in _CARGO or "installer" in path:
        return PLATFORM
    if "data/templates/" in path:
        return "report-print"
    for cls, prefix in _PATH_PREFIXES:
        if path.startswith(prefix):
            return cls
    return None


def normalise_path(path: str) -> str:
    """Current-layout path of a path of the 2017 layout (``LAYOUT_MAP``); others unchanged."""
    for old, new in LAYOUT_MAP:
        if path.startswith(old):
            return new + path[len(old) :]
    return path


def module_of_path(path: str) -> str:
    return module_of(normalise_path(path))


def _changed(commit: Commit) -> dict[str, int]:
    lines: dict[str, int] = defaultdict(int)
    for change in commit.files:
        lines[module_of_path(change.path)] += (change.added or 0) + (change.deleted or 0)
    return dict(lines)


def hunk_words(diff: str) -> str:
    """Words of the ``def``/``class`` names in the ``@@ ... @@ <context>`` headers of a diff."""
    words: list[str] = []
    for hunk in _HUNK_RE.finditer(diff):
        for part in str(hunk.group(1)).split("_"):
            words.extend(str(w.group(0)).lower() for w in _CAMEL_RE.finditer(part))
    return " ".join(words)


def memory_class(diff: str) -> str | None:
    """The one class that the keywords name in the changed function names, else ``None``."""
    matched = keyword_classes(hunk_words(diff))
    return next(iter(matched)) if len(matched) == 1 else None


def _memory_diff(commit: Commit, root: Path) -> str:
    paths = [c.path for c in commit.files if normalise_path(c.path) == MEMORY]
    if not paths:
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        attrs = Path(tmp) / "attributes"
        attrs.write_text("*.py diff=pydef\n", encoding="utf-8", newline="\n")
        return git_raw(
            root,
            "-c",
            f"core.attributesFile={attrs}",
            *_FUNCNAME_ARGS,
            "show",
            "--format=",
            "-U0",
            commit.sha,
            "--",
            *paths,
        )


def _class_of_top_module(commit: Commit) -> str:
    lines = _changed(commit)
    if not lines:
        return OTHER
    top = min(lines, key=lambda m: (-lines[m], m))
    by_class: Counter[str] = Counter()
    for change in commit.files:
        if module_of_path(change.path) != top:
            continue
        cls = path_class(normalise_path(change.path))
        if cls is not None:
            by_class[cls] += (change.added or 0) + (change.deleted or 0) + 1
    if not by_class:
        return OTHER
    return min(by_class, key=lambda c: (-by_class[c], CLASSES.index(c)))


def decide(commit: Commit, root: Path | None = None) -> tuple[str, str]:
    """Class and the rule that decided it; ``root`` enables the memory.py function rule."""
    if conventional_type(commit.subject) in PLATFORM_TYPES:
        return PLATFORM, RULE_TYPE
    if is_docs_only(commit):
        return DOCS_ONLY, RULE_TYPE
    matched = keyword_classes(commit.subject)
    if len(matched) == 1:
        return next(iter(matched)), RULE_KEYWORD
    cls = _class_of_top_module(commit)
    if cls != OTHER:
        return cls, RULE_PATH
    if root is not None:
        by_functions = memory_class(_memory_diff(commit, root))
        if by_functions is not None:
            return by_functions, RULE_MEMORY
    return OTHER, RULE_OTHER


def classify(commit: Commit) -> str:
    return decide(commit)[0]


def is_product_defect(commit: Commit) -> bool:
    return (
        is_fix(commit)
        and conventional_type(commit.subject) not in PLATFORM_TYPES
        and not is_docs_only(commit)
    )


@dataclass(frozen=True, slots=True)
class Row:
    sha: str
    date: str
    is_merge: bool
    kind: str
    fix: bool
    cls: str
    rule: str
    product: bool
    modules: tuple[str, ...]
    lines: tuple[tuple[str, int], ...]
    files: tuple[tuple[str, str], ...]

    def tag(self) -> str:
        return f"[история: pysport@{self.sha}]"

    def as_json(self) -> Json:
        return {
            "sha": self.sha,
            "date": self.date,
            "is_merge": self.is_merge,
            "type": self.kind,
            "is_fix": self.fix,
            "class": self.cls,
            "class_rule": self.rule,
            "product_defect": self.product,
            "modules": list(self.modules),
            "lines": _ints(dict(self.lines)),
            "files": [{"path": p, "module": m} for p, m in self.files],
        }

    @property
    def year(self) -> str:
        return self.date[:4]


def commit_row(commit: Commit, root: Path | None = None) -> Row:
    lines = _changed(commit)
    cls, rule = decide(commit, root)
    return Row(
        sha=commit.sha[:SHA_LEN],
        date=commit.date,
        is_merge=commit.is_merge,
        kind=conventional_type(commit.subject) or "none",
        fix=is_fix(commit),
        cls=cls,
        rule=rule,
        product=is_product_defect(commit),
        modules=tuple(sorted(lines)),
        lines=tuple(sorted(lines.items())),
        files=tuple(sorted((c.path, module_of_path(c.path)) for c in commit.files)),
    )


# ---------------------------------------------------------------- issues


@dataclass(frozen=True, slots=True)
class IssueRow:
    """Number, state, kind, labels, years and class; the title is never stored."""

    number: int
    state: str
    is_pr: bool
    merged: bool
    labels: tuple[str, ...]
    created_year: int
    closed_year: int | None
    cls: str
    source: str

    def tag(self) -> str:
        return f"[история: sportorg/pysport#{self.number}]"

    def as_json(self) -> Json:
        return {
            "number": self.number,
            "state": self.state,
            "is_pr": self.is_pr,
            "merged": self.merged,
            "labels": list(self.labels),
            "created_year": self.created_year,
            "closed_year": self.closed_year,
            "class": self.cls,
            "class_source": self.source,
        }


def _year(value: object) -> int | None:
    text = as_str(value)
    return int(text[:4]) if text[:4].isdigit() else None


def _issue_class(labels: Sequence[str], title: str) -> tuple[str, str]:
    for label in labels:
        if label in LABEL_CLASS:
            return LABEL_CLASS[label], "label"
    matched = keyword_classes(title)
    if len(matched) == 1:
        return next(iter(matched)), "keyword"
    return UNCLASSIFIED, "none"


def issue_rows(items: Iterable[Json]) -> list[IssueRow]:
    rows: list[IssueRow] = []
    for raw in items:
        item = as_dict(raw)
        labels = tuple(
            sorted(as_str(as_dict(label).get("name")) for label in as_list(item.get("labels")))
        )
        pull = item.get("pull_request")
        cls, source = _issue_class(labels, as_str(item.get("title")))
        rows.append(
            IssueRow(
                number=int(as_str(str(item.get("number", 0))) or 0),
                state=as_str(item.get("state")),
                is_pr=pull is not None,
                merged=bool(as_str(as_dict(pull).get("merged_at"))),
                labels=labels,
                created_year=_year(item.get("created_at")) or 0,
                closed_year=_year(item.get("closed_at")),
                cls=cls,
                source=source,
            )
        )
    return rows


# ---------------------------------------------------------------- tables


def _md(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines.extend("| " + " | ".join(str(c) for c in row) + " |" for row in rows)
    return "\n".join(lines)


def _pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}" if whole else "0.0"


@dataclass(frozen=True, slots=True)
class Stats:
    merges: int
    non_merge: int
    fixes: int
    product: int
    class_all: dict[str, int]
    class_product: dict[str, int]
    module_class: dict[str, dict[str, int]]
    module_all: dict[str, int]
    module_fix: dict[str, int]
    module_product: dict[str, int]
    year: dict[str, dict[str, int]]
    platform_types: dict[str, int]
    platform_year: dict[str, int]
    platform_class_product: int
    docs_only_fixes: int
    excluded_by_type: dict[str, int]
    rule1: int
    rule2: int
    class_rule_product: dict[str, int]
    class_rule_all: dict[str, int]


def _rule_counts(commits: Sequence[Commit]) -> tuple[int, int, Counter[str]]:
    excluded: Counter[str] = Counter()
    rule1 = rule2 = 0
    for c in commits:
        if c.is_merge:
            continue
        kind = conventional_type(c.subject) or ""
        if FIX_TYPE_RE.match(c.subject):
            rule1 += 1
        elif is_fix(c):
            rule2 += 1
        elif kind in NOT_FIX_TYPES and FIX_RE.search(c.subject):
            excluded[kind] += 1
    return rule1, rule2, excluded


def compute(rows: Sequence[Row], commits: Sequence[Commit]) -> Stats:
    non_merge = [r for r in rows if not r.is_merge]
    class_all: Counter[str] = Counter()
    class_product: Counter[str] = Counter()
    module_class: dict[str, Counter[str]] = defaultdict(Counter)
    module_all: Counter[str] = Counter()
    module_fix: Counter[str] = Counter()
    module_product: Counter[str] = Counter()
    year: dict[str, Counter[str]] = defaultdict(Counter)
    platform_types: Counter[str] = Counter()
    platform_year: Counter[str] = Counter()
    rule_all: Counter[str] = Counter()
    rule_product: Counter[str] = Counter()
    for r in rows:
        year[r.year]["all"] += 1
        if r.is_merge:
            year[r.year]["merges"] += 1
            continue
        year[r.year]["non_merge"] += 1
        for m in r.modules:
            module_all[m] += 1
        if not r.fix:
            continue
        year[r.year]["fix"] += 1
        class_all[r.cls] += 1
        rule_all[r.rule] += 1
        for m in r.modules:
            module_fix[m] += 1
        if r.kind in PLATFORM_TYPES:
            platform_types[r.kind] += 1
            platform_year[r.year] += 1
        if r.product:
            year[r.year]["product"] += 1
            class_product[r.cls] += 1
            rule_product[r.rule] += 1
            for m in r.modules:
                module_product[m] += 1
                module_class[m][r.cls] += 1
    rule1, rule2, excluded = _rule_counts(commits)
    return Stats(
        merges=len(rows) - len(non_merge),
        non_merge=len(non_merge),
        fixes=sum(1 for r in non_merge if r.fix),
        product=sum(1 for r in non_merge if r.product),
        class_all=dict(class_all),
        class_product=dict(class_product),
        module_class={m: dict(c) for m, c in module_class.items()},
        module_all=dict(module_all),
        module_fix=dict(module_fix),
        module_product=dict(module_product),
        year={y: dict(c) for y, c in year.items()},
        platform_types=dict(platform_types),
        platform_year=dict(platform_year),
        platform_class_product=sum(1 for r in non_merge if r.product and r.cls == PLATFORM),
        docs_only_fixes=sum(1 for r in non_merge if r.fix and r.cls == DOCS_ONLY),
        excluded_by_type=dict(excluded),
        rule1=rule1,
        rule2=rule2,
        class_rule_product=dict(rule_product),
        class_rule_all=dict(rule_all),
    )


def stats_json(s: Stats) -> Json:
    return {
        "merges": s.merges,
        "non_merge_commits": s.non_merge,
        "fix_commits": s.fixes,
        "product_defects": s.product,
        "fix_rule1_conventional": s.rule1,
        "fix_rule2_keyword": s.rule2,
        "fix_like_but_excluded_by_type": _ints(s.excluded_by_type),
        "fixes_docs_only": s.docs_only_fixes,
        "class_totals_all_fixes": _ints(s.class_all),
        "class_totals_product": _ints(s.class_product),
        "class_decided_by_rule_all_fixes": _ints(s.class_rule_all),
        "class_decided_by_rule_product": _ints(s.class_rule_product),
        "module_class_product": _nested(s.module_class),
        "module_non_merge": _ints(s.module_all),
        "module_fix": _ints(s.module_fix),
        "module_product": _ints(s.module_product),
        "per_year": _nested(s.year),
        "platform_build_by_type": _ints(s.platform_types),
        "platform_build_by_year": _ints(s.platform_year),
        "product_fixes_of_class_platform_build": s.platform_class_product,
    }


def tables_md(s: Stats) -> str:
    classes = [c for c in CLASSES if c in s.class_product or c in s.class_all]
    parts = ["## Class totals (fix commits, non-merge)", ""]
    parts.append(
        _md(
            ["class", "product defects", "all fix commits"],
            [(c, s.class_product.get(c, 0), s.class_all.get(c, 0)) for c in classes]
            + [(DOCS_ONLY, 0, s.class_all.get(DOCS_ONLY, 0))],
        )
    )
    modules = sorted(s.module_product, key=lambda m: (-s.module_product[m], m))
    parts += [
        "",
        "## Module x class (product defects; a commit counts once per module it touches)",
        "",
    ]
    parts.append(
        _md(
            ["module", *classes, "total"],
            [
                (m, *(s.module_class[m].get(c, 0) for c in classes), s.module_product[m])
                for m in modules
            ],
        )
    )
    share_modules = sorted(s.module_all, key=lambda m: (-s.module_fix.get(m, 0), m))
    parts += [
        "",
        "## Fix share per module (fix commits / non-merge commits touching the module)",
        "",
    ]
    parts.append(
        _md(
            ["module", "non-merge commits", "fix commits", "fix share %", "product defects"],
            [
                (
                    m,
                    s.module_all[m],
                    s.module_fix.get(m, 0),
                    _pct(s.module_fix.get(m, 0), s.module_all[m]),
                    s.module_product.get(m, 0),
                )
                for m in share_modules
            ],
        )
    )
    parts += ["", "## Per year", ""]
    parts.append(
        _md(
            [
                "year",
                "all commits",
                "merges",
                "non-merge",
                "fix commits",
                "fix share %",
                "product defects",
            ],
            [
                (
                    y,
                    c.get("all", 0),
                    c.get("merges", 0),
                    c.get("non_merge", 0),
                    c.get("fix", 0),
                    _pct(c.get("fix", 0), c.get("non_merge", 0)),
                    c.get("product", 0),
                )
                for y, c in sorted(s.year.items())
            ],
        )
    )
    parts += [
        "",
        "## Platform-build fixes (type `ci:`/`build:`; excluded from the product table)",
        "",
    ]
    parts.append(
        _md(
            ["year", "fix commits of type ci/build"],
            sorted(s.platform_year.items()),
        )
    )
    parts += ["", _md(["type", "fix commits"], sorted(s.platform_types.items()))]
    parts += [
        "",
        f"Product fixes (other types) whose class is `{PLATFORM}`: {s.platform_class_product}.",
    ]
    return "\n".join(parts)


def commits_md(rows: Sequence[Row]) -> str:
    return _md(
        ["commit", "date", "type", "class", "rule", "product", "modules"],
        [
            (
                r.tag(),
                r.date,
                r.kind,
                r.cls,
                r.rule,
                "yes" if r.product else "no",
                ", ".join(r.modules),
            )
            for r in rows
            if r.fix
        ],
    )


def compare_stage0(commits: Sequence[Commit], rows: Sequence[Row]) -> list[dict[str, Json]]:
    by_sha = {c.sha: r for c, r in zip(commits, rows, strict=True)}
    out: list[dict[str, Json]] = []
    for prefix in STAGE0:
        found = [r for sha, r in by_sha.items() if sha.startswith(prefix)]
        row = found[0] if found else None
        out.append(
            {
                "commit": prefix[:SHA_LEN],
                "found": row is not None,
                "is_fix": row.fix if row else False,
                "class": row.cls if row else "",
                "product_defect": row.product if row else False,
                "type": row.kind if row else "",
            }
        )
    return out


def issue_counts(rows: Sequence[IssueRow]) -> dict[str, dict[str, dict[str, int]]]:
    out: dict[str, dict[str, dict[str, int]]] = {"issues": {}, "prs": {}}
    for r in rows:
        kind = "prs" if r.is_pr else "issues"
        state = f"{r.state}+merged" if r.is_pr and r.merged else r.state
        out[kind].setdefault(r.cls, {}).setdefault(state, 0)
        out[kind][r.cls][state] += 1
    return out


def _issue_counts_json(rows: Sequence[IssueRow]) -> dict[str, Json]:
    return {kind: _nested(per) for kind, per in issue_counts(rows).items()}


def issues_md(rows: Sequence[IssueRow]) -> str:
    counts = issue_counts(rows)
    parts: list[str] = []
    for kind in ("issues", "prs"):
        states = sorted({s for per in counts[kind].values() for s in per})
        parts += [f"## {kind}: class x state", ""]
        parts.append(
            _md(
                ["class", *states, "total"],
                [
                    (c, *(per.get(s, 0) for s in states), sum(per.values()))
                    for c, per in sorted(counts[kind].items())
                ],
            )
        )
        parts.append("")
    parts += ["## Items", ""]
    parts.append(
        _md(
            ["item", "state", "pr", "merged", "labels", "created", "class", "class source"],
            [
                (
                    r.tag(),
                    r.state,
                    "yes" if r.is_pr else "no",
                    "yes" if r.merged else "no",
                    ", ".join(r.labels),
                    r.created_year,
                    r.cls,
                    r.source,
                )
                for r in rows
            ],
        )
    )
    return "\n".join(parts)


# ---------------------------------------------------------------- main


class Options(argparse.Namespace):
    out: Path = Path()
    cache_dir: Path = fetch.DEFAULT_CACHE


def _cache_keys() -> list[str]:
    return [ISSUES_KEY.format(n=n) for n in ISSUE_PAGES] + [LABELS_KEY]


def _top(table: Mapping[str, int], n: int = 5) -> str:
    best = sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    return ", ".join(f"`{m}` {v}" for m, v in best)


def _top_share(s: Stats) -> str:
    share = {
        m: s.module_fix.get(m, 0) / n for m, n in s.module_all.items() if n >= MIN_SHARE_COMMITS
    }
    best = sorted(share.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    return ", ".join(f"`{m}` {100 * v:.1f} %" for m, v in best)


def _fmt(table: Mapping[str, int]) -> str:
    return ", ".join(f"{k} {table[k]}" for k in RULES if k in table)


def _readme(
    s: Stats,
    stage0: Sequence[Mapping[str, Json]],
    issues: Sequence[IssueRow],
    pin: str,
) -> str:
    n_issues = sum(1 for r in issues if not r.is_pr)
    s0_fix = sum(1 for r in stage0 if r["is_fix"])
    s0_product = sum(1 for r in stage0 if r["product_defect"])
    issue_cls = dict(sorted(Counter(r.cls for r in issues if not r.is_pr).items()))
    pr_cls = dict(sorted(Counter(r.cls for r in issues if r.is_pr).items()))
    merged = sum(1 for r in issues if r.is_pr and r.merged)
    excluded = ", ".join(f"{k} {v}" for k, v in sorted(s.excluded_by_type.items()))
    classes = ", ".join(f"{c} {s.class_product[c]}" for c in CLASSES if c in s.class_product)
    return TEMPLATE.format(
        pin=pin,
        fix_re=FIX_RE.pattern,
        platform=PLATFORM,
        docs_only=DOCS_ONLY,
        unclassified=UNCLASSIFIED,
        label_class=LABEL_CLASS,
        total=s.non_merge + s.merges,
        merges=s.merges,
        non_merge=s.non_merge,
        fixes=s.fixes,
        fix_pct=f"{100 * s.fixes / s.non_merge:.1f}",
        rule1=s.rule1,
        rule2=s.rule2,
        product=s.product,
        docs_fixes=s.docs_only_fixes,
        ci_build=sum(s.platform_types.values()),
        excluded_n=sum(s.excluded_by_type.values()),
        excluded=excluded,
        classes=classes,
        rules_product=_fmt(s.class_rule_product),
        rules_all=_fmt(s.class_rule_all),
        other_product=s.class_product.get(OTHER, 0),
        layout_map="\n".join(f"  `{old}` -> `{new}`" for old, new in LAYOUT_MAP),
        memory=MEMORY,
        top_module=_top(s.module_product),
        min_share=MIN_SHARE_COMMITS,
        top_share=_top_share(s),
        s0_fix=s0_fix,
        s0_n=len(stage0),
        s0_product=s0_product,
        n_issues=n_issues,
        n_prs=len(issues) - n_issues,
        issue_cls=issue_cls,
        pr_cls=pr_cls,
        merged=merged,
    )


TEMPLATE: Final = """# Defect history (TASK-7 criterion 3)

What: fix commits of `pysport@{pin}` by module and error class, a reproducible counts table,
issues and PRs of `sportorg/pysport` by class. Produced by `scripts/archaeology/defects.py`
(command in `commands.txt`).
- `commits.json`: per commit short sha, date, merge flag, Conventional type, `is_fix`, class,
  `product_defect`, modules, changed lines per module. `commits.md`: the fix commits.
- `counts.json`, `counts.md`: class totals, module x class, fix share per module, per-year
  counts, platform-build table, Stage 0 comparison, cache SHA-256 values.
- `issues.json`, `issues.md`: number, state, is-PR, merged, labels, created/closed year, class.
  Titles and bodies are not written.

## Definitions (plan, "Defect rule and taxonomy", approved 2026-10-25)

Fix commit (non-merge; merges are counted separately and are never fixes):
1. Conventional subject type `fix`/`hotfix` (`^(hot)?fix(\\([^)]*\\))?!?:`), or
2. no Conventional type, or a type outside {{feat, docs, refactor, style, test, perf, chore}},
   and the subject matches `FIX_RE` =
   `{fix_re}` (case-insensitive).

`ci:`/`build:` fixes are class `{platform}` and are excluded from the product defect table.
A commit that touches only `docs/`, `*.md` or images is class `{docs_only}` and is not a
product defect. Product defect = fix, not of type `ci`/`build`, not docs-only.

Class: if exactly one class matches the subject keywords, that class; otherwise the class of
the module with the most changed lines (path table, `classify()`); otherwise `other`.
- Keyword stems match at the start of a word; short or ambiguous stems (`ci`, `mac`, `read`,
  `port`, `open`, `load`, `save`, `tab`, `path`, `place`, `round`) are whole words with an
  optional s/es/ed/ing [допущение: the plan lists stems without saying how they match].
- Fallback: the module with the most changed lines is chosen (ties by name), then the class
  with the most changed lines among its paths that the table maps [допущение: the plan says
  "class of the module"; modules are coarser than the path table]. `persistence` for
  `memory.py` needs a keyword, so it is not in the path table.
- A `ci:`/`build:` commit is class `{platform}` whether or not it is a fix.

Extensions of 2026-10-25 (maintainer, question В5 of `docs/reports/stage-1.md`):
- Old layout. Paths are normalised before the path table and before the module is computed
  (`normalise_path`, constant `LAYOUT_MAP`; first prefix wins):
{layout_map}
  [допущение: mapping read off `git -C .legacy/pysport show --stat ef2a741` ("Moved from app",
  2017-11-24) for `app/gui`, `app/models`, `app/modules`, `lib`; `app/plugins`,
  `app/controllers` (also `controller`, the typo `contoller`, `view`) are earlier names and are
  mapped by the same file names, and `core/otime.py`, `core/template.py` by `git log --follow`
  of the current files]. Top-level files of the 2017 layout (`app.py`, `SportOrg.pyw`, ...)
  and the rest of `core/` are not clearly mappable and stay `other`. `commits.json` keeps the
  original path and the normalised module per file (`files`); `modules` and `lines` use
  the normalised modules.
- `{memory}` by changed functions. If the keywords decide nothing and the path fallback gives
  `other`, and the commit changed `{memory}` (or its old-layout path), the headers of
  `git show --format= -U0 <sha> -- <path>` are read. A throwaway attributes file gives git a
  `def`/`class` funcname pattern, so the context is the innermost enclosing `def` or `class`.
  The names are split into words (snake_case, CamelCase), only names are used, not parameters.
  The keyword classifier runs on these words: exactly one class decides, otherwise the commit
  stays `other`.
- `class_rule` in `commits.json`: `keyword`, `memory-functions`, `path` (module fallback),
  `other`; `type` for `ci:`/`build:` and docs-only commits, which are decided before the keywords.

Issues and PRs: class from labels first, mapping `{label_class}` [допущение: only these two
labels name a class; `bug`, `feature`, `enhancement`, `question`, `python` do not], then the
keyword classifier on the title in memory (exactly one class), otherwise `{unclassified}`.

## Key numbers

- Commits: {total}; merges {merges}; non-merge {non_merge}.
- Fix commits: {fixes} ({fix_pct} % of non-merge): rule 1 {rule1}, rule 2 {rule2}.
- Product defects: {product}. Fix commits excluded from them: {docs_fixes} docs-only,
  {ci_build} of type ci/build.
- Fix-like subjects excluded by type (a `feat`/`docs`/... type with a fix word): {excluded_n}
  ({excluded}).
- Class totals of product defects: {classes}.
- Product defects by deciding rule: {rules_product}. All fix commits: {rules_all}.
- Before this extension (same pin): product classes calc 13, time 2, device 14, import-export 15,
  report-print 12, online 9, persistence 10, i18n 4, platform-build 4, ui 35, other 50; all fix
  commits: calc 13, time 2, device 14, import-export 15, report-print 12, online 9, persistence 10,
  i18n 4, platform-build 10, ui 35, other 50, docs-only 2. Now `other` is {other_product}
  of the product defects. The remaining `other` are top-level files of the 2017 layout,
  `.travis.yml`, tests, and `memory.py` changes whose function names name no class or several.
- Top modules by product-defect count: {top_module}.
- Top modules by fix share (at least {min_share} non-merge commits): {top_share}.
- Stage 0 heuristic: {s0_fix} of {s0_n} candidates are fixes under the new rule, {s0_product}
  are product defects.
- Issues {n_issues}, PRs {n_prs}. Issues by class: {issue_cls}. PRs by class: {pr_cls}.
  Merged PRs: {merged}. Detail by state in `issues.md`.

## Limits

- Merge commits ({merges}) are not counted. A PR with several commits counts per commit.
- Subjects are the only text signal; bodies are not read. A `feat:` subject with a fix word is
  not a fix by the rule, and a fix with a neutral subject is missed.
- Keywords such as `time`, `result`, `read` match many unrelated subjects; two matching
  classes fall to the path table.
- Precision and recall come from the agent's sample checks of 50 commits (Phase D, main
  session): `sample-check-1.agent.md` for the classifier before the change of 2026-10-25,
  `sample-check-2.agent.md` for the current one.
- Issues and PRs are a snapshot from the cache; the issues API gives `merged_at` only inside
  `pull_request`. Cache SHA-256 values are in the header of every `.md`.
- No author, login or e-mail is read into any output; subjects and titles are used in memory
  only.

## Open questions (for the maintainer, not decided here)

1. Is a `fix:` commit that touches only `tests/` a defect fix? Counted as a fix by the rule,
   shown under module `tests`.
2. Should `ci`/`build` fixes and product fixes whose class falls to `{platform}` by paths be
   reported together? They are separate here.
3. Squash commits that bundle features and fixes under one `feat:` subject are outside the rule.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=fetch.DEFAULT_CACHE)
    args = parser.parse_args(argv, namespace=Options())
    root = repo_root(PYSPORT)
    pin = legacy.find_pin(PYSPORT).commit
    commits = git_log(root, pin)
    rows = [commit_row(c, root) for c in commits]
    stats = compute(rows, commits)
    stage0 = compare_stage0(commits, rows)

    items: list[Json] = []
    for n in ISSUE_PAGES:
        items.extend(as_list(fetch.load_cached("github", ISSUES_KEY.format(n=n), args.cache_dir)))
    issues = sorted(issue_rows(items), key=lambda r: r.number)
    hashes = {k: fetch.cached_sha256("github", k, args.cache_dir) for k in _cache_keys()}
    hash_lines = "\n".join(f"- `{k}`: `{h}`" for k, h in hashes.items())

    header = (
        f"# Defect history of pysport@{pin_short(PYSPORT)} (pin `{pin}`)\n\n"
        "Produced by `scripts/archaeology/defects.py`; definitions in `README.md`. Cache SHA-256 "
        f"(GitHub, key relative to the cache):\n{hash_lines}"
    )
    out: Path = args.out
    write_outputs(out, "commits", [r.as_json() for r in rows], commits_md(rows), header)
    counts_json_full: Json = {
        "counts": stats_json(stats),
        "stage0": [dict(r) for r in stage0],
        "cache_sha256": _strs(hashes),
    }
    write_outputs(
        out, "counts", counts_json_full, tables_md(stats) + "\n\n" + _stage0_md(stage0), header
    )
    write_outputs(
        out,
        "issues",
        {"rows": [r.as_json() for r in issues], "counts": _issue_counts_json(issues)},
        issues_md(issues),
        header,
    )
    (out / "README.md").write_text(
        _readme(stats, stage0, issues, pin_short(PYSPORT)), encoding="utf-8", newline="\n"
    )
    (out / "commands.txt").write_text(_COMMANDS, encoding="utf-8", newline="\n")
    assert_tree_clean(root)
    print(f"fix commits {stats.fixes}, product defects {stats.product}, issues+PRs {len(issues)}")
    return 0


def _stage0_md(stage0: Sequence[Mapping[str, Json]]) -> str:
    return "## Stage 0 heuristic candidates under the new rule\n\n" + _md(
        ["commit", "found", "is fix", "type", "class", "product defect"],
        [
            (
                f"[история: pysport@{r['commit']}]",
                r["found"],
                r["is_fix"],
                r["type"],
                r["class"],
                r["product_defect"],
            )
            for r in stage0
        ],
    )


_COMMANDS: Final = """# Run from the repository root; offline (reads .legacy/pysport at the pin via
# git and the GitHub cache ~/.cache/sportorg-stage1, fetched by the main session).
PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.defects \\
    --out docs/evidence/stage-1/defects
uv run python -m scripts.legacy verify
"""


if __name__ == "__main__":
    sys.exit(main())
