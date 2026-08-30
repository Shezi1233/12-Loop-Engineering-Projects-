# Routine B: Publish the Approved Draft

## Trigger
This routine has an API trigger. It only runs when YOU fire it manually
(curled endpoint, GitHub Actions `workflow_dispatch`, etc.) AFTER you have
reviewed Routine A's draft.

## Task
1. Read `release-notes-draft.md` from the repo root.
2. Verify it exists and is non-empty.
3. Move it to `release-notes-final.md` (the "approved" version).
4. Commit on a new branch `release-notes/final-<ts>` and tag the commit.
5. Print "PUBLISHED" when finished.

## Why this needs an API trigger, not a schedule
Routine B is a SIDE EFFECT — it commits and tags. You don't want it firing
on a schedule; you want it firing ONLY when you've reviewed A's draft and
decided to publish. That's why it's an API trigger, not a cron.

## Permissions / Connectors
- `git commit` and `git tag` only
- `git push` is OPTIONAL (only on user request)
- No external API calls
- Locked to: only the one branch (release-notes/*)