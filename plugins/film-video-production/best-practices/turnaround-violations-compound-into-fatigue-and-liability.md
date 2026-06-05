# Turnaround violations compound into crew fatigue, safety risk, and liability

**Status:** Absolute rule
**Domain:** Film & video production / scheduling / crew safety / labor
**Applies to:** `film-video-production`

---

## Why this exists

Turnaround — the required minimum rest period between a crew member's dismissal and their next call time — exists in both union agreements (typically 8-10 hours minimum, with a "forced call" penalty when violated) and in occupational safety frameworks. Productions that routinely compress turnaround to save a day's schedule build up compounding fatigue risk: each consecutive short-turnaround day degrades crew judgment and reaction time, and the risk of a set accident increases. Beyond safety, a pattern of turnaround violations in a DPR record is a liability exposure if an on-set incident occurs on a fatigued crew, and a forced-call penalty on a union production is both a payroll cost and a producer credit-report item.

## How to apply

Track turnaround as a hard constraint in the schedule, not a goal:

```
Turnaround tracker — [Project] — Day __ — [Date]

Minimum required turnaround (per applicable agreement): ____ hours
                                                        (default: 10 hrs SAG-AFTRA main agreement)

For each crew member / cast:
  Name | Role | Day N wrap | Day N+1 call | Turnaround | Compliant? | Forced call auth
  ____ | ____ | __________ | ____________ | __________ | __________ | ________________
```

When a forced call is unavoidable:
1. Document the production need in the DPR.
2. Obtain explicit authorization from the UPM or line producer before issuing the call.
3. Notify the affected crew members before they wrap, not when their alarm fails to go off.
4. Budget the forced-call penalty as a known cost, not a surprise.

**Do:**
- Flag any day in the one-liner where the company move (travel between locations) plus anticipated wrap time leaves less than the required turnaround before the next day's call; solve it in scheduling, not on the day.
- Treat the turnaround as a floor, not a target — a crew that wraps early has a shorter actual day, but the turnaround requirement still governs the next-day call.
- For non-union productions, apply the same discipline as a safety and talent-retention practice even where no agreement requires it.

**Don't:**
- Schedule based on "planned wrap" rather than "realistic wrap"; a planned wrap that is routinely missed produces systematic turnaround violations.
- Omit turnaround violations from the DPR — documented violations are a management record; undocumented ones are a liability gap.
- Assume that a verbal "we're all good with it" from a fatigued crew member constitutes waiver of a union forced-call penalty; union agreements govern, not verbal agreements.

## Edge cases / when the rule does NOT apply

- Overnight shoots followed by a planned non-shoot day have no turnaround constraint to the next shoot day (only to the following call). Confirm the schedule explicitly builds the rest day.
- Split-schedule productions (half the crew on different shifts) have a different turnaround clock per shift; track each shift's turnaround separately.

## See also

- [`../agents/line-producer.md`](../agents/line-producer.md) — owns the schedule and is responsible for turnaround compliance.
- [`./one-liner-is-the-shoot-day-forcing-function.md`](./one-liner-is-the-shoot-day-forcing-function.md) — the one-liner is the surface where turnaround conflicts surface before the shoot day.
- [`./production-report-is-the-daily-legal-and-cost-record.md`](./production-report-is-the-daily-legal-and-cost-record.md) — forced calls and violations must appear in the DPR.

## Provenance

Derived from SAG-AFTRA and IATSE turnaround requirements, occupational safety standards for the film industry, and production management practice. `[unverified — training knowledge]` — validate forced-call penalties and minimum turnaround requirements against the applicable union agreement and state labor law.

---

_Last reviewed: 2026-06-05 by `claude`_
