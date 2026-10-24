"""Unit tests for the licence gate (no network, no installed-package access)."""

import pytest

from scripts.check_licenses import expression_verdict, metadata_verdict, split_packages

LOCK = """
version = 1

[[package]]
name = "sportorg-ng"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "Alpha_Lib" },
]

[package.dev-dependencies]
dev = [
    { name = "tool" },
]

[[package]]
name = "alpha-lib"
version = "1.0"
dependencies = [
    { name = "beta", marker = "sys_platform == 'win32'" },
]

[[package]]
name = "beta"
version = "2.0"

[[package]]
name = "tool"
version = "3.0"
dependencies = [
    { name = "tool-helper" },
    { name = "beta" },
]

[[package]]
name = "tool-helper"
version = "1.0"
"""


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("GPL-2.0-only", "denied"),
        ("GPLv2", "denied"),
        ("GPL-2.0-or-later", "ok"),
        ("Limited use license", "unknown"),
        ("MIT", "ok"),
        ("MIT OR GPL-2.0-only", "ok"),
        ("MIT AND GPL-2.0-only", "denied"),
        ("(MIT OR GPL-2.0-only) AND Apache-2.0", "ok"),
        ("GPL-3.0-or-later WITH GCC-exception-3.1", "ok"),
        ("AGPL-3.0-or-later", "denied"),
        ("Proprietary", "denied"),
        ("BSD License", "ok"),
        ("MIT OR", "unknown"),
        ("", "unknown"),
    ],
)
def test_expression_verdict(text: str, expected: str) -> None:
    assert expression_verdict(text) == expected


def test_classifier_is_used_when_no_expression() -> None:
    verdict, _ = metadata_verdict(
        None, ["License :: OSI Approved :: Apache Software License", "Typing :: Typed"], None
    )
    assert verdict == "ok"


def test_expression_beats_classifier_and_field() -> None:
    verdict, _ = metadata_verdict("GPL-2.0-only", ["License :: OSI Approved :: MIT License"], "MIT")
    assert verdict == "denied"


def test_split_runtime_and_dev() -> None:
    runtime, dev = split_packages(LOCK)
    assert runtime == ["alpha-lib", "beta"]
    assert dev == ["tool", "tool-helper"]
