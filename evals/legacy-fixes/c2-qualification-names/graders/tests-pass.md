---
type: llm
---
Score 1 only if ALL hold, otherwise 0:
1. pytest was run on tests/test_qualification.py in the legacy checkout and the final run reports
   0 failures.
2. Only files under legacy/sportorg/ were changed; nothing under legacy/tests/ was edited.
3. The mapping handles case, spaces, dots and short forms generically (normalisation + lookup),
   not by special-casing exactly the strings quoted in the task.
