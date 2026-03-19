# Nostromo

A CLI pomodoro timer. Single Python file, no dependencies.

## Requirements

Python 3 (pre-installed on macOS and most Linux distros).

## Usage

```
python3 pomodoro.py [--work N] [--break N] <project> <task>
python3 pomodoro.py [--work N] [--break N] <task>
```

If only a task is provided, the last used project is reused automatically.

## Examples

Start a session with a project and task (25 min work / 5 min break):

```bash
python3 pomodoro.py "my-app" "implement login page"
```

Continue on the same project — just pass the task:

```bash
python3 pomodoro.py "fix auth redirect bug"
```

Custom durations (50 min work / 10 min break):

```bash
python3 pomodoro.py --work 50 --break 10 "my-app" "refactor database layer"
```

## Optional: run as a command

```bash
chmod +x pomodoro.py
cp pomodoro.py /usr/local/bin/pomodoro
pomodoro "my-app" "write tests"
```

## State

Last used project is stored in `~/.nostromo/state.json`.
