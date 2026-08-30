"""Module with one planted bug — off-by-one in calculate."""


def calculate(x, y):
    # BUG: off-by-one in the return
    return x + y - 1


def doubled(x):
    return x * 2