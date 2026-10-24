# PATTERN: redundant cast to the same type; strict checker should report redundant cast
from typing import cast

z = cast(int, 1)
