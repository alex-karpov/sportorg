"""Hand-written mutants of the guard hook; each is applied to a copy and the guard tests are run.

Usage: python mutate_guard.py <copy-root> <python-exe>
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
PY = sys.argv[2]
GUARD = "scripts/hooks/guard.py"
COMMON = "scripts/hooks/_common.py"

MUTANTS = [
    ("drop rm", GUARD, "rm|rmdir|", "rmdir|"),
    ("drop cd", GUARD, "r\"cd|Set-Location", "r\"Set-Location"),
    ("drop > / >> redirection", GUARD, r")\b|>>?", r")\b"),
    ("drop sed -i", GUARD, r"sed\s+-i|", ""),
    ("drop git checkout", GUARD, "(checkout|switch|", "(switch|"),
    ("drop uv sync", GUARD, r"uv\s+(sync|add|", r"uv\s+(add|"),
    ("drop Set-Content", GUARD, "New-Item|Set-Content|", "New-Item|"),
    ("drop Remove-Item", GUARD, "|Remove-Item|", "|"),
    ("verb only at line start", GUARD, "(^|[\\s;&|(`])(", "(^)("),
    ("NotebookEdit not a file tool", GUARD, '"MultiEdit", "NotebookEdit"', '"MultiEdit"'),
    ("MultiEdit not a file tool", GUARD, '"Write", "MultiEdit",', '"Write",'),
    ("PowerShell not a shell tool", GUARD, '{"Bash", "PowerShell"}', '{"Bash"}'),
    ("ignore notebook_path", GUARD, ' or as_str(tool_input.get("notebook_path"))', ""),
    ("golden: no ask", GUARD, 'return Decision("ask", reason)', "return None"),
    ("file tools: no legacy deny", GUARD, "        if is_legacy(path):", "        if False:"),
    ("shell: and -> or", GUARD, "is_legacy(command) and MUTATING", "is_legacy(command) or MUTATING"),
    ("main prints nothing", GUARD, "        print(decision.to_json())", "        pass"),
    ("main exits 1 on decision", GUARD, "        print(decision.to_json())\n    return 0", "        print(decision.to_json())\n        return 1\n    return 0"),
    ("decision always deny in JSON", GUARD, '"permissionDecision": self.permission', '"permissionDecision": "deny"'),
    ("normalize keeps backslashes", COMMON, 'return path.replace("\\\\", "/")', "return path"),
    ("malformed payload raises", COMMON, "    except ValueError:\n        return {}", "    except ValueError:\n        raise"),
]


def run_tests() -> tuple[int, str]:
    # -B and no __pycache__: a mutant of the same size written within the same second as the
    # previous one would otherwise be served from the previous mutant's stale .pyc.
    for cache in ROOT.rglob("__pycache__"):
        for pyc in cache.glob("*.pyc"):
            pyc.unlink()
    proc = subprocess.run(
        [PY, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/scripts/test_guard.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    tail = (proc.stdout.strip().splitlines() or ["?"])[-1]
    return proc.returncode, tail


def main() -> int:
    probe = subprocess.run(
        [PY, "-c", "import scripts.hooks.guard as g; print(g.__file__)"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"guard module under test: {probe}")
    code, tail = run_tests()
    print(f"baseline: exit {code} | {tail}")
    killed = 0
    for name, rel, old, new in MUTANTS:
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        if original.count(old) != 1:
            print(f"SKIP  {name}: pattern found {original.count(old)} times")
            continue
        path.write_text(original.replace(old, new), encoding="utf-8")
        try:
            code, tail = run_tests()
        finally:
            path.write_text(original, encoding="utf-8")
        verdict = "killed" if code else "SURVIVED"
        killed += bool(code)
        print(f"{verdict:<8} {name:<32} | {tail}")
    print(f"killed {killed}/{len(MUTANTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
