# PATTERN: assert isinstance(v, int) on a str value (branch unreachable afterwards); checkers with unreachable/redundant warnings should flag
def s(v: str) -> int:
    assert isinstance(v, int)
    return v + 1
