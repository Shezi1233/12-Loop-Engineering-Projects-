#!/usr/bin/env python3
"""Morning brief with a memory — a scheduled loop that runs once.

Reads the spine (progress.md), gathers open TODO comments from the repo,
writes a dated summary, and dedupes against what it already recorded so a
second run builds on the first instead of repeating itself.

Usage:
    python morning-brief.py                 # uses ../progress.md as spine
    python morning-brief.py /path/to/summary.md
"""

import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SPINE = Path(__file__).parent.parent / "progress.md"


def read_spine(spine: Path) -> str:
    # Force UTF-8 — Windows default is cp1252 which mangles em-dashes.
    return spine.read_text(encoding="utf-8") if spine.exists() else ""


def collect_todos(repo: Path):
    """Return a list of (relative-path, line-no, text) for every TODO line."""
    todo_re = re.compile(r"\bTODO\b")
    found = []
    for p in sorted(repo.rglob("*.py")):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            if todo_re.search(line):
                found.append((str(p.relative_to(repo)), i, line.strip()))
    return found


def parse_recorded_todos(spine_text: str):
    """Pull the `file:line` keys from the most recent dated brief entry.

    Each line is formatted like `- `project-03/...:42` ...`.
    """
    # Find the last dated entry heading, then read the TODO block beneath it.
    entries = re.findall(
        # Require a real date pattern so stray "## " headings (like "## Done")
        # don't confuse the parser. Handle both CRLF (Windows) and LF line endings.
        r"## \d{4}-\d{2}-\d{2} \d{2}:\d{2} — Morning Brief\r?\n\r?\n.*?(?=## \d{4}-\d{2}-\d{2}|\Z)",
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
    spine = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SPINE
    repo = spine.parent
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

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

    print(entry)


if __name__ == "__main__":
    main()
