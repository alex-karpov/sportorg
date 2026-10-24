# PATTERN: explicit Any in signature; strict checker (disallow_any_explicit) should report explicit Any
from typing import Any


def f(a: Any) -> Any:
    return a
