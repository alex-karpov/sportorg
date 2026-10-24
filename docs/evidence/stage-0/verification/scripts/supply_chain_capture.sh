#!/usr/bin/env bash
# Lock-file canary through the real git pre-commit hook, and how CI action/image refs are pinned.
# Usage: supply_chain_capture.sh <clone with `uv sync` done and `uvx --python 3.14 pre-commit install` done>
set -u
P="$1"
cd "$P" || exit 2
echo "# $(date -Iseconds) | clone $(git rev-parse --short HEAD) | hooks: $(ls .git/hooks | grep -v sample | tr '\n' ' ')"

echo; echo '######## canary: add a dependency to pyproject.toml without `uv lock`, then git commit'
sed -i 's/^dependencies = \[\]$/dependencies = ["requests>=2"]/' pyproject.toml
git diff --stat
git -c user.name=verifier -c user.email=verifier@example.invalid commit -qam "canary: dependency without lock update" 2>&1 | grep -vE '^\s*$'
echo "[commit exit ${PIPESTATUS[0]}] HEAD after: $(git log --oneline -1)"
echo "--- what CI runs (uv sync --locked):"
uv sync --locked 2>&1 | tail -2; echo "[exit ${PIPESTATUS[0]}]"
git checkout -q -- pyproject.toml && git status --porcelain --untracked-files=no | grep . || echo "reverted: tracked files clean"

echo; echo "######## refs in CI and devcontainer"
grep -nE 'uses:|curl .*sh|container:' .github/workflows/ci.yml
grep -nE 'FROM|COPY --from' .devcontainer/Dockerfile
for ref in "actions/checkout v5" "astral-sh/setup-uv v10.3.2" "astral-sh/setup-uv v10"; do
  set -- $ref; printf '%-22s %-8s ' "$1" "$2"
  gh api "repos/$1/git/ref/tags/$2" --jq '.object.type + " " + .object.sha' 2>&1 | head -1
done
gh api repos/astral-sh/setup-uv/releases/latest --jq '"setup-uv latest release: " + .tag_name + " " + .published_at'
echo "uv.lock: $(grep -c '^\[\[package\]\]' uv.lock) packages, $(grep -c 'hash = "sha256:' uv.lock) sha256 hashes"
