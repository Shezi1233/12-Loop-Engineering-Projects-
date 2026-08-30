"""A math module with one planted bug: off-by-one in multiply."""


def add(a, b):
    return a + b


def multiply(a, b):
    # BUG: returns a * b - 1 instead of a * b
    return a * b - 1


def divide(a, b):
    return a / b