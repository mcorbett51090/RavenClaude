# Broken Appointment Rate Is the Schedule Efficiency Warning

**Status:** Primary diagnostic
**Domain:** Dental practice operations — schedule management
**Applies to:** `dental-practice`

---

## Why this exists

A broken appointment (cancellation without reschedule or no-show) is lost production with fixed overhead already committed — the chair cost, the provider time, and the assistant time are sunk the moment the slot empties. Industry benchmark for broken appointment rate is ≤5% of scheduled appointments; practices running 8–12% or higher are losing 3–7% of their potential daily production with no offsetting cost reduction. [unverified — training knowledge] The broken appointment rate is also a leading indicator of patient dissatisfaction and engagement: a rising rate before a revenue decline is a retention problem in early stages.

## How to apply

**How to calculate:**

```
Broken Appointment Rate = (No-shows + Same-Day Cancellations) / Total Scheduled Appointments × 100

Measure over a rolling 30-day window, by provider and by appointment type.
```

**Threshold triage:**

| Rate | Signal | Response |
|---|---|---|
| < 5% | Healthy | Monitor monthly |
| 5–8% | Watch zone | Identify top offenders by appointment type; add confirmation protocol |
| 8–12% | Diagnostic | Audit confirmation workflow; check reactivation lag; review patient satisfaction signals |
| > 12% | Active revenue threat | Escalate: consider a same-day fill list, a deposit policy for high-value procedures, or a targeted reactivation call campaign |

**Root-cause drill-down:**
1. Segment by appointment type — hygiene no-shows are usually different from restorative no-shows.
2. Segment by patient history — first-time patients vs. established patients have different drivers.
3. Segment by time-of-day — early morning and last-slot-of-day are highest-risk.
4. Check confirmation lead time — less than 48-hour confirmation correlates with higher no-show rates.

**Interventions ranked by cost-effectiveness:**
1. **Two-touch confirmation** — automated reminder at 72 hrs + staff call at 24 hrs; fastest, cheapest intervention.
2. **Same-day fill list** — maintain a running list of patients with unscheduled urgent treatment who want first-available call.
3. **Deposit policy** — for crown/implant/long restorative appointments, a lab-fee deposit reduces no-show rate significantly (confirm local norms and patient communication).
4. **Broken appointment fee policy** — enforce only where the practice has communicated it clearly in writing at intake.

**Do:**
- Track broken appointment rate by provider and appointment type, not as a single practice average.
- Review and act on the same-day fill list every morning during the huddle.
- Distinguish same-day cancellations that were rescheduled (recoverable) from true no-shows (production lost).

**Don't:**
- Use the broken appointment rate as a disciplinary number before diagnosing whether the confirmation workflow is the actual cause.
- Over-book to compensate for no-shows — double-booking to cover a 10% broken rate degrades care and creates scheduling chaos on low-no-show days.
- Accept a rising broken appointment rate as "just patient behavior" without investigating the confirmation and scheduling protocol.

## Edge cases / when the rule does NOT apply

Emergency-only and urgent-care practices have structurally higher same-day utilization and different appointment types; apply the broken-appointment rate separately to scheduled vs. walk-in slots. Pediatric practices may see seasonally elevated no-show rates during school holidays that are not a practice-management problem.

## See also
- [`../agents/dental-operations-analyst.md`](../agents/dental-operations-analyst.md) — builds the schedule-efficiency metrics including broken appointment rate.
- [`../agents/dental-practice-lead.md`](../agents/dental-practice-lead.md) — routes the diagnostic to operations or to the clinical planner if case complexity is driving avoidance.

## Provenance

Codifies standard dental operations management practice; benchmarks are [unverified — training knowledge] and should be validated against the practice's own PMS data and peer benchmarks.

---

_Last reviewed: 2026-06-05 by `claude`_
