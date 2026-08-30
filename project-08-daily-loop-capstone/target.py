"""A small Python module with intentional test/style issues for the lint sweep."""

import math


def circle_area(radius):
    """Calculate area of a circle: πr²."""
    return math.pi * radius ** 2


def sphere_volume(radius):
    """Calculate volume of a sphere: 4/3πr³."""
    return 4 / 3 * math.pi * radius ** 3


def fibonacci(n):
    """Return the nth Fibonacci number (1-indexed: fib(1)=1, fib(2)=1, fib(10)=55)."""
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b