# 0002 – Specification

## Overview
At the end of a completed pomodoro session (after the break phase), append a structured entry to two journal files: one grouped by day and one grouped by project. Both files use the identical entry format. The journal lives in a `journal/` directory relative to wherever `pomodoro.py` is located.

## Journal Directory Layout

```
journal/
  by-day/
    2026-03-19.md
    2026-03-20.md
    ...
  by-project/
    my-app.md
    other-project.md
    ...
```

Both subdirectories are created automatically if missing.

## Entry Format

Each entry is a markdown block appended to the target file:

```markdown
---
date: 2026-03-19
time: 14:32
project: my-app
task: implement login page
work_min: 25
break_min: 5
```

- A blank line separates consecutive entries.
- The `---` delimiter makes entries easy to split programmatically.
- Fields map 1:1 to the data available at session end. Any new fields added to the program in future iterations are appended to this block in the same YAML-style format.
- The file for a day (`by-day/2026-03-19.md`) and the file for a project (`by-project/my-app.md`) receive the **exact same entry text**.

## Trigger

Journal writing happens once, **after the break phase completes** (i.e., after `run_timer` for the break returns). Interrupted sessions (Ctrl+C) are not logged.

## Inputs

All values are already available in `main()` at session end:
- `project` — resolved project name
- `task` — task string
- `opts.work` — work duration in minutes
- `opts.brk` — break duration in minutes
- current date and time — from `datetime.now()`

## Edge Cases & Constraints
- Journal directory is resolved relative to the script's own location (`__file__`), not the working directory.
- Both target files are opened in append mode (`"a"`); created if missing.
- Errors writing the journal must not crash the program — print a warning to stderr and continue.
- No third-party dependencies; use `datetime`, `os`, `pathlib` from stdlib.
