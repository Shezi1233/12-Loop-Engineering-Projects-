#!/usr/bin/env python3
"""Make the tests pass, then stop.

A conditional loop: each iteration runs the test runner (pytest). The
COMMAND — not the agent — decides when it's done, via pytest's exit code.
Capped at MAX_TRIES so nothing runs unbounded.

Usage:
    python fix-loop.py
"""

import subprocess
import sys
from pathlib import Path

MAX_TRIES = 6
TEST_CMD = [sys.executable, "-m", "pytest", "-q"]


def main():
    cwd = Path(__file__).parent
    # Make sure tests start FAILING so the loop has something to do.
    # (They already are — this is a sanity check, not a reset.)
    print(f"[fix-loop] starting; cap = {MAX_TRIES} tries")
    print(f"[fix-loop] test command: {' '.join(TEST_CMD)}")

    for attempt in range(1, MAX_TRIES + 1):
        proc = subprocess.run(TEST_CMD, cwd=cwd, capture_output=True, text=True)

        # The command decides: exit code 0 == tests passed == done.
        if proc.returncode == 0:
            print(f"[fix-loop] PASSED on try {attempt} — tests pass, stopping")
            print("[fix-loop] done when: tests actually passed, not cap hit")
            return

        print(f"[fix-loop] try {attempt}/{MAX_TRIES}: tests FAILED "
              f"(exit {proc.returncode}) — making a fix attempt")

        if attempt == MAX_TRIES:
            print(f"[fix-loop] CAP HIT after {MAX_TRIES} tries — giving up")
            sys.exit(1)

        # The body: apply one fix attempt, then the loop re-runs the command.
        subprocess.run([sys.executable, "apply-fix.py"], cwd=cwd, check=True)

    print("[fix-loop] unreachable")
    sys.exit(1)


if __name__ == "__main__":
    main()