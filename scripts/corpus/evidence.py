"""Stage 2 S3 evidence (TASK-8 AC #2): ``docs/evidence/stage-2/corpus/``.

``synthetic``: a synthetic corpus laid out like the real one (``raw/<id>/``, ``files.tsv`` with
the kinds of discrepancy the real one has, ``inventory.csv``, a day file beside the file of the
whole event, logs, a file with ``scores_mode = formula``), anonymized with a fixed synthetic key.
Checks: a rebuild is byte-identical; locality — editing another file, adding a file, editing one
record changes nothing else [мейнтейнер: 2026-11-01]; the leak check of every copy; the invariant
(the oracle's output before and after is byte-identical) on every runnable race file.

``corpus``: the same build on ``$SPORTORG_CORPUS`` with ``$SPORTORG_ANONYMIZATION_KEY``; copies
go to ``~/.cache/sportorg-stage2/corpus`` with ``MANIFEST.json``; the manifest (counts, hashes,
neutral ids) to ``--out``; ``--invariant`` runs the oracle on each runnable original and copy.
Files with ``scores_mode = formula`` run only when named by ``--allow-formula`` (R22).

Usage::

    uv run python -m scripts.corpus.evidence synthetic --out docs/evidence/stage-2/corpus
    uv run python -m scripts.corpus.evidence corpus --out docs/evidence/stage-2/corpus --invariant
"""

from __future__ import annotations

import argparse
import copy
import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_int, as_list, as_str
from scripts.archaeology.common import write_outputs
from scripts.corpus import anonymize, catalog, invariant, pseudonym, racefile, synth
from scripts.legacy_env import clone_path, env_python

if TYPE_CHECKING:
    from collections.abc import Sequence

SYNTHETIC_KEY: Final = b"synthetic evidence key, not the corpus key"
DEFAULT_CACHE: Final = Path.home() / ".cache" / "sportorg-stage2" / "corpus"
CORPUS_ENV: Final = "SPORTORG_CORPUS"
INVENTORY_HEADER: Final = (
    "id,sport,race_type,processing_mode,punch_system,days,persons,version_race_day,"
    "resaved_after_race,protocol_kind,protocol_signed,protocol_matches_file,edits_after_print,"
    "special_cases,source,may_share"
)
EDITED_RECORD: Final = 3
TSV_COLUMNS: Final = ("listed", "matched", "missing_on_disk", "not_listed", "sha256_differs")
DIRECTORY_HEADER: Final = (
    "| directory | kinds | files.tsv: listed / matched / missing on disk / not listed / "
    "other hash | passport |"
)
RACE_FILE_HEADER: Final = (
    "| race file | format | shape | version | races: type / mode / persons / results "
    "| same start as | leaks |"
)


# ---------------------------------------------------------------- synthetic corpus


def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def _race(path: Path, doc: Json, fmt: str = "utf-8") -> None:
    _write(path, racefile.encode(synth.dumps(doc), fmt))


def _formula_race() -> Json:
    doc = as_dict(synth.rogaine())
    settings = as_dict(as_dict(as_list(doc["races"])[0])["settings"])
    settings["scores_mode"], settings["scores_formula"] = "formula", "max(0, 100 - time // 60000)"
    return doc


def synthetic_corpus(root: Path) -> Path:
    """A corpus of fictional data; file names stand for race names (they must not show)."""
    s01, s02, s03 = (root / "raw" / name for name in ("S01", "S02", "S03"))
    _race(s01 / "Кубок Выдумки 2019.json", synth.personal_individual())
    _race(s01 / "старый формат.json", synth.personal_old_format(), "cp1251")
    _write(s01 / "protocol" / "протокол.pdf", b"%PDF-1.4 synthetic protocol\n")
    _write(s01 / "source.txt", b"https://example.invalid/race\n")
    listed = [s01 / "Кубок Выдумки 2019.json", s01 / "старый формат.json"]
    rows = ["dest\tsha256\tsize\tsource"]
    rows += [f"raw/S01/{p.name}\t{catalog.sha256_of(p)}\t{p.stat().st_size}\tD:\\x" for p in listed]
    rows.append(f"raw/S01/deleted.pdf\t{'0' * 64}\t1\tD:\\x")
    _write(s01 / "files.tsv", ("\n".join(rows) + "\n").encode())
    multi = synth.personal_multi_day()
    _race(s02 / "все дни.json", multi, "gzip")
    for index, race in enumerate(racefile.races_of(multi)):
        day: Json = {"version": synth.LEGACY_VERSION, "current_race": 0, "races": [race]}
        _race(s02 / f"день {index + 1}.json", day)
    _write(s02 / "notes.md", "# Заметки\n".encode())
    readout = "start\n500001\n10:00:00\n10:30:00\nsplit_start\n31 10:05:00\nsplit_end\nend\n"
    _write(s02 / "si20250622.log", readout.encode())
    log = "INFO 2025-06-22 10:00:00,123 MainThread@main_window.py:267 открыт файл\n"
    _write(s02 / "sportorg.log", log.encode("cp1251"))
    _race(s03 / "рогейн с формулой.json", _formula_race())
    _race(s03 / "индивидуальная.json", synth.individual(), "gzip")
    inventory = f"{INVENTORY_HEADER}\nS01,ориентирование{',' * 14}\nS02{',' * 15}\nS03{',' * 15}\n"
    _write(root / "inventory.csv", inventory.encode())
    return root


