# Project 4 — A fix loop with a real checker

**Difficulty:** Medium–Hard (1–2 hrs)
**Concepts:** Maker-checker loop (Concepts 8 + 9 + 11)

## Goal

Build: A short skill file with fix steps, plus a separate reviewer agent that
replies PASS or FAIL. Take one real bug, have an implementer draft a fix in its
own checkout (worktree/branch), let the reviewer grade it. Open a PR only on PASS.

## Done when

- A good fix gets PASS + PR.
- A deliberately bad fix you plant gets FAIL with reasons.

## Skills used

- Maker-checker pattern: separate implementer (drafts) and reviewer (grades)
- Skill file (`skill-fix-bug.md`) encodes the fix procedure
- Real checker: `reviewer.py` runs tests AND validates minimal diff
- Worktree/branch isolation for each fix attempt
- PR only on PASS (simulated locally; GitHub Actions workflow for real PRs)

## How to run

```bash
cd project-04-fix-loop-real-checker

# 1. Confirm tests start failing (the planted bug)
python -m pytest -q
# → test_multiply FAILS

# 2. GOOD fix attempt — should PASS and simulate a PR
python fix-loop.py buggy-math.py
# → implementer creates branch, patches the -1, reviewer says PASS, branch pushed

# 3. BAD fix attempt — should FAIL with reasons
python fix-loop.py buggy-math.py --bad
# → implementer fixes, then we sabotage it, reviewer says FAIL, branch deleted
```

**What the reviewer checks:**
1. Tests pass (`pytest` exit code 0)
2. Diff is minimal — ONLY one ` - 1` removed, nothing else changed

## GitHub Actions

`.github/workflows/fix-loop.yml` runs the reviewer on every PR open/sync.
Add `GITHUB_TOKEN` permissions if you wire it to a real repo (not needed here).

## Test Status

⚠️ **NOT YET FULLY VERIFIED — needs setup + bug fixes**

**Bugs found during testing (fixed in code, needs re-test):**
1. `implementer.py` used Unix `date` command → crashed on Windows. Fixed: replaced with Python `time.time()`
2. Missing `conftest.py` → pytest couldn't import `buggy_math` module. Fixed: added `conftest.py` that adds project root to `sys.path`
3. Git repo not initialized in this project folder → `git checkout -b` failed. **Fixed:** ran `git init`, `git add`, `git commit`, renamed to `main`. Need to verify the fix actually works on re-test.

**Files modified during testing:**
- `implementer.py` — removed broken `date` command, uses `time.time()` instead
- `conftest.py` — NEW: makes `buggy_math` importable for pytest

**To verify (next session):**
```bash
cd project-04-fix-loop-real-checker
# Confirm git state
git branch              # should show: * main
git log --oneline       # should show 1 commit

# Run tests
python -m pytest -q     # should show 1 fail (test_multiply)

# GOOD fix
python fix-loop.py buggy-math.py    # should print "PASS" + simulate PR

# Reset
git checkout main buggy-math.py
git branch -D fix-attempt-*

# BAD fix
python fix-loop.py buggy-math.py --bad   # should print "FAIL" + delete branch
```