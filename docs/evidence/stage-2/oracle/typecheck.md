# Type checking the oracle driver (ADR-0009 T3)

`scripts/oracle_driver/{driver,snapshot}.py` copied into a temporary project, basedpyright (basedpyright 1.40.2 based on pyright 1.1.414) with `typeCheckingMode = all` and `pythonVersion = 3.8`. (b), leaving the driver out of the check, is not measured: it checks nothing.

| set-up | files | errors | warnings | rules |
|---|---|---|---|---|
| (a) legacy sources and packages: the legacy 3.8 interpreter | 4 | 32 | 0 | reportMissingTypeStubs 7, reportUnknownArgumentType 5, reportUnknownMemberType 15, reportUnknownVariableType 5 |
| (a') as (a) where no legacy exists (CI): the project interpreter | 4 | 99 | 0 | reportAny 1, reportMissingImports 8, reportUnknownArgumentType 13, reportUnknownMemberType 46, reportUnknownParameterType 3, reportUnknownVariableType 28 |
| (c) hand-written stubs, the project interpreter | 4 | 0 | 0 | none |

Python 3.9+ constructs in a 3.8 probe module, set-up (c):

- str.removeprefix (3.9): flagged False
- dict[...] at run time (3.9): flagged True
- dict | dict (3.9): flagged False
