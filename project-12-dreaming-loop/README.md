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

## Skills used

- Weekly reflection loop (reads its own state file: `dreaming-state.md`)
- Pattern detection: bucketing failures by reason, finding repeats
- Evidence citation: every proposed change links to specific log entries
- PR-as-output (never direct commit) so a human always reviews
- Deletion proposal: rules no recent run needed

## How to run

```bash
cd project-12-dreaming-loop

# 1. (Optional) Plant a repeated failure pattern to demonstrate the loop
python setup-repeated-failures.py
# → adds 3 dated entries to ../progress.md with the same FAIL reason

# 2. Run the dreaming loop (dry-run first)
python dreaming-loop.py --dry-run
# → reads progress.md
# → finds 3 repeated failures
# → drafts a rule change + a deletion
# → prints the proposed PR body

# 3. Run for real (creates a branch + simulated PR)
python dreaming-loop.py
# → branch: dreaming/propose-rule-<ts>
# → commits proposed-rule-change.md
# → "PR would be opened" (simulated locally)

# 4. Inspect the proposal
cat proposed-rule-change.md
```

**The dreaming loop:**
- Reads all `progress.md` entries since its last `dreaming-state.md` date
- Buckets failures by reason, finds any with ≥2 occurrences
- Drafts a small skill-file change to prevent the most-repeated failure
- Proposes one deletion (a rule no recent run needed)
- Opens a PR (never commits to main)
- Updates its own state file so the next run only sees new entries

## Files

| File | Purpose |
|------|---------|
| `dreaming-loop.py` | The weekly reflection engine |
| `setup-repeated-failures.py` | Plants 3 dated FAIL entries to demo the loop |
| `.github/workflows/dreaming.yml` | Weekly cron (04:00 UTC Sunday) + manual |
| `dreaming-state.md` | Created on first run; tracks "last run" date |

## Why "PR, never commit"

The dreaming loop proposes changes to *itself* and to other skills. It must
not be able to merge those changes without a human reading them first.
That's why the output is a PR — you read the evidence, you decide to merge.

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-12-dreaming-loop
# Setup git (in root, since dreaming-loop reads parent progress.md)
cd ..
git init && git add . && git commit -m "initial" && git checkout -b main
cd project-12-dreaming-loop

# 1. Plant repeated failures to demonstrate
python setup-repeated-failures.py
# → adds 3 dated FAIL entries to ../progress.md

# 2. Dry run
python dreaming-loop.py --dry-run
# → finds 3 repeated failures
# → drafts rule change + deletion
# → prints PR body (no push)

# 3. Real run
python dreaming-loop.py
# → branch: dreaming/propose-rule-<ts>
# → commits proposed-rule-change.md
# → "PR would be opened"

# 4. Inspect the proposal
cat proposed-rule-change.md
```