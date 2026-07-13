---
name: optimize-throughput-and-staffing
description: Turn an urgent-care center's wait-time and staffing picture into a throughput plan by segmenting door-to-door time (door-to-triage, triage-to-provider, provider-to-discharge) and attacking the longest segment, designing the split-flow/fast-track model before buying labor, and staffing the provider + MA/tech matrix to the intraday and seasonal demand curve using provider productivity (patients per provider-hour), returning the recommended moves with the projected wait-time and throughput lift and the conditions that would flip them. Reach for this when the user asks "my wait times are killing my reviews", "split-flow or a single queue?", "how do I staff the afternoon or respiratory-season surge?", or "why is my full waiting room moving so slowly?". Used by `urgent-care-operations-lead` (primary).
---

# Skill: optimize-throughput-and-staffing

> **Invoked by:** `urgent-care-operations-lead` (primary). Also consulted by `urgent-care-revenue-and-payer-specialist` for the throughput/capacity the occ-med line and payer volume demand.
>
> **When to invoke:** "My wait times are killing my reviews"; "split-flow vs single queue"; "how do I staff the afternoon / respiratory-season surge?"; "why is my full waiting room moving slowly?"; any move from a wait-time/staffing picture to a throughput plan.
>
> **Output:** the door-to-door segmentation (which segment is longest) + the split-flow/fast-track design + the provider + MA/tech matrix against the intraday/seasonal curve + provider productivity + projected wait-time/throughput lift + the 1-2 flip conditions. Capture it in [`../../templates/urgent-care-throughput-and-staffing-plan.md`](../../templates/urgent-care-throughput-and-staffing-plan.md).

## Procedure

1. **Segment door-to-door time before touching staffing.** Split total arrival-to-discharge into **door-to-triage**, **triage-to-provider**, and **provider-to-discharge**. The **longest segment** is the diagnostic — a long triage-to-provider wait is a flow/coverage problem, a long provider-to-discharge wait is an ancillary-turnaround/documentation problem. Don't reflexively add headcount. See [`../../knowledge/urgent-care-patterns-2026.md`](../../knowledge/urgent-care-patterns-2026.md).
2. **Design the flow before buying the labor.** Evaluate a **split-flow / fast-track** model — a low-acuity fast-track (simple, no-imaging visits, often vertical/chair flow) in parallel with a main flow for imaging/lab workups — plus front-end patterns (provider-in-triage / rapid medical evaluation). A right-sized flow usually shrinks the staffing ask.
3. **Map the demand curve — both shapes.** Chart the **intraday** curve (afternoon/evening peak, weekend peak) and the **seasonal** curve (respiratory-season surge). Flat staffing over-pays the trough and buckles at the peak.
4. **Size the provider + MA/tech matrix with provider productivity.** Use **patients per provider-hour** to convert the visit volume at each hour/season into provider-hours, then lay the MA/tech support against it. Contract a **flex pool** (per-diem/PRN, cross-trained MA/tech) ahead of respiratory season.
5. **Attack the longest segment with the matched lever.** Door-to-triage → registration/greeter/online check-in; triage-to-provider → split-flow + provider coverage + room turnover; provider-to-discharge → ancillary turnaround (route the x-ray/POCT capacity question to `design-ancillary-services-and-scope`), documentation/EMR efficiency, discharge process.
6. **Project the lift and state the flip conditions.** Estimate the wait-time and throughput improvement from the flow + staffing moves, and name the 1-2 facts that would change the plan (e.g. "if the payer/occ-med mix shifts volume to scheduled occ-med in the morning trough, the intraday matrix changes").

## Worked example

> User: "Our waiting room is always full and the reviews all mention the wait. Do I need to hire another provider?"

- **Door-to-door segmentation:** total visit time 78 min; door-to-triage 6 min, **triage-to-provider 44 min**, provider-to-discharge 28 min. The pain is triage-to-provider — a *flow* problem, not a raw provider-count problem.
- **Flow design:** stand up a **fast-track** for low-acuity visits (roughly the lower-acuity share of volume) so simple visits stop queuing behind imaging workups; add provider-in-triage at the afternoon peak.
- **Demand curve:** volume peaks 3–7pm and roughly doubles in respiratory season; current staffing is flat.
- **Staffing matrix:** with provider productivity ~2.5 patients/provider-hour, the peak needs a second provider *only 3–7pm* plus an added MA — cheaper and more effective than a full-time second provider all day. Contract a PRN provider for respiratory season.
- **Flip condition:** if a new occ-med contract loads scheduled morning volume, re-balance the matrix toward the morning.

## Guardrails

- Never prescribe a staffing add before segmenting door-to-door time — the longest segment selects the lever.
- Design the split-flow/fast-track *before* buying labor — flow usually reduces the headcount ask.
- Staff to the intraday *and* seasonal curve, sized by provider productivity — never to an average.
- Provider-to-discharge waits often route to ancillary turnaround and scope (`design-ancillary-services-and-scope`) and to visit economics (the revenue specialist) — name the seam, don't absorb it.
- Scope-of-service and any clinical staffing-model question is set **with the medical director** — this skill frames the operational trade-offs, not the clinical call.
- Volatile claims (EMR/PM features, UCA staffing/wait-time benchmarks, provider-productivity ranges) carry a **retrieval date** — re-verify before a client commitment.
