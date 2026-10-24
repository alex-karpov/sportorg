# PATTERN: bare type-ignore comment (no error code) silencing a genuine error; strict checker should flag ignore-without-code and ideally the error too
y: int = "s"  # type: ignore
