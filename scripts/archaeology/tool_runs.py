"""Run the Stage 1 tool candidates on the pinned legacy and compare their results (ADR-0007).

Run from the repo root (tools come from throwaway ``uvx`` environments, never the project's):
    uv run python -m scripts.legacy_clone
    PYTHONDONTWRITEBYTECODE=1 uv run python -m scripts.archaeology.tool_runs \
        --out docs/evidence/stage-1/tools --runs 5

Inside the Claude Code sandbox also set ``UV_TOOL_DIR=$TMPDIR/uv-tools`` (``~/.local/share/uv``
is read-only there). ``bench.json``/``bench.md`` hold counts and agreement (deterministic);
``timings.json`` holds wall times (median of ``--runs``), which differ between machines and runs.
Tools that may write next to the sources (skylos, deadcode, PyDriller) run on the copy
``.legacy-run/pysport``.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

import grimp

from scripts import legacy
from scripts._json import Json, as_dict, as_int, as_list, parse_json
from scripts.archaeology import tool_bench as tb
from scripts.archaeology.common import (
    PYSPORT,
    assert_tree_clean,
    git_log,
    git_raw,
    iter_imports,
    module_name,
    pin_short,
    repo_root,
    tracked_files,
    write_outputs,
)

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT: Final = legacy.ROOT
SRC: Final = ".legacy/pysport/sportorg"
VERSIONS: Final = {
    "radon": "6.0.1",
    "lizard": "1.24.3",
    "vulture": "2.16",
    "skylos": "5.0.0",
    "deadcode": "2.4.1",
    "pydriller": "2.12",
    "ast-grep-cli": "0.51.0",
}
PYDRILLER_SCRIPT: Final = """
import json, sys
from pydriller import Repository
counts, commits, merges = {}, 0, 0
for c in Repository(sys.argv[1]).traverse_commits():
    commits += 1
    if c.merge:
        merges += 1
        continue
    for f in c.modified_files:
        path = f.new_path or f.old_path
        counts[path] = counts.get(path, 0) + 1
