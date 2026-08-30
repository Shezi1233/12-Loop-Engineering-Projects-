# Project 10 — The secrets drill

**Difficulty:** Easy–Medium (30–45 min)
**Concept:** Routine drill — `.env` vs env vars

## Goal

Build: Write a prompt needing one dummy secret. First run: put the token in a
gitignored `.env` file — watch it fail to find the value. Second run: move
the token to environment variables + add the line "credentials are available
as environment variables; do not look for a .env file."

## Done when

- The second run reads the token from the environment.
- You can explain why the first failed (gitignored files never reach a fresh clone).

## Skills used

- `.env` vs `os.environ` — when each one works
- Gitignore semantics: a gitignored file is **never** in a fresh clone
- Routine execution context: a one-off Routine runs in a fresh shell with
  no state — it cannot see your local `.env`
- Prompts that need secrets should say "use environment variables" upfront

## How to run

```bash
cd project-10-secrets-drill

# 1. First run — try to read from .env (fails in fresh clone)
python run-routine.py --env-file
# → transcript: "ERROR: .env does not exist in fresh clone"
# → token-used.txt: "Token read: NO_TOKEN_FOUND"

# 2. Second run — read from environment variable
DUMMY_TOKEN=this-is-a-throwaway-token-do-not-use python run-routine.py --env-var
# → transcript: "Token read: this-is-a-throwaway-token-do-not-use"
# → token-used.txt: shows the real token

# 3. Read both transcripts
cat .transcripts/transcript-env-file-*.md
cat .transcripts/transcript-env-var-*.md
```

**The lesson:** A gitignored `.env` is invisible to:
- A fresh clone (no file to read)
- A Routine running in a sandboxed shell (no state from your local checkout)
- A CI/CD environment (the file is filtered out at clone time)

The fix is to **always** pass secrets via environment variables, and to
make the prompt say so: "credentials are available as environment
variables; do not look for a .env file."

## Test Status

⚠️ **NOT YET TESTED**

**To verify (next session):**
```bash
cd project-10-secrets-drill
# First run — .env approach (simulates fresh clone)
python run-routine.py --env-file
# → transcript: "ERROR: .env does not exist in fresh clone"
# → token-used.txt: "Token read: NO_TOKEN_FOUND"

# Second run — env var approach
DUMMY_TOKEN=this-is-a-throwaway-token-do-not-use python run-routine.py --env-var
# → transcript: "Token read: this-is-a-throwaway-token-do-not-use"
# → token-used.txt: shows the real token

# Read both transcripts
cat .transcripts/transcript-env-file-*.md
cat .transcripts/transcript-env-var-*.md
```

## Files

| File | Purpose |
|------|---------|
| `routine-prompt.md` | Both prompt versions (env-file vs env-var) |
| `run-routine.py` | Simulates both runs, writes transcripts |
| `.env` | The gitignored file (the one that "shouldn't be there") |
| `.gitignore` | Excludes `.env` from git |

**Files modified during testing:**
- `.gitignore` — excludes `.env` from git (the core teaching point)