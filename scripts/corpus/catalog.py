"""Walk the corpus, anonymize its race files, build the corpus manifest (Stage 2 S3, AC #2).

Reads only ``<corpus>/raw/`` and ``<corpus>/inventory.csv`` (Д3: the corpus root is closed to the
sandbox) and writes anonymized copies to a cache outside the repository with its ``MANIFEST.json``
(stage rule 11). The manifest that enters the repository holds counts, hashes and neutral ids only:

- a directory is shown by its name when it is neutral (``C01``), else by a keyed hash; a file by
  ``<directory>/<keyed hash of its path>`` (R21: file names hold race names). The id comes from
  the name, not from a position in a listing, so adding a file does not renumber the others;
- a file's kind is told by its content (``scripts.corpus.racefile.kind``), never by its name;
- race files: format (gzip, UTF-8, cp1251; ADR-0009 T6), shape, SportOrg version of the last save
  [код: pysport@b548c35 sportorg/modules/backup/json.py:21], hashes of the original and of the
  copy, per race the settings that choose the calculation, counts, stored statuses, the leak check
  of the copy, and keyed hashes of the race id and of its person ids, which mark the same race in
  a day file and in the file of the whole event (``starts``);
- ``files.tsv`` against the disk: listed, matched, missing on disk, not listed, other hash;
- the passport (``inventory.csv``): only values from the vocabulary of ``docs/data-request.md``;
  free text as ``filled``; ``source`` never; counts of unfilled cells;
- files with ``scores_mode = formula`` and their formulas (R22): such a file is not runnable by
  the oracle without the maintainer's consent; races with ``result_processing_mode = ardf``.

Other files (protocols, notes, logs) are counted by kind with their hash, never copied or read
for content beyond the kind; a readout log adds counts of readouts and punches.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import shutil
from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_list, as_str, parse_json
from scripts.corpus import anonymize, leakcheck, pseudonym, racefile

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

SCHEMA: Final = "sportorg-ng/corpus-manifest"
SCHEMA_VERSION: Final = 1
FILES_TSV: Final = "files.tsv"
_NEUTRAL_DIR = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,15}")
_SAFE_WORD = re.compile(r"[A-Za-z0-9_.\- ]{1,40}")
_SAFE_FORMULA = re.compile(r"[A-Za-z0-9_ +\-*/%().,<>=!]{0,200}")
_VERSION = re.compile(r"v?\d+(\.\d+)*[a-z0-9]*")
# [код: pysport@b548c35 sportorg/models/memory.py:67-93]
RACE_TYPES: Final = {0: "INDIVIDUAL_RACE", 2: "PURSUIT", 3: "RELAY", 6: "MULTI_DAY_RACE"}
STATUSES: Final = (
    "NONE", "OK", "FINISHED", "DISQUALIFIED", "MISSING_PUNCH", "DID_NOT_FINISH", "ACTIVE",
    "INACTIVE", "OVERTIME", "SPORTING_WITHDRAWAL", "NOT_COMPETING", "MOVED", "MOVED_UP",
    "DID_NOT_START", "DID_NOT_ENTER", "CANCELLED", "RESTORED", "MISS_PENALTY_LAP",
    "MULTI_DAY_ISSUE",
)  # fmt: skip
# The passport's vocabulary (docs/data-request.md, «Как разложить файлы»).
_YES_NO: Final = frozenset({"yes", "no"})
VOCABULARY: Final[dict[str, frozenset[str]]] = {
    "sport": frozenset({"ориентирование", "рогейн", "ARDF", "туризм", "циклический вид"}),
    "race_type": frozenset({"individual", "pursuit", "relay", "multi_day"}),
    "processing_mode": frozenset({"time", "scores", "ardf"}),
    "punch_system": frozenset(
        {"manual", "sportident", "sfr", "sportiduino", "rfid_impinj", "srpid", "huichang"}
    ),
    "resaved_after_race": frozenset({"yes", "no", "unknown"}),
    "protocol_kind": frozenset({"final", "preliminary", "none"}),
    "protocol_signed": _YES_NO,
    "protocol_matches_file": frozenset({"yes", "no", "unknown"}),
    "may_share": _YES_NO,
}
NUMBER_COLUMNS: Final = frozenset({"days", "persons"})
NEVER_COPIED: Final = frozenset({"source"})
_SPECIAL_CASE = re.compile(r"[a-z_]{1,30}")


def _safe(value: Json, default: str = "(other)") -> Json:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    text = as_str(value)
    return text if _SAFE_WORD.fullmatch(text) else default


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_of(path: Path) -> str:
    return _sha(path.read_bytes())


# ---------------------------------------------------------------- passport


def _passport_value(column: str, value: str) -> str:
    if column in VOCABULARY:
        first = value.split(maxsplit=1)[0] if column == "resaved_after_race" else value
        return first if first in VOCABULARY[column] else "(other)"
    if column in NUMBER_COLUMNS:
        return value if value.isdigit() else "(other)"
    if column == "version_race_day":
        return value if _VERSION.fullmatch(value) else "(other)"
    if column == "special_cases":
        cases = [c.strip() for c in value.split(";") if c.strip()]
        return ";".join(c if _SPECIAL_CASE.fullmatch(c) else "(other)" for c in cases)
    return "filled"


def read_inventory(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, Json]]:
    """Passport values per directory id, and the counts of the inventory."""
    if not path.is_file():
        return {}, {"present": False}
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")))
    columns = [c for c in (reader.fieldnames or []) if c and c != "id"]
    unfilled: Counter[str] = Counter()
    passports: dict[str, dict[str, str]] = {}
    for row in reader:
        directory = (row.get("id") or "").strip()
        passport: dict[str, str] = {}
        for column in columns:
            value = (row.get(column) or "").strip()
            if not value:
                unfilled[column] += 1
            elif column not in NEVER_COPIED:
                passport[column] = _passport_value(column, value)
        passports[directory] = passport
    counts: dict[str, Json] = {
        "present": True,
        "rows": len(passports),
        "columns": len(columns),
        "unfilled": dict[str, Json](sorted(unfilled.items())),
    }
    return passports, counts


# ---------------------------------------------------------------- files.tsv


def _tsv_rows(text: str) -> list[tuple[str, str]]:
    rows = [r for r in csv.reader(io.StringIO(text), delimiter="\t") if any(c.strip() for c in r)]
    if rows and any(c.strip().lower() in {"sha256", "dest"} for c in rows[0]):
        header = [c.strip().lower() for c in rows[0]]
        dest, sha = header.index("dest"), header.index("sha256")
        rows = rows[1:]
    else:
        dest, sha = 0, 1
    return [(r[dest].strip(), r[sha].strip().lower()) for r in rows if len(r) > max(dest, sha)]


def _match(dest: str, directory: str, on_disk: dict[str, str]) -> str | None:
    path = dest.replace("\\", "/").strip()
    if path in on_disk:
        return path
    for rel in on_disk:
        if path == f"{directory}/{rel}" or path.endswith(f"/{directory}/{rel}"):
            return rel
    return None


def files_tsv_counts(text: str, directory: str, on_disk: dict[str, str]) -> dict[str, Json]:
    """``on_disk``: relative path → SHA-256 of the files beside ``files.tsv``."""
    matched: set[str] = set()
    missing = differs = 0
    rows = _tsv_rows(text)
    for dest, sha in rows:
        rel = _match(dest, directory, on_disk)
        if rel is None:
            missing += 1
            continue
        matched.add(rel)
        differs += on_disk[rel] != sha
    return {
        "listed": len(rows),
        "matched": len(matched),
        "missing_on_disk": missing,
        "not_listed": len(on_disk) - len(matched),
        "sha256_differs": differs,
    }


# ---------------------------------------------------------------- race files


def _counts(values: Iterable[str]) -> dict[str, Json]:
    return dict[str, Json](sorted(Counter(values).items()))


def _status(value: Json) -> str:
    return STATUSES[value] if isinstance(value, int) and 0 <= value < len(STATUSES) else "(other)"


def race_facts(race: Json, index: int, key: bytes) -> dict[str, Json]:
    """What chooses the calculation, and counts; no name, title or value of a person."""
    item = as_dict(race)
    data, settings = as_dict(item.get("data")), as_dict(item.get("settings"))
    persons = [as_dict(p) for p in as_list(item.get("persons"))]
    results = [as_dict(r) for r in as_list(item.get("results"))]
    groups = [as_dict(g) for g in as_list(item.get("groups"))]
    race_type = data.get("race_type")
    person_ids = sorted(as_str(p.get("id")) for p in persons)
    return {
        "index": index,
        "race_type": RACE_TYPES.get(race_type, "(other)") if isinstance(race_type, int) else None,
        "processing_mode": _safe(settings.get("result_processing_mode", "time")),
        "score_mode": _safe(settings.get("result_processing_score_mode")),
        "scores_mode": _safe(settings.get("scores_mode", "off")),
        "marked_route_mode": _safe(settings.get("marked_route_mode", "off")),
        "time_accuracy": _safe(settings.get("time_accuracy", 0)),
        "any_course_groups": sum(1 for g in groups if g.get("is_any_course") is True),
        "persons": len(persons),
        "results": len(results),
        "groups": len(groups),
        "courses": len(as_list(item.get("courses"))),
        "organizations": len(as_list(item.get("organizations"))),
        "out_of_competition": sum(1 for p in persons if p.get("is_out_of_competition") is True),
        "statuses": _counts(_status(r.get("status")) for r in results),
        "result_objects": _counts(as_str(_safe(r.get("object"))) for r in results),
        "race_key": pseudonym.keyed_hash(key, "race-id", as_str(item.get("id"))),
        "persons_key": (
            pseudonym.keyed_hash(key, "race-persons", "\n".join(person_ids)) if persons else ""
        ),
    }


def _shape(doc: Json) -> str:
    if isinstance(doc, dict) and "races" in doc:
        return "races"
    return "list" if isinstance(doc, list) else "single race"


def _formula(file_id: str, index: int, race: Json) -> dict[str, Json] | None:
    settings = as_dict(as_dict(race).get("settings"))
    if settings.get("scores_mode") != "formula":
        return None
    text = str(settings.get("scores_formula", "0"))  # as legacy reads it (score_calculation.py:21)
    shown = text if _SAFE_FORMULA.fullmatch(text) and "__" not in text else None
    return {
        "file_id": file_id,
        "race": index,
        "formula": shown,
        "formula_sha256": _sha(text.encode("utf-8")),
    }


@dataclass
class _Build:
    key: bytes
    cache: Path
    race_files: list[dict[str, Json]] = field(default_factory=list[dict[str, Json]])
    other_files: list[dict[str, Json]] = field(default_factory=list[dict[str, Json]])
    formulas: list[Json] = field(default_factory=list[Json])
    copies: list[Json] = field(default_factory=list[Json])
    paths: dict[str, tuple[Path, Path]] = field(default_factory=dict[str, tuple["Path", "Path"]])
    masked: Counter[str] = field(default_factory=Counter[str])
    leaks: Counter[str] = field(default_factory=Counter[str])

    def race_file(self, directory: str, file_id: str, path: Path) -> None:
        raw = path.read_bytes()
        text, fmt = racefile.decode(raw)
        doc = parse_json(text)
        races = racefile.races_of(doc)
        out, _, stats = anonymize.anonymize_bytes(raw, key=self.key, neutral_id=file_id)
        name = file_id.split("/", 1)[1] + (".json.gz" if fmt == "gzip" else ".json")
        relative = f"anonymized/{directory}/{name}"
        target = self.cache / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(out)
        self.paths[file_id] = (path, target)
        masked_doc = parse_json(racefile.decode(out)[0])
        leaks = leakcheck.check_pair(doc, masked_doc)
        where = (
            leakcheck.leak_paths(doc, masked_doc)
            if any(v for k, v in leaks.items() if k.startswith("leak:"))
            else {}
        )
        formulas = [f for i, r in enumerate(races) if (f := _formula(file_id, i, r))]
        self.formulas.extend(formulas)
        self.masked.update(stats)
        self.leaks.update(leaks)
        version = as_dict(doc).get("version") if isinstance(doc, dict) else None
        self.race_files.append(
            {
                "file_id": file_id,
                "format": fmt,
                "shape": _shape(doc),
                "version": _safe(version) if version is not None else None,
                "size": len(raw),
                "sha256": _sha(raw),
                "anonymized_path": relative,
                "anonymized_sha256": _sha(out),
                "races": [race_facts(r, i, self.key) for i, r in enumerate(races)],
                "runnable": not formulas,
                "masked": dict[str, Json](sorted(stats.items())),
                "leaks": dict[str, Json](leaks),
                "leak_paths": dict[str, Json](where),
            }
        )
        self.copies.append({"path": relative, "sha256": _sha(out), "source_sha256": _sha(raw)})

    def other_file(self, file_id: str, kind: str, raw: bytes) -> None:
        entry: dict[str, Json] = {
            "file_id": file_id,
            "kind": kind,
            "size": len(raw),
            "sha256": _sha(raw),
        }
        if kind == "readout-log":
            entry["stats"] = dict[str, Json](racefile.readout_log_stats(racefile.decode(raw)[0]))
        elif kind == "sportorg-log":
            entry["stats"] = racefile.sportorg_log_stats(racefile.decode(raw)[0])
        self.other_files.append(entry)


def _directory_id(name: str, key: bytes) -> str:
    return (
        name
        if _NEUTRAL_DIR.fullmatch(name)
        else f"dir-{pseudonym.keyed_hash(key, 'dir-name', name)[:8]}"
    )


def _starts(race_files: list[dict[str, Json]]) -> dict[str, Json]:
    """Races that are one start: the same race id or the same persons, in any files."""
    races = [
        (f"{f['file_id']}#{r['index']}", r)
        for f in race_files
        for r in (as_dict(x) for x in as_list(f["races"]))
    ]
    parent = {name: name for name, _ in races}

    def root(name: str) -> str:
        while parent[name] != name:
            name = parent[name]
        return name

    first_by_key: dict[str, str] = {}
    for name, race in races:
        for key in ("race_key", "persons_key"):
            value = as_str(race[key])
            if not value:
                continue
            other = first_by_key.setdefault(f"{key}:{value}", name)
            a, b = sorted((root(name), root(other)))
            parent[b] = a
    groups: dict[str, list[str]] = {}
    for name, _ in races:
        groups.setdefault(root(name), []).append(name)
    for name, race in races:
        race["same_as"] = [n for n in groups[root(name)] if n != name]
    return {"races": len(races), "distinct": len(groups)}


def build(
    corpus: Path, cache: Path, *, key: bytes, paths: dict[str, tuple[Path, Path]] | None = None
) -> dict[str, Json]:
    """Anonymize every race file of ``corpus/raw`` into ``cache`` and return the manifest.

    ``paths``, if given, receives file id → (original, anonymized copy) for the invariant run.
    """
    shutil.rmtree(cache / "anonymized", ignore_errors=True)
    state = _Build(key, cache)
    passports, inventory = read_inventory(corpus / "inventory.csv")
    directories: list[Json] = []
    all_kinds: Counter[str] = Counter()
    raw_root = corpus / "raw"
    folders = sorted(p for p in raw_root.iterdir() if p.is_dir()) if raw_root.is_dir() else []
    for folder in folders:
        directory = _directory_id(folder.name, key)
        files = sorted(p for p in folder.rglob("*") if p.is_file())
        kinds: Counter[str] = Counter()
        on_disk: dict[str, str] = {}
        for path in files:
            rel = path.relative_to(folder).as_posix()
            if rel == FILES_TSV:
                continue
            raw = path.read_bytes()
            on_disk[rel] = _sha(raw)
            file_id = (
                f"{directory}/{pseudonym.keyed_hash(key, 'file-name', f'{folder.name}/{rel}')}"
            )
            kind = racefile.kind(raw)
            kinds[kind] += 1
            all_kinds[kind] += 1
            if kind == "race":
                state.race_file(directory, file_id, path)
            else:
                state.other_file(file_id, kind, raw)
        tsv = folder / FILES_TSV
        listing = (
            files_tsv_counts(tsv.read_text(encoding="utf-8-sig"), folder.name, on_disk)
            if tsv.is_file()
            else None
        )
        passport = passports.get(folder.name)
        directories.append(
            {
                "id": directory,
                "kinds": _counts(kinds.elements()),
                "files_tsv": listing,
                "in_inventory": passport is not None,
                "passport": dict[str, Json](sorted((passport or {}).items())),
            }
        )
    inventory["rows_without_directory"] = len(passports.keys() - {f.name for f in folders})
    starts = _starts(state.race_files)
    _write_cache_manifest(cache, key, state.copies)
    if paths is not None:
        paths.update(state.paths)
    races = [as_dict(r) for f in state.race_files for r in as_list(f["races"])]
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "key_id": pseudonym.key_id(key),
        "directories": directories,
        "race_files": list[Json](state.race_files),
        "other_files": list[Json](state.other_files),
        "starts": starts,
        "formulas": state.formulas,
        "ardf_races": sum(1 for r in races if r["processing_mode"] == "ardf"),
        "inventory": inventory,
        "totals": {
            "directories": len(directories),
            "race_files": len(state.race_files),
            "races": len(races),
            "formats": _counts(as_str(f["format"]) for f in state.race_files),
            "versions": _counts(as_str(f["version"] or "(none)") for f in state.race_files),
            "kinds": _counts(all_kinds.elements()),
            "masked": dict[str, Json](sorted(state.masked.items())),
            "leaks": dict[str, Json](sorted(state.leaks.items())),
        },
    }


def _write_cache_manifest(cache: Path, key: bytes, copies: list[Json]) -> None:
    """Rule 11: what lies in the cache, from which original, made by which command."""
    data: Json = {
        "generator": "python -m scripts.corpus.evidence (scripts/corpus/catalog.py: build)",
        "key_id": pseudonym.key_id(key),
        "files": sorted(copies, key=lambda c: as_str(as_dict(c)["path"])),
    }
    cache.mkdir(parents=True, exist_ok=True)
    text = racefile.dumps(data) + "\n"
    (cache / "MANIFEST.json").write_text(text, encoding="utf-8", newline="\n")
