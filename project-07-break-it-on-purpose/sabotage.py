#!/usr/bin/env python3
"""Sabotage the Project 3 loop in two ways.

1. Point the loop at a NONEXISTENT file (so it can never find TODOs).
2. Force an impossible success condition (the loop never reaches a good state).

This simulates a broken deployment. Then diagnose using ONLY the log + spine.

Usage:
    python sabotage.py nonexistent-file    # point at nonexistent file
    python sabotage.py impossible-cause    # impossible success condition
"""

import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RUNS_DIR = Path(__file__).parent / ".runs"


def log_to_run_dir(run_dir: Path, msg: str):
    run_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    with (run_dir / "beat.log").open("a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "impossible-cause"
    run_id = f"sabotage-{mode}-{int(time.time())}"
    run_dir = RUNS_DIR / run_id

    if mode == "nonexistent-file":
        # Replace the spine path with a nonexistent file
        log_to_run_dir(run_dir, f"[sabotage] pointing loop at nonexistent spine: "
                                 f"../../DOES_NOT_EXIST/progress.md")
        cmd = [sys.executable, "morning-brief.py", "../../DOES_NOT_EXIST/progress.md"]
    elif mode == "impossible-cause":
        log_to_run_dir(run_dir, "[sabotage] sabotage mode: impossible success condition")
        cmd = [sys.executable, "morning-brief.py", "--sabotage"]
    else:
        print(f"unknown mode: {mode}")
        sys.exit(2)

    proc = subprocess.run(cmd, capture_output=True, text=True)
    log_to_run_dir(run_dir, f"[sabotage] exit code: {proc.returncode}")
    log_to_run_dir(run_dir, f"[sabotage] stdout: {proc.stdout.strip()}")
    log_to_run_dir(run_dir, f"[sabotage] stderr: {proc.stderr.strip()}")

    # Write a "needs a human" note to the spine
    spine = Path(__file__).parent.parent / "progress.md"
    with spine.open("a") as f:
        f.write(f"\n## SABOTAGE DETECTED — needs a human\n\n"
                f"Mode: {mode}\n"
                f"Run: {run_id}\n"
                f"Exit code: {proc.returncode}\n"
                f"Diagnosed at: {datetime.now().isoformat()}\n"
                f"Log: {run_dir}/beat.log\n"
                f"Action needed: see `diagnose.py` and the spine note above.\n")

    print(f"[sabotage] run {run_id} — log in {run_dir}/beat.log")
    print("[sabotage] spine updated with 'needs a human' note")
    print(f"[sabotage] exit code: {proc.returncode}")


if __name__ == "__main__":
    main()