# Unstable legacy tests — agent observation

Agent judgement (Claude Code, Opus 5.5), not script output, not reviewed by a human.

Criterion: a legacy test is *unstable* if, in the same environment (same `.venv`, the hermetic
environment of `scripts/legacy_env.py`, clean copy before every run), its outcome differs between
runs. An unstable test is deselected in the evidence runs (`UNSTABLE_TESTS` in
`scripts/legacy_env.py`) so that a rerun is byte-identical. It is listed in every output under
`deselected`, and it is not counted as passed or failed.

Observations of 2026-10-31 (WSL2 Ubuntu, Claude Code sandbox). Runs of
`python -m scripts.legacy_env tests` into a scratch directory, before the deselection existed:

| Python | `QT_QPA_PLATFORM` | runs | `test_teamwork_keepalive_and_server_disconnect` failed |
|---|---|---|---|
| 3.13.17 | offscreen | 3 | 0 |
| 3.13.17 | none | 3 | 2 |
| 3.8.20 | offscreen | 4 | 0 |
| 3.8.20 | offscreen (first probe run) | 1 | the probe counted 4 failures instead of 3; the ids were not recorded then, so it is `[допущение]` that this test was the 4th |

A first evidence run with only that test deselected then saw
`tests/test_teamwork.py::test_teamwork_with_encryption` fail once without a platform: of two
identical runs, one had 4 failures, the other 3.

Decision (agent): deselect the five tests of `tests/test_teamwork.py` that start
`start_server_and_client` `[код: pysport@b548c35 tests/test_teamwork.py:40-92]`: `test_teamwork`,
`test_teamwork_keepalive_and_server_disconnect`, `test_teamwork_with_encryption`,
`test_teamwork_disconnect_on_encryption_mismatch`, `test_teamwork_race_id_mismatch_requires_confirmation`.
Two of them were seen flipping; the other three are built the same way. The sixth,
`test_teamwork_encrypted_packet_contains_nonce`, starts no server and stays in.

Why they are unstable `[код: pysport@b548c35 tests/test_teamwork.py:145-157]`: the test starts a real
server and client in threads with `keepalive_interval=0.5` and waits with `wait_until(..., timeout=8)`.
The outcome depends on scheduling, not on the program's logic. It is not related to recalculation or
to the Qt platform (it also failed once under `offscreen`, on the first 3.8 run, if the assumption
above holds).

Not unstable but environment-dependent: `tests/test_reader.py::test_huichang`, `::test_sportident`,
`::test_sportiduino` fail in every run inside the sandbox. Their fixture starts `socat` with ptys at the
fixed paths `/tmp/pty0` and `/tmp/pty1` `[код: pysport@b548c35 tests/test_reader.py:166-175]`, and the
sandbox makes `/tmp` read-only: `socat … E unlink("/tmp/pty0"): Read-only file system` (checked by
hand in this session). They stay in the evidence runs. Outside the sandbox they are expected to run
`[допущение]`; S5 (device replay) has to deal with the same limit.
