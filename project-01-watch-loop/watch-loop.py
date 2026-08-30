#!/usr/bin/env python3
"""An in-session watch loop: polls for a completion file every 60 seconds.

Usage:
    python watch-loop.py
"""

import signal
import sys
import time
from pathlib import Path

OUTPUT_FILE = Path(__file__).parent / "output.txt"
POLL_INTERVAL = 60  # check every minute
MAX_HOURS = 12  # hard cap: never run unbounded


def _stop(signum, frame):
    print("\n[watch-loop] received signal, stopping cleanly")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    deadline = time.time() + MAX_HOURS * 3600
    print(f"[watch-loop] watching for {OUTPUT_FILE.name} "
          f"(poll every {POLL_INTERVAL}s, max {MAX_HOURS}h)")

    while True:
        if OUTPUT_FILE.exists():
            print(f"[watch-loop] FINISHED — {OUTPUT_FILE.name} appeared: "
                  f"{OUTPUT_FILE.read_text().strip()}")
            break

        if time.time() > deadline:
            print("[watch-loop] TIMED OUT — hit the hard cap, giving up")
            break

        print(f"[watch-loop] still waiting... "
              f"({time.strftime('%H:%M:%S')})")
        try:
            time.sleep(POLL_INTERVAL)
        except (KeyboardInterrupt, SystemExit):
            print("\n[watch-loop] interrupted, stopping cleanly")
            raise


if __name__ == "__main__":
    main()