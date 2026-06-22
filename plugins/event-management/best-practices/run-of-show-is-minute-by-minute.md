# The run-of-show is minute-by-minute, with an owner per row

**Status:** Absolute rule
**Domain:** Event operations / production
**Applies to:** `event-management`

---

## Why this exists

A loose agenda ("morning sessions, lunch, afternoon panel") is a plan to improvise live. On the day, the show-caller, AV, and stage crew need to know — to the minute — what happens, when, what the cue is, and **who owns it**. A row with no owner is a moment with no one responsible to make it happen.

## How to apply

A timed table, one row per segment, minimum columns:

| Time | Duration | Segment | Cue / Tech | Owner / Role |
|---|---|---|---|---|
| 09:00 | 5m | Welcome | Walk-in music down, mic 1 live | MC |

**Do:**
- Use real clock times and durations that sum correctly.
- Name an owner or role on **every** row.
- Make cues explicit (mic, slides, lights, stream-record, transition music).
- Leave buffer in transitions.

**Don't:**
- Ship hour-block "agenda" granularity as a run-of-show.
- Leave any row without an owner column filled.

## Edge cases / when the rule does NOT apply

A 30-minute single-speaker webinar needs less granularity — but even then, the host, the cue, and the timing are written down.

## See also

- [`./have-a-plan-b-for-every-single-point-of-failure.md`](./have-a-plan-b-for-every-single-point-of-failure.md)
- [`../skills/build-run-of-show/SKILL.md`](../skills/build-run-of-show/SKILL.md)

## Provenance

Live-production show-calling practice. Codifies `event-operations-lead` house opinion ("a run-of-show without an owner column is an agenda").

---

_Last reviewed: 2026-06-22 by `claude`_
