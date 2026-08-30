#!/usr/bin/env python3
"""Run the secrets drill — simulates a one-off Routine invocation.

Two modes:
  --env-file  try to read token from a .env file (fails in fresh clone)
  --env-var   read token from environment variable (works in fresh clone)

Writes transcripts to .transcripts/<run-id>.md so you can read the
full run as if you were watching the model.

Usage:
    python run-routine.py --env-file
    DUMMY_TOKEN=abc123 python run-routine.py --env-var
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent
TRANSCRIPTS = REPO / ".transcripts"


def run_log(transcript, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    transcript.append(f"[{ts}] {msg}")


def run_env_file(transcript):
    """First run: try to read the token from a .env file."""
    run_log(transcript, "model: reading token from .env file using python-dotenv")
    env_file = REPO / ".env"

    if not env_file.exists():
        run_log(transcript, f"tool: ERROR: {env_file} does not exist in fresh clone")
        run_log(transcript, "model: token not found, will write what I see")
        token = "NO_TOKEN_FOUND"
    else:
        run_log(transcript, f"tool: found {env_file}, attempting to load")
        try:
            # Simulate python-dotenv
            with env_file.open() as f:
                for line in f:
                    if line.startswith("DUMMY_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        break
                else:
                    token = "NO_TOKEN_FOUND"
        except Exception as e:
            run_log(transcript, f"tool: ERROR reading .env: {e}")
            token = "NO_TOKEN_FOUND"

    (REPO / "token-used.txt").write_text(f"Token read: {token}\n")
    run_log(transcript, f"tool: wrote token-used.txt with: {token}")
    run_log(transcript, "status: SUCCESS")
    run_log(transcript, "model: DONE")


def run_env_var(transcript):
    """Second run: read token from environment variable."""
    run_log(transcript, "model: reading token from environment variable DUMMY_TOKEN")
    token = os.environ.get("DUMMY_TOKEN")
    if not token:
        run_log(transcript, "tool: ERROR: DUMMY_TOKEN not set in environment")
        token = "NO_TOKEN_FOUND"

    (REPO / "token-used.txt").write_text(f"Token read: {token}\n")
    run_log(transcript, f"tool: wrote token-used.txt with: {token}")
    run_log(transcript, "status: SUCCESS")
    run_log(transcript, "model: DONE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", action="store_true",
                        help="try to read token from .env (fails in fresh clone)")
    parser.add_argument("--env-var", action="store_true",
                        help="read token from environment variable")
    args = parser.parse_args()

    mode = "env-file" if args.env_file else ("env-var" if args.env_var else "env-file")

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

    if mode == "env-file":
        run_env_file(transcript)
    else:
        run_env_var(transcript)

    transcript_path.write_text("\n".join(transcript) + "\n")

    print(f"[run-routine] transcript written to {transcript_path}")
    print(f"[run-routine] mode: {mode}")


if __name__ == "__main__":
    main()