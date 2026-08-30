# Project 7 — Break it on purpose

**Difficulty:** Medium (45–60 min)
**Concepts:** Observability + cost (Concept 13 + 14)

## Goal

Build: Take the Project 3 loop. First measure one beat's token cost and
extrapolate to a monthly cost. Then sabotage it (point at a nonexistent file,
or an impossible success condition, with a limit set). Let it fail. Diagnose
the failure using ONLY the log + progress.md, without replaying the run.

## Done when

- You can say what failed and when from the spine alone.
- The loop left a clear "needs a human" note.
- You know its monthly cost.

## Skills used

- Observability: per-beat log files (`.runs/<run-id>/beat.log`) + spine notes
- Cost measurement: estimate tokens per beat, extrapolate to monthly
- Sabotage testing: deliberately break the loop, then diagnose from logs
- No-replay diagnosis: read the log + spine to find the failure, don't re-run

## How to run

```bash
cd project-07-break-it-on-purpose

# 1. First, measure one beat's cost
python measure-beat.py
# → writes .runs/measure-<ts>/beat.log + spine entry with monthly cost

# 2. Sabotage the loop in two ways
python sabotage.py impossible-cause     # impossible success condition
python sabotage.py nonexistent-file     # point at nonexistent spine

# 3. Diagnose from logs ONLY (no replay)
python diagnose.py
# → prints what failed, when, and the monthly cost
```

**The diagnosis reads the log + spine.** It never re-runs the sabotaged beat.
It finds the sabotage by grepping for "SABOTAGED" / "sabotage" / "nonexistent"
in `*.runs/*/beat.log`, then prints the full log for that run plus the spine's
"needs a human" note.

## Files

| File | Purpose |
|------|---------|
| `morning-brief.py` | Observability version of Project 3 — logs every beat |
| `measure-beat.py` | Runs one beat, estimates tokens, extrapolates monthly cost |
| `sabotage.py` | Breaks the loop (2 modes) and writes a spine "needs a human" note |
| `diagnose.py` | Reads log + spine, reports what failed, when, and monthly cost |

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-07-break-it-on-purpose
# 1. Measure one beat's cost
python measure-beat.py
# → writes .runs/measure-<ts>/beat.log
# → adds "Estimated monthly cost: $X" to ../progress.md

# 2. Sabotage (2 ways)
python sabotage.py impossible-cause     # pretends no TODOs
python sabotage.py nonexistent-file     # points at missing spine

# 3. Diagnose from logs only
python diagnose.py
# → finds sabotage in logs
# → reports what failed, when, monthly cost
# → does NOT replay the sabotaged beat
```