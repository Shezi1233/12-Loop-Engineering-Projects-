# Project 12 — Build a dreaming loop (final capstone)

**Difficulty:** Capstone (2–3 hrs)
**Concept:** Builds on Project 3 or 8 — weekly reflection loop

## Goal

Build: Needs a loop that's already run for a week with dated entries in
`progress.md` (from Project 3 or 8). Build a second, weekly-scheduled loop
that reads all log entries since its own `dreaming-state.md` date, finds any
repeated failure/correction, and drafts the smallest rules-file/skill change
to prevent it — as a PR (never a direct commit) citing its evidence. It
should also propose one deletion (a rule no recent run needed).

## Done when

- The PR's proposed change traces to real cited log entries
- A deliberately planted repeated failure gets caught
- Nothing changes without you merging it
- State persistence confirmed: repeated-failure count is stable across runs

## Skills used

- Weekly reflection loop (reads its own state file: `dreaming-state.md`)
- Pattern detection: bucketing failures by reason, finding repeats
- Evidence citation: every proposed change links to specific log entries
- PR-as-output (never direct commit) so a human always reviews
- Deletion proposal: rules no recent run needed

## How to run

```bash
cd project-12-dreaming-loop

# (Optional) Plant a repeated failure pattern to demo the loop
python setup-repeated-failures.py
# → adds 3 dated entries to ../progress.md with the same FAIL reason

# Dry-run: scan progress.md, report, don't create a PR
python dreaming-loop.py --dry-run    # explicit
python dreaming-loop.py              # also dry-run (default for safety)
# → finds 3 repeated failures
# → drafts rule change + deletion, prints the draft
# → progress.md entry: verdict: DRY_RUN, pr: none

# Live mode: actually create a PR
python dreaming-loop.py --live
# → creates branch: claude/dreaming-<ts>
# → commits proposed-rule-change.md to that branch
# → writes pr-body.md with evidence citations
# → progress.md entry: verdict: PR_OPENED, pr: branch: claude/dreaming-<ts>
# → prints: "gh pr create --base main --head <branch> --body-file pr-body.md"

# Reset state (forces full re-scan of all progress.md entries)
python dreaming-loop.py --reset-state
```

### Live vs dry-run mode

| Flag | What it does |
|------|-------------|
| (none) / `--dry-run` | Scans and reports; `pr: none` in progress.md |
| `--live` | Creates `claude/` branch, commits, cites evidence, logs `pr: branch: …` |

The default is **dry-run** so a casual `python dreaming-loop.py` call never
produces a real PR. Use `--live` intentionally when you want the PR.

## Files

| File | Purpose |
|------|---------|
| `dreaming-loop.py` | The weekly reflection engine |
| `setup-repeated-failures.py` | Plants 3 dated FAIL entries to demo the loop |
| `.github/workflows/dreaming.yml` | Weekly cron (04:00 UTC Sunday) + manual |
| `dreaming-state.md` | Tracks "last run" date; filters entries on next run |
| `proposed-rule-change.md` | Draft skill change (written in live mode) |
| `pr-body.md` | PR description body (written in live mode) |

## Why "PR, never commit"

The dreaming loop proposes changes to *itself* and to other skills. It must
not be able to merge those changes without a human reading them first.
That's why the output is a PR — you read the evidence, you decide to merge.

## State persistence

`dreaming-state.md` records the last-checked timestamp. Each run:
1. Reads the marker
2. Only processes `progress.md` entries newer than the marker
3. Writes the new marker back before exiting

This prevents the same repeated-failure pattern from being reported multiple
times. Use `--reset-state` to force a full re-scan.

## Test Status

✅ **FULLY VERIFIED**

Verified (2026-08-30):
1. Reset state (`--reset-state`), run with no repeated failures → `verdict: NO_REPEATED_FAILURE`, `pr: none`
2. Planted 3 repeated failures, ran `--live` → created `claude/` branch, `proposed-rule-change.md`, `pr-body.md` with evidence citations, logged `pr: branch: claude/dreaming-<ts>` in progress.md
3. Ran 2 more times with no new failures → count stayed stable (state correctly persisted)

Bugs fixed during verification:
- `open_pr()` now creates a `claude/` branch (not a direct commit to main) and cites evidence in the PR body
- `--reset-state` flag added for manual state control
- `find_repeated_failures()` now skips Dreaming Loop entries (which contain "FAIL" in their own status reports)
