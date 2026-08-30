#!/usr/bin/env python3
"""Reviewer: grades a fix by running tests + checking diff minimality.

Returns PASS if tests pass AND diff is minimal (only `target.py` changes,
no unrelated modifications). Returns FAIL with reasons otherwise.

Usage:
    python reviewer.py
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent
TARGET = REPO / "target.py"


def run_tests() -> tuple[bool, str]:
    """Run pytest, return (passed, output)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)


def check_diff_minimality() -> tuple[bool, str]:
    """Check that only target.py changed between main and this branch."""
    # Compare branch to main (not working tree vs HEAD)
    proc = subprocess.run(
        ["git", "diff", "main", "--name-only"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    changed_files = [f for f in proc.stdout.splitlines() if f]

    if not changed_files:
        # No changes at all — tests pass, nothing to fix — that's fine
        return True, "no changes needed: tests already pass"

    # Only target.py should change (the lint output)
    # Allow .runs/ (heartbeat artifacts) and also allow the engine's own source
    # files to change (since we're running the engine from this repo)
    allowed = {"target.py", ".runs"}
    risky = [f for f in changed_files if f not in allowed and not f.startswith(".runs")]
    if risky:
        return False, f"non-target files changed: {', '.join(risky[:5])}"

    # Check the actual diff content for ` - 1` off-by-one patterns
    diff_proc = subprocess.run(
        ["git", "diff", "main", "--", "target.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    diff = diff_proc.stdout
    off_by_one = diff.count(" - 1")
    if off_by_one > 0:
        return False, f"diff contains {off_by_one} off-by-one ` - 1` patterns"

    return True, "minimal diff: only target.py changes, clean"


def main():
    passed, output = run_tests()

    if not passed:
        print("FAIL")
        print(f"Reason: tests still failing")
        print(f"Output: {output[:500]}")  # truncate for readability
        sys.exit(1)

    minimal, reason = check_diff_minimality()
    if not minimal:
        print("FAIL")
        print(f"Reason: {reason}")
        sys.exit(1)

    # All checks passed
    print("PASS")
    print(f"Reason: {reason}")


if __name__ == "__main__":
    main()