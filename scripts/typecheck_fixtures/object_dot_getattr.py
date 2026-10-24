# PATTERN: getattr(obj, "attr") dodging an attribute error on str; checker returns Any silently, direct v.attr would be an error
def t(obj: str) -> object:
    return getattr(obj, "attr")
