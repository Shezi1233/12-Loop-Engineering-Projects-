#!/usr/bin/env python3
"""Reviewer for the doorbell loop.

Runs on the PR's diff, grades it, returns PASS or FAIL with reasons.
"""

import subprocess
import sys
from pathlib import Path

PLANTED_ISSUES = [
    ("off-by-one", " - 1"),
    ("deleted-null-check", "if not"),
]


def main():
    cwd = Path(__file__).parent
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-v"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr

    # Check for planted issues
    issues = []
    for name, pattern in PLANTED_ISSUES:
        if pattern in (Path(cwd / "src.py").read_text() if (Path(cwd / "src.py")).exists() else ""):
            issues.append(f"planted issue: {name}")

    if proc.returncode != 0:
        issues.append("tests fail")

    if issues:
        print("FAIL")
        print("Reasons:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)

    print("PASS")
    print("Clean — no planted issues, tests pass")


if __name__ == "__main__":
    main()