# Task 003: Report command and ASCII rendering

- **Agent**: backend
- **Depends on**: task001, task002

## Description
Wire up the `report` subcommand in `pomodoro.py` and implement the ASCII output renderer.

### CLI wiring

Convert `pomodoro.py` from a single-command script to one that supports subcommands using `argparse` sub-parsers:

- **`pomodoro.py <project> <task>` / `pomodoro.py <task>`** -- existing timer behavior (default when no known subcommand is given). Preserve full backward compatibility.
- **`pomodoro.py report [INTERVAL] [--from DATE] [--to DATE] [--project LIST]`** -- the new report subcommand.

The `--project` flag accepts a comma-separated string of project names (case-sensitive). When omitted, all projects are included.

### Report generation pipeline

1. Resolve the date range (task002).
2. Load and parse journal entries for that range (task001).
3. Filter by project if `--project` is specified.
4. Compute aggregates and render output.

### ASCII rendering

Print to stdout, no color codes, all lines within 80 columns. Three sections:

**Header:**
```
Report: YYYY-MM-DD to YYYY-MM-DD
Projects: name1, name2  (or "all")
```

**Per-Project Totals:**
```
== Per-Project Totals ==

  my-app         [████████████████░░░░]  1h 45m
  other-project  [████░░░░░░░░░░░░░░░░]    30m
```
Projects sorted alphabetically. Time formatted as `Xh Ym` (omit hours if 0, omit minutes if 0; minimum display is `0m`). Progress bar is 20 chars wide, filled proportionally to the project with the most time (`█` filled, `░` empty).

**Daily Breakdown** (omitted if the range is a single day):
```
== Daily Breakdown ==

  YYYY-MM-DD
    project-name      Xh Ym
```
Days sorted chronologically, projects sorted alphabetically within each day.

**Tasks:**
```
== Tasks ==

  my-app
    YYYY-MM-DD  task description          Xh Ym

  other-project
    YYYY-MM-DD  task description          Xh Ym
```
Grouped by project (alphabetical). Within each project, tasks are sorted chronologically (date, then time). Columns are left-aligned with fixed padding.

### Edge cases
- No entries found: print `No entries found for the given period.` and exit 0.
- No journal directory: print `No journal data found.` and exit 0.
- Project filter matches no entries: same as "no entries found".

## Acceptance Criteria
- [ ] `pomodoro.py report` runs without arguments and defaults to today
- [ ] `pomodoro.py report today` shows today's entries
- [ ] `pomodoro.py report this-week` shows the current week
- [ ] `pomodoro.py report --from 2026-03-01 --to 2026-03-19` works with custom dates
- [ ] `--project my-app` filters to a single project
- [ ] `--project my-app,other` filters to multiple projects
- [ ] Per-project totals are correct and sorted alphabetically
- [ ] Daily breakdown appears only for multi-day ranges
- [ ] Tasks section groups entries by project (alphabetical), tasks sorted chronologically within each group
- [ ] Per-project totals show an ASCII progress bar (`█`/`░`, 20 chars wide) scaled to the largest project
- [ ] Time formatting follows `Xh Ym` rules (no "0h", no "0m" when hours present, shows "0m" for zero)
- [ ] Output fits within 80 columns
- [ ] Existing timer functionality (`pomodoro.py <project> <task>`) is not broken
- [ ] No third-party dependencies
