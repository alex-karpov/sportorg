# BUG: str + int; checker should report unsupported operand types
def m(s: str) -> str:
    return s + 1
