# Type checker measurements (stage 0)

Machine: Windows-11-10.0.26300-SP0, 12 CPUs, benchmark script on Python 3.14.8, uv: uv 0.13.1 (62faed335 2026-10-13 x86_64-pc-windows-msvc), date 2026-10-24.
Legacy corpus: `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg` (read-only), runs per measurement: 3.

## 1. Metadata (PyPI)

| tool | version | latest on PyPI at run | released | license | wheel Windows | wheel Linux x86_64 | wheel macOS arm64 | sdist |
|---|---|---|---|---|---|---|---|---|
| mypy | 2.4.0 | 2.4.0 | 2026-10-01 | MIT | yes (platform wheel) | yes (platform wheel) | yes (platform wheel) | yes |
| pyright | 1.1.414 | 1.1.414 | 2026-09-10 | MIT | yes (any wheel) | yes (any wheel) | yes (any wheel) | yes |
| basedpyright | 1.40.2 | 1.40.2 | 2026-10-04 | MIT License | yes (any wheel) | yes (any wheel) | yes (any wheel) | yes |
| ty | 0.0.91 | 0.0.91 | 2026-10-22 | MIT License | yes (platform wheel) | yes (platform wheel) | yes (platform wheel) | yes |
| pyrefly | 1.4.0 | 1.4.0 | 2026-10-15 | MIT License | yes (platform wheel) | yes (platform wheel) | yes (platform wheel) | yes |
| zuban | 0.10.1 | 0.10.1 | 2026-10-11 | AGPL-3.0-only | yes (platform wheel) | yes (platform wheel) | yes (platform wheel) | no |

Reported versions (`--version`): mypy: `mypy 2.4.0 (compiled: yes)`; pyright: `pyright 1.1.414`; basedpyright: `basedpyright 1.40.2
based on pyright 1.1.414`; ty: `ty 0.0.91 (67fbd2874 2026-10-22)`; pyrefly: `pyrefly 1.4.0`; zuban: `zuban 0.10.1`

## 2. Fixture matrix (strict config; ✓ = at least one diagnostic attributed to the file, ✗ = silent)

| fixture | mypy | pyright | basedpyright | ty | pyrefly | zuban |
|---|---|---|---|---|---|---|
| any_leak_untyped_call.py | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| assert_isinstance_evasion.py | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| explicit_any_param.py | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| implicit_optional.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| missing_import.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| object_dot_getattr.py | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| pyright_ignore_unused.py | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| real_bug_missing_return.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| real_bug_optional_attr.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| real_bug_str_plus_int.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| redundant_cast.py | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| type_ignore_without_code.py | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| typeddict_wrong_key.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| unreachable_code.py | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| untyped_def.py | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| unused_type_ignore.py | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| wrong_cast.py | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ |
| control_clean false positive | clean | clean | clean | clean | clean | clean |
| total diagnostics (exit code) | 19 (exit 1) | 19 (exit 1) | 31 (exit 1) | 10 (exit 1) | 18 (exit 1) | 18 (exit 1) |
| diagnostics not attributed to a fixture | 0 | 0 | 0 | 0 | 0 | 0 |

## 3. Timing (seconds, wall clock via `time.perf_counter`, includes `uvx` launcher overhead)

| tool | uvx --version overhead | fixtures run (median) | single file (median) | legacy cold | legacy warm (min of rest) | legacy error count | legacy tool-reported | legacy exit | notes |
|---|---|---|---|---|---|---|---|---|---|
| mypy | 0.38 | 1.02 | 1.32 | 3.17 | 2.69 | 482 | {"errors": 481, "files_with_errors": 1, "files_checked": 177} | 1,1,1 |  |
| pyright | 1.16 | 1.59 | 1.07 | 5.75 | 5.63 | 1327 | {"errors": 1327, "warnings": 35, "files_checked": 177, "tool_seconds": 4.976} | 1,1,1 | legacy output truncated to 2000 lines in evidence file |
| basedpyright | 0.39 | 0.95 | 1.04 | 7.02 | 5.95 | 1505 | {"errors": 1505, "warnings": 25513, "files_checked": 177, "tool_seconds": 5.984} | 1,1,1 | legacy output truncated to 2000 lines in evidence file |
| ty | 0.06 | 0.12 | 0.12 | 0.40 | 0.32 | 1247 | {"errors": 1276} | 1,1,1 |  |
| pyrefly | 0.06 | 0.39 | 0.42 | 0.57 | 0.53 | 2912 | {} | 1,1,1 | legacy output truncated to 2000 lines in evidence file |
| zuban | 0.06 | 0.09 | 0.13 | 1.69 | 0.42 | 1679 | {"errors": 1678, "files_with_errors": 131, "files_checked": 177} | 1,1,1 |  |

