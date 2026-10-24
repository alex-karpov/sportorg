"""Apply one guard mutant to a copy, show the regex line and which tests fail, then restore.

Usage: python mutant_detail.py <copy-root> <python-exe> <old> <new>
"""

import subprocess
import sys
from pathlib import Path

root, py, old, new = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
guard = root / "scripts" / "hooks" / "guard.py"
data = guard.read_bytes()
print(f"pattern {old!r}: {data.count(old.encode())} occurrence(s); CRLF in file: {b'\r\n' in data}")
guard.write_bytes(data.replace(old.encode(), new.encode()))
try:
    line = next(ln for ln in guard.read_text().splitlines() if "Set-Location" in ln)
    print(f"mutated line: {line.strip()}")
    out = subprocess.run(
        [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf", "tests/scripts/test_guard.py"],
        cwd=root, capture_output=True, text=True, check=False,
    ).stdout
    print("\n".join(ln for ln in out.splitlines() if ln.startswith(("FAILED", "ERROR")) or "passed" in ln))
finally:
    guard.write_bytes(data)
