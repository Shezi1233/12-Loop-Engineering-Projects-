"""Tests for src.py."""

from src import calculate, doubled


def test_calculate():
    assert calculate(5, 3) == 8  # FAILS: returns 7


def test_doubled():
    assert doubled(4) == 8