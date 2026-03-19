# Task 001: Implement pomodoro.py

- **Agent**: backend
- **Depends on**: none (can run in parallel)

## Description
Create `pomodoro.py` in the project root as a single-file Python script implementing all features in `agents.md`. The file must include a shebang line (`#!/usr/bin/env python3`) and be marked executable (`chmod +x`).

## Acceptance Criteria
- [ ] Script runs with `python3 pomodoro.py` and as `./pomodoro.py`
- [ ] Two positional args → uses first as project, second as task
- [ ] One positional arg → uses `last_project` from state file as project
- [ ] Zero positional args → prints usage and exits with error
- [ ] `--work` and `--break` flags override defaults of 25 and 5
- [ ] Live countdown updates in-place on a single line
- [ ] Terminal bell rings at end of work phase and end of break phase
- [ ] `~/.nostromo/state.json` is created if missing and updated after each run
- [ ] Ctrl+C prints interruption message and exits cleanly
- [ ] No third-party dependencies
