# 0004 – Specification

## Overview
Replace the current single-line status string with a compact two-line display that always fits within 40 columns. The first line contains a progress bar and time remaining; the second line is a static key-hint row printed once per phase. Only the first line is redrawn on each tick.

## Display Layout

```
Work [████████████░░░░░░░░] 12:34
p:pause  s:stop  c:cancel  a:+5m
```

### Line 1 — progress line (redrawn every tick via `\r`)
```
<label> [<bar>] <MM:SS>
```

| Segment     | Width | Notes |
|-------------|-------|-------|
| `<label> `  | 6     | `"Work  "` or `"Break "` (padded to 6) |
| `[`         | 1     | |
| `<bar>`     | 20    | filled chars + empty chars = 20 total |
| `]`         | 1     | |
| ` `         | 1     | |
| `<MM:SS>`   | 5     | remaining time |
| **Total**   | **35**| fits in 40 cols with margin |

Bar characters: `█` for elapsed portion, `░` for remaining portion.

Progress fraction = `elapsed / total` (where `total` includes any added time and excludes pause time).

### Line 2 — key hints (printed once at phase start, not redrawn)
```
p:pause  s:stop  c:cancel  a:+5m
```
33 characters, fits in 40 cols.

## Startup header

Replace the current two-line header with a single compact line:

```
► my-app — write tests  [25m work / 5m break]
```

Truncate project+task to fit within 40 cols if needed (clip at 40 with no ellipsis required).

## Pause display

When paused, overwrite line 1 only:
```
\r  ⏸  Paused — p to resume
```
(padded to 35 chars to clear previous content)

## After `+5 min added`

Print on a new line (same as today), then redraw line 1 from current state.

## Changes to `_print_status`

Signature becomes:
```python
def _print_status(elapsed, total, label):
```
Takes `elapsed` and `total` directly to compute the fill fraction, instead of just `remaining`.

## Non-interactive fallback

Same format for line 1 (progress bar), but printed with `\r` and `time.sleep(1)` ticks as today. No key-hint line.

## Edge Cases & Constraints
- `total` may grow (via `a`); bar fraction is always clamped to `[0.0, 1.0]`
- Unicode block characters (`█`, `░`) are used; no fallback needed (UTF-8 terminals only)
- All output stays ≤ 40 cols
