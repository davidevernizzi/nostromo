# 0005 – Specification

## Overview
Implement a `report` subcommand (invoked as `pomodoro.py report`) that parses journal files, filters entries by date range and project, and prints a structured ASCII summary to stdout. The command is read-only; it does not modify any state or journal files.

## Inputs / Outputs

### CLI Interface

```
pomodoro.py report [INTERVAL] [--from DATE] [--to DATE] [--project LIST]
```

| Argument / Flag | Type | Description |
|---|---|---|
| `INTERVAL` | positional, optional | Predefined keyword (see below). Mutually exclusive with `--from`/`--to`. Defaults to `today` if nothing is specified. |
| `--from` | `YYYY-MM-DD` | Start date (inclusive). |
| `--to` | `YYYY-MM-DD` | End date (inclusive). Defaults to today if `--from` is given without `--to`. |
| `--project` | comma-separated string | Limit to these project names. Case-sensitive. |

### Predefined Intervals

| Keyword | Resolved Range |
|---|---|
| `today` | today .. today |
| `yesterday` | yesterday .. yesterday |
| `this-week` | Monday of current ISO week .. today |
| `last-week` | Monday of previous ISO week .. Sunday of previous ISO week |
| `this-month` | 1st of current month .. today |
| `last-month` | 1st of previous month .. last day of previous month |

If both a keyword and `--from`/`--to` are provided, exit with an error message.

### Output Format

The report is printed to stdout as plain text, no color codes. Structure:

```
Report: 2026-03-17 to 2026-03-19
Projects: my-app, other-project  (or "all" if no filter)

== Per-Project Totals ==

  my-app            1h 45m
  other-project       30m

== Daily Breakdown ==

  2026-03-17
    my-app            50m
    other-project     30m

  2026-03-18
    my-app            30m

  2026-03-19
    my-app            25m

== Tasks ==

  2026-03-17  my-app           implement login page      25m
  2026-03-17  my-app           write unit tests           25m
  2026-03-17  other-project    fix deployment script      30m
  2026-03-18  my-app           refactor auth module       30m
  2026-03-19  my-app           review PR comments         25m
```

Rules:
- If the interval is a single day, omit the "Daily Breakdown" section.
- Times are shown in `Xh Ym` format (omit hours if zero, omit minutes if zero).
- Sections are separated by a blank line.
- Projects are sorted alphabetically. Tasks are sorted chronologically.
- Column alignment uses fixed-width spacing; no box-drawing characters.

## Data Models

### Journal Entry (existing, read-only)

Entries are stored in `journal/by-day/YYYY-MM-DD.md`. Each entry is a `---`-delimited block:

```yaml
---
date: 2026-03-19
time: 14:32
project: my-app
task: implement login page
work_min: 25
break_min: 5
```

Optional fields (`paused_min`, `added_min`) are ignored by the report. The relevant fields are: `date`, `time`, `project`, `task`, `work_min`.

### Parsed Entry (in-memory)

```python
@dataclass
class JournalEntry:
    date: datetime.date
    time: str          # "HH:MM"
    project: str
    task: str
    work_min: int
```

## API Contracts

No network APIs. The command reads files from `journal/by-day/` relative to the script location. Each `.md` file whose name matches `YYYY-MM-DD.md` and falls within the requested date range is parsed.

## Edge Cases & Constraints

- **No entries found**: Print `No entries found for the given period.` and exit with code 0.
- **Malformed entries**: Skip entries that cannot be parsed. Print a warning to stderr: `Warning: skipping malformed entry in <file> at line <n>`.
- **Missing journal directory**: Print `No journal data found.` and exit with code 0.
- **Future dates in --from/--to**: Allowed (will just find no entries).
- **--from after --to**: Exit with error: `Error: --from date must be on or before --to date.`
- **Unknown interval keyword**: Exit with error: `Error: unknown interval '<value>'. Valid intervals: today, yesterday, this-week, last-week, this-month, last-month.`
- **No third-party dependencies**: Use only Python stdlib (`argparse`, `datetime`, `pathlib`, `os`, `dataclasses`).
- **Output width**: Keep all lines within 80 columns.
