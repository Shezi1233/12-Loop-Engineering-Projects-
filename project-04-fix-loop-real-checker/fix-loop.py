#!/usr/bin/env python3
"""Fix loop with a real checker (maker-checker pattern).

Orchestrates: implementer drafts a fix in a branch -> reviewer grades it.
Only on PASS does it push the branch and open a PR (simulated).

Usage:
    python fix-loop.py buggy_math.py        # good fix attempt
    python fix-loop.py buggy_math.py --bad  # deliberately bad fix
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd, **kwargs):
    """Run command, return (success, stdout, stderr)."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, **kwargs)
    return proc.returncode == 0, proc.stdout, proc.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="buggy file to fix")
    parser.add_argument("--bad", action="store_true", help="plant a deliberately bad fix")
    args = parser.parse_args()

    repo = Path(__file__).parent
    buggy_file = args.file

    print(f"[fix-loop] starting fix loop for {buggy_file}")
    print(f"[fix-loop] mode: {'BAD fix (planted failure)' if args.bad else 'GOOD fix'}")

    # 1. Ensure tests start failing (they already do)
    ok, out, err = run([sys.executable, "-m", "pytest", "-q"], repo)
    if ok:
        print("[fix-loop] tests already pass — nothing to fix")
        return

    # 2. Implementer makes a fix attempt in a fresh branch
    ok, out, err = run([sys.executable, "implementer.py", buggy_file], repo)
    if not ok:
        print(f"[fix-loop] implementer failed: {err}")
        sys.exit(1)

    # Parse branch and file from implementer output
    branch = None
    for line in out.splitlines():
        if line.startswith("BRANCH="):
            branch = line.split("=", 1)[1]
    if not branch:
        print("[fix-loop] implementer didn't report a branch")
        sys.exit(1)

    print(f"[fix-loop] implementer created branch: {branch}")

    # Switch to the branch to test the fix (implementer ran commands but we need to checkout)
    run(["git", "checkout", branch], repo)

    # 3. If --bad, sabotage the fix (add a wrong change)
    if args.bad:
        # Make an additional wrong change in the same file
        src = (repo / buggy_file).read_text()
        # Add a bogus change: change a valid return
        src = src.replace("return a + b", "return a + b + 999")
        (repo / buggy_file).write_text(src)
        run(["git", "add", buggy_file], repo)
        run(["git", "commit", "-m", "sabotage: add wrong change"], repo)
        print("[fix-loop] SABOTAGED: added a deliberate bad change")

    # 4. Reviewer grades the fix
    ok, out, err = run([sys.executable, "reviewer.py", buggy_file], repo)
    verdict = out.strip().splitlines()[0] if out.strip() else "ERROR"
    reason = "\n".join(out.strip().splitlines()[1:]) if len(out.strip().splitlines()) > 1 else ""

    print(f"[fix-loop] reviewer verdict: {verdict}")
    if reason:
        print(f"[fix-loop] reason: {reason}")

    # 5. Only on PASS: push branch and "open PR" (simulated)
    if verdict == "PASS":
        print(f"[fix-loop] PASS — pushing branch and simulating PR open")
        run(["git", "push", "-u", "origin", branch], repo)
        print(f"[fix-loop] PR would be opened for branch: {branch}")
        print(f"[fix-loop] DONE: good fix gets PASS+PR")
    else:
        print(f"[fix-loop] FAIL — branch discarded, no PR")
        # Clean up: go back to main and delete branch locally
        run(["git", "checkout", "main"], repo)
        run(["git", "branch", "-D", branch], repo)
        print(f"[fix-loop] DONE: bad fix gets FAIL with reasons")


if __name__ == "__main__":
    main()