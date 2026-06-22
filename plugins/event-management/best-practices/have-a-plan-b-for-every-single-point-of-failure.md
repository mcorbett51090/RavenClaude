# Have a plan B for every single point of failure

**Status:** Absolute rule
**Domain:** Event operations / contingency
**Applies to:** `event-management`

---

## Why this exists

Live events have moments where one thing breaking ends the event: the keynote speaker no-shows, the stream drops, the power fails, the registration system goes down, a key staffer is sick. The day-of is the worst possible time to invent the backup. A documented plan B — with a trigger and an owner — turns a disaster into a managed swap.

## How to apply

For every single point of failure, write:

| SPOF | Trigger | Fallback | Owner |
|---|---|---|---|
| Keynote speaker | No confirmation by T-7d / no-show | Backup speaker / pre-recorded / reshuffle agenda | Program lead |
| Live stream | Encoder/feed drops | Backup encoder + cellular bond; recorded fallback | AV lead |
| Power | Outage | Venue genset / UPS for critical AV | Venue + AV |

**Do:** identify SPOFs first (what, if it breaks, ends the event?), then back each one.
**Don't:** rely on "it'll be fine" for anything irreplaceable on the day.

## Edge cases / when the rule does NOT apply

Truly minor, gracefully-degrading elements (a nice-to-have breakout) don't each need a formal plan B — reserve the rigor for the single points of failure.

## See also

- [`./run-of-show-is-minute-by-minute.md`](./run-of-show-is-minute-by-minute.md)
- [`../templates/run-of-show.md`](../templates/run-of-show.md)

## Provenance

Live-production contingency practice. Codifies `event-operations-lead` house opinion ("the day-of is not when you invent the backup").

---

_Last reviewed: 2026-06-22 by `claude`_
