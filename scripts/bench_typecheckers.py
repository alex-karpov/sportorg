"""Benchmark Python type checkers on fixtures and on a read-only legacy corpus.

Stdlib only, Python >= 3.12.  Run from the repo root:
    uv run --no-sync python -m scripts.bench_typecheckers [--tools mypy ty ...]

Tools are launched through ``uvx --python 3.14 --from <pkg>==<ver> <exe>`` so nothing is
installed into the project.  The legacy corpus is only passed as a path argument; every
tool runs with cwd inside a fresh temp directory (or the config dir for the fixture run)
and caches (where configurable) go to the temp directory, so the corpus is never written.
"""

import argparse
import contextlib
import http.client
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from scripts._json import (
    Json,
    as_dict,
    as_float,
    as_int,
    as_list,
    as_opt_float,
    as_str,
    fetch_json,
    parse_json,
)
from scripts.legacy import checkout_dir

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "scripts" / "typecheck_fixtures"
CONFIGS = REPO / "scripts" / "typecheck_configs"
PYTHON = "3.14"
SINGLE_FILE_REL = "models/result/result_checker.py"  # relative to the legacy sportorg dir
SINGLE_FILE_TARGET_LINES = 300
VERSION_RUNS = 3
SINGLE_RUNS = 3
VERSION_TIMEOUT = 120
TRUNC_LIMIT = 2000
DEFAULT_LEGACY_PATH = checkout_dir("pysport") / "sportorg"
DEFAULT_OUT = Path("docs/evidence/stage-0/typecheckers/results.json")
BENCH_ERRORS = (
    OSError,
    http.client.HTTPException,
    ValueError,
    KeyError,
    IndexError,
    TypeError,
    RuntimeError,
    subprocess.SubprocessError,
    statistics.StatisticsError,
)

# name -> (pypi package, pinned version, executable)
TOOLS: dict[str, tuple[str, str, str]] = {
    "mypy": ("mypy", "2.4.0", "mypy"),
    "pyright": ("pyright", "1.1.414", "pyright"),
    "basedpyright": ("basedpyright", "1.40.2", "basedpyright"),
    "ty": ("ty", "0.0.91", "ty"),
    "pyrefly": ("pyrefly", "1.4.0", "pyrefly"),
    "zuban": ("zuban", "0.10.1", "zuban"),
}

type Result = dict[str, Json]


class Options(argparse.Namespace):
    """Typed command line options."""

    legacy_path: Path = DEFAULT_LEGACY_PATH
    runs: int = 3
    out: Path = DEFAULT_OUT
    timeout: float = 900
    skip_legacy: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.tools: list[str] = list(TOOLS)


@dataclass(frozen=True, slots=True)
class Bench:
    """Settings shared by every measurement of one run."""

    runs: int
    timeout: float
    evidence: Path  # directory for the per-tool output files (next to --out)


@dataclass
class RunResult:
    """Outcome of one external command."""

    seconds: float
    exit_code: int | None
    timed_out: bool
    stdout: str
    stderr: str


class Diag(NamedTuple):
    """One diagnostic attributed to a file."""

    file: str
    msg: str


def launcher(tool: str) -> list[str]:
    pkg, ver, exe = TOOLS[tool]
    return ["uvx", "--python", PYTHON, "--from", f"{pkg}=={ver}", exe]


def cfg(tool: str, name: str) -> str:
    return str(CONFIGS / tool / name)


def fixture_cmd(tool: str, tmp: str) -> list[str]:
    """Strict-config command for the fixtures directory (cwd = config dir)."""
    base = launcher(tool)
    fx = str(FIXTURES)
    if tool == "mypy":
        cache = str(Path(tmp) / "mypy_cache")
        return [
            *base,
            "--config-file",
            cfg(tool, "mypy.ini"),
            "--no-incremental",
            "--cache-dir",
            cache,
            fx,
        ]
    if tool in ("pyright", "basedpyright"):
        return [*base, "-p", cfg(tool, "pyrightconfig.json"), fx]
    if tool == "ty":
        return [*base, "check", "--config-file", cfg(tool, "ty.toml"), fx]
    if tool == "pyrefly":
        return [*base, "check", "-c", cfg(tool, "pyrefly.toml"), fx]
    if tool == "zuban":
        return [
            *base,
            "check",
            "--config-file",
            cfg(tool, "mypy.ini"),
            "--mode",
            "mypy",
            "--strict",
            fx,
        ]
    raise KeyError(tool)


