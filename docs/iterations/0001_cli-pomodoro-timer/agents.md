# 0001 – Specification

## Overview
A single Python script (`pomodoro.py`) with no third-party dependencies. It runs a pomodoro work/break cycle, displays a live countdown in the terminal, and persists the last-used project name across invocations.

## Inputs / Outputs

### Invocation
```
pomodoro [--work N] [--break N] [<project>] <task>
```

### Positional Arguments
- **2 positional args**: first is `project`, second is `task`
- **1 positional arg**: treated as `task`; `project` is loaded from the state file's `last_project` field
- **0 positional args**: print usage and exit with error

### Flags
| Flag | Default | Description |
|---|---|---|
| `--work N` | 25 | Work phase duration in minutes |
| `--break N` | 5 | Break phase duration in minutes |

## Data Models

### State File
- Path: `~/.nostromo/state.json`
- Schema: `{"last_project": "<string>"}`
- Created automatically (including parent directory) if missing
- Updated after every successful run with the current project

## Timer Behavior
1. Print `Starting pomodoro: <project> — <task>` with durations
2. Work phase: live countdown on a single overwritten line (`⏱  MM:SS remaining`)
3. On work end: bell (`\a`) + `\nWork done! Break time.`
4. Break phase: live countdown on a single overwritten line
5. On break end: bell (`\a`) + `\nBreak over. Well done!`

## Edge Cases & Constraints
- If 1 positional arg and no `last_project` in state: print error and exit with code 1
- Ctrl+C (`SIGINT`): print `\nPomodoro interrupted.` and exit cleanly (code 0)
- Dependencies: stdlib only — `argparse`, `time`, `json`, `os`, `signal`, `sys`
