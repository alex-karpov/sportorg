#!/usr/bin/env bash
# Re-capture the verification outputs that existed only in the session transcript.
# Runs on a clean clone of the project at the verified commit; nothing is written to the working checkout.
# Usage: verification_rerun.sh <clone> <scratch> [<legacy-checkout>]
set -u
CLONE="$1"; S="$2"; LEGACY="${3:-C:/Users/USER/Prog/Orient/_other/pysport-legacy}"
cd "$CLONE" || exit 2
step() { echo; echo "######## $*"; }
run() { echo "\$ $*"; "$@"; echo "[exit $?]"; }
check_summary() { uv run --no-sync python scripts/check.py --keep-going > "$S/check.out" 2>&1; local c=$?
  grep -E "$1" "$S/check.out"; sed -n '/== summary/,$p' "$S/check.out"; echo "[check.py exit $c]"; }

step "context"
echo "date: $(date -Iseconds) | clone: $CLONE | HEAD: $(git rev-parse HEAD)"
echo "$(uv --version) | $(git --version) | $(uname -s -r)"
git status --porcelain --untracked-files=no | grep . || echo "tracked files: clean"

step "item 2: uv sync; check.py --keep-going (full output)"
run uv sync --quiet
run uv run --no-sync python scripts/check.py --keep-going

step "item 3a: import os in core"
printf '"""Canary (a)."""\n\nimport os\n\nSEP = os.sep\n' > src/sportorg_ng/core/canary_os.py
check_summary 'BROKEN|not allowed|->|Contracts:'
rm src/sportorg_ng/core/canary_os.py

step "item 3b: function without annotations"
printf '"""Canary (b)."""\n\n\ndef add(a, b):\n    return a + b\n' > src/sportorg_ng/core/canary_untyped.py
check_summary '^ANN|error:|^Found'
rm src/sportorg_ng/core/canary_untyped.py

step "item 3c: bare type: ignore"
printf '"""Canary (c)."""\n\nx: int = "s"  # type: ignore\n' > src/sportorg_ng/core/canary_ignore.py
check_summary '^PGH|error:|^Found'
rm src/sportorg_ng/core/canary_ignore.py

step "item 3d: broken test"
printf 'def test_canary_broken() -> None:\n    assert 1 + 1 == 3\n' > tests/test_canary_broken.py
check_summary 'FAILED|failed|passed'
rm tests/test_canary_broken.py

step "item 3 extra: unused noqa, unused pyright ignore, explicit Any"
printf '"""Canary (extra)."""\n\nfrom typing import Any\n\nY: int = 1  # noqa: E501\nZ: int = 2  # pyright: ignore[reportAssignmentType]\n\n\ndef echo(value: Any) -> Any:\n    return value\n' > src/sportorg_ng/core/canary_extra.py
check_summary '^RUF100|^ANN401|reportUnnecessaryTypeIgnoreComment|reportExplicitAny|^Found'
rm src/sportorg_ng/core/canary_extra.py
git status --porcelain --untracked-files=all | grep -v '^?? .venv' | grep . || echo "after canaries: clean"

step "item 4: pre-commit with the default interpreter uvx picks (3.15 is installed on this machine)"
uvx pre-commit run --all-files > "$S/pc-default.out" 2>&1; c=$?
grep -E 'error:|Failed to build|Visual C|hint: `pyyaml`|\.{5,}' "$S/pc-default.out" | head -8; echo "[exit $c]"
step "item 4: uvx --python 3.14 pre-commit run --all-files (commit stage)"
uvx --python 3.14 pre-commit run --all-files > "$S/pc.out" 2>&1; c=$?
grep -E '\.{5,}|^- hook id|^Found [0-9]+ error' "$S/pc.out"; echo "files flagged by ruff:"
grep -E '^ *--> ' "$S/pc.out" | sed -E 's/:[0-9]+:[0-9]+$//' | sort -u; echo "[exit $c]"
step "item 4: same, pre-push stage"
uvx --python 3.14 pre-commit run --all-files --hook-stage pre-push 2>&1 | grep -E '\.{5,}'; echo "[exit ${PIPESTATUS[0]}]"
step "item 4: why check.py is green and pre-commit is red"
run uv run --no-sync ruff check scripts/typecheck_fixtures/untyped_def.py
run uv run --no-sync ruff check --force-exclude scripts/typecheck_fixtures/untyped_def.py

step "item 7c: guard hook payloads (uv run --no-project, as in .claude/settings.json)"
for f in guard_rm guard_log guard_golden_clone guard_bypass_py guard_bypass_junction; do
  echo "--- $f: $(cat "$S/$f.json")"
  uv run --no-project --python 3.14 python -m scripts.hooks.guard < "$S/$f.json"; echo "[exit $?] (no JSON above = allowed)"
done

step "item 7d: legacy_clone.py into a fresh temp destination"
D="$S/legacy-probe-rerun"; rm -rf "$D"
run uv run --no-sync python scripts/legacy_clone.py --source "$LEGACY" --dest "$D"
echo "clone HEAD: $(git -C "$D" rev-parse HEAD) | AGENTS.md: $(grep -o '[0-9a-f]\{40\}' AGENTS.md)"
rm -rf "$D"

step "item 9: vulnerabilities, licences, lock"
run uv audit
run uv run --no-sync python -m scripts.check_licenses
run uv lock --check

step "item 6: Backlog.md"
run backlog task list --plain
run backlog milestone list

step "item 5: CI run of the verified commit"
gh run view -R alex-karpov/sportorg 40093927242 --json headSha,conclusion,jobs --jq '"headSha " + .headSha + " | " + .conclusion, (.jobs[] | "  " + .conclusion + "  " + .name)'
echo "grimp in macos-latest / py3.15:"
gh run view -R alex-karpov/sportorg 40093927242 --log 2>/dev/null | grep -F 'macos-latest / py3.15' | grep -E 'Building grimp|Built grimp' | sed -E 's/^[^\t]*\t[^\t]*\t[0-9T:.Z-]+ /  /'

step "supply chain: secrets in history (gitleaks, clone mounted read-only)"
docker run --rm ghcr.io/gitleaks/gitleaks:latest version 2>&1 | tail -1
MSYS_NO_PATHCONV=1 docker run --rm -v "$CLONE:/repo:ro" ghcr.io/gitleaks/gitleaks:latest git /repo --redact --no-banner --no-color 2>&1 | tail -3
echo "[exit ${PIPESTATUS[0]}]"