# ---------------------------------------------------------------- checks


def _snapshot(cache: Path) -> dict[str, bytes]:
    return {
        p.relative_to(cache).as_posix(): p.read_bytes() for p in cache.rglob("*") if p.is_file()
    }


def _entries(manifest: Json, prefix: str = "") -> dict[str, Json]:
    keys = ("sha256", "anonymized_sha256", "anonymized_path")
    return {
        as_str(f["file_id"]): {k: f[k] for k in keys}
        for f in map(as_dict, as_list(as_dict(manifest)["race_files"]))
        if as_str(f["file_id"]).startswith(prefix)
    }


def _locality(root: Path, tmp: Path, baseline: Json, before: dict[str, bytes]) -> dict[str, Json]:
    """Edit a file of S02, then add a file to S01: the copies of the other files stay."""
    s01 = _entries(baseline, "S01/")
    edited = copy.deepcopy(as_dict(synth.personal_multi_day()))
    person = as_dict(as_list(as_dict(as_list(edited["races"])[0])["persons"])[0])
    person["surname"] = "Выдумщиков"
    _race(root / "raw" / "S02" / "все дни.json", edited, "gzip")
    after_edit = catalog.build(root, tmp / "edit", key=SYNTHETIC_KEY)
    edit_copies = _snapshot(tmp / "edit")
    same_edit = _entries(after_edit, "S01/") == s01 and all(
        edit_copies[as_str(as_dict(e)["anonymized_path"])]
        == before[as_str(as_dict(e)["anonymized_path"])]
        for e in s01.values()
    )
    changed = _entries(after_edit, "S02/") != _entries(baseline, "S02/")
    _race(root / "raw" / "S01" / "добавленный файл.json", synth.personal_individual(), "cp1251")
    after_add = catalog.build(root, tmp / "add", key=SYNTHETIC_KEY)
    old = _entries(after_edit)
    same_add = all(_entries(after_add).get(file_id) == entry for file_id, entry in old.items())
    return {
        "locality_edit_other_file": same_edit,
        "locality_edit_changes_the_edited_file": changed,
        "locality_add_file": same_add and len(_entries(after_add)) == len(old) + 1,
    }


def _one_record() -> bool:
    """Locality (2): one person and its result edited; every other record as before."""
    doc = synth.personal_individual()
    changed = copy.deepcopy(doc)
    race = as_dict(racefile.races_of(changed)[0])
    person = as_dict(as_list(race["persons"])[EDITED_RECORD])
    person["surname"], person["card_number"], person["birth_date"] = (
        "Придумкин",
        8_000_001,
        "1980-01-02",
    )
    as_dict(as_list(race["results"])[EDITED_RECORD])["card_number"] = 8_000_001

    def records(source: Json) -> dict[str, list[Json]]:
        masked = anonymize.anonymize(source, key=SYNTHETIC_KEY, neutral_id="S").doc
        out = as_dict(racefile.races_of(masked)[0])
        keys = ("persons", "results")
        return {k: [x for i, x in enumerate(as_list(out[k])) if i != EDITED_RECORD] for k in keys}

    return records(doc) == records(changed)


def _leak_total(manifest: Json) -> int:
    leaks = as_dict(as_dict(as_dict(manifest)["totals"])["leaks"])
    return sum(as_int(v) for k, v in leaks.items() if k.startswith("leak:"))


def run_invariant(
    manifest: Json, paths: dict[str, tuple[Path, Path]], *, allow: Sequence[str] = ()
) -> dict[str, Json]:
    """The oracle on each runnable original and its copy (first lane)."""
    python_exe = env_python(clone_path() / ".venv")
    rows: list[Json] = []
    for entry in map(as_dict, as_list(as_dict(manifest)["race_files"])):
        file_id = as_str(entry["file_id"])
        if entry["runnable"] is not True and file_id not in allow:
            rows.append(
                {"file_id": file_id, "identical": None, "skipped": "scores_mode = formula (R22)"}
            )
            continue
        original, copy_path = paths[file_id]
        report = invariant.check(original, copy_path, python_exe=python_exe)
        rows.append({"file_id": file_id, **report})
    ran = [as_dict(r) for r in rows if as_dict(r)["identical"] is not None]
    return {
        "lane": str(python_exe.parent.parent.name),
        "files": rows,
        "ran": len(ran),
        "identical": sum(1 for r in ran if r["identical"] is True),
        "different": sum(1 for r in ran if r["identical"] is False),
        "not_run": len(rows) - len(ran),
        "legacy_failed_alike": sum(1 for r in rows if as_dict(r).get("same_error") is True),
    }


