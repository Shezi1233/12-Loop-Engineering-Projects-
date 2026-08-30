# Routine A: Draft a Release Note

## Schedule
One-off (you fire it manually when you want a draft).

## Task
Read the last 5 commits from this repo's git log and draft a release-note
markdown file at `release-notes-draft.md` at the repo root. The file should
be reviewable — clear sections, dated, ready for human review.

## Output
1. The file `release-notes-draft.md` at the repo root
2. Print "DRAFT READY" when finished
3. Commit the file to a branch called `release-notes/draft-<ts>`

## Why this is a Routine, not a loop
Routine A runs ONCE when you fire it. It does not poll, it does not schedule
itself. You trigger it when you have a release to draft for.