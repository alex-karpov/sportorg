# BUG: attribute access on Optional (None has no upper); checker should report
def n(s: str | None) -> str:
    return s.upper()
