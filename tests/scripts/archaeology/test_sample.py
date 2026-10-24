"""Tests for scripts/archaeology/sample.py: seeded samples for the manual checks of Phase D."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts._json import as_dict, as_int
from scripts.archaeology import sample

if TYPE_CHECKING:
    from scripts._json import Json

ITEMS: list[Json] = [{"id": i, "kind": "fix" if i % 3 == 0 else "other"} for i in range(30)]


def test_sample_is_seeded_and_keeps_input_order() -> None:
    one = sample.sample(ITEMS, 5, seed=1)
    assert one == sample.sample(ITEMS, 5, seed=1)
    assert one != sample.sample(ITEMS, 5, seed=2)
    ids = [as_int(as_dict(item).get("id")) for item in one]
    assert ids == sorted(ids)
    assert len(ids) == 5


def test_stratified_split_takes_equal_shares() -> None:
    chosen = sample.sample(ITEMS, 6, seed=3, stratify="kind")
    kinds = [item["kind"] for item in chosen if isinstance(item, dict)]
    assert kinds.count("fix") == 3
    assert kinds.count("other") == 3


def test_sample_larger_than_population_returns_all() -> None:
    assert len(sample.sample(ITEMS[:4], 10, seed=0)) == 4


def test_table_shows_requested_fields() -> None:
    assert (
        sample.table([{"a": 1, "b": "x|y"}], ["a", "b"])
        == "| # | a | b |\n|---|---|---|\n| 1 | 1 | x\\|y |"
    )


def test_where_filters_before_sampling() -> None:
    chosen = sample.sample(ITEMS, 30, seed=0, where={"kind": "fix"})
    assert all(as_dict(item).get("kind") == "fix" for item in chosen)
    assert len(chosen) == 10


def test_parse_where_reads_json_values() -> None:
    assert sample.parse_where(["is_merge=false", "kind=fix"]) == {"is_merge": False, "kind": "fix"}
