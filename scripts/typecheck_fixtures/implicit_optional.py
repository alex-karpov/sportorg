# PATTERN: implicit Optional via default None; strict checker should report incompatible default / return type
def h(a: int = None) -> int:
    return a
