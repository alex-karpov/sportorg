#!/usr/bin/env bash
# ADR-0003 partial rerun inside WSL: bench_env.sh on an ext4 clone and on a dedicated /mnt/c copy.
# Usage (from Windows): wsl -d Ubuntu --cd '~' -- bash <this file> <scratch-v2-dir-as-/mnt/c-path>
set -u
export PATH="$HOME/.local/bin:$PATH"
V2="${1:?scratch v2 dir}"
EXT4="$HOME/verify-envb-ext4"
echo "# uv $(uv --version) | $(. /etc/os-release; echo "$PRETTY_NAME") | $(nproc) CPUs"
if [ ! -d "$EXT4" ]; then
  git -c safe.directory='*' clone -q "$V2/proj" "$EXT4" || exit 3
fi
echo "# ext4 clone: $EXT4 at $(git -C "$EXT4" rev-parse --short HEAD) fs=$(stat -f -c %T "$EXT4")"
echo "# 9p copy:    $V2/envb-9p fs=$(stat -f -c %T "$V2/envb-9p")"
bash "$EXT4/scripts/bench_env.sh" wsl-ext4 "$EXT4"
bash "$EXT4/scripts/bench_env.sh" wsl-9p "$V2/envb-9p"