Error count = lines matching `error` (case-insensitive) in the first legacy run; for pyright/basedpyright it is `summary.errorCount` from `--outputjson`. ty is run with `--output-format concise` and pyrefly with `--output-format min-text` on the legacy corpus so that lines map ~1:1 to diagnostics. Per-run times: mypy: legacy [3.2, 2.7, 2.7]; pyright: legacy [5.7, 5.6, 5.7]; basedpyright: legacy [7.0, 5.9, 6.1]; ty: legacy [0.4, 0.3, 0.3]; pyrefly: legacy [0.6, 0.5, 0.5]; zuban: legacy [1.7, 0.4, 0.4]

## 4. Exact command lines

### mypy
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\mypy`): `uvx --python 3.14 --from mypy==2.4.0 mypy --config-file C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\mypy\mypy.ini --no-incremental --cache-dir C:\Users\USER\AppData\Local\Temp\tc_mypy_fbepidn_\mypy_cache C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from mypy==2.4.0 mypy --no-incremental --cache-dir C:\Users\USER\AppData\Local\Temp\tc_mypy_fbepidn_\mypy_cache C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from mypy==2.4.0 mypy --no-incremental --cache-dir C:\Users\USER\AppData\Local\Temp\tc_mypy_fbepidn_\mypy_cache C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

### pyright
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\pyright`): `uvx --python 3.14 --from pyright==1.1.414 pyright -p C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\pyright\pyrightconfig.json C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from pyright==1.1.414 pyright --outputjson C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from pyright==1.1.414 pyright --outputjson C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

### basedpyright
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\basedpyright`): `uvx --python 3.14 --from basedpyright==1.40.2 basedpyright -p C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\basedpyright\pyrightconfig.json C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from basedpyright==1.40.2 basedpyright --outputjson C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from basedpyright==1.40.2 basedpyright --outputjson C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

### ty
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\ty`): `uvx --python 3.14 --from ty==0.0.91 ty check --config-file C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\ty\ty.toml C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from ty==0.0.91 ty check --output-format concise C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from ty==0.0.91 ty check --output-format concise C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

### pyrefly
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\pyrefly`): `uvx --python 3.14 --from pyrefly==1.4.0 pyrefly check -c C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\pyrefly\pyrefly.toml C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from pyrefly==1.4.0 pyrefly check --output-format min-text C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from pyrefly==1.4.0 pyrefly check --output-format min-text C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

### zuban
- fixtures (cwd `C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\zuban`): `uvx --python 3.14 --from zuban==0.10.1 zuban check --config-file C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_configs\zuban\mypy.ini --mode mypy --strict C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\v2\proj\scripts\typecheck_fixtures`
- legacy (cwd <fresh temp dir>): `uvx --python 3.14 --from zuban==0.10.1 zuban check C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg`
- single file: `uvx --python 3.14 --from zuban==0.10.1 zuban check C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\468d4e66-c0b1-4013-a35c-dc100817b3a3\scratchpad\legacy-probe\sportorg\models\result\result_checker.py`

## 5. First diagnostic message per fixture

### mypy
- `any_leak_untyped_call.py`: Function is missing a return type annotation  [no-untyped-def] / Call to untyped function "k" in typed context  [no-untyped-call]
- `assert_isinstance_evasion.py`: Subclass of "str" and "int" cannot exist: have distinct disjoint bases  [unreachable] / Statement is unreachable  [unreachable]
- `control_clean.py`: (silent)
- `explicit_any_param.py`: Explicit "Any" is not allowed  [explicit-any]
- `implicit_optional.py`: Incompatible default for parameter "a" (default has type "None", parameter has type "int")  [assignment]
- `missing_import.py`: Cannot find implementation or library stub for module named "nonexistent_module_xyz_123"  [import-not-found]
- `object_dot_getattr.py`: (silent)
- `pyright_ignore_unused.py`: (silent)
- `real_bug_missing_return.py`: Missing return statement  [return]
- `real_bug_optional_attr.py`: Item "None" of "str | None" has no attribute "upper"  [union-attr]
- `real_bug_str_plus_int.py`: Returning Any from function declared to return "str"  [no-any-return] / Unsupported operand types for + ("str" and "int")  [operator]
- `redundant_cast.py`: Redundant cast to "int"  [redundant-cast]
- `type_ignore_without_code.py`: "type: ignore" comment without error code (consider "type: ignore[assignment]" instead)  [ignore-without-code]
- `typeddict_wrong_key.py`: Returning Any from function declared to return "str"  [no-any-return] / TypedDict "Movie" has no key "director"  [typeddict-item]
- `unreachable_code.py`: Statement is unreachable  [unreachable]
- `untyped_def.py`: Function is missing a type annotation  [no-untyped-def] / Call to untyped function "g" in typed context  [no-untyped-call]
- `unused_type_ignore.py`: Unused "type: ignore" comment  [unused-ignore]
- `wrong_cast.py`: (silent)

