# Project 2 — Make the tests pass, then stop

**Difficulty:** Easy–Medium (30–45 min)
**Concepts:** Conditional loop (Concept 5) + command-as-decision-maker (Concept 11)

## Goal

Build: Add 2-3 small FAILING tests to the repo. Build a loop that keeps working until the tests pass, but a COMMAND (the test runner) — not the agent — decides when it's done. Cap it at 6 tries.

## Done when

- The loop stops because tests actually passed, not because it hit the cap.

## Skills used

- Conditional loop (iterate while a condition holds)
- Command-as-decision-maker: pytest's **exit code** is the sole success predicate
- Max-try limits so nothing runs unbounded
- Deterministic fix attempt per iteration

## How to run

```bash
cd project-02-tests-pass-then-stop

# Check the tests start failing
python -m pytest -q          # expect 3 failed

# Run the loop — it fixes one bug per round, stops when pytest says pass
python fix-loop.py
```

The loop prints `try 1/6: tests FAILED`, applies a fix, re-runs pytest, and
repeats until pytest exits 0 — then prints `PASSED on try N — tests pass, stopping`.

You can watch the source change between iterations: `mathlib.py` loses one
`- 1` per round until both bugs are gone.

## Test Status

✅ **FULLY VERIFIED**
- Initial state: 3 tests fail (assert 4 == 5, assert -1 == 0, assert 9 == 10)
- `fix-loop.py`: ran 3 rounds, fixed both bugs, exited on **try 3 (not the cap)**
- The command's exit code is the sole decision-maker — confirmed
- After fix: `mathlib.py` no longer contains `- 1` off-by-ones

**Side note for next time:** the `apply-fix.py` file in this project now
has a `# TODO planted for project 3 demo` comment (left over from Project 3
testing). Not a bug — just an artifact.