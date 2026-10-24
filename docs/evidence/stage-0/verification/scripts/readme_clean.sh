#!/bin/bash
# README steps on a clean ubuntu:24.04, one interactive-like shell, no set -e: every exit code is recorded.
cd ~
step() { echo; echo "######## $*"; }

step "README step 1 (verbatim): curl -LsSf https://astral.sh/uv/install.sh | sh"
curl -LsSf https://astral.sh/uv/install.sh | sh; echo "[exit ${PIPESTATUS[0]}/${PIPESTATUS[1]}]"

step "Not in README: prerequisites of a bare image (git, curl, CA certs)"
apt-get update -qq >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends git curl ca-certificates >/dev/null; echo "[exit $?]"

step "README step 1 (verbatim, retry after prerequisites)"
curl -LsSf https://astral.sh/uv/install.sh | sh; echo "[exit ${PIPESTATUS[0]}/${PIPESTATUS[1]}]"

step "README step 2 (with --branch stage-0 as the verifier was told): git clone ... && cd sportorg"
git clone --branch stage-0 https://github.com/alex-karpov/sportorg.git && cd sportorg; echo "[exit $?] pwd=$(pwd) head=$(git rev-parse HEAD 2>/dev/null)"

step "README step 3 (verbatim, same shell): uv sync"
uv sync; echo "[exit $?]"

step "Same shell after sourcing the env file the uv installer names"
. "$HOME/.local/bin/env"; echo "uv=$(command -v uv) $(uv --version)"

step "README step 3 (verbatim): uv sync"
uv sync; echo "[exit $?]"

step "README step 4 (verbatim): uv run python scripts/check.py"
uv run python scripts/check.py; echo "[exit $?]"

step "README step 5 (verbatim, optional): uvx pre-commit install"
uvx pre-commit install; echo "[exit $?]"
uv python list --only-installed
