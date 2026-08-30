## Proposed Rule Change

### Problem (15 repeated occurrences)

- [2026-08-30 12:55] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:56] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:57] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:57] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:58] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:59] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:59] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:00] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:01] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:01] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:02] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:03] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:02] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:03] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:04] Daily Lint Sweep: off-by-one in return statement

### Proposed fix

Before applying any patch, identify whether the failure is a known pattern.
If the diff contains ` - 1` in a return statement and tests are failing,
the implementer should remove ONLY that specific ` - 1` and nothing else.

### Proposed skill file change (add to skill-lint-fix.md)

```
## Pre-check: identify the off-by-one pattern

Before removing ` - 1`, verify:
1. The line starts with `return`
2. The expression before ` - 1` is an arithmetic expression
3. There is only ONE ` - 1` in the return statement

If all three are true, proceed with the fix.
If not, STOP and report: "off-by-one pattern not confirmed".
```

### Evidence
```
- [2026-08-30 12:55] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:56] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:57] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:57] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:58] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:59] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 12:59] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:00] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:01] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:01] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:02] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:03] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:02] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:03] Daily Lint Sweep: off-by-one in return statement
- [2026-08-30 13:04] Daily Lint Sweep: off-by-one in return statement
```

### Why this prevents the repeat

The implementer must confirm the off-by-one pattern before patching, not blindly
remove the first ` - 1` it finds.


## Proposed Deletion

### Rule: `check-gitignore`

No recent run has triggered or used this rule.
It can be safely removed from the skill file to keep it minimal.

Proposed change: delete the section for `check-gitignore` from the skill file.