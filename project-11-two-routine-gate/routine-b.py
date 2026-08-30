#!/usr/bin/env python3
"""Routine B: publish the approved draft as final.

API-triggered only. Reads `release-notes-draft.md`, copies it to
`release-notes-final.md`, commits on a new branch, tags the commit.

Usage:
    python routine-b.py                     # publish from current draft
    python routine-b.py --no-tag            # skip the tag step
"""

import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tag", action="store_true", help="skip the tag step")
    args = parser.parse_args()

    ts = int(time.time())
    branch = f"release-notes/final-{ts}"
    draft_path = REPO / "release-notes-draft.md"
    final_path = REPO / "release-notes-final.md"

    transcript = []

    run_log(transcript, "model: triggered — reviewing draft before publishing")
    if not draft_path.exists():
        run_log(transcript, f"tool: ERROR: {draft_path} does not exist")
        run_log(transcript, "status: FAIL — no draft to publish")
        sys.exit(1)

    content = draft_path.read_text()
    if not content.strip():
        run_log(transcript, f"tool: ERROR: {draft_path} is empty")
        run_log(transcript, "status: FAIL — draft is empty")
        sys.exit(1)

    run_log(transcript, f"tool: read draft ({len(content)} bytes)")

    # Move draft → final
    final_path.write_text(content)
    run_log(transcript, f"tool: wrote {final_path}")

    # Branch + commit
    run_log(transcript, f"model: creating branch {branch}")
    subprocess.run(["git", "checkout", "-b", branch], cwd=REPO, check=True)
    subprocess.run(["git", "add", "release-notes-final.md"], cwd=REPO, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"final: release notes {datetime.now().strftime('%Y-%m-%d')}"],
        cwd=REPO,
        check=True,
    )
    run_log(transcript, f"tool: committed on branch {branch}")

    if not args.no_tag:
        tag = f"release-{datetime.now().strftime('%Y%m%d')}-{ts}"
        subprocess.run(["git", "tag", tag], cwd=REPO, check=True)
        run_log(transcript, f"tool: tagged as {tag}")

    # Write transcript
    transcripts = REPO / ".transcripts"
    transcripts.mkdir(exist_ok=True)
    run_id = f"routine-B-{ts}"
    transcript_path = transcripts / f"{run_id}.md"
    transcript_path.write_text(
        f"# Transcript — {run_id}\n\n"
        f"Mode: publish\n"
        f"Branch: {branch}\n\n"
        + "\n".join(transcript) + "\n"
    )

    print(f"[routine-B] branch: {branch}")
    print(f"[routine-B] final: release-notes-final.md")
    print(f"[routine-B] transcript: {transcript_path}")
    print("[routine-B] PUBLISHED")


if __name__ == "__main__":
    main()