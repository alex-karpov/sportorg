# PATTERN: cast to an incompatible type (silently wrong); no checker is expected to flag it
from typing import cast

w: int = cast(int, "not an int")
