"""Tests for scripts/corpus/catalog.py: walk a corpus, anonymize its race files, build the manifest.

Every corpus here is synthetic, laid out as ``docs/data-request.md`` asks (``raw/<id>/…``,
``files.tsv``, ``inventory.csv``). File names stand for race names: the manifest must not show them.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from typing import TYPE_CHECKING

import pytest

from scripts._json import Json, as_dict, as_list, as_str, parse_json
from scripts.corpus import catalog, racefile, synth

if TYPE_CHECKING:
    from pathlib import Path

KEY = b"synthetic test key, not the corpus key"
NAME_A = "Кубок Выдумки 2019.json"
NAME_B = "Небывальск день 1.sportorg"


def _write_race(path: Path, doc: Json, fmt: str = "utf-8") -> bytes:
    raw = racefile.encode(synth.dumps(doc), fmt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    _write_race(root / "raw" / "S01" / NAME_A, synth.personal_individual())
    _write_race(
        root / "raw" / "S01" / "protocol" / "итоги.json", synth.personal_old_format(), "cp1251"
    )
    (root / "raw" / "S01" / "protocol" / "протокол.pdf").write_bytes(b"%PDF-1.4 synthetic")
    (root / "raw" / "S01" / "source.txt").write_text(
        "https://example.invalid/race\n", encoding="utf-8"
    )
    multi = synth.personal_multi_day()
    _write_race(root / "raw" / "S02" / "all days.json", multi, "gzip")
    for index, race in enumerate(racefile.races_of(multi)):
        day: Json = {"version": synth.LEGACY_VERSION, "current_race": 0, "races": [race]}
        _write_race(root / "raw" / "S02" / f"Небывальск день {index + 1}.sportorg", day)
    (root / "raw" / "S02" / "notes.md").write_text("# Заметки\n", encoding="utf-8")
    inventory = "id,sport,source,may_share\nS01,,https://x,\nS02,,,\n"
    (root / "inventory.csv").write_text(inventory, encoding="utf-8")
    return root


def _build(root: Path, tmp_path: Path) -> dict[str, Json]:
    return catalog.build(root, tmp_path / "cache", key=KEY)


def _race_files(manifest: dict[str, Json]) -> list[dict[str, Json]]:
    return [as_dict(f) for f in as_list(manifest["race_files"])]


def _directory(manifest: dict[str, Json], name: str) -> dict[str, Json]:
    return next(as_dict(d) for d in as_list(manifest["directories"]) if as_dict(d)["id"] == name)


def test_kinds_by_content_not_by_extension(tmp_path: Path) -> None:
    manifest = _build(_corpus(tmp_path), tmp_path)
    assert as_dict(_directory(manifest, "S01")["kinds"]) == {"pdf": 1, "race": 2, "text": 1}
    assert as_dict(_directory(manifest, "S02")["kinds"]) == {"race": 3, "text": 1}
    formats = sorted(as_str(f["format"]) for f in _race_files(manifest))
    assert formats == ["cp1251", "gzip", "utf-8", "utf-8", "utf-8"]


def test_no_file_name_and_no_personal_value_in_the_manifest(tmp_path: Path) -> None:
    text = json.dumps(_build(_corpus(tmp_path), tmp_path), ensure_ascii=False)
    for word in (
        "Кубок",
        "Небывальск",
        "итоги",
        "протокол",
        "notes",
        "Выдумкин",
        "example.invalid",
    ):
        assert word not in text


def test_file_id_comes_from_the_directory_and_the_name(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    before = {as_str(f["file_id"]) for f in _race_files(_build(root, tmp_path))}
    _write_race(root / "raw" / "S01" / "0 first in the listing.json", synth.personal_individual())
    after = {as_str(f["file_id"]) for f in _race_files(_build(root, tmp_path))}
    assert before < after
    assert all(i.startswith(("S01/", "S02/")) for i in after)


def test_shape_version_and_race_facts(tmp_path: Path) -> None:
    files = _race_files(_build(_corpus(tmp_path), tmp_path))
    shapes = sorted(as_str(f["shape"]) for f in files)
    assert shapes == ["races", "races", "races", "races", "single race"]
    gzip_file = next(f for f in files if f["format"] == "gzip")
    assert gzip_file["version"] == synth.LEGACY_VERSION
    races = [as_dict(r) for r in as_list(gzip_file["races"])]
    assert [r["race_type"] for r in races] == ["MULTI_DAY_RACE", "MULTI_DAY_RACE"]
    assert as_dict(races[0]["statuses"]) == {"OK": 5}
    assert races[0]["persons"] == 5


def test_hashes_of_the_original_and_of_the_copy(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    manifest = _build(root, tmp_path)
    original = (root / "raw" / "S01" / NAME_A).read_bytes()
    entry = next(
        f for f in _race_files(manifest) if f["sha256"] == hashlib.sha256(original).hexdigest()
    )
    copy = tmp_path / "cache" / as_str(entry["anonymized_path"])
    assert hashlib.sha256(copy.read_bytes()).hexdigest() == entry["anonymized_sha256"]
    assert racefile.decode(copy.read_bytes())[1] == "utf-8"


def test_cache_manifest_lists_every_copy(tmp_path: Path) -> None:
    manifest = _build(_corpus(tmp_path), tmp_path)
    cache = as_dict(parse_json((tmp_path / "cache" / "MANIFEST.json").read_text(encoding="utf-8")))
    assert len(as_list(cache["files"])) == len(_race_files(manifest)) == 5
    assert cache["key_id"] == manifest["key_id"]


def test_matching_races_are_one_start(tmp_path: Path) -> None:
    manifest = _build(_corpus(tmp_path), tmp_path)
    starts = as_dict(manifest["starts"])
    # S01: individual + old format; S02: two days, each also in the combined file.
    assert starts["races"] == 6
    assert starts["distinct"] == 4
    day_races = [as_dict(r) for f in _race_files(manifest) for r in as_list(f["races"])]
    assert sum(1 for r in day_races if as_list(r["same_as"])) == 4


def test_files_tsv_discrepancies_are_counted(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    folder = root / "raw" / "S01"
    good = hashlib.sha256((folder / NAME_A).read_bytes()).hexdigest()
    rows = [
        "dest\tsha256\tsize\tsource",
        f"raw/S01/{NAME_A}\t{good}\t1\tD:\\races\\{NAME_A}",
        f"S01\\protocol\\протокол.pdf\t{'0' * 64}\t1\tx",
        f"/home/someone/corpus/raw/S01/deleted.pdf\t{'1' * 64}\t1\tx",
    ]
    (folder / "files.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    listing = as_dict(_directory(_build(root, tmp_path), "S01")["files_tsv"])
    assert listing == {
        "listed": 3,
        "matched": 2,
        "missing_on_disk": 1,
        "not_listed": 2,
        "sha256_differs": 1,
    }


def test_inventory_counts_unfilled_and_never_copies_the_source(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    (root / "inventory.csv").write_text(
        "id,sport,source,may_share,edits_after_print\n"
        "S01,рогейн,https://x,yes,снят Выдумкин\n"
        "S02,,,,\n",
        encoding="utf-8",
    )
    manifest = _build(root, tmp_path)
    inventory = as_dict(manifest["inventory"])
    assert as_dict(inventory["unfilled"]) == {
        "edits_after_print": 1,
        "may_share": 1,
        "source": 1,
        "sport": 1,
    }
    s01 = as_dict(_directory(manifest, "S01")["passport"])
    assert s01 == {"edits_after_print": "filled", "may_share": "yes", "sport": "рогейн"}
    assert "https://x" not in json.dumps(manifest)


def test_formula_files_are_listed_and_not_runnable(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    doc = as_dict(synth.rogaine())
    race = as_dict(as_list(doc["races"])[0])
    as_dict(race["settings"])["scores_mode"] = "formula"
    as_dict(race["settings"])["scores_formula"] = "max(0, 100 - time // 60000)"
    _write_race(root / "raw" / "S03" / "f.json", doc)
    manifest = _build(root, tmp_path)
    formulas = [as_dict(f) for f in as_list(manifest["formulas"])]
    assert len(formulas) == 1
    assert formulas[0]["formula"] == "max(0, 100 - time // 60000)"
    entry = next(f for f in _race_files(manifest) if f["file_id"] == formulas[0]["file_id"])
    assert entry["runnable"] is False
    assert manifest["ardf_races"] == 0


def test_an_unsafe_formula_is_shown_by_its_hash_only(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    doc = as_dict(synth.rogaine())
    settings = as_dict(as_dict(as_list(doc["races"])[0])["settings"])
    settings["scores_mode"], settings["scores_formula"] = "formula", "__import__('os').getenv('X')"
    _write_race(root / "raw" / "S03" / "f.json", doc)
    formula = as_dict(as_list(_build(root, tmp_path)["formulas"])[0])
    assert formula["formula"] is None
    assert len(as_str(formula["formula_sha256"])) == 64


def test_an_undecodable_file_is_counted(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    (root / "raw" / "S01" / "broken.json").write_bytes(gzip.compress(b"\xff\xfe"))
    assert as_dict(_directory(_build(root, tmp_path), "S01")["kinds"])["binary"] == 1


def test_a_directory_with_a_telling_name_is_shown_by_a_hash(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    _write_race(root / "raw" / "Кубок Выдумки" / "a.json", synth.individual())
    ids = [as_str(as_dict(d)["id"]) for d in as_list(_build(root, tmp_path)["directories"])]
    assert "Кубок Выдумки" not in ids
    assert any(i.startswith("dir-") for i in ids)


def test_the_copies_leak_nothing(tmp_path: Path) -> None:
    manifest = _build(_corpus(tmp_path), tmp_path)
    totals = as_dict(as_dict(manifest["totals"])["leaks"])
    assert all(v == 0 for k, v in totals.items() if k.startswith("leak:"))


def test_rebuild_is_byte_identical(tmp_path: Path) -> None:
    root = _corpus(tmp_path)
    first = json.dumps(_build(root, tmp_path), sort_keys=True)
    copies = {p: p.read_bytes() for p in (tmp_path / "cache").rglob("*") if p.is_file()}
    assert json.dumps(_build(root, tmp_path), sort_keys=True) == first
    assert {p: p.read_bytes() for p in (tmp_path / "cache").rglob("*") if p.is_file()} == copies


@pytest.mark.parametrize("change", ["edit", "add"])
def test_locality_another_file_does_not_change_this_one(tmp_path: Path, change: str) -> None:
    """Locality (1) [мейнтейнер: 2026-11-01]: B changes or C appears; A stays byte-identical."""
    root = _corpus(tmp_path)

    def entry_a(manifest: dict[str, Json]) -> dict[str, Json]:
        entry = next(f for f in _race_files(manifest) if as_str(f["file_id"]).startswith("S01/"))
        return {k: entry[k] for k in ("file_id", "sha256", "anonymized_sha256", "anonymized_path")}

    first = _build(root, tmp_path)
    copy_a = (tmp_path / "cache" / as_str(entry_a(first)["anonymized_path"])).read_bytes()
    if change == "edit":
        doc = as_dict(synth.personal_multi_day())
        person = as_dict(as_list(as_dict(as_list(doc["races"])[0])["persons"])[0])
        person["surname"] = "Выдумщиков"
        _write_race(root / "raw" / "S02" / "all days.json", doc, "gzip")
    else:
        _write_race(
            root / "raw" / "S01" / "добавленный файл.json", synth.personal_individual(), "cp1251"
        )
    second = _build(root, tmp_path)
    assert entry_a(second) == entry_a(first)
    assert (tmp_path / "cache" / as_str(entry_a(second)["anonymized_path"])).read_bytes() == copy_a


def test_logs_are_counted_by_kind_without_their_content(tmp_path: Path) -> None:
    """Legacy's readout backup and its own log (N07, 2026-11-01): counts and hashes only."""
    root = _corpus(tmp_path)
    readout = "start\n8000001\n10:00:00\n10:30:00\nsplit_start\n31 10:05:00\nsplit_end\nend\n"
    (root / "raw" / "S02" / "si20250622.log").write_text(readout, encoding="utf-8")
    log = "INFO 2025-06-22 10:00:00,123 MainThread@main_window.py:267 Выдумкин\n"
    (root / "raw" / "S02" / "sportorg.log").write_text(log, encoding="cp1251")
    manifest = _build(root, tmp_path)
    kinds = as_dict(_directory(manifest, "S02")["kinds"])
    assert kinds["readout-log"] == kinds["sportorg-log"] == 1
    logs = {as_str(as_dict(f)["kind"]): as_dict(f) for f in as_list(manifest["other_files"])}
    assert as_dict(logs["readout-log"]["stats"])["readouts"] == 1
    assert as_dict(logs["sportorg-log"]["stats"]) == {
        "lines": 1,
        "continuation_lines": 0,
        "levels": {"INFO": 1},
        "locations": {"main_window.py:267": 1},
    }
    text = json.dumps(manifest, ensure_ascii=False)
    assert "8000001" not in text
    assert "Выдумкин" not in text


def test_templates_and_punch_codes_legacy_cannot_read_are_counted(tmp_path: Path) -> None:
    """F8: ``int()`` on list parts of a control template and on punch codes.

    [код: pysport@b548c35 sportorg/models/memory.py:1142-1160]
    """
    doc = as_dict(synth.individual())
    race = as_dict(as_list(doc["races"])[0])
    controls = [as_dict(c) for c in as_list(as_dict(as_list(race["courses"])[0])["controls"])]
    controls[0]["code"], controls[1]["code"] = "%(31,,32)", "%(31-35)"
    split = as_dict(as_list(as_dict(as_list(race["results"])[0])["splits"])[0])
    split["code"] = ""
    root = tmp_path / "corpus"
    _write_race(root / "raw" / "S01" / "a.json", doc)
    facts = as_dict(as_list(_race_files(_build(root, tmp_path))[0]["races"])[0])
    assert facts["list_templates_not_integer"] == 1
    assert facts["punch_codes_not_integer"] == 1
