# BUG: missing return on the flag=False branch; checker should report missing return
def p(flag: bool) -> int:
    if flag:
        return 1
