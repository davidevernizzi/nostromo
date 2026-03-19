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