def legacy_cmd(tool: str, target: str, tmp: str) -> list[str]:
    """Default (non-strict) config; caches disabled / redirected to temp."""
    base = launcher(tool)
    if tool == "mypy":
        return [*base, "--no-incremental", "--cache-dir", str(Path(tmp) / "mypy_cache"), target]
    if tool in ("pyright", "basedpyright"):
        return [*base, "--outputjson", target]
    if tool == "ty":
        return [*base, "check", "--output-format", "concise", target]
    if tool == "pyrefly":
        return [*base, "check", "--output-format", "min-text", target]
    if tool == "zuban":
        return [*base, "check", target]
    raise KeyError(tool)


def run(cmd: list[str], cwd: str, timeout: float | None = 900) -> RunResult:
    env = dict(os.environ)
    env.update({"PYTHONUTF8": "1", "NO_COLOR": "1"})
    env.pop("FORCE_COLOR", None)
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
            check=False,
        )
        out, err = proc.communicate()
        timed_out = True
    dt = time.perf_counter() - t0
    return RunResult(
        seconds=dt,
        exit_code=None if timed_out else proc.returncode,
        timed_out=timed_out,
        stdout=out.decode("utf-8", "replace"),
        stderr=err.decode("utf-8", "replace"),
    )


def combined(r: RunResult) -> str:
    s = r.stdout
    if r.stderr.strip():
        s += ("\n" if s and not s.endswith("\n") else "") + "--- stderr ---\n" + r.stderr
    return s


# ---------------------------------------------------------------- PyPI metadata


type PlatformTest = Callable[[str], bool]


def wheel_support(wheels: list[str], *, platform_ok: PlatformTest) -> str:
    """Report whether any wheel satisfies the platform test."""
    for n in wheels:
        if platform_ok(n):
            return "yes (" + ("any" if n.endswith("-any.whl") else "platform") + " wheel)"
    return "no"


def is_any_wheel(name: str) -> bool:
    return name.endswith("-any.whl")


def is_windows_wheel(name: str) -> bool:
    return is_any_wheel(name) or "win_amd64" in name or "win32" in name


def is_linux_wheel(name: str) -> bool:
    return is_any_wheel(name) or ("manylinux" in name and "x86_64" in name)


def is_macos_wheel(name: str) -> bool:
    return is_any_wheel(name) or ("macosx" in name and ("arm64" in name or "universal2" in name))


def license_text(info: dict[str, Json]) -> str:
    lic = as_str(info.get("license_expression")) or ""
    if not lic:
        raw = as_str(info.get("license")).strip()
        lic = raw.splitlines()[0][:80] if as_str(info.get("license")) else ""
    if not lic:
        cl = [
            c.split("::")[-1].strip()
            for c in map(as_str, as_list(info.get("classifiers", [])))
            if c.startswith("License ::")
        ]
        lic = ", ".join(cl)
    return lic


def pypi_meta(tool: str) -> Result:
    pkg, ver, _ = TOOLS[tool]
    try:
        d = as_dict(fetch_json(f"https://pypi.org/pypi/{pkg}/{ver}/json"))
        latest = as_str(
            as_dict(as_dict(fetch_json(f"https://pypi.org/pypi/{pkg}/json"))["info"])["version"],
        )
    except (OSError, http.client.HTTPException, ValueError, KeyError) as e:
        return {"error": repr(e)}
    info = as_dict(d["info"])
    files = [as_dict(f) for f in as_list(d["urls"])]
    names = [as_str(f["filename"]) for f in files]
    wheels = [n for n in names if n.endswith(".whl")]
    return {
        "version": ver,
        "latest_on_pypi": latest,
        "released": min(as_str(f["upload_time"]) for f in files)[:10],
        "license": license_text(info) or "(not stated in PyPI metadata)",
        "wheel_windows": wheel_support(wheels, platform_ok=is_windows_wheel),
        "wheel_linux_x86_64": wheel_support(wheels, platform_ok=is_linux_wheel),
        "wheel_macos_arm64": wheel_support(wheels, platform_ok=is_macos_wheel),
        "sdist": "yes" if any(n.endswith((".tar.gz", ".zip")) for n in names) else "no",
        "n_files": len(names),
    }


