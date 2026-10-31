"""Stage 2 evidence of the oracle seam (TASK-8 AC #1): ``docs/evidence/stage-2/oracle/``.

``run``: synthetic inputs (``scripts/corpus/synth.py``) and the oracle's output for each on the
first lane (``.legacy-run/pysport/.venv``, CPython 3.8.20); a second run on the same lane and a run
on the second lane (``.venv-3.13``) compared byte for byte; the canary (a later finish of one
runner moves their place and time); legacy's ``tests/data/test.json``, which holds personal data
(``[мейнтейнер: 2026-10-31]``), as counts and hashes only.

``typecheck``: how basedpyright sees the driver under three set-ups (ADR-0009 T3), each in a
temporary copy: (a) legacy sources and packages from the legacy interpreter, (a') the same without
legacy (as in CI), (c) the hand-written stubs; plus which Python 3.9+ constructs the 3.8 mode flags.

Usage::

    uv run python -m scripts.oracle_evidence run --out docs/evidence/stage-2/oracle
    uv run python -m scripts.oracle_evidence typecheck --out docs/evidence/stage-2/oracle
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts._json import Json, as_dict, as_int, as_list, as_str, parse_json
from scripts.archaeology.common import write_outputs
from scripts.corpus import synth
from scripts.legacy import ROOT, legacy_dir
from scripts.legacy_env import clone_path, env_python
from scripts.oracle_cli import OUTPUT_FILES, OracleRun, oracle, write_run
from scripts.oracle_compare import counts_only
from scripts.oracle_normalize import dumps

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

LANES: Final = {"first": ".venv", "second": ".venv-3.13"}
CANARY_BIB: Final = 101
CANARY_DELAY_MS: Final = 3 * 60_000
DRIVER_DIR: Final = ROOT / "scripts" / "oracle_driver"
PY38_PROBE: Final = {
    1: ("str.removeprefix (3.9)", 'x = "a".removeprefix("b")'),
    2: ("dict[...] at run time (3.9)", "y = dict[str, int]()"),
    3: ("dict | dict (3.9)", 'z = {"a": 1} | {"b": 2}'),
}


# ---------------------------------------------------------------- pure helpers


def diagnostic_counts(report: Json) -> dict[str, Json]:
    """Errors, warnings and diagnostics per rule of a ``basedpyright --outputjson`` report."""
    diagnostics = [as_dict(d) for d in as_list(as_dict(report).get("generalDiagnostics"))]
    by_rule: dict[str, int] = {}
    for diagnostic in diagnostics:
        rule = as_str(diagnostic.get("rule"), "(syntax)")
        by_rule[rule] = by_rule.get(rule, 0) + 1
    return {
        "errors": sum(1 for d in diagnostics if d.get("severity") == "error"),
        "warnings": sum(1 for d in diagnostics if d.get("severity") == "warning"),
        "files": as_int(as_dict(as_dict(report).get("summary")).get("filesAnalyzed")),
        "by_rule": dict[str, Json](sorted(by_rule.items())),
    }


def later_finish(doc: Json, *, bib: int, msec: int) -> Json:
    """Copy of a race file where the runner with ``bib`` finishes ``msec`` later."""
    copy = parse_json(dumps(doc))
    for race in map(as_dict, as_list(as_dict(copy).get("races"))):
        persons = [as_dict(p) for p in as_list(race.get("persons"))]
        ids = {pid for p in persons if p.get("bib") == bib and isinstance(pid := p.get("id"), str)}
        for result in map(as_dict, as_list(race.get("results"))):
            finish = result.get("finish_time")
            if result.get("person_id") in ids and isinstance(finish, int):
                result["finish_time"] = finish + msec
                return copy
    msg = f"no result with a finish for bib {bib}"
    raise ValueError(msg)


def result_by_bib(doc: Json, bib: int) -> dict[str, Json]:
    for race in as_list(as_dict(doc).get("races")):
        for result in map(as_dict, as_list(as_dict(race).get("results"))):
            if result.get("bib") == bib:
                return result
    msg = f"no result for bib {bib}"
    raise ValueError(msg)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _texts(run: OracleRun) -> dict[str, str]:
    docs = (run.results, run.stored, run.comparison, run.run)
    return {name: dumps(doc) for name, doc in zip(OUTPUT_FILES, docs, strict=True)}


def _same(a: OracleRun, b: OracleRun, files: tuple[str, ...]) -> bool:
    first, second = _texts(a), _texts(b)
    return all(first[name] == second[name] for name in files)


def _outcome(result: Mapping[str, Json]) -> str:
    status = as_str(result.get("status"))
    return f"{status}, place {result.get('place')}, {result.get('time_ms')} ms"


# ---------------------------------------------------------------- run


def _lanes() -> dict[str, Path]:
    return {lane: env_python(clone_path() / name) for lane, name in LANES.items()}


def _lane_runs(race_file: Path, pythons: Mapping[str, Path]) -> dict[str, OracleRun]:
    runs = {lane: oracle(race_file, python_exe=exe) for lane, exe in pythons.items()}
    runs["rerun"] = oracle(race_file, python_exe=pythons["first"])
    return runs


def _lane_row(name: str, runs: Mapping[str, OracleRun]) -> dict[str, Json]:
    data_files = OUTPUT_FILES[:3]  # run.json names the interpreter, so it differs between lanes
    first = runs["first"]
    return {
        "input": name,
        "python": {lane: as_dict(run.run).get("python") for lane, run in runs.items()},
        "outputs_sha256": {k: _sha(v) for k, v in _texts(first).items()},
        "rerun_identical": _same(first, runs["rerun"], OUTPUT_FILES),
        "second_lane_identical": _same(first, runs["second"], data_files),
    }


def _write_lanes(out: Path, rows: list[Json]) -> None:
    table = [
        "| input | first lane | rerun: 4 files identical | second lane: 3 data files identical |",
        "|---|---|---|---|",
    ]
    for row in map(as_dict, rows):
        python = as_dict(row.get("python"))
        table.append(
            f"| {row['input']} | {python.get('first')} | {row['rerun_identical']} | "
            f"{python.get('second')}: {row['second_lane_identical']} |"
        )
    header = (
        "# Oracle lanes and determinism (TASK-8 AC #1, ADR-0009 T1)\n\n"
        "Each input runs three times: twice on the first lane and once on the second. `run.json` "
        "names the interpreter, so between lanes only `results.json`, `stored.json` and "
        "`comparison.json` are compared."
    )
    write_outputs(out, "lanes", {"lanes": dict(LANES), "inputs": rows}, "\n".join(table), header)


def _canary(out: Path, before: OracleRun, python_exe: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="oracle-canary-") as tmp:
        changed_file = Path(tmp) / "individual-later.json"
        changed_doc = later_finish(synth.individual(), bib=CANARY_BIB, msec=CANARY_DELAY_MS)
        changed_file.write_text(synth.dumps(changed_doc), encoding="utf-8")
        after = oracle(changed_file, python_exe=python_exe)
    rows: list[Json] = []
    for bib in (101, 102, 103, 107):
        old, new = result_by_bib(before.results, bib), result_by_bib(after.results, bib)
        rows.append({"bib": bib, "before": _outcome(old), "after": _outcome(new)})
    old, new = result_by_bib(before.results, CANARY_BIB), result_by_bib(after.results, CANARY_BIB)
    data: Json = {
        "input": "inputs/individual.json",
        "change": f"finish of bib {CANARY_BIB} + {CANARY_DELAY_MS} ms",
        "rows": rows,
        "fired": old.get("place") != new.get("place") and old.get("time_ms") != new.get("time_ms"),
    }
    table = ["| bib | before | after |", "|---|---|---|"]
    table.extend(f"| {r['bib']} | {r['before']} | {r['after']} |" for r in map(as_dict, rows))
    table += ["", f"Canary fired (place and time of bib {CANARY_BIB} changed): {data['fired']}"]
    header = (
        "# Oracle canary (TASK-8 AC #1)\n\n"
        f"`inputs/individual.json` with the finish of bib {CANARY_BIB} moved "
        f"{CANARY_DELAY_MS // 60_000} minutes later, through the same oracle (first lane). "
        "Also asserted by "
        "`tests/scripts/oracle/test_oracle_cli.py::test_finish_change_moves_place`."
    )
    write_outputs(out, "canary", data, "\n".join(table), header)


def _legacy_test_json(out: Path, pythons: Mapping[str, Path]) -> None:
    source = legacy_dir() / "pysport" / "tests" / "data" / "test.json"
    runs = _lane_runs(source, pythons)
    first = runs["first"]
    races = as_list(as_dict(first.results).get("races"))
    data: Json = {
        "input": "pysport@b548c35 tests/data/test.json",
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "races": len(races),
        "results": sum(len(as_list(as_dict(r).get("results"))) for r in races),
        "run": first.run,
        "outputs_sha256": {k: _sha(v) for k, v in _texts(first).items()},
        "rerun_identical": _same(first, runs["rerun"], OUTPUT_FILES),
        "second_lane_identical": _same(first, runs["second"], OUTPUT_FILES[:3]),
        "comparison": counts_only(first.comparison),
    }
    fields = as_dict(as_dict(as_list(as_dict(data["comparison"]).get("races"))[0]).get("fields"))
    table = ["| field | same | different | not stored |", "|---|---|---|---|"]
    for name, counts in fields.items():
        c = as_dict(counts)
        table.append(f"| {name} | {c.get('same')} | {c.get('different')} | {c.get('not_stored')} |")
    header = (
        "# Oracle on legacy tests/data/test.json: counts and hashes only\n\n"
        "The file holds personal data (`[мейнтейнер: 2026-10-31]`, stage prompt), so no result, id "
        "or value of it is written here: counts of results, of stored-vs-recalculated field "
        "outcomes, and SHA-256 of the input and of the oracle's outputs. "
        f"{data['races']} race(s), {data['results']} results; rerun identical: "
        f"{data['rerun_identical']}; second lane identical: {data['second_lane_identical']}; "
        f"stored values that differ: {as_dict(data['comparison']).get('different')}."
    )
    write_outputs(out, "legacy-test-json", data, "\n".join(table), header)


def run_command(out: Path) -> int:
    pythons = _lanes()
    missing = [f"{lane}: {exe}" for lane, exe in pythons.items() if not exe.exists()]
    if missing:
        print("legacy runtime missing (scripts.legacy_env sync): " + "; ".join(missing))
        return 1
    inputs = out / "inputs"
    synth.main(["--out", str(inputs)])
    rows: list[Json] = []
    individual: OracleRun | None = None
    for name in synth.RACES:
        runs = _lane_runs(inputs / f"{name}.json", pythons)
        write_run(runs["first"], out / "synthetic" / name)
        rows.append(_lane_row(f"inputs/{name}.json", runs))
        individual = runs["first"] if name == "individual" else individual
    if individual is not None:
        _canary(out, individual, pythons["first"])
    _legacy_test_json(out, pythons)
    _write_lanes(out, rows)
    return 0


# ---------------------------------------------------------------- typecheck


def _site_python() -> Path:
    return Path(sys.executable)


VARIANTS: Final[dict[str, tuple[str, Callable[[], Path], bool]]] = {
    # name → (description, interpreter whose packages pyright sees, use the stubs)
    "a_legacy_sources": (
        "(a) legacy sources and packages: the legacy 3.8 interpreter",
        lambda: env_python(clone_path() / ".venv"),
        False,
    ),
    "a_without_legacy": (
        "(a') as (a) where no legacy exists (CI): the project interpreter",
        _site_python,
        False,
    ),
    "c_stubs": ("(c) hand-written stubs, the project interpreter", _site_python, True),
}


def _config(*, stubs: bool) -> dict[str, Json]:
    extra: list[Json] = [str(DRIVER_DIR / "stubs")] if stubs else []
    config: dict[str, Json] = {
        "include": ["scripts"],
        "pythonVersion": "3.8",
        "typeCheckingMode": "all",
        "extraPaths": [*extra, "."],
        "reportUnnecessaryTypeIgnoreComment": "error",
        "reportIgnoreCommentWithoutRule": "error",
        "reportImplicitStringConcatenation": False,
        "reportUnusedCallResult": False,
    }
    if stubs:
        config["reportMissingModuleSource"] = "none"
    return config


def _basedpyright(exe: str, python: Path, *, stubs: bool, probe: bool) -> Json:
    with tempfile.TemporaryDirectory(prefix="oracle-typecheck-") as tmp:
        target = Path(tmp) / "scripts" / "oracle_driver"
        target.mkdir(parents=True)
        (Path(tmp) / "scripts" / "__init__.py").write_text("", encoding="utf-8")
        for name in ("__init__.py", "driver.py", "snapshot.py"):
            shutil.copyfile(DRIVER_DIR / name, target / name)
        if probe:
            lines = [code for _, code in PY38_PROBE.values()]
            (target / "probe38.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
        config = Path(tmp) / "pyrightconfig.json"
        config.write_text(json.dumps(_config(stubs=stubs)), encoding="utf-8")
        cmd = [exe, "--outputjson", "--pythonpath", str(python), "-p", str(config)]
        done = subprocess.run(
            cmd, cwd=tmp, capture_output=True, text=True, encoding="utf-8", check=False
        )
    return parse_json(done.stdout)


def _probe_lines(report: Json) -> list[int]:
    lines: set[int] = set()
    for diagnostic in map(as_dict, as_list(as_dict(report).get("generalDiagnostics"))):
        if as_str(diagnostic.get("file")).endswith("probe38.py"):
            start = as_dict(as_dict(diagnostic.get("range")).get("start"))
            lines.add(as_int(start.get("line")) + 1)
    return sorted(lines)


def typecheck_command(out: Path) -> int:
    exe = shutil.which("basedpyright") or "basedpyright"
    version = subprocess.run(
        [exe, "--version"], capture_output=True, text=True, check=False
    ).stdout.strip()
    version = " ".join(version.split())  # "basedpyright X\nbased on pyright Y" on one line
    variants: dict[str, Json] = {}
    rows = ["| set-up | files | errors | warnings | rules |", "|---|---|---|---|---|"]
    for name, (description, python, stubs) in VARIANTS.items():
        counts = diagnostic_counts(_basedpyright(exe, python(), stubs=stubs, probe=False))
        variants[name] = {"description": description, **counts}
        rules = ", ".join(f"{k} {v}" for k, v in as_dict(counts["by_rule"]).items()) or "none"
        rows.append(
            f"| {description} | {counts['files']} | {counts['errors']} | {counts['warnings']} "
            f"| {rules} |"
        )
    flagged = _probe_lines(_basedpyright(exe, _site_python(), stubs=True, probe=True))
    probe: list[Json] = [
        {"construct": what, "flagged": line in flagged} for line, (what, _) in PY38_PROBE.items()
    ]
    rows += ["", "Python 3.9+ constructs in a 3.8 probe module, set-up (c):", ""]
    rows += [f"- {as_dict(p)['construct']}: flagged {as_dict(p)['flagged']}" for p in probe]
    data: Json = {"basedpyright": version, "variants": variants, "py38_probe": probe}
    header = (
        "# Type checking the oracle driver (ADR-0009 T3)\n\n"
        "`scripts/oracle_driver/{driver,snapshot}.py` copied into a temporary project, "
        f"basedpyright ({version}) with `typeCheckingMode = all` and `pythonVersion = 3.8`. "
        "(b), leaving the driver out of the check, is not measured: it checks nothing."
    )
    write_outputs(out, "typecheck", data, "\n".join(rows), header)
    return 0


# ---------------------------------------------------------------- CLI


class Options(argparse.Namespace):
    command: str = ""
    out: Path = Path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "typecheck"):
        sub.add_parser(name).add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Options())
    if args.command == "run":
        return run_command(args.out)
    return typecheck_command(args.out)


if __name__ == "__main__":
    sys.exit(main())
