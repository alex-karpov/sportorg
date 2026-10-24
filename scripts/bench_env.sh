#!/usr/bin/env bash
# Usage: bench_env.sh <env-label> <repo-path>
# Measures uv sync (cold/warm) and pytest/ruff/basedpyright wall times; prints a Markdown row.
set -u
label="${1:?env label}"; repo="${2:?repo path}"
cd "$repo" || exit 2
now() { date +%s.%N; }
elapsed() { awk -v a="$1" -v b="$2" 'BEGIN{printf "%.2f", b-a}'; }
timeit() { # prints seconds; command output goes to stderr
  echo "+ $*" >&2
  local s e; s=$(now); "$@" >&2; e=$(now); elapsed "$s" "$e"
}
median3() { printf '%s\n' "$@" | sort -n | sed -n 2p; }
runs3() { local r=(); for _ in 1 2 3; do r+=("$(timeit "$@")"); done; echo "runs: ${r[*]}" >&2; median3 "${r[@]}"; }

echo "# uv: $(uv --version)" >&2
rm -rf .venv
a=$(timeit uv sync --no-cache --python 3.14)
b=$(timeit uv sync)
c=$(runs3 uv run --no-sync pytest -q)
d=$(runs3 uv run --no-sync ruff check src tests)
e=$(runs3 uv run --no-sync basedpyright src tests)

fs=$(df -T "$repo" 2>/dev/null | awk 'NR>1{print $2}' | tail -1)
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) fs=${fs:-ntfs}; [ "$fs" = "-" ] && fs=ntfs;; esac
[ -z "$fs" ] && fs=$(awk -v p="$repo" '$2==p{print $3}' /proc/mounts | tail -1)
[ -z "$fs" ] && fs=unknown
echo "| $label | $(uname -s) $(uname -r) | $fs | $a | $b | $c | $d | $e |"
