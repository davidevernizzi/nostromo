# Task 001: Journal parser

- **Agent**: backend
- **Depends on**: none (can run in parallel with task002)

## Description
Create a module-level function (or small group of functions) in `pomodoro.py` that reads and parses journal entries from `journal/by-day/` files.

Specifically:

1. **`parse_journal_file(path) -> list[JournalEntry]`** -- reads a single `by-day/*.md` file and returns a list of `JournalEntry` dataclass instances. Each entry is delimited by a line starting with `---`. Relevant fields: `date`, `time`, `project`, `task`, `work_min`. Malformed entries are skipped with a warning to stderr.

2. **`load_journal_entries(journal_dir, start_date, end_date) -> list[JournalEntry]`** -- scans `journal/by-day/`, identifies files whose filename date falls within `[start_date, end_date]`, parses each, and returns all entries sorted by (date, time).

3. **`JournalEntry` dataclass** with fields: `date` (datetime.date), `time` (str), `project` (str), `task` (str), `work_min` (int).

The journal directory is resolved relative to the script location (`Path(__file__).parent / "journal"`), consistent with the existing `write_journal` function.

## Acceptance Criteria
- [ ] `JournalEntry` dataclass is defined with the five fields listed above
- [ ] `parse_journal_file` correctly parses entries separated by `---` lines
- [ ] Malformed entries are skipped with a stderr warning (not a crash)
- [ ] `load_journal_entries` only reads files whose date falls within the requested range
- [ ] Returned entries are sorted by date then time
- [ ] Missing journal directory returns an empty list (no crash)
- [ ] No third-party dependencies
