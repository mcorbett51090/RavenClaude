---
description: Set up, inspect, override, or remove the routine token reserve (keeps enough of the weekly cap for your claude.ai Routines).
allowed-tools: Bash, Read, Write, Edit, ToolSearch, AskUserQuestion
---

# /routine-reserve

Front door for the **routine token reserve**. Follow the `routine-reserve` skill
([`../skills/routine-reserve/SKILL.md`](../skills/routine-reserve/SKILL.md)) for the verb in `$ARGUMENTS`:

| Verb | Effect |
|---|---|
| `setup` | Wire the hourly meter Routine, the private data branch, the statusline reading and the posture knob. Confirms every outward step. |
| `status` (default) | Refresh and print the projected reserve, weekly usage, and per-Routine breakdown. |
| `override <pct>` | Hold exactly `<pct>`% for the rest of this week; reverts at the weekly reset. |
| `clear-override` | Return to the projected reserve. |
| `uninstall` | Remove the meter Routine and statusline wiring; the data branch is left in place and named. |

With no verb, run `status`.