# ---------------------------------------------------------------- output parsing

MYPY_RE = re.compile(r"^(?P<f>.+?\.py):\d+:(?:\d+:)? (?P<sev>error|warning): (?P<m>.*)$")
PYRIGHT_RE = re.compile(r"^\s*(?P<f>.+?\.py):\d+:\d+ - (?P<sev>error|warning): (?P<m>.*)$")
TY_HDR = re.compile(r"^(?P<sev>error|warning)(?:\[(?P<code>[^\]]+)\])?: (?P<m>.*)$")
PYREFLY_HDR = re.compile(r"^\s*(?P<sev>ERROR|WARN)\s+(?P<m>.*)$")
ARROW = re.compile(r"^\s*--> (?P<f>.+?\.py):\d+")


def parse_mypy_diags(text: str) -> list[Diag]:
    diags: list[Diag] = []
    for line in text.splitlines():
        m = MYPY_RE.match(line)
        if m:
            diags.append(Diag(Path(m["f"]).name, m["m"]))
    return diags


def parse_pyright_diags(text: str) -> list[Diag]:
    diags: list[Diag] = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = PYRIGHT_RE.match(line)
        if m:
            msg = m["m"]
            j = i + 1
            while j < len(lines) and lines[j].startswith("    ") and not PYRIGHT_RE.match(lines[j]):
                msg += " " + lines[j].strip()
                j += 1
            diags.append(Diag(Path(m["f"]).name, msg))
    return diags


def parse_arrow_diags(tool: str, text: str) -> list[Diag]:
    """Parse ty / pyrefly output: a header line followed by an ``-->`` location line."""
    diags: list[Diag] = []
    hdr = TY_HDR if tool == "ty" else PYREFLY_HDR
    cur: str | None = None
    for line in text.splitlines():
        m = hdr.match(line)
        if m:
            cur = m["m"] + (f" [{m['code']}]" if tool == "ty" and m["code"] else "")
            continue
        a = ARROW.match(line)
        if a and cur is not None:
            diags.append(Diag(Path(a["f"]).name, cur))
            cur = None
    return diags


def parse_diags(tool: str, text: str) -> list[Diag]:
    if tool in ("mypy", "zuban"):
        return parse_mypy_diags(text)
    if tool in ("pyright", "basedpyright"):
        return parse_pyright_diags(text)
    return parse_arrow_diags(tool, text)


def summary_mypy(text: str) -> Result:
    out: Result = {}
    m = re.search(r"Found (\d+) errors? in (\d+) files? \(checked (\d+) source files?\)", text)
    if m:
        out.update(errors=int(m[1]), files_with_errors=int(m[2]), files_checked=int(m[3]))
    elif re.search(r"Success: no issues found in (\d+) source files?", text):
        count = re.search(r"in (\d+) source", text)
        out.update(errors=0, files_checked=int(count[1]) if count else 0)
    return out


def summary_pyright(stdout: str) -> Result:
    out: Result = {}
    with contextlib.suppress(ValueError, KeyError):
        j = as_dict(parse_json(stdout[stdout.index("{") :]))
        s = as_dict(j["summary"])
        out.update(
            errors=s["errorCount"],
            warnings=s["warningCount"],
            files_checked=s["filesAnalyzed"],
            tool_seconds=s.get("timeInSec"),
        )
    return out


def summary_ty(text: str) -> Result:
    out: Result = {}
    m = re.search(r"Found (\d+) diagnostics?", text)
    if m:
        out["errors"] = int(m[1])
    elif "All checks passed" in text:
        out["errors"] = 0
    return out


