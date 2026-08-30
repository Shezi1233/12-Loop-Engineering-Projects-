# Project 3 — The morning brief with a memory

**Difficulty:** Medium (45–60 min)
**Concepts:** Scheduled loop (Concept 6) + spine memory file (Concept 12)

## Goal

Build: A scheduled loop that runs once, reads `progress.md`, gathers something
simple from the repo (open TODO comments), writes a short summary, and updates
`progress.md` with what it found + date.

## Done when

- Run it twice — the second run clearly builds on the first (doesn't repeat
  what's already recorded).

## Skills used

- Scheduled / recurring invocation (cron + GitHub Actions workflow included)
- Reads the shared spine (`../progress.md`)
- Gathers repo metadata (open `# TODO` comments across `.py` files)
- Memory: deduplicates findings against the last dated entry so each run adds
  only NEW information

## How to run

```bash
cd project-03-morning-brief-memory

# First run — records all current TODOs into the spine
python morning-brief.py

# Add a NEW todo to any .py file, then run again
echo "# TODO fix this later" >> ../project-01-watch-loop/morning-brief.py
# — or just re-run twice with no changes to see the dedupe in action
python morning-brief.py

# Inspect the spine
cat ../progress.md
```

The first run prints `Spine already held 0 TODO(s).` and lists everything.
The second run (no new TODOs) prints `Spine already held N TODO(s).` and
lists `- none new since last run` — proving it built on the first run.

## Scheduling

- **GitHub Actions** (no secrets): `.github/workflows/morning-brief.yml` runs
  daily at 09:00 UTC (edit the `cron:` line) and on manual `workflow_dispatch`.
- **Local cron**: `schedule.cron` has the exact line to paste into `crontab -e`
  (replace the path).
- Neither is wired to any real repo or token — it's all in-repo config only.

## Test Status

✅ **FULLY VERIFIED**
- Run 1: "Spine already held **0** TODO(s).", listed 7 TODOs
- Run 2 (with 1 new TODO added): "Spine already held **7** TODO(s).", listed only the 1 new TODO
- Dedup confirmed: second run shows only the newly added TODO, not the 7 from run 1
- UTF-8 encoding fix applied: `read_spine()` uses `encoding="utf-8"` explicitly (Windows default cp1252 was mangling em-dashes)
- CRLF handling fixed: regex uses `\r?\n` for Windows line endings

**Bugs fixed during testing:**
- Em-dash (—) was being mangled by Windows cp1252 default encoding → forced `encoding="utf-8"` on all file reads
- Regex needed `\r?\n` instead of `\n` for Windows line endings