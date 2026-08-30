#!/usr/bin/env python3
"""Reviewer agent: grades a fix by running tests + checking for minimal change.

Returns PASS if tests pass AND diff is minimal (only removes `- 1`).
Returns FAIL with reasons otherwise.

Usage:
    python reviewer.py /path/to/changed/file.py
"""

import subprocess
import sys
from pathlib import Path


def run_tests(workdir: Path) -> tuple[bool, str]:
    """Run pytest, return (passed, output)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=workdir,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, proc.stdout + proc.stderr


def check_minimal_diff(workdir: Path, changed_file: str) -> tuple[bool, str]:
    """Check that the only change is removing ` - 1` from a return statement.
    Compares current branch against main to see the actual fix diff."""
    proc = subprocess.run(
        ["git", "diff", "main", "--", changed_file],
        cwd=workdir,
        capture_output=True,
        text=True,
    )
    diff = proc.stdout
    if not diff:
        return False, "no changes in the target file"

    lines = diff.splitlines()
    # A "good" minimal fix: exactly one removed line ending in ` - 1`,
    # and exactly one added line that is the same minus the ` - 1` part.
    # Anything else (extra lines added/removed, comments changed, etc.) = bad.
    removed_minus_one = 0
    added_replacement = 0
    other_changes = 0
    for line in lines:
        if line.startswith("---") or line.startswith("+++"):
            continue  # diff header lines
        if line.startswith("-") and line.rstrip().endswith(" - 1"):
            removed_minus_one += 1
        elif line.startswith("+"):
            # Replacement line: should be the fix line without the ` - 1`
            # (must not contain ` - 1` itself)
            if " - 1" in line:
                other_changes += 1
            else:
                added_replacement += 1
        elif line.startswith("-"):
            other_changes += 1

    if removed_minus_one == 1 and added_replacement == 1 and other_changes == 0:
        return True, "minimal change: removed exactly one ` - 1`, added replacement"
    return False, (
        f"non-minimal diff: removed {removed_minus_one} `- 1`, "
        f"replacements {added_replacement}, other changes: {other_changes}"
    )


def main():
    if len(sys.argv) != 2:
        print("usage: python reviewer.py <changed-file>")
        sys.exit(2)

    changed_file = sys.argv[1]
    workdir = Path(__file__).parent

    # Step 1: tests must pass
    passed, output = run_tests(workdir)
    if not passed:
        print("FAIL")
        print(f"Reason: tests still failing\n{output}")
        return

    # Step 2: diff must be minimal
    minimal, reason = check_minimal_diff(workdir, changed_file)
    if not minimal:
        print("FAIL")
        print(f"Reason: {reason}")
        return

    # All good
    print("PASS")
    print(f"Reason: {reason}; tests pass")


if __name__ == "__main__":
    main()