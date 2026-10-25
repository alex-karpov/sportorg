"""Tests for scripts/archaeology/verify_locs.py on a temporary repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.archaeology import verify_locs
from scripts.archaeology.common import Loc

if TYPE_CHECKING:
    from pathlib import Path

    from tests.scripts.archaeology.conftest import Commit

WORDS = ("один", "два", "три")


def test_check_flags_line_out_of_range(repo: Path, commit: Commit) -> None:
    pin = commit("one", {"sportorg/x.py": b"a\nb\nc\n"})
    commit("two", {"sportorg/x.py": b"a\n"})
    pins = {"pysport": (repo, pin)}
    ok = Loc("pysport", "sportorg/x.py", 3)
    past_end = Loc("pysport", "sportorg/x.py", 2, 4)
    missing = Loc("pysport", "sportorg/y.py", 1)
    problems = verify_locs.check([ok, past_end, missing], pins)
    assert problems == [
        f"{past_end.tag()}: line 4 out of range (3 lines at {pin[:7]})",
        f"{missing.tag()}: file not found at {pin[:7]}",
    ]


def test_source_lines_reads_the_pin(repo: Path, commit: Commit) -> None:
    pin = commit("one", {"sportorg/x.py": "".join(f"{w}\n" for w in WORDS).encode()})
    commit("two", {"sportorg/x.py": b"changed\n"})
    pins = {"pysport": (repo, pin)}
    lines = verify_locs.source_lines(Loc("pysport", "sportorg/x.py", 2, 3), pins)
    assert lines == list(WORDS[1:])


def test_source_lines_counts_like_ast_not_str_splitlines(repo: Path, commit: Commit) -> None:
    # A form feed or U+2028 inside a line is not a line break for ast line numbers.
    pin = commit("one", {"sportorg/x.py": f"a = 1\x0c\nb = '{chr(0x2028)}'\r\nc = 3\n".encode()})
    pins = {"pysport": (repo, pin)}
    assert verify_locs.source_lines(Loc("pysport", "sportorg/x.py", 3), pins) == ["c = 3"]
    assert verify_locs.check([Loc("pysport", "sportorg/x.py", 4)], pins) != []
