#!/usr/bin/env python3
"""A long task: sleeps for N seconds, then writes a completion file.

Usage:
    python long-task.py 120
"""

import signal
import sys
import time
from pathlib import Path

OUTPUT_FILE = Path(__file__).parent / "output.txt"
MAX_SECONDS = 600  # hard cap: never run unbounded


def _stop(signum, frame):
    print("[long-task] received signal, stopping cleanly")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    if len(sys.argv) != 2:
        print("usage: python long-task.py <seconds>")
        sys.exit(2)

    seconds = min(int(sys.argv[1]), MAX_SECONDS)
    print(f"[long-task] starting: will sleep {seconds}s, then write {OUTPUT_FILE.name}")

    try:
        time.sleep(seconds)
    except (KeyboardInterrupt, SystemExit):
        print("[long-task] interrupted before completion")
        raise

    OUTPUT_FILE.write_text(f"done at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"[long-task] DONE — wrote {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()