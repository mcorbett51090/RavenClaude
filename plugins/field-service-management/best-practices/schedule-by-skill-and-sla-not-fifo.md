# Schedule by skill and SLA, not FIFO

**Status:** Pattern
**Domain:** Dispatch and scheduling
**Applies to:** `field-service-management`

---

## Why this exists

A first-in, first-out dispatch queue ignores the two most important axes of a service job: the
urgency (SLA tier) and the competency required (skill match). The consequences of FIFO dispatch
are predictable and recurring: a premium-SLA emergency waits behind a next-day routine job; a
technician is dispatched to a refrigerant job without EPA 608 certification; a high-skill technician
is sent to a basic filter change while a complex chiller sits unassigned. Every one of these is a
first-time-fix risk and an SLA miss in waiting.

Scheduling by skill and SLA is not sophisticated — it is the minimum viable dispatch logic. The
pattern is: SLA tier sets priority, skill match is a hard filter, geographic density breaks ties.
In that order, every time.

## How to apply

- **SLA tier sets priority.** P0 (emergency) pre-empts everything. P1 (premium SLA) pre-empts P2
  and below. P4 (planned PM) is the last to be assigned. This ordering is non-negotiable.
- **Skill match is a hard constraint, not a preference.** The dispatch board must filter out
  technicians who do not hold the required certification or equipment authorization for the job.
  A technician who cannot legally or safely perform the work is not an option for that job.
- **Geographic density breaks ties.** After priority and skill match, assign the job to the
  qualified technician whose route produces the highest jobs-per-drive-hour for the remainder
  of the day.

**Do:**

- Build and maintain a technician-skills matrix with certifications, equipment authorizations,
  and SLA-tier authorizations for each technician.
- Configure the dispatch board to enforce skill match as a hard filter before surfacing
  available technicians.
- Review SLA attainment by tier weekly; if P1/P2 misses are rising, check whether the root
  cause is a skill-coverage gap or a scheduling-logic failure.

**Don't:**

- Default to FIFO "because it's simple." Simple dispatch logic that produces callbacks and
  SLA misses is more expensive than correct logic.
- Treat skill match as an advisory that a dispatcher can override without a documented reason.
- Assign a job to the nearest available technician without checking skill match first.

## Edge cases / when the rule does NOT apply

In a true emergency where no skill-matched technician is available and life/safety is at risk,
the nearest available technician may be dispatched to stabilize the situation — with a follow-up
dispatch of a qualified technician for the actual repair. Document the stabilization-only scope
clearly; it is not a first-time-fix attempt.

## See also

- [`./first-time-fix-is-the-master-metric.md`](./first-time-fix-is-the-master-metric.md)
- [`../knowledge/fsm-decision-trees.md`](../knowledge/fsm-decision-trees.md) (schedule-priority tree)
- [`../skills/dispatch-and-scheduling/SKILL.md`](../skills/dispatch-and-scheduling/SKILL.md)

## Provenance

Reflects dispatch-optimization principles from field-service management literature and platform
design (ServiceTitan, Salesforce Field Service, IFS) — all route dispatching through SLA priority
and skill match as the primary filters before any geographic or availability optimization.
`[verify-at-use]`

---

_Last reviewed: 2026-06-08 by `claude`._
