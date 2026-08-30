#!/usr/bin/env python3
"""Observability version of the Project 3 morning brief.

Every beat logs to: a per-run log file (.runs/<run-id>/beat.log) AND the
spine (progress.md). After a sabotage, you can diagnose the failure using
ONLY the log + spine — no replay.

Usage:
    python morning-brief.py                 # normal run
    python morning-brief.py --sabotage      # sabotaged run (impossible success condition)
"""

import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SPINE = Path(__file__).parent.parent / "progress.md"
RUNS_DIR = Path(__file__).parent / ".runs"


def log_to_run_dir(run_dir: Path, msg: str):
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "beat.log").open("a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


def read_spine(spine: Path) -> str:
    return spine.read_text() if spine.exists() else ""


def collect_todos(repo: Path):
    todo_re = re.compile(r"\bTODO\b")
    found = []
    for p in sorted(repo.rglob("*.py")):
        if ".git" in p.parts or "__pycache__" in p.parts or ".runs" in p.parts:
            continue
        try:
            lines = p.read_text().splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            if todo_re.search(line):
                found.append((str(p.relative_to(repo)), i, line.strip()))
    return found


def parse_recorded_todos(spine_text: str):
    entries = re.findall(
        r"## .+? — Morning Brief\n\n.*?(?=## |\Z)",
        spine_text,
        re.DOTALL,
    )
    recorded = set()
    if entries:
        block = entries[-1]
        for m in re.finditer(r"`([^`]+):(\d+)`", block):
            recorded.add((m.group(1), int(m.group(2))))
    return recorded


def fmt_todos(todos) -> str:
    if not todos:
        return "- none new since last run"
    return "\n".join(f"- `{f}:{n}` {t}" for f, n, t in todos)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sabotage", action="store_true",
                        help="impossible success condition (never succeeds)")
    parser.add_argument("spine", nargs="?", default=str(DEFAULT_SPINE),
                        help="path to the spine file (default: ../progress.md)")
    args = parser.parse_args()

    run_id = f"beat-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = RUNS_DIR / run_id
    log_to_run_dir(run_dir, f"[beat] starting run {run_id}")

    spine = Path(args.spine)
    repo = spine.parent
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    log_to_run_dir(run_dir, f"[beat] spine path: {spine}")
    log_to_run_dir(run_dir, f"[beat] sabotage mode: {args.sabotage}")

    # Sabotage: impossible success condition. The loop can NEVER find any TODOs.
    if args.sabotage:
        log_to_run_dir(run_dir, "[beat] SABOTAGED: success condition is impossible — "
                                 "will always report 'none new since last run' even when TODOs exist")
        # Pretend we collected nothing, regardless of reality
        current = []
        recorded = set()
        new_todos = []
    else:
        spine_text = read_spine(spine)
        current = collect_todos(repo)
        recorded = parse_recorded_todos(spine_text)
        current_keys = {(f, n) for f, n, _ in current}
        new_todos = [t for t in current if (t[0], t[1]) not in recorded]

    entry = (
        f"## {now} — Morning Brief\n\n"
        f"Spine already held {len(recorded)} TODO(s).\n\n"
        f"Open TODO comments:\n{fmt_todos(new_todos)}\n\n"
        f"Total open: {len(current)}\n"
    )

    with spine.open("a", encoding="utf-8") as fh:
        fh.write(entry)

    log_to_run_dir(run_dir, f"[beat] wrote spine entry: {now}")
    log_to_run_dir(run_dir, f"[beat] DONE")

    print(entry)


if __name__ == "__main__":
    main()