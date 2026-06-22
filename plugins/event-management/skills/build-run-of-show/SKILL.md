---
name: build-run-of-show
description: "Build a minute-by-minute run-of-show / show-flow: a timed table with a row per segment — time, duration, what happens, the cue, and a named owner/role — plus the contingency plan-Bs for the day-of."
---

# Build Run-of-Show

A run-of-show is a **timed table**, not an agenda. One row per segment, an owner on every row.

## The columns (minimum)

| Time | Duration | Segment | Cue / Tech | Owner / Role |
|---|---|---|---|---|
| 08:30 | 30m | Doors / check-in | Lobby AV on, registration live | Ops lead |
| 09:00 | 5m | Welcome | Walk-in music down, mic 1 live | MC |
| 09:05 | 40m | Keynote | Slides up, stream record on | Speaker + AV |

## Rules
- **Minute-by-minute.** Real clock times and durations that add up, not "morning session".
- **An owner per row.** Every row names a person or role responsible. No owner → no one runs it.
- **Cues are explicit.** Mic, slides, lights, stream-record, transition music — written, so the AV/stage team can follow it cold.
- **Build buffers in.** Transitions and overruns are real; leave slack.

## Pair it with contingency
Every single point of failure (speaker, stream, power, key staff) needs a plan B with a trigger and an owner — keep it next to the run-of-show so the day-of team has both.

## Anti-patterns
- A run-of-show with no owner/role column.
- "Agenda" granularity (hour blocks) instead of segment-level timing.
- Cues left implicit ("AV will know").

Output via [`../../templates/run-of-show.md`](../../templates/run-of-show.md). For the go/no-go and format upstream, see [`../design-event-plan-and-budget/SKILL.md`](../design-event-plan-and-budget/SKILL.md).
