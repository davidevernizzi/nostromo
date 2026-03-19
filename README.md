# Nostromo

A CLI pomodoro timer. Single Python file, no dependencies.

## Requirements

Python 3 (pre-installed on macOS and most Linux distros).

## Usage

```
python3 nostromo.py [--work N] [--break N] <project> <task>
python3 nostromo.py [--work N] [--break N] <task>
```

If only a task is provided, the last used project is reused automatically.

## Examples

Start a session with a project and task (25 min work / 5 min break):

```bash
python3 nostromo.py "my-app" "implement login page"
```

Continue on the same project — just pass the task:

```bash
python3 nostromo.py "fix auth redirect bug"
```

Custom durations (50 min work / 10 min break):

```bash
python3 nostromo.py --work 50 --break 10 "my-app" "refactor database layer"
```

## Optional: run as a command

```bash
chmod +x nostromo.py
cp nostromo.py /usr/local/bin/nostromo
nostromo "my-app" "write tests"
```

## Report

Generate a report of time spent:

```
python3 nostromo.py report [interval] [--from DATE] [--to DATE] [--project LIST]
```

Predefined intervals: `today` (default), `yesterday`, `this-week`, `last-week`, `this-month`, `last-month`.

```bash
# Today's sessions
python3 nostromo.py report

# This week, filtered to one project
python3 nostromo.py report this-week --project my-app

# Custom date range, multiple projects
python3 nostromo.py report --from 2026-03-01 --to 2026-03-15 --project my-app,other-project
```

Output includes per-project totals, a daily breakdown (for multi-day ranges), and a full task list.

## State

Last used project is stored in `~/.nostromo/state.json`.
