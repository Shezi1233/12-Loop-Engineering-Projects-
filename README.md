# Loop Engineering Practice

Throwaway repository for the "Loop Engineering" crash course from *The AI Agent Factory* by The AI Agent Factory.

12 project folders — one per project — each self-contained and independently runnable.

## Index

| # | Folder | Difficulty | Summary |
|---|--------|------------|---------|
| 1 | `project-01-watch-loop` | Easy (15–30 min) | In-session loop that watches a long task and notifies when it finishes |
| 2 | `project-02-tests-pass-then-stop` | Easy–Medium (30–45 min) | Conditional loop that keeps working until tests pass, capped at 6 tries |
| 3 | `project-03-morning-brief-memory` | Medium (45–60 min) | Scheduled loop that reads `progress.md`, gathers repo info, writes a summary |
| 4 | `project-04-fix-loop-real-checker` | Medium–Hard (1–2 hrs) | Maker-checker loop with a real reviewer that grades fixes |
| 5 | `project-05-codify-the-body` | Medium–Hard (1–1.5 hrs) | Reusable script that wraps the draft-and-review body from Project 4 |
| 6 | `project-06-doorbell-loop` | Medium (45–60 min) | Event-driven loop that auto-reviews pull requests on trigger |
| 7 | `project-07-break-it-on-purpose` | Medium (45–60 min) | Observability + cost: measure a beat, extrapolate, then sabotage and diagnose |
| 8 | `project-08-daily-loop-capstone` | Capstone (2–4 hrs) | Full 6-part loop (heartbeat, worktree, skill, maker-checker, connector, spine) |
| 9 | `project-09-rehearse-routine-free` | Easy (20–30 min) | One-off routine drill — fire, read transcript, change prompt, fire again |
| 10 | `project-10-secrets-drill` | Easy–Medium (30–45 min) | Routine drill: `.env` vs environment variables for credentials |
| 11 | `project-11-two-routine-gate` | Medium–Hard (1–2 hrs) | Two routines: one drafts, one runs on API trigger after manual approval |
| 12 | `project-12-dreaming-loop` | Capstone (2–3 hrs) | Weekly loop that reads logs, finds repeated failures, drafts a rules PR |

## Usage

Each project folder contains its own `README.md` with goal, difficulty, skills used, "done when" criteria, and **Test Status** (what's been verified so far), plus working starter code.

Clone or open the folder, read the project README, and follow its instructions.

## Test Status (overall)

| # | Project | Status |
|---|---------|--------|
| 1 | Watch loop | ✅ Fully verified |
| 2 | Tests pass then stop | ✅ Fully verified |
| 3 | Morning brief with memory | ✅ Fully verified (after UTF-8 + CRLF fixes) |
| 4 | Fix loop with real checker | ⚠️ Code fixed, needs re-test (git init done, conftest.py added) |
| 5 | Codify the body | ⚠️ Depends on Project 4 git state |
| 6 | Doorbell loop | ⚠️ Not yet tested |
| 7 | Break it on purpose | ⚠️ Not yet tested |
| 8 | Daily loop capstone | ⚠️ Tests pass (5/5), needs git init + engine run |
| 9 | Rehearse routine free | ⚠️ Not yet tested |
| 10 | Secrets drill | ⚠️ Not yet tested |
| 11 | Two-routine gate | ⚠️ Not yet tested, needs git init |
| 12 | Dreaming loop | ⚠️ Not yet tested, needs git init in root |

## Bugs fixed during initial testing (next session — re-verify)

1. **Project 3 (morning-brief.py):** Windows cp1252 default encoding was mangling the em-dash (—) in the regex. Fixed by forcing `encoding="utf-8"` on all file reads. Also changed regex to use `\r?\n` for Windows CRLF line endings.
2. **Project 4 (implementer.py):** Used Unix `date` command which doesn't exist on Windows. Fixed by using Python's `time.time()`. Git repo initialized in project folder (`main` branch created, master deleted).
3. **Project 4, 5, 6, 8:** Added `conftest.py` to each project that needs it — makes local modules importable for pytest (otherwise `from buggy_math import ...` fails with `ModuleNotFoundError`).

## To resume testing (next session)

Start with Project 4 (the dependency point). If Project 4 works, Projects 5 and 8 will be unblocked. The other projects (6, 7, 9, 10, 11, 12) don't depend on earlier ones and can be tested in any order.

Each project README has a "Test Status" section at the bottom with the exact commands to run.