def summary_pyrefly(text: str) -> Result:
    out: Result = {}
    for line in reversed(text.splitlines()):
        m = re.search(r"INFO\s+(\d+) errors?", line)
        if m:
            out["errors"] = int(m[1])
            break
    return out


def summary_info(tool: str, text: str, stdout: str) -> Result:
    """Tool-reported totals (errors, files) when printed."""
    if tool in ("mypy", "zuban"):
        return summary_mypy(text)
    if tool in ("pyright", "basedpyright"):
        return summary_pyright(stdout)
    if tool == "ty":
        return summary_ty(text)
    if tool == "pyrefly":
        return summary_pyrefly(text)
    return {}


def count_error_lines(tool: str, r: RunResult) -> int:
    if tool in ("pyright", "basedpyright"):
        s = summary_info(tool, "", r.stdout)
        if "errors" in s:
            return as_int(s["errors"])
    return sum(1 for ln in combined(r).splitlines() if re.search("error", ln, re.IGNORECASE))


def write_trunc(path: Path, text: str, limit: int = TRUNC_LIMIT) -> bool:
    lines = text.splitlines()
    trunc = len(lines) > limit
    if trunc:
        kept = "\n".join(lines[:limit])
        text = kept + f"\n... [TRUNCATED: {len(lines)} lines total, first {limit} kept]\n"
    path.write_text(text, encoding="utf-8")
    return trunc


# ---------------------------------------------------------------- per-tool bench


def median_seconds(runs: list[RunResult]) -> float:
    return statistics.median(x.seconds for x in runs)


def bench_fixtures(tool: str, tmp: str, bench: Bench) -> Result:
    fcmd = fixture_cmd(tool, tmp)
    fruns = [run(fcmd, str(CONFIGS / tool), bench.timeout) for _ in range(bench.runs)]
    first = fruns[0]
    text = combined(first)
    header = f"$ (cwd={CONFIGS / tool})\n$ {' '.join(fcmd)}\n# exit={first.exit_code}\n\n"
    (bench.evidence / f"fixtures-{tool}.txt").write_text(header + text, encoding="utf-8")
    diags = parse_diags(tool, first.stdout + "\n" + first.stderr)
    names = sorted(p.name for p in FIXTURES.glob("*.py"))
    per: dict[str, list[str]] = {n: [] for n in names}
    unattributed = 0
    for d in diags:
        if d.file in per:
            per[d.file].append(d.msg)
        else:
            unattributed += 1
    return {
        "cmd": list[Json](fcmd),
        "cwd": str(CONFIGS / tool),
        "exit": first.exit_code,
        "timeout": first.timed_out,
        "seconds": [x.seconds for x in fruns],
        "median_seconds": median_seconds(fruns),
        "reported": {n: bool(per[n]) for n in names},
        "messages": {n: list[Json](msgs) for n, msgs in per.items()},
        "unattributed_diags": unattributed,
        "total_diags": len(diags),
    }


def bench_legacy(tool: str, legacy: Path, tmp: str, bench: Bench) -> Result:
    lcmd = legacy_cmd(tool, str(legacy), tmp)
    lruns: list[RunResult] = []
    trunc = False
    for i in range(bench.runs):
        r = run(lcmd, tmp, bench.timeout)
        lruns.append(r)
        if i == 0:
            body = (
                f"$ (cwd=temp dir)\n$ {' '.join(lcmd)}\n"
                f"# exit={r.exit_code} timeout={r.timed_out} seconds={r.seconds:.2f}\n\n"
                + combined(r)
            )
            trunc = write_trunc(bench.evidence / f"legacy-{tool}.txt", body)
        if r.timed_out:
            break
    r0 = lruns[0]
    warm = [x.seconds for x in lruns[1:] if not x.timed_out]
    return {
        "cmd": list[Json](lcmd),
        "cwd": "<fresh temp dir>",
        "exit_codes": [x.exit_code for x in lruns],
        "timeouts": [x.timed_out for x in lruns],
        "seconds": [x.seconds for x in lruns],
        "cold_seconds": r0.seconds,
        "warm_seconds": min(warm) if warm else None,
        "error_lines": count_error_lines(tool, r0),
        "summary": summary_info(tool, combined(r0), r0.stdout),
        "last_line": next((ln for ln in reversed(combined(r0).splitlines()) if ln.strip()), ""),
        "output_truncated_in_evidence": trunc,
        "stderr_head": r0.stderr[:500],
    }


