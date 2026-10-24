# Stage 0 evidence

Tool outputs and the commands behind them, referenced from the ADRs and `docs/reports/stage-0.md`.
`verification/` holds the outputs of the independent check of 2026-10-24
(`docs/reports/stage-0-verification.md`); `legacy-layout/` those of ADR-0006.

## Recorded paths: the username is replaced with `USER`
On 2026-10-25, by the maintainer's decision, the local username in recorded paths was replaced with
`USER` in every file under `docs/`: 4612 occurrences in 37 files (35 here, ADR-0006 and the stage
report); one of them, followed by `;`, was replaced by hand. Forms: `C:\Users\USER\…` (any case,
`\`, `\\` or `/`), `/c/Users/USER/…`, `/mnt/c/Users/USER`, `/home/USER`, and
the Claude Code project directory name `C--Users-USER-…`. Regular expressions, with `<name>` standing
for the username, applied to the raw bytes of each file (two Windows console outputs in
`legacy-layout/` are not UTF-8 and stay as they were):

```
(?i)(users)([\\/]+)<name>(?=[\\/])   ->  \1\2USER
Users-<name>-                        ->  Users-USER-
/home/<name>(?![\w-])                ->  /home/USER
```

Nothing else changed: counts, timings, messages and line widths are as the tools printed them, apart
from the shorter username. The independent round-2 check found two occurrences outside paths, replaced
the same day: the ACE owner in `legacy-layout/probe-fsmode-windows.md` (`USER`) and the pattern in
`verification/scripts/extra_capture.sh` (`<name>`). Path-dependent scripts in `verification/scripts/` need the real path to run
again. The commits up to `9597b15` keep the original paths; the maintainer accepted that instead of
rewriting the public history (`docs/reports/stage-0.md`, question 3 of 2026-10-24).
