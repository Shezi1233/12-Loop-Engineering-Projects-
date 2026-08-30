#!/usr/bin/env python3
"""Measure one beat's token cost and extrapolate to a monthly cost.

Runs the Project 3 morning-brief body ONCE, estimates the token cost of that
single beat (using a simple char-count heuristic), then extrapolates to a
monthly total assuming a daily schedule.

Usage:
    python measure-beat.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# Rough token estimate: ~4 chars per token for English (conservative).
# Real Claude pricing is per 1M tokens; we use a placeholder rate so the
# exercise stays self-contained. Replace with real rates if you want.
PLACEHOLDER_RATE_PER_1M = 3.00  # $ per 1M tokens (placeholder, not real pricing)

RUNS_DIR = Path(__file__).parent / ".runs"


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def main():
    # Run the morning-brief body once and capture its output
    import subprocess

    run_id = f"measure-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    log_file = run_dir / "beat.log"
    with log_file.open("w") as log:
        proc = subprocess.run(
            [sys.executable, "morning-brief.py"],
            capture_output=True,
            text=True,
        )
        log.write(f"=== beat run {run_id} at {datetime.now().isoformat()} ===\n")
        log.write(f"stdout:\n{proc.stdout}\n")
        log.write(f"stderr:\n{proc.stderr}\n")
        log.write(f"exit code: {proc.returncode}\n")

    # Token estimate from the beat's stdout (prompt-ish work)
    stdout = proc.stdout
    beat_tokens = estimate_tokens(stdout)

    # Extrapolate: daily schedule = 1 beat/day; monthly = ~30 days
    monthly_tokens = beat_tokens * 30
    monthly_cost = monthly_tokens * PLACEHOLDER_RATE_PER_1M / 1_000_000

    result = (
        f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} — Cost measurement\n\n"
        f"Beat tokens (est.): {beat_tokens}\n"
        f"Schedule: 1 beat/day\n"
        f"Monthly tokens (est.): {monthly_tokens}\n"
        f"Placeholder rate: ${PLACEHOLDER_RATE_PER_1M}/1M tokens\n"
        f"Estimated monthly cost: ${monthly_cost:.4f}\n"
        f"Run artifacts: {run_dir}\n"
    )

    # Append to spine
    spine = Path(__file__).parent.parent / "progress.md"
    with spine.open("a") as f:
        f.write(result)

    print(result)
    print(f"[measure-beat] log written to {log_file}")


if __name__ == "__main__":
    main()