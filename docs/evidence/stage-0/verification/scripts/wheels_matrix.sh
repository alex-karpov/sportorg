#!/usr/bin/env bash
# Can uv resolve each package (with its dependencies) from wheels only, per Python version and platform?
# Usage: wheels_matrix.sh <workdir>
set -u
cd "$1" || exit 2
pkgs="PySide6 PyQt6 cryptography orjson msgspec pydantic lxml psutil pytest hypothesis ruff mypy basedpyright ty pyrefly import-linter cx_Freeze pyinstaller briefcase pre-commit pyyaml hidapi nuitka"
plats="x86_64-pc-windows-msvc x86_64-manylinux_2_28 aarch64-apple-darwin"
one() { # pkg py plat -> "pkg py plat ok|FAIL reason"
  local out
  if out=$(echo "$1" | uv pip compile - --no-config --only-binary :all: --python-version "$2" --python-platform "$3" --no-header --no-annotate --quiet 2>&1); then
    echo "$1 $2 $3 ok"
  else
    echo "$1 $2 $3 FAIL $(echo "$out" | grep -m1 -oE "no (wheels|source distribution|version)[^.]*|Because [^,]*" | head -c 110)"
  fi
}
export -f one
for p in $pkgs; do for v in 3.14 3.15; do for t in $plats; do echo "$p $v $t"; done; done; done |
  xargs -P 8 -n 3 bash -c 'one "$0" "$1" "$2"' | sort
