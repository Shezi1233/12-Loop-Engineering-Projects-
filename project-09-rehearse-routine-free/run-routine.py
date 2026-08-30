#!/usr/bin/env python3
"""Run the routine body — simulates a one-off Routine invocation.

Two modes:
  --success   read git log, write summary, print DONE (transcript = success)
  --fail      try to read a nonexistent file, cannot recover (transcript = failure)

Writes a "transcript" file to .transcripts/<run-id>.md so you can read
the full run as if you were watching the model in real time.

Usage:
    python run-routine.py --success
    python run-routine.py --fail
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent
TRANSCRIPTS = REPO / ".transcripts"


def run_log(transcript, msg):
    """Append a step to the transcript (the model or a tool just did something)."""
    ts = datetime.now().strftime("%H:%M:%S")
    transcript.append(f"[{ts}] {msg}")


def run_success(transcript):
    """The success path: read git log, write a summary."""
    run_log(transcript, "model: reading yesterday's commits from git log")
    # Step 1: shell out to git log (one day back)
    one_day_ago = int(time.time()) - 24 * 3600
    one_day_ago_str = datetime.fromtimestamp(one_day_ago).strftime("%Y-%m-%d")
    proc = subprocess.run(
        ["git", "log", f"--since={one_day_ago_str}", "--oneline"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    commits = proc.stdout.strip() or "(no commits in the last 24h)"
    run_log(transcript, f"tool: git log returned: {commits[:80]}")

    # Step 2: write summary
    summary = f"## Yesterday's Commits ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    summary += "```\n"
    summary += commits + "\n"
    summary += "```\n"

    summary_path = REPO / "yesterday-summary.md"
    summary_path.write_text(summary)
    run_log(transcript, f"tool: wrote {summary_path} ({len(summary)} bytes)")

    # Step 3: status
    run_log(transcript, "status: SUCCESS")
    run_log(transcript, "model: DONE")


def run_fail(transcript):
    """The failure path: try to read a nonexistent file. The model can't recover."""
    run_log(transcript, "model: trying to read a file we know does not exist")
    nonexistent = REPO / "DOES_NOT_EXIST.md"

    run_log(transcript, f"tool: cat {nonexistent}")
    try:
        content = nonexistent.read_text()
        run_log(transcript, f"tool: read {len(content)} bytes")
    except FileNotFoundError as e:
        run_log(transcript, f"tool: ERROR: {e}")

    # The model recovers poorly
    run_log(transcript, "model: I can't read that file, but I'll still write something")
    run_log(transcript, "tool: write yesterday-summary.md (note: based on nothing)")

    summary = "## Yesterday's Commits (placeholder, file was missing)\n"
    (REPO / "yesterday-summary.md").write_text(summary)
    run_log(transcript, "status: SUCCESS (deceptively!)")
    run_log(transcript, "model: DONE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--success", action="store_true")
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()

    mode = "success" if args.success else ("fail" if args.fail else "success")

    TRANSCRIPTS.mkdir(exist_ok=True)
    run_id = f"transcript-{mode}-{int(time.time())}"
    transcript_path = TRANSCRIPTS / f"{run_id}.md"

    transcript = [
        f"# Transcript — run {run_id}",
        f"",
        f"Prompt body: routine-prompt.md",
        f"Mode: {mode}",
        f"Started: {datetime.now().isoformat()}",
        f"",
        f"## Run",
        f"",
    ]

    if mode == "success":
        run_success(transcript)
    else:
        run_fail(transcript)

    transcript_path.write_text("\n".join(transcript) + "\n")

    print(f"[run-routine] transcript written to {transcript_path}")
    print(f"[run-routine] status: {mode}")


if __name__ == "__main__":
    main()