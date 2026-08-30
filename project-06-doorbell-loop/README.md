# Project 6 — The doorbell loop

**Difficulty:** Medium (45–60 min)
**Concepts:** Event-driven loop (Concept 7) + connector/permission (Concept 10)

## Goal

Build: Make the repo review its own pull requests automatically on a PR
trigger. Open a PR containing one planted bug (off-by-one or deleted null
check) and wait.

## Done when

- The PR gets a review you never asked for, and it flags the planted bug.

## Skills used

- Event-driven loop (no polling — fires only when a PR opens/syncs)
- GitHub Actions workflow as the "doorbell" listener
- Connector: the workflow posts a review on the PR using `gh pr review`
- Permissions locked down (`pull-requests: write`, no extra scopes)
- Planted bug in `src.py` (`calculate` off-by-one)

## How to run

```bash
cd project-06-doorbell-loop

# 1. Verify the bug causes a test failure
python -m pytest -q
# → test_calculate FAILED

# 2. Local dry-run of the reviewer
python reviewer.py
# → FAIL — found a planted issue

# 3. Wire it to a real GitHub PR to see the doorbell ring:
#    - open a PR with src.py changed
#    - the workflow runs automatically (no one asked)
#    - it posts an APPROVE or REQUEST_CHANGES review
```

**The doorbell is the `on: pull_request:` trigger in the workflow.**
It only fires when something happens (a PR opens/syncs). There is no
polling loop — the repo waits for the event, then reviews itself.

## Permissions

The workflow uses `GITHUB_TOKEN` (scoped to `pull-requests: write`).
No extra tokens. This is a throwaway exercise repo — don't wire it to
your real GitHub orgs without asking.

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-06-doorbell-loop
# Confirm the planted bug
python -m pytest -q       # should show: test_calculate FAILED

# Local reviewer check
python reviewer.py          # should print: FAIL + "tests fail"

# Doorbell dry-run
python doorbell.py --diff-path ./src.py --pr-number 1
# → prints verdict based on planted patterns in the file
```

**GitHub Actions:** `.github/workflows/doorbell.yml` — fires on PR open/sync.
Not wired to any real repo. Needs a real GitHub repo + PR to fully test the
review posting (local dry-run is sufficient for the exercise).