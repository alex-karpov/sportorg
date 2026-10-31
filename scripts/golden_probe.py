"""Measure golden-file protection mechanisms for ADR-0008 (TASK-8 AC #7).

``scenarios`` builds a temporary git repository per scenario and mechanism and records whether the
mechanism detects the change. Mechanisms:

- ``a_trailer``: ``scripts/golden_guard.py`` (each golden commit needs ``Golden-Approved-By:``);
- ``c1_manifest_signers_in_repo``: prototype of a signed hash manifest (``ssh-keygen -Y``) whose
  allowed signers file lives in the repository;
- ``c2_manifest_signer_pinned_outside``: the same manifest, verified against the maintainer's key
  kept outside the repository (for example a CI variable).

Mechanism (b), CODEOWNERS with required review, lives in GitHub settings: ``facts`` records them
(through ``gh api``, raw responses cached outside the repository) together with history counts at a
pinned revision. Outputs are deterministic: no hashes of temporary commits, no timings.

Usage::

    uv run python -m scripts.golden_probe scenarios --out docs/evidence/stage-2/golden-guard
    uv run python -m scripts.golden_probe facts --out DIR --repo OWNER/NAME --rev REV --cache DIR
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts._json import Json, as_dict, as_list, as_str, parse_json
from scripts.archaeology.common import write_outputs
from scripts.golden_guard import check_range

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

type Outcome = Literal["detected", "passed", "unavailable"]
type Approval = Literal["none", "maintainer", "forged", "text_in_body"]

MECHANISMS = ("a_trailer", "c1_manifest_signers_in_repo", "c2_manifest_signer_pinned_outside")
NAMESPACE = "sportorg-golden"
SIGNER = "maintainer"
MANIFEST = "tests/golden.manifest"
SIGNERS = ".github/golden-signers"
AGENT_TRAILER = "Co-Authored-By: Claude"
ROOT = Path(__file__).resolve().parents[1]
GIT_ENV = {
    "GIT_AUTHOR_NAME": "probe",
    "GIT_AUTHOR_EMAIL": "probe@example.invalid",
    "GIT_COMMITTER_NAME": "probe",
    "GIT_COMMITTER_EMAIL": "probe@example.invalid",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
}


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    description: str
    change: Literal["add", "modify", "delete", "rename_out", "evil_merge", "non_golden"]
    approval: Approval


SCENARIOS = (
    Scenario("add", "new golden file, no approval", "add", "none"),
    Scenario("modify", "golden file edited, no approval", "modify", "none"),
    Scenario("delete", "golden file deleted, no approval", "delete", "none"),
    Scenario("rename_out", "golden file moved out of tests/golden/", "rename_out", "none"),
    Scenario("evil_merge", "golden file changed only in a merge resolution", "evil_merge", "none"),
    Scenario("approved", "golden file edited with maintainer approval", "modify", "maintainer"),
    Scenario("non_golden", "code change only", "non_golden", "none"),
    Scenario("text_in_body", "approval words in the body, not a trailer", "modify", "text_in_body"),
    Scenario("forged", "the committer (an agent) writes the approval itself", "modify", "forged"),
)
PASSING = frozenset({"approved", "non_golden"})
EXPECTED: dict[str, Outcome] = {
    s.name: "passed" if s.name in PASSING else "detected" for s in SCENARIOS
}


@dataclass(slots=True)
class Row:
    scenario: str
    description: str
    expected: Outcome
    results: dict[str, Outcome] = field(default_factory=dict[str, "Outcome"])


@dataclass(frozen=True, slots=True)
class Raw:
    """A cached ``gh api`` response: exit code and stdout."""

    exit: int
    stdout: str


# ---------------------------------------------------------------- temporary repositories


class Repo:
    path: Path

    def __init__(self, path: Path, *, init: bool = True) -> None:
        self.path = path
        if init:
            path.mkdir(parents=True)
            self.git("init", "--quiet", "--initial-branch=main")

    @classmethod
    def clone(cls, source: Path, path: Path) -> Repo:
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(source), str(path)],
            capture_output=True,
            check=True,
        )
        return cls(path, init=False)

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", *args],
            cwd=self.path,
            env=os.environ | GIT_ENV,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def write(self, name: str, text: str) -> None:
        target = self.path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        self.git("add", "--", name)

    def commit(self, message: str) -> None:
        self.git("commit", "--quiet", "--allow-empty", "-m", message)


class Signer:
    """Ed25519 keys of the maintainer and of an agent, made by ``ssh-keygen`` in a temp dir."""

    exe: str
    keys: Path
    pinned: Path

    def __init__(self, keys: Path, exe: str) -> None:
        self.exe = exe
        self.keys = keys
        for who in ("maintainer", "agent"):
            self._run("-q", "-t", "ed25519", "-N", "", "-C", who, "-f", str(keys / who))
        self.pinned = keys / "pinned-signers"
        self.pinned.write_text(self.signers_line("maintainer"), encoding="utf-8")

    def _run(self, *args: str, stdin: bytes | None = None) -> int:
        return subprocess.run(
            [self.exe, *args], input=stdin, capture_output=True, check=False
        ).returncode

    def signers_line(self, who: str) -> str:
        public = (self.keys / f"{who}.pub").read_text(encoding="utf-8").split()
        return f'{SIGNER} namespaces="{NAMESPACE}" {public[0]} {public[1]}\n'

    def sign(self, repo: Repo, who: str) -> None:
        manifest = repo.path / MANIFEST
        manifest.write_text(manifest_text(repo.path), encoding="utf-8", newline="\n")
        sig = repo.path / f"{MANIFEST}.sig"
        sig.unlink(missing_ok=True)
        if self._run("-Y", "sign", "-f", str(self.keys / who), "-n", NAMESPACE, str(manifest)):
            msg = "ssh-keygen -Y sign failed"
            raise RuntimeError(msg)
        repo.git("add", "--", MANIFEST, f"{MANIFEST}.sig")

    def verify(self, repo: Repo, signers: Path) -> bool:
        manifest = repo.path / MANIFEST
        sig = repo.path / f"{MANIFEST}.sig"
        if not manifest.exists() or not sig.exists() or not signers.exists():
            return False
        if manifest.read_text(encoding="utf-8") != manifest_text(repo.path):
            return False
        args = ("-Y", "verify", "-f", str(signers), "-I", SIGNER, "-n", NAMESPACE, "-s", str(sig))
        return self._run(*args, stdin=manifest.read_bytes()) == 0


def manifest_text(root: Path) -> str:
    golden = root / "tests" / "golden"
    files = sorted(p for p in golden.rglob("*") if p.is_file()) if golden.exists() else []
    lines = [
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}"
        for p in files
    ]
    return "".join(f"{line}\n" for line in lines)


# ---------------------------------------------------------------- scenarios


def _message(subject: str, approval: Approval, family: str) -> str:
    if family == "a" and approval in {"maintainer", "forged"}:
        return f"{subject}\n\nGolden-Approved-By: maintainer"
    if approval == "text_in_body":
        return f"{subject}\n\nGolden-Approved-By: maintainer\n\nMore text after it."
    return subject


def _approve(repo: Repo, approval: Approval, signer: Signer | None) -> None:
    if signer is None or approval in {"none", "text_in_body"}:
        return
    if approval == "forged":
        repo.write(SIGNERS, signer.signers_line("agent"))
        signer.sign(repo, "agent")
    else:
        signer.sign(repo, "maintainer")


def _build(path: Path, scenario: Scenario, signer: Signer | None) -> Repo:
    """Base on main (approved golden file), then the scenario on branch ``work``."""
    family = "a" if signer is None else "c"
    repo = Repo(path)
    repo.write("tests/golden/a.json", "{}\n")
    if signer is not None:
        repo.write(SIGNERS, signer.signers_line("maintainer"))
        signer.sign(repo, "maintainer")
    repo.commit(_message("base", "maintainer", family))
    repo.git("switch", "--quiet", "-c", "work")
    match scenario.change:
        case "add":
            repo.write("tests/golden/b.json", "{}\n")
        case "modify":
            repo.write("tests/golden/a.json", '{"changed": true}\n')
        case "delete":
            repo.git("rm", "--quiet", "tests/golden/a.json")
        case "rename_out":
            repo.git("mv", "tests/golden/a.json", "tests/a.json")
        case "non_golden":
            repo.write("src.txt", "code\n")
        case "evil_merge":
            repo.git("switch", "--quiet", "-c", "side", "main")
            repo.write("side.txt", "side\n")
            repo.commit("side")
            repo.git("switch", "--quiet", "work")
            repo.write("work.txt", "work\n")
            repo.commit("work")
            repo.git("merge", "--quiet", "--no-ff", "--no-commit", "side")
            repo.write("tests/golden/a.json", '{"merged": true}\n')
    _approve(repo, scenario.approval, signer)
    repo.commit(_message(f"scenario {scenario.name}", scenario.approval, family))
    return repo


def _outcome(*, detected: bool) -> Outcome:
    return "detected" if detected else "passed"


def run_scenarios(
    workdir: Path, mechanisms: Sequence[str] = MECHANISMS, ssh_keygen: str | None = None
) -> list[Row]:
    rows: list[Row] = []
    signer: Signer | None = None
    wants_c = any(m.startswith("c") for m in mechanisms)
    if wants_c and ssh_keygen is not None:
        keys = workdir / "keys"
        keys.mkdir()
        signer = Signer(keys, ssh_keygen)
    for scenario in SCENARIOS:
        row = Row(scenario.name, scenario.description, EXPECTED[scenario.name])
        if "a_trailer" in mechanisms:
            repo = _build(workdir / f"a-{scenario.name}", scenario, None)
            found = check_range("HEAD", base=None, cwd=repo.path)
            row.results["a_trailer"] = _outcome(detected=bool(found))
        if wants_c:
            if signer is None:
                for name in mechanisms[1:]:
                    row.results[name] = "unavailable"
            else:
                repo = _build(workdir / f"c-{scenario.name}", scenario, signer)
                in_repo = signer.verify(repo, repo.path / SIGNERS)
                outside = signer.verify(repo, signer.pinned)
                row.results["c1_manifest_signers_in_repo"] = _outcome(detected=not in_repo)
                row.results["c2_manifest_signer_pinned_outside"] = _outcome(detected=not outside)
        rows.append(row)
    return rows


def _ssh_keygen_version(exe: str) -> str:
    result = subprocess.run(
        [exe.replace("ssh-keygen", "ssh"), "-V"], capture_output=True, text=True, check=False
    )
    return (result.stderr or result.stdout).strip()


def scenarios_command(out: Path) -> None:
    exe = shutil.which("ssh-keygen")
    with tempfile.TemporaryDirectory(prefix="golden-probe-") as tmp:
        rows = run_scenarios(Path(tmp), ssh_keygen=exe)
    matches = {m: sum(1 for r in rows if r.results.get(m) == r.expected) for m in MECHANISMS}
    data: Json = {
        "mechanisms": list(MECHANISMS),
        "ssh": _ssh_keygen_version(exe) if exe else "ssh-keygen not found",
        "matches_expected": dict[str, Json](matches),
        "scenarios": [
            {
                "scenario": r.scenario,
                "description": r.description,
                "expected": r.expected,
                "results": dict[str, Json](r.results),
            }
            for r in rows
        ],
    }
    header = "| scenario | expected | " + " | ".join(MECHANISMS) + " |"
    lines = [header, "|---" * (2 + len(MECHANISMS)) + "|"]
    for r in rows:
        cells = " | ".join(r.results.get(m, "-") for m in MECHANISMS)
        lines.append(f"| {r.scenario}: {r.description} | {r.expected} | {cells} |")
    lines.append(
        f"| **matches expected (of {len(rows)})** | | "
        + " | ".join(str(matches[m]) for m in MECHANISMS)
        + " |"
    )
    title = (
        "# Golden-file protection: scenario matrix (ADR-0008)\n\n"
        "Generated by `python -m scripts.golden_probe scenarios`; one temporary repository per "
        "scenario and mechanism. `detected` = the check fails, `passed` = the commit goes through."
    )
    write_outputs(out, "scenarios", data, "\n".join(lines), title)


# ---------------------------------------------------------------- facts


def git_facts(repo: Path, *, rev: str) -> dict[str, int]:
    """Signed, agent and author counts in the history of ``rev`` (counts only, no identities)."""
    sep = "\x1f"
    log = subprocess.run(
        ["git", "log", f"--format=%G?{sep}%ae{sep}%(trailers:only,unfold){sep}\x1e", rev],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    records = [r.strip("\n") for r in log.split("\x1e") if r.strip()]
    commits = [r.split(sep) for r in records]
    agent = [c for c in commits if AGENT_TRAILER in c[2]]
    return {
        "commits": len(commits),
        "signed_commits": sum(1 for c in commits if c[0] != "N"),
        "authors": len({c[1] for c in commits}),
        "agent_commits": len(agent),
        "agent_commit_authors": len({c[1] for c in agent}),
    }


def github_facts(raw: dict[str, Raw]) -> dict[str, Json]:
    repo = as_dict(parse_json(raw["repo"].stdout))
    protection = raw["protection"]
    return {
        "visibility": as_str(repo.get("visibility")),
        "owner_type": as_str(as_dict(repo.get("owner")).get("type")),
        "collaborators": len(as_list(parse_json(raw["collaborators"].stdout))),
        "rulesets": len(as_list(parse_json(raw["rulesets"].stdout))),
        "main_protected": protection.exit == 0,
    }


GH_ENDPOINTS: dict[str, str] = {
    "repo": "repos/{repo}",
    "collaborators": "repos/{repo}/collaborators",
    "rulesets": "repos/{repo}/rulesets",
    "protection": "repos/{repo}/branches/main/protection",
}


def _cached_gh(cache: Path, repo: str, fetch: Callable[[str], Raw]) -> dict[str, Raw]:
    """Read responses from ``cache``; fetch and store only the missing ones."""
    cache.mkdir(parents=True, exist_ok=True)
    manifest_path = cache / "MANIFEST.json"
    exists = manifest_path.exists()
    manifest = as_dict(parse_json(manifest_path.read_text("utf-8"))) if exists else {}
    raw: dict[str, Raw] = {}
    for key, template in GH_ENDPOINTS.items():
        endpoint = template.format(repo=repo)
        path = cache / f"{key}.json"
        if not path.exists():
            response = fetch(endpoint)
            text = json.dumps({"exit": response.exit, "stdout": response.stdout}, indent=1)
            path.write_text(text + "\n", encoding="utf-8")
            manifest[key] = {
                "endpoint": endpoint,
                "fetched": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        stored = as_dict(parse_json(path.read_text(encoding="utf-8")))
        exit_code = stored.get("exit")
        raw[key] = Raw(exit_code if isinstance(exit_code, int) else 1, as_str(stored.get("stdout")))
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", "utf-8")
    return raw


def _gh(endpoint: str) -> Raw:
    result = subprocess.run(
        ["gh", "api", endpoint], capture_output=True, text=True, encoding="utf-8", check=False
    )
    return Raw(result.returncode, result.stdout)


def facts_command(out: Path, *, repo: str, rev: str, cache: Path) -> None:
    raw = _cached_gh(cache, repo, _gh)
    hashes = {k: hashlib.sha256((cache / f"{k}.json").read_bytes()).hexdigest() for k in raw}
    git = git_facts(ROOT, rev=rev)
    data: Json = {
        "rev": rev,
        "git": dict[str, Json](git),
        "github": github_facts(raw),
        "github_cache_sha256": dict[str, Json](sorted(hashes.items())),
        "repo": repo,
    }
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    out.mkdir(parents=True, exist_ok=True)
    (out / "facts.json").write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- canary


def run_canary(source: Path, workdir: Path) -> dict[str, int]:
    """Exit codes of ``check.py --only golden`` in a clone of ``source`` after a golden commit.

    The clone is checked against its own HEAD before the canary commit (``GOLDEN_BASE``), as CI
    does for a push, so the result does not depend on which branches the source has.
    """
    clone = Repo.clone(source, workdir / "canary")
    head = clone.git("rev-parse", "HEAD")
    clone.write("tests/golden/canary.json", "{}\n")
    clone.commit("canary: golden file without approval")
    env = os.environ | {"GOLDEN_BASE": head}
    command = [sys.executable, str(clone.path / "scripts" / "check.py"), "--only", "golden"]

    def run() -> int:
        return subprocess.run(
            command, cwd=clone.path, env=env, capture_output=True, check=False
        ).returncode

    without = run()
    clone.git("commit", "--quiet", "--amend", "-m", "canary\n\nGolden-Approved-By: canary")
    return {"without_trailer": without, "with_trailer": run()}


def canary_command(out: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="golden-canary-") as tmp:
        result = run_canary(ROOT, Path(tmp))
    data: Json = {
        "command": "scripts/check.py --only golden (GOLDEN_BASE = HEAD before the canary commit)",
        "exit_codes": dict[str, Json](result),
        "expected": {"with_trailer": 0, "without_trailer": 1},
    }
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    out.mkdir(parents=True, exist_ok=True)
    (out / "canary.json").write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- CLI


class Options(argparse.Namespace):
    command: str = ""
    out: Path = Path()
    repo: str = ""
    rev: str = ""
    cache: Path = Path()


def parse_args(argv: list[str] | None) -> Options:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    scen = sub.add_parser("scenarios")
    scen.add_argument("--out", type=Path, required=True)
    facts = sub.add_parser("facts")
    facts.add_argument("--out", type=Path, required=True)
    facts.add_argument("--repo", required=True, help="OWNER/NAME on GitHub")
    facts.add_argument("--rev", required=True, help="history counts are taken at this revision")
    facts.add_argument("--cache", type=Path, required=True, help="raw gh api responses")
    canary = sub.add_parser("canary", help="golden commit on a clone of this repository")
    canary.add_argument("--out", type=Path, required=True)
    return parser.parse_args(argv, namespace=Options())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "scenarios":
        scenarios_command(args.out)
    elif args.command == "canary":
        canary_command(args.out)
    else:
        facts_command(args.out, repo=args.repo, rev=args.rev, cache=args.cache.expanduser())
    return 0


if __name__ == "__main__":
    sys.exit(main())
