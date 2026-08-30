# Project 8 — Your own daily loop (capstone)

**Difficulty:** Capstone (2–4 hrs)
**Concepts:** Full 6-part loop (heartbeat, worktree, skill, maker-checker, connector, spine)

## Goal

Build: Pick one real recurring chore (dependency audit, docs-freshness check,
changelog draft, lint sweep). Build the FULL 6-part loop: heartbeat, worktree,
skill, maker-checker, connector, spine. Add budget guards.

## Done when

It runs unattended for a week and you trust what it ships because you read
it, not because you stopped reading.

## The 6 parts (this project)

| # | Part | File |
|---|------|------|
| 1 | Heartbeat (max-runtime cap) | `heartbeat-wrapper.sh` |
| 2 | Worktree (fresh branch per run) | `daily-lint-engine.py` |
| 3 | Skill (fix procedure) | `skill-lint-fix.md` |
| 4 | Maker-checker (implementer + reviewer) | `implementer.py`, `reviewer.py` |
| 5 | Connector (push + open PR on PASS only) | `connector.py` |
| 6 | Spine (dated entry to `progress.md`) | `append_spine()` in engine |

## The recurring chore: lint sweep

Each beat:
1. Pulls the current `target.py`
2. Runs the test suite
3. Drafts fixes in a fresh branch `daily-lint-<ts>`
4. Has the reviewer grade the diff
5. If PASS → push branch + simulate PR open
6. If FAIL → discard branch + log
7. Append a dated entry to the spine

## Budget guards

- `MAX_ATTEMPTS=5` (max fix attempts inside the engine)
- `MAX_SECONDS=300` (engine hard cap; 5 min if run directly)
- `MAX_SECONDS=1800` (heartbeat wrapper default; 30 min)
- `timeout-minutes: 30` in the GitHub Actions workflow

## How to run

```bash
cd project-08-daily-loop-capstone

# 1. Verify tests pass with the current target
python -m pytest -q                    # expect: 5 passed

# 2. Run the engine once (one pass, exits)
python daily-lint-engine.py
# → creates branch daily-lint-<ts>
# → implementer runs
# → reviewer grades
# → if PASS: push + simulate PR; if FAIL: discard

# 3. Run via heartbeat wrapper (the real "loop" driver)
chmod +x heartbeat-wrapper.sh
./heartbeat-wrapper.sh
# → enforces 30-min wall-clock cap
# → writes heartbeat + spine entry regardless of outcome

# 4. Inspect the spine
cat ../progress.md
# → look for "## YYYY-MM-DD HH:MM — Daily Lint Sweep"
```

## GitHub Actions

`.github/workflows/daily-lint.yml` runs the engine daily at 06:00 UTC.
Budget: 30 minutes per run. No real tokens needed for the throwaway repo.

## Test Status

⚠️ **PARTIALLY TESTED — needs git init**

**Verified:**
- `target.py` + `test_target.py`: pytest shows 5 passed ✅
- `conftest.py` added ✅ (makes `target` module importable for pytest)

**Needs setup (next session):**
- Git repo needs to be initialized in this project folder
- Run `git init && git add . && git commit -m "initial" && git checkout -b main`

**To verify (next session):**
```bash
cd project-08-daily-loop-capstone
# Setup git
git init && git add . && git commit -m "initial" && git checkout -b main

# Verify tests
python -m pytest -q           # expect: 5 passed

# Run engine
python daily-lint-engine.py  # one pass, exits

# Check spine
cat ../progress.md
```