"""Tests for the pure parts of scripts/oracle_evidence.py (no legacy runtime, no type checker)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import oracle_evidence
from scripts._json import as_dict, as_list
from scripts.corpus import synth

if TYPE_CHECKING:
    from scripts._json import Json


def test_diagnostic_counts_by_severity_and_rule() -> None:
    report: Json = {
        "generalDiagnostics": [
            {"severity": "error", "rule": "reportMissingImports", "file": "/x/a.py"},
            {"severity": "error", "rule": "reportMissingImports", "file": "/x/a.py"},
            {"severity": "warning", "rule": "reportAny", "file": "/x/b.py"},
            {"severity": "error", "file": "/x/a.py"},
        ],
        "summary": {"filesAnalyzed": 2},
    }

    assert oracle_evidence.diagnostic_counts(report) == {
        "errors": 3,
        "warnings": 1,
        "files": 2,
        "by_rule": {"(syntax)": 1, "reportAny": 1, "reportMissingImports": 2},
    }


def test_later_finish_moves_only_the_given_bib() -> None:
    doc = synth.individual()

    changed = oracle_evidence.later_finish(doc, bib=101, msec=180_000)

    race = as_dict(as_list(as_dict(changed)["races"])[0])
    before = as_dict(as_list(as_dict(doc)["races"])[0])
    pid = next(as_dict(p)["id"] for p in as_list(race["persons"]) if as_dict(p)["bib"] == 101)
    for new, old in zip(as_list(race["results"]), as_list(before["results"]), strict=True):
        new_finish, old_finish = as_dict(new)["finish_time"], as_dict(old)["finish_time"]
        if as_dict(new)["person_id"] == pid:
            assert isinstance(new_finish, int)
            assert isinstance(old_finish, int)
            assert new_finish - old_finish == 180_000
        else:
            assert new_finish == old_finish


def test_later_finish_rejects_an_unknown_bib() -> None:
    with pytest.raises(ValueError, match="bib 999"):
        oracle_evidence.later_finish(synth.individual(), bib=999, msec=1)


def test_result_by_bib_reads_the_normalized_document() -> None:
    doc: Json = {"races": [{"results": [{"bib": 7, "place": 2}, {"bib": 8, "place": 1}]}]}

    assert oracle_evidence.result_by_bib(doc, 7) == {"bib": 7, "place": 2}
    with pytest.raises(ValueError, match="bib 9"):
        oracle_evidence.result_by_bib(doc, 9)
