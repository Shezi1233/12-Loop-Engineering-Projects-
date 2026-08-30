# Project 5 — Codify the body

**Difficulty:** Medium–Hard (1–1.5 hrs)
**Concept:** Reusable workflow/script (builds on Project 4)

## Goal

Build: Take Project 4's orchestration and turn it into ONE re-runnable
unit/script (a `for` loop over candidates with fan-out + wait, reviewer
exit code as the checker). Run it twice.

## Done when

- One command runs the whole draft-and-review body with no step-by-step prompting.
- You prove a fresh session/shell remembers nothing from the last run (it's an
  engine, not a loop, until it has a heartbeat + progress file).

## Skills used

- Engine vs loop distinction: engine is stateless, run-anywhere
- Fan-out + wait pattern (`ThreadPoolExecutor` + `as_completed`)
- Reviewer exit code as the success predicate
- State lives in: spine (`progress.md`), git branches, and `.runs/<run-id>/`
- Heartbeat file per run; spine entry per run

## How to run

```bash
cd project-05-codify-the-body

# 1. First run — 2 candidates, both should PASS
python engine.py
# → checks 2 candidates, writes to spine, creates .runs/run-<ts>/

# 2. Inspect the spine
cat ../progress.md

# 3. Reset for a clean second run
git checkout main

# 4. Second run with 3 candidates
python engine.py --candidates 3
# → 3 candidates, new run dir, new spine entry

# 5. Prove freshness — engine has no in-memory state
python engine.py --prove-fresh
# → writes .runs/<ts>/freshness.txt proving globals have no list state
```

**Key teaching point:** This is an ENGINE, not a loop. The "loop" is implicit
in whoever calls `engine.py` (cron, GitHub Actions, a parent agent). The
engine itself has no `while True` — it runs once, exits, leaves a heartbeat
file (`.runs/<run-id>/`) and a spine entry. A fresh shell running it again
sees no state from the first run.

## Why it's an engine not a loop

- No `while True` — exits after one pass
- Max candidates = 5 (heartbeat limit)
- Run artifacts in `.runs/<run-id>/` (heartbeat)
- Each run appends to `../progress.md` (spine)
- A fresh `python engine.py` invocation sees zero in-memory state

## GitHub Actions (optional)

```yaml
on: { workflow_dispatch: {} }
jobs:
  codify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd project-05-codify-the-body && python engine.py
```

## Test Status

⚠️ **NOT YET TESTED — depends on Project 4 being fixed first**

**Requires:** Project 4 git repo fix + `conftest.py` (added, see Project 4 status)

**To verify (next session):**
```bash
cd project-05-codify-the-body
# Confirm git state
git branch              # should show: * main
git log --oneline      # should show 1 commit

# Run engine
python engine.py
# → phase 1: fan out implementers
# → phase 2: fan out reviewers
# → phase 3: aggregate
# → writes to ../progress.md

# Verify freshness
python engine.py --prove-fresh
# → writes .runs/<ts>/freshness.txt

# Second run (fresh shell) should behave identically
```