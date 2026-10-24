"""Collect Python 3.12-3.15 support data for PyPI packages (stdlib only, Python >= 3.12).

Run from the repo root:
    uv run --no-sync python -m scripts.python_support_matrix [--packages a,b] [--out-dir DIR]

Wheel matching rules: cpXY-cpXY wheels match XY; cpNN-abi3 wheels match every
cp version >= NN (reported as "abi3>=cpNN"); py3*-none-* wheels match every cp
version. Free-threaded (abi tag ending in 't') wheels are ignored. Platform
tags: win_amd64; manylinux*x86_64; macosx*arm64 (macosx*universal2 also counted).
"""

import argparse
import datetime as dt
import hashlib
import http.client
import itertools
import json
import re
import sys
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scripts._json import (
    Json,
    as_dict,
    as_list,
    as_str,
    fetch_bytes,
    parse_json,
)

PACKAGES = (
    "PySide6, PyQt6, wxPython, pywebview, flet, toga, textual, pyserial, cryptography, orjson, "
    "msgspec, pydantic, aiohttp, httpx, requests, jinja2, docxtpl, python-docx, lxml, pywin32, "
    "psutil, playsound3, polib, python-dateutil, chardet, sportident, boltons, pyusb, pywinusb, "
    "hidapi, pytest, hypothesis, pytest-cov, pytest-xdist, mutmut, coverage, ruff, mypy, pyright, "
    "basedpyright, ty, pyrefly, zuban, import-linter, pre-commit, pip-audit, pip-licenses, "
    "licensecheck, liccheck, cyclonedx-bom, cx_Freeze, pyinstaller, nuitka, briefcase, uv, "
    "poethepoet, nox, tox, deptry, vulture, bandit, pydocstyle"
)
CP = ["312", "313", "314", "315"]
PLATS = {
    "win": r"win_amd64",
    "linux": r"manylinux.*x86_64",
    "mac": r"macosx.*(arm64|universal2)",
}
UA = {"User-Agent": "python-support-matrix/1.0 (stage-0 evidence)"}
VERSIONS = ("3.12", "3.13", "3.14", "3.15")
HTTP_NOT_FOUND = 404
MAX_LICENSE_LEN = 80
LICENSE_SNIPPET_LEN = 60
MIN_WHEEL_PARTS = 5
DEFAULT_OUT_DIR = Path("docs/evidence/stage-0")
FETCH_ERRORS = (OSError, http.client.HTTPException, ValueError)

type Record = dict[str, Json]


class Options(argparse.Namespace):
    """Typed command line options."""

    packages: str = PACKAGES
    out_dir: Path = DEFAULT_OUT_DIR


def http_get(url: str, tries: int = 3) -> bytes:
    """Fetch ``url`` with retries; a 404 is not retried."""
    last: Exception | None = None
    for _ in range(tries):
        try:
            return fetch_bytes(url, headers=UA, timeout=30.0)
        except urllib.error.HTTPError as e:
            last = e
            if e.code == HTTP_NOT_FOUND:
                break
        except FETCH_ERRORS as e:
            last = e
    if last is None:
        msg = f"no attempts made for {url}"
        raise RuntimeError(msg)
    raise last


def vkey(v: str) -> list[int]:
    return [int(p) if p.isdigit() else -1 for p in re.split(r"[.\-+_]", v)]


def is_pre(v: str) -> bool:
    return bool(re.search(r"\d(a|b|rc|c|dev|alpha|beta|pre)\d*", v, re.IGNORECASE)) or ".dev" in v


def file_list(value: Json) -> list[dict[str, Json]]:
    return [as_dict(f) for f in as_list(value)]


def latest_stable(data: dict[str, Json]) -> str | None:
    rel = as_dict(data.get("releases", {}))
    cands = [
        v
        for v, files in rel.items()
        if files and not is_pre(v) and not all(f.get("yanked") for f in file_list(files))
    ]
    v = as_str(as_dict(data["info"])["version"])
    if v in cands:
        return v
    return max(cands, key=vkey) if cands else None


