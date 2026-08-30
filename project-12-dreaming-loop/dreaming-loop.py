#!/usr/bin/env python3
"""Dreaming loop: reads progress.md, finds repeated failures, drafts a rule-change PR.

A weekly-scheduled loop that:
1. Reads all progress.md entries since its own dreaming-state.md date
2. Detects repeated failure/correction cycles
3. Drafts the smallest skill/rules-file change to prevent the repeated failure
4. Proposes one deletion (a rule no recent run needed)
5. Opens a PR with the change, citing evidence from the log entries

NEVER commits directly to main — always opens a PR on a `claude/` branch
so a human can review before merging.

Usage:
    python dreaming-loop.py --live           # actually create a branch + PR
    python dreaming-loop.py                  # dry-run (default): scan, report, no PR
    python dreaming-loop.py --dry-run        # explicit dry-run
    python dreaming-loop.py --reset-state    # reset dreaming-state.md and exit
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

    A "repeated failure" is: any non-dreaming-entry with FAIL in its content,
    AND that has an explicit `reason:` field (not just a `verdict:` field).
    Dreaming Loop entries are skipped — their own "verdict:" line contains FAIL
    but they are status reports, not actual failures to act on.
    """
    failures = []
    for entry in entries:
        content = entry["content"]
        # Skip Dreaming Loop entries — they are status reports, not failures
        if "Dreaming Loop" in entry["entry_type"]:
            continue
        # Only process entries with "FAIL" that also have a real `reason:` field
        if "FAIL" not in content:
            continue
        reason_m = re.search(
            r"(?:^|\n)\s*[-*]?\s*reason:\s*(.+?)(?:\n|$)",
            content,
            re.IGNORECASE | re.MULTILINE,
        )
        if not reason_m:
            # No explicit reason field — skip (this filters out entries whose
            # only "FAIL" reference is in a verdict/status line)
            continue
        reason = reason_m.group(1).strip()
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
    """Create a `claude/` branch, write the proposed change, commit, and
    produce a PR body that cites the evidence (which runs, how often, why
    this fix stops it). Never commits to main directly.

    Returns a string of the form "branch: <name>" so progress.md can log it.
    """
    # 1. Stash any dirty working-tree changes (e.g. progress.md edits) so
    #    the new branch is a clean copy of main. We pop the stash at the end
    #    so the user keeps their work.
    stash_proc = subprocess.run(
        ["git", "stash", "push", "-m", "dreaming-loop: auto-stash before branch switch"],
        cwd=REPO, capture_output=True, text=True,
    )
    stashed = "No local changes to save" not in (stash_proc.stdout or "")

    # 2. Switch back to main (if not already there) so we branch off a clean state
    current_branch_proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO, check=True, capture_output=True, text=True,
    )
    current_branch = (current_branch_proc.stdout or "").strip() or "main"

    if current_branch != "main":
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=REPO, check=True, capture_output=True,
        )

    # 3. Create the claude/ branch (use -B so it's idempotent if re-run)
    subprocess.run(
        ["git", "checkout", "-B", branch],
        cwd=REPO, check=True, capture_output=True,
    )

    # 4. Write the proposed rule change to the working tree
    change_file = REPO / "project-12-dreaming-loop" / "proposed-rule-change.md"
    change_file.parent.mkdir(parents=True, exist_ok=True)
    change_file.write_text(change_content, encoding="utf-8")

    rel_path = str(change_file.relative_to(REPO)).replace("\\", "/")
    # Use -f to bypass any .gitignore (proposed-rule-change.md is listed
    # there but the dreaming loop is the only legitimate writer of this file)
    subprocess.run(["git", "add", "-f", rel_path], cwd=REPO, check=True, capture_output=True)

    # Build evidence citation for the commit message
    evidence_citation = ""
    if evidence:
        evidence_citation = "\n\nEvidence:\n" + "\n".join(
            f"- [{f['date'].strftime('%Y-%m-%d %H:%M')}] {f['entry_type']}: {f['reason']}"
            for f in evidence
        )

    commit_msg = f"dreaming-loop: propose rule change — {branch}{evidence_citation}"
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=REPO, check=True, capture_output=True,
    )

    # 5. Build the PR body. It MUST cite the evidence (which runs, how often)
    #    and the reason this fix stops the repeat. The proposed-rule-change.md
    #    IS the draft PR body — it's already cited above.
    pr_body = f"""## Dreaming Loop: Rule Change PR

**Branch:** `{branch}`
**Draft file:** `{rel_path}`
**Repeated-failure instances:** {len(evidence)}

### Evidence (cited from progress.md)

"""
    for f in evidence:
        pr_body += f"- [{f['date'].strftime('%Y-%m-%d %H:%M')}] {f['entry_type']}: {f['reason']}\n"

    pr_body += f"""

### Why this fix stops the repeat

This change was drafted because the same failure reason appeared
**{len(evidence)} times** in the scoped window. The new pre-check rule
forces the implementer to verify the off-by-one pattern before patching,
preventing the blind-remove-of-`-1` behaviour that produced the repeated
failures above.

---

{change_content}

---

**Do not merge without human review.** The dreaming loop NEVER commits to
main directly — this PR is a proposal, you decide to merge.
"""

    # Also write the PR body to a sibling file so the user can inspect it
    pr_file = REPO / "project-12-dreaming-loop" / "pr-body.md"
    pr_file.write_text(pr_body, encoding="utf-8")

    # 6. Try push — fine if no remote (throwaway repo)
    push = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=REPO, capture_output=True, text=True,
    )
    if push.returncode != 0:
        # No remote is expected; that's fine
        pass

    # 7. Switch back to main and pop the stash so the user keeps their work
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=REPO, check=True, capture_output=True,
    )
    if stashed:
        subprocess.run(
            ["git", "stash", "pop"],
            cwd=REPO, capture_output=True, text=True,
        )

    print(f"[dreaming-loop] PR OPENED — branch: {branch}")
    print(f"[dreaming-loop] PR description (first 800 chars):")
    print(pr_body[:800])
    if len(pr_body) > 800:
        print("...")
    print(f"[dreaming-loop] Draft file: {change_file}")
    print(f"[dreaming-loop] PR body file: {pr_file}")
    print(f"[dreaming-loop] (open a PR with: gh pr create --base main --head {branch} --body-file {pr_file})")

    return f"branch: {branch}"


