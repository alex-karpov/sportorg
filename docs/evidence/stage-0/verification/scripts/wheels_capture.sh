#!/usr/bin/env bash
# Independent check of ADR-0001 with uv's resolver (wheels only), plus the two findings it produced.
# Usage: wheels_capture.sh <tools-dir> <workdir> <project-clone>
set -u
T="$1"; W="$2"; P="$3"
mkdir -p "$W"
echo "# $(date -Iseconds) | $(uv --version)"
echo; echo "######## per package, with dependencies: uv pip compile --only-binary :all: (23 packages x {3.14,3.15} x 3 platforms)"
bash "$T/wheels_matrix.sh" "$W" > "$W/raw.txt"
echo "ok: $(grep -c ' ok$' "$W/raw.txt") of $(wc -l < "$W/raw.txt")"; grep FAIL "$W/raw.txt"
echo; echo "######## the project's own lock (uv export --frozen --all-groups), wheels only"
(cd "$P" && uv export --frozen --no-hashes --all-groups --no-emit-project --quiet) > "$W/project-req.txt"
echo "pins: $(grep -c '==' "$W/project-req.txt")"
for v in 3.14 3.15; do for t in x86_64-pc-windows-msvc x86_64-manylinux_2_28 aarch64-apple-darwin; do
  printf '%s %-24s ' "$v" "$t"
  if out=$(cd "$W" && uv pip compile project-req.txt --no-config --only-binary :all: --python-version "$v" --python-platform "$t" --no-header --quiet 2>&1); then echo ok; else echo "FAIL: $(echo "$out" | grep -m1 'cause:\|Because' | sed 's/^ *//')"; fi
done; done
echo; echo "######## grimp 3.17 files on PyPI for macOS and cp315"
curl -s https://pypi.org/pypi/grimp/3.17/json | uv run --no-project python -c "import json,sys; d=json.load(sys.stdin); [print(' ', u['filename']) for u in d['urls'] if 'macosx' in u['filename'] and ('cp314' in u['filename'] or 'cp315' in u['filename'])]"
echo; echo "######## orjson cp315 Linux x86_64 wheels on PyPI, and resolution per glibc floor"
curl -s https://pypi.org/pypi/orjson/json | uv run --no-project python -c "import json,sys; d=json.load(sys.stdin); print('  latest', d['info']['version']); [print(' ', u['filename']) for u in d['urls'] if 'cp315' in u['filename'] and 'linux' in u['filename'] and 'x86_64' in u['filename']]"
for t in x86_64-manylinux_2_28 x86_64-manylinux_2_34 x86_64-manylinux_2_40; do
  printf '  %-24s ' "$t"; (cd "$W" && echo orjson | uv pip compile - --no-config --only-binary :all: --python-version 3.15 --python-platform "$t" --no-header --quiet >/dev/null 2>&1) && echo ok || echo FAIL
done
