#!/usr/bin/env python3
"""Diagnose a sabotage using ONLY the log + spine (no replay).

Reads every .runs/<run-id>/beat.log and the spine, then reports:
- What failed
- When it failed (timestamp)
- The monthly cost (from the most recent measurement)

Usage:
    python diagnose.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

RUNS_DIR = Path(__file__).parent / ".runs"
SPINE = Path(__file__).parent.parent / "progress.md"


def read_logs():
    """Read every beat.log and return a list of (run_id, timestamp, line)."""
    entries = []
    for log_file in sorted(RUNS_DIR.glob("*/beat.log")):
        run_id = log_file.parent.name
        for line in log_file.read_text().splitlines():
            # Lines look like: 2026-08-29T12:34:56.789 message
            m = re.match(r"^(\d{4}-\d{2}-\d{2}T\S+)\s+(.*)$", line)
            if m:
                entries.append((run_id, m.group(1), m.group(2)))
            else:
                entries.append((run_id, "?", line))
    return entries


def read_spine():
    return SPINE.read_text() if SPINE.exists() else ""


def extract_monthly_cost(spine_text: str):
    match = re.search(
        r"Estimated monthly cost: \$(\d+\.\d+)",
        spine_text,
    )
    return match.group(1) if match else None


def main():
    logs = read_logs()
    spine_text = read_spine()

    print("=" * 60)
    print("DIAGNOSIS — from log + spine only (no replay)")
    print("=" * 60)

    if not logs:
        print("\nNo beat logs found — nothing to diagnose.")
        return

    # Find sabotage entries
    sabotage_entries = [
        e for e in logs
        if "SABOTAGED" in e[2] or "sabotage" in e[2].lower()
        or "nonexistent" in e[2].lower()
        or "impossible" in e[2].lower()
    ]

    print(f"\nTotal beats logged: {len(logs)}")
    print(f"Sabotage beats: {len(sabotage_entries)}")

    if not sabotage_entries:
        print("\nNo sabotage detected in logs.")
        return

    print("\n--- Sabotage timeline ---")
    for run_id, ts, msg in sabotage_entries:
        print(f"[{ts}] {run_id}: {msg}")

    # Find the first sabotage beat and the run it belongs to
    first_sabotage = sabotage_entries[0]
    run_id = first_sabotage[0]
    ts = first_sabotage[1]

    print(f"\n--- Diagnosis ---")
    print(f"WHAT FAILED: The sabotage made the loop's success condition impossible.")
    print(f"WHEN: {ts}")
    print(f"RUN: {run_id}")
    print(f"EVIDENCE: {first_sabotage[2]}")

    # Show all entries for that run
    run_entries = [e for e in logs if e[0] == run_id]
    print(f"\n--- Full log for run {run_id} ---")
    for _, t, m in run_entries:
        print(f"  [{t}] {m}")

    # Show the spine note
    spine_note = re.search(
        r"## SABOTAGE DETECTED.*?(?=## |\Z)",
        spine_text,
        re.DOTALL,
    )
    if spine_note:
        print(f"\n--- Spine note (needs a human) ---")
        print(spine_note.group(0).strip())

    # Cost
    cost = extract_monthly_cost(spine_text)
    print(f"\n--- Monthly cost ---")
    print(f"Estimated monthly cost: ${cost} (placeholder rate)")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"-> WHAT: {first_sabotage[2].split('[')[0].strip() if '[' in first_sabotage[2] else first_sabotage[2]}")
    print(f"-> WHEN: {ts}")
    print(f"-> RUN: {run_id}")
    print(f"-> SPINE NOTE: {'yes' if spine_note else 'no'}")
    print(f"-> MONTHLY COST: ${cost}")
    print(f"-> DIAGNOSED WITHOUT REPLAY: yes")


if __name__ == "__main__":
    main()