def line_distance(path: Path) -> int:
    """Distance of the file's line count from the preferred single-file size."""
    with path.open("rb") as fh:
        return abs(sum(1 for _ in fh) - SINGLE_FILE_TARGET_LINES)


def bench_single(tool: str, legacy: Path, tmp: str, timeout: float) -> Result:
    sf = legacy / SINGLE_FILE_REL
    single_note: str | None = None
    if not sf.exists():
        sf = min(legacy.rglob("*.py"), key=line_distance)
        single_note = f"{SINGLE_FILE_REL} missing; used {sf}"
    scmd = legacy_cmd(tool, str(sf), tmp)
    sruns = [run(scmd, tmp, timeout) for _ in range(SINGLE_RUNS)]
    return {
        "file": str(sf),
        "note": single_note,
        "cmd": list[Json](scmd),
        "seconds": [x.seconds for x in sruns],
        "median_seconds": median_seconds(sruns),
        "exit_codes": [x.exit_code for x in sruns],
        "error_lines": count_error_lines(tool, sruns[0]),
    }


def bench_tool(tool: str, legacy: Path, bench: Bench, *, skip_legacy: bool) -> Result:
    res: Result = {"tool": tool, "meta": pypi_meta(tool)}
    tmp = tempfile.mkdtemp(prefix=f"tc_{tool}_")
    try:
        # version + launcher overhead
        vcmd = [*launcher(tool), "--version"]
        vr = [run(vcmd, tmp, VERSION_TIMEOUT) for _ in range(VERSION_RUNS)]
        res["version_output"] = vr[-1].stdout.strip() or vr[-1].stderr.strip()
        res["version_cmd_exit"] = vr[-1].exit_code
        res["launcher_overhead_s"] = median_seconds(vr)

        res["fixtures"] = bench_fixtures(tool, tmp, bench)
        if skip_legacy:
            return res
        res["legacy"] = bench_legacy(tool, legacy, tmp, bench)
        res["single_file"] = bench_single(tool, legacy, tmp, bench.timeout)
    except BENCH_ERRORS as e:
        res["failed"] = repr(e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


# ---------------------------------------------------------------- report


def fmt(x: float | None, nd: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{nd}f}"


def md_header(machine: dict[str, Json], legacy: Path, runs: int) -> list[str]:
    return [
        "# Type checker measurements (stage 0)",
        "",
        (
            f"Machine: {machine['platform']}, {machine['cpu_count']} CPUs, "
            f"benchmark script on Python {machine['python']}, uv: {machine['uv']}, "
            f"date {machine['date']}."
        ),
        f"Legacy corpus: `{legacy}` (read-only), runs per measurement: {runs}.",
        "",
        "## 1. Metadata (PyPI)",
        "",
    ]


def md_metadata(tools: list[str], res: dict[str, Json]) -> list[str]:
    o = [
        (
            "| tool | version | latest on PyPI at run | released | license | wheel Windows "
            "| wheel Linux x86_64 | wheel macOS arm64 | sdist |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for t in tools:
        m = as_dict(as_dict(res[t])["meta"])
        if "error" in m:
            o.append(f"| {t} | metadata error: {m['error']} |||||||")
            continue
        o.append(
            f"| {t} | {m['version']} | {m['latest_on_pypi']} | {m['released']} | {m['license']} "
            f"| {m['wheel_windows']} | {m['wheel_linux_x86_64']} | {m['wheel_macos_arm64']} "
            f"| {m['sdist']} |",
        )
    versions = "; ".join(f"{t}: `{as_dict(res[t]).get('version_output', '?')}`" for t in tools)
    o += ["", "Reported versions (`--version`): " + versions, ""]
    return o


def fixture_cell(f: dict[str, Json], name: str) -> str:
    if not f:
        return "fail"
    return "✓" if as_dict(f["reported"]).get(name) else "✗"


def md_fixture_matrix(tools: list[str], res: dict[str, Json]) -> list[str]:
    o = [
        (
            "## 2. Fixture matrix (strict config; ✓ = at least one diagnostic attributed "
            "to the file, ✗ = silent)"
        ),
        "",
    ]
    names = sorted(p.name for p in FIXTURES.glob("*.py") if p.name != "control_clean.py")
    fx = {t: as_dict(as_dict(res[t]).get("fixtures")) for t in tools}
    o.append("| fixture | " + " | ".join(tools) + " |")
    o.append("|---|" + "---|" * len(tools))
    o += [f"| {n} | " + " | ".join(fixture_cell(fx[t], n) for t in tools) + " |" for n in names]

    def false_positive(f: dict[str, Json]) -> str:
        if not f:
            return "fail"
        return "FALSE POSITIVE" if as_dict(f["reported"]).get("control_clean.py") else "clean"

    def total(f: dict[str, Json]) -> str:
        return "fail" if not f else f"{f['total_diags']} (exit {f['exit']})"

    def unattributed(f: dict[str, Json]) -> str:
        return "fail" if not f else str(f["unattributed_diags"])

    o.append(
        "| control_clean false positive | "
        + " | ".join(false_positive(fx[t]) for t in tools)
        + " |"
    )
    o.append("| total diagnostics (exit code) | " + " | ".join(total(fx[t]) for t in tools) + " |")
    o.append(
        "| diagnostics not attributed to a fixture | "
        + " | ".join(unattributed(fx[t]) for t in tools)
        + " |",
    )
    return o


def timing_notes(r: dict[str, Json]) -> list[str]:
    lg = as_dict(r.get("legacy"))
    s = as_dict(r.get("single_file"))
    notes: list[str] = []
    if r.get("failed"):
        notes.append("FAILED: " + as_str(r["failed"]))
    if lg and any(as_list(lg["timeouts"])):
        notes.append("TIMEOUT 900 s")
    if lg and lg["output_truncated_in_evidence"]:
        notes.append("legacy output truncated to 2000 lines in evidence file")
    if s and s.get("note"):
        notes.append(as_str(s["note"]))
    return notes


def timing_row(t: str, r: dict[str, Json]) -> str:
    f = as_dict(r.get("fixtures"))
    lg = as_dict(r.get("legacy"))
    s = as_dict(r.get("single_file"))
    exit_codes = ",".join(str(c) for c in as_list(lg["exit_codes"])) if lg else "n/a"
    return (
        f"| {t} | {fmt(as_opt_float(r.get('launcher_overhead_s')))} "
        f"| {fmt(as_opt_float(f.get('median_seconds')))} "
        f"| {fmt(as_opt_float(s.get('median_seconds')))} | "
        f"{fmt(as_opt_float(lg.get('cold_seconds')))} "
        f"| {fmt(as_opt_float(lg.get('warm_seconds')))} "
        f"| {lg['error_lines'] if lg else 'n/a'} | "
        f"{(json.dumps(lg['summary']) if lg else 'n/a')} | {exit_codes} "
        f"| {'; '.join(timing_notes(r))} |"
    )


def legacy_seconds(r: dict[str, Json]) -> list[float]:
    return [round(as_float(x), 1) for x in as_list(as_dict(r["legacy"])["seconds"])]


def md_timing(tools: list[str], res: dict[str, Json]) -> list[str]:
    o = [
        "",
        (
            "## 3. Timing (seconds, wall clock via `time.perf_counter`, "
            "includes `uvx` launcher overhead)"
        ),
        "",
        (
            "| tool | uvx --version overhead | fixtures run (median) | single file (median) "
            "| legacy cold | legacy warm (min of rest) | legacy error count "
            "| legacy tool-reported | legacy exit | notes |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    o += [timing_row(t, as_dict(res[t])) for t in tools]
    per_run = "; ".join(
        f"{t}: legacy {legacy_seconds(as_dict(res[t]))}"
        for t in tools
        if as_dict(as_dict(res[t]).get("legacy"))
    )
    o += [
        "",
        "Error count = lines matching `error` (case-insensitive) in the first legacy run; "
        "for pyright/basedpyright it is `summary.errorCount` from `--outputjson`. "
        "ty is run with `--output-format concise` and pyrefly with "
        "`--output-format min-text` on the legacy corpus so that lines map ~1:1 to "
        "diagnostics. Per-run times: " + per_run,
        "",
    ]
    return o


def md_commands(tools: list[str], res: dict[str, Json]) -> list[str]:
    o = ["## 4. Exact command lines", ""]
    for t in tools:
        r = as_dict(res[t])
        o.append(f"### {t}")
        fx = as_dict(r.get("fixtures"))
        lg = as_dict(r.get("legacy"))
        sf = as_dict(r.get("single_file"))
        if fx:
            o.append(
                f"- fixtures (cwd `{fx['cwd']}`): `{' '.join(map(as_str, as_list(fx['cmd'])))}`"
            )
        if lg:
            o.append(f"- legacy (cwd {lg['cwd']}): `{' '.join(map(as_str, as_list(lg['cmd'])))}`")
        if sf:
            o.append(f"- single file: `{' '.join(map(as_str, as_list(sf['cmd'])))}`")
        o.append("")
    return o


def md_messages(tools: list[str], res: dict[str, Json]) -> list[str]:
    o = ["## 5. First diagnostic message per fixture", ""]
    for t in tools:
        f = as_dict(as_dict(res[t]).get("fixtures"))
        if not f:
            continue
        o.append(f"### {t}")
        messages = as_dict(f["messages"])
        for n in sorted(messages):
            ms = [as_str(m) for m in as_list(messages[n])]
            o.append(
                f"- `{n}`: " + (" / ".join(m[:160] for m in ms[:3]) if ms else "(silent)"),
            )
        o.append("")
    return o


def make_md(results: Result, machine: dict[str, Json], legacy: Path, runs: int) -> str:
    res = as_dict(results["tools"])
    tools = [t for t in TOOLS if t in res]
    o = md_header(machine, legacy, runs)
    o += md_metadata(tools, res)
    o += md_fixture_matrix(tools, res)
    o += md_timing(tools, res)
    o += md_commands(tools, res)
    o += md_messages(tools, res)
    return "\n".join(o) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy-path", type=Path, default=DEFAULT_LEGACY_PATH)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--tools", nargs="*", default=list(TOOLS))
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--skip-legacy", action="store_true")
    a = ap.parse_args(argv, namespace=Options())

    legacy = a.legacy_path if a.legacy_path.is_absolute() else (REPO / a.legacy_path).resolve()
    if not legacy.exists():
        print(f"legacy path not found: {legacy}", file=sys.stderr)
        return 2
    out = a.out if a.out.is_absolute() else REPO / a.out
    evidence = out.parent  # every output file goes next to --out
    evidence.mkdir(parents=True, exist_ok=True)
    existing = as_dict(parse_json(out.read_text(encoding="utf-8"))) if out.exists() else {}
    uvv = subprocess.run(
        ["uv", "--version"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    machine: dict[str, Json] = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python": sys.version.split()[0],
        "uv": uvv,
        "date": time.strftime("%Y-%m-%d"),
    }
    tools_out = as_dict(existing.get("tools", {}))
    results: Result = {
        "machine": machine,
        "legacy_path": str(legacy),
        "runs": a.runs,
        "tools": tools_out,
    }
    for t in a.tools:
        print(f"== {t}", flush=True)
        bench = Bench(a.runs, a.timeout, evidence)
        tools_out[t] = bench_tool(t, legacy, bench, skip_legacy=a.skip_legacy)
        out.write_text(json.dumps(results, indent=2), encoding="utf-8")
        r = as_dict(tools_out[t])
        print("  failed:" if r.get("failed") else "  ok", r.get("failed", ""), flush=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    (evidence / "results.md").write_text(
        make_md(results, machine, legacy, a.runs), encoding="utf-8"
    )
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
