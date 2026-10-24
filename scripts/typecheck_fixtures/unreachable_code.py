# PATTERN: code after unconditional return; checkers with warn_unreachable should report unreachable code
def r() -> int:
    return 1
    print("never")