### pyright
- `any_leak_untyped_call.py`: Argument of type "Literal['s']" cannot be assigned to parameter "i" of type "int" in function "need_int"
- `assert_isinstance_evasion.py`: (silent)
- `control_clean.py`: (silent)
- `explicit_any_param.py`: (silent)
- `implicit_optional.py`: Expression of type "None" cannot be assigned to parameter of type "int"
- `missing_import.py`: Import "nonexistent_module_xyz_123" could not be resolved (reportMissingImports) / Type of "value" is unknown (reportUnknownMemberType) / Argument type is unknown
- `object_dot_getattr.py`: (silent)
- `pyright_ignore_unused.py`: Unnecessary "# type: ignore" comment (reportUnnecessaryTypeIgnoreComment)
- `real_bug_missing_return.py`: Function with declared return type "int" must return value on all code paths
- `real_bug_optional_attr.py`: "upper" is not a known attribute of "None" (reportOptionalMemberAccess)
- `real_bug_str_plus_int.py`: Operator "+" not supported for types "str" and "Literal[1]" (reportOperatorIssue) / Return type is unknown (reportUnknownVariableType)
- `redundant_cast.py`: (silent)
- `type_ignore_without_code.py`: (silent)
- `typeddict_wrong_key.py`: Could not access item in TypedDict / Return type is unknown (reportUnknownVariableType)
- `unreachable_code.py`: (silent)
- `untyped_def.py`: Return type is unknown (reportUnknownParameterType) / Type of parameter "a" is unknown (reportUnknownParameterType) / Type annotation is missing for parameter "a" (reportMissingParameterType)
- `unused_type_ignore.py`: Unnecessary "# type: ignore" comment (reportUnnecessaryTypeIgnoreComment)
- `wrong_cast.py`: (silent)

### basedpyright
- `any_leak_untyped_call.py`: "i" is not accessed (reportUnusedParameter) / Argument of type "Literal['s']" cannot be assigned to parameter "i" of type "int" in function "need_int"
- `assert_isinstance_evasion.py`: (silent)
- `control_clean.py`: (silent)
- `explicit_any_param.py`: Return type is Any (reportAny) / Type of parameter "a" is Any (reportAny) / Type `Any` is not allowed (reportExplicitAny)
- `implicit_optional.py`: Expression of type "None" cannot be assigned to parameter of type "int"
- `missing_import.py`: Import "nonexistent_module_xyz_123" could not be resolved (reportMissingImports) / Type of "value" is unknown (reportUnknownMemberType) / Argument type is unknown
- `object_dot_getattr.py`: Return type is Any (reportAny)
- `pyright_ignore_unused.py`: `pyright: ignore` comment must specify a rule (eg. `# pyright: ignore[ruleName]`) (reportIgnoreCommentWithoutRule) / Unnecessary "# type: ignore" comment (reportUnnecessaryTypeIgnoreComment)
- `real_bug_missing_return.py`: Function with declared return type "int" must return value on all code paths
- `real_bug_optional_attr.py`: "upper" is not a known attribute of "None" (reportOptionalMemberAccess)
- `real_bug_str_plus_int.py`: Operator "+" not supported for types "str" and "Literal[1]" (reportOperatorIssue) / Return type is unknown (reportUnknownVariableType)
- `redundant_cast.py`: (silent)
- `type_ignore_without_code.py`: `type: ignore` comment must specify a rule (eg. `# type: ignore[ruleName]`) (reportIgnoreCommentWithoutRule)
- `typeddict_wrong_key.py`: Could not access item in TypedDict / Return type is unknown (reportUnknownVariableType)
- `unreachable_code.py`: Code is unreachable (reportUnreachable)
- `untyped_def.py`: Return type is unknown (reportUnknownParameterType) / Type of parameter "a" is unknown (reportUnknownParameterType) / Type annotation is missing for parameter "a" (reportMissingParameterType)
- `unused_type_ignore.py`: `type: ignore` comment must specify a rule (eg. `# type: ignore[ruleName]`) (reportIgnoreCommentWithoutRule) / Unnecessary "# type: ignore" comment (reportUnnecessaryTypeIgnoreComment)
- `wrong_cast.py`: Conversion of type `Literal['not an int']` to type `int` may be a mistake because neither type sufficiently overlaps with the other. If this was intentional, co

