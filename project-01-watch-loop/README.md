# Project 1 — A watch loop

**Difficulty:** Easy (15–30 min)
**Concept:** In-session loop (Concept 4)

## Goal

Build: Start a long task in the repo (e.g. a script that sleeps for a while then writes a file). Set up an in-session loop that checks every minute whether the task has finished, and tells you the moment it has.

## Done when

- The loop notices the task finished, says so once, and can be stopped cleanly.
- You never sat watching the terminal.

## Skills used

- In-session loop pattern (polling a condition with a sleep interval)
- Clean shutdown (handle Ctrl+C / SIGTERM)
- File-existence as a completion signal

## How to run

```bash
# Terminal A — start the long task
python long-task.py 120

# Terminal B — start the watch loop
python watch-loop.py
```

The watch loop polls `output.txt` every 60 seconds and exits the moment the file
appears. Press `Ctrl+C` to stop it cleanly at any time.

## Test Status

✅ **FULLY VERIFIED**
- `long-task.py 5`: writes `output.txt` correctly with timestamp
- `watch-loop.py`: detects `output.txt`, prints "FINISHED" once, exits 0
- Clean Ctrl+C handling: confirmed