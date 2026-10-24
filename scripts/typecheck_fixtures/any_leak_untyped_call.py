# PATTERN: untyped function result (inferred/Any) passed to int parameter; str is returned but int expected; strict checkers that infer the return type report an error, those treating it as Any are silent
def k():
    return "s"


def need_int(i: int) -> None: ...


need_int(k())
