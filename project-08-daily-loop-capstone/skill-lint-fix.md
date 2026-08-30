# Skill: Fix Lint / Test Failures

## Context
You are given a Python module with one or more bugs or style issues. The goal is
to make the test suite pass with a minimal diff.

## Fix Steps
1. Run the test suite (`pytest -q`) to see which test(s) fail.
2. Read the failing test(s) to understand what the expected behavior is.
3. Fix the target file (`target.py`) so all tests pass.
   - Make minimal changes — only what's needed.
   - Do NOT change test files.
4. Re-run the test suite to confirm all tests pass.
5. Check that the git diff is minimal (only the necessary changes).
   - `git diff` should show clean, focused changes.
   - No unrelated modifications (e.g., no `.runs/` or `__pycache__`).

## Important Constraints
- Do NOT add new functions, imports, or change signatures unless needed for the fix.
- Do NOT change test files — only `target.py`.
- The fix must be minimal and surgical.
- `git diff` reviewed before submission.

## Reviewer Checklist (used by reviewer.py)
- [ ] All tests pass (`pytest` exit code 0)
- [ ] Diff is minimal (only `target.py` changes, no other files)
- [ ] No new ` - 1` off-by-one patterns introduced
- [ ] Code reads naturally — no forced or ugly changes