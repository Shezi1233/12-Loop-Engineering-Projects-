"""Three small FAILING tests for mathlib. Deliberately broken on purpose."""

from mathlib import add, double


def test_add_basic():
    assert add(2, 3) == 5  # FAILS: returns 4


def test_add_zero():
    assert add(0, 0) == 0  # FAILS: returns -1


def test_double_basic():
    assert double(5) == 10  # FAILS: returns 9