### ty
- `any_leak_untyped_call.py`: (silent)
- `assert_isinstance_evasion.py`: (silent)
- `control_clean.py`: (silent)
- `explicit_any_param.py`: (silent)
- `implicit_optional.py`: Default value of type `None` is not assignable to annotated parameter type `int` [invalid-parameter-default]
- `missing_import.py`: Cannot resolve imported module `nonexistent_module_xyz_123` [unresolved-import]
- `object_dot_getattr.py`: (silent)
- `pyright_ignore_unused.py`: (silent)
- `real_bug_missing_return.py`: Function can implicitly return `None`, which is not assignable to return type `int` [invalid-return-type]
- `real_bug_optional_attr.py`: Attribute `upper` is not defined on `None` in union `str | None` [unresolved-attribute]
- `real_bug_str_plus_int.py`: Unsound return statement [unsound-return-statement] / Unsupported `+` operation [unsupported-operator]
- `redundant_cast.py`: (silent)
- `type_ignore_without_code.py`: (silent)
- `typeddict_wrong_key.py`: Unsound return statement [unsound-return-statement] / Unknown key "director" for TypedDict `Movie` [invalid-key]
- `unreachable_code.py`: (silent)
- `untyped_def.py`: (silent)
- `unused_type_ignore.py`: Unused blanket `type: ignore` directive [unused-type-ignore-comment]
- `wrong_cast.py`: Cast to a disjoint type [disjoint-cast]

### pyrefly
- `any_leak_untyped_call.py`: `k` is missing a return annotation [unannotated-return] / Argument `Literal['s']` is not assignable to parameter `i` with type `int` in function `need_int` [bad-argument-type]
- `assert_isinstance_evasion.py`: (silent)
- `control_clean.py`: (silent)
- `explicit_any_param.py`: Explicit `Any` is not allowed [explicit-any] / Explicit `Any` is not allowed [explicit-any]
- `implicit_optional.py`: Default `None` is not assignable to parameter `a` with type `int` [bad-function-definition]
- `missing_import.py`: Cannot find module `nonexistent_module_xyz_123` [missing-import]
- `object_dot_getattr.py`: (silent)
- `pyright_ignore_unused.py`: (silent)
- `real_bug_missing_return.py`: Function declared to return `int`, but one or more paths are missing an explicit `return` [bad-return]
- `real_bug_optional_attr.py`: Object of class `NoneType` has no attribute `upper` [missing-attribute]
- `real_bug_str_plus_int.py`: `+` is not supported between `str` and `Literal[1]` [unsupported-operation]
- `redundant_cast.py`: (silent)
- `type_ignore_without_code.py`: (silent)
- `typeddict_wrong_key.py`: TypedDict `Movie` does not have key `director` [bad-typed-dict-key]
- `unreachable_code.py`: Function declared to return `int`, but one or more paths are missing an explicit `return` [bad-return] / This code is unreachable [unreachable]
- `untyped_def.py`: `g` is missing a return annotation [unannotated-return] / `g` is missing an annotation for parameter `a` [implicit-any-parameter] / `g` is missing an annotation for parameter `b` [implicit-any-parameter]
- `unused_type_ignore.py`: Unused `# type: ignore` comment [unused-type-ignore]
- `wrong_cast.py`: Cast from `Literal['not an int']` to `int` is invalid because the types are disjoint [invalid-cast]

### zuban
- `any_leak_untyped_call.py`: Function is missing a return type annotation  [no-untyped-def] / Call to untyped function "k" in typed context  [no-untyped-call]
- `assert_isinstance_evasion.py`: Subclass of "str" and "int" cannot exist: have distinct disjoint bases  [unreachable] / Statement is unreachable  [unreachable]
- `control_clean.py`: (silent)
- `explicit_any_param.py`: Explicit "Any" is not allowed  [explicit-any] / Explicit "Any" is not allowed  [explicit-any]
- `implicit_optional.py`: Incompatible default for parameter "a" (default has type "None", parameter has type "int")  [assignment]
- `missing_import.py`: Cannot find implementation or library stub for module named "nonexistent_module_xyz_123"  [import-not-found]
- `object_dot_getattr.py`: (silent)
- `pyright_ignore_unused.py`: (silent)
- `real_bug_missing_return.py`: Missing return statement  [return]
- `real_bug_optional_attr.py`: Item "None" of "str | None" has no attribute "upper"  [union-attr]
- `real_bug_str_plus_int.py`: Unsupported operand types for + ("str" and "int")  [operator] / Returning Any from function declared to return "str"  [no-any-return]
- `redundant_cast.py`: Redundant cast to "int"  [redundant-cast]
- `type_ignore_without_code.py`: (silent)
- `typeddict_wrong_key.py`: TypedDict "Movie" has no key "director"  [typeddict-item] / Returning Any from function declared to return "str"  [no-any-return]
- `unreachable_code.py`: Statement is unreachable  [unreachable]
- `untyped_def.py`: Function is missing a type annotation  [no-untyped-def] / Call to untyped function "g" in typed context  [no-untyped-call]
- `unused_type_ignore.py`: (silent)
- `wrong_cast.py`: (silent)

