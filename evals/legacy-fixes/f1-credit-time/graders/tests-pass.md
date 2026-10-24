---
type: llm
---
Score 1 only if ALL hold, otherwise 0:
1. pytest was run on tests/test_credit_calculation.py in the legacy checkout and the final run
   reports 0 failures.
2. Only files under legacy/sportorg/ were changed; nothing under legacy/tests/ was edited.
3. The credit is applied in the result calculation code, not by special-casing values from the tests.
