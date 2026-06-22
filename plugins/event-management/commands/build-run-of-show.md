---
description: "Build a minute-by-minute run-of-show with an owner per row, plus logistics, registration ops, and a plan-B per single point of failure."
argument-hint: "[event/day + format + key segments]"
---

You are running `/event-management:build-run-of-show`. Use `event-operations-lead` + the `build-run-of-show` skill.

## Steps
1. Lay out the timed show-flow — real clock times, durations that sum, a cue and a named owner/role on every row.
2. Capture venue/vendor/AV logistics, call times, and load-in/out.
3. Size registration/check-in for peak arrival; name the system-down and walk-up fallbacks.
4. Write a plan B for every single point of failure (speaker, stream, power, key staff) — trigger + fallback + owner.
5. Emit using `templates/run-of-show.md` + the Structured Output block.
