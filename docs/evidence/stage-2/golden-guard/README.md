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
- The raw `gh api` responses of 2026-10-31 are in `~/.cache/sportorg-stage2/github/` with `MANIFEST.json`
  (fetch time and SHA-256 per response). They were first written to the session scratchpad, because the
  sandbox did not yet allow that path, and copied there unchanged after the maintainer allowed it the same
  day. The rerun from that cache reproduces `facts.json` byte for byte. On a machine without the cache the
  command fetches them again, and `facts.json` then changes if the GitHub settings have changed.
- CI ran the new step on all seven jobs of run 41222366113 (`stage-2@dab1040`, 2026-10-31): `ok` everywhere,
  329 tests including the canary passed (ADR-0008, Decision).
