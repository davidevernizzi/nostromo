# Task 002: Add pause and extension fields to journal

- **Agent**: backend
- **Depends on**: none (can run in parallel with task001)

## Description
Update `write_journal()` to accept `paused_sec` and `added_sec` keyword arguments and conditionally append `paused_min` and `added_min` fields to the YAML entry block. Fields are omitted when their value is zero to keep entries clean.

Update `main()` to accumulate `paused_sec` and `added_sec` from both phase results and pass them to `write_journal`.

## Acceptance Criteria
- [ ] `paused_min` appears in the journal entry only when total pause time > 0
- [ ] `added_min` appears in the journal entry only when total added time > 0
- [ ] Values are rounded to the nearest minute
- [ ] Existing journal entries (without these fields) remain valid
- [ ] `write_journal` signature is backwards-compatible (keyword args with defaults of 0)
