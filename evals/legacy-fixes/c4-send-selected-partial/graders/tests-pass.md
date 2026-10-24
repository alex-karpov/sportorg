---
type: llm
---
Score 1 only if ALL hold, otherwise 0:
1. pytest was run on tests/test_race_partial.py in the legacy checkout and the final run reports
   0 failures.
2. Only files under legacy/sportorg/ were changed; nothing under legacy/tests/ was edited.
3. Ordering follows the main model and multi-day matching uses the multi-day id; no test-specific
   hard-coding.
