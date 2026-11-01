# [код: pysport@b548c35 sportorg/common/otime.py:34-191]
from typing_extensions import Self

class PythonOTime:
    def __init__(
        self, day: int = 0, hour: int = 0, minute: int = 0, sec: int = 0, msec: int = 0
    ) -> None: ...
    @classmethod
    def now(cls) -> Self: ...
    def to_msec(self, sub_sec: int = 3) -> int: ...

# ``_RustOTime or PythonOTime``: the Rust extension is optional (sportorg_core).
OTime: type[PythonOTime]
