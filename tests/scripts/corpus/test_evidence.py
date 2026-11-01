"""Tests for scripts/corpus/evidence.py: the S3 evidence on synthetic data and on the corpus."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_list, parse_json
from scripts.corpus import evidence, synth
from scripts.legacy_env import clone_path, env_python

if TYPE_CHECKING:
    from pathlib import Path

requires_legacy = pytest.mark.skipif(
    not env_python(clone_path() / ".venv").exists(), reason="legacy runtime missing"
)


def test_synthetic_corpus_has_the_shapes_of_the_real_one(tmp_path: Path) -> None:
    root = evidence.synthetic_corpus(tmp_path / "corpus")
    folders = sorted(p.name for p in (root / "raw").iterdir())
    assert folders == ["S01", "S02", "S03"]
    assert (root / "inventory.csv").is_file()
    assert (root / "raw" / "S01" / "files.tsv").is_file()


def test_synthetic_evidence_without_the_oracle_is_reproducible_and_clean(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    assert evidence.main(["synthetic", "--out", str(first), "--skip-invariant"]) == 0
    assert evidence.main(["synthetic", "--out", str(second), "--skip-invariant"]) == 0
    for name in ("synthetic.json", "synthetic.md"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    data = as_dict(parse_json((first / "synthetic.json").read_text(encoding="utf-8")))
    checks = as_dict(data["checks"])
    assert checks["rebuild_identical"] is True
    assert checks["locality_edit_other_file"] is True
    assert checks["locality_add_file"] is True
    assert checks["locality_one_record"] is True
    assert checks["leaks"] == 0
    text = (first / "synthetic.md").read_text(encoding="utf-8")
    for surname in synth.INVENTED_SURNAMES:
        assert surname.strip() not in text


@requires_legacy
def test_synthetic_invariant_holds(tmp_path: Path) -> None:
    assert evidence.main(["synthetic", "--out", str(tmp_path)]) == 0
    data = as_dict(parse_json((tmp_path / "synthetic.json").read_text(encoding="utf-8")))
    rows = [as_dict(r) for r in as_list(as_dict(data["invariant"])["files"])]
    ran = [r for r in rows if r["identical"] is not None]
    assert len(ran) == len(rows) - 1
    assert all(r["identical"] is True for r in ran)
    skipped = next(r for r in rows if r["identical"] is None)
    assert "formula" in str(skipped["skipped"])


def test_synthetic_corpus_holds_status_comments_as_legacy_writes_them(tmp_path: Path) -> None:
    assert evidence.main(["synthetic", "--out", str(tmp_path), "--skip-invariant"]) == 0
    text = (tmp_path / "synthetic.md").read_text(encoding="utf-8")
    assert (
        "status comments (C1): rule clause kept 3, clause kept and hint masked 1, masked 2" in text
    )
