# Task 001: Implement compact display with progress bar

- **Agent**: backend
- **Depends on**: none

## Description
Refactor `_print_status` and all output in `run_timer` and `main` to match the layout defined in `agents.md`. Specific changes:

1. **`_print_status(elapsed, total, label)`** — compute fill fraction, build bar string (20 chars of `█`/`░`), write `\r<label> [<bar>] <MM:SS>` padded to 35 chars
2. **Key hint line** — print `p:pause  s:stop  c:cancel  a:+5m\n` once at the start of each interactive phase (before the loop)
3. **Pause message** — overwrite line 1 with `\r  ⏸  Paused — p to resume` (pad to 35)
4. **Startup header** in `main()` — replace two-line header with single `► <project> — <task>  [<work>m work / <break>m break]`
5. **Non-interactive fallback** — same bar format, `\r` update each second

## Acceptance Criteria
- [ ] Progress line is always ≤ 40 cols
- [ ] Bar visually fills left-to-right as time elapses
- [ ] Bar fraction accounts for added time (denominator grows)
- [ ] Key hints are printed once per phase, not re-printed on every tick
- [ ] Pause message overwrites the progress line cleanly
- [ ] Startup header fits 40 cols
- [ ] Non-interactive path shows the progress bar too
