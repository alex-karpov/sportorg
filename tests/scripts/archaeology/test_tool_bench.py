"""Tests for scripts/archaeology/tool_bench.py: PyPI metadata summary and agreement metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.archaeology import tool_bench
from scripts.archaeology.common import ImportRef

if TYPE_CHECKING:
    from scripts._json import Json


@pytest.mark.parametrize(
    ("filename", "python", "expected"),
    [
        ("radon-6.0.1-py2.py3-none-any.whl", "3.15", {"linux", "windows", "macos"}),
        ("x-1-cp314-cp314-win_amd64.whl", "3.14", {"windows"}),
        ("x-1-cp314-cp314-win_amd64.whl", "3.15", set[str]()),
        ("x-1-cp314-cp314t-manylinux_2_17_x86_64.whl", "3.14", set[str]()),
        ("x-1-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", "3.15", {"linux"}),
        ("x-1-cp39-abi3-musllinux_1_2_aarch64.whl", "3.14", set[str]()),
        ("x-1-cp313-cp313-macosx_11_0_arm64.whl", "3.14", set[str]()),
        ("x-1-py3-none-macosx_11_0_arm64.whl", "3.14", {"macos"}),
        ("x-1-py3-none-win_amd64.whl", "3.14", {"windows"}),
    ],
)
def test_wheel_platforms(filename: str, python: str, expected: set[str]) -> None:
    assert tool_bench.wheel_platforms(filename, python) == expected


def test_pypi_summary_reads_latest_release() -> None:
    data: Json = {
        "info": {
            "name": "Demo",
            "version": "2.0",
            "license_expression": None,
            "license": "",
            "requires_python": ">=3.9",
            "classifiers": [
                "Development Status :: 5 - Production/Stable",
                "License :: OSI Approved :: MIT License",
            ],
            "project_urls": {"Source": "https://example.invalid/demo"},
        },
        "urls": [
            {"filename": "demo-2.0.tar.gz", "upload_time_iso_8601": "2026-09-01T10:00:00.1Z"},
            {
                "filename": "demo-2.0-py3-none-any.whl",
                "upload_time_iso_8601": "2026-09-02T10:00:00.1Z",
            },
        ],
    }
    assert tool_bench.pypi_summary(data) == {
        "name": "Demo",
        "version": "2.0",
        "released": "2026-09-01",
        "license": "MIT License (classifier)",
        "requires_python": ">=3.9",
        "status": "5 - Production/Stable",
        "wheels_3.14": "linux, macos, windows",
        "wheels_3.15": "linux, macos, windows",
        "source": "https://example.invalid/demo",
    }


def test_pypi_summary_prefers_license_expression_and_reports_missing_wheels() -> None:
    data: Json = {
        "info": {"name": "n", "version": "1", "license_expression": "Apache-2.0", "license": "x"},
        "urls": [{"filename": "n-1.tar.gz", "upload_time_iso_8601": "2026-01-01T00:00:00Z"}],
    }
    summary = tool_bench.pypi_summary(data)
    assert summary["license"] == "Apache-2.0"
    assert summary["wheels_3.14"] == "none (sdist only)"
    assert summary["status"] == "not declared"


def test_spearman_ranks_with_ties() -> None:
    assert tool_bench.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert tool_bench.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert tool_bench.spearman([1, 1, 2], [1, 1, 2]) == pytest.approx(1.0)


def test_overlap_counts() -> None:
    assert tool_bench.overlap({"a", "b", "c"}, {"b", "c", "d", "e"}) == {
        "only_a": 1,
        "only_b": 2,
        "both": 2,
        "jaccard": 0.4,
    }


ROOT = "/repo/.legacy/pysport"


def test_parse_ruff_c901_keys_by_relative_path_and_line() -> None:
    data: Json = [
        {
            "code": "C901",
            "filename": f"{ROOT}/sportorg/a.py",
            "location": {"row": 15, "column": 5},
            "message": "`play` is too complex (2 > 0)",
        },
        {
            "code": "E501",
            "filename": f"{ROOT}/sportorg/a.py",
            "location": {"row": 1, "column": 1},
            "message": "x",
        },
    ]
    assert tool_bench.parse_ruff_c901(data, ROOT) == {("sportorg/a.py", 15): ("play", 2)}


def test_parse_radon_takes_functions_methods_and_closures_not_classes() -> None:
    closure: Json = {
        "type": "function",
        "name": "inner",
        "complexity": 1,
        "lineno": 9,
        "closures": [],
    }
    method: Json = {"type": "method", "name": "m", "complexity": 3, "lineno": 5, "closures": []}
    data: Json = {
        ".legacy/pysport/sportorg/a.py": [
            {"type": "class", "name": "C", "complexity": 4, "lineno": 4, "methods": [method]},
            method,
            {"type": "function", "name": "f", "complexity": 2, "lineno": 8, "closures": [closure]},
        ]
    }
    assert tool_bench.parse_radon(data, ".legacy/pysport") == {
        ("sportorg/a.py", 5): ("m", 3),
        ("sportorg/a.py", 8): ("f", 2),
        ("sportorg/a.py", 9): ("inner", 1),
    }


def test_parse_lizard_csv() -> None:
    text = (
        '5,2,42,2,6,"__init__@5-10@.legacy/pysport/sportorg/libs/wo.py",'
        '".legacy/pysport/sportorg/libs/wo.py","__init__","__init__( self )",5,10\n'
    )
    assert tool_bench.parse_lizard_csv(text, ".legacy/pysport") == {
        ("sportorg/libs/wo.py", 5): ("__init__", 2)
    }


def test_parse_vulture_lines() -> None:
    text = (
        ".legacy/pysport/sportorg/config.py:24: unused function 'module_path' (60% confidence)\n"
        ".legacy/pysport/sportorg/x.py:7: unreachable code after 'if' (100% confidence)\n"
    )
    assert tool_bench.parse_vulture(text, ".legacy/pysport") == [
        {
            "path": "sportorg/config.py",
            "line": 24,
            "kind": "unused function",
            "name": "module_path",
            "confidence": 60,
        },
        {
            "path": "sportorg/x.py",
            "line": 7,
            "kind": "unreachable code",
            "name": "if",
            "confidence": 100,
        },
    ]


def test_import_targets_like_grimp() -> None:
    modules = {"pkg", "pkg.models", "pkg.models.memory", "pkg.gui"}
    targets = tool_bench.import_targets
    assert targets(ImportRef("pkg.models", ("memory", "race"), 1, local=False), modules) == {
        "pkg.models.memory",
        "pkg.models",
    }
    assert targets(ImportRef("pkg.models.memory", ("race",), 1, local=True), modules) == {
        "pkg.models.memory"
    }
    assert targets(ImportRef("pkg.gui.widgets.x", (), 1, local=False), modules) == {"pkg.gui"}
    assert targets(ImportRef("PySide6.QtCore", ("Qt",), 1, local=False), modules) == set()
