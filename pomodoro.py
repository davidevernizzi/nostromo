#!/usr/bin/env python3
import argparse
import calendar
import json
import os
import signal
import sys
import time
import datetime as dt
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.nostromo/state.json")

# Platform-specific keypress reading
if os.name == "nt":
    import msvcrt

    def _read_key(_timeout=0.05):
        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8", errors="ignore")
        time.sleep(_timeout)
        return None

else:
    import select
    import termios
    import tty

    def _read_key(timeout=0.05):
        if select.select([sys.stdin], [], [], timeout)[0]:
            return sys.stdin.read(1)
        return None


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def run_timer(seconds, label):
    """Run a countdown timer with interactive key controls.

    Returns a dict:
        {"outcome": "completed"|"cancelled"|"stopped", "elapsed_sec": int, "paused_sec": int, "added_sec": int}
    """
    interactive = sys.stdin.isatty() and os.name != "nt" or (os.name == "nt" and sys.stdin.isatty())

    total = seconds
    elapsed = 0.0
    paused_sec = 0
    added_sec = 0
    tick = 0.05  # seconds per loop iteration

    BAR_WIDTH = 20
    HINTS = "p:pause  s:stop  c:cancel  a:+5m"

    def _print_status():
        fraction = min(elapsed / total, 1.0) if total > 0 else 0.0
        filled = round(fraction * BAR_WIDTH)
        bar = "█" * filled + "░" * (BAR_WIDTH - filled)
        remaining = max(total - elapsed, 0)
        mm, ss = divmod(int(remaining), 60)
        lbl = label[:5].ljust(6)
        line = f"{lbl}[{bar}] {mm:02d}:{ss:02d}"
        sys.stdout.write(f"\r{line:<35}")
        sys.stdout.flush()

    if not interactive:
        for elapsed_s in range(0, seconds + 1):
            fraction = min(elapsed_s / seconds, 1.0) if seconds > 0 else 1.0
            filled = round(fraction * BAR_WIDTH)
            bar = "█" * filled + "░" * (BAR_WIDTH - filled)
            remaining = max(seconds - elapsed_s, 0)
            mm, ss = divmod(remaining, 60)
            lbl = label[:5].ljust(6)
            line = f"{lbl}[{bar}] {mm:02d}:{ss:02d}"
            sys.stdout.write(f"\r{line:<35}")
            sys.stdout.flush()
            if elapsed_s < seconds:
                time.sleep(1)
        sys.stdout.write("\n\a")
        sys.stdout.flush()
        return {"outcome": "completed", "elapsed_sec": seconds, "paused_sec": 0, "added_sec": 0}

    # Save and switch to raw terminal mode
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin)
        sys.stdout.write(f"{HINTS}\n")
        sys.stdout.flush()

        while elapsed < total:
            _print_status()

            key = _read_key(tick)

            if key == "p":
                pause_start = time.monotonic()
                sys.stdout.write(f"\r{'  ⏸  Paused — p to resume':<35}")
                sys.stdout.flush()
                while True:
                    k = _read_key(0.1)
                    if k == "p":
                        break
                    if k == "c":
                        paused_sec += int(time.monotonic() - pause_start)
                        sys.stdout.write("\nCancelled.\n")
                        sys.stdout.flush()
                        return {"outcome": "cancelled", "elapsed_sec": int(elapsed), "paused_sec": paused_sec, "added_sec": added_sec}
                    if k == "s":
                        paused_sec += int(time.monotonic() - pause_start)
                        sys.stdout.write("\nStopped early.\n")
                        sys.stdout.flush()
                        return {"outcome": "stopped", "elapsed_sec": int(elapsed), "paused_sec": paused_sec, "added_sec": added_sec}
                paused_sec += int(time.monotonic() - pause_start)

            elif key == "c":
                sys.stdout.write("\nCancelled.\n")
                sys.stdout.flush()
                return {"outcome": "cancelled", "elapsed_sec": int(elapsed), "paused_sec": paused_sec, "added_sec": added_sec}

            elif key == "s":
                sys.stdout.write("\nStopped early.\n")
                sys.stdout.flush()
                return {"outcome": "stopped", "elapsed_sec": int(elapsed), "paused_sec": paused_sec, "added_sec": added_sec}

            elif key == "a":
                total += 300
                added_sec += 300
                sys.stdout.write("\n+5 min added.\n")
                sys.stdout.write(f"{HINTS}\n")
                sys.stdout.flush()

            else:
                elapsed += tick

        sys.stdout.write("\n\a")
        sys.stdout.flush()
        return {"outcome": "completed", "elapsed_sec": int(elapsed), "paused_sec": paused_sec, "added_sec": added_sec}

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def write_journal(project, task, work_min, break_min, paused_sec=0, added_sec=0):
    now = datetime.now()
    entry = (
        f"---\n"
        f"date: {now.strftime('%Y-%m-%d')}\n"
        f"time: {now.strftime('%H:%M')}\n"
        f"project: {project}\n"
        f"task: {task}\n"
        f"work_min: {work_min}\n"
        f"break_min: {break_min}\n"
    )
    if paused_sec:
        entry += f"paused_min: {round(paused_sec / 60)}\n"
    if added_sec:
        entry += f"added_min: {round(added_sec / 60)}\n"

    journal_dir = Path(__file__).parent / "journal"
    by_day = journal_dir / "by-day" / f"{now.strftime('%Y-%m-%d')}.md"
    by_project = journal_dir / "by-project" / f"{project}.md"
    try:
        by_day.parent.mkdir(parents=True, exist_ok=True)
        by_project.parent.mkdir(parents=True, exist_ok=True)
        for path in (by_day, by_project):
            with open(path, "a") as f:
                f.write(entry + "\n")
    except OSError as e:
        print(f"Warning: could not write journal: {e}", file=sys.stderr)


