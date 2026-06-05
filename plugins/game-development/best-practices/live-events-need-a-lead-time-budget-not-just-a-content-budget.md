# Live events need a lead-time budget, not just a content budget

**Status:** Pattern
**Domain:** Game live-ops
**Applies to:** `game-development`

---

## Why this exists

Live-ops events are the content and retention engine for a live-service game. The most common live-ops failure is not a bad event design — it is running out of lead time. A holiday event that takes 8 weeks to develop requires a greenlight in early October for a December delivery. A studio that sizes its live-events roadmap by content cost without modeling the lead-time requirement ends up shipping under-tested events, shipping nothing during key seasonal windows, or burning the team on crunch to compensate for calendar planning that didn't account for the development pipeline. Lead time is as real a constraint as content cost, and it must be planned before the events calendar is committed.

## How to apply

For each event type in the live-ops roadmap, define the lead-time budget (development + QA + delivery pipeline) and plan the events calendar backward from the target live date.

```
Live-event lead-time model:

  Event type | Content scope | Typical lead time | Notes
  ---|---|---|---
  Minor event (reskinned content, loot table update) | low | 2–3 weeks | mostly QA + submission
  Standard event (new challenges + cosmetics) | medium | 4–6 weeks | design + art + QA
  Major event (new mechanic + story chapter + economy change) | high | 8–12 weeks | full pipeline
  Seasonal event (holiday + limited currency + marketing tie-in) | high | 10–16 weeks | marketing sync adds 2–4 weeks

  Calendar-planning rule:
    Target live date for each event → subtract lead time → greenlight/kick-off date
    Never commit a live date without confirming the kick-off date is within team capacity.

  Platform submission overhead (add to lead time):
    iOS App Store: 3–7 days (variable)
    Google Play: 1–3 days
    Console certification: 3–10+ business days (first parties vary)

  Buffer rule: add 20% to the estimated lead time for any event with a new mechanic or first-time asset category.
```

**Do:**
- Build the live-events calendar backward from key dates (holidays, anniversaries, store cycles) using the lead-time model.
- Include platform submission lead time in every event's delivery plan.
- Flag any event whose kick-off date falls inside a milestone crunch as a scheduling conflict, not a stretch target.

**Don't:**
- Commit to a seasonal live date without confirming the greenlight date is outside team crunch.
- Use the same lead-time estimate for a minor event and a major mechanic addition.
- Treat platform submission as zero-time; it is often 1–10 days of hard pipeline time the team can't control.

## Edge cases / when the rule does NOT apply

Server-side-only events (no client update required, fully configurable from the dashboard) have near-zero lead time once the framework exists — they still need QA but skip the submission pipeline. Very small teams doing all server-side live-ops may have faster lead times; calibrate to the actual pipeline, not generic industry estimates.

## See also

- [`../agents/live-ops-analyst.md`](../agents/live-ops-analyst.md) — reads the live-ops vital signs that determine which events are worth the lead-time investment.
- [`./live-service-is-an-operating-model-not-a-launch.md`](./live-service-is-an-operating-model-not-a-launch.md) — the parent rule establishing the live-ops operating model that the events calendar serves.

## Provenance

Codifies the lead-time budgeting discipline for live-service game teams. The calendar-commitment-without-lead-time-model error is the most common root cause of under-tested seasonal events; the backward-planning discipline from target live date is the standard correction.

---

_Last reviewed: 2026-06-05 by `claude`_
