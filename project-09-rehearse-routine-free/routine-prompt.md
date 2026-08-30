# Routine: Summarize Yesterday's Commits

## Task
Look at the git log of THIS REPO and produce a short summary of yesterday's
commits (or the last 24 hours). Write the summary to a new file called
`yesterday-summary.md` at the repo root.

## Constraints
- Read the actual git log, not your memory.
- Keep the summary under 200 words.
- Don't change any other files.
- If there are no commits in the last 24 hours, say so explicitly.

## Output
1. The summary text
2. The new file `yesterday-summary.md` at the repo root
3. Print "DONE" when finished

## How this works in a real Routine

This is the body of a one-off Routine. In Claude Code, a Routine is a
scheduled or triggered invocation. The "transcript" is what the model says +
what tools it calls + their outputs. You see the full transcript after a
run finishes.

In this project, we simulate the body in a single script and write a fake
"transcript" so you can read it like a real run log.