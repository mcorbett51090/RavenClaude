# Value-Stream Map the Whole, Not a Slice

**Status:** Pattern
**Domain:** Process Improvement — Lean / Measure phase
**Applies to:** `process-improvement`

---

## Why this exists

A team that maps only its own slice of the process optimizes a fragment and is surprised when end-to-end lead time does not improve. Value-stream mapping is valuable precisely because it forces the whole value stream into one picture — from raw trigger (customer request, PO, application received) to delivered outcome — so that the real constraint and the real queue locations are visible. A slice-level swimlane is not the same tool; it answers "who does what" but not "where does time go."

## How to apply

**Current-state VSM construction:**

1. **Define scope boundaries:** The stream starts at the customer trigger (Demand) and ends at delivered value (Customer receives). Do not start at "our department receives the work-item" — that hides upstream queues.
2. **Walk the floor (or interview the end-to-end chain):** Interview or observe every handoff; do not reconstruct from org charts.
3. **Capture the metrics that matter** for each process box:
   - Cycle time (touch time)
   - Process lead time (elapsed, including wait)
   - Queue / inventory ahead of the step
   - % Complete and Accurate (%C&A) — what fraction of incoming work items are correct on first receipt
   - Number of people / shifts
4. **Draw the information flow** above the process boxes — how work gets triggered and instructed (push vs pull; what system; how often).
5. **Calculate the value-add ratio:** `Value-Add Time ÷ Total Lead Time`. A ratio below 10% (common in transactional processes) is the burning platform for the project.
6. **Draw the future-state VSM** before the Improve phase: it is the target, not a wish-list.

**Do:**
- Use a paper/whiteboard VSM in the mapping workshop; translate to digital after the team agrees.
- Surface and label every queue (triangle with an N, the inventory count or age of the queue).
- Identify the *pacemaker* — the single step that controls the flow rate — and treat it as the constraint.

**Don't:**
- Map only the happy path; the %C&A box captures where rework loops enter.
- Mix current-state and future-state on the same VSM; they are separate artifacts serving different purposes.
- Use a swimlane map as a substitute — swimlanes show roles, not time flow or inventory.

## Edge cases / when the rule does NOT apply

- **Single-step processes** (a process with genuinely one handoff): the SIPOC is sufficient; a VSM adds no information.
- **Software deployment / CI pipelines:** the VSM metaphor applies but the tooling is pipeline analytics (lead time from commit to production), not a paper map. The principle — measure the whole pipeline, not a phase of it — still holds.

## See also

- [`../agents/process-analyst.md`](../agents/process-analyst.md) — the agent that builds the current-state VSM
- [`./optimize-the-constraint-not-a-sub-process.md`](./optimize-the-constraint-not-a-sub-process.md) — the follow-on rule about directing improvement to the pacemaker

## Provenance

Standard Lean practice: Value Stream Mapping (Rother & Shook, "Learning to See," Lean Enterprise Institute). %C&A metric from Karen Martin & Mike Osterling, "Value Stream Mapping" (2014). _Last verified: 2026-06-05 against lean-enterprise-institute.org documentation._

---

_Last reviewed: 2026-06-05 by `claude`_
