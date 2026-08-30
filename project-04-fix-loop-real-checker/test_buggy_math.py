"""Tests for buggy-math. One test fails due to the planted bug."""


from buggy_math import add, multiply, divide


def test_add():
    assert add(2, 3) == 5


def test_multiply():
    assert multiply(6, 7) == 42  # FAILS: returns 41


def test_divide():
    assert divide(10, 2) == 5