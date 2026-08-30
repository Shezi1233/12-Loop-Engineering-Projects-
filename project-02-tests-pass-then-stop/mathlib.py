"""A tiny math library with two planted bugs (off-by-one errors)."""


def add(a, b):
    # BUG 1: returns a + b - 1 instead of a + b
    return a + b
def double(a):
    # BUG 2: returns a * 2 - 1 instead of a * 2
    return a * 2