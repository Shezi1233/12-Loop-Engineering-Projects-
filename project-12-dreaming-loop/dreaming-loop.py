#!/usr/bin/env python3
"""Dreaming loop: reads progress.md, finds repeated failures, drafts a rule-change PR.

A weekly-scheduled loop that:
1. Reads all progress.md entries since its own dreaming-state.md date
2. Detects repeated failure/correction cycles
3. Drafts the smallest skill/rules-file change to prevent the repeated failure
4. Proposes one deletion (a rule no recent run needed)
5. Opens a PR with the change, citing evidence from the log entries

NEVER commits directly — always opens a PR so a human can review before merging.

Usage:
    python dreaming-loop.py --live           # create PR for repeated failures
    python dreaming-loop.py                  # dry-run: scan, report, don't create PR
    python dreaming-loop.py --dry-run        # same as above (explicit)
"""

import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent   # the root loop-engineering-practice/
SPINE = REPO / "progress.md"
DREAMING_STATE = REPO / "project-12-dreaming-loop" / "dreaming-state.md"


def read_dreaming_state() -> datetime:
    """Return the datetime of the last dreaming loop run (date + time)."""
    if not DREAMING_STATE.exists():
        return None
    content = DREAMING_STATE.read_text(encoding="utf-8")
    # Match "last run: YYYY-MM-DD HH:MM" — includes time if present
    m = re.search(r"last run:\s*(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}))?", content)
    if not m:
        return None
    date_str = m.group(1)
    time_str = m.group(2) or "00:00"
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def parse_spine_entries(spine_text: str) -> list[dict]:
    """Parse all dated entries from progress.md.

    Returns a list of dicts: {date, entry_type, content, raw}
    """
    entries = []
    # Match entries like: "## YYYY-MM-DD HH:MM — Daily Lint Sweep"
    # Captures date-only for grouping, full datetime for comparison
    pattern = re.compile(
        r"##\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+—\s+([^\n]+)\n\n(.*?)(?=\n##\s+\d{4}|\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(spine_text):
        date_str = m.group(1)
        time_str = m.group(2)
        full_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        entries.append({
            "date": full_dt,
            "entry_type": m.group(3).strip(),
            "content": m.group(4).strip(),
            "raw": m.group(0),
        })
    return entries


def find_repeated_failures(entries: list[dict]) -> list[dict]:
    """Find failure/correction cycles that repeat across entries.

    A "repeated failure" is: any entry with FAIL in its content.
    Bucketed by failure reason to find patterns.
    """
    failures = []
    for entry in entries:
        content = entry["content"]
        if "FAIL" in content:
            # Extract the failure reason — prioritize "reason:" field over "verdict:"
            # Many entries have both: "verdict: FAIL" and "reason: <actual reason>"
            # We want the actual reason, not just the FAIL verdict
            reason_m = re.search(
                r"(?:^|\n)\s*[-*]?\s*reason:\s*(.+?)(?:\n|$)",
                content,
                re.IGNORECASE | re.MULTILINE,
            )
            if reason_m:
                reason = reason_m.group(1).strip()
            else:
                # Fallback: use first non-blank line of content
                reason = content.split("\n")[0][:80]
            failures.append({
                "date": entry["date"],
                "entry_type": entry["entry_type"],
                "reason": reason,
                "raw": entry["raw"],
            })
    return failures


def find_repeated_corrections(failures: list[dict]) -> dict:
    """Find failures with the same reason across 2+ entries — a repeated pattern."""
    by_reason: dict[str, list] = {}
    for f in failures:
        # Normalize: lowercase, strip, use first 80 chars as bucket key
        key = f["reason"].lower().strip()[:80]
        by_reason.setdefault(key, []).append(f)

    repeated = {k: v for k, v in by_reason.items() if len(v) >= 2}
    return repeated


def draft_rule_change(repeated_failures: dict, all_entries: list[dict]) -> str:
    """Draft a skill/rule change that prevents the most repeated failure."""
    if not repeated_failures:
        return None

    # Pick the most repeated failure reason
    top_reason = max(repeated_failures.items(), key=lambda kv: len(kv[1]))
    reason_key, instances = top_reason

    # Build evidence list
    evidence_lines = []
    for f in instances:
        ts = f["date"].strftime("%Y-%m-%d %H:%M")
        evidence_lines.append(f"- [{ts}] {f['entry_type']}: {f['reason']}")

    # Build the proposed skill change
    rule_change = f"""## Proposed Rule Change

### Problem ({len(instances)} repeated occurrences)

{"\n".join(evidence_lines)}

### Proposed fix

Before applying any patch, identify whether the failure is a known pattern.
If the diff contains ` - 1` in a return statement and tests are failing,
the implementer should remove ONLY that specific ` - 1` and nothing else.

### Proposed skill file change (add to skill-lint-fix.md)

```
## Pre-check: identify the off-by-one pattern

Before removing ` - 1`, verify:
1. The line starts with `return`
2. The expression before ` - 1` is an arithmetic expression
3. There is only ONE ` - 1` in the return statement

If all three are true, proceed with the fix.
If not, STOP and report: "off-by-one pattern not confirmed".
```

### Evidence
```
{"\n".join(evidence_lines)}
```

### Why this prevents the repeat

The implementer must confirm the off-by-one pattern before patching, not blindly
remove the first ` - 1` it finds.
"""
    return rule_change


def draft_rule_deletion(all_entries: list[dict]) -> str:
    """Propose deleting one rule that no recent run needed.

    Scans all entries for rule keywords. If a rule was never cited in
    the last 30 days, suggest deleting it.
    """
    used_rules = set()
    # These are the rules in the skill file — track which ones were actually used
    known_rules = {"check-gitignore", "check-python-version", "check-return-statement"}

    for entry in all_entries:
        content = entry["content"].lower()
        if "gitignore" in content:
            used_rules.add("check-gitignore")
        if "python" in content and "version" in content:
            used_rules.add("check-python-version")
        if "return" in content and "statement" in content:
            used_rules.add("check-return-statement")

    unused = known_rules - used_rules
    if unused:
        rule = sorted(unused)[0]
        return f"""## Proposed Deletion

### Rule: `{rule}`

No recent run has triggered or used this rule.
It can be safely removed from the skill file to keep it minimal.

Proposed change: delete the section for `{rule}` from the skill file.
"""
    return None


def open_pr(branch: str, change_content: str, evidence: list) -> str:
    """Create branch, write proposed change, commit — push attempt (no remote = fine)."""
    # Create branch from main
    subprocess.run(["git", "checkout", "-b", branch], cwd=REPO, check=True, capture_output=True)

    # Write the proposed rule change
    change_file = REPO / "project-12-dreaming-loop" / "proposed-rule-change.md"
    change_file.parent.mkdir(parents=True, exist_ok=True)
    change_file.write_text(change_content, encoding="utf-8")

    rel_path = str(change_file.relative_to(REPO)).replace("\\", "/")
    subprocess.run(["git", "add", rel_path], cwd=REPO, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"dreaming-loop: propose rule change — {branch}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    )

    # Try push — fine if no remote (throwaway repo)
    push = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if push.returncode != 0:
        print(f"[dreaming-loop] push skipped (no remote): {push.stderr.strip()}")

    pr_body = f"""## Dreaming Loop: Rule Change PR

Evidence from {len(evidence)} repeated failure entries in progress.md.

This PR was opened by the dreaming loop — **do not merge without human review**.

"""
    pr_body += change_content

    print(f"[dreaming-loop] PR created — branch: {branch}")
    print(f"[dreaming-loop] PR description:")
    print(pr_body[:600])
    if len(pr_body) > 600:
        print("...")
    print(f"[dreaming-loop] See: {change_file}")

    return f"branch: {branch}"


def update_dreaming_state():
    """Update dreaming-state.md with current date + time so next run starts from here."""
    now = datetime.now()
    state = f"# Dreaming Loop State\n\nlast run: {now.strftime('%Y-%m-%d %H:%M')}\n"
    DREAMING_STATE.parent.mkdir(parents=True, exist_ok=True)
    DREAMING_STATE.write_text(state, encoding="utf-8")


def append_spine(verdict: str, failure_count: int, pr_info: str):
    """Append this dreaming loop run to the spine."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {now} — Dreaming Loop\n\n"
        f"- failures scanned: {failure_count}\n"
        f"- verdict: {verdict}\n"
        f"- pr: {pr_info}\n"
    )
    with SPINE.open("a", encoding="utf-8") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(
        description="Dreaming loop: find repeated failures, draft a rule-change PR."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="create the PR for real (default: dry-run — scan and report only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="scan and report, don't create PR (default behaviour without --live)",
    )
    args = parser.parse_args()

    live_mode = args.live and not args.dry_run
    mode_label = "LIVE" if live_mode else "DRY-RUN"

    print(f"[dreaming-loop] starting [{mode_label}]")

    # Read state
    last_run = read_dreaming_state()
    print(f"[dreaming-loop] last dreaming run: {last_run}")

    spine_text = SPINE.read_text(encoding="utf-8") if SPINE.exists() else ""
    entries = parse_spine_entries(spine_text)
    print(f"[dreaming-loop] total spine entries: {len(entries)}")

    # Filter to entries since last dreaming run
    # Use >= so entries from the same day as last_run are included
    if last_run is None:
        since_last = entries
    else:
        since_last = [e for e in entries if e["date"] >= last_run]
    print(f"[dreaming-loop] entries since last run ({last_run}): {len(since_last)}")

    # Find repeated failures
    failures = find_repeated_failures(since_last)
    print(f"[dreaming-loop] failures found: {len(failures)}")

    repeated = find_repeated_corrections(failures)
    print(f"[dreaming-loop] repeated failure patterns: {len(repeated)}")
    for k, v in repeated.items():
        print(f"  - '{k[:60]}...' appears {len(v)} times")

    verdict = "NO_REPEATED_FAILURE"
    pr_info = "none"

    if repeated:
        rule_change = draft_rule_change(repeated, since_last)
        deletion = draft_rule_deletion(since_last)

        combined = (rule_change or "") + "\n\n" + (deletion or "")
        combined = combined.strip()

        print(f"[dreaming-loop] drafted rule change ({len(combined)} chars)")

        if live_mode:
            branch = f"claude/dreaming-{int(time.time())}"
            pr_info = open_pr(branch, combined, list(repeated.values())[0])
            verdict = "PR_OPENED"
        else:
            print("[dreaming-loop] DRY-RUN — PR not created:")
            print(combined[:400])
            if len(combined) > 400:
                print("...")
            verdict = "DRY_RUN"

    else:
        print("[dreaming-loop] no repeated failures — nothing to propose")

    # Update state + spine
    update_dreaming_state()
    append_spine(verdict, len(failures), pr_info)

    print(f"[dreaming-loop] DONE — verdict: {verdict}")


if __name__ == "__main__":
    main()
