---
name: build-scheduling-and-evv-workflow
description: "Build the visit schedule and the EVV workflow by traversing the home-health decision tree (plan of care + authorization → staffing match & caregiver continuity → visit schedule to ordered frequency/units → EVV capture: check-in/out via GPS/telephony/device per the state model → exception handling for missed/late/unverified visits), then return the continuity-staffed schedule, the EVV capture setup, and the exception procedure that keeps every visit billable and defensible. Reach for this when the user asks 'schedule this patient's visits', 'assign a caregiver for continuity', 'set up EVV', 'why is this visit unverified?', or 'handle a missed visit'. Used by home-care-operations-specialist (primary) and home-health-agency-lead."
---

# Skill: build-scheduling-and-evv-workflow

> **Invoked by:** `home-care-operations-specialist` (primary — the staffing match, schedule, and EVV setup) and `home-health-agency-lead` (when the staffing/capacity model turns on scheduling capacity and continuity).
>
> **When to invoke:** "schedule this patient's visits"; "assign a caregiver / keep continuity"; "set up EVV / Electronic Visit Verification"; "why is this visit unverified?"; "handle a missed / late visit"; "our EVV compliance is dropping"; any "who visits, when, and did we verify it" question.
>
> **Output:** the visit schedule matched to the plan of care & authorization + the continuity-first staffing assignment + the EVV capture setup (per the state model) + the exception-handling procedure for missed/late/unverified visits — so every visit is billable and defensible.

## Procedure

1. **Anchor the schedule on the plan of care and the authorization.** Build visits to the **ordered frequency/duration per discipline** (skilled HH) or the **authorized units/service type** (Medicaid waiver / private pay). Don't over-visit (unpaid past a capped authorization, and a finding) or under-visit (a LUPA risk under PDGM, and a plan-of-care-compliance finding). The plan of care is the contract; the schedule executes it.
2. **Match staff for continuity, not just coverage.** Traverse the staffing branch in [`../../knowledge/home-health-care-decision-tree.md`](../../knowledge/home-health-care-decision-tree.md): assign the **skill level the visit requires** (RN vs LPN vs therapist vs aide/caregiver), within travel/geography and availability — and prefer the **same familiar caregiver** across the episode. **Continuity of caregiver is the quality metric patients feel** (it shows up in HHCAHPS and retention); a revolving door of unfamiliar caregivers is the churn to design out.
3. **Set up EVV capture on every visit — it's the Cures Act mandate.** The 21st Century Cures Act requires **Electronic Visit Verification** for Medicaid personal-care and home-health services. Capture the six required elements: **type of service, individual receiving it, individual providing it, date, location, and check-in/out times**. Choose the capture method by the **state EVV model** (GPS/mobile app, telephony/IVR, or fixed device) and whether the state runs an **open model** (agency picks the vendor) or a **closed/state-mandated aggregator**. _(State EVV models vary — retrieval date on the specific state.)_
4. **Wire the EVV data flow.** Confirm visits flow from capture → the EVV vendor/aggregator → the claim, and that the captured visit **matches the authorization and the schedule** (right patient, right service, within the authorized window). A visit that's delivered but not verified — or verified but mismatched to the authorization — is a denial waiting to happen.
5. **Run an exception-handling procedure — same day, not month-end.** Every **missed, late, early, over/under-duration, GPS-mismatch, or manually-edited** visit is an exception: flag it, get the reason, correct or document it, and (for a genuinely missed visit) notify per the plan of care and reschedule. An unresolved EVV exception is an **unbillable visit and a compliance finding** — the exception queue is worked continuously, because it's the difference between a clean claim and a denial.
6. **Reconcile the schedule to actuals and to the authorization.** Weekly: scheduled vs delivered vs verified vs authorized. Under-delivery risks LUPA (PDGM) and plan-of-care compliance; over-delivery burns unpaid units; unverified delivery is unbillable. Tune staffing and the schedule from the reconciliation.
7. **State the exception/continuity conditions** — the 1-2 facts that would break the schedule (e.g., "the assigned caregiver resigns → continuity breaks → re-assign with a warm handoff, not a cold swap"; "the state's EVV aggregator changes → re-validate the data flow before the next billing cycle").

## Worked example

> User: "New skilled patient, SN 3x/week + aide 2x/week, Medicaid MCO. Build the schedule and make sure EVV holds up."

- **Anchor:** ordered SN 3x/wk (RN/LPN) + aide 2x/wk against the MCO **authorization** (units + service type + dates) — confirm the authorization covers both service types before scheduling.
- **Continuity match:** assign one **primary RN** and one **primary aide** for the episode (same faces), within travel radius; name a backup for coverage without breaking continuity on the routine visits.
- **EVV setup:** state runs a **closed model** → capture via the state aggregator's mobile app (GPS check-in/out) with telephony fallback for no-signal homes; the six data elements captured every visit.
- **Data flow:** visits flow capture → aggregator → claim, matched to the authorization; mismatches (wrong service code, out-of-window) held for review.
- **Exceptions:** a Tuesday aide visit checks in but not out → same-day flag → caregiver confirms and completes the check-out with a documented reason → visit becomes billable rather than lost.
- **Condition:** if the aide leaves, re-assign with a warm handoff (introduce the new aide on a continuity visit) rather than a cold swap that dents HHCAHPS.

## Guardrails

- **Anchor the schedule on the plan of care + authorization** — over-visiting a capped authorization is unpaid work; under-visiting risks LUPA (PDGM) and a plan-of-care-compliance finding.
- **Continuity of caregiver is the quality metric patients feel** — schedule the same familiar caregiver where possible; a revolving door shows up in HHCAHPS.
- **EVV is not optional** — capture the six Cures-Act elements on every Medicaid visit; an unverified visit is unbillable and a survey finding.
- **Work EVV exceptions the same day, not at month-end** — the exception queue is the difference between a clean claim and a denial.
- **Match the captured visit to the authorization and schedule** — a delivered-but-mismatched visit is a denial.
- Building the schedule is **execution** (the operations specialist); the **staffing/capacity model** and continuity targets are **policy** (the `home-health-agency-lead`) — keep the seam clean; route caregiver **hiring** to `people-operations-hr`.
- State EVV models, aggregator vendors, and the required elements are **volatile** — carry a **retrieval date** on the specific state model. See [`../../knowledge/home-health-care-patterns-2026.md`](../../knowledge/home-health-care-patterns-2026.md). **Not medical, legal, or reimbursement advice.**
