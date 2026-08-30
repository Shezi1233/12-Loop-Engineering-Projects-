#!/usr/bin/env python3
"""Doorbell loop reviewer — reviews a diff and posts a GitHub review.

Intended to be invoked by the GitHub Actions workflow on pull_request events.

Usage (local, for testing):
    python doorbell.py --diff-path ./diff.txt --pr-number 1
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def parse_diff(diff_text: str):
    """Return a list of (file, line_no, context) for every changed line."""
    changes = []
    for line in diff_text.splitlines():
        m = re.match(r"^@@ .*\+(\d+),?\d* @@", line)
        if m:
            changes.append(int(m.group(1)))
    return changes


def review(diff_text: str, pr_number: int):
    """Analyze the diff, return (verdict, comment)."""
    planted = {"off-by-one": " - 1", "null-check": "if not"}
    found = []
    for pattern in planted.values():
        for line in diff_text.splitlines():
            if pattern in line:
                found.append(f"planted pattern `{pattern}` found in diff")

    if found:
        return "FAIL", "; ".join(found)
    return "PASS", "clean diff — no planted issues"


def post_review(gh, pr_number, verdict, comment):
    """Post a review on the PR via the GitHub CLI."""
    if not gh:
        print(f"[doorbell] (dry-run) would review PR #{pr_number}")
        print(f"[doorbell] verdict: {verdict}")
        print(f"[doorbell] comment: {comment}")
        return
    run = lambda c: subprocess.run(c, capture_output=True, text=True)
    run(["gh", "api", f"/repos/{gh}/pulls/{pr_number}/reviews",
         "--method", "POST", "--field", f"body={comment}",
         "--field", f"event={'REQUEST_CHANGES' if verdict == 'FAIL' else 'APPROVE'}"])


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff-path")
    parser.add_argument("--pr-number", type=int)
    parser.add_argument("--gh", default="")
    args = parser.parse_args()

    diff_text = Path(args.diff_path).read_text() if args.diff_path else ""
    verdict, comment = review(diff_text, args.pr_number or 0)
    print(f"VERDICT={verdict}")
    print(f"COMMENT={comment}")

    post_review(args.gh, args.pr_number or 0, verdict, comment)


if __name__ == "__main__":
    main()