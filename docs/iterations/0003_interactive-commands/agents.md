# 0003 – Specification

## Overview
Refactor `run_timer()` to poll for single-keypress input on each tick without blocking. Four keys are supported during any active phase: `p` (pause), `c` (cancel), `s` (stop), `a` (add time). The timer loop tracks total paused time and total added time, which are returned to `main()` and written to the journal.

## Keypress Input

### Unix/macOS
Use `tty.setraw()` + `termios` to put stdin into raw mode, and `select.select` with a short timeout to poll for input without blocking:

```python
import tty, termios, select

def _read_key(timeout=0.05):
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read(1)
    return None
```

Restore terminal settings in a `finally` block after the phase ends.

### Windows
Use `msvcrt.kbhit()` + `msvcrt.getch()` as a fallback.

Detect platform via `os.name == 'nt'`.

## Timer Loop Refactor

`run_timer(seconds, label)` becomes `run_timer(seconds, label) -> dict` and returns:
```python
{"outcome": "completed" | "cancelled" | "stopped", "paused_sec": int, "added_sec": int}
```

The loop ticks every ~0.05 s (to stay responsive to keypresses) and accumulates elapsed time. Remaining time is recalculated each tick as `total_seconds - elapsed`.

### Key Behaviours

| Key | Phase | Behaviour |
|---|---|---|
| `p` | any | Toggle pause. On pause: freeze countdown, show `Paused — press p to resume`. On resume: continue. Accumulate pause duration in `paused_sec`. |
| `c` | any | Immediately exit with `outcome = "cancelled"`. Print `\nCancelled.`. |
| `s` | any | Immediately exit with `outcome = "stopped"`. Print `\nStopped early.`. |
| `a` | any | Add 300 s (5 min) to `total_seconds`. Print `\n+5 min added.`. Accumulate in `added_sec`. |

Display line format (updated every tick):
```
Work: 12:34 remaining  [p]ause  [s]top  [c]ancel  [a]dd 5m
```

## `main()` Changes

After each `run_timer()` call, inspect `outcome`:

**Work phase:**
- `completed` → proceed to break as today
- `stopped` → call `write_journal(...)` with partial data, then exit
- `cancelled` → exit without logging

**Break phase:**
- `completed` or `stopped` → call `write_journal(...)`
- `cancelled` → exit without logging

Accumulate `paused_sec` and `added_sec` across both phases and pass totals to `write_journal`.

## Journal Entry Changes

Two new optional fields appended to the existing YAML block:

```
paused_min: 3
added_min: 10
```

- `paused_min`: total pause time rounded to nearest minute (omit if 0)
- `added_min`: total minutes added via `a` (omit if 0)

`write_journal` signature becomes:
```python
def write_journal(project, task, work_min, break_min, paused_sec=0, added_sec=0)
```

## Edge Cases & Constraints
- Terminal must be restored to original settings even if an exception occurs (use `finally`).
- If stdin is not a tty (e.g. piped input), skip raw mode and disable interactive commands silently.
- Ctrl+C during a session still triggers the existing `SIGINT` handler (restoring terminal before exit is handled by the `finally` block).
- No new third-party dependencies.
