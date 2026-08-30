# Skill: Fix an Off-By-One Bug

## Context
You are given a Python module with one or more off-by-one bugs. Each bug follows
the pattern: a return statement ends with ` - 1` where it should not.

## Fix Steps
1. Run the test suite to see which test(s) fail.
2. Open the failing module and locate the return statement with ` - 1`.
3. Remove the ` - 1` suffix from that return statement.
4. Re-run tests. If they pass, the fix is complete.
5. If multiple bugs exist, repeat steps 1-4 for each.

## Important Constraints
- Do NOT change any logic other than removing the trailing ` - 1`.
- Do NOT add new functions, imports, or change signatures.
- The fix must be minimal and surgical.