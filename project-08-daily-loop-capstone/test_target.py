"""Tests for target.py — each one asserts correctness; fixes in target.py make them pass."""

import math
import pytest
from target import circle_area, sphere_volume, fibonacci


def test_circle_area_1():
    assert circle_area(1) == pytest.approx(math.pi)


def test_circle_area_2():
    """Should be exactly 4π when r=2."""
    result = circle_area(2)
    assert result == pytest.approx(4 * math.pi)


def test_sphere_volume_1():
    """Volume of sphere r=1 = 4/3π ≈ 4.18879."""
    result = sphere_volume(1)
    assert abs(result - 4.18879) < 0.001


def test_fibonacci_1():
    assert fibonacci(1) == 1


def test_fibonacci_10():
    assert fibonacci(10) == 55