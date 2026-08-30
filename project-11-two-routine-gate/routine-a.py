#!/usr/bin/env python3
"""Routine A: draft a release note from the last 5 commits.

One-off invocation. Creates a new branch `release-notes/draft-<ts>` and
writes `release-notes-draft.md` to it.

Usage:
    python routine-a.py
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent


def run_log(transcript, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    transcript.append(f"[{ts}] {msg}")


def main():
    ts = int(time.time())
    branch = f"release-notes/draft-{ts}"

    transcript = []

    run_log(transcript, "model: reading last 5 commits via git log")
    proc = subprocess.run(
        ["git", "log", "--oneline", "-n", "5"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    commits = proc.stdout.strip() or "(no commits yet)"
    run_log(transcript, f"tool: git log returned: {commits[:80]}")

    # Build the draft
    today = datetime.now().strftime("%Y-%m-%d")
    draft = f"""# Release Notes — Draft {today}

## Summary
Based on the last 5 commits.

## Commits included
```
{commits}
```

## Status
DRAFT — review before approving via Routine B.
"""
    (REPO / "release-notes-draft.md").write_text(draft)
    run_log(transcript, f"tool: wrote release-notes-draft.md ({len(draft)} bytes)")

    # Create branch and commit
    run_log(transcript, f"model: creating branch {branch}")
    subprocess.run(["git", "checkout", "-b", branch], cwd=REPO, check=True)
    subprocess.run(["git", "add", "release-notes-draft.md"], cwd=REPO, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"draft: release notes {today}"],
        cwd=REPO,
        check=True,
    )
    run_log(transcript, f"tool: committed on branch {branch}")

    # Write transcript
    transcripts = REPO / ".transcripts"
    transcripts.mkdir(exist_ok=True)
    run_id = f"routine-A-{ts}"
    transcript_path = transcripts / f"{run_id}.md"
    transcript_path.write_text(
        f"# Transcript — {run_id}\n\n"
        f"Mode: draft\n"
        f"Branch: {branch}\n\n"
        + "\n".join(transcript) + "\n"
    )

    print(f"[routine-A] branch: {branch}")
    print(f"[routine-A] draft: release-notes-draft.md")
    print(f"[routine-A] transcript: {transcript_path}")
    print("[routine-A] DRAFT READY")


if __name__ == "__main__":
    main()