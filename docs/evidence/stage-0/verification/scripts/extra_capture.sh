#!/usr/bin/env bash
# Remaining verification facts that existed only in the transcript, re-captured on the clean clone.
# Usage: extra_capture.sh <clone> <scratch>
set -u
C="$1"; S="$2"
cd "$C" || exit 2
echo "# $(date -Iseconds) | clone HEAD $(git rev-parse HEAD)"

echo; echo "######## rule 8: personal data in tracked files"
echo "--- e-mail addresses (excluding noreply/anthropic/example and decorators):"
git grep -nIoE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' | grep -vE 'noreply@|@anthropic\.com|example\.(org|com|invalid)|@pytest|@v[0-9]|@[0-9]' || echo "  none"
echo "--- Cyrillic first name + surname pairs outside docs/brief.md:"
git grep -nIP '\b[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+(ов|ев|ин|ын|ий|ая|ова|ева|ина|ская|ский)\b' -- ':!docs/brief.md' || echo "  none"
echo "--- 7-8 digit numbers (card-number shaped) in docs/evidence and evals:"
git grep -nIoP '(?<![\w.:/-])\d{7,8}(?![\w.-])' -- docs/evidence evals || echo "  none"
echo "--- race data files committed:"
git ls-files | grep -E '\.(sportorg|csv|xlsx?|xml|db|sqlite)$' || echo "  none"
echo "--- tracked files containing the maintainer's absolute home path (any separator):"
git grep -lI -iE 'Users[/\\]+<name>' | wc -l

echo; echo "######## licence check heuristics (scripts/check_licenses.py verdict())"
uv run --no-sync python -c "from scripts.check_licenses import verdict as v; [print(f'  {l!r:28} -> {v(\"x\", l)}') for l in ['GPL-2.0-only','GPL-2.0-or-later','Limited use license','SSPL-1.0','BUSL-1.1','CC-BY-NC-4.0','EUPL-1.2']]"
echo "--- installed packages vs packages the licence check sees:"
uv pip list --format freeze 2>/dev/null | cut -d= -f1 | tr 'A-Z_' 'a-z-' | tr -d '\r' | sort > "$S/installed.txt"
uv run --no-sync python -m scripts.check_licenses --json 2>/dev/null | uv run --no-sync python -c "import json,sys; t=sys.stdin.read(); rows=json.loads(t[:t.rindex(']')+1]); print('\n'.join(sorted(r['Name'].lower().replace('_','-') for r in rows)))" | tr -d '\r' > "$S/checked.txt"
echo "  installed: $(wc -l < "$S/installed.txt") | checked: $(wc -l < "$S/checked.txt") | not checked (besides the project): $(comm -23 "$S/installed.txt" "$S/checked.txt" | grep -v '^sportorg-ng$' | tr '\n' ' ')"

echo; echo "######## guard hook vs the project venv (uv run --no-project --python 3.14, as in .claude/settings.json)"
echo "--- healthy .venv in the clone:"
uv run --no-project --python 3.14 python -c "import sys; import scripts.hooks.guard; print('  prefix:', sys.prefix); print('  non-stdlib modules:', sorted({m.split('.')[0] for m in sys.modules} - set(sys.stdlib_module_names) - set(sys.builtin_module_names)))"
B="$S/guard-brokenvenv-rerun"; rm -rf "$B"; mkdir -p "$B/.venv/Scripts" "$B/.venv/bin" "$B/.venv/lib64"; cp -r "$C/scripts" "$B/"
printf 'home = /usr/bin\nversion_info = 3.14.0\ninclude-system-site-packages = false\n' > "$B/.venv/pyvenv.cfg"; printf '#!/bin/sh\n' > "$B/.venv/bin/python"
for variant in broken absent; do
  [ "$variant" = absent ] && rm -rf "$B/.venv"
  echo "--- $variant .venv:"
  (cd "$B" && uv run --no-project --python 3.14 python -c "import sys; print('  prefix:', sys.prefix)" && uv run --no-project --python 3.14 python -m scripts.hooks.guard < "$S/guard_rm.json"; echo "  [exit $?]")
done
rm -rf "$B"