def handle_interrupt(sig, frame):
    print("\nPomodoro interrupted.")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Task 001 – Journal parser
# ---------------------------------------------------------------------------

@dataclass
class JournalEntry:
    date: dt.date
    time: str
    project: str
    task: str
    work_min: int


def parse_journal_file(path):
    entries = []
    try:
        text = Path(path).read_text()
    except OSError:
        return entries

    blocks = text.split("---")
    line_offset = 0
    for block in blocks:
        raw_lines = block.split("\n")
        fields = {}
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                fields[key.strip()] = val.strip()

        if not fields:
            line_offset += len(raw_lines)
            continue

        try:
            entry = JournalEntry(
                date=dt.date.fromisoformat(fields["date"]),
                time=fields["time"],
                project=fields["project"],
                task=fields["task"],
                work_min=int(fields["work_min"]),
            )
            entries.append(entry)
        except (KeyError, ValueError):
            print(
                f"Warning: skipping malformed entry in {path} near line {line_offset}",
                file=sys.stderr,
            )
        line_offset += len(raw_lines)

    return entries


def load_journal_entries(journal_dir, start_date, end_date):
    by_day = Path(journal_dir) / "by-day"
    if not by_day.exists():
        return []

    entries = []
    for p in sorted(by_day.glob("????-??-??.md")):
        try:
            file_date = dt.date.fromisoformat(p.stem)
        except ValueError:
            continue
        if start_date <= file_date <= end_date:
            entries.extend(parse_journal_file(p))

    entries.sort(key=lambda e: (e.date, e.time))
    return entries


# ---------------------------------------------------------------------------
# Task 002 – Time interval resolution
# ---------------------------------------------------------------------------

_VALID_KEYWORDS = ("today", "yesterday", "this-week", "last-week", "this-month", "last-month")


def resolve_interval(keyword):
    today = dt.date.today()
    if keyword == "today":
        return today, today
    if keyword == "yesterday":
        d = today - dt.timedelta(days=1)
        return d, d
    if keyword == "this-week":
        start = today - dt.timedelta(days=today.weekday())
        return start, today
    if keyword == "last-week":
        start = today - dt.timedelta(days=today.weekday() + 7)
        end = start + dt.timedelta(days=6)
        return start, end
    if keyword == "this-month":
        return today.replace(day=1), today
    if keyword == "last-month":
        first_of_current = today.replace(day=1)
        last_of_prev = first_of_current - dt.timedelta(days=1)
        first_of_prev = last_of_prev.replace(day=1)
        return first_of_prev, last_of_prev
    raise ValueError(
        f"Error: unknown interval '{keyword}'. Valid intervals: {', '.join(_VALID_KEYWORDS)}."
    )


def resolve_date_range(interval_keyword, from_date, to_date):
    today = dt.date.today()
    has_keyword = interval_keyword is not None
    has_explicit = from_date is not None or to_date is not None

    if has_keyword and has_explicit:
        print("Error: cannot combine an interval keyword with --from/--to.", file=sys.stderr)
        sys.exit(1)

    if has_keyword:
        try:
            return resolve_interval(interval_keyword)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    if has_explicit:
        start = from_date
        end = to_date if to_date is not None else today
        if start > end:
            print("Error: --from date must be on or before --to date.", file=sys.stderr)
            sys.exit(1)
        return start, end

    # default
    return today, today


# ---------------------------------------------------------------------------
# Task 003 – ASCII renderer
# ---------------------------------------------------------------------------

