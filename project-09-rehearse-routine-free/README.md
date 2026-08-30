# Project 9 — Rehearse a routine for free

**Difficulty:** Easy (20–30 min)
**Concept:** Routine drill (one-off runs)

## Goal

Build: In a throwaway repo, create a routine whose prompt does one small
checkable thing (e.g. summarize yesterday's commits onto a branch). Fire it
as a one-off run and read the full transcript. Then change the prompt so it
must fail (read a nonexistent file) and fire once more.

## Done when

- You've seen two runs — one success transcript, one failure transcript —
  and can explain why the status column alone can't tell them apart.

## Skills used

- Routine prompt → body mapping
- Reading a routine transcript (model + tool calls + outputs)
- Distinguishing "looks like success" from "actually succeeded"
- The deceptive FAILURE pattern: model says "DONE" even when something was wrong

## How to run

```bash
cd project-09-rehearse-routine-free

# 1. First run — success path
python run-routine.py --success
# Writes .transcripts/transcript-success-<ts>.md

# 2. Read the success transcript
cat .transcripts/transcript-success-*.md | head -20

# 3. Second run — failure path
python run-routine.py --fail
# Writes .transcripts/transcript-fail-<ts>.md

# 4. Read the failure transcript — and notice: status: SUCCESS
cat .transcripts/transcript-fail-*.md | head -25
```

**The lesson:** Both transcripts end with `status: SUCCESS` and `model: DONE`.
The failure path even writes a file! Status alone can't tell them apart.
You have to read the transcript to see that the failure path:
- Tried to read a nonexistent file
- Got `FileNotFoundError`
- "Recovered" by writing a placeholder
- Claimed DONE anyway

That's the whole point of Project 9: the status column lies. Read the
transcript, every time.

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-09-rehearse-routine-free
# Success run
python run-routine.py --success
# → writes .transcripts/transcript-success-<ts>.md

# Read success transcript
cat .transcripts/transcript-success-*.md
# → should end with: status: SUCCESS, model: DONE

# Failure run
python run-routine.py --fail
# → writes .transcripts/transcript-fail-<ts>.md

# Read failure transcript
cat .transcripts/transcript-fail-*.md
# → should ALSO end with: status: SUCCESS, model: DONE
# → but the body should show: "ERROR: DOES_NOT_EXIST.md does not exist"
# → that's the teaching point: status alone is misleading
```

## Files

| File | Purpose |
|------|---------|
| `routine-prompt.md` | The Routine's body prompt (read git log, write summary) |
| `run-routine.py` | Simulates the run; writes a transcript to `.transcripts/` |
| `.transcripts/` | Where the two transcripts land |