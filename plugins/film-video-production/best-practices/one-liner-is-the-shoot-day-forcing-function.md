# Maintain a one-liner for every shoot day — it is the forcing function for scheduling conflicts

**Status:** Absolute rule
**Domain:** Film & video production / scheduling
**Applies to:** `film-video-production`

---

## Why this exists

A shoot schedule that lives only in the line producer's head or in a full breakdown cannot be quickly scanned for day-level conflicts — double-booked cast, overlapping location holds, or a company move that leaves no turn-around time. The one-liner (a single-line summary for each shoot day listing the shoot date, scenes, location, cast members, and page count) is the scanning surface. It exposes conflicts that a full breakdown hides in its own density. A missing one-liner means scheduling conflicts surface on the day, when the cost of resolving them is highest.

## How to apply

Generate a one-liner from the strip board before any scheduling review:

```
One-liner — [Project title] — Draft [#] — [Date]

Day | Date    | Int/Ext | Scene #s      | Location          | Cast    | Pgs
--- | ------- | ------- | ------------- | ----------------- | ------- | ----
1   | Mon 1/6 | INT     | 12, 14, 15    | Office – Studio A | 1, 3    | 4-1/8
2   | Mon 1/6 | EXT     | 7             | Parking lot       | 1, 2, 4 | 2-2/8
3   | Tue 1/7 | INT     | 22, 23        | Kitchen – Studio B| 2, 5    | 3-4/8
```

Review the one-liner, not the full breakdown, as the primary conflict-detection surface:
- Cast appearing in overlapping days → reschedule before confirming the deal.
- Location appearing in two rows on the same calendar date → confirm it supports simultaneous units, or split the day.
- Page count per day vs. the project's historical or estimated pages-per-day → flag days that are over-packed before the schedule is locked.

**Do:**
- Regenerate the one-liner after every scheduling change, not just at the end of a revision cycle.
- Use it as the document shared with cast for availability confirmations — it is the right level of detail for that audience.
- Flag days where the total scene page count exceeds the project's realistic pages-per-day rate; those days are the overage risk pool.

**Don't:**
- Share the full breakdown with talent or location owners — it contains internal budget and production notes that are not for external parties.
- Lock the schedule before the one-liner has been reviewed against cast availability confirmations — availability is confirmed against dates, not against a breakdown.
- Treat the one-liner as the schedule; it is the scan surface, not the production bible.

## Edge cases / when the rule does NOT apply

- Single-location, minimal-cast productions (e.g., a two-person interview shoot) where all scenes are at one location can manage without a formal one-liner, though the conflict-detection discipline still applies.
- Second-unit schedules that are planned independently of the main unit should each have their own one-liner; merging them prematurely obscures company-move conflicts.

## See also

- [`../agents/line-producer.md`](../agents/line-producer.md) — generates and owns the one-liner as part of scheduling.
- [`./schedule-to-the-shoot-day-not-the-calendar.md`](./schedule-to-the-shoot-day-not-the-calendar.md) — the foundational rule this operationalizes at the day level.

## Provenance

Derived from standard production scheduling practice (strip board to one-liner workflow) and the line producer's scheduling methodology. `[unverified — training knowledge]` — validate page-per-day benchmarks against the project's specific format and genre.

---

_Last reviewed: 2026-06-05 by `claude`_
