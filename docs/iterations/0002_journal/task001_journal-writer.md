# Task 001: Implement journal writer

- **Agent**: backend
- **Depends on**: none

## Description
Add journal-writing logic to `pomodoro.py`. After the break phase completes, append an entry to `journal/by-day/<date>.md` and `journal/by-project/<project>.md`. Both files receive the identical entry text.

Introduce a `write_journal(project, task, work_min, break_min)` function that:
1. Resolves the `journal/` directory relative to `__file__`
2. Creates `journal/by-day/` and `journal/by-project/` if missing
3. Builds the entry string (see `agents.md` for format)
4. Appends the entry to both target files
5. Catches any `OSError` and prints a warning to stderr without raising

Call `write_journal(...)` from `main()` immediately after the break timer completes, before printing "Break over. Well done!".

## Acceptance Criteria
- [ ] `journal/by-day/YYYY-MM-DD.md` is created/appended after a completed session
- [ ] `journal/by-project/<project>.md` is created/appended after a completed session
- [ ] Both files contain the identical entry
- [ ] Entry format matches the spec in `agents.md` exactly
- [ ] Interrupted sessions (Ctrl+C) produce no journal entry
- [ ] Write errors print a warning but do not crash the program
- [ ] No new third-party dependencies introduced
