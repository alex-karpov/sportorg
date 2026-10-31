# Golden-file protection (TASK-8 AC #7, ADR-0008)

Every file here is script output; the commands are in `commands.txt`.

| File | What it shows |
|---|---|
| `scenarios.md`, `scenarios.json` | 9 scenarios × 3 mechanisms: (a) trailer check `scripts/golden_guard.py`, (c1) signed manifest with signers in the repository, (c2) signed manifest with the signer pinned outside it. `detected` = the check fails |
| `canary.json` | `scripts/check.py --only golden` on a clone of this repository: exit 1 for a golden commit without `Golden-Approved-By:`, exit 0 with it |
| `facts.json` | history counts at `aeb6cb7` (commits, signed, agent co-authored, distinct authors — counts only) and GitHub settings (visibility, collaborators, rulesets, protection of `main`), with the SHA-256 of each cached raw response |

Notes:
- The (c) columns are a prototype written for the measurement, not product code. They need `ssh-keygen -Y`;
  without it they read `unavailable`. Measured with OpenSSH 10.2p1 (WSL2 Ubuntu). Windows and macOS
  were not measured.
- Session S1 (2026-10-31): the sandbox did not allow writing to `~/.cache/sportorg-stage2/`, and running
  outside it was refused, so the raw `gh api` responses of this run are in the session scratchpad. They are
  not kept after the session. The SHA-256 values in `facts.json` identify them. A rerun with the
  `commands.txt` path fetches them again, and `facts.json` changes only if the GitHub settings have changed.
- CI has not run the new step yet (nothing pushed in S1).
