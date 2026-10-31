# [код: pysport@b548c35 sportorg/modules/backup/json.py:34-47]: what File.open calls with the file.
from typing import IO

def load(file: IO[str], *, compress: bool = False) -> None: ...
