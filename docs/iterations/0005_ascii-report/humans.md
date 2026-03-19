# 0005 – ASCII Report

## Description
Add a `report` command to the pomodoro CLI that reads journal entries and prints a plain-text summary to the terminal. The report shows total time per project, a per-day breakdown when the interval spans multiple days, and a list of tasks completed. Users can filter by time interval (predefined keywords like "today", "this-week", or explicit --from/--to dates) and by one or more projects.

## Rationale
The journal already captures every completed session, but there is no way to review accumulated work without manually reading the raw files. A built-in report command closes the feedback loop: users can see at a glance how much time they spent, on what, and when. Keeping the output ASCII-only ensures it works in any terminal and is easy to pipe or redirect.
