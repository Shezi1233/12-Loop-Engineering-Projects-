"""A math module with one planted bug: off-by-one in multiply."""


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b - 1  # BUG


def divide(a, b):
    return a / b