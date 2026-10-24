# PATTERN: function without annotations; strict checker should report missing annotations (and call g(1, "x") is a runtime error)
def g(a, b):
    return a + b


g(1, "x")
