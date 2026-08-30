#!/usr/bin/env python3
"""Set up a deliberate repeated-failure pattern in progress.md for testing.

This is the "planted repeated failure" the dreaming loop should catch.
Inserts 3 dated entries that all have the same failure reason.

Usage:
    python setup-repeated-failures.py
"""

import time
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).parent.parent
SPINE = REPO / "progress.md"


def main():
    now = datetime.now()
    # Plant 3 entries dated 1, 2, 3 days ago with the same failure
    entries = []
    for days_ago in (3, 2, 1):
        date = now - timedelta(days=days_ago)
        ts = date.strftime("%Y-%m-%d %H:%M")
        entries.append(
            f"\n## {ts} — Daily Lint Sweep\n\n"
            f"- verdict: FAIL\n"
            f"- runtime: 12.3s\n"
            f"- branch: `daily-lint-{int(date.timestamp())}`\n"
            f"- engine: daily-lint-engine.py\n"
            f"- reason: 'non-minimal diff: removed 1 `- 1`, other changes: 0'\n"
        )

    with SPINE.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(e)

    print(f"[setup] planted 3 repeated-failure entries in {SPINE}")


if __name__ == "__main__":
    main()