def parse_wheel(fn: str) -> tuple[list[str], list[str], list[str]] | None:
    parts = fn[:-4].split("-")
    if len(parts) < MIN_WHEEL_PARTS:
        return None
    return parts[-3].split("."), parts[-2].split("."), parts[-1].split(".")


def tag_match(py: str, abi: str, n: int, plats: list[str]) -> str | None:
    """Describe how one (python tag, abi tag) pair matches cp version ``n``, if at all."""
    if abi.startswith("cp") and abi.endswith("t"):
        return None
    m = re.fullmatch(r"cp(\d)(\d+)", py)
    if m:
        num = int(m.group(1) + m.group(2))
        if abi == py and num == n:
            return f"cp{n}"
        if abi == "abi3" and num <= n:
            return f"abi3>=cp{num}"
    elif py.startswith("py3") and abi == "none":
        return "py3-none-any" if "any" in plats else "py3-none"
    return None


def wheel_match(files: list[dict[str, Json]], cp: str, plat_re: str) -> str | None:
    """Return best match descriptor or None."""
    n = int(cp)
    best: str | None = None
    for f in files:
        if f.get("packagetype") != "bdist_wheel" or f.get("yanked"):
            continue
        p = parse_wheel(as_str(f["filename"]))
        if not p:
            continue
        pys, abis, plats = p
        if not any(t == "any" or re.fullmatch(plat_re, t) for t in plats):
            continue
        for py, abi in itertools.product(pys, abis):
            found = tag_match(py, abi, n, plats)
            if found == f"cp{n}":
                return "cp" + cp
            best = best or found
    return best


def license_of(info: dict[str, Json]) -> str | None:
    le = info.get("license_expression")
    if le:
        return as_str(le)
    lic = as_str(info.get("license") or "").strip()
    if lic and len(lic) < MAX_LICENSE_LEN and "\n" not in lic:
        return lic
    cls = [
        c.split("::")[-1].strip()
        for c in map(as_str, as_list(info.get("classifiers", [])))
        if c.startswith("License ::")
    ]
    cls = [c for c in cls if c != "OSI Approved"] or cls
    if cls:
        return "; ".join(cls)
    if lic:
        return lic.splitlines()[0][:LICENSE_SNIPPET_LEN] + "..."
    return None


def requires_python_of(info: dict[str, Json], files: list[dict[str, Json]]) -> Json:
    return info.get("requires_python") or next(
        (f.get("requires_python") for f in files if f.get("requires_python")),
        None,
    )


def describe(rec: Record, data: dict[str, Json]) -> Record:
    """Fill ``rec`` from the parsed PyPI JSON ``data``."""
    info = as_dict(data["info"])
    ver = latest_stable(data)
    rec["latest"] = ver
    rec["info_version"] = info["version"]
    if not ver:
        rec["error"] = "no stable release"
        return rec
    files = file_list(as_dict(data["releases"])[ver])
    ups = [as_str(f["upload_time_iso_8601"]) for f in files if f.get("upload_time_iso_8601")]
    rec["released"] = max(ups)[:10] if ups else None
    rec["requires_python"] = requires_python_of(info, files)
    cl = {as_str(c) for c in as_list(info.get("classifiers", []))}
    rec["classifiers"] = {v: f"Programming Language :: Python :: {v}" in cl for v in VERSIONS}
    rec["license"] = license_of(info)
    rec["wheel_count"] = sum(1 for f in files if f.get("packagetype") == "bdist_wheel")
    rec["sdist"] = any(f.get("packagetype") == "sdist" for f in files)
    rec["wheels"] = {cp: {pl: wheel_match(files, cp, rx) for pl, rx in PLATS.items()} for cp in CP}
    return rec


def process(name: str) -> Record:
    url = f"https://pypi.org/pypi/{name}/json"
    rec: Record = {"name": name, "url": url}
    try:
        raw = http_get(url)
    except FETCH_ERRORS as e:
        rec["error"] = f"{type(e).__name__}: {e}"
        return rec
    rec["sha256"] = hashlib.sha256(raw).hexdigest()
    return describe(rec, as_dict(parse_json(raw)))


