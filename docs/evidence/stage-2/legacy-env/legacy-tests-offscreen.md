# Legacy tests: legacy-tests-offscreen

Python 3.8.20, `QT_QPA_PLATFORM` = offscreen, no `DISPLAY`/`WAYLAND_DISPLAY`. Translation setup exit 0, pytest exit 1, crashed: False.

- all tests: error 0, failed 3, passed 282, skipped 10, total 295
- recalculation tests (`tests/test_relay_results.py`, `tests/test_result_calculation.py`): error 0, failed 0, passed 40, skipped 8, total 48

Not passed:
- `tests.test_reader::test_huichang: failed`
- `tests.test_reader::test_sportident: failed`
- `tests.test_reader::test_sportiduino: failed`
- `tests.test_relay_results.TestRelayResults::test_14_full_team_with_less_legs_before_dsq: skipped`
- `tests.test_relay_results.TestRelayResults::test_15_incomplete_dsq_team_with_better_result: skipped`
- `tests.test_relay_results.TestRelayResults::test_16_full_dsq_team_same_completed_legs_worse_result: skipped`
- `tests.test_relay_results.TestRelayResults::test_18_not_started_team: skipped`
- `tests.test_relay_results.TestRelayResultsBestTeamPlacing::test_14_full_team_with_less_legs_before_dsq: skipped`
- `tests.test_relay_results.TestRelayResultsBestTeamPlacing::test_15_incomplete_dsq_team_with_better_result: skipped`
- `tests.test_relay_results.TestRelayResultsBestTeamPlacing::test_16_full_dsq_team_same_completed_legs_worse_result: skipped`
- `tests.test_relay_results.TestRelayResultsBestTeamPlacing::test_18_not_started_team: skipped`
- `tests.test_theme::test_detect_system_theme_windows_registry_light: skipped`
- `tests.test_wdb::test_WDB_read_file: skipped`
