---
name: registration-and-attendee-ops
description: "Registration and attendee operations: model the funnel (reach -> visit -> register -> confirm -> attend) not a headcount, then run check-in as a throughput operation — lanes, staffing, badge/QR flow sized for peak arrival with a system-down fallback."
---

# Registration & Attendee Ops

Two halves: the **funnel** (marketing/revenue) and the **operation** (day-of). Both matter.

## The funnel (not a headcount)

```
reach → page visit → register → confirm → attend
```

Each arrow is a conversion rate. A single "we need 500" hides the leak. Track stage-by-stage; fix the leaking stage. Account for **attrition** — registered ≠ attended (no-show rates vary by format; virtual is typically higher).

## The check-in operation

- **Size for peak arrival**, not average — arrivals bunch before the keynote.
- Plan lanes, staffing, and a badge/QR flow that scans fast.
- Have a **system-down fallback** (printed list, manual badges) and a **walk-up** path.
- For virtual/hybrid: the "door" is the join link and the platform login — test it, and staff a help channel for login failures.

## Anti-patterns
- Treating registration as one number instead of a funnel.
- Sizing check-in for average, getting a line out the door at peak.
- No fallback when the registration system or join link fails.

The funnel optimization is `event-marketing-revenue`'s; the check-in throughput is `event-operations-lead`'s. See [`../post-event-measurement/SKILL.md`](../post-event-measurement/SKILL.md) for measuring attend-rate against target.
