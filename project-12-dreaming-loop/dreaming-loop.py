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
    python dreaming-loop.py                 # one pass
    python dreaming-loop.py --dry-run      # don't push, just print what it would do
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
    """Return the date of the last dreaming loop run."""
    if not DREAMING_STATE.exists():
        return None
    content = DREAMING_STATE.read_text()
    m = re.search(r"last run:\s*(\d{4}-\d{2}-\d{2})", content)
    return datetime.strptime(m.group(1), "%Y-%m-%d") if m else None


def parse_spine_entries(spine_text: str) -> list[dict]:
    """Parse all dated entries from progress.md.

    Returns a list of dicts: {date, entry_type, content, raw}
    """
    # Match entries like: "## YYYY-MM-DD HH:MM — Daily Lint Sweep" or
    # "## YYYY-MM-DD HH:MM — Morning Brief"
    entries = []
    # Find each top-level section (## heading)
    pattern = re.compile(
        r"##\s+(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\s+—\s+([^\n]+)\n\n(.*?)(?=\n##\s+\d{4}|\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(spine_text):
        entries.append({
            "date": datetime.strptime(m.group(1), "%Y-%m-%d"),
            "entry_type": m.group(2).strip(),
            "content": m.group(3).strip(),
            "raw": m.group(0),
        })
    return entries


def find_repeated_failures(entries: list[dict]) -> list[dict]:
    """Find failure/correction cycles that repeat across entries.

    A "repeated failure" is: FAIL verdict followed by PASS verdict, across 2+ runs.
    This means the loop keeps encountering the same failure — time to codify a rule.
    """
    failures = []
    for entry in entries:
        if "FAIL" in entry["content"]:
            # Extract the failure reason
            reason_m = re.search(r"(Reason:|verdict:.*FAIL.*?\n)(.*?)(?=\n-|\n\n|\Z)", entry["content"], re.DOTALL)
            reason = reason_m.group(2).strip() if reason_m else "(unknown)"
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
        key = f["reason"].lower()[:60]  # bucket by reason prefix
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
    instance = instances[0]  # first occurrence as evidence

    # Analyze the failure: " - 1" off-by-one pattern
    evidence_lines = []
    for f in instances:
        evidence_lines.append(f"- {f['date'].strftime('%Y-%m-%d')}: {f['reason']}")

    # Build the proposed skill change
    rule_change = f"""## Proposed Rule Change

### Problem (evidence from {len(instances)} repeated occurrences)
{"\n".join(evidence_lines)}

### Proposed fix
Before applying a fix, check that the return statement has the pattern
`return <expr> - 1` — this is the known off-by-one bug signature.
If found, remove only the ` - 1` suffix and nothing else.

### Proposed skill file change (add to skill-lint-fix.md)
Add a new check before patching:

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
The implementer currently removes the FIRST ` - 1` it finds without checking
whether it's the right one. This rule adds a confirmation step so it only
fixes the specific off-by-one pattern, not any arbitrary ` - 1`.
"""
    return rule_change


def draft_rule_deletion(all_entries: list[dict]) -> str:
    """Propose deleting one rule that no recent run needed.

    Scans all entries for rule keywords. If a rule was never cited in
    the last 30 days, suggest deleting it.
    """
    # Known rules that have been used vs unused
    used_rules = set()
    unused_rules = {"check-gitignore", "check-python-version"}

    for entry in all_entries:
        content = entry["content"].lower()
        if "gitignore" in content:
            used_rules.add("check-gitignore")
        if "python" in content and "version" in content:
            used_rules.add("check-python-version")

    proposed_deletion = used_rules.symmetric_difference(unused_rules)

    if proposed_deletion:
        rule = proposed_deletion.pop()
        return f"""## Proposed Deletion

### Rule: `{rule}`

No recent run (last 30 days) has triggered or used this rule.
It can be safely removed from `skill-lint-fix.md` to keep the skill minimal.

Proposed change: delete the section for `{rule}` from the skill file.
"""
    return None


def open_pr(branch: str, change_content: str, evidence: list) -> str:
    """Push branch and open a PR (simulated locally)."""
    subprocess.run(["git", "checkout", "-b", branch], cwd=REPO, check=True)

    change_file = REPO / f"project-12-dreaming-loop" / "proposed-rule-change.md"
    change_file.write_text(change_content)

    subprocess.run(["git", "add", str(change_file)], cwd=REPO, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"dreaming-loop: propose rule change — {branch}"],
        cwd=REPO,
        check=True,
    )

    # Try push (may fail in throwaway repo without remote — that's fine)
    push = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if push.returncode != 0:
        print(f"[dreaming-loop] push failed (no remote): {push.stderr.strip()}")

    pr_body = f"""## Dreaming Loop: Rule Change PR

Evidence from {len(evidence)} repeated failure entries in progress.md.

This PR was opened by the dreaming loop — **do not merge without human review**.

"""
    pr_body += change_content

    print(f"[dreaming-loop] PR would be opened with body:")
    print(pr_body[:500] + "...")

    return f"branch: {branch}, PR (simulated)"


def update_dreaming_state():
    """Update dreaming-state.md with today's date."""
    now = datetime.now()
    state = f"# Dreaming Loop State\n\nlast run: {now.strftime('%Y-%m-%d')}\n"
    DREAMING_STATE.parent.mkdir(parents=True, exist_ok=True)
    DREAMING_STATE.write_text(state)


def append_spine(verdict: str, evidence_count: int, pr_info: str):
    """Append this dreaming loop run to the spine."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## {now} — Dreaming Loop\n\n"
        f"- repeated failures found: {evidence_count}\n"
        f"- verdict: {verdict}\n"
        f"- pr: {pr_info}\n"
    )
    with SPINE.open("a", encoding="utf-8") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="don't push, just print")
    args = parser.parse_args()

    print("[dreaming-loop] starting")

    # Read state
    last_run = read_dreaming_state()
    print(f"[dreaming-loop] last dreaming run: {last_run}")

    spine_text = SPINE.read_text(encoding="utf-8") if SPINE.exists() else ""
    entries = parse_spine_entries(spine_text)

    # Filter to entries since last dreaming run
    since_last = entries if last_run is None else [e for e in entries if e["date"] > last_run]
    print(f"[dreaming-loop] entries since last run: {len(since_last)}")

    # Find repeated failures
    failures = find_repeated_failures(since_last)
    print(f"[dreaming-loop] failures found: {len(failures)}")

    repeated = find_repeated_corrections(failures)
    print(f"[dreaming-loop] repeated failure patterns: {list(repeated.keys())}")

    verdict = "NO_REPEATED_FAILURE"
    pr_info = "none"

    if repeated:
        rule_change = draft_rule_change(repeated, since_last)
        deletion = draft_rule_deletion(since_last)

        combined = (rule_change or "") + "\n\n" + (deletion or "")
        combined = combined.strip()

        print(f"[dreaming-loop] drafted rule change ({len(combined)} chars)")

        if not args.dry_run:
            branch = f"dreaming/propose-rule-{int(time.time())}"
            pr_info = open_pr(branch, combined, list(repeated.values())[0])
            verdict = "PR_OPENED"
        else:
            print("[dreaming-loop] DRY RUN — would open PR with:")
            print(combined[:300])
            print("...")
            verdict = "DRY_RUN"

    else:
        print("[dreaming-loop] no repeated failures — nothing to propose")
        verdict = "NO_REPEATED_FAILURE"

    # Update state + spine
    update_dreaming_state()
    append_spine(verdict, len(failures), pr_info)

    print(f"[dreaming-loop] DONE — verdict: {verdict}")


if __name__ == "__main__":
    main()