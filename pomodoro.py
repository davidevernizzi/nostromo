#!/usr/bin/env python3
import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.nostromo/state.json")


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
    for remaining in range(seconds, 0, -1):
        mm, ss = divmod(remaining, 60)
        sys.stdout.write(f"\r{label}: {mm:02d}:{ss:02d} remaining  ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n\a")
    sys.stdout.flush()


def write_journal(project, task, work_min, break_min):
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


def main():
    signal.signal(signal.SIGINT, handle_interrupt)

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

    print(f"Starting pomodoro: {project} — {task}")
    print(f"Work: {opts.work} min  |  Break: {opts.brk} min\n")

    run_timer(opts.work * 60, "Work")
    print("Work done! Break time.")

    run_timer(opts.brk * 60, "Break")
    write_journal(project, task, opts.work, opts.brk)
    print("Break over. Well done!")


if __name__ == "__main__":
    main()
