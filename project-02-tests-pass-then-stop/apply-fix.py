#!/usr/bin/env python3
"""One fix attempt: patches the first remaining off-by-one bug in mathlib.py.

This is the "agent's body" the loop calls each round. It fixes ONE bug per run.
Idempotent — if no bug remains, it does nothing.
"""

import re
import sys
from pathlib import Path

MATHLIB = Path(__file__).parent / "mathlib.py"


def main():
    src = MATHLIB.read_text()
    # Match a return statement with a trailing " - 1" (the planted bug pattern).
    pattern = re.compile(r"(return .*?)\s*-\s*1\s*$", re.MULTILINE)
    match = pattern.search(src)
    if not match:
        print("[apply-fix] no remaining off-by-one bug to fix")
        return

    fixed = pattern.sub(lambda m: m.group(1), src, count=1)
    MATHLIB.write_text(fixed)
    print(f"[apply-fix] patched: removed '- 1' from a return statement")


if __name__ == "__main__":
# TODO planted for project 3 demo
