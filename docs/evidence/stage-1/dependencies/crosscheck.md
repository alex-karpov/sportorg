# Cross-check of vulnerability sources: pysport@b548c35

Produced by `scripts/archaeology/dependencies.py` (command in `commands.txt`). Sources:
- `uv.lock`, `pyproject.toml`, `Cargo.lock` of pysport@b548c35, read through git.
- PyPI JSON cache `pypi/`: 123 files, combined SHA-256 `e9b1748f101858e955c478cbca6dfaa0a2c539fe9b0c3a502817c7993d60df5e` (per-file values in `summary.json`).
- OSV query cache `osv/`: 137 files, combined SHA-256 `bcb3e2bb59deee80aba743695999f08c84f14d977553d74287c68cfcc074690c` (per-file values in `summary.json`).
- crates.io JSON cache `crates/`: 14 files, combined SHA-256 `7e2071bea42e7e76a4a8c7eb75c08b04013065a548fc8b99598ed4d5234446a7` (per-file values in `summary.json`).
- `tools/uv-audit-legacy.json`: SHA-256 `838867634555d674066ca1fd387317fc84cbf3e0c0ea6dbbe346ee44e6d13c48`.
- `tools/osv-scanner-legacy.json`: SHA-256 `af422970dc30e04aa2c84f8654cff385d9a3062dd9fdeb4d964b1621f7cb26dd`.

| comparison | both | only own | only other |
|---|---|---|---|
| own vs osv-scanner (Cargo.lock) | 4 | 0 | 0 |
| own vs osv-scanner (uv.lock) | 227 | 0 | 0 |
| own vs uv audit (Python) | 227 | 0 | 0 |

## own vs osv-scanner (Cargo.lock): records present on one side only (0)

None.

## own vs osv-scanner (uv.lock): records present on one side only (0)

None.

## own vs uv audit (Python): records present on one side only (0)

None.
