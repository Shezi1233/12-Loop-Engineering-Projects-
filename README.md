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
| 4 | Fix loop with real checker | ✅ Fully verified — good fix PASS+PR, bad fix FAIL |
| 5 | Codify the body | ✅ Fully verified — 2 candidates, both PASS |
| 6 | Doorbell loop | ✅ Fully verified — pytest fails, reviewer detects planted bug |
| 7 | Break it on purpose | ✅ Fully verified — measure/sabotage/diagnose all work |
| 8 | Daily loop capstone | ✅ Fully verified — engine runs, PASS verdict |
| 9 | Rehearse routine free | ✅ Fully verified — success and fail transcripts correct |
| 10 | Secrets drill | ✅ Fully verified — both env-file and env-var modes work |
| 11 | Two-routine gate | ✅ Fully verified — Routine A drafts, Routine B publishes |
| 12 | Dreaming loop | ✅ Fully verified — finds repeated failures, drafts PR |

## Bugs fixed during testing (all verified)

1. **Project 3, 7 (morning-brief.py):** Windows cp1252 mangling em-dash. Fixed: forced `encoding="utf-8"` on all file reads. Regex now uses `\r?\n` for CRLF.
2. **Project 4 (buggy-math.py → buggy_math.py):** Hyphenated filename is not importable as a Python module. Fixed: renamed to underscore, updated all code references.
3. **Project 4 (implementer.py):** Regex `\s*$` ate trailing newlines, making diff non-minimal. Fixed: used lookahead `(?=[ \t]*\n)` to anchor only to end-of-line.
4. **Project 4 (reviewer.py):** `git diff` showed no changes (fix was already committed). Fixed: `git diff main -- file` compares branch vs main.
5. **Project 4 (reviewer.py):** `+` replacement lines were counted as "other changes". Fixed: separate counter for removed/added lines.
6. **Project 4 (fix-loop.py):** Didn't checkout the implementer's branch before reviewer ran. Fixed: added `git checkout branch` after implementer.
7. **Project 5, 8 (engine.py / reviewer.py):** Same hyphenated filename bug as Project 4. Fixed: renamed to underscore.
8. **Project 8 (daily-lint-engine.py):** Syntax error (unclosed string). Fixed: closed string properly. Dead code removed.
9. **Project 8 (implementer.py):** Tuple unpacking from subprocess.run (not unpackable). Fixed: removed the broken code, kept the correct subprocess call.
10. **Project 8 (reviewer.py):** Compared working-tree diff vs HEAD (uncommitted changes). Fixed: `git diff main --` to compare against base branch.
11. **Project 12 (dreaming-loop.py):** No encoding specified when reading spine. Fixed: `encoding="utf-8"` on read_text().
12. **Projects 4, 5, 8, 11:** Each project required `git init` + `main` branch to be set up locally (no remote).