def _fmt_duration(minutes):
    if minutes == 0:
        return "0m"
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def render_report(entries, start_date, end_date, projects_filter):
    if not entries:
        print("No entries found for the given period.")
        return

    multi_day = start_date != end_date

    # Header
    projects_label = ", ".join(sorted(projects_filter)) if projects_filter else "all"
    print(f"Report: {start_date} to {end_date}")
    print(f"Projects: {projects_label}")

    # Per-project totals
    totals = {}
    for e in entries:
        totals[e.project] = totals.get(e.project, 0) + e.work_min

    print("\n== Per-Project Totals ==\n")
    proj_col = max((len(p) for p in totals), default=10) + 2
    for proj in sorted(totals):
        dur = _fmt_duration(totals[proj])
        print(f"  {proj:<{proj_col}}{dur}")

    # Daily breakdown (multi-day only)
    if multi_day:
        from collections import defaultdict
        daily = defaultdict(lambda: defaultdict(int))
        for e in entries:
            daily[e.date][e.project] += e.work_min

        print("\n== Daily Breakdown ==\n")
        for day in sorted(daily):
            print(f"  {day}")
            for proj in sorted(daily[day]):
                dur = _fmt_duration(daily[day][proj])
                print(f"    {proj:<{proj_col}}{dur}")

    # Tasks list
    print("\n== Tasks ==\n")
    date_col = 10
    task_col = 30
    for e in entries:
        dur = _fmt_duration(e.work_min)
        proj_part = f"{e.project:<{proj_col}}"
        task_part = f"{e.task:<{task_col}}"
        line = f"  {e.date}  {proj_part}{task_part}{dur}"
        print(line[:80])


def run_report(argv):
    parser = argparse.ArgumentParser(prog="pomodoro report")
    parser.add_argument("interval", nargs="?", default=None,
                        help="Predefined interval: today, yesterday, this-week, last-week, this-month, last-month")
    parser.add_argument("--from", dest="from_date", metavar="DATE",
                        help="Start date YYYY-MM-DD (inclusive)")
    parser.add_argument("--to", dest="to_date", metavar="DATE",
                        help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--project", metavar="LIST",
                        help="Comma-separated project names to include")

    opts = parser.parse_args(argv)

    def parse_date(s, flag):
        try:
            return dt.date.fromisoformat(s)
        except ValueError:
            print(f"Error: invalid date for {flag}: '{s}'. Expected YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

    from_date = parse_date(opts.from_date, "--from") if opts.from_date else None
    to_date = parse_date(opts.to_date, "--to") if opts.to_date else None

    start_date, end_date = resolve_date_range(opts.interval, from_date, to_date)

    projects_filter = None
    if opts.project:
        projects_filter = [p.strip() for p in opts.project.split(",") if p.strip()]

    journal_dir = Path(__file__).parent / "journal"
    if not journal_dir.exists():
        print("No journal data found.")
        return

    entries = load_journal_entries(journal_dir, start_date, end_date)
    if projects_filter:
        entries = [e for e in entries if e.project in projects_filter]

    render_report(entries, start_date, end_date, projects_filter)


def main():
    signal.signal(signal.SIGINT, handle_interrupt)

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        run_report(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(
        prog="pomodoro",
        description="CLI pomodoro timer",
        usage="%(prog)s [--work N] [--break N] [project] task",
    )
    parser.add_argument("--work", type=int, default=25, metavar="N", help="work duration in minutes (default: 25)")
    parser.add_argument("--break", dest="brk", type=int, default=5, metavar="N", help="break duration in minutes (default: 5)")
    parser.add_argument("args", nargs="*")

    opts = parser.parse_args()
    positional = opts.args

    state = load_state()

    if len(positional) == 2:
        project, task = positional
    elif len(positional) == 1:
        task = positional[0]
        project = state.get("last_project")
        if not project:
            print("Error: no project specified and no previous project found.", file=sys.stderr)
            print("Usage: pomodoro [--work N] [--break N] <project> <task>", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    state["last_project"] = project
    save_state(state)

    header = f"► {project} — {task}  [{opts.work}m work / {opts.brk}m break]"
    print(header[:40])

    total_paused = 0
    total_added = 0

    work_result = run_timer(opts.work * 60, "Work")
    total_paused += work_result["paused_sec"]
    total_added += work_result["added_sec"]
    work_min_actual = max(1, round(work_result["elapsed_sec"] / 60))

    if work_result["outcome"] == "cancelled":
        return
    if work_result["outcome"] == "stopped":
        write_journal(project, task, work_min_actual, 0, total_paused, total_added)
        return

    print("Work done! Break time.")

    break_result = run_timer(opts.brk * 60, "Break")
    total_paused += break_result["paused_sec"]
    total_added += break_result["added_sec"]
    break_min_actual = max(1, round(break_result["elapsed_sec"] / 60))

    if break_result["outcome"] == "cancelled":
        return

    write_journal(project, task, work_min_actual, break_min_actual, total_paused, total_added)
    print("Break over. Well done!")


if __name__ == "__main__":
    main()
