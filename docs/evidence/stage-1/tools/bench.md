# Tool candidates: measurements on pysport@b548c35

Produced by `scripts/archaeology/tool_runs.py` (command in `commands.txt`). Wall times are in `timings.json` (not deterministic). Versions: ast-grep-cli 0.51.0, deadcode 2.4.1, lizard 1.24.3, pydriller 2.12, radon 6.0.1, skylos 5.0.0, vulture 2.16; ruff and grimp from `uv.lock`.

## N1

```json
{
 "exit": {
  "lizard": 0,
  "radon": 0,
  "ruff": 1
 },
 "functions": {
  "lizard": 1967,
  "radon": 1961,
  "ruff": 1973
 },
 "ruff_vs_lizard": {
  "common_functions": 1967,
  "equal_complexity": 1513,
  "only_other": 0,
  "only_ruff": 6,
  "spearman": 0.898
 },
 "ruff_vs_radon": {
  "common_functions": 1961,
  "equal_complexity": 1511,
  "only_other": 0,
  "only_ruff": 12,
  "spearman": 0.8986
 }
}
```

## N2

```json
{
 "edges": {
  "grimp": 588,
  "own": 603
 },
 "only_grimp_first": [],
 "only_own_first": [
  "sportorg.gui.menu.actions -> sportorg.modules.recovery.recovery_orgeo_finish_csv",
  "sportorg.gui.menu.actions -> sportorg.modules.recovery.recovery_si_master_csv",
  "sportorg.gui.menu.actions -> sportorg.modules.recovery.recovery_sportorg_html",
  "sportorg.gui.menu.actions -> sportorg.modules.recovery.recovery_sportorg_si_log",
  "sportorg.modules.recovery.recovery_orgeo_finish_csv -> sportorg.models.memory",
  "sportorg.modules.recovery.recovery_orgeo_finish_csv -> sportorg.utils.time",
  "sportorg.modules.recovery.recovery_si_master_csv -> sportorg.common.otime",
  "sportorg.modules.recovery.recovery_si_master_csv -> sportorg.models.memory",
  "sportorg.modules.recovery.recovery_si_master_csv -> sportorg.modules.sportident.fix_time_sicard_5",
  "sportorg.modules.recovery.recovery_si_master_csv -> sportorg.utils.time",
  "sportorg.modules.recovery.recovery_sportorg_html -> sportorg.utils.text",
  "sportorg.modules.recovery.recovery_sportorg_si_log -> sportorg.common.otime",
  "sportorg.modules.recovery.recovery_sportorg_si_log -> sportorg.models.memory",
  "sportorg.modules.recovery.recovery_sportorg_si_log -> sportorg.modules.sportident.fix_time_sicard_5",
  "sportorg.modules.recovery.recovery_sportorg_si_log -> sportorg.utils.time"
 ],
 "own_vs_grimp": {
  "both": 588,
  "jaccard": 0.9751,
  "only_a": 15,
  "only_b": 0
 }
}
```

## N3

```json
{
 "deadcode": {
  "exit": 1,
  "stderr_tail": "AttributeError: module 'ast' has no attribute 'Str'"
 },
 "skylos": {
  "exit": 1,
  "stderr_tail": "ERROR    Error during analysis: [Errno 1] Operation not permitted"
 },
 "vulture": {
  "by_kind": {
   "redundant if-condition": 2,
   "unreachable code": 1,
   "unused attribute": 41,
   "unused class": 92,
   "unused function": 12,
   "unused method": 81,
   "unused property": 3,
   "unused variable": 50
  },
  "exit": 3,
  "findings": 282
 }
}
```

## N6

```json
{
 "commits": {
  "own": 1340,
  "pydriller": 1340
 },
 "merges": {
  "own": 198,
  "pydriller": 198
 },
 "pydriller_exit": 0,
 "tracked_files": 324,
 "tracked_files_with_equal_change_count": 323
}
```

## N8

```json
{
 "ast_grep_exit": 0,
 "hits": {
  "ast_grep": 7,
  "git_grep": 7
 },
 "only_git_grep": [],
 "overlap": {
  "both": 7,
  "jaccard": 1.0,
  "only_a": 0,
  "only_b": 0
 },
 "pattern": "sys.platform"
}
```