print(json.dumps({"commits": commits, "merges": merges, "files": counts}))
"""


@dataclass(frozen=True, slots=True)
class Run:
    exit: int
    stdout: str
    stderr_tail: str
    median_s: float


def _uvx(tool: str, *args: str, command: str | None = None, with_: str | None = None) -> list[str]:
    spec = f"{tool}@{VERSIONS[tool]}"
    if with_ is not None:
        return ["uvx", "--python", "3.14", "--with", with_, *args]
    if command is not None:
        return ["uvx", "--python", "3.14", "--from", spec, command, *args]
    return ["uvx", "--python", "3.14", spec, *args]


def _scrub(text: str) -> str:
    """Drop machine paths from tool messages (home directory names are not evidence)."""
    return text.replace(str(ROOT), "<repo>").replace(str(Path.home()), "~")


def timed(cmd: list[str], cwd: Path, runs: int) -> Run:
    times: list[float] = []
    result = None
    for _ in range(runs):
        started = time.perf_counter()
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        times.append(time.perf_counter() - started)
    assert result is not None  # noqa: S101 - runs >= 1 is enforced by argparse choices
    tail = result.stderr.strip().splitlines()[-1:] if result.returncode else []
    return Run(result.returncode, result.stdout, _scrub(" ".join(tail)), statistics.median(times))


def timed_call[T](func: Callable[[], T], runs: int) -> tuple[T, float]:
    times: list[float] = []
    value: T | None = None
    for _ in range(runs):
        started = time.perf_counter()
        value = func()
        times.append(time.perf_counter() - started)
    assert value is not None  # noqa: S101 - runs >= 1 is enforced by argparse choices
    return value, statistics.median(times)


# ---------------------------------------------------------------- needs


def _pairs(base: tb.Complexity, other: tb.Complexity) -> dict[str, Json]:
    common = sorted(set(base) & set(other))
    rho = tb.spearman([base[k][1] for k in common], [other[k][1] for k in common])
    return {
        "common_functions": len(common),
        "only_ruff": len(set(base) - set(other)),
        "only_other": len(set(other) - set(base)),
        "equal_complexity": sum(base[k][1] == other[k][1] for k in common),
        "spearman": round(rho, 4),
    }


def n1_complexity(runs: int, timings: dict[str, float]) -> dict[str, Json]:
    ruff = timed(
        [
            "ruff", "check", "--no-cache", "--isolated", "--select", "C901",
            "--config", "lint.mccabe.max-complexity=0", "--output-format", "json", SRC,
        ],
        ROOT,
        runs,
    )  # fmt: skip
    radon = timed(_uvx("radon", "cc", "-j", SRC), ROOT, runs)
    lizard = timed(_uvx("lizard", "--csv", SRC), ROOT, runs)
    timings.update(
        {"N1 ruff": ruff.median_s, "N1 radon": radon.median_s, "N1 lizard": lizard.median_s}
    )
    by_ruff = tb.parse_ruff_c901(parse_json(ruff.stdout), str(repo_root(PYSPORT)))
    by_radon = tb.parse_radon(parse_json(radon.stdout), ".legacy/pysport")
    by_lizard = tb.parse_lizard_csv(lizard.stdout, ".legacy/pysport")
    return {
        "functions": {"ruff": len(by_ruff), "radon": len(by_radon), "lizard": len(by_lizard)},
        "exit": {"ruff": ruff.exit, "radon": radon.exit, "lizard": lizard.exit},
        "ruff_vs_radon": _pairs(by_ruff, by_radon),
        "ruff_vs_lizard": _pairs(by_ruff, by_lizard),
    }


def _own_edges(repo: Path) -> set[tuple[str, str]]:
    files = tracked_files(repo, "sportorg/*.py")
    modules = {module_name(path)[0] for path in files}
    edges: set[tuple[str, str]] = set()
    for path in files:
        name, is_package = module_name(path)
        source = git_raw(repo, "show", f"HEAD:{path}")
        for ref in iter_imports(source, name, is_package=is_package, path=path):
            edges.update((name, target) for target in tb.import_targets(ref, modules))
    return {edge for edge in edges if edge[0] != edge[1]}


def _grimp_edges(repo: Path) -> set[tuple[str, str]]:
    sys.path.insert(0, str(repo))
    try:
        graph = grimp.build_graph("sportorg", cache_dir=None)
    finally:
        sys.path.remove(str(repo))
    return {(m, i) for m in graph.modules for i in graph.find_modules_directly_imported_by(m)}


def n2_imports(runs: int, timings: dict[str, float]) -> dict[str, Json]:
    repo = repo_root(PYSPORT)
    own, own_s = timed_call(lambda: _own_edges(repo), runs)
    by_grimp, grimp_s = timed_call(lambda: _grimp_edges(repo), runs)
    timings.update({"N2 own ast": own_s, "N2 grimp": grimp_s})
    only_own = sorted(f"{a} -> {b}" for a, b in own - by_grimp)
    only_grimp = sorted(f"{a} -> {b}" for a, b in by_grimp - own)
    return {
        "edges": {"own": len(own), "grimp": len(by_grimp)},
        "own_vs_grimp": dict(
            tb.overlap({f"{a} {b}" for a, b in own}, {f"{a} {b}" for a, b in by_grimp})
        ),
        "only_own_first": list[Json](only_own[:20]),
        "only_grimp_first": list[Json](only_grimp[:20]),
    }


def n3_dead_code(runs: int, timings: dict[str, float]) -> dict[str, Json]:
    copy = legacy.checkout_dir(PYSPORT, legacy.run_dir())
    vulture = timed(_uvx("vulture", SRC, "--min-confidence", "0"), ROOT, runs)
    skylos = timed(
        _uvx("skylos", "sportorg", "--json", "--no-upload", "--confidence", "0"), copy, 1
    )
    deadcode = timed(_uvx("deadcode", "sportorg"), copy, 1)
    timings["N3 vulture"] = vulture.median_s
    findings = tb.parse_vulture(vulture.stdout, ".legacy/pysport")
    kinds = Counter(str(f["kind"]) for f in findings)
    return {
        "vulture": {
            "exit": vulture.exit,
            "findings": len(findings),
            "by_kind": dict(sorted(kinds.items())),
        },
        "skylos": {"exit": skylos.exit, "stderr_tail": skylos.stderr_tail},
        "deadcode": {"exit": deadcode.exit, "stderr_tail": deadcode.stderr_tail},
    }


def n6_history(runs: int, timings: dict[str, float]) -> dict[str, Json]:
    repo, copy = repo_root(PYSPORT), legacy.checkout_dir(PYSPORT, legacy.run_dir())
    log, own_s = timed_call(lambda: git_log(repo), runs)
    driller = timed(
        _uvx(
            "pydriller", "python", "-I", "-c", PYDRILLER_SCRIPT, str(copy), with_="pydriller==2.12"
        ),
        ROOT,
        1,
    )
    timings.update({"N6 own git log": own_s, "N6 pydriller": driller.median_s})
    own_files: Counter[str] = Counter()
    for commit in log:
        if not commit.is_merge:
            own_files.update({change.path for change in commit.files})
    data = as_dict(parse_json(driller.stdout)) if driller.exit == 0 else {}
    their_files = {k: as_int(v) for k, v in as_dict(data.get("files")).items()}
    tracked = tracked_files(repo)
    equal = sum(own_files[p] == their_files.get(p, 0) for p in tracked)
    return {
        "commits": {"own": len(log), "pydriller": as_int(data.get("commits"))},
        "merges": {"own": sum(c.is_merge for c in log), "pydriller": as_int(data.get("merges"))},
        "tracked_files_with_equal_change_count": equal,
        "tracked_files": len(tracked),
        "pydriller_exit": driller.exit,
    }


def n8_scan(runs: int, timings: dict[str, float]) -> dict[str, Json]:
    pattern = "sys.platform"
    grep = timed(
        ["git", "-C", ".legacy/pysport", "grep", "-n", "-F", pattern, "--", "*.py"], ROOT, runs
    )
    sg_args = ("run", "-p", pattern, "-l", "python", "--json=compact", ".legacy/pysport")
    sg = timed(_uvx("ast-grep-cli", *sg_args, command="ast-grep"), ROOT, runs)
    timings.update({"N8 git grep": grep.median_s, "N8 ast-grep": sg.median_s})
    grep_hits = {
        line.split(":", 2)[0] + ":" + line.split(":", 2)[1] for line in grep.stdout.splitlines()
    }
    sg_hits: set[str] = set()
    if sg.exit == 0:
        for item in as_list(parse_json(sg.stdout)) if sg.stdout.strip() else []:
            entry = as_dict(item)
            start = as_dict(as_dict(entry.get("range")).get("start"))
            path = str(entry.get("file", "")).removeprefix(".legacy/pysport/")
            sg_hits.add(f"{path}:{as_int(start.get('line')) + 1}")
    return {
        "pattern": pattern,
        "hits": {"git_grep": len(grep_hits), "ast_grep": len(sg_hits)},
        "overlap": dict(tb.overlap(grep_hits, sg_hits)),
        "only_git_grep": list[Json](sorted(grep_hits - sg_hits)),
        "ast_grep_exit": sg.exit,
    }


NEEDS: Final = {
    "N1": n1_complexity,
    "N2": n2_imports,
    "N3": n3_dead_code,
    "N6": n6_history,
    "N8": n8_scan,
}


class Options(argparse.Namespace):
    out: Path = Path()
    runs: int = 5
    only: str = ",".join(NEEDS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--runs", type=int, choices=range(1, 11), default=5)
    parser.add_argument("--only", default=",".join(NEEDS))
    args = parser.parse_args(argv, namespace=Options())
    results: dict[str, Json] = {}
    timings: dict[str, float] = {}
    for need in args.only.split(","):
        results[need] = NEEDS[need](args.runs, timings)
        assert_tree_clean(repo_root(PYSPORT))
    lines = [
        f"## {need}\n\n```json\n{json.dumps(value, indent=1, sort_keys=True)}\n```"
        for need, value in sorted(results.items())
    ]
    header = (
        f"# Tool candidates: measurements on pysport@{pin_short(PYSPORT)}\n\n"
        "Produced by `scripts/archaeology/tool_runs.py` (command in `commands.txt`). "
        "Wall times are in `timings.json` (not deterministic). Versions: "
        + ", ".join(f"{k} {v}" for k, v in sorted(VERSIONS.items()))
        + "; ruff and grimp from `uv.lock`."
    )
    write_outputs(args.out, "bench", dict(results), "\n\n".join(lines), header)
    rounded = {k: round(v, 2) for k, v in sorted(timings.items())}
    (args.out / "timings.json").write_text(json.dumps(rounded, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rounded))
    return 0


if __name__ == "__main__":
    sys.exit(main())