# ---------------------------------------------------------------- markdown


def _join(counts: Json) -> str:
    return ", ".join(f"{k} {v}" for k, v in as_dict(counts).items()) or "—"


def manifest_tables(manifest: Json) -> str:
    data = as_dict(manifest)
    totals = as_dict(data["totals"])
    counts = as_dict(totals["leaks"])
    leaks: dict[str, Json] = {
        kind: sum(as_int(v) for k, v in counts.items() if k.startswith(f"{kind}:"))
        for kind in ("leak", "residual")
    }
    residual = {k: v for k, v in counts.items() if k.startswith("residual:")}
    lines = [
        (
            f"Key id `{data['key_id']}`. {totals['directories']} directories, "
            f"{totals['race_files']} race files, {totals['races']} races, "
            f"{as_dict(data['starts'])['distinct']} distinct starts "
            "(races that share a race id or the same persons count once)."
        ),
        "",
        f"- kinds of files: {_join(totals['kinds'])}",
        f"- race file formats: {_join(totals['formats'])}",
        f"- SportOrg versions of the last save: {_join(totals['versions'])}",
        f"- races with `result_processing_mode = ardf`: {data['ardf_races']}",
        f"- files with `scores_mode = formula` (R22): {len(as_list(data['formulas']))}",
        f"- leak check of the copies: {_join(leaks)} (residual by category: {_join(residual)})",
        "",
        DIRECTORY_HEADER,
        "|---|---|---|---|",
    ]
    for d in map(as_dict, as_list(data["directories"])):
        tsv = as_dict(d["files_tsv"])
        listing = " / ".join(str(tsv[k]) for k in TSV_COLUMNS) if tsv else "—"
        passport = _join(d["passport"]) if d["in_inventory"] else "no row"
        lines.append(f"| {d['id']} | {_join(d['kinds'])} | {listing} | {passport} |")
    lines += [
        "",
        RACE_FILE_HEADER,
        "|---|---|---|---|---|---|---|",
    ]
    for f in map(as_dict, as_list(data["race_files"])):
        races = as_list(f["races"])
        described = "; ".join(
            f"{r['race_type']} / {r['processing_mode']} / {r['persons']} / {r['results']}"
            for r in map(as_dict, races)
        )
        same = sum(len(as_list(as_dict(r)["same_as"])) for r in races)
        found = sum(as_int(v) for k, v in as_dict(f["leaks"]).items() if k.startswith("leak:"))
        lines.append(
            f"| {f['file_id']} | {f['format']} | {f['shape']} | {f['version']} | {described} | "
            f"{same} | {found} |"
        )
    unfilled = as_dict(as_dict(data["inventory"]).get("unfilled"))
    lines += ["", f"Passport (`inventory.csv`): unfilled cells per column: {_join(unfilled)}."]
    return "\n".join(lines)


def invariant_tables(report: Json) -> str:
    data = as_dict(report)
    lines = [
        (
            f"Lane `{data['lane']}`: {data['ran']} files ran, {data['identical']} identical, "
            f"{data['different']} different, {data['not_run']} not run."
        ),
        "",
        "| race file | identical | not identical: paths and counts |",
        "|---|---|---|",
    ]
    for row in map(as_dict, as_list(data["files"])):
        errors = as_dict(row.get("errors"))
        reason = row.get("skipped") or (
            f"legacy failed: original {errors.get('original')}, copy {errors.get('anonymized')}"
            if errors
            else None
        )
        detail = (
            as_str(reason)
            if reason
            else _join(
                {
                    f"{name}: {path}": n
                    for name, paths in as_dict(row.get("differences")).items()
                    for path, n in as_dict(paths).items()
                }
            )
        )
        lines.append(f"| {row['file_id']} | {row['identical']} | {detail} |")
    return "\n".join(lines)


# ---------------------------------------------------------------- commands


