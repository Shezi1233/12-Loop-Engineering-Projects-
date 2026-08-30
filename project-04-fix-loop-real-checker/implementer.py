#!/usr/bin/env python3
"""Implementer: applies ONE fix attempt in a fresh worktree/branch.

Given a buggy file, applies the skill's fix step (remove one ` - 1`),
commits the change, returns the branch name.

Usage:
    python implementer.py buggy_math.py
"""

import re
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("usage: python implementer.py <buggy-file>")
        sys.exit(2)

    buggy_file = sys.argv[1]
    workdir = Path(__file__).parent
    repo_root = workdir

    # Create a fresh branch for this fix attempt
    import time
    branch = f"fix-attempt-{int(time.time())}"

    subprocess.run(["git", "checkout", "-b", branch], cwd=repo_root, check=True)

    # Apply one fix: find and remove the first ` - 1` at end of code line.
    # Matches ` - 1` (with possible trailing space) but NOT newlines, so the
    # surrounding line structure stays intact.
    src = (repo_root / buggy_file).read_text()
    pattern = re.compile(r" - 1(?=[ \t]*\n)", re.MULTILINE)
    match = pattern.search(src)
    if not match:
        print("[implementer] no ` - 1` pattern found — nothing to fix")
        # Still commit so reviewer can see (or we exit)
        sys.exit(0)

    fixed = pattern.sub("", src, count=1)
    (repo_root / buggy_file).write_text(fixed)
    print(f"[implementer] patched {buggy_file}: removed one ` - 1`")

    # Commit
    subprocess.run(["git", "add", buggy_file], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"fix: remove off-by-one in {buggy_file}"],
        cwd=repo_root,
        check=True,
    )

    print(f"BRANCH={branch}")
    print(f"FILE={buggy_file}")


if __name__ == "__main__":
    main()