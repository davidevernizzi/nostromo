# Task 001: Refactor timer loop with interactive commands

- **Agent**: backend
- **Depends on**: none

## Description
Refactor `run_timer()` to support non-blocking keypress polling and return an outcome dict. Implement the `p`, `c`, `s`, `a` key handlers as specified in `agents.md`. Update `main()` to branch on the outcome of each phase.

Key implementation points:
- Abstract input into a `_read_key(timeout)` function with Unix (`tty`/`termios`/`select`) and Windows (`msvcrt`) branches
- Guard raw-mode setup with `sys.stdin.isatty()` check; if not a tty, run the original blocking loop
- Restore terminal in a `finally` block
- Update the display line to show available keys

## Acceptance Criteria
- [ ] `p` pauses the countdown and resumes on second press
- [ ] `c` exits immediately with no journal entry
- [ ] `s` exits immediately and triggers journal write
- [ ] `a` adds 5 minutes to the current phase countdown; can be pressed multiple times
- [ ] Display line shows remaining time and available key hints
- [ ] Terminal is always restored on exit (normal, Ctrl+C, or exception)
- [ ] Behaviour is unchanged when stdin is not a tty