def synthetic_command(out: Path, *, skip_invariant: bool) -> int:
    with tempfile.TemporaryDirectory(prefix="corpus-synthetic-") as tmp_dir:
        tmp = Path(tmp_dir)
        root = synthetic_corpus(tmp / "corpus")
        paths: dict[str, tuple[Path, Path]] = {}
        manifest = catalog.build(root, tmp / "cache", key=SYNTHETIC_KEY, paths=paths)
        first_copies = _snapshot(tmp / "cache")
        invariant_report = None if skip_invariant else run_invariant(manifest, paths)
        rebuilt = catalog.build(root, tmp / "cache", key=SYNTHETIC_KEY)
        checks: dict[str, Json] = {
            "rebuild_identical": rebuilt == manifest and _snapshot(tmp / "cache") == first_copies,
            **_locality(root, tmp, manifest, first_copies),
            "locality_one_record": _one_record(),
            "leaks": _leak_total(manifest),
        }
    data: dict[str, Json] = {
        "key": "synthetic (SYNTHETIC_KEY in scripts/corpus/evidence.py)",
        "checks": checks,
        "manifest": manifest,
    }
    body = ["| check | result |", "|---|---|"] + [f"| {k} | {v} |" for k, v in checks.items()]
    body += ["", "## Manifest of the synthetic corpus", "", manifest_tables(manifest)]
    if invariant_report is not None:
        data["invariant"] = invariant_report
        body += [
            "",
            "## Invariant: the oracle before and after",
            "",
            invariant_tables(invariant_report),
        ]
    header = (
        "# Anonymization on a synthetic corpus (TASK-8 AC #2, Stage 2 S3)\n\n"
        "Fictional data in the layout of the real corpus (`scripts/corpus/evidence.py: "
        "synthetic_corpus`), anonymized with a fixed synthetic key. Locality: editing a file of "
        "S02 and adding a file to S01 leave every other copy byte-identical; editing one record "
        "leaves the other records as before. The invariant runs the oracle (first lane) on each "
        "runnable original and its copy and compares `results.json`, `stored.json` and "
        "`comparison.json` byte for byte."
    )
    write_outputs(out, "synthetic", data, "\n".join(body), header)
    failed = [k for k, v in checks.items() if v is not True and k != "leaks"] + (
        ["leaks"] if checks["leaks"] else []
    )
    print(f"{out}/synthetic.md: checks failed: {failed or 'none'}")
    return 1 if failed else 0


def corpus_command(out: Path, *, cache: Path, with_invariant: bool, allow: Sequence[str]) -> int:
    corpus = os.environ.get(CORPUS_ENV)
    if not corpus:
        print(f"{CORPUS_ENV} is not set")
        return 2
    try:
        key = pseudonym.load_key(os.environ)
    except pseudonym.MissingKeyError as exc:
        print(exc)
        return 2
    paths: dict[str, tuple[Path, Path]] = {}
    manifest = catalog.build(Path(corpus), cache, key=key, paths=paths)
    header = (
        "# Corpus manifest (TASK-8 AC #2, Stage 2 S3)\n\n"
        "Built by `scripts/corpus/catalog.py` on `$SPORTORG_CORPUS/raw` and `inventory.csv` as "
        "they were at the run; the corpus is still being assembled. Directories by their neutral "
        "names, files by `<directory>/<keyed hash of the path>`; no file name, race name or "
        "personal value. The anonymized copies are outside the repository (D2 (a)), in the cache "
        "named in `commands.txt`, with `MANIFEST.json`."
    )
    write_outputs(out, "manifest", manifest, manifest_tables(manifest), header)
    leaks = _leak_total(manifest)
    print(
        f"{out}/manifest.md: {as_dict(manifest['totals'])['race_files']} race files; leaks {leaks}"
    )
    if with_invariant:
        report = run_invariant(manifest, paths, allow=allow)
        header = (
            "# Invariant on the corpus: the oracle before and after anonymization\n\n"
            "`scripts/corpus/invariant.py` on each runnable race file of the corpus and its "
            "anonymized copy; counts and JSON paths only, never values."
        )
        write_outputs(out, "invariant", report, invariant_tables(report), header)
        print(f"{out}/invariant.md: {report['identical']} of {report['ran']} identical")
        return 1 if leaks or report["different"] else 0
    return 1 if leaks else 0


class Options(argparse.Namespace):
    command: str = ""
    out: Path = Path()
    cache: Path = DEFAULT_CACHE
    skip_invariant: bool = False
    invariant: bool = False
    allow_formula: tuple[str, ...] = ()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    synthetic = sub.add_parser("synthetic")
    synthetic.add_argument("--out", type=Path, required=True)
    synthetic.add_argument(
        "--skip-invariant", action="store_true", help="without the legacy runtime"
    )
    corpus = sub.add_parser("corpus")
    corpus.add_argument("--out", type=Path, required=True)
    corpus.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    corpus.add_argument("--invariant", action="store_true", help="run the oracle before and after")
    corpus.add_argument(
        "--allow-formula", action="append", default=[], help="file id (R22 consent)"
    )
    args = parser.parse_args(argv, namespace=Options())
    if args.command == "synthetic":
        return synthetic_command(args.out, skip_invariant=args.skip_invariant)
    return corpus_command(
        args.out, cache=args.cache, with_invariant=args.invariant, allow=args.allow_formula
    )


if __name__ == "__main__":
    sys.exit(main())
