#!/usr/bin/env python3
"""Connector: on PASS, push the branch and open a PR (simulated locally).

Only runs when the reviewer says PASS. Uses `git push` and simulates a PR
open (prints the PR URL template). In a real GitHub repo this would use
`gh pr create`; here it just prints what would happen.

Usage:
    python connector.py                     # push + simulate PR open
    python connector.py --dry-run           # don't push, just print intent
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent


def get_current_branch() -> str:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def push_and_open_pr(dry_run: bool = False):
    branch = get_current_branch()
    print(f"[connector] on branch: {branch}")

    if not dry_run:
        # Push branch and set upstream
        ok, out, err = subprocess.run(
            ["git", "push", "--set-upstream", "origin", branch],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if ok:
            print(f"[connector] pushed {branch} to origin")
        else:
            print(f"[connector] push FAILED: {err}")
            return

    # Simulate PR open
    print(f"[connector] would open PR: daily-lint sweep — {branch}")
    print(f"[connector] PR title: 'Lint sweep: fix {len(get_changed_files())} issues'")
    print(f"[connector] PR body would summarize the changes made to target.py")
    print(f"[connector] DONE: PR simulation complete")


def get_changed_files() -> list:
    """Return list of changed file names (from last commit)."""
    proc = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return [f for f in proc.stdout.splitlines() if f]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="print intent without pushing")
    args = parser.parse_args()

    branch = get_current_branch()
    # If we're already on main with no branch, don't push
    if branch == "main":
        print("[connector] currently on main — nothing to push")
        print("[connector] DONE: on main, no push needed")
        return

    dry = args.dry_run
    print(f"[connector] starting push+PR for branch: {branch}")
    push_and_open_pr(dry_run=dry)
    print(f"[connector] DONE")


if __name__ == "__main__":
    main()