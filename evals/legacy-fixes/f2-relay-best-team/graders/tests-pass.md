---
type: llm
---
Score 1 only if ALL hold, otherwise 0:
1. pytest was run on tests/test_relay_results.py in the legacy checkout and the final run reports
   0 failures.
2. Only files under legacy/sportorg/ were changed; nothing under legacy/tests/ was edited.
3. Team placing is computed in the result calculation code as a general rule, not by hard-coding
   expected places from the tests.
