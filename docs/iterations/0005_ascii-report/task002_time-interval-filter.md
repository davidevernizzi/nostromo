# Task 002: Time interval resolution

- **Agent**: backend
- **Depends on**: none (can run in parallel with task001)

## Description
Implement the logic that converts CLI arguments into a concrete `(start_date, end_date)` pair of `datetime.date` objects.

Specifically:

1. **`resolve_interval(keyword) -> (date, date)`** -- takes a predefined interval keyword and returns the inclusive date range. Supported keywords and their semantics (relative to today):

   | Keyword | start_date | end_date |
   |---|---|---|
   | `today` | today | today |
   | `yesterday` | yesterday | yesterday |
   | `this-week` | Monday of current ISO week | today |
   | `last-week` | Monday of previous ISO week | Sunday of previous ISO week |
   | `this-month` | 1st of current month | today |
   | `last-month` | 1st of previous month | last day of previous month |

   Raises `ValueError` for unknown keywords.

2. **`resolve_date_range(args) -> (date, date)`** -- higher-level function that inspects parsed CLI arguments and returns the date range. Logic:
   - If a positional interval keyword is given and `--from`/`--to` are also given, raise an error.
   - If `--from` is given, use it as start; `--to` defaults to today if omitted.
   - If neither keyword nor `--from`/`--to` is given, default to `today`.
   - Validate that start <= end.

All date math uses `datetime.date` and `datetime.timedelta` from stdlib. Calendar month boundaries use `calendar.monthrange`.

## Acceptance Criteria
- [ ] All six predefined keywords resolve to correct date ranges
- [ ] `--from` without `--to` defaults end to today
- [ ] Providing both a keyword and `--from`/`--to` produces a clear error
- [ ] `--from` after `--to` produces a clear error
- [ ] Unknown keywords produce a clear error listing valid options
- [ ] No third-party dependencies
