# [код: pysport@b548c35 sportorg/models/result/result_tools.py:59-64]
from sportorg.models.memory import Race

def recalculate_results(
    race_object: Race | None = None, *, recheck_results: bool = True
) -> None: ...
