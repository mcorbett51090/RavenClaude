# Schedule Utilization Measures Whether Capacity Is Reaching Patients

**Status:** Pattern
**Domain:** Scheduling / practice capacity
**Applies to:** `dental-practice`

---

## Why this exists

A practice can have a full appointment book and still be under-producing if the schedule is built with low-value fill (short appointments, hygiene recare gaps, end-of-day holes) rather than high-value operative cases. Schedule utilization — the ratio of productive chair time to available chair time — surfaces this problem where production-per-hour cannot alone. A dentist running at 65% schedule utilization with large blocks of buffer time and broken appointments is not a production problem; it is a scheduling architecture problem. Misdiagnosing it as a case-acceptance or PPO problem leads to the wrong interventions.

## How to apply

Measure schedule utilization by tracking filled chair-time against available chair-time, segmented by appointment type.

```
Schedule utilization scorecard:
- Available chair-time: hours in the schedule template (excluding lunch, admin blocks)
- Productive chair-time: hours actually used for patient treatment in the same period
- Utilization % = productive / available × 100
  Target: ≥85% for a healthy practice [unverified — training knowledge]

Segmented view (minimum monthly):
  - Dentist chair utilization: operative vs. check/exam time ratio
  - Hygiene chair utilization: recall + perio + new patient time ratio
  - Broken appointments + short-notice cancellations as % of available slots

Red flags:
  - Utilization < 75% for 2+ consecutive months
  - >15% of available slots affected by broken appointments or same-day cancellations
  - End-of-day or post-lunch "open chair" pattern recurring weekly
```

**Do:**
- Build the appointment template with intent — designate "high-value operative" slots in the morning and fill them before adding shorter appointments.
- Track broken-appointment rate by appointment type; high-value operative cases that break cause disproportionate production loss.
- Reconcile schedule utilization against production per hour monthly — low utilization AND low production per hour confirm a capacity-architecture problem; high utilization AND low production per hour suggest a fee or payer-mix problem.

**Don't:**
- Count "blocked" time (provider PTO, CE days) as broken appointments — clean the schedule template before computing utilization.
- Treat schedule utilization as equivalent to busyness — a fully booked hygiene column of 30-minute cleanings is high utilization but may be low-value if the perio protocol is under-applied.
- Compare utilization across practices without normalizing for hours-open per week.

## Edge cases / when the rule does NOT apply

Specialty practices (oral surgery, orthodontics) with appointment structures very different from GP — procedure times are longer and utilization benchmarks differ. Use segment-specific benchmarks.

## See also

- [`../agents/dental-operations-analyst.md`](../agents/dental-operations-analyst.md) — owns practice scorecard and production analytics including schedule utilization.
- [`./production-per-hour-is-the-capacity-lens.md`](./production-per-hour-is-the-capacity-lens.md) — production per hour is the output of utilization × fee — read both together.

## Provenance

Standard dental practice operations management; grounded in published scheduling-efficiency frameworks from Dental Economics and ADA practice management guidance; the 85% utilization target is a commonly cited benchmark — verify against a current source before using in a client deliverable.

---

_Last reviewed: 2026-06-05 by `claude`_
