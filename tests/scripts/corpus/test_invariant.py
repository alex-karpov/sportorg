"""Tests for scripts/corpus/invariant.py: the oracle gives the same output before and after Д1.

The main test of the anonymization (plan S3): statuses, times, places — in fact every byte of
``results.json``, ``stored.json`` and ``comparison.json`` — are the same for the original and the
anonymized file. Integration tests need the legacy runtime and are skipped where it is missing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.corpus import anonymize, invariant, pseudonym, racefile, synth
from scripts.legacy_env import clone_path, env_python

if TYPE_CHECKING:
    from pathlib import Path

    from scripts._json import Json

KEY = b"synthetic test key, not the corpus key"
LEGACY_PYTHON = env_python(clone_path() / ".venv")
requires_legacy = pytest.mark.skipif(
    not LEGACY_PYTHON.exists(), reason="legacy runtime missing (scripts.legacy_env sync)"
)


def test_diff_counts_by_path_without_values() -> None:
    before: Json = {
        "races": [{"results": [{"place": 1, "time_ms": 5}, {"place": 2, "time_ms": 6}]}]
    }
    after: Json = {"races": [{"results": [{"place": 2, "time_ms": 5}, {"place": 1, "time_ms": 6}]}]}
    assert invariant.diff_counts(before, after) == {"races[].results[].place": 2}


def test_diff_counts_lengths_and_missing_keys() -> None:
    assert invariant.diff_counts({"a": [1, 2]}, {"a": [1]}) == {"a.length": 1}
    assert invariant.diff_counts({"a": 1}, {"b": 1}) == {"a": 1, "b": 1}
    assert invariant.diff_counts({"a": 1}, {"a": 1}) == {}


def _pair(tmp_path: Path, name: str, fmt: str) -> tuple[Path, Path]:
    text = synth.dumps(synth.PERSONAL[name]())
    original = tmp_path / f"{name}.{fmt}"
    original.write_bytes(racefile.encode(text, fmt))
    out, _, _ = anonymize.anonymize_bytes(original.read_bytes(), key=KEY, neutral_id="S00-test")
    anonymized = tmp_path / f"{name}.anon.{fmt}"
    anonymized.write_bytes(out)
    return original, anonymized


CASES = [(name, "utf-8") for name in synth.PERSONAL] + [
    ("personal_individual", "cp1251"),
    ("personal_individual", "gzip"),
]


@requires_legacy
@pytest.mark.parametrize(("name", "fmt"), CASES)
def test_oracle_output_is_the_same_after_anonymization(tmp_path: Path, name: str, fmt: str) -> None:
    original, anonymized = _pair(tmp_path, name, fmt)
    report = invariant.check(original, anonymized, python_exe=LEGACY_PYTHON)
    assert report["identical"] is True, report


@requires_legacy
def test_the_invariant_sees_a_merged_spelling(tmp_path: Path) -> None:
    """Canary: folding the day-2 spellings into day 1 changes legacy's multi-day result."""
    original, anonymized = _pair(tmp_path, "personal_multi_day", "utf-8")
    text = anonymized.read_text(encoding="utf-8")
    broken = tmp_path / "merged.json"
    # Same pseudonym on both days: what a normalization without the variant suffix would do.
    for variant, plain in (("Ёжиков", "Ежиков"), ("НЕБЫВАЛОВ", "Небывалов")):
        text = text.replace(
            pseudonym.pseudonym(KEY, "person", variant), pseudonym.pseudonym(KEY, "person", plain)
        )
    broken.write_text(text, encoding="utf-8")
    report = invariant.check(original, broken, python_exe=LEGACY_PYTHON)
    assert report["identical"] is False


@requires_legacy
def test_a_read_only_gzip_original_runs(tmp_path: Path) -> None:
    """Legacy opens gzip files ``r+b``.

    [код: pysport@b548c35 sportorg/modules/backup/file.py:33-41]
    """
    original, anonymized = _pair(tmp_path, "personal_individual", "gzip")
    original.chmod(0o444)
    anonymized.chmod(0o444)
    report = invariant.check(original, anonymized, python_exe=LEGACY_PYTHON)
    assert report["identical"] is True, report


@requires_legacy
def test_a_file_legacy_cannot_open_is_reported_for_both_sides(tmp_path: Path) -> None:
    doc = synth.personal_individual()
    for race in racefile.races_of(doc):
        assert isinstance(race, dict)
        # read by _race_migrate [код: pysport@b548c35 sportorg/modules/backup/json.py:92]
        del race["groups"]
    original = tmp_path / "broken.json"
    original.write_text(synth.dumps(doc), encoding="utf-8")
    out, _, _ = anonymize.anonymize_bytes(original.read_bytes(), key=KEY, neutral_id="S00-test")
    anonymized = tmp_path / "broken.anon.json"
    anonymized.write_bytes(out)
    report = invariant.check(original, anonymized, python_exe=LEGACY_PYTHON)
    assert report["identical"] is None
    where = "KeyError at sportorg/modules/backup/json.py:"
    errors = report["errors"]
    assert isinstance(errors, dict)
    assert all(str(errors[side]).startswith(where) for side in ("original", "anonymized"))
    assert report["same_error"] is True
