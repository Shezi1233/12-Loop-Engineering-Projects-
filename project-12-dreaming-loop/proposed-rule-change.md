## Proposed Rule Change

### Problem (7 repeated occurrences)

- [2026-08-30 13:09] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:12] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:31] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:40] Dreaming Loop: - failures scanned: 0

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
- [2026-08-30 13:09] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:12] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:18] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:31] Dreaming Loop: - failures scanned: 0
- [2026-08-30 13:40] Dreaming Loop: - failures scanned: 0
```

### Why this prevents the repeat

The implementer must confirm the off-by-one pattern before patching, not blindly
remove the first ` - 1` it finds.


## Proposed Deletion

### Rule: `check-gitignore`

No recent run has triggered or used this rule.
It can be safely removed from the skill file to keep it minimal.

Proposed change: delete the section for `check-gitignore` from the skill file.