def cell(rec: Record, ver: str) -> str:
    cls = bool(as_dict(rec["classifiers"])[ver])
    w = as_dict(as_dict(rec["wheels"])["3" + ver[2:]])
    have = [p for p, m in w.items() if m]
    if len(have) == len(PLATS):
        whl = "whl"
    elif have:
        whl = f"whl({','.join(have)})"
    else:
        whl = ""
    if cls and whl:
        return f"cls+{whl}"
    return whl or ("cls" if cls else "-")


def esc(s: Json) -> str:
    return str(s if s is not None else "-").replace("|", "\\|")


def json_dumps(value: Json) -> str:
    """Serialize with the report's two-space indentation."""
    return json.dumps(value, indent=2)


def fetch_eol(out: Path) -> Record:
    """Download the endoflife.date schedule and store it next to the report."""
    eol: Record = {"url": "https://endoflife.date/api/python.json"}
    try:
        raw = http_get(as_str(eol["url"]))
        eol["sha256"] = hashlib.sha256(raw).hexdigest()
        eol["data"] = parse_json(raw)
        (out / "endoflife-python.json").write_text(json_dumps(eol["data"]), encoding="utf-8")
    except FETCH_ERRORS as e:
        eol["error"] = f"{type(e).__name__}: {e}"
    return eol


def table_row(r: Record) -> str:
    if "error" in r:
        return f"| {r['name']} | ERROR | | | | | | | {esc(r['error'])} |"
    return (
        "| "
        + " | ".join(
            [
                as_str(r["name"]),
                as_str(r["latest"]),
                as_str(r["released"]) or "-",
                esc(r["requires_python"]),
                *[cell(r, v) for v in VERSIONS],
                esc(r["license"]),
            ],
        )
        + " |"
    )


def eol_lines(eol: Record) -> list[str]:
    if "data" not in eol:
        return [f"endoflife.date fetch failed: {eol['error']}"]
    lines = ["| cycle | releaseDate | eol (security end) | latest |", "|---|---|---|---|"]
    cycles = [as_dict(c) for c in as_list(eol["data"])]
    lines += [
        f"| {c['cycle']} | {c.get('releaseDate')} | {c.get('eol')} | {c.get('latest')} |"
        for c in sorted(cycles, key=lambda c: vkey(as_str(c["cycle"])))
        if vkey("3.9") <= vkey(as_str(c["cycle"])) <= vkey("3.15")
    ]
    return lines


def render_md(now: str, recs: list[Record], eol: Record) -> str:
    lines = [
        "# Python support matrix",
        "",
        f"Fetched: {now} (UTC)",
        "",
        (
            "Cells: `cls`=trove classifier, "
            "`whl`=wheels for win_amd64+manylinux x86_64+macosx arm64 "
            "(abi3/py3-none-any counted), `whl(win,linux,mac)`=only listed platforms, `-`=neither."
        ),
        "",
        "| package | latest | released | requires_python | 3.12 | 3.13 | 3.14 | 3.15 | license |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    fails = [r for r in recs if "error" in r]
    lines += [table_row(r) for r in recs]
    lines += ["", "## Python release/EOL schedule", ""]
    lines += eol_lines(eol)
    if fails:
        lines += ["", "## Fetch failures", ""] + [f"- {r['name']}: {r['error']}" for r in fails]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packages", default=PACKAGES, help="comma-separated package list")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    a = ap.parse_args(argv, namespace=Options())
    names = [n.strip() for n in a.packages.split(",") if n.strip()]
    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    with ThreadPoolExecutor(8) as ex:
        recs = list(ex.map(process, names))

    eol = fetch_eol(out)
    report: Record = {"fetched_at": now, "packages": list(recs), "endoflife": eol}
    (out / "python-support-matrix.json").write_text(json_dumps(report), encoding="utf-8")
    (out / "python-support-matrix.md").write_text(render_md(now, recs, eol), encoding="utf-8")
    failed = sum(1 for r in recs if "error" in r)
    print(f"ok: {len(recs) - failed}/{len(recs)} packages; eol={'data' in eol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
