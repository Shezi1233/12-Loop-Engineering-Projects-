# Routine: Read Dummy Token and Use It

## Task
Read a token from the environment, then write it (or a confirmation) to a file
called `token-used.txt` at the repo root.

## First-run version (uses .env)
Load the token from a `.env` file. Use python-dotenv.

## Second-run version (uses env vars)
Credentials are available as environment variables; do not look for a .env file.
Read the token directly from `os.environ`.

## Output
1. The token (or "no token found" message)
2. The file `token-used.txt` at the repo root
3. Print "DONE" when finished

## How this works in a real Routine
The Routine runs in a fresh shell, with no memory of past runs. If the token
is in a gitignored `.env` file, the Routine will NEVER see it — because the
file is gitignored, it doesn't exist in a fresh clone, and there's no .env
to read.

This project simulates both runs and writes transcripts to `.transcripts/`.