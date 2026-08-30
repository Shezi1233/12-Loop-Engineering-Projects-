# Project 11 — Build the two-routine gate

**Difficulty:** Medium–Hard (1–2 hrs)
**Concept:** Routine drill — maker-checker gate

## Goal

Build: Routine A (one-off schedule) drafts something reviewable (a branch or
summary). Routine B has an API trigger and does one small follow-up action.
Review A's draft yourself, then approve by firing B manually.

## Done when

- B only ran because you fired it
- B's transcript shows the action happened
- Connectors/permissions are locked down

## Skills used

- Two-routine gate: A drafts, B publishes — A runs on a one-off, B on an API trigger
- API trigger as the "gate" (HTTP endpoint, GitHub `workflow_dispatch`)
- Permission lockdown: B can only commit to `release-notes/*` branches
- Manual approval workflow: review the draft, then fire B yourself

## How to run

```bash
cd project-11-two-routine-gate

# 1. Run Routine A — drafts release notes
python routine-a.py
# → creates branch release-notes/draft-<ts>
# → writes release-notes-draft.md
# → "DRAFT READY"

# 2. Review the draft
cat release-notes-draft.md

# 3a. Fire Routine B directly (local)
python routine-b.py
# → creates branch release-notes/final-<ts>
# → writes release-notes-final.md
# → tags the commit
# → "PUBLISHED"

# OR 3b. Fire Routine B via the local API trigger
python api-server.py                        # starts on :8765
# In another terminal:
curl -X POST http://localhost:8765/publish

# 4. Read Routine B's transcript — proves YOU fired it
cat .transcripts/routine-B-*.md
```

## Why two routines, not one

Routine A drafts (low risk, no side effects beyond a branch).
Routine B publishes (commits, tags — visible side effects).

If you combined them, you'd auto-publish every draft. Separating them
means **nothing publishes without a human reviewing the draft and firing
Routine B manually**.

## Permissions / Connectors (locked down)

- `git commit` and `git tag` only on `release-notes/*` branches
- No external API calls
- GitHub Actions: `contents: write` for the workflow
- Local API server: only `POST /publish`, only on `127.0.0.1`

## Files

| File | Purpose |
|------|---------|
| `routine-A-draft.md` | Routine A's prompt (the draft task) |
| `routine-B-follow-up.md` | Routine B's prompt (the publish task) |
| `routine-a.py` | Routine A's body (one-off, schedules nothing) |
| `routine-b.py` | Routine B's body (API-triggered) |
| `api-server.py` | Tiny HTTP server: `POST /publish` runs Routine B |
| `.github/workflows/routine-b-trigger.yml` | GitHub `workflow_dispatch` trigger for Routine B |

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-11-two-routine-gate
# Setup git
git init && git add . && git commit -m "initial" && git checkout -b main

# 1. Run Routine A
python routine-a.py
# → branch: release-notes/draft-<ts>
# → writes release-notes-draft.md
# → DRAFT READY

# 2. Review
cat release-notes-draft.md

# 3a. Fire Routine B directly
python routine-b.py
# → branch: release-notes/final-<ts>
# → writes release-notes-final.md
# → tags commit
# → PUBLISHED

# OR 3b. Fire via API trigger
python api-server.py
# In another terminal:
curl -X POST http://localhost:8765/publish

# 4. Read Routine B's transcript
cat .transcripts/routine-B-*.md
# → proves YOU fired it
```