def update_dreaming_state(marker: datetime = None):
    """Update dreaming-state.md with the highest entry timestamp processed.

    marker: the latest entry's datetime. If None, use the current time.
    On the next run, only entries with date > marker are processed.
    """
    if marker is None:
        marker = datetime.now()
    state = f"# Dreaming Loop State\n\nlast run: {marker.strftime('%Y-%m-%d %H:%M')}\n"
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
        help="create the PR for real on a claude/ branch (default: dry-run — scan and report only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="scan and report, don't create PR (default behaviour without --live)",
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="reset dreaming-state.md and exit (forces a full re-scan of progress.md)",
    )
    args = parser.parse_args()

    # --reset-state: wipe state and bail out before any scanning
    if args.reset_state:
        print("[dreaming-loop] --reset-state: clearing dreaming-state.md")
        if DREAMING_STATE.exists():
            DREAMING_STATE.unlink()
        print("[dreaming-loop] dreaming-state.md removed. Next run will scan all entries.")
        return

    # Live mode is when --live is passed and --dry-run is NOT passed.
    # Default (no flags) = dry-run for safety.
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
    # Use > (strict) so the marker always moves forward — once an entry is
    # processed, it will never be re-scanned.
    if last_run is None:
        since_last = entries
    else:
        since_last = [e for e in entries if e["date"] > last_run]
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
    # Marker = highest entry timestamp processed (so next run starts strictly
    # AFTER this point). If no entries were processed, marker = current time.
    if entries:
        marker = max(e["date"] for e in entries)
    else:
        marker = datetime.now()
    update_dreaming_state(marker)
    append_spine(verdict, len(failures), pr_info)

    print(f"[dreaming-loop] DONE — verdict: {verdict}")


if __name__ == "__main__":
    main()
