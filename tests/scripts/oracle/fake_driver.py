"""Stand-in for scripts/oracle_driver/driver.py in the unit tests of scripts/oracle_cli.py.

Runs under the project interpreter. The "race file" holds the behaviour: ``{"crash": ...}`` prints
personal-looking text to stderr and exits 1; ``{"raise": ...}`` raises inside ``snapshot.guarded``;
anything else is copied to RAW_OUT as the driver payload.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts._json import as_dict, parse_json
from scripts.oracle_driver import snapshot


def main(argv: list[str]) -> int:
    race_file, raw_out = argv[0], argv[1]
    payload = as_dict(parse_json(Path(race_file).read_text(encoding="utf-8")))
    if "crash" in payload:
        sys.stderr.write("Traceback: Ivanov Ivan 8001234\n")
        return 1
    if "raise" in payload:

        def work() -> dict[str, object]:
            msg = "Ivanov Ivan 8001234"
            raise KeyError(msg)

        return snapshot.guarded(raw_out, work)
    meta = as_dict(payload.get("meta"))
    meta["now_arg"] = argv[argv.index("--now") + 1] if "--now" in argv else None
    payload["meta"] = meta
    Path(raw_out).write_text(
        json.dumps({"protocol": snapshot.PROTOCOL, **payload}), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
