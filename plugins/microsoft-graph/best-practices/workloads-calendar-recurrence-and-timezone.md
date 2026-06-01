# Read recurring calendar events with calendarView — and pin the time zone

**Status:** Primary diagnostic — when an app shows wrong/missing event times or only one occurrence of a recurring series, check the read shape and the time-zone header first.

**Domain:** Web API / Outlook workloads

**Applies to:** `microsoft-graph`

---

## Why this exists

Recurring events are the single most common source of calendar bugs on Graph. `GET /events` returns the **series master** (one object with a `recurrence` rule) plus any single events — it does **not** expand the series into individual occurrences. Code that lists `/events` and renders them shows one row for a weekly meeting, not the 52 instances the user expects. Separately, Graph returns and accepts times in UTC by default; without an explicit time-zone preference an app silently renders everything in UTC and every displayed time is wrong for the user.

## How to apply

**To read what's on the calendar in a window, use `calendarView`** — it expands recurrence into individual occurrences between `startDateTime` and `endDateTime`. Use `/events` only when you specifically want the series master (e.g. to edit the recurrence rule).

```http
# expanded occurrences in a date window — the right read for "what's on my calendar"
GET /me/calendarView?startDateTime=2026-06-01T00:00:00Z&endDateTime=2026-06-30T23:59:59Z&$select=subject,start,end,type
Prefer: outlook.timezone="Pacific Standard Time"
# start/end now come back in PST; event.type tells you master vs occurrence vs exception

# editing the series vs one instance:
PATCH /me/events/{seriesMasterId}     # changes the whole series
PATCH /me/events/{occurrenceId}       # creates/updates a single-instance exception
```

**Do:**

- Use `calendarView` (with a bounded window) to display "what's happening"; it expands the series for you.
- Send `Prefer: outlook.timezone="<Windows tz name>"` on every calendar read/write whose times you display.
- Distinguish `event.type` = `seriesMaster` / `occurrence` / `exception` / `singleInstance` before editing — patch the master to change all, an occurrence to change one.

**Don't:**

- List `/events` and assume you have every occurrence — you have masters + singles only.
- Render times without a time-zone Prefer header (you'll show UTC).
- Patch the series master when the user meant "just move this one meeting" (or vice-versa).

## Edge cases / when the rule does NOT apply

`calendarView` requires a bounded date window and is capped (paginate large windows). The `Prefer: outlook.timezone` value uses **Windows** time-zone names (e.g. `"Pacific Standard Time"`), not IANA (`America/Los_Angeles`) on v1.0 `[verify-at-build]`. For "what changed in my calendar," prefer a delta query or subscription over re-reading `calendarView` on a timer (house opinion #6). Single, non-recurring events don't need `calendarView` — a direct `/events/{id}` is fine.

## See also

- [`./workloads-use-immutable-ids-for-stored-references.md`](./workloads-use-immutable-ids-for-stored-references.md) — store the `event` ID as immutable
- [`./api-delta-for-what-changed.md`](./api-delta-for-what-changed.md) — for change detection, not polling calendarView
- [`../knowledge/workloads-notifications-decision-trees.md`](../knowledge/workloads-notifications-decision-trees.md) — the recurring-event read tree
- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns mail/calendar
- [Get calendar view / Outlook calendar](https://learn.microsoft.com/graph/api/calendar-list-calendarview) — authoritative

## Provenance

From the Microsoft Learn calendar pages (`calendarView`, recurrence, `Prefer: outlook.timezone`), retrieved 2026-05-30 via Microsoft Learn MCP. Codifies the recurring-event/time-zone footguns the workloads agent had no citable rule for. Windows-vs-IANA tz-name support is version-sensitive — `[verify-at-build]`. Surfaced by the two-panel coverage audit 2026-06-01.

---

_Last reviewed: 2026-06-01 by `claude`_
